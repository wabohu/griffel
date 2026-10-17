#!/usr/bin/env python3
"""All GUI scenarios (tests/gui/test_*.py) one after another, each in its own X server.
The scenarios in WITH_I3 run a second time under i3 (focus handling without herbstluftwm),
if i3 is installed.

    python tests/gui/run.py

Exit code 0 = all ok. Screenshots: tests/gui/out/<scenario>/.
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

WITH_I3 = ("test_overlay", "test_board")

here = Path(__file__).resolve().parent
failed = []
runs = [(scenario, None) for scenario in sorted(here.glob("test_*.py"))]
if shutil.which("i3"):
    runs += [(here / f"{name}.py", "i3") for name in WITH_I3]
else:
    print("i3 not installed: skipping the runs under i3\n", flush=True)
for scenario, wm in runs:
    label = f"{scenario.stem} ({wm})" if wm else scenario.stem
    print(f"=== {label}", flush=True)
    env = dict(os.environ, GRIFFEL_TEST_WM=wm) if wm else None
    if subprocess.run([sys.executable, str(scenario)], env=env).returncode != 0:
        failed.append(label)
    print(flush=True)
print("All GUI scenarios OK." if not failed else f"Failed: {', '.join(failed)}")
sys.exit(1 if failed else 0)
