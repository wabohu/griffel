"""Demo pictures for the README, made reproducibly in the test X server.

    python tests/gui/demo.py

Writes docs/images/screenshot.png (a terminal marked up in screenshot mode),
docs/images/whiteboard.png (a small diagram with docked arrows) and
docs/images/overview.png (the key overview). Colors: Tokyo Night Storm from
demo-alacritty.toml and the color selection in DEMO_CONFIG, the same for every run on every
machine. Needs alacritty and bat besides the harness programs (and the font RobotoMono Nerd
Font for the same look). Not a test: run it by hand after visible changes and look at the
pictures.
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from harness import Session, _qt_image, wait  # noqa: E402

IMAGES = Path(__file__).resolve().parents[2] / "docs" / "images"
ALACRITTY = Path(__file__).resolve().parent / "demo-alacritty.toml"

# Appended to the harness config: nine colors, Shift+A S D F G Z X C V in this order
DEMO_CONFIG = """
[colors]
order = ["yellow", "magenta", "cyan", "green", "red", "blue", "white", "bright_black", "foreground"]
default = "yellow"
"""

CONFIG = """\
[server]
host = "0.0.0.0"
port = 8080
workers = 8

[database]
url = "postgres://app@db.internal/shop"
password = "hunter2-correct-horse"
pool_size = 2
timeout = 30

