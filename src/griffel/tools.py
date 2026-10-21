"""Tools: enum, names from the config, geometry of the shapes and icons.

Without Canvas dependencies, so elements.py and the rest of the package can build on it
without importing each other.
"""
import math
import sys
from enum import Enum

from PySide6.QtCore import QPointF, QRectF
from PySide6.QtGui import QPainterPath


class Tool(Enum):
    FREEHAND = "Freehand"
    LINE = "Line"
    ARROW = "Arrow"
    RECT = "Rectangle"
    ELLIPSE = "Ellipse"
    TEXT = "Text"
    SELECT = "Select"  # not a drawing tool, always first in the bar (key W)
    MARKER = "Marker"  # numbered circle, optionally with a pointer line; fixed place at the end (key C)
    BLUR = "Blur"  # pixelates the screenshot below; fixed place at the end (key Z), screenshot mode only


# Tools with a fixed place in the bar, not part of [tools] order
FIXED_TOOLS = (Tool.SELECT, Tool.MARKER, Tool.BLUR)

# Marker: circle radius from the stroke width (levels 2/4/8/12 px -> radius 15/18/24/30)
MARKER_BASE_RADIUS = 12
MARKER_RADIUS_PER_WIDTH = 1.5


def marker_radius(width):
    return MARKER_BASE_RADIUS + width * MARKER_RADIUS_PER_WIDTH


# Corner radius of the rectangle in pixels (default; per element in ShapeElement.radius,
# for new rectangles from [rect] in the config)
RECT_RADIUS = 8


def parse_tool(name):
    """Config name ('freehand', 'Rect', …) -> Tool; unknown -> None."""
    return Tool.__members__.get(name.strip().upper())


def tool_order(names):
    """Tools in the order of the config, without unknown ones and duplicates.

    Without a usable list: all tools in the order of the enum.
    Select, Marker and Blur are not part of it, they have a fixed place (FIXED_TOOLS).
    """
    result = []
    for name in names or []:
        tool = parse_tool(name)
        if tool is None:
            print(f"[tools] Unknown tool: {name!r}", file=sys.stderr)
        elif tool not in result and tool not in FIXED_TOOLS:
            result.append(tool)
    return result or [t for t in Tool if t not in FIXED_TOOLS]


def shape_path(tool, start, end, pen_width, radius=RECT_RADIUS):
    """Builds the path of a shape from start and end point (everything except freehand)."""
    path = QPainterPath()
    if tool == Tool.LINE:
        path.moveTo(start)
        path.lineTo(end)
    elif tool == Tool.ARROW:
        path.moveTo(start)
        path.lineTo(end)
        add_arrow_head(path, end, math.atan2(end.y() - start.y(), end.x() - start.x()), pen_width)
    elif tool == Tool.RECT:
        # Qt shrinks the radius itself if the rectangle is too small for it
        path.addRoundedRect(QRectF(start, end).normalized(), radius, radius)
    elif tool == Tool.ELLIPSE:
        path.addEllipse(QRectF(start, end).normalized())
    elif tool == Tool.BLUR:  # area that gets pixelated (drawn in ShapeElement.paint)
        path.addRect(QRectF(start, end).normalized())
    elif tool == Tool.MARKER:  # start = tip (points at the spot), end = circle center
        path.moveTo(start)
        path.lineTo(end)
        path.addEllipse(end, marker_radius(pen_width), marker_radius(pen_width))
    return path


def arrow_head_length(pen_width):
    return max(14, pen_width * 4)


def add_arrow_head(path, end, angle, pen_width):
    """Two strokes back from end, against the direction angle (radians)."""
    head_len = arrow_head_length(pen_width)
    spread = math.radians(25)
    for sign in (-1, 1):
        tip = QPointF(
            end.x() - head_len * math.cos(angle + sign * spread),
            end.y() - head_len * math.sin(angle + sign * spread),
        )
        path.moveTo(end)
        path.lineTo(tip)


# --- Curved arrow (roadmap 21, plan docs/notes/plan-kurvenpfeil.md) ---
def straight_controls(start, end):
    """Control points on the thirds of the chord: the cubic curve is exactly straight."""
    return start + (end - start) / 3, start + (end - start) * (2 / 3)


