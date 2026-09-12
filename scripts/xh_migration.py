"""Explicit, reversible v2 -> v3 report-workspace migration."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import sqlite3
import sys
import uuid
import zipfile

from xh_core import atomic, digest, encoded, stamp
from xh_layout import (
    LAYOUT_VERSION, PLUGIN_VERSION, V2_PATHS, V3_PATHS, detect_layout,
    ensure_new_layout, map_legacy_path, rewrite_known_paths,
)


def _read_config(root):
    file = Path(root) / "project.json"
    if not file.is_file():
        raise ValueError("Missing project.json; this is not an initialized workspace")
    try:
        return json.loads(file.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        raise ValueError("Invalid project.json") from exc


def _db_rows(db_path):
    uri = Path(db_path).resolve().as_uri() + "?mode=ro"
    db = sqlite3.connect(uri, uri=True)
    db.row_factory = sqlite3.Row
    try:
        tables = {r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        required = {"revisions", "heads", "approvals"}
        if not required <= tables:
            raise ValueError("State DB lacks required revision/approval tables")
        revisions = [dict(r) for r in db.execute("SELECT * FROM revisions ORDER BY created,id")]
        heads = {r["artifact"]: r["revision"] for r in db.execute("SELECT * FROM heads")}
        approvals = [dict(r) for r in db.execute("SELECT * FROM approvals")]
        return revisions, heads, approvals
    finally:
        db.close()


def preflight(root):
    root = Path(root).resolve()
    config = _read_config(root)
    layout = detect_layout(root)
    if layout.version == LAYOUT_VERSION:
        db_path = root / V3_PATHS["state_db"]
        if not db_path.is_file():
            raise ValueError("v3 project.json exists but the v3 state DB is missing")
        return {"project": str(root), "from_layout": 3, "to_layout": 3,
                "already_migrated": True, "writes": False, "mapping": []}
    db_path = root / V2_PATHS["state_db"]
    if not db_path.is_file():
        raise ValueError("Legacy project.json exists but .xh/state.sqlite is missing; refusing to create empty state")
    revisions, heads, approvals = _db_rows(db_path)
    by_id = {r["id"]: r for r in revisions}
    missing_blobs, missing_heads, mapping = [], [], []
    for row in revisions:
        try:
            meta = json.loads(row.get("meta") or "{}")
        except json.JSONDecodeError:
            meta = {}
        item = map_legacy_path(row["path"], meta)
        item.update(artifact=row["artifact"], revision=row["id"])
        mapping.append(item)
        blob = root / V2_PATHS["artifacts"] / row["hash"]
        if not blob.is_file() or digest(blob.read_bytes()) != row["hash"]:
            missing_blobs.append(row["id"])
    for artifact, revision in heads.items():
        row = by_id.get(revision)
        if not row:
            missing_heads.append(artifact + ":missing-revision")
            continue
        file = root / Path(row["path"])
        if not file.is_file() or digest(file.read_bytes()) != row["hash"]:
            missing_heads.append(artifact + ":missing-or-modified-file")
    if missing_blobs or missing_heads:
        raise ValueError("Preflight failed: " + json.dumps(
            {"missing_or_changed_blobs": missing_blobs, "missing_or_changed_heads": missing_heads},
            ensure_ascii=False))
    plan_id = "MIG-" + digest(encoded({"config": config, "mapping": mapping}))[:20]
    return {
        "project": str(root), "migration_id": plan_id, "from_layout": layout.version,
        "to_layout": LAYOUT_VERSION, "already_migrated": False, "writes": False,
        "revisions": len(revisions), "approvals": len(approvals), "heads": len(heads),
        "mapping": mapping,
        "source_policy": "unclassified legacy sources remain under " + V3_PATHS["legacy_sources"],
        "calculations_policy": "preserved under " + V3_PATHS["legacy_calculations"] + "; never deleted",
    }


def _snapshot(root, migration_id, db_path):
    snapshots = root.parent / ".xh-migration-snapshots"
    snapshots.mkdir(parents=True, exist_ok=True)
    out = snapshots / f"{root.name}-{migration_id}.zip"
    if out.exists():
        return out
    temp_db = snapshots / f".{root.name}-{migration_id}.sqlite"
    source = sqlite3.connect(db_path)
    target = sqlite3.connect(temp_db)
    try:
        source.backup(target)
    finally:
        target.close(); source.close()
    try:
        with zipfile.ZipFile(out, "x", zipfile.ZIP_DEFLATED) as z:
            z.write(root / "project.json", "project.json")
            z.write(temp_db, ".xh/state.sqlite")
            z.writestr("snapshot.json", json.dumps({"migration_id": migration_id,
                "created": stamp(), "source_layout": 2}, ensure_ascii=False, indent=2))
    finally:
        if temp_db.exists():
            temp_db.unlink()
    return out


def _copy_verified(source, target, expected_hash=None):
    raw = source.read_bytes()
    if expected_hash and digest(raw) != expected_hash:
        raise ValueError("Source changed during migration: " + str(source))
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        if digest(target.read_bytes()) == digest(raw):
            return False
        raise ValueError("Migration destination conflict: " + str(target))
    with open(target, "xb") as stream:
        stream.write(raw); stream.flush(); os.fsync(stream.fileno())
    return True


def _rewrite_current_heads(root, db, migration_id):
    """Create lineage revisions for JSON heads containing known legacy paths."""
    db.row_factory = sqlite3.Row
    created = []
    rows = db.execute("SELECT r.* FROM heads h JOIN revisions r ON r.id=h.revision").fetchall()
    for row in rows:
        blob = root / V3_PATHS["artifacts"] / row["hash"]
        raw = blob.read_bytes()
        if not row["path"].lower().endswith(".json"):
            continue
        try:
            value = json.loads(raw.decode("utf-8-sig"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            continue
        updated = rewrite_known_paths(value)
        if updated == value:
            continue
        new_raw = encoded(updated)
        new_hash = digest(new_raw)
        new_blob = root / V3_PATHS["artifacts"] / new_hash
        if not new_blob.exists():
            atomic(new_blob, new_raw)
        rid = uuid.uuid4().hex
        meta = json.loads(row["meta"] or "{}")
        meta.update({"migration_id": migration_id, "lineage_revision": row["id"],
                     "reason": "embedded workspace paths rewritten"})
        db.execute("INSERT INTO revisions VALUES(?,?,?,?,?,?,?,?,?)", (
            rid, row["artifact"], new_hash, row["path"], "system", "workspace-migration",
            row["deps"], json.dumps(meta, ensure_ascii=False), stamp()))
        db.execute("UPDATE heads SET revision=? WHERE artifact=?", (rid, row["artifact"]))
        atomic(root / Path(row["path"]), new_raw)
        created.append({"artifact": row["artifact"], "from_revision": row["id"], "to_revision": rid})
    return created


def apply(root):
    root = Path(root).resolve()
    plan = preflight(root)
    if plan.get("already_migrated"):
        result = verify(root)
        return {**plan, "writes": False, "idempotent": True, "verify": result}
    migration_id = plan["migration_id"]
    lock = root.parent / f".{root.name}-{migration_id}.lock"
    try:
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError as exc:
        raise ValueError("Migration lock exists; inspect or resume the recorded migration") from exc
    os.close(fd)
    try:
        legacy_db = root / V2_PATHS["state_db"]
        snapshot = _snapshot(root, migration_id, legacy_db)
        ensure_new_layout(root)
        journal_path = root / V3_PATHS["migration"] / f"{migration_id}.json"
        journal = {"migration_id": migration_id, "status": "copying", "snapshot": str(snapshot),
                   "started": stamp(), "mapping": plan["mapping"]}
        atomic(journal_path, encoded(journal))

        # Copy immutable blobs and current head files; legacy originals remain untouched.
        revisions, heads, _ = _db_rows(legacy_db)
        by_id = {r["id"]: r for r in revisions}
        for row in revisions:
            _copy_verified(root / V2_PATHS["artifacts"] / row["hash"],
                           root / V3_PATHS["artifacts"] / row["hash"], row["hash"])
        mapping_by_revision = {m["revision"]: m for m in plan["mapping"]}
        for revision in heads.values():
            row = by_id[revision]; target = mapping_by_revision[revision]["to"]
            _copy_verified(root / Path(row["path"]), root / Path(target), row["hash"])

        new_db_path = root / V3_PATHS["state_db"]
        if new_db_path.exists():
            new_db_path.unlink()
        source = sqlite3.connect(legacy_db); target = sqlite3.connect(new_db_path)
        try:
            source.backup(target)
        finally:
            target.close(); source.close()
        db = sqlite3.connect(new_db_path)
        try:
            db.execute("BEGIN IMMEDIATE")
            db.execute("CREATE TABLE IF NOT EXISTS workspace_migrations(id TEXT PRIMARY KEY, data TEXT NOT NULL)")
            for item in plan["mapping"]:
                if item["to"] != item["from"]:
                    db.execute("UPDATE revisions SET path=? WHERE id=?", (item["to"], item["revision"]))
            lineage = _rewrite_current_heads(root, db, migration_id)
            config = _read_config(root)
            config.update(schema_version=3, layout_version=LAYOUT_VERSION, plugin_version=PLUGIN_VERSION)
            old_project = db.execute("SELECT r.* FROM heads h JOIN revisions r ON r.id=h.revision WHERE h.artifact='project'").fetchone()
            project_raw = encoded(rewrite_known_paths(config)); project_hash = digest(project_raw)
            atomic(root / V3_PATHS["artifacts"] / project_hash, project_raw)
            rid = uuid.uuid4().hex
            deps = old_project["deps"] if old_project else "{}"
            db.execute("INSERT INTO revisions VALUES(?,?,?,?,?,?,?,?,?)", (rid, "project", project_hash,
                "project.json", "system", "workspace-migration", deps,
                json.dumps({"migration_id": migration_id, "lineage_revision": old_project["id"] if old_project else None}, ensure_ascii=False), stamp()))
            db.execute("INSERT OR REPLACE INTO heads VALUES('project',?)", (rid,))
            record = {"migration_id": migration_id, "snapshot": str(snapshot), "lineage": lineage,
                      "mapping": plan["mapping"], "status": "applied", "applied": stamp()}
            db.execute("INSERT OR REPLACE INTO workspace_migrations VALUES(?,?)", (migration_id, json.dumps(record, ensure_ascii=False)))
            db.commit()
        except BaseException:
            db.rollback(); raise
        finally:
            db.close()
        # Switch readers only after the new DB and all mapped heads are durable.
        atomic(root / "project.json", project_raw)
        journal.update(status="applied", completed=stamp(), lineage=lineage)
        atomic(journal_path, encoded(journal))
        result = verify(root)
        if not result["passed"]:
            raise ValueError("Post-migration verification failed: " + json.dumps(result, ensure_ascii=False))
        return {**plan, "writes": True, "snapshot": str(snapshot), "lineage": lineage, "verify": result}
    finally:
        if lock.exists():
            lock.unlink()


def verify(root):
    root = Path(root).resolve()
    config = _read_config(root)
    db_path = root / V3_PATHS["state_db"]
    failures = []
    if config.get("layout_version") != LAYOUT_VERSION:
        failures.append("project.json is not layout v3")
    if not db_path.is_file():
        failures.append("v3 state DB missing")
        return {"passed": False, "failures": failures}
    revisions, heads, approvals = _db_rows(db_path)
    by_id = {r["id"]: r for r in revisions}
    for artifact, revision in heads.items():
        row = by_id.get(revision)
        if not row:
            failures.append(artifact + ": missing head revision"); continue
        blob = root / V3_PATHS["artifacts"] / row["hash"]
        file = root / Path(row["path"])
        if not blob.is_file() or digest(blob.read_bytes()) != row["hash"]:
            failures.append(artifact + ": blob mismatch")
        if not file.is_file() or digest(file.read_bytes()) != row["hash"]:
            failures.append(artifact + ": head file mismatch")
    return {"passed": not failures, "failures": failures, "revisions": len(revisions),
            "heads": len(heads), "approvals": len(approvals), "legacy_preserved":
            (root / V2_PATHS["state_db"]).is_file()}


def rollback(root, migration_id=None):
    root = Path(root).resolve()
    if detect_layout(root).version != LAYOUT_VERSION:
        return {"rolled_back": False, "idempotent": True, "layout_version": detect_layout(root).version}
    journals = sorted((root / V3_PATHS["migration"]).glob("MIG-*.json"))
    if migration_id:
        journals = [p for p in journals if p.stem == migration_id]
    if not journals:
        raise ValueError("No migration journal found")
    journal = json.loads(journals[-1].read_text(encoding="utf-8"))
    snapshot = Path(journal["snapshot"])
    if not snapshot.is_file():
        raise ValueError("Migration snapshot is missing; rollback refused")
    if not (root / V2_PATHS["state_db"]).is_file():
        raise ValueError("Legacy DB is missing; rollback refused")
    with zipfile.ZipFile(snapshot) as z:
        original = z.read("project.json")
    atomic(root / "project.json", original)
    marker = snapshot.parent / f"{root.name}-{journal['migration_id']}-rollback.json"
    atomic(marker, encoded({"migration_id": journal["migration_id"], "rolled_back": stamp(),
                            "note": "v3 expansion retained; legacy reader reactivated"}))
    return {"rolled_back": True, "migration_id": journal["migration_id"],
            "layout_version": detect_layout(root).version, "v3_expansion_retained": True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["preflight", "dry-run", "apply", "verify", "rollback", "resume"])
    parser.add_argument("--project", required=True)
    parser.add_argument("--migration-id")
    args = parser.parse_args()
    try:
        if args.action in {"preflight", "dry-run"}:
            result = preflight(args.project)
        elif args.action in {"apply", "resume"}:
            result = apply(args.project)
        elif args.action == "verify":
            result = verify(args.project)
        else:
            result = rollback(args.project, args.migration_id)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (ValueError, OSError, sqlite3.Error, zipfile.BadZipFile) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
