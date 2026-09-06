import importlib.util
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


SPEC = importlib.util.spec_from_file_location(
    "installer_adversarial", Path(__file__).parents[1] / "install.py"
)
installer = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(installer)


class StatelessInstallerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.source = self.base / "source"
        self.skill = self.source / "revibe"
        self.skill.mkdir(parents=True)
        (self.skill / "SKILL.md").write_text("v1")
        self.root = self.base / "target" / "skills"

    def manifest(self):
        return installer.source_manifest(self.source)

    def install(self):
        return installer.apply(self.root, self.manifest(), self.source)

    def test_destination_contains_only_product_skills_and_no_state(self):
        self.install()
        self.assertEqual(["revibe"], [path.name for path in self.root.iterdir()])
        self.assertFalse((self.root / ".revibe-install.json").exists())
        self.assertFalse((self.root / ".revibe-lock").exists())
        self.assertFalse((self.root.parent / ".revibe").exists())

    def test_unrelated_skill_is_preserved_and_stale_revibe_skill_is_removed(self):
        self.install()
        unrelated = self.root / "my-skill"
        unrelated.mkdir()
        (unrelated / "SKILL.md").write_text("mine")
        stale = self.root / "revibe-old"
        stale.mkdir()
        (stale / "SKILL.md").write_text("old")

        self.install()

        self.assertTrue(unrelated.is_dir())
        self.assertFalse(stale.exists())

    def test_existing_revibe_skill_with_extra_file_is_refused(self):
        self.install()
        (self.root / "revibe" / "notes.txt").write_text("keep")
        with self.assertRaises(installer.Conflict):
            self.install()
        self.assertTrue((self.root / "revibe" / "notes.txt").is_file())

    def test_legacy_state_is_removed_during_update(self):
        self.install()
        (self.root / ".revibe-install.json").write_text("legacy")
        (self.root / ".revibe-lock").write_bytes(b"legacy")
        adjacent = self.root.parent / ".revibe" / self.root.name
        adjacent.mkdir(parents=True)
        (adjacent / ".revibe-install.json").write_text("legacy")

        self.install()

        self.assertFalse((self.root / ".revibe-install.json").exists())
        self.assertFalse((self.root / ".revibe-lock").exists())
        self.assertFalse(adjacent.exists())
        self.assertEqual(["revibe"], [path.name for path in self.root.iterdir()])

    def test_symlink_destination_is_rejected(self):
        outside = self.base / "outside"
        outside.mkdir()
        link = self.base / "link"
        try:
            link.symlink_to(outside, target_is_directory=True)
        except OSError:
            self.skipTest("Symlink creation unavailable on this host")
        with self.assertRaises(installer.Conflict):
            installer.preflight(link / "skills", self.manifest())
        self.assertEqual([], list(outside.iterdir()))

    def test_linked_source_is_rejected(self):
        linked_source = self.base / "source-link"
        try:
            linked_source.symlink_to(self.source, target_is_directory=True)
        except OSError:
            self.skipTest("Symlink creation unavailable on this host")
        with self.assertRaises(installer.Conflict):
            installer.apply(self.root, self.manifest(), linked_source)
        self.assertFalse(self.root.exists())

    def test_python_310_junction_destination_is_rejected(self):
        if os.name != "nt":
            self.skipTest("Windows junction test")
        outside = self.base / "outside"
        outside.mkdir()
        link = self.base / "junction-root"
        result = subprocess.run(
            ["cmd", "/c", "mklink", "/J", str(link), str(outside)],
            capture_output=True,
            text=True,
        )
        if result.returncode:
            self.skipTest(f"junction creation unavailable: {result.stderr}")
        with self.assertRaises(installer.Conflict):
            installer.apply(link / "skills", self.manifest(), self.source)
        self.assertFalse((outside / "skills").exists())

    def test_uninstall_removes_owned_names_without_touching_unrelated(self):
        self.install()
        stale = self.root / "revibe-old"
        stale.mkdir()
        (stale / "SKILL.md").write_text("old")
        unrelated = self.root / "my-skill"
        unrelated.mkdir()
        (unrelated / "SKILL.md").write_text("mine")

        installer.apply(self.root, self.manifest(), self.source, uninstall=True)

        self.assertFalse((self.root / "revibe").exists())
        self.assertTrue(stale.is_dir())
        self.assertTrue(unrelated.is_dir())

    def test_uninstall_preserves_unknown_revibe_prefixed_skill(self):
        self.install()
        other = self.root / "revibe-third-party"
        other.mkdir()
        (other / "SKILL.md").write_text("third-party")

        installer.apply(self.root, self.manifest(), self.source, uninstall=True)

        self.assertFalse((self.root / "revibe").exists())
        self.assertTrue((other / "SKILL.md").is_file())


if __name__ == "__main__":
    unittest.main()
