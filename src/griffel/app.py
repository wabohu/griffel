"""griffel: screenshot annotation tool and whiteboard (startup).

    griffel              annotate a screenshot of the monitor under the mouse
    griffel image.png    open a saved drawing or any PNG
    griffel --board      empty whiteboard in a normal window
    griffel --last       open the latest screenshot from the history
    griffel --version

From the source folder: python run.py … Usage: docs/usage.md. The drawing surface is in canvas.py.
"""
import argparse
import os
import sys
from pathlib import Path

from PySide6.QtGui import QColor, QCursor, QGuiApplication, QPixmap
from PySide6.QtWidgets import QApplication

from griffel import __version__
from griffel.canvas import Canvas
from griffel.document import load_document
from griffel import history, wm
from griffel.config import load_config
from griffel.history import is_entry
from griffel.notify import notify
from griffel.settings import Settings


# --- Capture -----------------------------------------------------------------
def grab_screen():
    """Screenshot of the monitor under the mouse pointer (X11)."""
    screen = QGuiApplication.screenAt(QCursor.pos()) or QGuiApplication.primaryScreen()
    return screen, screen.grabWindow(0)


# --- Session check -----------------------------------------------------------
IGNORE_WAYLAND = "GRIFFEL_IGNORE_WAYLAND"  # set to 1 to skip the check (own risk)
BOARD_HINT = "The whiteboard works: griffel --board"


def unsupported_session(app):
    """Why screenshots cannot work here, or None. Wayland: grabWindow returns a black image,
    the overlay needs X11 (bypass window, xdotool)."""
    if os.environ.get(IGNORE_WAYLAND):
        return None
    if wm.wayland_session():
        return f"griffel needs an X11 session for screenshots (Wayland detected). {BOARD_HINT}"
    platform = app.platformName()
    if platform not in ("xcb", "offscreen"):
        return f"griffel needs an X11 session for screenshots (Qt platform {platform}). {BOARD_HINT}"
    return None


def refuse_unsupported(app):
    """Quit with exit code 2 if the screenshot overlay cannot work in this session."""
    message = unsupported_session(app)
    if message:
        print(message, file=sys.stderr)
        notify(message)  # often started without a terminal (hotkey), so also as a notification
        sys.exit(2)


# --- Start -------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Screenshot annotation tool and whiteboard")
    parser.add_argument("file", nargs="?",
                        help="open a saved drawing or any PNG instead of a screenshot")
    parser.add_argument("--board", action="store_true",
                        help="empty whiteboard in a normal window instead of a screenshot")
    parser.add_argument("--last", action="store_true",
                        help="open the latest screenshot from the history (e.g. via a hotkey)")
    parser.add_argument("--version", action="version", version=f"griffel {__version__}")
    args, qt_args = parser.parse_known_args()  # pass the rest (e.g. Qt options) on to Qt
    app = QApplication(sys.argv[:1] + qt_args)

    if args.last:  # newest history entry; folder from the config ([history] dir)
        entries = history.entries(Settings(load_config(), False).history_dir)
        if not entries:
            message = "History is empty"
            print(message, file=sys.stderr)
            notify(message)  # often started without a terminal (hotkey), so also as a notification
            sys.exit(1)
        args.file = str(entries[-1])

    if args.file:
        background, elements, is_drawing, message, crop = load_document(args.file, with_crop=True)
        if background is None:
            print(message, file=sys.stderr)
            sys.exit(1)
        screen = QGuiApplication.screenAt(QCursor.pos()) or QGuiApplication.primaryScreen()
        if isinstance(background, QColor):  # saved whiteboard
            canvas = Canvas(screen, None, elements, document_path=args.file,
                            board=True, board_color=background)
            canvas.show_window()
        else:
            refuse_unsupported(app)
            # Own drawing: Ctrl+S overwrites it. Other image: Ctrl+S creates a new file
            # History entry: changes land there automatically, Ctrl+S creates (as with a
            # fresh screenshot) a separate file in the output folder
            canvas = Canvas(screen, QPixmap.fromImage(background), elements,
                            document_path=args.file if is_drawing else None)
            canvas.set_crop(crop)  # saved crop (key y), stays editable
            if is_entry(args.file, canvas.settings.history_dir):
                canvas.document_path = None
                canvas.start_history(Path(args.file).expanduser().resolve())
            canvas.show_overlay()
        canvas.report(message)
    elif args.board:
        screen = QGuiApplication.screenAt(QCursor.pos()) or QGuiApplication.primaryScreen()
        canvas = Canvas(screen, None, board=True)
        canvas.show_window()
    else:
        refuse_unsupported(app)
        screen, pixmap = grab_screen()  # grab first, then show the window!
        canvas = Canvas(screen, pixmap)
        canvas.show_overlay()
        canvas.start_history()  # new entry in the history
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
