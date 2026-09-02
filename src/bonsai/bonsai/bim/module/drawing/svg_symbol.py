# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026 Bonsai Contributors
#
# This file is part of Bonsai.
#
# Bonsai is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Bonsai is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Bonsai.  If not, see <http://www.gnu.org/licenses/>.

# This file was generated with the assistance of an AI coding tool.

"""Converts symbol definitions from ``symbols.svg`` into 2D polylines that the
drawing decorators can draw directly in the 3D viewport.

Only the small subset of SVG used by Bonsai's bundled ``symbols.svg`` (and, by
extension, any custom replacement following the same conventions) is
supported: ``<rect>``, ``<circle>``, ``<ellipse>``, ``<line>``, ``<polyline>``,
``<polygon>`` and ``<path>`` with the ``M/L/H/V/C/S/Q/T/A/Z`` commands.
``<text>`` elements (used as template fields, e.g. door tag numbers) are
ignored as text is drawn separately by the decorators.

Parsing is deliberately forgiving: any unsupported/malformed content is
skipped rather than raised, so a symbol that can't be parsed simply falls
back to the generic placeholder marker used previously.
"""

from __future__ import annotations

import math
import os
import re
from functools import lru_cache
from typing import Optional
from xml.etree import ElementTree as ET

from mathutils import Vector

# number of segments used to tessellate curves/arcs/circles
CURVE_SEGMENTS = 12
CIRCLE_SEGMENTS = 24

_NUMBER_RE = re.compile(r"[-+]?(?:\d+\.\d*|\.\d+|\d+)(?:[eE][-+]?\d+)?")
_TOKEN_RE = re.compile(r"[MmLlHhVvCcSsQqTtAaZz]|" + _NUMBER_RE.pattern)
_ARITY = {"M": 2, "L": 2, "H": 1, "V": 1, "C": 6, "S": 4, "Q": 4, "T": 2, "A": 7, "Z": 0}
_COMMAND_LETTERS = set("MmLlHhVvCcSsQqTtAaZz")


def _parse_path_commands(d: str) -> list[tuple[str, list[float]]]:
    """Tokenize a SVG path ``d`` attribute into ``(command, args)`` pairs,
    expanding implicit repeated coordinates into separate commands."""
    tokens = _TOKEN_RE.findall(d)
    commands: list[tuple[str, list[float]]] = []
    i = 0
    n = len(tokens)
    cmd: Optional[str] = None
    while i < n:
        tok = tokens[i]
        if tok in _COMMAND_LETTERS:
            cmd = tok
            i += 1
            if _ARITY[cmd.upper()] == 0:
                commands.append((cmd, []))
                cmd = None
            continue
        if cmd is None:
            # stray number without a preceding command, ignore it
            i += 1
            continue
        arity = _ARITY[cmd.upper()]
        try:
            args = [float(tokens[i + k]) for k in range(arity)]
        except (IndexError, ValueError):
            break
        i += arity
        commands.append((cmd, args))
        # implicit repeats of a moveto behave as a lineto
        if cmd in ("M", "m"):
            cmd = "L" if cmd == "M" else "l"
    return commands


def _cubic_bezier_points(
    p0: Vector, p1: Vector, p2: Vector, p3: Vector, segments: int = CURVE_SEGMENTS
) -> list[Vector]:
    points = []
    n = max(1, segments)
    for i in range(1, n + 1):
        t = i / n
        mt = 1 - t
        x = mt**3 * p0.x + 3 * mt**2 * t * p1.x + 3 * mt * t**2 * p2.x + t**3 * p3.x
        y = mt**3 * p0.y + 3 * mt**2 * t * p1.y + 3 * mt * t**2 * p2.y + t**3 * p3.y
        points.append(Vector((x, y)))
    return points


def _quadratic_bezier_points(p0: Vector, p1: Vector, p2: Vector, segments: int = CURVE_SEGMENTS) -> list[Vector]:
    points = []
    n = max(1, segments)
    for i in range(1, n + 1):
        t = i / n
        mt = 1 - t
        x = mt**2 * p0.x + 2 * mt * t * p1.x + t**2 * p2.x
        y = mt**2 * p0.y + 2 * mt * t * p1.y + t**2 * p2.y
        points.append(Vector((x, y)))
    return points


def _ellipse_arc_points(
    cx: float, cy: float, rx: float, ry: float, start_deg: float, end_deg: float, segments: int = CIRCLE_SEGMENTS
) -> list[Vector]:
    points = []
    t0 = math.radians(start_deg)
    t1 = math.radians(end_deg)
    n = max(1, segments)
    for i in range(n + 1):
        t = t0 + (t1 - t0) * i / n
        points.append(Vector((cx + rx * math.cos(t), cy + ry * math.sin(t))))
    return points


