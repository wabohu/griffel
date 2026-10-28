# File format

A drawing saved with <kbd>Ctrl</kbd>+<kbd>S</kbd> (or
<kbd>Shift</kbd>+<kbd>Enter</kbd>, or kept in the history) is a normal PNG that
shows the finished picture, markings included. Any image viewer can open it.

To keep it editable, the PNG also carries a JSON document in a text chunk with
the key `griffel`. Programs that save the image again usually drop that chunk; the picture stays, the editing data is gone.

**What this means for privacy**: the file contains the screenshot *without* the
markings. With a crop, only the cropped part is stored (unless
`[output] keep_full_screenshot = true`); history entries always keep the whole
screenshot. Blurred areas are burned into the stored screenshot, so they can't
be recovered. To pass an image on without any of this, export it with
<kbd>Ctrl</kbd>+<kbd>E</kbd>.

## The document

```json
{
  "format": "griffel",
  "version": 1,
  "background": {"type": "image", "png": "<Base64 PNG of the screenshot>"},
  "elements": [ ... ],
  "crop": [x, y, width, height]
}
```

- `background`: the screenshot without markings, or on a whiteboard
  `{"type": "color", "color": "#24283b"}`.
- `elements`: from bottom to top (later ones are drawn on top).
- `crop` (optional): the crop frame. Missing when there is none, and in files
  that store only the cropped part.
- `version`: a newer version than griffel knows opens anyway, with a warning;
  elements it can't read are skipped.

Coordinates are pixels of the background image (on a whiteboard: canvas
coordinates, which can be negative). Colors are `"#rrggbb"`. Every
element has a `type`, an `id` (unique within the file), `pos` (`[x, y]`) and
`rotation` (degrees, clockwise, around `pos`); its own points are relative to
`pos`.

### Shapes: `"type": "shape"`

| Key | Meaning |
|---|---|
| `tool` | `freehand`, `line`, `arrow`, `rect`, `ellipse`, `marker` or `blur` |
| `points` | `[[x, y], ...]` relative to `pos`. Lines, arrows, rectangles, ellipses, blur: two corners or end points. Freehand: the path. Curved arrow: start, two control points, end (cubic Bézier). Marker: tip, circle center |
| `color`, `width` | color and stroke width |
| `radius` | rectangles: corner radius |
| `kind` | markers: `number` or `letter`; arrows: `curve` for a curved arrow |
| `order` | markers: placing order; the shown number is the position among markers of the same kind |
| `label` | optional text inside the shape or on the line: `{"text", "font_size"}`, plus `"font": "mono"` for monospace |
| `ends` | lines and arrows docked to other elements: `[id or null, id or null]` for start and end |

### Text: `"type": "text"`

`text`, `color`, `font_size`, and `"font": "mono"` for monospace.

### Images: `"type": "image"`

`png` (Base64 PNG of the image) and `size` (`[width, height]` as shown).

## Older files

Files from before the rename to griffel use the key `slate` for the text chunk
and the format name; griffel still reads them. Broken or unknown elements are
skipped, a broken document opens as a plain image.
