# Using griffel

This page explains what griffel can do and how, one feature at a time. For a quick
look-up of all keys, see the [key reference](#key-reference) at the end, or press
<kbd>?</kbd> inside griffel.

Every key except <kbd>Esc</kbd> can be changed under `[keys]` in
`~/.config/griffel/config.toml` (see [config.example.toml](../config.example.toml)).
This page lists the defaults.

- [Overview](#overview)
- [Drawing](#drawing)
- [Selecting and editing](#selecting-and-editing)
- [Text in shapes and on arrows](#text-in-shapes-and-on-arrows)
- [Connectors](#connectors)
- [Crop and clearing an area](#crop-and-clearing-an-area)
- [Copy, save, export](#copy-save-export)
- [Copying elements and pasting images](#copying-elements-and-pasting-images)
- [Whiteboard](#whiteboard)
- [History](#history)
- [Pointing: spotlight and magnifier](#pointing-spotlight-and-magnifier)
- [Command line](#command-line)
- [Key reference](#key-reference)

## Overview

griffel has two modes:

- **Screenshot**: `griffel` freezes the monitor under the mouse and shows it
  fullscreen. You draw on top, then copy or save the result. Meant to be started
  with a global hotkey (see the README).
- **Whiteboard**: `griffel --board` opens an empty canvas in a normal window,
  for sketches and diagrams. It can be panned and zoomed and has no edges.

Most things work the same in both. Where a feature exists in only one mode,
this page says so.

**The bar** at the bottom shows the tools, the colors and the sizes; click
them or use the keys. <kbd>B</kbd> shows or hides it. In screenshot mode it
starts hidden, on the whiteboard visible (`[ui] show_bar`, `show_bar_board`).

**Quitting**: in screenshot mode <kbd>Esc</kbd> quits (after first ending
whatever is active, see below), <kbd>Enter</kbd> copies the image and quits.
The whiteboard closes only with <kbd>Ctrl</kbd>+<kbd>Q</kbd> or by closing the
window, and asks first if there are unsaved changes.

**<kbd>Esc</kbd>** always steps back one level: it ends text input, then
pointing, removes a crop being drawn or selected, clears the selection, and
only then quits (screenshot mode).

**<kbd>?</kbd>** shows an overview of all keys as they are currently bound,
only what applies in the current mode. Any key or a click closes it. The
keyboard picture in it follows `[help]`: normal keyboard, column stagger
(split keyboards) or grid, QWERTY, QWERTZ or AZERTY (by default taken from
`setxkbmap`).

**Undo** with <kbd>R</kbd>, redo with <kbd>Shift</kbd>+<kbd>R</kbd>. Every
change can be undone, also moving, recoloring and changing the background.

## Drawing

Pick a tool, then drag on the canvas.

| Tool | Key | What it draws |
|---|---|---|
| Select | <kbd>W</kbd> | nothing; selects and edits (see [Selecting and editing](#selecting-and-editing)) |
| Freehand | <kbd>A</kbd> | a free line along the mouse |
| Line | <kbd>S</kbd> | a straight line |
| Arrow | <kbd>D</kbd> | a straight arrow; <kbd>D</kbd> again: curved arrow |
| Rectangle | <kbd>F</kbd> | a rectangle with rounded corners (`[rect] radius`) |
| Ellipse | <kbd>G</kbd> | an ellipse |
| Text | <kbd>T</kbd> | click and type |
| Marker | <kbd>C</kbd> | a numbered circle; <kbd>C</kbd> again: letters |
| Blur | <kbd>Z</kbd> | a pixelated area (screenshot mode only) |

The keys <kbd>A</kbd> to <kbd>T</kbd> follow `[tools] order` in the config:
the first tool there gets <kbd>A</kbd>, the second <kbd>S</kbd>, and so on.

### Color and size

| Key | Action |
|---|---|
| <kbd>Shift</kbd>+<kbd>A</kbd> <kbd>S</kbd> <kbd>D</kbd> <kbd>F</kbd> <kbd>G</kbd> <kbd>Z</kbd> <kbd>X</kbd> <kbd>C</kbd> <kbd>V</kbd> <kbd>B</kbd> | pick a color, in the order of the color bar |
| <kbd>Tab</kbd> / <kbd>Shift</kbd>+<kbd>Tab</kbd> | next / previous color |
| <kbd>Alt</kbd>+<kbd>A</kbd> <kbd>S</kbd> <kbd>D</kbd> <kbd>F</kbd> | size level 1 to 4: stroke width, or font size for text |
| <kbd>Alt</kbd>+wheel | fine size: ±1 px stroke or ±2 px text per notch |

Color and size apply to what you draw next. With a selection they change the
selected elements instead; while typing, the text being typed. The levels are
set under `[size]`, with separate stroke widths for screenshot and whiteboard.
<kbd>Alt</kbd>+wheel needs a selection or text being typed.

If your window manager uses <kbd>Alt</kbd> as its modifier, it takes the
<kbd>Alt</kbd> keys before griffel sees them; move them under `[keys]` (see the
README, "Clashes with your window manager").

On a light whiteboard background, colors are shown a bit darker so they stay
readable. They are stored unchanged.

### Mouse pointer

While drawing, the pointer is a crosshair in the current color. The small
circle in its middle is as wide as the stroke (zoom included), and the tool's
shape sits at the bottom right. In the select tool it is an arrow with a small
selection frame, and resize arrows over handles.

### Text

Click with the text tool and type. <kbd>Esc</kbd> or a click elsewhere ends
the input; <kbd>Enter</kbd> starts a new line. To change a text later,
double-click it (select tool), or drag it to move it.

<kbd>Alt</kbd>+<kbd>V</kbd> switches to a **monospace** font for code,
commands and paths, and back. It works while typing (no "v" is typed), on
selected texts and labels, and for the next text. The font is the terminal font
from your Alacritty config if there is one, otherwise the system's monospace
font; `[text] mono_font` sets another one.

### Curved arrow

Press <kbd>D</kbd> while the arrow is already active to switch between straight
and curved; the bar icon and the pointer show which. The choice lasts for the
session, the start value is `[arrow] default`.

Draw the path freehand: while you draw it becomes one smooth curve, an arc or a
gentle S, with the head at the end. An almost straight stroke snaps to straight.

Selected, a curved arrow has four handles: the two ends (each takes its control
point along) and the two control points, with dashed guide lines. It can be
rotated with the round handle. It does not dock onto shapes and takes no text.

### Markers

Markers are numbered circles for steps: 1, 2, 3 or A, B, C.

- Click: a circle.
- Drag: a circle with a pointer line; the tip is where you press, the circle
  where you release.
- <kbd>C</kbd> again while the marker is active switches between numbers and
  letters; the two are counted separately.

Deleting a marker renumbers the others, undo brings the old numbers back. Color
and size work as for shapes. In the select tool, tip and circle have their own
handles.

### Blur (screenshot mode only)

Drag an area with <kbd>Z</kbd>: the screenshot below is pixelated, the
markings on top are not. The block size follows the size (stroke width × 3).
A blur area can be selected, moved and resized like a rectangle; whatever lies
below is always pixelated.

When saving (also in the history) the blur is burned into the stored
screenshot, so no file contains what was hidden. After reopening a file, the
blur can't be removed any more.

## Selecting and editing

Switch to the select tool with <kbd>W</kbd>.

**Selecting**

- Click an element. Unfilled shapes are hit on their outline (with a small
  tolerance), text and images anywhere.
- <kbd>Shift</kbd>+click adds an element to the selection or removes it.
- Drag on an empty spot: a rubber band selects everything completely inside it
  (with <kbd>Shift</kbd>: adds to the selection).
- <kbd>Ctrl</kbd>+<kbd>A</kbd> selects everything.
- A plain click on one of several selected elements selects only that one.
- <kbd>Esc</kbd> clears the selection.

**Changing**

| Action | Mouse | Keys |
|---|---|---|
| Move | drag | <kbd>H</kbd> <kbd>J</kbd> <kbd>K</kbd> <kbd>L</kbd> (10 px), with <kbd>Shift</kbd> 1 px (`[move]`) |
| Resize | drag a handle | – |
| Rotate | drag the round handle above the frame | <kbd>Q</kbd> / <kbd>Shift</kbd>+<kbd>Q</kbd>: 5° counterclockwise / clockwise |
| Bring forward / send backward | – | <kbd>Ctrl</kbd>+<kbd>↑</kbd> / <kbd>Ctrl</kbd>+<kbd>↓</kbd> |
| Bring to front / send to back | – | <kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>↑</kbd> / <kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>↓</kbd> |
| Delete | – | <kbd>Del</kbd> or <kbd>Backspace</kbd> |
| Color, size | the bar | as when drawing |

Details:

- Handles appear only when a single element is selected. Corners resize; for
  lines and arrows the handles are the end points; for text, resizing scales
  the font. Images keep their aspect ratio.
- Everything else works on several elements at once and is one undo step.
  Pressing a key repeatedly in quick succession (moving, rotating, Alt+wheel)
  also counts as one step.
- Rotating turns around the middle, several elements around their common
  middle. Blur areas and markers don't rotate. Lines and straight arrows have
  no round handle; turn them with their end points.
- Several elements keep their order among each other when brought to the front
  or back.
- Double-click a text to edit it, an empty spot to start a new text.

## Text in shapes and on arrows

A rectangle, an ellipse, a line or an arrow can carry a text of its own, a
label. In the select tool, double-click into the shape (on its outline, its
empty inside or its text) or on the line, and type.

- **In a rectangle or ellipse** the text wraps at the shape's width (a bit
  narrower in an ellipse) and stays centered. <kbd>Esc</kbd> or a click
  elsewhere ends the input.
- **On a line or arrow** the text sits in the middle of the line, upright, in a
  small box: on the whiteboard in its background color (the line seems
  interrupted), on a screenshot in the bar color. It doesn't wrap;
  <kbd>Enter</kbd> starts a new line.

The label has the shape's color and moves, rotates and resizes with it. It is
part of the shape: a click selects the shape, <kbd>Del</kbd> deletes both,
copying takes it along. Empty the text to remove the label.

A color picked while typing recolors shape and label; <kbd>Alt</kbd>+<kbd>A</kbd>
<kbd>S</kbd> <kbd>D</kbd> <kbd>F</kbd> and <kbd>Alt</kbd>+wheel change the font
size. With the text tool (<kbd>T</kbd>), a click into a shape makes a loose
text instead.

## Connectors

*Whiteboard only. On a screenshot lines and arrows never dock.*

A line or arrow whose start or end lands on or near the outline of a rectangle,
ellipse, image or loose text docks there; the shape is highlighted while you
drag. A docked end points at the middle of the shape and stops at its outline.
When the shape moves, rotates or is resized, the end follows.

- Deep inside a shape the end stays free, so you can still point at something
  inside a frame.
- Dock or undock an end later by dragging its handle (select tool).
- Moving or rotating the arrow itself lets go of the shapes that don't move
  along.
- Deleting a shape leaves the end free where it was; undo docks it again.
- Copying shapes together with their arrows keeps the copies connected; a
  copied arrow alone is free.

## Crop and clearing an area

*Screenshot mode only.*

### Crop

Press <kbd>X</kbd> and drag a frame. Outside is darkened, the size in pixels
shows at the bottom right, and you continue with your tool. Everything you
copy, save or export from now on contains only the crop.

| To … | do |
|---|---|
| resize or move it | <kbd>X</kbd> again: drag a handle (corners: both directions, edges: one) or drag inside |
| … with the select tool | click the crop's edge, then drag its handles or its edge; the inside stays free for the elements in it |
| draw a new one | <kbd>X</kbd>, then drag outside the old one |
| remove it | <kbd>Esc</kbd> while drawing it or while it is selected |

Everything can be undone.

### Clearing an area

<kbd>Del</kbd> with a crop and no element selected clears the area inside the
crop (the crop doesn't need to be selected). The screenshot there is filled
with the most frequent color around it, on a web page or in a terminal usually
its background. The markings stay, the crop is removed. One undo brings both
back. Saved files contain the cleared area.

## Copy, save, export

| Key | What happens | Result |
|---|---|---|
| <kbd>Enter</kbd> | copy the image, quit (whiteboard: only copy) | PNG in the clipboard |
| <kbd>Ctrl</kbd>+<kbd>C</kbd> | copy the image, stay open; with a selection: copy the elements instead | PNG in the clipboard |
| <kbd>Ctrl</kbd>+<kbd>S</kbd> | save the editable drawing | PNG file with editing data |
| <kbd>Shift</kbd>+<kbd>Enter</kbd> | save like <kbd>Ctrl</kbd>+<kbd>S</kbd>, copy the file's path, quit (whiteboard: stays open) | file + path in the clipboard |
| <kbd>Ctrl</kbd>+<kbd>E</kbd> | export a clean image | PNG file without editing data |

The image is rendered in full resolution without the bar, selection frames or
handles. In screenshot mode it covers the screenshot or the crop; on the
whiteboard the area of all elements. With `xclip` installed, the clipboard keeps
the image after griffel quits.

**Files** go to `[output] dir` (default: your pictures folder, `griffel/`).
<kbd>Ctrl</kbd>+<kbd>S</kbd> creates a new file the first time and overwrites
the same file after that. Whiteboard files end in `_board.png`.

**Editable files** are normal PNGs that any program can show. Inside, they
carry the screenshot without markings and all elements, so griffel can open them
again with everything editable. With a crop, only the cropped part of the
screenshot is stored, and elements completely outside are left out; reopened,
the frame can't grow beyond it. `[output] keep_full_screenshot = true` keeps
the whole screenshot and the crop frame instead. Blur is always burned in. To
pass an image on without any of that, use <kbd>Ctrl</kbd>+<kbd>E</kbd>.

**Opening** a file: `griffel file.png`. A griffel drawing opens with
everything editable, a saved whiteboard as a whiteboard, any other PNG as the
background of a new drawing. An image larger than the screen (e.g. from another
monitor) is shown scaled down and saved in full resolution; a smaller one in
original size, centered.

## Copying elements and pasting images

| Key | Action |
|---|---|
| <kbd>Ctrl</kbd>+<kbd>C</kbd> with a selection | copy the elements |
| <kbd>Ctrl</kbd>+<kbd>V</kbd> | paste at the mouse |
| <kbd>Ctrl</kbd>+<kbd>D</kbd> | duplicate the selection, slightly offset |

Pasting works across windows, e.g. from a screenshot into the whiteboard, also
after the first one is closed. Pasted elements are selected afterwards, markers
count on, blur areas are left out on the whiteboard.

**A crop with its markings** can go to the whiteboard too: mark up the
screenshot, crop it (<kbd>X</kbd>), press <kbd>Enter</kbd> or
<kbd>Ctrl</kbd>+<kbd>C</kbd> without a selection, then
<kbd>Ctrl</kbd>+<kbd>V</kbd> in the whiteboard. The screenshot part arrives as
an image (blur burned in), and the markers, shapes and texts on it stay
separate, editable elements. Other programs get the finished image as usual.

**Images from other programs** (e.g. copied in a browser) are pasted as an
image element: it can be moved, resized at the corners (the aspect ratio stays),
deleted and put in front or behind; it has no color or stroke width.

## Whiteboard

`griffel --board` opens it. Saved whiteboards (`…_board.png`) open as a
whiteboard again.

| Action | Mouse | Keys |
|---|---|---|
| Pan | wheel (with <kbd>Shift</kbd>, tilt wheel or touchpad: sideways), drag with the middle button | – |
| Zoom (10–800 %) | <kbd>Ctrl</kbd>+wheel, towards the mouse | <kbd>Ctrl</kbd>+<kbd>0</kbd>: 100 % |
| See everything | – | <kbd>Ctrl</kbd>+<kbd>W</kbd>; again: back to the previous view |
| Change the background | – | <kbd>Ctrl</kbd>+<kbd>B</kbd> / <kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>B</kbd>: next / previous |

The backgrounds come from `[board] backgrounds`, the first one from
`[board] background`. The background is saved with the drawing and can be
undone. <kbd>Ctrl</kbd>+<kbd>W</kbd> fits everything into the window, at most
at 100 %. Pressing it again goes back only if you haven't zoomed or panned in
between.

<kbd>Esc</kbd> and <kbd>Enter</kbd> don't close the whiteboard. With unsaved
changes, <kbd>Ctrl</kbd>+<kbd>Q</kbd> or closing the window asks whether to
save, discard or cancel.

## History

*Screenshot mode only.*

Every screenshot you change something on is saved automatically, shortly after
each change and when quitting. Screenshots without changes are not kept. By
default the last 100 are kept in `~/.local/share/griffel/history/`
(`[history]`: on/off, folder, number).

| Key | Action |
|---|---|
| <kbd>←</kbd> | load the older screenshot into the same window |
| <kbd>→</kbd> | load the newer one |

Changes go into the loaded entry; undo starts fresh there.
`griffel --last` opens the latest entry directly, a good candidate for a hotkey.
An entry can also be opened as a file; then <kbd>Ctrl</kbd>+<kbd>S</kbd> creates
a separate file in the output folder.

The history keeps the whole screenshot and the crop frame, also with
`keep_full_screenshot = false`.

## Pointing: spotlight and magnifier

For showing things while sharing your screen or teaching.

| Key | Action |
|---|---|
| <kbd>E</kbd> | spotlight: everything darkened except a circle around the mouse |
| <kbd>Shift</kbd>+<kbd>E</kbd> | magnifier: magnifies around the mouse (2×) |

Clicks draw nothing meanwhile, and the pointer is hidden. The same key,
<kbd>Esc</kbd> or a tool change ends it. Radius, darkening and magnification
are set under `[pointer]`.

## Command line

```
griffel              annotate a screenshot of the monitor under the mouse
griffel FILE         open a saved drawing or any PNG
griffel --board      empty whiteboard in a normal window
griffel --last       open the latest screenshot from the history
griffel --version
```

Exit codes: 0 normally; 1 if a file can't be opened or the history is empty
(`--last`); 2 in a Wayland session.

**Wayland** is not supported. If `WAYLAND_DISPLAY` is set or
`XDG_SESSION_TYPE` is `wayland` (also when running via XWayland), griffel
refuses screenshots and image files with a notice. The whiteboard (`--board`,
saved whiteboards) still opens. If your setup can take screenshots anyway,
`GRIFFEL_IGNORE_WAYLAND=1` skips the check.

## Key reference

The defaults, grouped like the overview (<kbd>?</kbd>).

**Tools**

| Key | Action |
|---|---|
| <kbd>W</kbd> | select |
| <kbd>A</kbd> <kbd>S</kbd> <kbd>D</kbd> <kbd>F</kbd> <kbd>G</kbd> <kbd>T</kbd> | freehand, line, arrow (again: curved), rectangle, ellipse, text |
| <kbd>C</kbd> | marker (again: 1 2 3 / A B C) |
| <kbd>Z</kbd> | blur (screenshot) |
| <kbd>X</kbd> | crop (screenshot) |

**Color and size**

| Key | Action |
|---|---|
| <kbd>Shift</kbd>+<kbd>A</kbd> <kbd>S</kbd> <kbd>D</kbd> <kbd>F</kbd> <kbd>G</kbd> <kbd>Z</kbd> <kbd>X</kbd> <kbd>C</kbd> <kbd>V</kbd> <kbd>B</kbd> | color 1–10 |
| <kbd>Tab</kbd> | next color |
| <kbd>Shift</kbd>+<kbd>Tab</kbd> | previous color |
| <kbd>Alt</kbd>+<kbd>A</kbd> <kbd>S</kbd> <kbd>D</kbd> <kbd>F</kbd> | size level 1–4 |
| <kbd>Alt</kbd>+wheel | fine size |
| <kbd>Alt</kbd>+<kbd>V</kbd> | monospace text on/off |

**Selection**

| Key | Action |
|---|---|
| <kbd>Ctrl</kbd>+<kbd>A</kbd> | select all |
| <kbd>H</kbd> <kbd>J</kbd> <kbd>K</kbd> <kbd>L</kbd> | move |
| <kbd>Shift</kbd>+<kbd>H</kbd> <kbd>J</kbd> <kbd>K</kbd> <kbd>L</kbd> | move finely |
| <kbd>Q</kbd> | rotate counterclockwise |
| <kbd>Shift</kbd>+<kbd>Q</kbd> | rotate clockwise |
| <kbd>Ctrl</kbd>+<kbd>↑</kbd> | bring forward |
| <kbd>Ctrl</kbd>+<kbd>↓</kbd> | send backward |
| <kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>↑</kbd> | bring to front |
| <kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>↓</kbd> | send to back |
| <kbd>Del</kbd>, <kbd>Backspace</kbd> | delete (with a crop and nothing selected: clear the area) |
| <kbd>Ctrl</kbd>+<kbd>V</kbd> | paste |
| <kbd>Ctrl</kbd>+<kbd>D</kbd> | duplicate |

**Output**

| Key | Action |
|---|---|
| <kbd>Enter</kbd> | copy the image and quit |
| <kbd>Shift</kbd>+<kbd>Enter</kbd> | save, copy the path, quit |
| <kbd>Ctrl</kbd>+<kbd>C</kbd> | copy the image (with a selection: the elements) |
| <kbd>Ctrl</kbd>+<kbd>S</kbd> | save editable |
| <kbd>Ctrl</kbd>+<kbd>E</kbd> | export a clean PNG |

**View** (whiteboard)

| Key | Action |
|---|---|
| <kbd>Ctrl</kbd>+<kbd>0</kbd> | zoom 100 % |
| <kbd>Ctrl</kbd>+<kbd>W</kbd> | fit everything / back |
| <kbd>Ctrl</kbd>+<kbd>B</kbd> | next background |
| <kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>B</kbd> | previous background |

**History** (screenshot)

| Key | Action |
|---|---|
| <kbd>←</kbd> | older screenshot |
| <kbd>→</kbd> | newer screenshot |

**Pointing**

| Key | Action |
|---|---|
| <kbd>E</kbd> | spotlight on/off |
| <kbd>Shift</kbd>+<kbd>E</kbd> | magnifier on/off |

**General**

| Key | Action |
|---|---|
| <kbd>R</kbd> | undo |
| <kbd>Shift</kbd>+<kbd>R</kbd> | redo |
| <kbd>B</kbd> | bar on/off |
| <kbd>?</kbd> | overview of all keys |
| <kbd>Ctrl</kbd>+<kbd>Q</kbd> | quit |
| <kbd>Esc</kbd> | end text input or pointing, remove the crop, deselect, otherwise quit (fixed) |
