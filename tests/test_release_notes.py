import importlib.util
from pathlib import Path
import unittest
import subprocess
import sys
import tempfile

SPEC = importlib.util.spec_from_file_location("release_notes", Path(__file__).parents[1] / "tools" / "release_notes.py")
release_notes = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(release_notes)


class ReleaseNotesTests(unittest.TestCase):
    def test_highlights_exclude_historical_releases(self):
        changelog = "# Changelog\n\n## [Unreleased]\n\n### Changed\n\n- New loop\n\n## [1.2.0]\n\n- Old change\n"
        result = release_notes.notes("1.2.0", "abc123", "v1.2.0", "- Fix loop (abc123)", changelog)
        self.assertIn("New loop", result)
        self.assertNotIn("Old change", result)
        self.assertIn("Fix loop (abc123)", result)

    def test_empty_highlights_still_include_direct_commits(self):
        result = release_notes.notes("1.2.0", "abc123", "v1.2.0", "- Fix typo (abc123)", "")
        self.assertNotIn("Maintained changelog highlights", result)
        self.assertIn("Fix typo (abc123)", result)

    def test_rerun_keeps_tag_and_commit_range(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            def git(*args):
                return subprocess.check_output(["git", *args], cwd=root, text=True).strip()
            git("init", "-q")
            git("config", "user.email", "test@example.invalid")
            git("config", "user.name", "Release test")
            (root / "VERSION").write_text("1.2.0\n", encoding="utf-8")
            (root / "CHANGELOG.md").write_text("## [Unreleased]\n\n", encoding="utf-8")
            git("add", ".")
            git("commit", "-qm", "Original release")
            git("tag", "v1.2.0")
            (root / "change.txt").write_text("new", encoding="utf-8")
            git("add", ".")
            git("commit", "-qm", "Direct push change")
            script = str(Path(release_notes.__file__).resolve())
            subprocess.check_call([sys.executable, script], cwd=root, stdout=subprocess.DEVNULL)
            tag = (root / "dist/release-tag.txt").read_text(encoding="utf-8")
            first = (root / "dist/release-notes.md").read_text(encoding="utf-8")
            git("tag", tag)
            subprocess.check_call([sys.executable, script], cwd=root, stdout=subprocess.DEVNULL)
            self.assertEqual(tag, (root / "dist/release-tag.txt").read_text(encoding="utf-8"))
            self.assertEqual(first, (root / "dist/release-notes.md").read_text(encoding="utf-8"))
            self.assertIn("Direct push change", first)
            self.assertNotIn("Original release", first)


if __name__ == "__main__":
    unittest.main()
