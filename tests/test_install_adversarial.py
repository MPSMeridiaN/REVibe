import contextlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import patch


SPEC = importlib.util.spec_from_file_location(
    "installer_adversarial", Path(__file__).parents[1] / "install.py"
)
installer = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(installer)


@contextlib.contextmanager
def without_path_is_junction():
    """Emulate Python 3.10, where pathlib has no is_junction method."""
    had_method = hasattr(Path, "is_junction")
    saved_method = getattr(Path, "is_junction", None)
    if had_method:
        delattr(Path, "is_junction")
    try:
        yield
    finally:
        if had_method:
            Path.is_junction = saved_method


class AdversarialInstallerTests(unittest.TestCase):
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

    def make_junction(self, link, target):
        if os.name != "nt":
            self.skipTest("Windows junction test")
        target.mkdir(parents=True, exist_ok=True)
        result = subprocess.run(
            ["cmd", "/c", "mklink", "/J", str(link), str(target)],
            capture_output=True,
            text=True,
        )
        if result.returncode:
            self.skipTest(f"junction creation unavailable: {result.stderr}")
        self.addCleanup(lambda: os.rmdir(link) if os.path.lexists(link) else None)

    def test_empty_user_directory_inside_owned_skill_is_not_deleted(self):
        self.install()
        keep = self.root / "revibe" / "user-empty-directory"
        keep.mkdir()
        (self.skill / "SKILL.md").write_text("v2")

        with self.assertRaises(installer.Conflict):
            installer.apply(self.root, self.manifest(), self.source)
        self.assertTrue(keep.is_dir())

    def test_legacy_file_only_manifest_remains_updatable(self):
        references = self.skill / "references"
        references.mkdir()
        (references / "reference.md").write_text("reference")
        self.install()
        manifest_path = self.root / installer.MANIFEST
        legacy = json.loads(manifest_path.read_text())
        legacy["format"] = 1
        for files in legacy["skills"].values():
            for filename in list(files):
                if filename.endswith("/"):
                    del files[filename]
        manifest_path.write_text(json.dumps(legacy))
        (self.skill / "SKILL.md").write_text("v2")

        installer.apply(self.root, self.manifest(), self.source)
        self.assertEqual("v2", (self.root / "revibe" / "SKILL.md").read_text())

    def test_python_310_junction_destination_is_rejected(self):
        outside = self.base / "outside"
        link = self.base / "junction-root"
        self.make_junction(link, outside)

        with without_path_is_junction():
            with self.assertRaises(installer.Conflict):
                installer.apply(link, self.manifest(), self.source)
        self.assertFalse((outside / "revibe").exists())

    def test_linked_source_is_rejected(self):
        linked_source = self.base / "source-junction"
        self.make_junction(linked_source, self.source)

        with self.assertRaises(installer.Conflict):
            installer.apply(self.root, self.manifest(), linked_source)
        self.assertFalse(self.root.exists())

    def test_keyboard_interrupt_before_journal_can_be_recovered(self):
        self.install()
        before = installer.inventory(self.root / "revibe")
        (self.skill / "SKILL.md").write_text("v2")
        real_copytree = installer.shutil.copytree

        def interrupt_during_backup(src, dst, *args, **kwargs):
            if Path(dst).parent.name == "old":
                raise KeyboardInterrupt()
            return real_copytree(src, dst, *args, **kwargs)

        with patch.object(installer.shutil, "copytree", side_effect=interrupt_during_backup):
            with self.assertRaises(KeyboardInterrupt):
                self.install()

        self.assertTrue((self.root / installer.TRANSACTION).exists())
        installer.recover(self.root)
        self.assertEqual(before, installer.inventory(self.root / "revibe"))
        self.assertFalse((self.root / installer.TRANSACTION).exists())

    def test_interrupt_before_prepared_phase_discards_transaction(self):
        self.install()
        before = installer.inventory(self.root / "revibe")
        (self.skill / "SKILL.md").write_text("v2")
        real_replace = installer.os.replace

        def interrupt_prepared_marker(src, dst):
            if Path(src).name == "prepared.json":
                raise KeyboardInterrupt()
            return real_replace(src, dst)

        with patch.object(installer.os, "replace", side_effect=interrupt_prepared_marker):
            with self.assertRaises(KeyboardInterrupt):
                self.install()

        installer.recover(self.root)
        self.assertEqual(before, installer.inventory(self.root / "revibe"))
        self.assertFalse((self.root / installer.TRANSACTION).exists())

    def test_interrupt_after_prepared_phase_rolls_back_safely(self):
        self.install()
        before = installer.inventory(self.root / "revibe")
        (self.skill / "SKILL.md").write_text("v2")
        real_remove_tree = installer.remove_tree

        def interrupt_first_replacement(path, parent):
            if path == self.root / "revibe":
                raise KeyboardInterrupt()
            return real_remove_tree(path, parent)

        with patch.object(installer, "remove_tree", side_effect=interrupt_first_replacement):
            with self.assertRaises(KeyboardInterrupt):
                self.install()

        installer.recover(self.root)
        self.assertEqual(before, installer.inventory(self.root / "revibe"))
        self.assertFalse((self.root / installer.TRANSACTION).exists())

    def test_interrupt_after_prepared_journal_rename_rolls_back(self):
        self.install()
        before = installer.inventory(self.root / "revibe")
        (self.skill / "SKILL.md").write_text("v2")
        real_replace = installer.os.replace

        def replace_prepared_then_interrupt(src, dst):
            result = real_replace(src, dst)
            if Path(src).name == "prepared.json":
                raise KeyboardInterrupt()
            return result

        with patch.object(installer.os, "replace", side_effect=replace_prepared_then_interrupt):
            with self.assertRaises(KeyboardInterrupt):
                self.install()

        journal = json.loads((self.root / installer.TRANSACTION / "journal.json").read_text())
        self.assertEqual("prepared", journal["phase"])
        installer.recover(self.root)
        self.assertEqual(before, installer.inventory(self.root / "revibe"))
        self.assertFalse((self.root / installer.TRANSACTION).exists())

    def test_interrupt_after_manifest_replace_rolls_back(self):
        self.install()
        before = installer.inventory(self.root / "revibe")
        (self.skill / "SKILL.md").write_text("v2")
        real_replace = installer.os.replace

        def replace_manifest_then_interrupt(src, dst):
            result = real_replace(src, dst)
            if Path(src).name == "manifest.json":
                raise KeyboardInterrupt()
            return result

        with patch.object(installer.os, "replace", side_effect=replace_manifest_then_interrupt):
            with self.assertRaises(KeyboardInterrupt):
                self.install()

        self.assertEqual("v2", (self.root / "revibe" / "SKILL.md").read_text())
        installer.recover(self.root)
        self.assertEqual(before, installer.inventory(self.root / "revibe"))
        self.assertFalse((self.root / installer.TRANSACTION).exists())

    def test_new_unowned_skill_created_during_install_is_not_deleted(self):
        (self.skill / "SKILL.md").write_text("v1")
        self.install()
        new_skill = self.source / "revibe-new"
        new_skill.mkdir()
        (new_skill / "SKILL.md").write_text("product")
        new_manifest = self.manifest()

        real_write_json = installer.write_json

        def write_journal_then_add_user_skill(path, data):
            real_write_json(path, data)
            if Path(path).name == "journal.json":
                user_skill = self.root / "revibe-new"
                user_skill.mkdir()
                (user_skill / "SKILL.md").write_text("user-owned")

        with patch.object(installer, "write_json", side_effect=write_journal_then_add_user_skill):
            with self.assertRaises(installer.Conflict):
                installer.apply(self.root, new_manifest, self.source)
        self.assertEqual("user-owned", (self.root / "revibe-new" / "SKILL.md").read_text())
        self.assertFalse((self.root / installer.TRANSACTION).exists())

    def test_unowned_manifest_created_during_install_is_not_overwritten(self):
        new_manifest = self.manifest()
        real_write_json = installer.write_json

        def write_journal_then_add_user_manifest(path, data):
            real_write_json(path, data)
            if Path(path).name == "journal.json":
                (self.root / installer.MANIFEST).write_text("user metadata")

        with patch.object(installer, "write_json", side_effect=write_journal_then_add_user_manifest):
            with self.assertRaises(installer.Conflict):
                installer.apply(self.root, new_manifest, self.source)
        self.assertEqual("user metadata", (self.root / installer.MANIFEST).read_text())
        self.assertFalse((self.root / installer.TRANSACTION).exists())

    def test_recover_refuses_to_race_a_live_install(self):
        self.install()
        (self.skill / "SKILL.md").write_text("v2")
        ready = threading.Event()
        release = threading.Event()
        result = {}
        real_write_json = installer.write_json

        def pause_after_journal(path, data):
            real_write_json(path, data)
            if Path(path).name == "journal.json":
                ready.set()
                release.wait(5)

        def run_install():
            try:
                result["value"] = self.install()
            except BaseException as exc:  # Keep the test thread from hiding the race.
                result["error"] = exc

        with patch.object(installer, "write_json", side_effect=pause_after_journal):
            thread = threading.Thread(target=run_install, daemon=True)
            thread.start()
            try:
                self.assertTrue(ready.wait(5))
                try:
                    installer.recover(self.root)
                except installer.Conflict:
                    recovered_while_live = False
                else:
                    recovered_while_live = True
            finally:
                release.set()
                thread.join(5)

        self.assertFalse(recovered_while_live)
        self.assertNotIn("error", result)
        self.assertEqual("v2", (self.root / "revibe" / "SKILL.md").read_text())

    def test_live_operation_lock_blocks_second_process(self):
        ready = self.base / "lock-ready"
        release = self.base / "lock-release"
        child_code = (
            "from pathlib import Path\n"
            "import sys, time\n"
            "import install\n"
            "root, ready, release = map(Path, sys.argv[1:])\n"
            "with install.operation_lock(root):\n"
            "    ready.write_text('ready')\n"
            "    while not release.exists():\n"
            "        time.sleep(0.01)\n"
        )
        child = subprocess.Popen(
            [
                sys.executable,
                "-c",
                child_code,
                str(self.root),
                str(ready),
                str(release),
            ],
            cwd=Path(__file__).parents[1],
        )
        try:
            deadline = time.monotonic() + 5
            while not ready.exists() and child.poll() is None and time.monotonic() < deadline:
                time.sleep(0.01)
            self.assertTrue(ready.exists(), child.poll())
            with self.assertRaises(installer.Conflict):
                installer.apply(self.root, self.manifest(), self.source)
        finally:
            release.write_text("release")
            child.wait(timeout=5)
        self.assertEqual(0, child.returncode)

    def test_recover_checks_live_lock_before_no_transaction_result(self):
        self.root.mkdir(parents=True)
        ready = self.base / "lock-ready"
        release = self.base / "lock-release"
        child_code = (
            "from pathlib import Path\n"
            "import sys, time\n"
            "import install\n"
            "root, ready, release = map(Path, sys.argv[1:])\n"
            "with install.operation_lock(root):\n"
            "    ready.write_text('ready')\n"
            "    while not release.exists():\n"
            "        time.sleep(0.01)\n"
        )
        child = subprocess.Popen(
            [
                sys.executable,
                "-c",
                child_code,
                str(self.root),
                str(ready),
                str(release),
            ],
            cwd=Path(__file__).parents[1],
        )
        try:
            deadline = time.monotonic() + 5
            while not ready.exists() and child.poll() is None and time.monotonic() < deadline:
                time.sleep(0.01)
            self.assertTrue(ready.exists(), child.poll())
            with self.assertRaises(installer.Conflict):
                installer.recover(self.root)
        finally:
            release.write_text("release")
            child.wait(timeout=5)
        self.assertEqual(0, child.returncode)

    def test_recovery_accepts_equivalent_destination_path(self):
        root_alias = self.base / "target" / "skills" / ".." / "skills"
        root_canonical = root_alias.resolve()
        installer.apply(root_alias, self.manifest(), self.source)
        (self.skill / "SKILL.md").write_text("v2")
        real_replace = installer.os.replace

        def interrupt_manifest_replace(src, dst):
            if Path(src).name == "manifest.json":
                raise KeyboardInterrupt()
            return real_replace(src, dst)

        with patch.object(installer.os, "replace", side_effect=interrupt_manifest_replace):
            with self.assertRaises(KeyboardInterrupt):
                installer.apply(root_alias, self.manifest(), self.source)

        installer.recover(root_canonical)
        self.assertEqual("v1", (root_canonical / "revibe" / "SKILL.md").read_text())

    def test_legacy_transaction_without_phase_can_be_recovered(self):
        self.install()
        before = installer.inventory(self.root / "revibe")
        (self.skill / "SKILL.md").write_text("v2")
        real_replace = installer.os.replace

        def interrupt_manifest_replace(src, dst):
            if Path(src).name == "manifest.json":
                raise KeyboardInterrupt()
            return real_replace(src, dst)

        with patch.object(installer.os, "replace", side_effect=interrupt_manifest_replace):
            with self.assertRaises(KeyboardInterrupt):
                self.install()
        journal_path = self.root / installer.TRANSACTION / "journal.json"
        legacy_journal = json.loads(journal_path.read_text())
        legacy_journal.pop("phase")
        journal_path.write_text(json.dumps(legacy_journal))

        installer.recover(self.root)
        self.assertEqual(before, installer.inventory(self.root / "revibe"))
        self.assertFalse((self.root / installer.TRANSACTION).exists())

    def test_corrupt_old_backup_is_rejected_before_replacement(self):
        self.install()
        before = installer.inventory(self.root / "revibe")
        (self.skill / "SKILL.md").write_text("v2")
        real_copytree = installer.shutil.copytree

        def corrupt_old_backup(src, dst, *args, **kwargs):
            result = real_copytree(src, dst, *args, **kwargs)
            if Path(dst).parent.name == "old":
                (Path(dst) / "SKILL.md").write_text("corrupt backup")
            return result

        real_replace = installer.os.replace

        def fail_manifest_replace(src, dst):
            if Path(src).name == "manifest.json":
                raise OSError("simulated manifest failure")
            return real_replace(src, dst)

        with patch.object(installer.shutil, "copytree", side_effect=corrupt_old_backup):
            with patch.object(installer.os, "replace", side_effect=fail_manifest_replace):
                with self.assertRaises(installer.Conflict):
                    self.install()
        self.assertEqual(before, installer.inventory(self.root / "revibe"))
        self.assertFalse((self.root / installer.TRANSACTION).exists())


if __name__ == "__main__":
    unittest.main()
