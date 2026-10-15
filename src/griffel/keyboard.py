"""Keyboard picture of the key overview (?): which keys it shows and where.

The picture shows the left half of a keyboard, 3 rows of an outer column plus 5 letters,
in one of three shapes ([help] keyboard):
    row     normal keyboard (ANSI): rows offset, wide tab / caps / shift on the outside
    column  column stagger like split keyboards (Corne, Kyria), offsets from [help] stagger
    ortho   plain grid (Planck, Preonic)
and with the letters of a layout ([help] layout, "auto" asks setxkbmap). Only the picture
depends on it, the keys themselves are always Qt key symbols.

No Qt here: caps() returns positions in key units, ui.HelpPanel turns them into pixels.
"""
import re
import shutil
import subprocess
from collections import namedtuple
from functools import cache

KINDS = ("row", "column", "ortho")

# Letters of the left half (top, home, bottom row) and the whole rows for sorting the color
# fields of the overview by keyboard row (number row first)
LAYOUTS = {
    "qwerty": ("qwert", "asdfg", "zxcvb"),
    "qwertz": ("qwert", "asdfg", "yxcvb"),  # z sits right of t, outside the picture
    "azerty": ("azert", "qsdfg", "wxcvb"),
}
FULL_ROWS = {
    "qwerty": ("1234567890", "qwertyuiop", "asdfghjkl;", "zxcvbnm,./"),
    "qwertz": ("1234567890", "qwertzuiop", "asdfghjkl", "yxcvbnm,.-"),
    "azerty": ("1234567890", "azertyuiop", "qsdfghjklm", "wxcvbn,;:!"),
}
# setxkbmap layout names (first two letters are enough) -> layout of the picture
QWERTZ = {"de", "at", "ch", "cz", "hu", "sk", "si", "hr"}
AZERTY = {"fr", "be"}

# column: how far each of the 6 columns (outer one first) sits lower, in key heights
DEFAULT_STAGGER = (0.78, 0.78, 0.26, 0.0, 0.26, 0.38)
DEFAULT_OUTER = ("tab", "", "")  # outer column for column and ortho, top to bottom
# row: wide keys on the outside (width in key widths, ANSI), the letters start right of them
ROW_OUTER = (("tab", 1.5), ("caps", 1.75), ("shift", 2.25))

# One key: name (as the keymap writes it, "" = empty key), position and width in key units
Cap = namedtuple("Cap", "key x y width")


def caps(kind, layout, stagger=DEFAULT_STAGGER, outer=DEFAULT_OUTER):
    """Keys of the picture: [Cap], outer column first, then column by column."""
    letters = LAYOUTS[layout]
    if kind == "row":
        result = [Cap(key, 0.0, row, width) for row, (key, width) in enumerate(ROW_OUTER)]
        result += [Cap(letters[row][col], width + col, row, 1.0)
                   for col in range(5) for row, (_, width) in enumerate(ROW_OUTER)]
        return result
    offsets = stagger if kind == "column" else (0.0,) * 6
    result = [Cap(key, 0.0, offsets[0] + row, 1.0) for row, key in enumerate(outer)]
    result += [Cap(letters[row][col], col + 1.0, offsets[col + 1] + row, 1.0)
               for col in range(5) for row in range(3)]
    return result


def picture_keys(cap_list):
    """Keys that can carry an action in the picture (caps and shift cannot)."""
    return {cap.key for cap in cap_list if cap.key and cap.key not in ("caps", "shift")}


def parse_layout(query):
    """Output of `setxkbmap -query` -> picture layout; unknown or missing -> qwerty.
    With several layouts ("us,de") the first one counts."""
    match = re.search(r"^layout:\s*(\S+)", query or "", re.MULTILINE)
    name = match.group(1).split(",")[0][:2].lower() if match else ""
    return "qwertz" if name in QWERTZ else "azerty" if name in AZERTY else "qwerty"


@cache
def detect_layout():
    """Picture layout of the running X session (once per start); without setxkbmap qwerty."""
    if not shutil.which("setxkbmap"):
        return "qwerty"
    try:
        result = subprocess.run(["setxkbmap", "-query"], capture_output=True, text=True, timeout=2)
    except (OSError, subprocess.SubprocessError):
        return "qwerty"
    return parse_layout(result.stdout if result.returncode == 0 else "")
