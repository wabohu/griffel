#!/usr/bin/env python3
"""Start griffel from the source folder, without installing it.

    python run.py              annotate a screenshot of the monitor under the mouse
    python run.py --board      empty whiteboard (all options: python run.py --help)

Must stay executable: a symlink in ~/.local/bin can point to it (hotkeys).
"""
import sys
from pathlib import Path

# Transition (plan-pakete.md, step 1): the modules still import each other flat
sys.path.insert(0, str(Path(__file__).resolve().parent / "src" / "griffel"))

from app import main  # noqa: E402

if __name__ == "__main__":
    main()
