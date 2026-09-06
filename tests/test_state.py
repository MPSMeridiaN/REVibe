import importlib.util
import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).parents[1]
SPEC = importlib.util.spec_from_file_location("statecheck", ROOT / "tools" / "check_state.py")
statecheck = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(statecheck)


class StateTests(unittest.TestCase):
    def setUp(self):
        self.state = json.loads((ROOT / "product/skills/revibe/references/state-template.json").read_text())

    def legacy_state(self):
        state = copy.deepcopy(self.state)
        state["schema_version"] = 1
        state.pop("run", None)
        for stage, record in state["stages"].items():
            record["artifact"] = f".revibe/handoffs/{stage}.md"
        return state

    def state_for_run(self, run_id):
        state = copy.deepcopy(self.state)
        state["run"]["id"] = run_id
        for stage, record in state["stages"].items():
            record["artifact"] = f".revibe/{run_id}/handoffs/{stage}.md"
        return state

    def write_run(self, project, run_id, state=None):
        run_dir = project / ".revibe" / run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        run_state = state if state is not None else self.state_for_run(run_id)
        (run_dir / "state.json").write_text(json.dumps(run_state), encoding="utf-8")

    def run_checker(self, project, *args):
        return subprocess.run(
            [sys.executable, str(ROOT / "tools" / "check_state.py"), str(project), *args],
            capture_output=True,
            text=True,
        )

    def test_initial_state_is_valid(self):
        self.assertEqual([], statecheck.check(self.state))

    def test_schema1_legacy_state_remains_read_only_compatible(self):
        self.assertEqual([], statecheck.check(self.legacy_state()))

    def test_later_revision_does_not_invalidate_previous_handoff(self):
        self.state["revision"] = 7
        self.state["stages"]["discover"].update(status="complete", input_revision=0, output_revision=2)
        self.state["stages"]["verify"].update(status="awaiting_review", input_revision=2, output_revision=7)
        self.assertEqual([], statecheck.check(self.state))

    def test_unknown_and_cyclic_dependencies_rejected(self):
        self.state["decisions"] = [
            {"id": "dec.a", "status": "pending", "depends_on": ["dec.b"]},
            {"id": "dec.b", "status": "pending", "depends_on": ["dec.a", "ev.missing"]},
        ]
        errors = statecheck.check(self.state)
        self.assertTrue(any("unknown dependency" in e for e in errors))
        self.assertTrue(any("cycle" in e for e in errors))

    def test_complete_stage_cannot_consume_stale_input(self):
        self.state["stages"]["discover"]["status"] = "stale"
        self.state["stages"]["verify"]["status"] = "complete"
        self.assertTrue(any("depends on stale" in e for e in statecheck.check(self.state)))

    def test_user_decision_needs_recorded_feedback(self):
        self.state["decisions"] = [{"id": "dec.a", "status": "accepted", "depends_on": []}]
        self.assertTrue(any("lacks user feedback" in e for e in statecheck.check(self.state)))

    def test_forward_stage_dependency_rejected(self):
        self.state["stages"]["discover"]["depends_on"] = ["stage:plan"]
        self.assertTrue(any("forward stage" in e for e in statecheck.check(self.state)))

    def test_task_references_resolve_through_canonical_index(self):
        self.state["tasks"] = [{"id": "task.fix-total", "status": "pending", "depends_on": []}]
        self.state["evidence"] = [{"id": "ev.fix-check", "status": "observed", "depends_on": ["task.fix-total"]}]
        self.assertEqual([], statecheck.check(self.state))
        self.state["tasks"] = []
        self.assertTrue(any("unknown dependency task.fix-total" in e for e in statecheck.check(self.state)))

    def test_saved_handoff_uses_its_stage_revision(self):
        self.state["revision"] = 7
        self.state["stages"]["discover"].update(status="complete", input_revision=0, output_revision=2)
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            handoff = root / self.state["stages"]["discover"]["artifact"]
            handoff.parent.mkdir(parents=True)
            handoff.write_text(
                f"# discover handoff\n- run_id: {self.state['run']['id']}\n- status: complete\n"
                "- input_revision: 0\n- output_revision: 2\n- next_stage: verify\n"
            )
            self.assertEqual([], statecheck.check(self.state, root))
            handoff.write_text(handoff.read_text().replace("output_revision: 2", "output_revision: 3"))
            self.assertTrue(any("handoff revision mismatch" in e for e in statecheck.check(self.state, root)))

    def test_corrected_decision_invalidates_consuming_stage(self):
        self.state["decisions"] = [{"id": "dec.target", "status": "stale", "depends_on": []}]
        self.state["stages"]["design"].update(status="complete", depends_on=["dec.target"])
        self.assertTrue(any("depends on stale dec.target" in e for e in statecheck.check(self.state)))

    def test_schema2_rejects_malformed_run_metadata(self):
        cases = (
            ("id", "../escape", "run.id"),
            ("request", "   ", "run.request"),
            ("status", "done", "run.status"),
        )
        for field, value, marker in cases:
            with self.subTest(field=field):
                state = copy.deepcopy(self.state)
                state["run"][field] = value
                self.assertTrue(any(marker in error for error in statecheck.check(state)))

    def test_cross_run_artifact_path_is_rejected(self):
        state = self.state_for_run("alpha")
        state["revision"] = 1
        state["stages"]["discover"].update(status="complete", input_revision=0, output_revision=1)
        state["stages"]["discover"]["artifact"] = ".revibe/beta/handoffs/discover.md"
        self.assertTrue(any("unexpected artifact path" in error for error in statecheck.check(state)))

    def test_cross_run_handoff_metadata_is_rejected(self):
        state = self.state_for_run("alpha")
        state["revision"] = 1
        state["stages"]["discover"].update(status="complete", input_revision=0, output_revision=1)
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            handoff = root / state["stages"]["discover"]["artifact"]
            handoff.parent.mkdir(parents=True)
            handoff.write_text(
                "# discover handoff\n- run_id: beta\n- status: complete\n"
                "- input_revision: 0\n- output_revision: 1\n- next_stage: verify\n",
                encoding="utf-8",
            )
            errors = statecheck.check(state, root)
        self.assertTrue(any("handoff run_id mismatch" in error for error in errors))

    def test_cross_run_handoff_symlink_is_rejected(self):
        state = self.state_for_run("alpha")
        state["revision"] = 1
        state["stages"]["discover"].update(status="complete", input_revision=0, output_revision=1)
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            alpha_handoff = root / state["stages"]["discover"]["artifact"]
            beta_handoff = root / ".revibe/beta/handoffs/discover.md"
            beta_handoff.parent.mkdir(parents=True)
            beta_handoff.write_text(
                "# discover handoff\n- run_id: beta\n- status: complete\n"
                "- input_revision: 0\n- output_revision: 1\n- next_stage: verify\n",
                encoding="utf-8",
            )
            alpha_handoff.parent.mkdir(parents=True)
            try:
                os.symlink(beta_handoff, alpha_handoff)
            except (OSError, NotImplementedError):
                self.skipTest("symbolic links are unavailable")
            errors = statecheck.check(state, root)
        self.assertTrue(any("escapes the selected run" in error for error in errors))

    def test_cli_requires_run_when_multiple_runs_exist(self):
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp)
            self.write_run(project, "alpha")
            self.write_run(project, "beta")
            result = self.run_checker(project)
        self.assertNotEqual(0, result.returncode)
        self.assertIn("alpha", result.stdout)
        self.assertIn("beta", result.stdout)
        self.assertIn("--run", result.stdout)

    def test_cli_selects_runs_with_local_record_ids(self):
        state = self.state_for_run("alpha")
        state["decisions"] = [{"id": "dec.same", "status": "pending", "depends_on": []}]
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp)
            self.write_run(project, "alpha", state)
            self.write_run(project, "beta", self.state_for_run("beta") | {"decisions": state["decisions"]})
            alpha = self.run_checker(project, "--run", "alpha")
            beta = self.run_checker(project, "--run", "beta")
        self.assertEqual(0, alpha.returncode, alpha.stdout + alpha.stderr)
        self.assertEqual(0, beta.returncode, beta.stdout + beta.stderr)

    def test_cli_requires_explicit_legacy_selection(self):
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp)
            legacy_path = project / ".revibe/state.json"
            legacy_path.parent.mkdir(parents=True)
            legacy_path.write_text(json.dumps(self.legacy_state()), encoding="utf-8")
            implicit = self.run_checker(project)
            explicit = self.run_checker(project, "--legacy")
        self.assertNotEqual(0, implicit.returncode)
        self.assertIn("--legacy", implicit.stdout)
        self.assertEqual(0, explicit.returncode, explicit.stdout + explicit.stderr)


if __name__ == "__main__":
    unittest.main()
