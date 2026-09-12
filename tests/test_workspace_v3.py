import io
import json
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from xh_core import Project, digest, encoded, stamp
from xh_delivery import deliver_bytes, import_feedback
from xh_knowledge_transfer import export_projection, stage_import
from xh_layout import LAYOUT_VERSION, V2_PATHS, V3_PATHS
from xh_learning import Learning
from xh_migration import apply, preflight, rollback, verify


def docx_bytes(text):
    import docx
    stream = io.BytesIO()
    document = docx.Document(); document.add_paragraph(text); document.save(stream)
    return stream.getvalue()


def legacy_workspace(root):
    root.mkdir(parents=True)
    for folder in ["sources", "calculations", ".ai", ".xh/artifacts"]:
        (root / folder).mkdir(parents=True, exist_ok=True)
    config = {"schema_version": 2, "metadata": {"project_name": "Legacy"},
              "source_roots": [], "sections": []}
    (root / "project.json").write_bytes(encoded(config))
    records = [
        ("project", "project.json", encoded(config), {}, {}),
        ("source:x", "sources/x.md", b"source", {}, {"kind": "PROJECT"}),
        ("calculation:x", "calculations/x.xlsx", b"calculation", {}, {}),
        ("manifest", ".ai/MANIFEST.json", encoded({"source_ref": "sources/x.md"}),
         {"source:x": "SOURCE_REV"}, {}),
    ]
    db = sqlite3.connect(root / ".xh/state.sqlite")
    db.executescript("""
    CREATE TABLE revisions(id TEXT PRIMARY KEY, artifact TEXT, hash TEXT, path TEXT,
      origin TEXT, actor TEXT, deps TEXT, meta TEXT, created TEXT);
    CREATE TABLE heads(artifact TEXT PRIMARY KEY, revision TEXT);
    CREATE TABLE approvals(revision TEXT PRIMARY KEY, actor TEXT, created TEXT);
    """)
    revisions = {}
    for index, (artifact, path, raw, deps, meta) in enumerate(records):
        revision = f"R{index}"; revisions[artifact] = revision
        if artifact == "source:x":
            # Fill the stable dependency ID used by the manifest fixture.
            pass
        actual_deps = {k: revisions.get(k, value) for k, value in deps.items()}
        hsh = digest(raw)
        target = root / path; target.parent.mkdir(parents=True, exist_ok=True); target.write_bytes(raw)
        (root / ".xh/artifacts" / hsh).write_bytes(raw)
        db.execute("INSERT INTO revisions VALUES(?,?,?,?,?,?,?,?,?)", (revision, artifact, hsh,
            path, "human", "fixture", json.dumps(actual_deps), json.dumps(meta), stamp()))
        db.execute("INSERT INTO heads VALUES(?,?)", (artifact, revision))
    db.execute("INSERT INTO approvals VALUES(?,?,?)", (revisions["manifest"], "user", stamp()))
    db.commit(); db.close()
    return revisions


class LayoutMigrationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.root = Path(self.tmp.name) / "legacy"
        self.revisions = legacy_workspace(self.root)

    def tearDown(self):
        self.tmp.cleanup()

    def test_legacy_opens_without_creating_new_state(self):
        p = Project(self.root)
        try:
            self.assertEqual(p.layout.version, 2)
            self.assertEqual(p.read("source:x"), b"source")
            self.assertTrue(p.approved("manifest"))
            self.assertFalse((self.root / V3_PATHS["state_db"]).exists())
        finally:
            p.close()

    def test_missing_legacy_db_fails_instead_of_creating_empty_state(self):
        broken = Path(self.tmp.name) / "broken"; broken.mkdir()
        (broken / "project.json").write_text('{"schema_version":2}', encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "state database is missing"):
            Project.init(broken)
        self.assertFalse((broken / V2_PATHS["state_db"]).exists())

    def test_dry_run_apply_verify_retry_and_rollback(self):
        before = sorted(p.relative_to(self.root).as_posix() for p in self.root.rglob("*"))
        plan = preflight(self.root)
        self.assertFalse(plan["writes"])
        self.assertEqual(before, sorted(p.relative_to(self.root).as_posix() for p in self.root.rglob("*")))
        source_map = next(m for m in plan["mapping"] if m["artifact"] == "source:x")
        self.assertEqual(source_map["status"], "legacy-unclassified")
        result = apply(self.root)
        self.assertTrue(result["verify"]["passed"])
        self.assertTrue((self.root / V2_PATHS["state_db"]).is_file())
        self.assertTrue((self.root / V3_PATHS["legacy_calculations"] / "x.xlsx").is_file())
        p = Project(self.root)
        try:
            self.assertEqual(p.layout.version, LAYOUT_VERSION)
            self.assertEqual(p.read("source:x"), b"source")
            self.assertFalse(p.approved("manifest"))
            approvals = p.db.execute("SELECT count(*) FROM approvals").fetchone()[0]
            self.assertEqual(approvals, 1)
            manifest = json.loads(p.read("manifest"))
            self.assertTrue(manifest["source_ref"].startswith(V3_PATHS["legacy_sources"]))
            manifest_head = p.head("manifest")
            self.assertEqual(json.loads(manifest_head["deps"])["source:x"], self.revisions["source:x"])
            self.assertFalse(p.stale("manifest"))
        finally:
            p.close()
        self.assertTrue(apply(self.root)["idempotent"])
        self.assertTrue(verify(self.root)["passed"])
        rolled = rollback(self.root)
        self.assertTrue(rolled["rolled_back"])
        p = Project(self.root)
        try:
            self.assertEqual(p.layout.version, 2)
            self.assertTrue(p.approved("manifest"))
        finally:
            p.close()


class DeliveryPairTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.root = Path(self.tmp.name) / "project"
        Project.init(self.root, {"project_name": "Fixture"}); self.p = Project(self.root)
        self.p.put("report", self.p.path("outputs", "report.md"), "# Report", "system")

    def tearDown(self):
        self.p.close(); self.tmp.cleanup()

    def test_pair_retry_partial_failure_and_no_overwrite(self):
        first = docx_bytes("R01")
        with self.assertRaises(RuntimeError):
            deliver_bytes(self.p, "BC_R01", first, simulate_failure_after_output=True)
        result = deliver_bytes(self.p, "BC_R01", first)
        output = self.root / result["output_path"]; feedback = self.root / result["feedback_path"]
        self.assertEqual(output.read_bytes(), feedback.read_bytes())
        edited = docx_bytes("R01 edited"); feedback.write_bytes(edited)
        retry = deliver_bytes(self.p, "BC_R01", first)
        self.assertTrue(retry["feedback_modified"])
        self.assertEqual(feedback.read_bytes(), edited)
        with self.assertRaisesRegex(ValueError, "different immutable baseline"):
            deliver_bytes(self.p, "BC_R01", docx_bytes("other"))

    def test_diff_uses_exact_pair_deduplicates_and_detects_baseline_change(self):
        r1_bytes, r2_bytes = docx_bytes("R01"), docx_bytes("R02")
        r1 = deliver_bytes(self.p, "BC_R01", r1_bytes)
        r2 = deliver_bytes(self.p, "BC_R02", r2_bytes)
        (self.root / r1["feedback_path"]).write_bytes(docx_bytes("R01 edited"))
        imported = import_feedback(self.p, release_id="BC_R01")
        self.assertTrue(imported["imported"])
        self.assertFalse(imported["learning_candidate_created"])
        self.assertTrue(import_feedback(self.p, release_id="BC_R01")["duplicate"])
        self.assertEqual((self.root / r2["output_path"]).read_bytes(), r2_bytes)
        (self.root / r1["output_path"]).write_bytes(b"tampered")
        with self.assertRaisesRegex(ValueError, "baseline changed"):
            import_feedback(self.p, release_id="BC_R01")


class KnowledgeTransferTests(unittest.TestCase):
    def test_projection_import_is_staged_and_never_transfers_approval(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "operational"
            with Learning(root) as kb:
                row = kb.candidate("Rule", "Keep sources", [{"reference": "fixture", "quote": "source"}],
                    "author", cases=[{"input": {"facts": [{}]}, "expected_findings": ["missing_source"],
                    "explanation": "guard"}])
                row = kb.validate(row["id"], "reviewer", True, True, True, "checked")
                kb.approve(row["id"], "operator", "approval-1", row["content_hash"])
            package = Path(temp) / "projection.zip"
            export_projection(root, package)
            staged = stage_import(package, Path(temp) / "other-operational")
            self.assertTrue(staged["staged"])
            self.assertFalse(staged["approval_transferred"])
            self.assertFalse((Path(temp) / "other-operational/learning/registry.sqlite").exists())
            with self.assertRaisesRegex(ValueError, "synced Drive"):
                Learning(Path(temp) / "My Drive" / "knowledge")


if __name__ == "__main__":
    unittest.main()
