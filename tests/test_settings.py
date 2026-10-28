#!/usr/bin/env python3
"""Settings test: Settings from different configs, without a window.

    python tests/test_settings.py

Checks that missing or unusable values never crash but lead to the default value.
Uses the isolated environment from regress.py (empty HOME, default palette).
Exit code 0 = all ok, 1 = failures.
"""
import contextlib
import io
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import regress  # noqa: E402,F401  (sets HOME, config and QT_QPA_PLATFORM)

from PySide6.QtGui import QColor, QGuiApplication, QKeySequence  # noqa: E402

failures = []


def check(name, condition):
    print(f"{'OK  ' if condition else 'FAIL  '}  {name}")
    if not condition:
        failures.append(name)


def quiet(func, *args):
    """Call without the expected hints on stderr; returns (result, hints)."""
    err = io.StringIO()
    with contextlib.redirect_stderr(err):
        result = func(*args)
    return result, err.getvalue()


def main():
    app = QGuiApplication(sys.argv)  # noqa: F841  (KeyMap needs Qt)
    from griffel import settings as st
    from griffel.tools import RECT_RADIUS, Tool

    # Empty config: everything default, no crash
    s, _ = quiet(st.Settings, {}, False)
    check("empty: size levels", s.stroke_widths == list(st.DEFAULT_STROKE_WIDTHS)
          and s.text_sizes == list(st.DEFAULT_TEXT_SIZES))
    check("empty: start level", s.default_size_level == st.DEFAULT_SIZE_LEVEL - 1)
    check("empty: start tool", s.default_tool == st.DEFAULT_TOOL)
    check("empty: start color", s.swatches[s.default_color_index] == s.palette.lookup(st.DEFAULT_COLOR))
    check("empty: step sizes", s.move_steps == {False: st.DEFAULT_MOVE_STEP, True: st.DEFAULT_MOVE_STEP_FINE})
    check("empty: dunst and rofi", s.use_dunst and s.use_rofi and s.rofi_theme is None)
    from griffel.history import default_history_dir
    check("empty: history on, default folder, 100", s.history_enabled and s.history_dir == default_history_dir()
          and s.history_keep == st.DEFAULT_HISTORY_KEEP)
    check("empty: bar off in screenshot mode", s.show_bar is False)
    check("empty: editable files only keep the crop", s.keep_full_screenshot is False)
    check("empty: spotlight 90 px / 45 %, magnifier 100 px / 2x", s.spotlight_radius == 90 and s.lens_radius == 100
          and s.spotlight_dim == 45 and s.lens_zoom == 2.0)
    tuned, hints2 = quiet(st.Settings, {"pointer": {"spotlight_dim": 30, "lens_zoom": 3, "lens_radius": 0.5}}, False)
    check("dimming and magnification from [pointer], integer as zoom ok, fraction as radius not",
          tuned.spotlight_dim == 30 and tuned.lens_zoom == 3.0 and tuned.lens_radius == 100 and "lens_radius" in hints2)
    own, hints = quiet(st.Settings, {"pointer": {"spotlight_radius": 140, "lens_radius": "big"}}, False)
    wrong, _ = quiet(st.Settings, {"pointer": {"spotlight_radius": 5000}}, False)
    check("radii from [pointer], invalid -> default with a hint",
          own.spotlight_radius == 140 and own.lens_radius == 100 and "lens_radius" in hints
          and wrong.spotlight_radius == 90)
    curve, _ = quiet(st.Settings, {"arrow": {"default": "curve"}}, False)
    odd, odd_hints = quiet(st.Settings, {"arrow": {"default": "wavy"}}, False)
    check("arrow variant: straight by default, curve from [arrow], unknown -> straight with a hint",
          s.default_arrow_kind == "straight" and curve.default_arrow_kind == "curve"
          and odd.default_arrow_kind == "straight" and "[arrow]" in odd_hints)
    check("screenshot: corner radius, no whiteboard background",
          s.rect_radius == st.DEFAULT_RECT_RADIUS and s.board_background is None and s.board_backgrounds is None)

    # Whiteboard: own radius, backgrounds from the default list
    b, _ = quiet(st.Settings, {}, True)
    check("whiteboard: corner radius", b.rect_radius == st.DEFAULT_RECT_RADIUS_BOARD)
    check("whiteboard: own stroke widths", b.stroke_widths == list(st.DEFAULT_STROKE_WIDTHS_BOARD))
    own_s, _ = quiet(st.Settings, {"size": {"stroke": [1, 2, 3, 4], "stroke_board": [5, 6, 7, 8]}}, False)
    own_b, _ = quiet(st.Settings, {"size": {"stroke": [1, 2, 3, 4], "stroke_board": [5, 6, 7, 8]}}, True)
    check("stroke widths: stroke in screenshot mode, stroke_board in the whiteboard",
          own_s.stroke_widths == [1, 2, 3, 4] and own_b.stroke_widths == [5, 6, 7, 8])
    check("whiteboard: bar on", b.show_bar is True)
    flipped, _ = quiet(st.Settings, {"ui": {"show_bar": True, "show_bar_board": False}}, False)
    flipped_b, _ = quiet(st.Settings, {"ui": {"show_bar": True, "show_bar_board": False}}, True)
    broken, _ = quiet(st.Settings, {"ui": {"show_bar": "yes"}}, False)
    check("bar from [ui] show_bar / show_bar_board, broken -> default",
          flipped.show_bar and not flipped_b.show_bar and broken.show_bar is False)
    check("whiteboard: backgrounds", len(b.board_backgrounds) == len(st.DEFAULT_BOARD_BACKGROUNDS)
          and b.board_background == b.board_backgrounds[0])

    # Unusable values: default plus a hint
    bad = {
        "tools": {"order": "not an array", "default": "magic_wand"},
        "size": {"stroke": [1, 2], "text": [1, 2, 3, 4], "default": 9},
        "colors": {"order": ["nonexistent"], "default": "purple", "light": {"red": "broken", "blue": 5}},
        "ui": {"bar_opacity": 3, "bar_background": "nonsense", "messages": "carrier_pigeon", "dialogs": 1},
        "board": {"background": "nope", "backgrounds": ["neither", 7]},
        "rect": {"radius": -1, "radius_board": 999},
        "move": {"step": 0, "step_fine": "fine"},
        "keys": {"undo": 5, "nonexistent": "x"},
        "history": {"enabled": "yes", "keep": 0, "dir": 42},
    }
    s, hints = quiet(st.Settings, bad, True)
    check("broken: size levels", s.stroke_widths == list(st.DEFAULT_STROKE_WIDTHS_BOARD)
          and s.text_sizes == list(st.DEFAULT_TEXT_SIZES) and s.default_size_level == st.DEFAULT_SIZE_LEVEL - 1)
    check("broken: tools", s.default_tool == st.DEFAULT_TOOL and Tool.FREEHAND in s.tools)
    check("broken: color bar not empty", len(s.swatches) > 0 and 0 <= s.default_color_index < len(s.swatches))
    check("broken: light variants skipped", s.light_overrides == {})
    expected_bg = QColor(s.palette.lookup(st.DEFAULT_BAR_BACKGROUND))
    expected_bg.setAlphaF(st.DEFAULT_BAR_OPACITY)  # Theme puts the opacity into the background color
    check("broken: bar colors", s.theme.background == expected_bg)
    check("broken: dunst and rofi", s.use_dunst and s.use_rofi)
    check("broken: whiteboard backgrounds", len(s.board_backgrounds) == len(st.DEFAULT_BOARD_BACKGROUNDS)
          and s.board_background == QColor(s.palette.lookup(st.DEFAULT_BOARD_BACKGROUND)))
    check("broken: corner radius", s.rect_radius == st.DEFAULT_RECT_RADIUS_BOARD)
    check("broken: step sizes", s.move_steps == {False: st.DEFAULT_MOVE_STEP, True: st.DEFAULT_MOVE_STEP_FINE})
    check("broken: history", s.history_enabled and s.history_keep == st.DEFAULT_HISTORY_KEEP
          and s.history_dir == default_history_dir())
    check("broken: hints on stderr", "[size]" in hints and "[ui]" in hints and "[rect]" in hints)

    # Valid values are taken over
    good = {
        "size": {"stroke": [1, 3, 5, 7], "default": 4},
        "colors": {"light": {"red": "#112233"}},
        "ui": {"messages": "toast", "dialogs": "qt"},
        "rect": {"radius": 0},
        "move": {"step": 25, "step_fine": 2},
        "output": {"dir": "~/somewhere", "keep_full_screenshot": True},
        "history": {"enabled": False, "keep": 5, "dir": "~/my-history"},
    }
    s, _ = quiet(st.Settings, good, False)
    check("valid: taken over", s.stroke_widths == [1, 3, 5, 7] and s.default_size_level == 3
          and s.rect_radius == 0 and s.move_steps == {False: 25, True: 2}
          and not s.use_dunst and not s.use_rofi and s.output_dir == "~/somewhere" and s.keep_full_screenshot
          and s.light_overrides == {s.palette.lookup("red"): "#112233"}
          and not s.history_enabled and s.history_keep == 5 and s.history_dir == Path.home() / "my-history")

    # Monospace font: [text] mono_font, otherwise the terminal font from Alacritty
    import tempfile

    from griffel import colors
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        both = base / "both.toml"
        both.write_text('[font.normal]\nfamily = "Plain Mono"\n[font.bold]\nfamily = "Bold Mono"\n')
        normal_only = base / "normal.toml"
        normal_only.write_text('[font.normal]\nfamily = "Plain Mono"\n')
        imported = base / "main.toml"
        imported.write_text('[general]\nimport = ["normal.toml"]\n[colors.primary]\nbackground = "#000000"\n')
        none = base / "none.toml"
        none.write_text('[font]\nsize = 12\n')
        broken = base / "broken.toml"
        broken.write_text('[font.normal\nfamily = ')
        fonts = [colors.load_terminal_font(p) for p in (both, normal_only, imported, none)]
        broken_font, _ = quiet(colors.load_terminal_font, broken)
    check(f"terminal font: bold first, else normal, via import, none -> None ({fonts})",
          fonts == ["Bold Mono", "Plain Mono", "Plain Mono", None] and broken_font is None)
    # Palette: [colors] source and [palette] on top of Alacritty or the built-in values
    with tempfile.TemporaryDirectory() as tmp:
        alacritty = Path(tmp) / "alacritty.toml"
        alacritty.write_text('[colors.normal]\nred = "#aa0000"\ngreen = "#00aa00"\n'
                             '[colors.primary]\nbackground = "#101010"\n')
        own = colors.palette_overrides({"red": "#FF0000", "bright-blue": "0x0000ff", "background": "#202020"})
        mixed = colors.load_palette(alacritty, "auto", own)
        builtin = colors.load_palette(alacritty, "builtin")
        only_alacritty = colors.load_palette(alacritty, "alacritty")
    check("palette: [palette] wins over Alacritty, the rest from Alacritty or built-in",
          mixed.lookup("red") == "#ff0000" and mixed.lookup("green") == "#00aa00"
          and mixed.lookup("bright_blue") == "#0000ff" and mixed.background == "#202020"
          and mixed.lookup("yellow") == colors.DEFAULT_NORMAL["yellow"]
          and only_alacritty.lookup("red") == "#aa0000")
    check("palette: source = builtin ignores Alacritty",
          builtin.lookup("red") == colors.DEFAULT_NORMAL["red"] and builtin.background == colors.DEFAULT_BACKGROUND)
    bad, hints = quiet(colors.palette_overrides, {"purple": "#123456", "red": "rot", "blue": 5, "green": "#00ff00"})
    check(f"palette: unknown names and values skipped with a hint ({bad})",
          bad == {"green": "#00ff00"} and hints.count("[palette]") == 3)
    missing, hints = quiet(colors.load_palette, None, "alacritty")
    unknown, hints2 = quiet(colors.load_palette, None, "kitty")
    check("palette: source = alacritty without a config / unknown source -> hint, built-in palette",
          missing.lookup("red") == colors.DEFAULT_NORMAL["red"] and "no Alacritty config" in hints
          and unknown.lookup("red") == colors.DEFAULT_NORMAL["red"] and "unknown" in hints2)
    themed = st.Settings({"colors": {"source": "builtin", "order": ["red", "green"]},
                          "palette": {"red": "#ff0000", "background": "#202020"}}, False)
    check("palette: Settings takes [palette] for the bar and the theme background",
          themed.swatches == ["#ff0000", colors.DEFAULT_NORMAL["green"]]
          and themed.palette.lookup("background") == "#202020"
          and themed.theme.background.name() == "#202020")

    # rofi prompts: bar colors as rasi variables, or own rasi file ([ui] rofi_colors)
    from griffel import notify
    bar = st.Settings({"ui": {"bar_background": "#000000", "bar_foreground": "#ffffff",
                              "bar_accent": "#ff0000", "bar_opacity": 0.5}}, False)
    rv = bar.rofi_vars()
    check(f"rofi: colors from the bar, opaque, mixed in between ({rv})",
          rv == {"background": "#000000", "foreground": "#ffffff", "selected": "#ff0000",
                 "background-alt": "#262626", "frame": "#4c4c4c", "dimmed": "#a6a6a6"}
          and s.rofi_colors is None
          and st.Settings({"ui": {"rofi_colors": "~/x.rasi"}}, False).rofi_colors == "~/x.rasi")
    cmd = notify.rofi_command("Save?", colors={"background": "#000000", "frame": "#4d4d4d"})
    with tempfile.TemporaryDirectory() as tmp:
        rasi = Path(tmp) / "colors.rasi"
        rasi.write_text("* { base03: #111111; }")
        with_file = notify.rofi_command("Save?", colors=rv, colors_file=rasi)
        missing_file, hints = quiet(notify.rofi_command, "Save?", None, rv, Path(tmp) / "nope.rasi")
    check("rofi: command line with the bar colors, a rasi file instead, missing file -> bar colors",
          cmd[-4:] == ["-theme", str(notify.ROFI_THEME), "-theme-str", "* { background: #000000; frame: #4d4d4d; }"]
          and with_file[-1] == f'@import "{rasi}"' and "background:" not in " ".join(with_file)
          and missing_file[-1].startswith("* { background: #000000;") and "rofi_colors" in hints)

    # Focus after the overlay: [wm] focus
    bad_focus, hints = quiet(st.Settings, {"wm": {"focus": "sway"}}, False)
    check("[wm] focus: valid taken over, missing = auto, unknown -> hint, auto",
          st.Settings({"wm": {"focus": "ewmh"}}, False).focus_method == "ewmh"
          and s.focus_method == "auto" and bad_focus.focus_method == "auto" and "[wm]" in hints)

    own_font = st.Settings({"text": {"mono_font": "My Mono"}}, False)
    check("monospace: [text] mono_font, empty = terminal font (none in the test: system font)",
          own_font.mono_family == "My Mono" and st.Settings({"text": {"mono_font": ""}}, False).mono_family is None
          and s.mono_family is None)

    # Key overview (?): every action described, content per mode
    from griffel import shortcuts
    from griffel.keymap import DEFAULT_KEYS, KeyMap
    missing = [a for a in DEFAULT_KEYS if a not in shortcuts.DESCRIPTIONS and not shortcuts.GROUPED.match(a)]
    check(f"overview: every action has a description {missing or ''}", not missing)
    keymap = KeyMap({"keys": {"undo": "u"}, "tools": {"order": ["rect", "text"]}})
    shot = dict(shortcuts.sections(keymap, [Tool.RECT, Tool.TEXT], 9, 4, board=False))
    board = dict(shortcuts.sections(keymap, [Tool.RECT, Tool.TEXT], 9, 4, board=True))
    flat = lambda sec: {(k, t) for entries in sec.values() for k, t in entries}  # noqa: E731
    check("overview: own bindings and tool order",
          ("u", "undo") in flat(shot) and ("a", "Rectangle") in flat(shot) and ("s", "Text") in flat(shot)
          and shot["Tools"][0] == ("w", "Select"))
    check("overview: slots combined", ("shift+a s d f g z x c v", "color from the bar") in flat(shot)
          and ("alt+a s d f", "size in levels") in flat(shot) and ("h j k l", "move") in flat(shot))
    check("overview: only what applies in the mode", "History" in shot and "History" not in board
          and "View" in board and "View" not in shot)
    check("overview: all keys of an action, lower case, own names",
          ("?", "this overview") in flat(shot) and ("del, backspace", "delete (nothing selected: clear the crop area)") in flat(shot)
          and ("del, backspace", "delete") in flat(board)
          and ("enter", "copy image and quit") in flat(shot) and ("ctrl+s", "save editable") in flat(shot)
          and ("←", "older screenshot") in flat(shot) and ("ctrl+shift+b", "previous background") in flat(board))
    ov = shortcuts.overview(keymap, [Tool.RECT, Tool.TEXT], 9, 4, board=False)
    check("panel data: tools with Select first, colors and sizes per key",
          ov["tools"] == [(Tool.SELECT, "w"), (Tool.RECT, "a"), (Tool.TEXT, "s"), (Tool.MARKER, "c"), (Tool.BLUR, "z")]
          and ov["colors"] == list("asdfgzxcv") and ov["sizes"] == list("asdf")
          and ov["color_hint"] == "shift + …, tab / shift+tab cycles" and ov["size_hint"].startswith("alt + …"))
    keys = ov["keyboard"]
    listed = {k for _, entries in ov["lists"] for k, _ in entries}
    check("panel data: keyboard picture with tools, single keys and Shift, not repeated in the lists",
          keys["w"]["plain"] == (Tool.SELECT, "Select") and keys["a"]["plain"][0] == Tool.RECT
          and keys["q"]["plain"][1].startswith("rotate") and keys["q"]["shift"][1].startswith("rotate")
          and keys["x"]["plain"] == (None, "crop") and keys["tab"]["shift"] == (None, "color ←")
          and "u" not in keys and not {"q", "shift+q", "x", "b", "e", "w"} & listed and "?" in listed)
    board_keys = shortcuts.overview(keymap, [Tool.RECT, Tool.TEXT], 9, 4, board=True)["keyboard"]
    check("panel data: keyboard picture only with what applies (no crop, no blur on the whiteboard)",
          "x" not in board_keys and "z" not in board_keys and "e" in board_keys)
    names = [name for name, _ in ov["lists"]]
    check("panel data: picture groups not repeated in the lists",
          not {"Tools", "Color and size", "Mouse"} & set(names) and ov["mouse"] and "Output" in names)
    plain = st.Settings({}, False)
    check("theme: accent blue, heading magenta (default)",
          plain.theme.accent == QColor(plain.palette.lookup("blue"))
          and plain.theme.heading == QColor(plain.palette.lookup("magenta")))
    own, _ = quiet(st.Settings, {"ui": {"bar_heading": "yellow", "bar_accent": "nonsense"}}, False)
    check("theme: heading from [ui] bar_heading, unknown accent -> default",
          own.theme.heading == QColor(own.palette.lookup("yellow")) and own.theme.accent == plain.theme.accent)

    # scripts/sync_config.py: take over new entries, keep own values
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
    import tomllib

    import sync_config
    template = (
        '# Template\n\n[ui]\nbar = "background"   # comment with "#" in it\ncolor = "#f8f6f0"  # light\n'
        'new = true\n\n[colors.light]\n# yellow = "#8f5e15"\n\n[keys]\nundo = "r"\n')
    user = ('# My config\n[ui]\nbar = "#112233"\ncolor = "#f8f6f0"\nalt = 3\n'
            '[colors.light]\nyellow = "#000000"\n[keys]\nundo = ["u", "ctrl+z"]\n[own]\nx = "a # b"\n')
    text, added, own = sync_config.merge(template, user)
    merged = tomllib.loads(text)
    check("sync_config: new keys added, own values kept",
          added == [("ui", "new")] and merged["ui"] == {"bar": "#112233", "color": "#f8f6f0", "new": True, "alt": 3}
          and merged["keys"]["undo"] == ["u", "ctrl+z"] and merged["own"] == {"x": "a # b"})
    check("sync_config: comments of the template, own header, example replaced",
          text.startswith("# My config\n") and '# comment with "#" in it' in text
          and 'yellow = "#000000"' in text and '# yellow' not in text)
    check("sync_config: second run changes nothing", sync_config.merge(template, text)[0] == text)

    # Keyboard picture of the overview ([help], keyboard.py)
    from griffel import keyboard as kb
    check("[help] default: normal keyboard, layout from setxkbmap, default stagger and outer column",
          plain.help_keyboard == "row" and plain.help_layout == "auto" and plain.help_stagger == kb.DEFAULT_STAGGER
          and plain.help_outer == kb.DEFAULT_OUTER and plain.picture_layout() in kb.LAYOUTS)
    kyria = st.Settings({"help": {"keyboard": "column", "layout": "qwertz", "stagger": [1, 1, 0.5, 0, 0.5, 0.5],
                                  "outer_column": ["Tab", "=", "`"]}}, False)
    check("[help] own values taken over", kyria.help_keyboard == "column" and kyria.picture_layout() == "qwertz"
          and kyria.help_stagger == (1.0, 1.0, 0.5, 0.0, 0.5, 0.5) and kyria.help_outer == ("tab", "=", "`"))
    bad_help, hints = quiet(st.Settings, {"help": {"keyboard": "split", "layout": "dvorak", "stagger": [1, 2],
                                                   "outer_column": "tab"}}, False)
    check("[help] broken values: defaults with hints",
          bad_help.help_keyboard == "row" and bad_help.help_layout == "auto"
          and bad_help.help_stagger == kb.DEFAULT_STAGGER and bad_help.help_outer == kb.DEFAULT_OUTER
          and all(word in hints for word in ("keyboard", "layout", "stagger", "outer_column")))
    layouts = [kb.parse_layout(q) for q in ("rules: evdev\nmodel: pc105\nlayout: us\nvariant: altgr-intl\n",
                                            "layout:     de\n", "layout: fr\n", "layout: us,de\n", "layout: ch\n",
                                            "", None)]
    check(f"layout from setxkbmap: us, de, fr, first of several, ch, nothing ({layouts})",
          layouts == ["qwerty", "qwertz", "azerty", "qwerty", "qwertz", "qwerty", "qwerty"])
    row = kb.caps("row", "qwerty")
    check("picture row: wide tab/caps/shift outside, letters offset by row (0, 0.25, 0.75)",
          [(c.key, c.width) for c in row[:3]] == [("tab", 1.5), ("caps", 1.75), ("shift", 2.25)]
          and [(c.key, c.x) for c in row if c.key in "qaz"] == [("q", 1.5), ("a", 1.75), ("z", 2.25)]
          and kb.picture_keys(row) == set("qwertasdfgzxcvb") | {"tab"})
    column = kb.caps("column", "qwerty", outer=("tab", "=", "`"))
    check("picture column: stagger per column, own outer column",
          [(c.key, c.y) for c in column if c.key in ("tab", "w", "e", "d")]
          == [("tab", 0.78), ("w", 0.26), ("e", 0.0), ("d", 1.0)] and "=" in kb.picture_keys(column))
    ortho = kb.caps("ortho", "azerty")
    check("picture ortho azerty: no offset, a top left, w bottom left",
          {c.y for c in ortho} == {0.0, 1.0, 2.0} and next(c for c in ortho if c.key == "a").y == 0.0
          and next(c for c in ortho if c.key == "w").y == 2.0)
    for kind in kb.KINDS:
        for layout in kb.LAYOUTS:
            caps = kb.caps(kind, layout)
            data = shortcuts.overview(keymap, [Tool.RECT, Tool.TEXT], 9, 4, False, caps, kb.FULL_ROWS[layout])
            on_picture = {key if layer == "plain" else f"shift+{key}"
                          for key, layers in data["keyboard"].items() for layer in layers}
            listed = {part.strip() for _, entries in data["lists"] for keys, _ in entries for part in keys.split(",")}
            lost = [k for a in ("tool_blur", "crop", "spotlight", "undo", "tool_select")
                    for k in map(shortcuts.display, keymap.labels(a)) if k not in on_picture | listed]
            check(f"overview {kind}/{layout}: every key on the picture or in the lists {lost or ''}", not lost)
    qwertz = shortcuts.overview(keymap, [Tool.RECT], 9, 4, False, kb.caps("row", "qwertz"))
    check("overview qwertz: z (blur) not on the keyboard picture, so in the list Tools",
          "z" not in qwertz["keyboard"] and ("z", "Blur") in dict(qwertz["lists"]).get("Tools", [])
          and "y" not in qwertz["keyboard"] and "z" in shortcuts.overview(keymap, [Tool.RECT], 9, 4, False)["keyboard"])

    # The README example for Alt as the window manager's modifier: valid, nothing bound twice
    alt_free = {"size_1": "ctrl+1", "size_2": "ctrl+2", "size_3": "ctrl+3", "size_4": "ctrl+4",
                "text_font": "ctrl+m"}
    moved, hints = quiet(KeyMap, {"keys": alt_free})
    check(f"keys: README example without Alt, no warnings {hints!r}",
          not hints and all(moved.labels(a) == [QKeySequence(k).toString()] for a, k in alt_free.items()))

    # Wayland detection (Qt-free, also under XWayland where Qt reports "xcb")
    from griffel.wm import wayland_session
    check("wayland: WAYLAND_DISPLAY or XDG_SESSION_TYPE, not x11 or empty",
          wayland_session({"WAYLAND_DISPLAY": "wayland-0"}) and wayland_session({"XDG_SESSION_TYPE": "wayland"})
          and not wayland_session({"XDG_SESSION_TYPE": "x11", "WAYLAND_DISPLAY": ""}) and not wayland_session({}))

    print("\nAll OK." if not failures else f"\n{len(failures)} failed.")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
