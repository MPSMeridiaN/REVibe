import importlib.util
import json
import re
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).parents[1]
SPEC = importlib.util.spec_from_file_location("packager", ROOT / "tools" / "package.py")
packager = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(packager)


class DistributionTests(unittest.TestCase):
    def test_release_metadata_is_consistent(self):
        package = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))
        version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        self.assertEqual("1.0.3", version)
        self.assertEqual(version, package["version"])
        self.assertEqual("bin/revibe.mjs", package["bin"]["revibe"])
        self.assertIn("product", package["files"])
        self.assertNotIn("tests", package["files"])

    def test_reproducible_package_installs_without_repository(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            first = packager.build(base / "a").read_bytes()
            second_path = packager.build(base / "b")
            self.assertEqual(first, second_path.read_bytes())
            with zipfile.ZipFile(second_path) as bundle:
                names = bundle.namelist()
                self.assertFalse(any("/tests/" in n or "/tools/" in n or "/docs/" in n or "GOAL.md" in n for n in names))
                self.assertIn("revibe/install.py", names)
                self.assertIn("revibe/VERSION", names)
                bundle.extractall(base / "extracted")
            extracted = base / "extracted" / "revibe"
            destination = base / "space in target" / "skills"
            def run(*flags):
                result = subprocess.run([sys.executable, str(extracted / "install.py"), "--destination", str(destination), *flags], capture_output=True, text=True)
                self.assertEqual(0, result.returncode, result.stderr)
                return result.stdout
            run("--dry-run")
            self.assertFalse(destination.exists())
            run()
            skills = list(destination.glob("*/SKILL.md"))
            self.assertEqual(11, len(skills))
            self.assertTrue((destination / "revibe" / "references" / "protocol.md").is_file())
            self.assertEqual((ROOT / "LICENSE").read_bytes(), (destination / "revibe" / "LICENSE").read_bytes())
            for document in destination.rglob("*.md"):
                for target in re.findall(r"\]\(([^)]+)\)", document.read_text(encoding="utf-8")):
                    if "://" not in target and not target.startswith("#"):
                        self.assertTrue((document.parent / target.split("#")[0]).is_file(), f"Broken installed reference: {document}: {target}")
            self.assertIn("Already current", run())
            run("--uninstall")
            self.assertEqual([], list(destination.glob("*/SKILL.md")))

    def test_all_native_targets_in_isolated_project(self):
        with tempfile.TemporaryDirectory() as temp:
            result = subprocess.run([sys.executable, str(ROOT / "install.py"), "--all", "--project", temp], capture_output=True, text=True)
            self.assertEqual(0, result.returncode, result.stderr)
            for location in (".agents", ".claude", ".opencode", ".cursor", ".gemini"):
                self.assertEqual(11, len(list((Path(temp) / location / "skills").glob("*/SKILL.md"))))


if __name__ == "__main__":
    unittest.main()