def fit_cubic(points, straight_tolerance=0.0):
    """Control points (c1, c2) of the cubic Bézier curve from points[0] to points[-1]
    that runs as close as possible to all points (least squares).

    Each point gets a parameter t from its share of the stroke length (chord length
    parametrization); the curve at t is B(t) = b0·P0 + b1·c1 + b2·c2 + b3·P3 with the
    Bernstein weights b0…b3. Start and end are fixed, so only c1 and c2 are unknown: setting
    the derivative of the squared error to zero gives two linear equations (per axis).
    If no point lies further than straight_tolerance from the chord, the curve becomes
    exactly straight (an almost straight stroke should not sag).
    """
    start, end = points[0], points[-1]
    chord = end - start
    length = math.hypot(chord.x(), chord.y())
    if length > 1e-9:
        deviation = max(abs(chord.x() * (p.y() - start.y()) - chord.y() * (p.x() - start.x())) / length
                        for p in points)
    else:
        deviation = max(math.hypot(p.x() - start.x(), p.y() - start.y()) for p in points)
    if len(points) < 3 or deviation <= straight_tolerance:
        return straight_controls(start, end)
    steps = [math.hypot(b.x() - a.x(), b.y() - a.y()) for a, b in zip(points, points[1:])]
    total = sum(steps)
    if total < 1e-9:
        return straight_controls(start, end)
    a11 = a12 = a22 = 0.0
    x1, x2 = QPointF(0, 0), QPointF(0, 0)
    run = 0.0
    for point, step in zip(points, [0.0] + steps):
        run += step
        t = run / total
        u = 1 - t
        b0, b1, b2, b3 = u ** 3, 3 * u * u * t, 3 * u * t * t, t ** 3
        rest = point - start * b0 - end * b3  # what c1 and c2 have to explain
        a11 += b1 * b1
        a12 += b1 * b2
        a22 += b2 * b2
        x1 += rest * b1
        x2 += rest * b2
    det = a11 * a22 - a12 * a12
    if abs(det) < 1e-12:
        return straight_controls(start, end)
    return (x1 * a22 - x2 * a12) / det, (x2 * a11 - x1 * a12) / det


def curve_path(points, pen_width):
    """Curved arrow from points = [start, c1, c2, end]: the curve plus the head at the end.
    The head points along the last stretch of the curve as long as the head (looks right even
    where the curve bends sharply at its very end)."""
    start, c1, c2, end = points
    path = QPainterPath(start)
    path.cubicTo(c1, c2, end)
    total = path.length()
    if total < 1e-6:
        return path
    back = path.pointAtPercent(path.percentAtLength(max(0.0, total - arrow_head_length(pen_width))))
    if math.hypot(end.x() - back.x(), end.y() - back.y()) < 1e-6:
        back = start
    add_arrow_head(path, end, math.atan2(end.y() - back.y(), end.x() - back.x()), pen_width)
    return path


def tool_icon(tool, curve=False):
    """Icon for the tool bar, in field coordinates 0-30 (bottom right stays free for the key).
    curve: the arrow as the curved variant."""
    path = QPainterPath()
    if tool == Tool.FREEHAND:
        path.moveTo(6, 18)
        path.cubicTo(10, 4, 14, 26, 23, 9)
    elif tool == Tool.LINE:
        path.moveTo(7, 22)
        path.lineTo(22, 7)
    elif tool == Tool.ARROW and curve:  # arc with the head at its upper end
        path.moveTo(6, 22)
        path.cubicTo(8, 10, 14, 7, 22, 8)
        path.moveTo(16, 4)
        path.lineTo(22, 8)
        path.lineTo(17, 13)
    elif tool == Tool.ARROW:
        path.moveTo(7, 22)
        path.lineTo(22, 7)
        path.moveTo(14, 7)
        path.lineTo(22, 7)
        path.lineTo(22, 15)
    elif tool == Tool.RECT:
        path.addRoundedRect(QRectF(5, 8, 17, 12), 3, 3)
    elif tool == Tool.ELLIPSE:
        path.addEllipse(QRectF(5, 7, 17, 14))
    elif tool == Tool.TEXT:
        path.moveTo(8, 8)
        path.lineTo(22, 8)
        path.moveTo(15, 8)
        path.lineTo(15, 22)
    elif tool == Tool.MARKER:  # circle with "1"
        path.addEllipse(QRectF(5, 5, 19, 19))
        path.moveTo(12.5, 11)
        path.lineTo(15, 9)
        path.lineTo(15, 20)
    elif tool == Tool.BLUR:  # grid like coarse pixels (bottom right stays free for the key)
        for i in range(4):
            path.moveTo(6 + i * 5, 6)
            path.lineTo(6 + i * 5, 21)
            path.moveTo(6, 6 + i * 5)
            path.lineTo(21, 6 + i * 5)
    elif tool == Tool.SELECT:  # mouse pointer
        path.moveTo(9, 5)
        path.lineTo(9, 21)
        path.lineTo(13, 17)
        path.lineTo(16, 23)
        path.lineTo(18.5, 22)
        path.lineTo(15.5, 16)
        path.lineTo(21, 16)
        path.closeSubpath()
    return path