def _arc_to_points(
    x0: float,
    y0: float,
    rx: float,
    ry: float,
    phi_deg: float,
    large_arc: bool,
    sweep: bool,
    x1: float,
    y1: float,
    segments: int = CURVE_SEGMENTS,
) -> list[Vector]:
    """Elliptical arc endpoint-to-center parameterization, per SVG spec F.6.5."""
    if rx == 0 or ry == 0:
        return [Vector((x1, y1))]

    phi = math.radians(phi_deg)
    cos_phi, sin_phi = math.cos(phi), math.sin(phi)
    dx2 = (x0 - x1) / 2
    dy2 = (y0 - y1) / 2
    x1p = cos_phi * dx2 + sin_phi * dy2
    y1p = -sin_phi * dx2 + cos_phi * dy2

    rx, ry = abs(rx), abs(ry)
    lam = (x1p**2) / (rx**2) + (y1p**2) / (ry**2)
    if lam > 1:
        s = math.sqrt(lam)
        rx *= s
        ry *= s

    sign = -1 if large_arc == sweep else 1
    num = rx**2 * ry**2 - rx**2 * y1p**2 - ry**2 * x1p**2
    den = rx**2 * y1p**2 + ry**2 * x1p**2
    co = sign * math.sqrt(max(num / den, 0)) if den else 0
    cxp = co * (rx * y1p / ry)
    cyp = co * (-ry * x1p / rx)

    cx = cos_phi * cxp - sin_phi * cyp + (x0 + x1) / 2
    cy = sin_phi * cxp + cos_phi * cyp + (y0 + y1) / 2

    def vector_angle(ux, uy, vx, vy):
        dot = ux * vx + uy * vy
        length = math.sqrt(ux**2 + uy**2) * math.sqrt(vx**2 + vy**2)
        a = math.acos(max(-1.0, min(1.0, dot / length))) if length else 0.0
        return -a if (ux * vy - uy * vx) < 0 else a

    theta1 = vector_angle(1, 0, (x1p - cxp) / rx, (y1p - cyp) / ry)
    dtheta = vector_angle((x1p - cxp) / rx, (y1p - cyp) / ry, (-x1p - cxp) / rx, (-y1p - cyp) / ry)
    if not sweep and dtheta > 0:
        dtheta -= 2 * math.pi
    elif sweep and dtheta < 0:
        dtheta += 2 * math.pi

    points = []
    n = max(1, segments)
    for i in range(1, n + 1):
        t = theta1 + dtheta * i / n
        ex = rx * math.cos(t)
        ey = ry * math.sin(t)
        points.append(Vector((cos_phi * ex - sin_phi * ey + cx, sin_phi * ex + cos_phi * ey + cy)))
    return points


def _path_to_polylines(d: str) -> list[list[Vector]]:
    commands = _parse_path_commands(d)
    polylines: list[list[Vector]] = []
    cur = Vector((0.0, 0.0))
    start = Vector((0.0, 0.0))
    poly: list[Vector] = []
    prev_cubic_ctrl: Optional[Vector] = None
    prev_quad_ctrl: Optional[Vector] = None

    def flush():
        nonlocal poly
        if len(poly) >= 2:
            polylines.append(poly)
        poly = []

    for cmd, args in commands:
        c = cmd.upper()
        off = cur if cmd.islower() else Vector((0.0, 0.0))

        if c == "M":
            flush()
            cur = Vector((args[0], args[1])) + off
            start = cur.copy()
            poly = [cur.copy()]
        elif c == "L":
            cur = Vector((args[0], args[1])) + off
            poly.append(cur.copy())
        elif c == "H":
            cur = Vector((cur.x + args[0] if cmd.islower() else args[0], cur.y))
            poly.append(cur.copy())
        elif c == "V":
            cur = Vector((cur.x, cur.y + args[0] if cmd.islower() else args[0]))
            poly.append(cur.copy())
        elif c == "C":
            p1 = Vector((args[0], args[1])) + off
            p2 = Vector((args[2], args[3])) + off
            p3 = Vector((args[4], args[5])) + off
            poly.extend(_cubic_bezier_points(cur, p1, p2, p3))
            prev_cubic_ctrl = p2
            cur = p3
        elif c == "S":
            p2 = Vector((args[0], args[1])) + off
            p3 = Vector((args[2], args[3])) + off
            p1 = (2 * cur - prev_cubic_ctrl) if prev_cubic_ctrl is not None else cur.copy()
            poly.extend(_cubic_bezier_points(cur, p1, p2, p3))
            prev_cubic_ctrl = p2
            cur = p3
        elif c == "Q":
            p1 = Vector((args[0], args[1])) + off
            p2 = Vector((args[2], args[3])) + off
            poly.extend(_quadratic_bezier_points(cur, p1, p2))
            prev_quad_ctrl = p1
            cur = p2
        elif c == "T":
            p2 = Vector((args[0], args[1])) + off
            p1 = (2 * cur - prev_quad_ctrl) if prev_quad_ctrl is not None else cur.copy()
            poly.extend(_quadratic_bezier_points(cur, p1, p2))
            prev_quad_ctrl = p1
            cur = p2
        elif c == "A":
            rx, ry, rot, large_arc, sweep, x, y = args
            target = Vector((x, y)) + off
            poly.extend(_arc_to_points(cur.x, cur.y, rx, ry, rot, bool(large_arc), bool(sweep), target.x, target.y))
            cur = target
        elif c == "Z":
            if poly and (poly[0] - start).length > 1e-9:
                poly.append(start.copy())
            cur = start.copy()
            flush()
            continue

        if c not in ("C", "S"):
            prev_cubic_ctrl = None
        if c not in ("Q", "T"):
            prev_quad_ctrl = None

    flush()
    return polylines


