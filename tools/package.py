"""Build a reproducible, lean distribution without development artifacts."""
from pathlib import Path
import hashlib
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import install


def build(output: Path) -> Path:
    install.source_manifest()
    output.mkdir(parents=True, exist_ok=True)
    archive = output / "revibe.zip"
    files = [ROOT / "install.py", ROOT / "INSTALL.md", ROOT / "CHANGELOG.md", ROOT / "LICENSE", ROOT / "VERSION"]
    files += sorted(p for p in (ROOT / "product").rglob("*") if p.is_file())
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
        for path in sorted(files):
            info = zipfile.ZipInfo("revibe/" + path.relative_to(ROOT).as_posix(), (2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            bundle.writestr(info, path.read_bytes())
    checksum = hashlib.sha256(archive.read_bytes()).hexdigest()
    (output / "SHA256SUMS").write_text(f"{checksum}  revibe.zip\n", encoding="utf-8")
    return archive


if __name__ == "__main__":
    print(build(ROOT / "dist"))
