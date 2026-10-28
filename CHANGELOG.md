# Changelog

All notable changes to griffel. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), versions follow
[Semantic Versioning](https://semver.org/).

## [0.1.0] - unreleased

The first release.

### Screenshot mode
- Freezes the monitor under the mouse in a fullscreen overlay that bypasses the
  window manager; global hotkeys keep working, the keyboard focus goes back to
  the previous window on close
- Crop, and clear an area by filling it with the surrounding color
- Blur that is burned into every saved file
- History of every changed screenshot, browsable with ← →, `--last`

### Drawing and editing
- Freehand, line, arrow (straight or curved), rectangle, ellipse, text (also
  monospace), numbered or lettered markers
- Text inside shapes and on lines and arrows
- Select one or many elements: move, resize, rotate, change color and size,
  change the order, copy, paste, duplicate; undo and redo for everything
- Spotlight and magnifier for pointing

### Whiteboard
- `griffel --board`: an endless canvas with pan and zoom and switchable
  backgrounds; colors are darkened on light backgrounds
- Arrows and lines dock to shapes and follow them
- Copy elements between screenshot and whiteboard, also a crop with its markings

### Output
- Copy to the clipboard (kept after quitting via `xclip`), save editable PNGs
  with the editing data inside, export clean PNGs
- Saved files with a crop store only the cropped part by default

### Setup
- Config in `~/.config/griffel/config.toml`: keys, tools, colors, sizes, bar
  colors, messages and prompts (dunst/rofi or Qt), history, output folder
- Colors and the monospace font from the Alacritty config if there is one,
  otherwise a built-in palette
- Key overview (`?`) with a keyboard picture for row-staggered, column-staggered
  and ortho keyboards in QWERTY, QWERTZ and AZERTY
- Scales with the screen height; works with HiDPI scaling
- Refuses to run on Wayland with a clear message (the whiteboard still works)
