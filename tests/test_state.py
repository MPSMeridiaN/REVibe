import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).parents[1]
SPEC = importlib.util.spec_from_file_location("statecheck", ROOT / "tools" / "check_state.py")
statecheck = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(statecheck)


class StateTests(unittest.TestCase):
    def setUp(self):
        self.state = json.loads((ROOT / "product/skills/revibe/references/state-template.json").read_text())

    def test_initial_state_is_valid(self):
        self.assertEqual([], statecheck.check(self.state))

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
            handoff = root / ".revibe/handoffs/discover.md"
            handoff.parent.mkdir(parents=True)
            handoff.write_text("# discover handoff\n- status: complete\n- input_revision: 0\n- output_revision: 2\n- next_stage: verify\n")
            self.assertEqual([], statecheck.check(self.state, root))
            handoff.write_text(handoff.read_text().replace("output_revision: 2", "output_revision: 3"))
            self.assertTrue(any("handoff revision mismatch" in e for e in statecheck.check(self.state, root)))

    def test_corrected_decision_invalidates_consuming_stage(self):
        self.state["decisions"] = [{"id": "dec.target", "status": "stale", "depends_on": []}]
        self.state["stages"]["design"].update(status="complete", depends_on=["dec.target"])
        self.assertTrue(any("depends on stale dec.target" in e for e in statecheck.check(self.state)))


if __name__ == "__main__":
    unittest.main()
