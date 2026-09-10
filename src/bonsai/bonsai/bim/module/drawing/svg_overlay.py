# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026
# SPDX-License-Identifier: GPL-3.0-or-later
# This file was generated with the assistance of an AI coding tool.

"""Stroke-only preview of the final drawing SVG, independent of Blender.

Supports tag/class selectors (including compounds and descendants), inherited
stroke styles, and straight paths. Fills, curves, transforms, clipping, text,
references and paint servers are deliberately outside this first slice.
"""

import math
import re
import xml.etree.ElementTree as ET
from typing import NamedTuple

Point = tuple[float, float]
NUMBER = r"[-+]?(?:\d*\.\d+|\d+\.?\d*)(?:[eE][-+]?\d+)?"
TOKEN = re.compile(rf"[MLHVZmlhvz]|{NUMBER}")
SELECTOR = re.compile(r"(?:[a-zA-Z][\w-]*|\*)?(?:\.[\w-]+)*")
DEFAULTS = {"stroke": "none", "stroke-width": "1", "stroke-opacity": "1", "stroke-dasharray": "none"}
COLORS = {
    "black": "000000",
    "silver": "c0c0c0",
    "gray": "808080",
    "white": "ffffff",
    "maroon": "800000",
    "red": "ff0000",
    "purple": "800080",
    "fuchsia": "ff00ff",
    "green": "008000",
    "lime": "00ff00",
    "olive": "808000",
    "yellow": "ffff00",
    "navy": "000080",
    "blue": "0000ff",
    "teal": "008080",
    "aqua": "00ffff",
    "orange": "ffa500",
    "grey": "808080",
}


class Stroke(NamedTuple):
    segments: list[tuple[Point, Point]]
    color: tuple[float, float, float, float]
    width: float


class Drawing(NamedTuple):
    view_box: tuple[float, float, float, float]
    strokes: list[Stroke]


def numbers(value: str) -> list[float]:
    if re.sub(NUMBER, "", value).strip(" ,\t\r\n"):
        raise ValueError("Unsupported SVG number")
    result = [float(v) for v in re.findall(NUMBER, value)]
    if not all(math.isfinite(v) for v in result):
        raise ValueError("Non-finite SVG number")
    return result


def length(value: str) -> float:
    # Bonsai's viewBox uses paper mm, with unitless (or px) CSS lengths.
    values = numbers(value.removesuffix("px"))
    if len(values) != 1:
        raise ValueError("Unsupported SVG length")
    return values[0]


def color(value: str) -> tuple[float, float, float] | None:
    value = value.strip().lower()
    value = "#" + COLORS[value] if value in COLORS else value
    if re.fullmatch(r"#[0-9a-f]{3}(?:[0-9a-f]{3})?", value):
        digits = value[1:]
        if len(digits) == 3:
            digits = "".join(c * 2 for c in digits)
        return tuple(int(digits[i : i + 2], 16) / 255 for i in (0, 2, 4))
    if value.startswith("rgb(") and value.endswith(")"):
        values = numbers(value[4:-1])
        if len(values) == 3:
            return tuple(max(0, min(255, v)) / 255 for v in values)
    return None


def declarations(text: str) -> dict[str, tuple[bool, str]]:
    result = {}
    for declaration in text.split(";"):
        key, sep, value = declaration.partition(":")
        key, value = key.strip().lower(), value.strip()
        if sep and value:
            important = bool(re.search(r"\s*!important\s*$", value, re.I))
            value = re.sub(r"\s*!important\s*$", "", value, flags=re.I)
            if key not in result or important or not result[key][0]:
                result[key] = (important, value)
    return result


def matches(selector: list[str], ancestry: list[ET.Element]) -> bool:
    def compound(part, element):
        tag, *classes = part.split(".")
        return (tag in ("", "*", element.tag.rsplit("}", 1)[-1])) and set(classes).issubset(
            element.get("class", "").split()
        )

    if not compound(selector[-1], ancestry[-1]):
        return False
    index = len(ancestry) - 2
    for part in reversed(selector[:-1]):
        while index >= 0 and not compound(part, ancestry[index]):
            index -= 1
        if index < 0:
            return False
        index -= 1
    return True


def paths(data: str) -> list[list[Point]]:
    """Reject a whole primitive if any command is unsupported, avoiding false joins."""
    if TOKEN.sub("", data).strip(" ,\t\r\n"):
        raise ValueError("Unsupported SVG path")
    tokens = TOKEN.findall(data)
    result = []
    current = (0.0, 0.0)
    command = None
    index = 0
    while index < len(tokens):
        if tokens[index].isalpha():
            command = tokens[index]
            index += 1
            if command.upper() == "Z":
                if not result:
                    raise ValueError("Path must start with moveto")
                current = result[-1][0]
                result[-1].append(current)
                command = None
                continue
        if command is None or (not result and command.upper() != "M"):
            raise ValueError("Path must start with moveto")
        count = 2 if command.upper() in ("M", "L") else 1
        values = numbers(" ".join(tokens[index : index + count]))
        if len(values) != count:
            raise ValueError("Incomplete SVG path command")
        index += count
        relative = command.islower()
        x, y = current
        if command.upper() in ("M", "L"):
            current = (values[0] + (x if relative else 0), values[1] + (y if relative else 0))
        elif command.upper() == "H":
            current = (values[0] + (x if relative else 0), y)
        else:
            current = (x, values[0] + (y if relative else 0))
        if command.upper() == "M":
            result.append([current])
            command = "l" if relative else "L"
        else:
            result[-1].append(current)
    return result


