"""GUI test: HiDPI scaling (QT_SCALE_FACTOR=2 on a 1920x1080 screen).

The scene counts in image pixels, not in logical ones: a rectangle dragged from screen pixel
400,300 to 1000,700 is saved there, next to a background of 1920x1080, and lands in the same
place when the history entry is opened again (--last).
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from harness import GRIFFEL, Session, check, load_drawing, summary, wait  # noqa: E402


def rect_ok(rect):
    """The rectangle from 400,300 to 1000,700 (outline included, a few pixels of slack)."""
    return (abs(rect.left() - 400) < 10 and abs(rect.top() - 300) < 10
            and abs(rect.right() - 1000) < 10 and abs(rect.bottom() - 700) < 10)


def main():
    with Session("hidpi", env={"QT_SCALE_FACTOR": "2"}) as s:
        s.key("alt+Escape")
        check("overlay started", wait(lambda: s.griffel_pids(), 10))
        wait(lambda: s.windows_of(s.griffel_pids()[0]), 10)
        time.sleep(0.5)
        s.key("f")                                 # rectangle
        time.sleep(0.2)
        s.drag(400, 300, 1000, 700)
        time.sleep(0.4)
        s.screenshot("01-rect")
        s.key("Return")
        check("quit", wait(lambda: not s.griffel_pids(), 10))
        entries = s.history_entries()
        check("history entry written", len(entries) == 1)
        if not entries:
            return summary()
        background, elements = load_drawing(entries[0])
        check(f"background in full resolution ({background.width()}x{background.height()})",
              (background.width(), background.height()) == (1920, 1080))
        rect = elements[0].sceneBoundingRect() if elements else None
        check(f"rectangle saved in image pixels ({rect and rect.getRect()})", rect is not None and rect_ok(rect))

        s.spawn([sys.executable, str(GRIFFEL), "--last"], log="last")
        check("--last opens the entry", wait(lambda: s.griffel_pids(), 10))
        time.sleep(0.8)
        shot = s.screenshot("02-reopened")
        from PySide6.QtGui import QImage
        image = QImage(str(shot))
        on_outline = image.pixelColor(700, 300).red() > 150 and image.pixelColor(400, 500).red() > 150
        check("reopened: the rectangle is in the same place on screen", on_outline)
        s.key("Escape")
        wait(lambda: not s.griffel_pids(), 10)
    return summary()


if __name__ == "__main__":
    sys.exit(main())
