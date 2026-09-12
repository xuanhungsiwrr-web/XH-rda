"""Offline knowledge projection adapter; never opens SQLite on Drive-sync storage."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sqlite3
import sys
import zipfile

from xh_core import atomic, digest, encoded, stamp
from xh_layout import PLUGIN_VERSION


def export_projection(operational_root, destination):
    root = Path(operational_root).resolve()
    db_path = root / "learning/registry.sqlite"
    if not db_path.is_file():
        raise ValueError("Operational knowledge DB is missing")
    out = Path(destination).resolve()
    if out.exists():
        raise ValueError("Projection destination exists")
    uri = db_path.as_uri() + "?mode=ro"
    db = sqlite3.connect(uri, uri=True)
    try:
        rows = [json.loads(r[0]) for r in db.execute("SELECT data FROM lessons ORDER BY id")]
        approved = [row for row in rows if row.get("status") == "approved"]
    finally:
        db.close()
    files = {f"approved/{row['id']}.json": encoded(row) for row in approved}
    manifest = {"format": "xh-tuvan.knowledge-projection.v1", "plugin_version": PLUGIN_VERSION,
                "created": stamp(), "records": [{"path": name, "sha256": digest(raw)}
                for name, raw in sorted(files.items())]}
    out.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out, "x", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("manifest.json", encoded(manifest))
        for name, raw in files.items():
            archive.writestr(name, raw)
    return {"path": str(out), "records": len(files), "sha256": digest(out.read_bytes()),
            "note": "Read-only projection package; publication is an external controlled step"}


def stage_import(package, operational_root):
    source = Path(package).resolve()
    if not source.is_file():
        raise ValueError("Projection package is missing")
    root = Path(operational_root).resolve()
    with zipfile.ZipFile(source) as archive:
        manifest = json.loads(archive.read("manifest.json"))
        if manifest.get("format") != "xh-tuvan.knowledge-projection.v1":
            raise ValueError("Unsupported projection format")
        payload = {}
        for record in manifest.get("records", []):
            raw = archive.read(record["path"])
            if digest(raw) != record["sha256"]:
                raise ValueError("Projection hash mismatch: " + record["path"])
            payload[record["path"]] = json.loads(raw)
    import_id = "IMPORT-" + digest(source.read_bytes())[:20]
    target = root / "learning/imports" / (import_id + ".json")
    if target.exists():
        if digest(target.read_bytes()) != digest(encoded({"manifest": manifest, "records": payload})):
            raise ValueError("Import ID collision")
        return {"import_id": import_id, "staged": False, "duplicate": True, "path": str(target)}
    body = {"manifest": manifest, "records": payload, "status": "staged-not-approved",
            "note": "Staging does not write registry.sqlite or transfer approvals"}
    atomic(target, encoded(body))
    return {"import_id": import_id, "staged": True, "records": len(payload), "path": str(target),
            "approval_transferred": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    exp = sub.add_parser("export"); exp.add_argument("--operational-root", required=True); exp.add_argument("--out", required=True)
    imp = sub.add_parser("stage-import"); imp.add_argument("--package", required=True); imp.add_argument("--operational-root", required=True)
    args = parser.parse_args()
    try:
        result = export_projection(args.operational_root, args.out) if args.action == "export" else stage_import(args.package, args.operational_root)
        print(json.dumps(result, ensure_ascii=False, indent=2)); return 0
    except (ValueError, OSError, sqlite3.Error, zipfile.BadZipFile) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr); return 2


if __name__ == "__main__":
    raise SystemExit(main())
