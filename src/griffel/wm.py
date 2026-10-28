"""Give the focus back after the screenshot overlay.

The overlay bypasses the window manager and takes the keyboard focus itself
(activateWindow). The window manager does not notice this focus change and does not give
it back on close, so afterwards no window had the focus. That is why the tool gives it
back itself on close: to the window the window manager considers focused at that moment.
This also works if you have switched the workspace or window via a hotkey in the meantime.

Two ways to ask for that window ([wm] focus):
- herbstluftwm: herbstclient attr clients.focus.winid
- ewmh: the root property _NET_ACTIVE_WINDOW, which almost every window manager on X11
  keeps (i3, bspwm, awesome, Openbox, Xfce, KDE, GNOME)
"auto" takes herbstluftwm if herbstclient answers, otherwise ewmh.

Without a focused window nothing happens.
Without a screen (tests, QT_QPA_PLATFORM=offscreen) no external programs are ever started.
"""
import os
import re
import shutil
import subprocess
import sys

METHODS = ("auto", "herbstluftwm", "ewmh", "off")

_hinted = False  # hint about missing xdotool/wmctrl only once per session


def wayland_session(env=None):
    """True in a Wayland session, also when Qt itself runs via XWayland (then platformName
    is "xcb" too, so only the environment tells)."""
    env = os.environ if env is None else env
    return bool(env.get("WAYLAND_DISPLAY")) or env.get("XDG_SESSION_TYPE") == "wayland"


def _run(cmd):
    """Run a command, return its output; None on any problem."""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=2, check=True)
    except (OSError, subprocess.SubprocessError) as e:
        print(f"[wm] {' '.join(cmd)} failed: {e}", file=sys.stderr)
        return None
    return result.stdout.strip()


def _query(cmd):
    """Like _run, but silent: an error here only means "no window"."""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=2)
    except (OSError, subprocess.SubprocessError):
        return None
    output = result.stdout.strip()
    return output if result.returncode == 0 and output else None


def herbstluftwm_running():
    """Does herbstluftwm answer? (herbstclient alone may be installed next to another WM)"""
    return bool(shutil.which("herbstclient")) and _query(["herbstclient", "version"]) is not None


def herbstluftwm_window():
    """X window ID of the window herbstluftwm has focused right now, otherwise None."""
    if not shutil.which("herbstclient"):
        return None
    # Without a focused window (empty tag) the attribute does not exist -> error, None
    return _query(["herbstclient", "attr", "clients.focus.winid"])


def ewmh_window():
    """X window ID from _NET_ACTIVE_WINDOW (the window manager's active window), otherwise None."""
    if shutil.which("xdotool"):
        return _query(["xdotool", "getactivewindow"])
    if shutil.which("xprop"):
        # "_NET_ACTIVE_WINDOW(WINDOW): window id # 0x1a00003"; 0x0 = none
        match = re.search(r"#\s*(0x[0-9a-fA-F]+)", _query(["xprop", "-root", "_NET_ACTIVE_WINDOW"]) or "")
        if match and int(match.group(1), 16):
            return str(int(match.group(1), 16))
    return None


def give_focus(winid):
    """Put the keyboard focus on winid: xdotool, otherwise wmctrl, otherwise herbstclient."""
    global _hinted
    if shutil.which("xdotool"):
        _run(["xdotool", "windowfocus", winid])  # sets the X focus directly
    elif shutil.which("wmctrl"):
        _run(["wmctrl", "-i", "-a", winid])  # asks the window manager to activate it
    elif shutil.which("herbstclient"):
        _run(["herbstclient", "jumpto", winid])
    elif not _hinted:
        _hinted = True
        print("[wm] Neither xdotool nor wmctrl found, cannot give the focus back", file=sys.stderr)


def force_focus(winid):
    """Put the X focus on our own (bypass) window without a timestamp.

    Qt sets the focus of a bypass window with the time of the last event it has seen. If the
    window manager has given the focus away later (e.g. i3 after a hotkey), the X server
    ignores that older request. xdotool uses CurrentTime, which always wins. Without xdotool
    nothing happens (then only a click brings the focus back)."""
    if os.environ.get("QT_QPA_PLATFORM") == "offscreen" or not shutil.which("xdotool"):
        return
    _run(["xdotool", "windowfocus", str(winid)])


def restore_focus(method="auto"):
    """Give the keyboard focus back to the window the window manager has focused."""
    if method == "off" or os.environ.get("QT_QPA_PLATFORM") == "offscreen":
        return
    if method == "auto":
        method = "herbstluftwm" if herbstluftwm_running() else "ewmh"
    winid = herbstluftwm_window() if method == "herbstluftwm" else ewmh_window()
    if winid is not None:
        give_focus(winid)
