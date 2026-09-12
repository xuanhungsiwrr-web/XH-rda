import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
WRAPPER = ROOT / "bridge" / "wrapper.py"


class WrapperTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.workspace = self.root / "project"
        self.workspace.mkdir()
        self.capture = self.root / "request.json"
        self.output = self.root / "output.json"
        self.bridge = self.root / "fake_bridge.py"
        self.bridge.write_text(
            "import argparse,json,pathlib,sys\n"
            "p=argparse.ArgumentParser();p.add_argument('--context');p.parse_args()\n"
            "request=json.load(sys.stdin)\n"
            "capture=pathlib.Path(sys.argv[0]).with_name('captured.json')\n"
            "capture.write_text(json.dumps(request),encoding='utf-8')\n"
            "if request.get('pause_requested'):\n"
            "  workspace=pathlib.Path(request['workspace']); d=workspace/'30_Working'/'.xh'/'handoffs'; d.mkdir(parents=True,exist_ok=True)\n"
            "  (d/'pause.json').write_text(json.dumps({'protocol_version':'1.1','task_id':request['task_id'],'state':'safe'}),encoding='utf-8')\n"
            "  print(json.dumps({'protocol_version':'1.1','task_id':request['task_id'],'handoff_uri':f\"xh-tuvan://handoff/{request['task_id']}/pause.json\"}))\n"
            "  raise SystemExit(0)\n"
            "response=json.loads(pathlib.Path(sys.argv[0]).with_name('response.json').read_text())\n"
            "print(json.dumps(response))\n",
            encoding="utf-8",
        )

    def tearDown(self):
        self.temp.cleanup()

    def context(self, task_id="T-TEST"):
        path = self.root / "context.json"
        path.write_text(json.dumps({
            "protocol_version": "1.1",
            "task_id": task_id,
            "attempt_id": "A-1",
            "generation": 1,
            "worker_id": "pc-main",
            "channel_id": "codex-subscription",
            "permissions": {"level": "SAFE_EDIT"},
            "budget": {"api_soft_usd": 0, "api_hard_usd": 0},
            "channel_bridge": [sys.executable, str(self.bridge)],
            "timeout_seconds": 10,
        }), encoding="utf-8")
        return path

    def task(self, task_id="T-TEST", task_type="analyze_project"):
        return {
            "task_id": task_id,
            "task_type": task_type,
            "plugin": "xh-tuvan",
            "project": {"project_id": "REAL", "workspace_uri": str(self.workspace)},
            "execution": {"master_capability": "MASTER"},
            "permissions": {"level": "SAFE_EDIT"},
            "user_request": "Đánh giá mức độ sẵn sàng lập NCKT",
        }

    def run_wrapper(self, payload, response, context_path=None):
        (self.root / "response.json").write_text(json.dumps(response), encoding="utf-8")
        context_path = context_path or self.context()
        return subprocess.run(
            [sys.executable, str(WRAPPER), "--context", str(context_path)],
            input=json.dumps(payload), capture_output=True, text=True, encoding="utf-8",
            timeout=15, check=False,
        )

    def test_healthcheck(self):
        result = subprocess.run(
            [sys.executable, str(WRAPPER), "--healthcheck"],
            capture_output=True, text=True, encoding="utf-8", check=False,
        )
        self.assertEqual(result.returncode, 0)
        self.assertEqual(json.loads(result.stdout), {"protocol_version": "1.1", "healthy": True})

    def test_legacy_protocol_1_0_execute_remains_supported(self):
        self.output.write_text(json.dumps({"outcome": "completed", "deliverable": "legacy",
                                           "evidence": ["source"], "blockers": []}), encoding="utf-8")
        context = self.context()
        data = json.loads(context.read_text(encoding="utf-8"))
        data["protocol_version"] = "1.0"
        context.write_text(json.dumps(data), encoding="utf-8")
        result = self.run_wrapper(self.task(), {"success": True, "output_ref": self.output.as_uri()}, context)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["status"], "COMPLETED")

    def test_completed_result_requires_evidence(self):
        self.output.write_text(json.dumps({
            "outcome": "completed", "deliverable": "Đã đánh giá",
            "evidence": ["source.pdf"], "blockers": [],
        }), encoding="utf-8")
        response = {"success": True, "output_ref": self.output.as_uri(),
                    "usage": {"input_tokens": 5}, "latency_seconds": 0.2, "error_type": None}
        result = self.run_wrapper(self.task(), response)
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "COMPLETED")
        self.assertEqual(payload["outputs"][0]["uri"], self.output.as_uri())
        request = json.loads((self.root / "captured.json").read_text(encoding="utf-8"))
        self.assertEqual(request["task_id"], "T-TEST")
        self.assertIn("skills\\xh-tuvan\\SKILL.md", request["prompt_or_instruction"])
        self.assertNotIn("API key", request["prompt_or_instruction"])

    def test_completed_readiness_may_report_later_blockers(self):
        self.output.write_text(json.dumps({
            "outcome": "completed", "deliverable": "Đã đánh giá mức độ sẵn sàng",
            "evidence": ["source.pdf"], "blockers": ["Thiếu khảo sát"],
        }), encoding="utf-8")
        response = {"success": True, "output_ref": self.output.as_uri(),
                    "usage": {}, "latency_seconds": 0.2, "error_type": None}
        result = self.run_wrapper(self.task(), response)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["status"], "COMPLETED")

    def test_blocked_domain_result_is_not_false_completion(self):
        self.output.write_text(json.dumps({
            "outcome": "blocked", "deliverable": "Thiếu đầu vào",
            "evidence": ["source.pdf"], "blockers": ["Thiếu khảo sát"],
        }), encoding="utf-8")
        response = {"success": True, "output_ref": self.output.as_uri(),
                    "usage": {}, "latency_seconds": 0.2, "error_type": None}
        result = self.run_wrapper(self.task(), response)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["status"], "FAILED")

    def test_bound_task_mismatch_is_rejected(self):
        response = {"success": False, "output_ref": None, "usage": {},
                    "latency_seconds": 0.0, "error_type": "NOT_RUN"}
        result = self.run_wrapper(self.task(task_id="OTHER"), response)
        self.assertEqual(result.returncode, 3)
        self.assertEqual(result.stdout, "")

    def test_generic_task_type_is_accepted_as_default(self):
        self.output.write_text(json.dumps({"outcome": "completed", "deliverable": "generic",
                                           "evidence": ["source"], "blockers": []}), encoding="utf-8")
        response = {"success": True, "output_ref": self.output.as_uri(), "latency_seconds": 0}
        result = self.run_wrapper(self.task(task_type="generic"), response)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["status"], "COMPLETED")

    def test_pause_returns_only_valid_plugin_owned_handoff(self):
        self.output.write_text(json.dumps({"outcome": "completed", "deliverable": "x",
                                           "evidence": ["state"], "blockers": []}), encoding="utf-8")
        response = {"success": True, "output_ref": self.output.as_uri(), "latency_seconds": 0}
        context = self.context()
        (self.root / "pause.request.json").write_text(json.dumps({
            "protocol_version": "1.1", "task_id": "T-TEST", "action": "pause"}), encoding="utf-8")
        result = self.run_wrapper(self.task(), response)
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["protocol_version"], "1.1")
        self.assertEqual(payload["task_id"], "T-TEST")
        self.assertTrue(payload["handoff_uri"].startswith("xh-tuvan://handoff/T-TEST/pause-"))
        self.assertEqual(json.loads((self.root / "pause.response.json").read_text()), payload)
        self.assertNotIn("safe", result.stdout)
        self.assertEqual(result.stderr, "")

    def test_pause_rejects_wrong_task_request(self):
        (self.root / "pause.request.json").write_text(json.dumps({
            "protocol_version": "1.1", "task_id": "OTHER", "action": "pause"}), encoding="utf-8")
        result = self.run_wrapper(self.task(), {"success": False})
        self.assertEqual(result.returncode, 3)
        self.assertNotIn("OTHER", result.stdout + result.stderr)

    def test_pause_response_references_existing_plugin_handoff(self):
        (self.root / "pause.request.json").write_text(json.dumps({
            "protocol_version": "1.1", "task_id": "T-TEST", "action": "pause"}), encoding="utf-8")
        result = self.run_wrapper(self.task(), {"success": False})
        self.assertEqual(result.returncode, 0, result.stderr)
        uri = json.loads(result.stdout)["handoff_uri"]
        name = Path(urlparse(uri).path).name
        handoff = self.workspace / "30_Working" / ".xh" / "handoffs" / name
        self.assertTrue(handoff.is_file())
        state = json.loads(handoff.read_text(encoding="utf-8"))
        self.assertEqual(state["task_id"], "T-TEST")
        self.assertEqual(state["state"], "paused_before_channel_completion")
        self.assertNotIn("user_request", state)

    def test_mid_channel_pause_stops_child_and_publishes_handoff(self):
        self.bridge.write_text(self.bridge.read_text(encoding="utf-8").replace(
            "response=json.loads", "import time;time.sleep(10)\nresponse=json.loads"), encoding="utf-8")
        context = self.context()
        process = subprocess.Popen(
            [sys.executable, str(WRAPPER), "--context", str(context)],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, encoding="utf-8",
        )
        assert process.stdin is not None
        process.stdin.write(json.dumps(self.task()))
        process.stdin.close()
        process.stdin = None
        deadline = time.monotonic() + 3
        while not (self.root / "captured.json").exists() and time.monotonic() < deadline:
            time.sleep(0.02)
        (self.root / "pause.request.json").write_text(json.dumps({
            "protocol_version": "1.1", "task_id": "T-TEST", "action": "pause"}), encoding="utf-8")
        stdout, stderr = process.communicate(timeout=5)
        self.assertEqual(process.returncode, 0, stderr)
        payload = json.loads(stdout)
        self.assertEqual(payload["task_id"], "T-TEST")
        self.assertEqual(json.loads((self.root / "pause.response.json").read_text()), payload)

    def test_resume_passes_opaque_uri_and_consumes_handoff(self):
        handoff_dir = self.workspace / "30_Working" / ".xh" / "handoffs"
        handoff_dir.mkdir(parents=True)
        handoff = handoff_dir / "resume.json"
        handoff.write_text(json.dumps({"protocol_version": "1.1", "task_id": "T-TEST",
                                       "state": "ready"}), encoding="utf-8")
        self.output.write_text(json.dumps({"outcome": "completed", "deliverable": "resumed",
                                           "evidence": ["handoff"], "blockers": []}), encoding="utf-8")
        context = self.context()
        data = json.loads(context.read_text(encoding="utf-8"))
        data["resume_handoff_uri"] = "xh-tuvan://handoff/T-TEST/resume.json"
        context.write_text(json.dumps(data), encoding="utf-8")
        response = {"success": True, "output_ref": self.output.as_uri(), "latency_seconds": 0}
        result = self.run_wrapper(self.task(), response, context)
        self.assertEqual(result.returncode, 0, result.stderr)
        request = json.loads((self.root / "captured.json").read_text(encoding="utf-8"))
        self.assertEqual(request["resume_handoff_uri"], data["resume_handoff_uri"])
        self.assertNotIn("state", request["prompt_or_instruction"])
        self.assertIn("consumed_at", json.loads(handoff.read_text(encoding="utf-8")))

    def test_resume_rejects_wrong_task_handoff(self):
        handoff_dir = self.workspace / "30_Working" / ".xh" / "handoffs"
        handoff_dir.mkdir(parents=True)
        (handoff_dir / "other.json").write_text(json.dumps({"protocol_version": "1.1", "task_id": "OTHER"}), encoding="utf-8")
        context = self.context()
        data = json.loads(context.read_text(encoding="utf-8"))
        data["resume_handoff_uri"] = "xh-tuvan://handoff/OTHER/other.json"
        context.write_text(json.dumps(data), encoding="utf-8")
        result = self.run_wrapper(self.task(), {"success": False}, context)
        self.assertEqual(result.returncode, 3)

    def test_resume_replay_is_rejected(self):
        handoff_dir = self.workspace / "30_Working" / ".xh" / "handoffs"
        handoff_dir.mkdir(parents=True)
        handoff = handoff_dir / "used.json"
        handoff.write_text(json.dumps({"protocol_version": "1.1", "task_id": "T-TEST",
                                       "consumed_at": "2026-01-01T00:00:00Z"}), encoding="utf-8")
        context = self.context()
        data = json.loads(context.read_text(encoding="utf-8"))
        data["resume_handoff_uri"] = "xh-tuvan://handoff/T-TEST/used.json"
        context.write_text(json.dumps(data), encoding="utf-8")
        result = self.run_wrapper(self.task(), {"success": False}, context)
        self.assertEqual(result.returncode, 3)


if __name__ == "__main__":
    unittest.main()