def _rect_to_polyline(elem: ET.Element) -> list[Vector]:
    x = float(elem.get("x", 0))
    y = float(elem.get("y", 0))
    w = float(elem.get("width", 0))
    h = float(elem.get("height", 0))
    if w <= 0 or h <= 0:
        return []

    rx_attr, ry_attr = elem.get("rx"), elem.get("ry")
    rx = float(rx_attr) if rx_attr is not None else (float(ry_attr) if ry_attr is not None else 0.0)
    ry = float(ry_attr) if ry_attr is not None else rx
    rx = max(0.0, min(rx, w / 2))
    ry = max(0.0, min(ry, h / 2))

    if rx <= 0 or ry <= 0:
        return [Vector((x, y)), Vector((x + w, y)), Vector((x + w, y + h)), Vector((x, y + h)), Vector((x, y))]

    segments = max(2, CURVE_SEGMENTS // 4)
    points = [Vector((x + rx, y)), Vector((x + w - rx, y))]
    points += _ellipse_arc_points(x + w - rx, y + ry, rx, ry, 270, 360, segments)
    points += _ellipse_arc_points(x + w - rx, y + h - ry, rx, ry, 0, 90, segments)
    points += _ellipse_arc_points(x + rx, y + h - ry, rx, ry, 90, 180, segments)
    points += _ellipse_arc_points(x + rx, y + ry, rx, ry, 180, 270, segments)
    return points


def _shape_to_polylines(elem: ET.Element) -> list[list[Vector]]:
    tag = elem.tag.rsplit("}", 1)[-1]
    try:
        if tag == "rect":
            polyline = _rect_to_polyline(elem)
            return [polyline] if polyline else []
        if tag in ("circle", "ellipse"):
            cx = float(elem.get("cx", 0))
            cy = float(elem.get("cy", 0))
            rx = float(elem.get("r", elem.get("rx", 0)))
            ry = float(elem.get("r", elem.get("ry", 0)))
            if rx <= 0 or ry <= 0:
                return []
            return [_ellipse_arc_points(cx, cy, rx, ry, 0, 360)]
        if tag == "line":
            p1 = Vector((float(elem.get("x1", 0)), float(elem.get("y1", 0))))
            p2 = Vector((float(elem.get("x2", 0)), float(elem.get("y2", 0))))
            return [[p1, p2]]
        if tag == "path":
            d = elem.get("d")
            return _path_to_polylines(d) if d else []
        if tag in ("polyline", "polygon"):
            coords = [float(n) for n in _NUMBER_RE.findall(elem.get("points", ""))]
            points = [Vector((coords[i], coords[i + 1])) for i in range(0, len(coords) - 1, 2)]
            if len(points) < 2:
                return []
            if tag == "polygon":
                points.append(points[0])
            return [points]
    except (TypeError, ValueError, ZeroDivisionError, IndexError):
        return []
    return []


@lru_cache(maxsize=8)
def _load_symbols(path: str, mtime: float) -> dict[str, list[list[Vector]]]:
    """Parse `path` (a symbols.svg file) once per (path, mtime) and return
    ``{symbol_id: [polyline, ...]}`` where each polyline is a list of local
    2D coordinates in the symbol's own SVG units."""
    result: dict[str, list[list[Vector]]] = {}
    try:
        root = ET.parse(path).getroot()
    except (ET.ParseError, OSError):
        return result

    for group in root:
        symbol_id = group.get("id")
        if not symbol_id:
            continue
        polylines: list[list[Vector]] = []
        for child in group:
            if child.tag.rsplit("}", 1)[-1] == "text":
                continue
            polylines.extend(_shape_to_polylines(child))
        if polylines:
            result[symbol_id] = polylines
    return result


def get_symbol_polylines(symbols_path: str, symbol_id: str) -> Optional[list[list[Vector]]]:
    """Return cached local-space polylines for `symbol_id`, or `None` if the
    symbol couldn't be found or parsed (e.g. a custom symbol that isn't
    present in the resolved symbols.svg), so callers can fall back to a
    generic placeholder marker."""
    if not symbols_path or not symbol_id:
        return None
    try:
        mtime = os.path.getmtime(symbols_path)
    except OSError:
        return None
    return _load_symbols(symbols_path, mtime).get(symbol_id)