def segments(points: list[Point], dash: list[float]) -> list[tuple[Point, Point]]:
    if not dash or sum(dash) == 0:
        return list(zip(points, points[1:]))
    if len(dash) % 2:
        dash = dash * 2
    result = []
    index, remaining = 0, dash[0]
    for start, end in zip(points, points[1:]):
        distance = math.dist(start, end)
        position = 0.0
        while position < distance:
            if remaining <= 0:
                index = (index + 1) % len(dash)
                remaining = dash[index]
                continue
            step = min(remaining, distance - position)
            if index % 2 == 0:
                result.append(
                    tuple(
                        tuple(a + (b - a) * fraction / distance for a, b in zip(start, end))
                        for fraction in (position, position + step)
                    )
                )
            position += step
            remaining -= step
    return result


def parse_svg(source: str) -> Drawing:
    root = ET.fromstring(source)
    view_box = numbers(root.get("viewBox", ""))
    if len(view_box) != 4 or min(view_box[2:]) <= 0:
        raise ValueError("Drawing SVG needs a positive viewBox")
    rules = []
    for element in root.iter():
        if element.tag.rsplit("}", 1)[-1] != "style":
            continue
        css = re.sub(r"/\*.*?\*/", "", "".join(element.itertext()), flags=re.S)
        # At-rules and nested rules are outside this subset.
        css = re.sub(r"@[^;{}]+;|@[^{}]+\{(?:[^{}]|\{[^{}]*\})*\}", "", css)
        for selectors, body in re.findall(r"([^{}]+)\{([^{}]*)\}", css):
            for selector in selectors.split(","):
                parts = selector.split()
                if not parts or not all(SELECTOR.fullmatch(part) for part in parts):
                    continue
                specificity = (selector.count("."), sum(part[0] not in ".*" for part in parts))
                rules.append((parts, specificity, declarations(body)))

    strokes = []

    def visit(element, ancestry, inherited):
        tag = element.tag.rsplit("}", 1)[-1]
        if tag not in ("svg", "g", "a", "path", "line", "polyline", "polygon"):
            return
        if tag == "svg" and ancestry:
            return
        ancestry = ancestry + [element]
        style = dict(inherited)
        winners = {}
        for key, value in element.attrib.items():
            winners[key] = ((False, 0, 0, 0, -1), value)
        for order, (selector, specificity, properties) in enumerate(rules):
            if matches(selector, ancestry):
                for key, (important, value) in properties.items():
                    priority = (important, 0, *specificity, order)
                    if key not in winners or priority >= winners[key][0]:
                        winners[key] = (priority, value)
        for key, (important, value) in declarations(element.get("style", "")).items():
            priority = (important, 1, 0, 0, 0)
            if key not in winners or priority >= winners[key][0]:
                winners[key] = (priority, value)
        for key, (_, value) in winners.items():
            if value != "inherit":
                style[key] = value
        if style.get("display") == "none" or any(
            style.get(key, "none") != "none" for key in ("transform", "clip-path", "mask", "filter")
        ):
            return
        try:
            opacity = float(inherited.get("opacity", "1")) * float(winners.get("opacity", (None, "1"))[1])
            style["opacity"] = str(opacity)
            if tag in ("svg", "g", "a"):
                for child in element:
                    visit(child, ancestry, style)
                return
            rgb = color(style["stroke"])
            width = length(style["stroke-width"])
            alpha = max(0, min(1, opacity * float(style["stroke-opacity"])))
            if rgb is None or width <= 0 or alpha == 0 or style.get("visibility") in ("hidden", "collapse"):
                return
            if tag == "path":
                polylines = paths(element.get("d", ""))
            elif tag == "line":
                polylines = [[tuple(length(element.get(f"{axis}{i}", "0")) for axis in "xy") for i in (1, 2)]]
            else:
                values = numbers(element.get("points", ""))
                if len(values) % 2:
                    return
                points = list(zip(values[::2], values[1::2]))
                polylines = [points + points[:1] if tag == "polygon" else points]
            dash = [] if style["stroke-dasharray"] == "none" else numbers(style["stroke-dasharray"])
            if any(v < 0 for v in dash):
                dash = []
            edges = [edge for points in polylines for edge in segments(points, dash)]
            if edges:
                strokes.append(Stroke(edges, (*rgb, alpha), width))
        except (ValueError, OverflowError):
            # An unsupported style or malformed primitive must not break the viewport.
            return

    visit(root, [], DEFAULTS)
    return Drawing(tuple(view_box), strokes)


def paper_to_camera(point: Point, view_box: tuple[float, float, float, float], width: float, height: float) -> Point:
    """Invert SvgWriter's paper mapping; dimensions encode the drawing scale."""
    x, y, w, h = view_box
    return ((point[0] - x) / w - 0.5) * width, (0.5 - (point[1] - y) / h) * height
