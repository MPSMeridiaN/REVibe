import importlib.util
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location("installer", Path(__file__).parents[1] / "install.py")
installer = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(installer)


class InstallerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.source = self.base / "source"
        self.skill = self.source / "revibe"
        self.skill.mkdir(parents=True)
        (self.skill / "SKILL.md").write_text("---\nname: revibe\ndescription: Test\n---\nOriginal\n")
        self.root = self.base / "target" / "skills"

    def manifest(self):
        return installer.source_manifest(self.source)

    def install(self):
        return installer.apply(self.root, self.manifest(), self.source)

    def test_install_repeat_update_and_uninstall_preserve_unrelated(self):
        self.root.mkdir(parents=True)
        other = self.root / "my-skill"
        other.mkdir()
        (other / "SKILL.md").write_text("mine")
        self.install()
        first = (self.root / "revibe" / "SKILL.md").stat().st_mtime_ns
        self.assertIn("Already current", self.install())
        self.assertEqual(first, (self.root / "revibe" / "SKILL.md").stat().st_mtime_ns)
        (self.skill / "SKILL.md").write_text("Updated")
        self.install()
        self.assertEqual("Updated", (self.root / "revibe" / "SKILL.md").read_text())
        installer.apply(self.root, self.manifest(), self.source, uninstall=True)
        self.assertFalse((self.root / "revibe").exists())
        self.assertEqual("mine", (other / "SKILL.md").read_text())

    def test_skill_directory_contains_only_skill_directories(self):
        self.install()
        self.assertEqual(["revibe"], [path.name for path in self.root.iterdir()])
        self.assertTrue((self.root / "revibe" / "SKILL.md").is_file())
        self.assertFalse(any(path.is_file() for path in self.root.iterdir()))

    def test_reserved_revibe_skill_can_be_refreshed_without_state(self):
        import shutil
        self.root.mkdir(parents=True)
        shutil.copytree(self.skill, self.root / "revibe")
        self.assertIn("Already current", self.install())
        self.assertEqual("Original\n", (self.root / "revibe" / "SKILL.md").read_text().split("---\n")[-1])

    def test_modified_owned_skill_and_extra_file_refused(self):
        self.install()
        (self.root / "revibe" / "notes.txt").write_text("keep")
        with self.assertRaises(installer.Conflict):
            self.install()
        with self.assertRaises(installer.Conflict):
            installer.apply(self.root, self.manifest(), self.source, uninstall=True)
        self.assertEqual("keep", (self.root / "revibe" / "notes.txt").read_text())

    def test_preflight_does_not_write(self):
        installer.preflight(self.root, self.manifest())
        self.assertFalse(self.root.exists())

    def test_removed_product_skill_is_removed_on_upgrade(self):
        import shutil
        extra = self.source / "revibe-old"
        extra.mkdir()
        (extra / "SKILL.md").write_text("old")
        self.install()
        shutil.rmtree(extra)
        self.install()
        self.assertFalse((self.root / "revibe-old").exists())

    def test_manifest_traversal_is_rejected(self):
        for name in ("../revibe", "revibe/../../outside", "REVibe", "revibe:outside"):
            with self.subTest(name=name), self.assertRaises(installer.Conflict):
                installer.validate_manifest({"format": 1, "skills": {name: {"SKILL.md": "0" * 64}}})
        for filename in ("../outside", "/outside", "C:/outside", "a\\b", "a//b"):
            with self.subTest(filename=filename), self.assertRaises(installer.Conflict):
                installer.validate_manifest({"format": 1, "skills": {"revibe": {"SKILL.md": "0" * 64, filename: "0" * 64}}})

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

    def test_multiple_destinations_preflight_before_writing(self):
        project = self.base / "project"
        conflict = project / ".claude" / "skills" / "revibe"
        conflict.mkdir(parents=True)
        (conflict / "user-file.txt").write_text("keep")
        with patch.object(installer, "source_manifest", return_value=self.manifest()):
            result = installer.main(["--codex", "--claude", "--project", str(project)])
        self.assertEqual(1, result)
        self.assertFalse((project / ".agents").exists())

    def test_native_paths_and_xdg(self):
        from argparse import Namespace
        values = {h: False for h in installer.PATHS}
        args = Namespace(**values, all=True, destination=None, project=str(self.base), user=False)
        self.assertEqual(5, len(installer.destinations(args)))
        args.all = False
        args.opencode = True
        args.project = None
        with patch.dict(os.environ, {"XDG_CONFIG_HOME": str(self.base / "config")}):
            self.assertEqual([self.base / "config" / "opencode" / "skills"], installer.destinations(args))

    def test_local_scope_defaults_to_portable_target_and_is_repeatable(self):
        project = self.base / "project"
        self.assertEqual(0, installer.main(["--local", "--project", str(project)]))
        self.assertTrue((project / ".agents" / "skills" / "revibe" / "SKILL.md").is_file())
        self.assertEqual(0, installer.main(["--local", "--project", str(project)]))
        self.assertEqual(11, len(list((project / ".agents" / "skills").glob("*/SKILL.md"))))

    def test_local_scope_defaults_to_portable_target_even_with_marker(self):
        project = self.base / "project"
        (project / ".claude").mkdir(parents=True)
        self.assertEqual(0, installer.main(["--local", "--project", str(project)]))
        self.assertTrue((project / ".agents" / "skills" / "revibe" / "SKILL.md").is_file())

    def test_auto_scope_adapts_only_to_one_clear_marker(self):
        project = self.base / "project"
        (project / ".claude").mkdir(parents=True)
        self.assertEqual(0, installer.main(["--local", "--project", str(project), "--harness", "auto"]))
        self.assertTrue((project / ".claude" / "skills" / "revibe" / "SKILL.md").is_file())

        ambiguous = self.base / "ambiguous"
        (ambiguous / ".claude").mkdir(parents=True)
        (ambiguous / ".cursor").mkdir()
        self.assertEqual(0, installer.main(["--local", "--project", str(ambiguous), "--harness", "auto"]))
        self.assertTrue((ambiguous / ".agents" / "skills" / "revibe" / "SKILL.md").is_file())

    def test_explicit_harness_overrides_auto_detection(self):
        project = self.base / "project"
        (project / ".claude").mkdir(parents=True)
        self.assertEqual(0, installer.main(["--local", "--project", str(project), "--harness", "cursor"]))
        self.assertTrue((project / ".cursor" / "skills" / "revibe" / "SKILL.md").is_file())

    def test_global_scope_uses_user_home(self):
        user_home = self.base / "home"
        with patch.object(installer.Path, "home", return_value=user_home):
            self.assertEqual(0, installer.main(["--global", "--harness", "codex"]))
        self.assertTrue((user_home / ".agents" / "skills" / "revibe" / "SKILL.md").is_file())

    def test_bad_cli_is_rejected(self):
        self.root.mkdir(parents=True)
        self.assertEqual(1, installer.main([]))
        self.assertEqual(1, installer.main(["--destination", str(self.root), "--codex"]))


if __name__ == "__main__":
    unittest.main()
