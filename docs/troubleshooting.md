# Troubleshooting

Start griffel from a terminal to see its messages; started from a hotkey they go
nowhere. `griffel --version` tells which version you run.

## griffel says it needs an X11 session, or the screenshot is black

griffel works only on X11. In a Wayland session (`WAYLAND_DISPLAY` set or
`XDG_SESSION_TYPE=wayland`, also when it runs via XWayland) it refuses to take a
screenshot, because it would get a black or empty image there. The whiteboard
(`griffel --board`) still works. GNOME and KDE start Wayland by default; choose
the X11/Xorg session when you log in.

If your setup can take screenshots anyway, `GRIFFEL_IGNORE_WAYLAND=1 griffel`
skips the check.

## The hotkey does nothing

- Run the same command in a terminal. If it works there, your window manager
  doesn't find `griffel` in its `PATH`: `~/.local/bin` is often missing when the
  window manager isn't started from a login shell. Use the absolute path in the
  hotkey.
- i3: use `exec --no-startup-id griffel`, otherwise the busy cursor stays until
  i3 gives up.
- Check that no other binding uses the same key.

## No window has the keyboard focus after closing a screenshot

The screenshot overlay bypasses the window manager, so griffel gives the focus
back itself when it closes. For that it needs `xdotool` (or `wmctrl`); only
with herbstluftwm it works without them. Install `xdotool`. If it still goes
wrong, try `[wm] focus = "ewmh"` in the config; `"off"` turns this off
completely.

## Some keys do nothing while griffel is open

Your window manager gets keys before griffel does. If Alt is its modifier
(common with i3, Openbox, awesome), Alt+A S D F (size) and Alt+V (monospace)
never arrive. Move them under `[keys]`; the README has an example under
"Clashes with your window manager".

On QWERTZ and AZERTY some default keys sit in odd places (e.g. Z for blur).
All keys except Esc can be changed under `[keys]`.

## The clipboard is empty after griffel quits

On X11 the program that copied something has to keep running to hand it out.
griffel uses `xclip` for that; without it the image lives only as long as
griffel. Install `xclip`.

## Prompts and messages look different than expected

Messages go through `notify-send` (needs a notification daemon such as dunst),
prompts through `rofi`. If one is missing or fails, griffel falls back to its own
Qt windows. To always use those, set `[ui] messages = "toast"` and
`dialogs = "qt"`. The colors of the rofi prompts follow the bar; `[ui]
rofi_colors` can load your own rasi file instead.

## The colors don't match my terminal

griffel reads its palette from the Alacritty config, if there is one
(`[colors] source = "auto"`); for other terminals it uses a built-in palette.
Set your own colors under `[palette]`, and choose which ones appear in the bar
under `[colors] order`. `PYTHONPATH=src python -m griffel.colors` (from the
source folder) shows what griffel found.

## Lines look thin on a HiDPI screen

With scaling (e.g. `Xft.dpi` 192 or `QT_SCALE_FACTOR=2`) griffel works in the
screenshot's real pixels, so a 4 px line is 4 physical pixels. Raise the stroke
widths and font sizes under `[size]`.

## The screenshot shows the wrong monitor

griffel takes the monitor the mouse is on when it starts. Move the mouse to the
monitor you want before pressing the hotkey.

## Where are my files?

- Saved and exported images: `[output] dir`, by default `griffel/` in your
  pictures folder (`~/Pictures/griffel`).
- History: `~/.local/share/griffel/history/` (or `$XDG_DATA_HOME`), set with
  `[history]`.
- Config: `~/.config/griffel/config.toml`.
