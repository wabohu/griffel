#!/usr/bin/env python3
"""Print the CHANGELOG.md section of one version (the release notes).

    python scripts/changelog_section.py 0.1.0

Exit code 1 if the version has no section or its section still says "unreleased"
(the release workflow stops then). Qt-free, used by .github/workflows/release.yml.
"""
import re
import sys
from pathlib import Path

CHANGELOG = Path(__file__).resolve().parent.parent / "CHANGELOG.md"


def section(text, version):
    """(heading, body) of '## [version] - date' in text, or None."""
    match = re.search(rf"^## \[{re.escape(version)}\][^\n]*\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    if not match:
        return None
    return match.group(0).splitlines()[0], match.group(1).strip()


def main(argv):
    if len(argv) != 2:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    version = argv[1].removeprefix("v")
    found = section(CHANGELOG.read_text(), version)
    if found is None:
        print(f"CHANGELOG.md has no section for {version}", file=sys.stderr)
        return 1
    heading, body = found
    if "unreleased" in heading.lower():
        print(f"CHANGELOG.md: {version} is still marked unreleased, put the date there", file=sys.stderr)
        return 1
    print(body)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