[cache]
backend = "redis"
ttl = 300
"""

# Terminal geometry with demo-alacritty.toml, in screen pixels (1920x1080; the saved pictures
# lack the border, so there everything sits BORDER pixels further up and left)
LINE_1_Y = 146    # middle of line 1
LINE_H = 43       # line height
TEXT_X = 181      # left edge of the file text
CHAR_W = 18.75    # width of one character


def use_colors(s):
    """The demo's Alacritty config and color selection in the session's home."""
    config = s.tmp / "home" / ".config"
    (config / "alacritty").mkdir(parents=True, exist_ok=True)
    (config / "alacritty" / "alacritty.toml").write_text(ALACRITTY.read_text())
    with open(config / "griffel" / "config.toml", "a") as f:
        f.write(DEMO_CONFIG)


def line_y(n):
    return round(LINE_1_Y + (n - 1) * LINE_H)


def start_terminal(s):
    """A fullscreen terminal showing a config file (herbstluftwm tiles it)."""
    config = s.tmp / "server.toml"
    config.write_text(CONFIG)
    shell = ("sleep 1; printf '\\033[?25l$ bat config/server.toml\\n'; "  # after the WM resized it
             f"bat --paging=never --style=numbers,grid --theme=ansi {config}; sleep 600")
    s.spawn(["alacritty", "-e", "sh", "-c", shell], log="terminal")
    time.sleep(3)


def start_overlay(s):
    s.key("alt+Escape")
    wait(lambda: s.griffel_pids(), 10)
    wait(lambda: s.windows_of(s.griffel_pids()[0]), 10)
    time.sleep(0.5)


def click(s, x, y):
    s.move(x, y)
    s.run(["xdotool", "click", "1"])
    time.sleep(0.1)


BORDER = 8  # window border of herbstluftwm (and its antialiasing), cut off


def save(s, shot, name, area=None):
    """Screenshot to docs/images/name; area = (x, y, width, height), otherwise all but the border."""
    IMAGES.mkdir(parents=True, exist_ok=True)
    image = _qt_image(s.screenshot(shot))
    x, y, w, h = area or (BORDER, BORDER, image.width() - 2 * BORDER, image.height() - 2 * BORDER)
    image.copy(x, y, w, h).save(str(IMAGES / name))
    print(f"written: docs/images/{name}")


def screenshot_demo():
    with Session("demo-screenshot") as s:
        use_colors(s)
        start_terminal(s)
        start_overlay(s)
        s.key("b")                                   # show the bar
        # Blur over the password value
        s.key("z")
        s.drag(TEXT_X + round(11 * CHAR_W) - 6, line_y(8) - 20,    # the value after 'password = '
               TEXT_X + round(34 * CHAR_W) + 6, line_y(8) + 20)
        # Markers 1 and 2 left of workers and pool_size
        s.key("c")
        s.key("shift+g")                             # red
        s.key("alt+d")                               # size level 3, readable when scaled down
        click(s, 30, line_y(4))
        click(s, 30, line_y(9))
        # Rectangle around pool_size, arrow from the note to it
        s.key("f")
        s.drag(TEXT_X - 12, line_y(9) - 22, TEXT_X + round(13 * CHAR_W) + 12, line_y(9) + 26)  # 'pool_size = 2'
        s.key("d")
        s.drag(900, 800, TEXT_X + round(13 * CHAR_W) + 24, line_y(9) + 6)
        # Note in monospace
        s.key("t")
        click(s, 860, 825)
        s.key("alt+v")
        s.type("8 workers, 2 connections?")
        s.key("Escape")
        s.key("w")
        click(s, 1700, 900)                          # nothing selected, the select tool's pointer
        s.move(1700, 1000)
        time.sleep(0.4)
        save(s, "screenshot", "screenshot.png")
        s.key("Escape")
        s.key("Escape")


def panel_area(image, inset=4):
    """Bounding box of everything not black above the bar (the overview on an empty screen),
    a few pixels inside its rounded edge."""
    def lit(x, y):
        c = image.pixelColor(x, y)
        return c.red() + c.green() + c.blue() > 30
    height = image.height() - 120   # above the bar
    rows = [y for y in range(0, height, 2) if any(lit(x, y) for x in range(0, image.width(), 8))]
    cols = [x for x in range(0, image.width(), 2) if any(lit(x, y) for y in range(rows[0], rows[-1], 8))]
    return (cols[0] + inset, rows[0] + inset, cols[-1] - cols[0] - 2 * inset, rows[-1] - rows[0] - 2 * inset)


def overview_demo():
    """The key overview on an empty (black) screen, cut to the panel."""
    with Session("demo-overview") as s:
        use_colors(s)
        start_overlay(s)
        s.key("shift+question")
        time.sleep(0.6)
        image = _qt_image(s.screenshot("overview"))
        save(s, "overview", "overview.png", panel_area(image))
        s.key("Escape")
        s.key("Escape")


def label(s, x, y, text):
    """Double click into a shape (select tool) and type its label."""
    s.key("w")
    s.move(x, y)
    s.run(["xdotool", "click", "--repeat", "2", "--delay", "80", "1"])
    time.sleep(0.3)
    s.type(text)
    s.key("Escape")
    time.sleep(0.2)


def whiteboard_demo():
    with Session("demo-whiteboard") as s:
        use_colors(s)
        s.key("alt+Delete")
        wait(lambda: s.griffel_pids() and s.windows_of(s.griffel_pids()[0]), 10)
        time.sleep(0.5)
        # Three boxes and a database ellipse
        s.key("alt+d")
        s.key("shift+f")                             # green
        s.key("f")
        s.drag(260, 280, 560, 420)
        s.key("shift+z")                             # blue
        s.drag(810, 280, 1110, 420)
        s.key("shift+a")                             # yellow
        s.drag(810, 620, 1110, 760)
        s.key("shift+s")                             # magenta
        s.key("g")
        s.drag(1360, 280, 1660, 420)
        label(s, 410, 350, "Browser")
        label(s, 960, 350, "API")
        label(s, 960, 690, "Worker")
        label(s, 1510, 350, "Database")
        # Docked arrows (start and end on the outlines)
        s.key("shift+v")                             # foreground
        s.key("d")
        s.drag(562, 350, 808, 350)
        s.drag(1112, 350, 1358, 350)
        s.drag(960, 422, 960, 618)
        label(s, 685, 350, "JSON")
        label(s, 1235, 350, "SQL")
        # Curved arrow from the worker back to the database, and a note
        s.key("d")
        s.key("d")
        s.run(["xdotool", "mousemove", "1112", "700", "mousedown", "1",
               *[a for x, y in ((1250, 690), (1380, 640), (1470, 560), (1505, 480), (1510, 424))
                 for a in ("mousemove", str(x), str(y), "sleep", "0.02")], "mouseup", "1"])
        s.key("t")
        click(s, 1240, 760)
        s.type("nightly cleanup")
        s.key("Escape")
        s.key("w")
        click(s, 300, 900)
        s.move(1800, 950)
        time.sleep(3)                                # until the message "Arrow: curved" is gone
        save(s, "whiteboard", "whiteboard.png")
        s.key("ctrl+q")
        time.sleep(0.6)
        s.type("discard")
        s.key("Return")


if __name__ == "__main__":
    screenshot_demo()
    overview_demo()
    whiteboard_demo()
