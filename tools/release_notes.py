"""Prepare per-commit release metadata; publishing belongs to GitHub Actions."""
from pathlib import Path
import re
import subprocess


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], text=True, encoding="utf-8").strip()


def notes(version: str, sha: str, previous: str, commits: str, changelog: str) -> str:
    section = re.search(r"^## \[Unreleased\]\s*\n(.*?)(?=^## |\Z)", changelog, re.M | re.S)
    highlights = section.group(1).strip() if section else ""
    body = f"Built from `{sha}`. Product version: `{version}`.\n\n"
    if highlights:
        body += f"## Maintained changelog highlights\n\n{highlights}\n\n"
    body += f"## Commits since {previous or 'the initial commit'}\n\n{commits}\n\n"
    body += "## Install\n\n```sh\nnpx -y MPSMeridiaN/REVibe --local\n```\n\n"
    body += "The command follows main. For this exact build, download `revibe.zip` below; verify it with `SHA256SUMS`.\n"
    return body


def main() -> None:
    version = Path("VERSION").read_text(encoding="utf-8").strip()
    sha = git("rev-parse", "HEAD")
    tag = f"v{version}+sha.{sha[:12]}"
    # Exclude HEAD so rerunning a published commit keeps the same notes range.
    candidates = git("tag", "--merged", "HEAD^", "--list", "v*").splitlines()
    previous = ""
    if candidates:
        previous = min(candidates, key=lambda ref: int(git("rev-list", "--count", f"{ref}..HEAD")))
    revision_range = f"{previous}..HEAD" if previous else "HEAD"
    commits = git("log", "--reverse", "--format=- %s (%h)", revision_range)
    changelog = Path("CHANGELOG.md").read_text(encoding="utf-8")
    if previous and not git("diff", previous, "HEAD", "--", "CHANGELOG.md"):
        changelog = ""  # Do not repeat unchanged maintained highlights.
    output = Path("dist")
    output.mkdir(exist_ok=True)
    (output / "release-tag.txt").write_text(tag, encoding="utf-8")
    (output / "release-notes.md").write_text(notes(version, sha, previous, commits, changelog), encoding="utf-8")
    print(tag)


if __name__ == "__main__":
    main()
