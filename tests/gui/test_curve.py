#!/usr/bin/env python3
"""GUI test curved arrow (roadmap 21): d d = curved, a shaky arc becomes a round curve,
the select tool shows four handles with guide lines, dragging the end handle reshapes it,
the history entry contains the curved arrow.

    python tests/gui/test_curve.py

Screenshots: tests/gui/out/curve/ (look at them: is the curve round?). Exit code 0 = all ok.
"""
import math
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from harness import Session, check, load_elements, summary, wait  # noqa: E402

# Quarter circle around (1100, 700) with radius 300, from (800, 700) up to (1100, 400), shaky
ARC = [(round(1100 - 300 * math.cos(a)) + (5 if i % 2 else -5), round(700 - 300 * math.sin(a)))
       for i, a in enumerate(math.pi / 2 * i / 30 for i in range(31))]
ARC[0], ARC[-1] = (800, 700), (1100, 400)


def main():
    with Session("curve") as s:
        s.key("alt+Escape")
        check("overlay started", wait(lambda: s.griffel_pids(), 10))
        pid = s.griffel_pids()[0]
        wait(lambda: s.windows_of(pid), 10)
        time.sleep(0.4)
        s.key("d")
        s.key("d")                                 # arrow again: curved
        time.sleep(0.2)
        moves = [arg for x, y in ARC[1:] for arg in ("mousemove", str(x), str(y))]
        s.run(["xdotool", "mousemove", *map(str, ARC[0]), "mousedown", "1", *moves, "mouseup", "1"])
        time.sleep(0.4)
        s.screenshot("01-curve")
        s.key("w")
        s.move(1100 - round(300 * math.cos(math.pi / 4)), 700 - round(300 * math.sin(math.pi / 4)))
        s.run(["xdotool", "click", "1"])           # select on the curve
        time.sleep(0.3)
        s.screenshot("02-handles")
        s.drag(1100, 400, 1200, 450)               # end handle: the curve follows, control point along
        time.sleep(0.3)
        s.screenshot("03-end-dragged")
        s.key("Return")
        check("quit", wait(lambda: not s.griffel_pids(), 10))
        entries = s.history_entries()
        arrows = [e for e in load_elements(entries[0]) if e.tool.name == "ARROW"] if entries else []
        check(f"one curved arrow saved ({[a.arrow_kind for a in arrows]})",
              len(arrows) == 1 and arrows[0].arrow_kind == "curve" and len(arrows[0].points) == 4)
        if arrows:
            ends = [arrows[0].mapToScene(arrows[0].points[i]) for i in (0, 1, 3)]
            start, c1, end = ((round(p.x()), round(p.y())) for p in ends)
            check(f"start in place, end dragged to (1200, 450) ({start}, {end})",
                  abs(start[0] - 800) <= 2 and abs(start[1] - 700) <= 2
                  and abs(end[0] - 1200) <= 2 and abs(end[1] - 450) <= 2)
            # A round quarter circle: the first control point lies straight above the start
            check(f"round: the first control point is above the start ({c1})",
                  abs(c1[0] - 800) < 30 and 450 < c1[1] < 600)
    return summary()


if __name__ == "__main__":
    sys.exit(main())
