# griffel

A screenshot annotation tool and whiteboard for Linux. I wanted something like
Epic Pen or Tekapoint on my own X11 desktop, something I could change whenever
it got in my way. This is it.

griffel (say GRIF-ul) is German for the stylus you write on a slate with.

Press a hotkey and griffel freezes the current monitor. Draw arrows, boxes and
notes on top, blur what nobody should see, then paste the result wherever it
needs to go. Without a screenshot it's a whiteboard for quick sketches and
diagrams.

It's made for the keyboard and a tiling window manager (herbstluftwm and sxhkd
in my case). It should run on any X11 setup, but I only use it on mine.
Wayland doesn't work.

## What it can do

**Drawing**
- Freehand, lines, arrows, rectangles, ellipses and text, also in a monospace
  font for code and commands
- Numbered or lettered markers that renumber themselves
- Blur to pixelate passwords, names and the like
- Erase an area by filling it with the color around it
- Text inside shapes and on arrows
- Spotlight and magnifier for pointing at things while sharing your screen

**Editing**
- Select one or many elements, move, resize, rotate, recolor, change their order
- Copy, paste and duplicate, also between a screenshot and a whiteboard
- Undo and redo for everything

**Saving**
- Copy to the clipboard or save as PNG, the whole screen or just a cropped area
- Saved files stay editable: the drawing data is stored inside the PNG, so any
  image viewer still shows a normal picture
- Every screenshot you've changed is kept in a history, so yesterday's
  annotation can still be edited today

**Whiteboard**
- Endless canvas with pan and zoom, dark or light background
- Arrows stick to shapes and follow them when you move things around
- On a light background colors are darkened automatically so they stay readable

**Setup**
- Colors and the monospace font come from your Alacritty config
- Keys, tools, colors and sizes can be changed in a TOML file
- Scales with the screen, so it stays usable on 4K

## Requirements

- Linux with X11
- Python 3.11 or newer and PySide6 (Arch: `pyside6`)
- `xclip` for the clipboard
- Optional: `xdotool` and `herbstclient` to give the focus back on close,
  `notify-send` with a notification daemon like dunst, and `rofi` for prompts.
  Without them griffel falls back to its own Qt dialogs.

## Getting started

```sh
git clone https://github.com/wabohu/griffel.git
ln -s "$PWD/griffel/run.py" ~/.local/bin/griffel   # starts it from the source folder

griffel              # annotate a screenshot of the monitor under the mouse
griffel --board      # empty whiteboard in a normal window
griffel --last       # open the latest screenshot from the history
griffel image.png    # open a saved drawing or any PNG
griffel --version
```

Put `griffel` on a global hotkey, that's how it's meant to be used. Inside, `?`
shows all keys and Esc quits. The full list is in [docs/usage.md](docs/usage.md).

## Configuration

Settings live in `~/.config/griffel/config.toml`. Every option is explained in
[config.example.toml](config.example.toml). You don't need the file at all,
anything missing falls back to the defaults.

## Privacy

- Saved drawings (Ctrl+S, Shift+Enter) carry their editing data inside the PNG,
  including the screenshot below the markings. With a crop, only the cropped part
  is stored, unless you set `[output] keep_full_screenshot = true`. Blurred areas
  are burned in, so they can't be recovered from the file.
- The history in `~/.local/share/griffel/history` keeps the whole screenshot of
  every image you changed, by default the last 100. Turn it off or shorten it
  under `[history]`.
- To pass an image on, Ctrl+E exports a plain PNG without any editing data.

## Tests

```sh
python tests/test_settings.py
python tests/test_document.py
python tests/regress.py
python tests/gui/run.py      # needs Xvfb, herbstluftwm, sxhkd, xdotool
```

## License

GPL-3.0-or-later, see [LICENSE](LICENSE).
