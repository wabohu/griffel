"""Messages and prompts via external programs: dunst (notify-send) and rofi.

Both functions report back whether it worked. If it does not work (program
missing, error, timeout), the caller uses the Qt solution (Toast or
QMessageBox). The tool never crashes because of this.
"""
import os
import shutil
import subprocess
import sys
from importlib.resources import files
from pathlib import Path

# Package data: found in the source folder and in the installed package (pyproject.toml, package-data)
ROFI_THEME = Path(str(files("griffel") / "data" / "griffel.rasi"))
NOT_AVAILABLE = object()  # return value of ask() when rofi is not usable

_last_notification_id = None  # replace the same notification instead of stacking new ones


def _headless():
    """Without a real screen (tests with QT_QPA_PLATFORM=offscreen) never create external
    windows or notifications on the desktop."""
    return os.environ.get("QT_QPA_PLATFORM") == "offscreen"


def notify(text, error=False, timeout_ms=3000):
    """Notification via notify-send (dunst). Returns: True if it went out."""
    global _last_notification_id
    if _headless() or not shutil.which("notify-send"):
        return False
    cmd = ["notify-send", "--app-name=griffel", "--print-id",
           f"--urgency={'critical' if error else 'normal'}", f"--expire-time={timeout_ms}"]
    if _last_notification_id:
        cmd.append(f"--replace-id={_last_notification_id}")
    cmd += ["griffel", text]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=3, check=True)
    except (OSError, subprocess.SubprocessError) as e:
        print(f"[notify] notify-send failed: {e}", file=sys.stderr)
        return False
    _last_notification_id = result.stdout.strip() or None
    return True


def rofi_command(question, theme=None, colors=None, colors_file=None):
    """Command line for rofi -dmenu. theme: own rasi file (None = griffel.rasi),
    colors: {variable: "#rrggbb"} for the theme (the bar colors), colors_file: rasi file
    that is loaded instead of colors ([ui] rofi_colors)."""
    theme = Path(theme).expanduser() if theme else ROFI_THEME
    # -i: case-insensitive, -matching fuzzy: "dc" finds "Discard", "cn" finds "Cancel"
    cmd = ["rofi", "-dmenu", "-i", "-matching", "fuzzy", "-no-custom", "-format", "i",
           "-p", "", "-mesg", question]
    if theme.is_file():
        cmd += ["-theme", str(theme)]
    colors_file = Path(colors_file).expanduser() if colors_file else None
    if colors_file and colors_file.is_file():
        cmd += ["-theme-str", f'@import "{colors_file}"']
    else:
        if colors_file:
            print(f"[ui] rofi_colors: {colors_file} not found, using the bar colors", file=sys.stderr)
        if colors:
            values = " ".join(f"{name}: {value};" for name, value in colors.items())
            cmd += ["-theme-str", f"* {{ {values} }}"]
    return cmd


def ask(question, choices, theme=None, colors=None, colors_file=None):
    """Choice via rofi -dmenu. Returns: index of the choice, None on Esc/cancel,
    NOT_AVAILABLE if rofi is missing or does not start (then use a Qt dialog).
    theme, colors, colors_file: see rofi_command.

    rofi grabs the keyboard itself; an own keyboard grab would have to be
    released beforehand (the tool no longer uses one, see Canvas.show_overlay).
    """
    if _headless() or not shutil.which("rofi"):
        return NOT_AVAILABLE
    cmd = rofi_command(question, theme, colors, colors_file)
    try:
        result = subprocess.run(cmd, input="\n".join(choices), capture_output=True,
                                text=True, timeout=300)
    except (OSError, subprocess.SubprocessError) as e:
        print(f"[notify] rofi failed: {e}", file=sys.stderr)
        return NOT_AVAILABLE
    if result.returncode == 1:  # Esc
        return None
    try:
        index = int(result.stdout.strip())
    except ValueError:
        print(f"[notify] rofi: unexpected output {result.stdout!r} {result.stderr.strip()!r}",
              file=sys.stderr)
        return NOT_AVAILABLE
    return index if 0 <= index < len(choices) else None
