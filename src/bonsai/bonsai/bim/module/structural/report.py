# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026 Ryan Schultz
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

"""Calculation reports: the calculations behind what Bonsai solves, with their diagrams.

A report is a folder holding the same content as HTML, with its math rendered by a bundled
KaTeX, and as Markdown, which most Markdown viewers render too. Diagrams are SVG files that
both link, drawn from the same data as the loads shown in the viewport.
"""

import datetime
import math
import re
import shutil
from collections.abc import Iterable
from pathlib import Path
from typing import Any, Union

import ifcopenshell
import ifcopenshell.util.unit
import numpy as np
import pystache

import bonsai.tool as tool
from bonsai.bim.module.structural.load_decoration_data import ShaderInfo, box_crosses_segments

# What is white in the viewport, as resultants, made near black for paper; symbols in it are left uncoloured.
NEUTRAL = "#222222"
# X, Y and Z components, as red, green and blue that read on white and on dark pages alike.
AXIS_COLORS = {(1.0, 0.0, 0.0): "#d23a3a", (0.0, 1.0, 0.0): "#2e9e44", (0.0, 0.0, 1.0): "#3b74d8"}
# A symbol's subscript in diagram labels, written F_{x1} as in the steps.
SUBSCRIPT = re.compile(r"_\{([^}]*)\}")

# How each eighth's angle is measured, as Edit Load enters it.
EIGHTH_AXES = {
    "Q1": "from +X, turning up",
    "Q2": "from +Z, turning right",
    "Q3": "from +Z, turning left",
    "Q4": "from −X, turning up",
    "Q5": "from −X, turning down",
    "Q6": "from −Z, turning left",
    "Q7": "from −Z, turning right",
    "Q8": "from +X, turning down",
}


def write_report(
    directory: Path,
    model: ifcopenshell.entity_instance,
    items: Union[set[ifcopenshell.entity_instance], None] = None,
    detailed: bool = False,
) -> Path:
    """Write the calculation report of an analysis model into a folder, returning its HTML page.

    :param items: Only report these structural items, if given.
    :param detailed: Show more of how equations resolve, in grey, to learn from.
    """
    directory.mkdir(parents=True, exist_ok=True)
    data = get_report_data(model, items, directory, detailed)
    for template, name in (("report.html.mustache", "index.html"), ("report.md.mustache", "report.md")):
        source = tool.Blender.get_data_dir_path(Path("calcs") / template).read_text(encoding="utf-8")
        (directory / name).write_text(pystache.render(source, data), encoding="utf-8")
    shutil.copytree(tool.Blender.get_data_dir_path(Path("calcs") / "katex"), directory / "katex", dirs_exist_ok=True)
    return directory / "index.html"


def get_report_data(
    model: ifcopenshell.entity_instance,
    items: Union[set[ifcopenshell.entity_instance], None],
    directory: Path,
    detailed: bool = False,
) -> dict[str, Any]:
    ifc_file = tool.Ifc.get()
    unit = get_force_unit_symbol()
    cases = []
    for case in [g for g in model.LoadedBy or [] if g.is_a("IfcStructuralLoadCase")]:
        points = []
        drawing = None
        for item in tool.Structural.get_point_items(case):
            if items is not None and item not in items:
                continue
            activities = [a for a in tool.Structural.get_chain_activities(item, case) if is_point_force(a)]
            if not activities:
                continue
            if drawing is None:
                drawing = ShaderInfo(case)
                drawing.update()
            name = f"{get_slug(case.Name)}_{get_slug(item.Name)}_{item.id()}.svg"
            links = tool.Structural.get_magnitude_groups(activities)
            resultant_found = bool(
                tool.Structural.get_resultant_found([tool.Structural.get_locks(a) for a in activities], links)
            )
            has_diagram = write_diagram(drawing, item, directory / "diagrams" / name, resultant_found)
            point = {"name": item.Name or "Unnamed", "diagram": f"diagrams/{name}" if has_diagram else None}
            colors = get_force_colors(drawing, item)
            tilt = tool.Structural.get_axes_tilt(item)
            axis_colors = get_axis_colors(len(activities), tilt)
            slope = tool.Structural.get_axes_slope(item)
            svg_colors = {activity: get_svg_color(color) for activity, color in colors.items()}
            eighth = tool.Structural.get_resultant_eighth(item, case)
            point.update(
                get_resultant_calculation(activities, unit, svg_colors, detailed, tilt, axis_colors, slope, eighth)
            )
            # Resolved along the point's tilted axes too, whatever the viewport shows.
            resolved = name.replace(".svg", "_axes.svg")
            if point["has_tilted"] and write_resolved_diagram(
                item, activities, colors, directory / "diagrams" / resolved
            ):
                point["tilted_diagram"] = f"diagrams/{resolved}"
            points.append(point)
        if points:
            moments = get_moment_calculation(case, drawing, directory, detailed)
            cases.append({"name": case.Name or "Unnamed", "points": points, "moments": moments})
    project = next(iter(ifc_file.by_type("IfcProject")), None)
    return {
        "title": f"{model.Name or 'Analysis Model'} calculations",
        "project": (project.Name if project else None) or "Unnamed",
        "model": model.Name or "Unnamed",
        "date": datetime.date.today().isoformat(),
        "force_unit": unit,
        "cases": cases,
        "has_cases": bool(cases),
        "detailed": detailed,
    }


def get_moment_calculation(
    case: ifcopenshell.entity_instance,
    drawing: Union[ShaderInfo, None],
    directory: Path,
    detailed: bool = False,
) -> Union[dict[str, Any], None]:
    """The moments of a load case's point forces about the point chosen as its moment centre, A, if one is.

    Each force's moment is found as its magnitude times its moment arm, then by Varignon's theorem from its
    components and their distances from A, and they are added. Moments are counter-clockwise positive as the
    X-Z plane is seen from -Y; moments applied as loads are left out, as the viewport leaves them out.
    """
    centre = tool.Structural.get_moment_centre(case)
    if not centre or not (centre_obj := tool.Ifc.get_object(centre)) or centre_obj.type != "MESH":
        return None
    if drawing is None:
        drawing = ShaderInfo(case)
        drawing.update()
    length_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
    location = lambda obj: np.array(obj.matrix_world @ obj.data.vertices[0].co, dtype=float) / length_scale
    at = location(centre_obj)
    unit, length_unit = drawing.moment_unit, drawing.length_unit
    text_unit = r"\ \text{" + re.sub(r"([#$%&_{}])", r"\\\1", unit) + "}"
    length_text = r"\ \text{" + re.sub(r"([#$%&_{}])", r"\\\1", length_unit) + "}"
    rows, steps, palette, values, unknowns = [], [], [], [], []
    place_kind, place_activity = tool.Structural.get_moment_centre_unknown(case)
    for item in tool.Structural.get_point_items(case):
        if not (obj := tool.Ifc.get_object(item)) or obj.type != "MESH" or not obj.data.vertices:
            continue
        colors = get_force_colors(drawing, item)
        for activity in [a for a in tool.Structural.get_chain_activities(item, case) if is_point_force(a)]:
            x, _, z = get_force_terms(activity, 1)["vector"]
            if not (x or z):
                continue
            i = len(values) + 1
            point = location(obj)
            moment, arm, _ = tool.Structural.get_moment(at, point, np.array((x, 0.0, z)))
            dx, dz = point[0] - at[0], point[2] - at[2]
            color = get_svg_color(colors.get(activity.id(), (1, 1, 1, 2)))
            palette.append(color)
            values.append(moment)
            row = get_table_row(f"F_{{{i}}}", activity.AppliedLoad.Name or "Unnamed", math.hypot(x, z), "", [], color)
            row |= {
                "at": item.Name or "Unnamed",
                "dx": f"{dx:.2f}",
                "dz": f"{dz:.2f}",
                "arm": f"{arm:.2f}",
                "moment": f"{moment:+.2f} {unit}",  # Counter-clockwise positive, as the steps are.
            }
            row["magnitude"] += f" {drawing.force_unit}"
            locks = tool.Structural.get_locks(activity)
            if not locks[0]:
                row["magnitude"] += " 🔓"  # Found, to make the moment kept.
            if place_kind in ("POINT_X", "POINT_Z") and activity == place_activity:
                row["dx" if place_kind == "POINT_X" else "dz"] += " 🔓"  # Where it acts, found for the moment kept.
            unknowns.append((i, locks, math.hypot(x, z), arm, math.hypot(dx, dz), activity, x, z, dz, dx))
            rows.append(row)
            steps += get_arm_steps(i, dx, dz, x, z, arm, length_text, point, at)
            sign = "-" if moment < 0 else ""
            steps.append(
                f"M_{{{i}}} = {sign}F_{{{i}}}\\, d_{{{i}}} = {sign}({math.hypot(x, z):.2f})({arm:.2f}{length_text})"
                f" = {moment:.2f}{text_unit}"
            )
            # By Varignon's theorem: each component times its distance from A, turning the way it does.
            steps.append(
                f"M_{{{i}}} = F_{{z{i}}}\\, \\Delta x_{{{i}}} - F_{{x{i}}}\\, \\Delta z_{{{i}}} = ({z:.2f})({dx:.2f})"
                f" - ({x:.2f})({dz:.2f}) = {moment:.2f}{text_unit}"
            )
    if not values:
        return None
    total = sum(values)
    symbol = "\\Sigma M_A" if len(values) > 1 else "M_A"
    if len(values) > 1:
        terms = " + ".join(f"M_{{{i}}}" for i in range(1, len(values) + 1))
        numbers = " + ".join(f"({v:.2f})" for v in values)
        steps.append(f"{symbol} = {terms} = {numbers} = {bold(f'{total:.2f}', True, text_unit)}")
    else:
        steps.append(f"{symbol} = M_{{1}} = {bold(f'{total:.2f}', True, text_unit)}")
    steps += get_kept_moment_steps(case, values, unknowns, text_unit, drawing.force_unit)
    name = f"{get_slug(case.Name)}_moments_{centre.id()}.svg"
    has_diagram = write_diagram(drawing, centre, directory / "diagrams" / name, key=f"{centre_obj.name} moments")
    return {
        "centre": centre.Name or "Unnamed",
        "diagram": f"diagrams/{name}" if has_diagram else None,
        "forces": rows,
        "steps": [
            {
                "latex": get_colored_symbols(
                    f"{{\\color{{#8c8c8c}}\\qquad {step}}}" if isinstance(step, Detail) else step, palette
                ),
                "detail": isinstance(step, Detail),
                "lead": isinstance(step, Lead),
            }
            for step in steps
            if detailed or not isinstance(step, Detail)
        ],
        "summary": f"{'ΣM' if len(values) > 1 else 'M'} about A = {total:+.2f} {unit}, counter-clockwise positive.",
        "unit": unit,
        "length_unit": length_unit,
    }


def get_kept_moment_steps(
    case: ifcopenshell.entity_instance,
    values: list[float],
    unknowns: list[tuple],  # Each force's number, locks, magnitude, arm, r, applied load, X, Z and Δz.
    text_unit: str,
    force_unit: str,
) -> list[str]:
    """How the one unknown was found, when a load case keeps a sum of moments: the moment it must make, then its
    magnitude from its arm, or its direction from where it acts.

    :param unknowns: Each force's number, locks, magnitude, moment arm, distance r from A and applied load.
    """
    kept = tool.Structural.get_resultant_moment(case)
    kind, activity = tool.Structural.get_moment_centre_unknown(case)
    if kept is not None and kind:
        return get_kept_centre_steps(kind, activity, kept, values, unknowns, text_unit)
    found = [entry for entry in unknowns if not all(entry[1])]
    if kept is None or not found:
        return []
    i, locks, magnitude, arm, r, *_ = found[0]
    moment = values[i - 1]
    rest = sum(values) - moment
    force_text = r"\ \text{" + re.sub(r"([#$%&_{}])", r"\\\1", force_unit) + "}"
    steps = [
        f"\\text{{Kept: }} \\Sigma M_A = {kept:.2f}{text_unit}",
        f"M_{{{i}}} = \\Sigma M_A - \\textstyle\\sum_{{others}} M = ({kept:.2f}) - ({rest:.2f}) = {moment:.2f}{text_unit}",
    ]
    if not locks[0] and arm:
        value = bold(f"{magnitude:.2f}", True, force_text)
        steps.append(
            f"F_{{{i}}} = \\frac{{|M_{{{i}}}|}}{{d_{{{i}}}}} = \\frac{{{abs(moment):.2f}}}{{{arm:.2f}}} = {value}"
        )
    elif not locks[1] and magnitude and r:
        sine = min(abs(moment) / (magnitude * r), 1.0)
        steps.append(
            f"\\sin \\phi_{{{i}}} = \\frac{{|M_{{{i}}}|}}{{F_{{{i}}}\\, r_{{{i}}}}} = "
            f"\\frac{{{abs(moment):.2f}}}{{({magnitude:.2f})({r:.2f})}} = {sine:.4f}"
        )
        angle = f"{math.degrees(math.asin(sine)):.1f}" + "^\\circ"
        steps.append(f"\\phi_{{{i}}} = {bold(angle)}")
    return steps


def get_kept_centre_steps(
    kind: str,
    activity: ifcopenshell.entity_instance,
    kept: float,
    values: list[float],
    unknowns: list[tuple],  # Each force's number, locks, magnitude, arm, r, applied load, X, Z and Δz.
    text_unit: str,
) -> list[str]:
    """How a place was found when a load case keeps a sum of moments and a place is its unknown. A force's point
    along X: from the moment it must make, as A and the other forces stay. A's place: with one force, its arm, r or
    angle from its moment; with several, it follows from them all, as moving A changes each"""
    entry = next((e for e in unknowns if e[5] == activity), None)
    if not entry:
        return []
    i, _, magnitude, arm, r, _, x, z, dz, dx = entry
    if kind in ("POINT_REACH", "POINT_SWING"):
        how = "along the line from A" if kind == "POINT_REACH" else "round A, its distance kept"
        return [
            f"\\text{{Kept: }} \\Sigma M_A = {kept:.2f}{text_unit}",
            f"\\text{{The point of }} F_{{{i}}} \\text{{ is placed for it, {how}}}",
        ]
    if kind in ("POINT_X", "POINT_Z") and (z if kind == "POINT_X" else x):
        moment = values[i - 1]
        length_text = r"\ \text{" + text_unit.rpartition(".")[2].rstrip("}") + "}"
        steps = [
            f"\\text{{Kept: }} \\Sigma M_A = {kept:.2f}{text_unit}",
            f"\\text{{The point of }} F_{{{i}}} \\text{{ is placed for it, along {kind[-1]}}}",
            f"M_{{{i}}} = \\Sigma M_A - \\textstyle\\sum_{{others}} M = ({kept:.2f}) - ({sum(values) - moment:.2f})"
            f" = {moment:.2f}{text_unit}",
        ]
        # From its moment, F_z dx - F_x dz, the distance along the way it moves.
        if kind == "POINT_X":
            found = bold(f"{(moment + x * dz) / z:.2f}", True, length_text)
            steps.append(
                f"\\Delta x_{{{i}}} = \\frac{{M_{{{i}}} + F_{{x{i}}}\\, \\Delta z_{{{i}}}}}{{F_{{z{i}}}}} = "
                f"\\frac{{({moment:.2f}) + ({x:.2f})({dz:.2f})}}{{{z:.2f}}} = {found}"
            )
        else:
            found = bold(f"{(z * dx - moment) / x:.2f}", True, length_text)
            steps.append(
                f"\\Delta z_{{{i}}} = \\frac{{F_{{z{i}}}\\, \\Delta x_{{{i}}} - M_{{{i}}}}}{{F_{{x{i}}}}} = "
                f"\\frac{{({z:.2f})({dx:.2f}) - ({moment:.2f})}}{{{x:.2f}}} = {found}"
            )
        return steps
    # Words set as text, not as letters of the maths around them.
    words = {
        "ARM": f"\\text{{moment arm }} d_{{{i}}}",
        "REACH": f"\\text{{distance }} r_{{{i}}}",
        "SWING": f"\\text{{angle }} \\phi_{{{i}}}",
    }
    steps = [
        f"\\text{{Kept: }} \\Sigma M_A = {kept:.2f}{text_unit}",
        f"\\text{{A is placed for it, its }} {words[kind]} \\text{{ found}}",
    ]
    if len(values) != 1 or not magnitude:
        return steps  # Moving A changes every force's moment, so its place follows from them all at once.
    length_text = text_unit.rpartition(".")[2].rstrip("}")
    length_text = r"\ \text{" + length_text + "}"
    if kind == "ARM":
        value = bold(f"{abs(kept) / magnitude:.2f}", True, length_text)
        steps.append(
            f"d_{{{i}}} = \\frac{{|M_A|}}{{F_{{{i}}}}} = \\frac{{{abs(kept):.2f}}}{{{magnitude:.2f}}} = {value}"
        )
    elif kind == "REACH" and r and arm:
        sine = arm / r
        value = bold(f"{abs(kept) / (magnitude * sine):.2f}", True, length_text)
        steps.append(
            f"r_{{{i}}} = \\frac{{|M_A|}}{{F_{{{i}}} \\sin \\phi_{{{i}}}}} = "
            f"\\frac{{{abs(kept):.2f}}}{{({magnitude:.2f})({sine:.4f})}} = {value}"
        )
    elif kind == "SWING" and r:
        sine = min(abs(kept) / (magnitude * r), 1.0)
        steps.append(
            f"\\sin \\phi_{{{i}}} = \\frac{{|M_A|}}{{F_{{{i}}}\\, r_{{{i}}}}} = "
            f"\\frac{{{abs(kept):.2f}}}{{({magnitude:.2f})({r:.2f})}} = {sine:.4f}"
        )
        angle = f"{math.degrees(math.asin(sine)):.1f}" + "^\\circ"
        steps.append(f"\\phi_{{{i}}} = {bold(angle)}")
    return steps


def get_arm_steps(
    i: int,
    dx: float,
    dz: float,
    x: float,
    z: float,
    arm: float,
    length_text: str,
    point: Union[np.ndarray, None] = None,
    at: Union[np.ndarray, None] = None,
) -> list[str]:
    """How a force's moment arm is found, as a text finds it from the figure: r from A to the force's point, the
    angle phi between r and the force's line of action, d = r sin phi, the distance square to that line, and s =
    r cos phi, along it from the force's point to the arm's foot, the right triangle's sides checked.

    :param point: Where the force acts and where A is, to show in detail where r's run and rise come from.
    """
    r = math.hypot(dx, dz)
    if r < 1e-9:
        return [f"r_{{{i}}} = 0:\\ F_{{{i}}} \\text{{ acts at A, so }} d_{{{i}}} = 0"]
    along_r = math.degrees(math.atan2(dz, dx)) % 360
    along_force = math.degrees(math.atan2(z, x)) % 360
    between = abs(along_force - along_r)
    phi = min(between % 180, 180 - between % 180)  # The acute angle between the two lines.
    steps = []
    if point is not None and at is not None:
        # From A to the force's point, as the table's distances run.
        for axis, k, delta in (("x", 0, dx), ("z", 2, dz)):
            step = f"\\Delta {axis}_{{{i}}} = {axis}_{{F{i}}} - {axis}_{{A}} = ({point[k]:.2f}) - ({at[k]:.2f}) = {delta:.2f}"
            steps.append(Lead(step) if axis == "x" else Detail(step))
    s = r * math.cos(math.radians(phi))
    steps += [
        f"r_{{{i}}} = \\sqrt{{\\Delta x_{{{i}}}^2 + \\Delta z_{{{i}}}^2}} = \\sqrt{{({dx:.2f})^2 + ({dz:.2f})^2}}"
        f" = {r:.2f}{length_text}",
        Detail(
            f"\\text{{From }} +X\\text{{: }} r_{{{i}}} \\text{{ at }} {along_r:.1f}^\\circ,\\ "
            f"F_{{{i}}} \\text{{ at }} {along_force:.1f}^\\circ"
        ),
        Detail(
            f"|{along_force:.1f}^\\circ - {along_r:.1f}^\\circ| = {between:.1f}^\\circ"
            f"\\text{{, the lines' acute angle }} {phi:.1f}^\\circ"
        ),
        f"\\phi_{{{i}}} = {phi:.1f}^\\circ \\text{{ between }} r_{{{i}}} \\text{{ and }} F_{{{i}}}\\text{{'s line of action}}",
        f"d_{{{i}}} = r_{{{i}}} \\sin \\phi_{{{i}}} = ({r:.2f}) \\sin {phi:.1f}^\\circ = {arm:.2f}{length_text}",
        # The third side, along the line of action, and the sides checked, as the diagram labels them.
        Lead(f"s_{{{i}}} = r_{{{i}}} \\cos \\phi_{{{i}}} = ({r:.2f}) \\cos {phi:.1f}^\\circ = {s:.2f}{length_text}"),
        Detail(
            f"s_{{{i}}}^2 + d_{{{i}}}^2 = ({s:.2f})^2 + ({arm:.2f})^2 = {s * s + arm * arm:.2f} = "
            f"({r:.2f})^2 = r_{{{i}}}^2"
        ),
    ]
    return steps


def get_force_colors(drawing: ShaderInfo, item: ifcopenshell.entity_instance) -> dict[int, tuple]:
    """The colour each activity's force is drawn in at an item, as in the viewport"""
    if not (obj := tool.Ifc.get_object(item)):
        return {}
    return {
        text["force_of"]: text["color"]
        for text in drawing.text_info
        if text.get("object") == obj.name and text.get("force_of")
    }


def write_resolved_diagram(
    item: ifcopenshell.entity_instance,
    activities: list[ifcopenshell.entity_instance],
    colors: dict[int, tuple],
    path: Path,
) -> bool:
    """Write a diagram of each force at a point resolved along its tilted axes, as the steps resolve them"""
    if not (obj := tool.Ifc.get_object(item)):
        return False
    drawing = ShaderInfo()
    drawing.get_force_units()
    forces = [np.array(get_force_terms(activity, i)["vector"]) for i, activity in enumerate(activities, 1)]
    drawing.draw_resolved_point_forces(
        obj.name,
        forces,
        tool.Structural.get_axes_rotation(item),
        [colors.get(activity.id(), (1, 1, 1, 2)) for activity in activities],
        [activity.id() for activity in activities],
        tool.Structural.get_axes_slope(item),
    )
    return write_diagram(drawing, item, path)


def is_point_force(activity: ifcopenshell.entity_instance) -> bool:
    return bool(activity.AppliedLoad and activity.AppliedLoad.is_a("IfcStructuralLoadSingleForce"))


def get_force_unit_symbol() -> str:
    unit = ifcopenshell.util.unit.get_project_unit(tool.Ifc.get(), "FORCEUNIT")
    return ifcopenshell.util.unit.get_unit_symbol(unit) if unit else "N"


def get_slug(name: Union[str, None]) -> str:
    return re.sub(r"[^\w.-]+", "_", name or "").strip("_") or "Unnamed"


def bold(text: str, is_bold: bool = True, suffix: str = "") -> str:
    """A value in bold in LaTeX, for one found by solving, with its suffix, as a unit, bold too"""
    if not is_bold:
        return text + suffix
    return f"\\mathbf{{{text}}}" + suffix.replace("\\text{", "\\textbf{")


class Detail(str):
    """A step shown only in detailed reports: the working between the main steps"""


class Lead(Detail):
    """A detailed step that starts a new piece of working, so is set apart from the working before it"""


def get_resultant_calculation(
    activities: list[ifcopenshell.entity_instance],
    unit: str,
    colors: Union[dict[int, str], None] = None,
    detailed: bool = False,
    tilt: Union[float, None] = 0.0,
    axis_colors: Union[dict[str, str], None] = None,
    slope: Union[tuple[float, float], None] = None,
    resultant_eighth: Union[str, None] = None,
) -> dict[str, Any]:
    """The steps for concurrent point forces and their resultant.

    :param tilt: Degrees the point's own axes are tilted by in the X-Z plane: if any, forces are also resolved
        along them, as along an incline.
    :param resultant_eighth: The eighth chosen to measure the resultant's angle in, as Edit Resultant keeps it.

    If some force values were unknown (unlocked) and found by Edit Resultant, the steps find them first, as
    the problem was posed, then add the forces up as a check. Edit Resultant solves two unknowns, so the
    number unlocked tells what was known of the resultant: with one, its direction; with two, all of it.
    """
    text_unit = r"\ \text{" + re.sub(r"([#$%&_{}])", r"\\\1", unit) + "}"
    forces = [get_force_terms(activity, i) for i, activity in enumerate(activities, 1)]
    for force, link, factor in zip(forces, *tool.Structural.get_magnitude_links(activities)):
        force["link"], force["factor"] = link, factor
    # Each force in the colour of its arrow. Markdown keeps colour only in math, so symbols are coloured there.
    palette = [(colors or {}).get(activity.id(), NEUTRAL) for activity in activities]
    sources = get_link_sources(forces)
    rows = []
    for i, (force, color) in enumerate(zip(forces, palette)):
        found = [text for text, locked in zip(("magnitude", "direction"), force["locks"]) if not locked]
        if force.get("given") and "magnitude" not in found:
            found.insert(0, "magnitude")  # Found from its known component.
        if i in sources and "magnitude" in found:
            # Tied to another's, as "magnitude = 0.25 × F₂", so that it does not read as free.
            source, k = sources[i]
            symbol = re.sub(r"_\{(\d+)\}", lambda m: m.group(1).translate(SUBSCRIPTS), forces[source]["symbol"])
            found[found.index("magnitude")] = (
                f"magnitude = {symbol}" if math.isclose(k, 1.0) else f"magnitude = {k:g} × {symbol}"
            )
        rows.append(get_table_row(force["symbol"], force["name"], force["magnitude"], force["direction"], found, color))
        rows[-1]["magnitude"] += f" {unit}"
    solving, find = get_solving_steps(forces, text_unit, resultant_eighth)
    # Components first, then the unknowns found from them, then the resultant with what was found.
    found = {
        i: "MAGNITUDE" if force["locks"][1] else "WHOLE"
        for i, force in enumerate(forces)
        if not all(force["locks"]) or force.get("given")
    }
    resultant_found = tool.Structural.get_resultant_found(
        [force["locks"] for force in forces], [force["link"] for force in forces]
    )
    components, steps, summary = get_sum_steps(
        forces, text_unit, unit, found if solving else None, resultant_found, resultant_eighth
    )
    # The resultant too. What of it was found follows from how many force values were: two unknowns in all.
    total = [sum(force["vector"][k] for force in forces) for k in range(3)]
    # Rounding noise across an axis would put a resultant along it into the neighbouring eighth.
    total = [c if abs(c) > 1e-9 * max(map(abs, total), default=0) else 0.0 for c in total]
    magnitude = math.sqrt(sum(c * c for c in total))
    direction = "components given"
    if magnitude <= 1e-9:
        direction = "none: the forces are in equilibrium"
    elif not total[1]:
        eighth, angle = get_resultant_direction(total[0], total[2], resultant_eighth)
        direction = f"{angle:.1f}° {eighth}, {EIGHTH_AXES[eighth]}"
    found = resultant_found
    rows.append(get_table_row("R", "Resultant", magnitude, direction, found, NEUTRAL))
    rows[-1]["magnitude"] += f" {unit}"
    # Detailed steps in grey, applied in LaTeX so that both formats show it; force symbols keep their colours.
    gray = lambda step: f"{{\\color{{#8c8c8c}}\\qquad {step}}}" if isinstance(step, Detail) else step  # Indented.
    render = lambda steps, colors=axis_colors, resolved=len(forces) == 1: [
        {
            "latex": get_colored_symbols(gray(step), palette, colors, resolved),
            "detail": isinstance(step, Detail),
            "lead": isinstance(step, Lead),
        }
        for step in steps
        if detailed or not isinstance(step, Detail)
    ]
    tilted = get_tilted_steps(forces, tilt, text_unit, slope) if tilt else []
    return {
        "forces": rows,
        "find": get_colored_symbols(find, palette),  # With inline math, $F_{2}$, as both formats read.
        "solving": render(solving),
        "has_solving": bool(solving),
        "components": render(components),
        "steps": render(steps),
        "summary": summary,
        # Its diagram draws each force's components along x' and z', so they take their axes' colours.
        "tilted": render(tilted, {"x'": AXIS_COLORS[(1.0, 0.0, 0.0)], "z'": AXIS_COLORS[(0.0, 0.0, 1.0)]}, True),
        "has_tilted": bool(tilted),
        "tilt_note": (
            (f"x′ runs along a {slope[0]:g}:{slope[1]:g} slope, " if slope else "x′ is ")
            + f"tilted {tilt:.1f}° from +X towards +Z, with z′ square to it."
            if tilted
            else ""
        ),
        # A push added to other forces is drawn, and added, as a pull along its line.
        "push_note": (
            "By the principle of transmissibility, a push is added as a pull along its line of action."
            if len(forces) > 1 and any(force.get("push") for force in forces)
            else ""
        ),
    }


def get_tilted_steps(
    forces: list[dict[str, Any]],
    tilt: float,
    text_unit: str,
    slope: Union[tuple[float, float], None] = None,
) -> list[str]:
    """Each force resolved along a point's tilted axes x' and z' as a textbook does, then their sums.

    A component uses the smaller of the two angles the force's line makes with the axes, as P sin θ and
    P cos θ, and the ratios of the slope's sides when that angle is the slope's own. Its sign is told in
    words: up or down the slope, away from or into the surface.

    :param slope: The rise and run the axes were tilted by, if they were.
    """
    steps: list[str] = [Detail("\\text{Each component uses the smaller angle the force's line makes with the axes}")]
    x_axis = (math.cos(math.radians(tilt)), math.sin(math.radians(tilt)))
    z_axis = (-x_axis[1], x_axis[0])
    # x' points up a slope rising to the right, and down one falling to the right.
    heading = tilt % 360
    x_words = ("along +x'", "along -x'")
    if 0 < heading < 90:
        x_words = ("up the slope", "down the slope")
    elif 270 < heading < 360:
        x_words = ("down the slope", "up the slope")
    words = {
        "x'": x_words,
        "z'": ("away from the surface", "into the surface")
        if -90 < (tilt + 180) % 360 - 180 < 90
        else ("along +z'", "along -z'"),
    }
    slope_angle = math.degrees(math.atan2(*slope)) if slope else None
    totals = {"x'": [], "z'": []}
    for i, force in enumerate(forces, 1):
        if not force["in_plane"]:
            continue
        x, _, z = force["vector"]
        magnitude, direction = math.hypot(x, z), math.degrees(math.atan2(z, x)) % 360
        between = abs((direction - tilt + 180) % 360 - 180)  # Between the force and x', 0 to 180.
        with_x = min(between, 180 - between)  # Between their lines.
        with_z = 90 - with_x
        steps.append(Lead(f"{force['symbol']} \\text{{ acts at }} {direction:.1f}^\\circ \\text{{ from }} +X"))
        steps.append(
            Detail(
                f"\\text{{Its line makes }} {with_x:.1f}^\\circ \\text{{ with }} x' \\text{{ and }} {with_z:.1f}^\\circ \\text{{ with }} z'"
            )
        )
        angle = min(with_x, with_z)
        # cos of the angle with its own axis, sin of the angle with the other.
        functions = {"x'": "\\cos" if with_x <= with_z else "\\sin", "z'": "\\sin" if with_x <= with_z else "\\cos"}
        by_slope = slope is not None and math.isclose(angle, abs(slope_angle), abs_tol=1e-6)
        for name, axis in (("x'", x_axis), ("z'", z_axis)):
            value = x * axis[0] + z * axis[1]
            if by_slope:
                rise, run = abs(slope[0]), abs(slope[1])
                side = rise if functions[name] == "\\sin" else run
                term = f"\\left(\\frac{{{side:g}}}{{{get_slope_hypotenuse(rise, run)}}}\\right)"
            else:
                term = f"{functions[name]} {angle:.1f}^\\circ"
            sign = "-" if value < -1e-9 else ""
            part = abs(value) / magnitude
            steps.append(
                f"F_{{{name}{i}}} = {sign}F_{{{i}}} {term} = {sign}({magnitude:.2f}) {term} = {value:.2f}{text_unit}"
            )
            steps.append(Detail(f"{term} = {part:.4f}"))
            steps.append(Detail(f"{sign}({magnitude:.2f})({part:.4f}) = {value:.2f}"))
            if abs(value) < 0.005:
                steps.append(Detail(f"\\text{{Zero: it lies square to }} {name}"))
            else:
                steps.append(
                    Detail(f"\\text{{{'Negative' if sign else 'Positive'}: it points {words[name][bool(sign)]}}}")
                )
            totals[name].append((i, value))
    for name, values in totals.items():
        if len(values) > 1:
            symbols = " + ".join(f"F_{{{name}{i}}}" for i, _ in values)
            numbers = " + ".join(f"({v:.2f})" if v < 0 else f"{v:.2f}" for _, v in values)
            total = sum(v for _, v in values)
            steps.append(f"R_{{{name}}} = \\Sigma F_{{{name}}} = {symbols} = {numbers} = {total:.2f}{text_unit}")
    return steps


def get_table_row(
    symbol: str, name: str, magnitude: float, direction: str, found: list[str], color: str
) -> dict[str, str]:
    return {
        "color": color,
        "symbol": symbol,
        "colored_symbol": f"{{\\color{{{color}}}{symbol}}}" if color != NEUTRAL else symbol,
        "name": name,
        "magnitude": f"{magnitude:.2f}",
        "direction": direction,
        "found": ", ".join(found),
        # Values found by solving are set in bold.
        "magnitude_found": "magnitude" in found,
        "direction_found": "direction" in found,
    }


def get_axis_colors(count: int, tilt: Union[float, None]) -> dict[str, str]:
    """The colours of the components the diagram draws, by the axis of their symbols, if it draws any.

    A single force is drawn with its components; several forces show their resultant's components only
    when components are shown. With tilted axes in the local frame, they lie along x' and z'.
    """
    props = tool.Structural.get_structural_props()
    if not ((count == 1 and props.force_display != "RESULTANT") or props.force_display in ("COMPONENTS", "BOTH")):
        return {}
    prime = "'" if props.reference_frame == "LOCAL_COORDS" and tilt else ""
    return {f"x{prime}": get_svg_color((1, 0, 0, 1)), f"z{prime}": get_svg_color((0, 0, 1, 1))}


def get_colored_symbols(
    step: str,
    palette: list[str],
    axis_colors: Union[dict[str, str], None] = None,
    color_force_components: bool = False,
) -> str:
    """Colour symbols in a step as the diagram colours what they stand for.

    A force's symbols, F_{2}, F_{x2} and \\theta_{2}, take its arrow's colour. Components the diagram draws
    take their axis colours instead: the resultant's, R_x, and a force's, F_{x1}, if it is drawn resolved.
    """
    axis_colors = axis_colors or {}

    def colored(match: re.Match) -> str:
        symbol = match[0]
        if match[2]:  # A force's symbol.
            axis, i = match[1], int(match[2]) - 1
            if axis and color_force_components and axis in axis_colors:
                color = axis_colors[axis]
            elif 0 <= i < len(palette):
                color = palette[i]
            else:
                return symbol
        elif match[5]:  # A force's angle.
            i = int(match[5]) - 1
            if not 0 <= i < len(palette):
                return symbol
            color = palette[i]
        elif (axis := match[3] or match[4]) in axis_colors:  # A component of the resultant.
            color = axis_colors[axis]
        else:
            return symbol
        if color == NEUTRAL:
            return symbol  # Left to the page's own text colour, which reads on dark themes too.
        return f"{{\\color{{{color}}}{symbol}}}"

    return re.sub(r"F_\{([xyz]'?)?(\d+)\}|R_(?:\{([xyz]'?)\}|([xyz])(?![A-Za-z]))|\\theta_\{(\d+)\}", colored, step)


def get_force_terms(activity: ifcopenshell.entity_instance, i: int) -> dict[str, Any]:
    """A force's values, and how its components are written from its magnitude and angle"""
    load = activity.AppliedLoad
    x, y, z = (getattr(load, a) or 0.0 for a in ("ForceX", "ForceY", "ForceZ"))
    force = {
        "symbol": f"F_{{{i}}}",
        "name": load.Name or "Unnamed",
        "vector": (x, y, z),
        "magnitude": math.sqrt(x * x + y * y + z * z),
        "locks": tool.Structural.get_locks(activity),
        "in_plane": not y and bool(x or z),
        "direction": "components given",
    }
    if force["in_plane"]:
        named = re.search(r" (Q[1-8])$", load.Name or "")
        eighth, angle, _, _ = tool.Structural.get_eighth(x, z, named[1] if named else None)
        force["direction"] = f"{angle:.1f}° {eighth}, {EIGHTH_AXES[eighth]}"
        force["terms"] = get_component_terms(x, z, eighth, angle)
        # Entered as a slope, its components follow by similar triangles, as ratios of the slope's sides.
        if (slope := get_named_slope(load.Name or "", x, z)) is not None:
            rise, run = slope
            force["slope"] = slope
            force["direction"] = f"{rise:g}:{run:g} slope, {force['direction']}"
            force["terms"] = get_slope_terms(x, z, rise, run)
        # Entered against the point's own axes, as a primed eighth in its name records, it is described so; its
        # components are still added along X and Z.
        primed = re.search(r"(?: at (-?[\d.]+):(-?[\d.]+))? (Q[1-8])′$", load.Name or "")
        connects = activity.AssignedToStructuralItem
        if primed and connects and (tilt := tool.Structural.get_axes_tilt(connects[0].RelatingElement)):
            local, local_angle, _, _ = tool.Structural.get_eighth(*tool.Structural.to_axes(x, z, tilt), primed[3])
            words = EIGHTH_AXES[local].replace("X", "x′").replace("Z", "z′")
            force["direction"] = f"{local_angle:.1f}° {local}′, {words}"
            if primed[1]:
                force["direction"] = f"{float(primed[1]):g}:{float(primed[2]):g} slope, {force['direction']}"
    force["given"] = tool.Structural.get_known_component(activity) if force["in_plane"] else None
    if tool.Structural.get_push(activity):
        force["push"] = True
        force["direction"] += ", push"
    return force


def get_named_slope(name: str, x: float, z: float) -> Union[tuple[float, float], None]:
    """The rise and run a generated load name records, if they are the slope of the components x and z"""
    if not (match := re.search(r" at (-?[\d.]+):(-?[\d.]+)(?: \S+)?$", name)):
        return None
    rise, run = abs(float(match[1])), abs(float(match[2]))
    if not (rise or run) or not math.isclose(abs(x) * rise, abs(z) * run, rel_tol=1e-6, abs_tol=1e-9):
        return None
    return rise, run


def get_slope_hypotenuse(rise: float, run: float) -> str:
    """The slope triangle's hypotenuse, as a number if it is a whole one, as 5 for 3:4, else as a root"""
    hypotenuse = math.hypot(rise, run)
    if math.isclose(hypotenuse, round(hypotenuse), abs_tol=1e-9):
        return f"{round(hypotenuse)}"
    return f"\\sqrt{{{rise * rise + run * run:g}}}"


def get_slope_terms(x: float, z: float, rise: float, run: float) -> dict[str, str]:
    """The ratios of the X and Z components of a slope to its force, with signs, as -\\left(\\frac{4}{5}\\right)"""
    hypotenuse = get_slope_hypotenuse(rise, run)
    return {
        "x": f"{'-' if x < 0 else ''}\\left(\\frac{{{run:g}}}{{{hypotenuse}}}\\right)",
        "z": f"{'-' if z < 0 else ''}\\left(\\frac{{{rise:g}}}{{{hypotenuse}}}\\right)",
    }


def get_component_terms(x: float, z: float, eighth: str, angle: float) -> dict[str, str]:
    """The trigonometry of the X and Z components of a direction, with signs, as -\\sin 40.0^\\circ"""
    # Measured from a horizontal axis, X takes the cosine; from a vertical one, the sine.
    trig_x, trig_z = (r"\cos", r"\sin") if eighth in ("Q1", "Q4", "Q5", "Q8") else (r"\sin", r"\cos")
    return {
        "x": f"{'-' if x < 0 else ''}{trig_x} {angle:.1f}^\\circ",
        "z": f"{'-' if z < 0 else ''}{trig_z} {angle:.1f}^\\circ",
    }


def get_resultant_direction(x: float, z: float, chosen: Union[str, None] = None) -> tuple[str, float]:
    """The eighth a resultant's angle is measured in, and the angle: the one chosen for it, as 60 degrees from -X
    rather than 30 from +Z, else the eighth it falls in"""
    if chosen and (angle := tool.Structural.get_angle_from_eighth(x, z, chosen)) is not None:
        return chosen, angle
    eighth, angle, _, _ = tool.Structural.get_eighth(x, z)
    return eighth, angle


def get_sum_steps(
    forces: list[dict[str, Any]],
    text_unit: str,
    unit: str,
    found: Union[dict[int, str], None] = None,
    resultant_found: tuple[str, ...] = (),
    resultant_eighth: Union[str, None] = None,
) -> tuple[list[str], list[str], str]:
    """Each force's components, then their sums, and the resultant's magnitude and angle.

    :param found: Forces whose values are found by solving, by index: MAGNITUDE if only that, else WHOLE.
        Their components come with the resultant, once found; before solving, an unknown magnitude's are
        written with its symbol, and an unknown force's not at all.
    :param resultant_eighth: The eighth chosen to measure the resultant's angle in, if any.
    :return: The component steps, the resultant steps, and the result in words.
    """
    number = lambda value: f"{value:.2f}" if value >= 0 else f"({value:.2f})"
    found = found or {}
    components, steps = [], []
    for i, force in enumerate(forces, 1):
        x, y, z = force["vector"]
        if force["in_plane"]:
            if slope := force.get("slope"):
                # The slope triangle's sides, the hypotenuse found first.
                rise, run = slope
                hypotenuse = get_slope_hypotenuse(rise, run)
                value = f"{hypotenuse} = {math.hypot(rise, run):.4f}" if "sqrt" in hypotenuse else hypotenuse
                components.append(
                    Lead(
                        f"{force['symbol']} \\text{{ rises }} {rise:g} \\text{{ in }} {run:g} \\text{{ along its slope}}"
                    )
                )
                components.append(Detail(f"\\sqrt{{{rise:g}^2 + {run:g}^2}} = {value}"))
            for axis, value in (("x", x), ("z", z)):
                term = force["terms"][axis]
                sign, trig = ("-", term[1:]) if term.startswith("-") else ("", term)
                symbolic = f"F_{{{axis}{i}}} = {sign}F_{{{i}}} {trig}"
                numeric = f"{symbolic} = {sign}({force['magnitude']:.2f}) {trig} = {value:.2f}{text_unit}"
                ratio = abs(value) / force["magnitude"]
                working = [
                    Detail(f"{trig} = {ratio:.4f}"),
                    Detail(f"{sign}({force['magnitude']:.2f})({ratio:.4f}) = {value:.2f}"),
                ]
                if i - 1 not in found:
                    components += [numeric, *working]
                else:
                    if found[i - 1] == "MAGNITUDE":
                        components.append(symbolic)
                    steps += [numeric, *working]
        else:
            for axis, value in (("x", x), ("y", y), ("z", z)):
                if value or axis != "y":
                    (steps if i - 1 in found else components).append(f"F_{{{axis}{i}}} = {value:.2f}{text_unit}")
    axes = ["x", "y", "z"] if any(force["vector"][1] for force in forces) else ["x", "z"]
    index = {"x": 0, "y": 1, "z": 2}
    totals = {axis: sum(force["vector"][index[axis]] for force in forces) for axis in axes}
    for axis in axes:
        symbols = " + ".join(f"F_{{{axis}{i}}}" for i in range(1, len(forces) + 1))
        values = " + ".join(number(force["vector"][index[axis]]) for force in forces)
        steps.append(f"R_{axis} = \\Sigma F_{axis} = {symbols} = {values} = {totals[axis]:.2f}{text_unit}")
    resultant = math.sqrt(sum(value * value for value in totals.values()))
    squares = " + ".join(f"R_{axis}^2" for axis in axes)
    values = " + ".join(f"{number(totals[axis])}^2" for axis in axes)
    added = " + ".join(f"{totals[axis] ** 2:.2f}" for axis in axes)
    steps.append(Detail(f"{squares} = {values} = {added} = {resultant**2:.2f}"))
    steps.append(
        f"R = \\sqrt{{{squares}}} = \\sqrt{{{values}}} = {bold(f'{resultant:.2f}', 'magnitude' in resultant_found, text_unit)}"
    )
    summary = f"R = {resultant:.2f} {unit}"
    if len(axes) == 2 and resultant > 1e-9:
        eighth, angle = get_resultant_direction(totals["x"], totals["z"], resultant_eighth)
        angle_text, eighth_text = f"{angle:.1f}^\\circ", f"\\ \\text{{{eighth}}}"
        # Past a quarter turn, whole quarter turns from the eighth's axis, then the rest from the axis reached.
        turns = int((angle + 1e-9) // 90)
        reached = (90 * (int(eighth[1]) // 2) + (90 if int(eighth[1]) % 2 else -90) * turns) % 360
        along, across = ("x", "z") if reached in (0, 180) else ("z", "x")
        ratio = abs(totals[across]) / abs(totals[along])
        if turns:
            steps.append(Detail(f"\\text{{Measured {EIGHTH_AXES[eighth]}}}"))  # As "from −Z, turning left".
            axis = {0: "+X", 90: "+Z", 180: "−X", 270: "−Z"}[reached]
            steps.append(Detail(f"{90 * turns}^\\circ \\text{{ turns it to }} {axis}"))
        else:
            steps.append(Detail(f"\\text{{Measured {EIGHTH_AXES[eighth].split(',')[0]}}}"))  # As "from −Z".
        theta = "\\theta" if turns else "\\theta_R"  # Past a quarter turn, the rest of the angle.
        steps.append(
            Detail(
                f"\\tan{theta} = \\frac{{|R_{across}|}}{{|R_{along}|}} = "
                f"\\frac{{{abs(totals[across]):.2f}}}{{{abs(totals[along]):.2f}}} = {ratio:.4f}"
            )
        )
        prefix = f"{90 * turns}^\\circ + " if turns else ""
        steps.append(
            f"\\theta_R = {prefix}\\tan^{{-1}}\\left(\\frac{{|R_{across}|}}{{|R_{along}|}}\\right) = "
            f"{prefix}\\tan^{{-1}}\\left(\\frac{{{abs(totals[across]):.2f}}}{{{abs(totals[along]):.2f}}}\\right) = "
            f"{bold(angle_text, 'direction' in resultant_found, eighth_text)}"
        )
        summary += f" at {angle:.1f}° {eighth}, {EIGHTH_AXES[eighth]}"
    elif resultant <= 1e-9:
        summary += ": the forces are in equilibrium"
    return components, steps, summary


def get_solving_steps(
    forces: list[dict[str, Any]], text_unit: str, resultant_eighth: Union[str, None] = None
) -> tuple[list[str], str]:
    """The steps finding what was unknown, and what they find: magnitudes from known components, then unlocked values"""
    steps, finds = [], []
    for n, force in enumerate(forces, 1):
        if not (given := force.get("given")):
            continue
        # The known component, written with the unknown magnitude, then solved for it.
        axis = given.lower()
        value = force["vector"][0 if axis == "x" else 2]
        term = force["terms"][axis]
        sign, ratio = ("-", term[1:]) if term.startswith("-") else ("", term)
        part = abs(value) / force["magnitude"]
        steps.append(f"F_{{{axis}{n}}} = {sign}F_{{{n}}} {ratio} = {value:.2f}{text_unit}")
        steps.append(Detail(f"{ratio} = {part:.4f}"))
        steps.append(Detail(f"\\text{{Divide both sides by }} {ratio}:"))
        magnitude = f"{force['magnitude']:.2f}"
        steps.append(f"F_{{{n}}} = \\frac{{{abs(value):.2f}}}{{{ratio}}} = {bold(magnitude, True, text_unit)}")
        finds.append(f"The magnitude of ${force['symbol']}$, its {axis} component and direction being known.")
    unknown_steps, unknown_find = get_unknown_steps(forces, text_unit, resultant_eighth)
    return steps + unknown_steps, " ".join(finds + ([unknown_find] if unknown_find else []))


def get_unknown_steps(
    forces: list[dict[str, Any]], text_unit: str, resultant_eighth: Union[str, None] = None
) -> tuple[list[str], str]:
    """The steps finding the unknown (unlocked) values, and what they find, or none if all were known.

    Unknown magnitudes are found from the sums along X and Z, as the book does.
    """
    unknowns = [
        (i, kind)
        for i, force in enumerate(forces)
        for kind, locked in zip(("MAGNITUDE", "DIRECTION"), force["locks"])
        if not locked
    ]
    # Forces of equal magnitude count as one unknown, written as the first of them, or follow one known.
    groups = get_link_groups(forces)
    known_links = {forces[i]["link"] for i, f in enumerate(forces) if f.get("link") and f["locks"][0]}
    unknowns = [
        (i, kind)
        for i, kind in unknowns
        if kind != "MAGNITUDE"
        or not forces[i].get("link")
        or (forces[i]["link"] not in known_links and i == groups[forces[i]["link"]][0])
    ]
    if not unknowns or len(unknowns) > 2 or not all(force["in_plane"] for force in forces):
        return [], ""
    vectors = [np.array((force["vector"][0], force["vector"][2])) for force in forces]
    resultant = sum(vectors)
    # Said first, as texts say it: "but T1 = T2". One following a known magnitude is worked out there and then.
    steps = [
        get_link_statement(forces, members)
        for members in groups.values()
        if not any(forces[j]["locks"][0] for j in members)
    ]
    for j, (known, k) in get_link_sources(forces).items():
        if not forces[known]["locks"][0]:
            continue
        value = bold(f"{np.linalg.norm(vectors[j]):.2f}", True, text_unit)
        symbol, known_symbol = forces[j]["symbol"], forces[known]["symbol"]
        if math.isclose(k, 1.0):
            steps.append(f"{symbol} = {known_symbol} = {value}")
        else:
            known_value = np.linalg.norm(vectors[known])
            steps.append(f"{symbol} = {k:g}\\, {known_symbol} = {k:g}({known_value:.2f}) = {value}")
    if len(unknowns) == 2 and unknowns[0][0] == unknowns[1][0]:
        # A whole force: what the others leave of the resultant.
        i = unknowns[0][0]
        symbol = forces[i]["symbol"]
        n = i + 1
        for axis, k in (("x", 0), ("z", 1)):
            others = [v[k] for j, v in enumerate(vectors) if j != i]
            terms = " - ".join(["R_" + axis] + [f"F_{{{axis}{j + 1}}}" for j in range(len(forces)) if j != i])
            numbers = " - ".join([f"({resultant[k]:.2f})"] + [f"({value:.2f})" for value in others])
            steps.append(f"F_{{{axis}{n}}} = {terms} = {numbers} = {vectors[i][k]:.2f}{text_unit}")
        steps.append(
            f"{symbol} = \\sqrt{{F_{{x{n}}}^2 + F_{{z{n}}}^2}} = {bold(f'{np.linalg.norm(vectors[i]):.2f}', True, text_unit)}"
        )
        if vectors[i].any():
            eighth, angle, _, _ = tool.Structural.get_eighth(vectors[i][0], vectors[i][1])
            angle_text, eighth_text = f"{angle:.1f}^\\circ", f"\\ \\text{{{eighth}}}"
            along, across = ("x", "z") if eighth in ("Q1", "Q4", "Q5", "Q8") else ("z", "x")
            steps.append(
                f"\\theta_{{{n}}} = \\tan^{{-1}}\\left(\\frac{{|F_{{{across}{n}}}|}}{{|F_{{{along}{n}}}|}}\\right) "
                f"= {bold(angle_text, True, eighth_text)}"
            )
        return steps, f"${symbol}$ in magnitude and direction, $R$ being known."
    if any(kind == "DIRECTION" for _, kind in unknowns) or any(not vectors[i].any() for i, _ in unknowns):
        return [], ""
    found = [i for i, _ in unknowns]
    # An unknown standing for forces of equal magnitude: the sum of their directions, its terms theirs together.
    members = {i: groups.get(forces[i].get("link"), [i]) for i in found}
    unit = lambda j: vectors[j] / np.linalg.norm(vectors[j])
    # Each linked force as a multiple of the first of them, which stands for them, by their ratios.
    multiple = lambda i, j: forces[j].get("factor", 1.0) / forces[i].get("factor", 1.0)
    lines = [
        {
            "symbol": forces[i]["symbol"],
            "unit": sum(multiple(i, j) * unit(j) for j in members[i]),
            "terms": (
                forces[i]["terms"]
                if len(members[i]) == 1
                else get_joined_terms([forces[j] for j in members[i]], [multiple(i, j) for j in members[i]])
            ),
        }
        for i in found
    ]
    named = lambda i: forces[i]["symbol"]
    # The links found with them, said after what is found: "F_{2} and R (with F_{3} = 0.25\, F_{2})".
    said = [get_link_statement(forces, members[i]) for i in found if len(members[i]) > 1]
    with_links = f" (with ${'$, $'.join(said)}$)" if said else ""
    if len(found) == 1:
        # A force's magnitude, and the resultant's along its known direction.
        if np.linalg.norm(resultant) < 1e-9:
            return [], ""
        eighth, angle, _, _ = tool.Structural.get_eighth(resultant[0], resultant[1])
        along = resultant / np.linalg.norm(resultant)
        terms = get_component_terms(along[0], along[1], eighth, angle)
        lines.append({"symbol": "R", "unit": along, "terms": terms, "is_resultant": True})
        # Said as the resultant is measured elsewhere in the report, from the eighth chosen for it if any.
        shown, shown_angle = get_resultant_direction(resultant[0], resultant[1], resultant_eighth)
        find = (
            f"The magnitudes of ${named(found[0])}$ and $R${with_links}, "
            f"$R$ acting at ${shown_angle:.1f}^\\circ$ {shown}, {EIGHTH_AXES[shown]}."
        )
    else:
        find = f"The magnitudes of ${named(found[0])}$ and ${named(found[1])}${with_links}, $R$ being known."
    # Along parallel lines, as two vertical forces, the sums along X and Z cannot tell the two apart: a value found
    # so was found another way, as by a kept moment, whose own section shows how.
    (ax, az), (bx, bz) = lines[0]["unit"], lines[1]["unit"]
    if abs(ax * bz - az * bx) < 1e-9:
        return [], ""
    linked = {j for i in found for j in members[i]}
    knowns = [vectors[j] for j in range(len(forces)) if j not in linked]
    steps += get_two_unknown_steps(knowns, lines, None if len(found) == 1 else resultant, text_unit)
    # Each linked force takes the one found, times its ratio.
    for i in found:
        if len(members[i]) < 2:
            continue
        found_value = np.linalg.norm(vectors[i])
        if all(math.isclose(multiple(i, j), 1.0) for j in members[i]):
            steps.append(f"{get_link_statement(forces, members[i])} = {bold(f'{found_value:.2f}', True, text_unit)}")
            continue
        for j in members[i][1:]:
            k = f"{multiple(i, j):g}"
            value = bold(f"{np.linalg.norm(vectors[j]):.2f}", True, text_unit)
            steps.append(f"{forces[j]['symbol']} = {k}\\, {forces[i]['symbol']} = {k}({found_value:.2f}) = {value}")
    return steps, find


def get_link_statement(forces: list[dict[str, Any]], members: list[int]) -> str:
    """Linked magnitudes said as texts say them, F_{2} = F_{3}, or F_{3} = 0.25\\, F_{2} for a ratio"""
    first = members[0]
    multiples = [forces[j].get("factor", 1.0) / forces[first].get("factor", 1.0) for j in members]
    if all(math.isclose(m, 1.0) for m in multiples):
        return " = ".join(forces[j]["symbol"] for j in members)
    return ",\\quad ".join(
        f"{forces[j]['symbol']} = {m:g}\\, {forces[first]['symbol']}" for j, m in zip(members[1:], multiples[1:])
    )


SUBSCRIPTS = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")


def get_link_sources(forces: list[dict[str, Any]]) -> dict[int, tuple[int, float]]:
    """Each linked force but the one its group is given from, with that one and its multiple of it: the one of
    known magnitude if any, otherwise the first"""
    sources = {}
    for members in get_link_groups(forces).values():
        first = next((j for j in members if forces[j]["locks"][0]), members[0])
        for j in members:
            if j != first:
                sources[j] = (first, forces[j].get("factor", 1.0) / forces[first].get("factor", 1.0))
    return sources


def get_link_groups(forces: list[dict[str, Any]]) -> dict[str, list[int]]:
    """The forces linked as of equal magnitude, by link, if two or more share one"""
    groups: dict[str, list[int]] = {}
    for i, force in enumerate(forces):
        if force.get("link"):
            groups.setdefault(force["link"], []).append(i)
    return {key: members for key, members in groups.items() if len(members) > 1}


def get_joined_terms(forces: list[dict[str, Any]], multiples: Union[list[float], None] = None) -> dict[str, str]:
    """The trigonometry of linked forces together, per axis, each times its multiple of the first, as
    (-\\cos 30.0^\\circ - 0.25 \\cos 60.0^\\circ)"""
    multiples = multiples or [1.0] * len(forces)
    joined = {}
    for axis in ("x", "z"):
        parts = []
        for term, m in zip((force["terms"][axis] for force in forces), multiples):
            sign, trig = ("-", term[1:]) if term.startswith("-") else ("+", term)
            parts.append((sign, trig if math.isclose(m, 1.0) else f"{m:g}\\, {trig}"))
        first = f"{'-' if parts[0][0] == '-' else ''}{parts[0][1]}"
        rest = "".join(f" {sign} {trig}" for sign, trig in parts[1:])
        joined[axis] = f"\\left({first}{rest}\\right)"
    return joined


def get_two_unknown_steps(
    knowns: list[np.ndarray],
    lines: list[dict[str, Any]],
    resultant: Union[np.ndarray, None],
    text_unit: str,
) -> list[str]:
    """Find two unknown magnitudes along known lines from the sums along X and Z, as the book does.

    If one unknown's line is vertical or horizontal, the sum across it leaves it out and finds the other,
    and the other sum then finds it. Otherwise both sums hold both unknowns: the first is solved for one,
    which is put into the second.

    :param knowns: The known forces, as X and Z components.
    :param lines: The unknowns: symbol, unit direction, the trigonometry of its components, and whether
        it is the resultant, which stands on the right of the sums.
    :param resultant: The known resultant, or None if it is one of the unknowns.
    """
    eps = 1e-9
    index = {"x": 0, "z": 1}
    clean = lambda value: value if abs(value) >= 0.005 else 0.0  # Not -0.00 from rounding.
    number = lambda value: f"({value:.2f})" if clean(value) < 0 else f"{clean(value):.2f}"
    steps: list[str] = []
    values: dict[str, float] = {}  # Unknowns found so far.

    def get_coefficient(line: dict[str, Any], axis: str) -> float:
        """The part of an unknown on the left of a sum: the resultant, on the right, moves across negated"""
        component = float(line["unit"][index[axis]])
        return -component if line.get("is_resultant") else component

    def get_equation(axis: str) -> str:
        """The sum along an axis, the unknowns written with their symbols"""
        k = index[axis]
        # Known forces with no part along the axis are left out.
        left = " + ".join(number(float(v[k])) for v in knowns if abs(v[k]) >= 0.005)
        right = f"{clean(float(resultant[k])):.2f}" if resultant is not None else "0.00"
        for line in lines:
            if abs(line["unit"][k]) < eps:
                continue
            term = line["terms"][axis]
            sign, trig = ("-", term[1:]) if term.startswith("-") else ("+", term)
            if line.get("is_resultant"):
                right = f"{'-' if sign == '-' else ''}R {trig}"
            elif left:
                left += f" {sign} {line['symbol']} {trig}"
            else:
                left = f"{'-' if sign == '-' else ''}{line['symbol']} {trig}"
        return f"\\Sigma F_{axis} = R_{axis}:\\quad {left or '0'} = {right}"

    def get_rest(axis: str) -> float:
        """What the known forces and the unknowns found so far leave across the sum, on the right"""
        k = index[axis]
        right = float(resultant[k]) if resultant is not None else 0.0
        left = sum(float(v[k]) for v in knowns)
        left += sum(values[line["symbol"]] * get_coefficient(line, axis) for line in lines if line["symbol"] in values)
        return right - left

    def solve(line: dict[str, Any], axis: str) -> None:
        """Find an unknown from a sum it is the only unknown left in"""
        rest, factor = get_rest(axis), get_coefficient(line, axis)
        value = rest / factor
        term = line["terms"][axis]
        if line.get("is_resultant"):
            steps.append(Detail(f"{term}\\, R = {clean(-rest):.2f}"))
        else:
            steps.append(Detail(f"{term}\\, {line['symbol']} = {rest:.2f}"))
        steps.append(Detail(f"{term} = {line['unit'][index[axis]]:.4f}"))
        numerator, denominator = (rest, term) if not line.get("is_resultant") else (-rest, term)
        if numerator < 0 and denominator.startswith("-"):
            numerator, denominator = -numerator, denominator[1:]  # Both signs cancel.
        steps.append(
            f"{line['symbol']} = \\frac{{{numerator:.2f}}}{{{denominator}}} = {bold(f'{value:.2f}', True, text_unit)}"
        )
        values[line["symbol"]] = value

    # A line along an axis drops out of the sum across it.
    for first, second in ((lines[0], lines[1]), (lines[1], lines[0])):
        for axis, other in (("x", "z"), ("z", "x")):
            if abs(first["unit"][index[axis]]) < eps and abs(second["unit"][index[axis]]) > eps:
                steps.append(Detail(f"{first['symbol']} \\text{{ has no component along }} {axis}"))
                steps.append(Detail(f"\\text{{as }} {first['symbol']} \\text{{ lies square to }} {axis}"))
                steps.append(get_equation(axis))
                solve(second, axis)
                steps.append(get_equation(other))
                steps.append(Detail(f"\\text{{With }} {second['symbol']} = {values[second['symbol']]:.2f}"))
                solve(first, other)
                return steps

    # Neither does, so solve one sum for one unknown and put it into the other.
    (a, b), symbols = lines, (lines[0]["symbol"], lines[1]["symbol"])
    p1, q1, h1 = get_coefficient(a, "x"), get_coefficient(b, "x"), clean(get_rest("x"))
    p2, q2, h2 = get_coefficient(a, "z"), get_coefficient(b, "z"), clean(get_rest("z"))
    # Each sum, with its working directly under it: its trigonometry, then the sum in numbers.
    for axis, (p, q, h) in (("x", (p1, q1, h1)), ("z", (p2, q2, h2))):
        steps.append(get_equation(axis))
        for line in lines:
            steps.append(Detail(f"{line['terms'][axis]} = {line['unit'][index[axis]]:.4f}"))
        steps.append(Detail(f"\\text{{In numbers: }} {p:.4f}\\, {symbols[0]} + ({q:.4f})\\, {symbols[1]} = {h:.2f}"))
    # From the first: a = h1 / p1 - (q1 / p1) b
    offset, slope = h1 / p1, -q1 / p1
    # The first unknown in terms of the second, dropping a zero term when the sum's right is zero.
    in_terms = (
        f"{offset:.4f} + ({slope:.4f})\\, {symbols[1]}" if abs(offset) >= 0.00005 else f"{slope:.4f}\\, {symbols[1]}"
    )
    # Solve the first sum for the first unknown: move the second's term across, then divide.
    steps.append(Lead(f"\\text{{Take }} \\Sigma F_x \\text{{ in numbers and solve it for }} {symbols[0]}:"))
    steps.append(Detail(f"{p1:.4f}\\, {symbols[0]} + ({q1:.4f})\\, {symbols[1]} = {h1:.2f}"))
    steps.append(Detail(f"\\text{{Subtract }} ({q1:.4f})\\, {symbols[1]} \\text{{ from both sides:}}"))
    steps.append(Detail(f"({p1:.4f})\\, {symbols[0]} = {h1:.2f} - ({q1:.4f})\\, {symbols[1]}"))
    steps.append(Detail(f"\\text{{Divide both sides by }} {p1:.4f}:"))
    steps.append(f"{symbols[0]} = \\frac{{{h1:.2f} - ({q1:.4f})\\, {symbols[1]}}}{{{p1:.4f}}} = {in_terms}")
    if abs(offset) >= 0.00005:
        steps.append(Detail(f"\\frac{{{h1:.2f}}}{{{p1:.4f}}} = {offset:.4f}"))
    steps.append(Detail(f"\\frac{{-({q1:.4f})}}{{{p1:.4f}}} = {slope:.4f}"))
    # Put it into the second sum, which leaves only the second unknown.
    steps.append(Lead(f"\\text{{Put }} {symbols[0]} = {in_terms} \\text{{ into }} \\Sigma F_z:"))
    steps.append(f"({p2:.4f})({in_terms}) + ({q2:.4f})\\, {symbols[1]} = {h2:.2f}")
    gathered, rest = p2 * slope + q2, h2 - p2 * offset
    if abs(gathered) < eps:
        return steps  # Parallel lines, which Edit Resultant does not solve.
    steps.append(Detail(f"({p2:.4f})({slope:.4f}) = {p2 * slope:.4f}"))
    if abs(offset) >= 0.00005:
        steps.append(Detail(f"({p2:.4f})({offset:.4f}) = {p2 * offset:.4f}"))
        steps.append(Detail(f"\\text{{Moved across: }} {h2:.2f} - ({p2 * offset:.4f}) = {rest:.4f}"))
    steps.append(
        Detail(
            f"\\text{{Gathering the }} {symbols[1]} \\text{{ terms: }} {p2 * slope:.4f} + ({q2:.4f}) = {gathered:.4f}"
        )
    )
    steps.append(Detail(f"({gathered:.4f})\\, {symbols[1]} = {rest:.4f}"))
    second = rest / gathered
    steps.append(f"{symbols[1]} = \\frac{{{rest:.4f}}}{{{gathered:.4f}}} = {bold(f'{second:.2f}', True, text_unit)}")
    # Then back into the first unknown's expression.
    steps.append(Lead(f"\\text{{Put }} {symbols[1]} = {second:.2f} \\text{{ back into }} {symbols[0]} = {in_terms}:"))
    first = offset + slope * second
    put_in = f"{offset:.4f} + ({slope:.4f})({second:.2f})" if abs(offset) >= 0.00005 else f"({slope:.4f})({second:.2f})"
    steps.append(f"{symbols[0]} = {put_in} = {bold(f'{first:.2f}', True, text_unit)}")
    return steps


def write_diagram(
    drawing: ShaderInfo,
    item: ifcopenshell.entity_instance,
    path: Path,
    resultant_found: bool = False,
    key: Union[str, None] = None,
) -> bool:
    """Write a structural item's load diagram as an SVG, as the X-Z plane is seen from -Y, or nothing if none.

    Values found by solving are labelled larger: those marked unlocked, and the resultant's if it was found.

    :param key: What the drawing data is tagged with, if not the item's object, as moments about it are.
    """
    if not (obj := tool.Ifc.get_object(item)):
        return False
    name = key or obj.name
    # Looking along Y, as the drawing's Y axis runs, which is left out.
    shapes = [
        e["primitive"] | {"color": e["color"]}
        for e in drawing.info
        if e.get("object") == name and "primitive" in e and not e.get("along_view")
    ]
    texts = [t for t in drawing.text_info if t.get("object") == name and not t.get("along_view")]
    # Each force and component named by its symbol in the calculations, as the drawing names them.
    texts = [t | {"text": f"{t['symbol']} = {t['text']}"} if t.get("symbol") else t for t in texts]
    if not shapes:
        return False
    flat = lambda point: np.array((point[0], -point[2]))  # SVG's Y runs down.
    points = [flat(p) for shape in shapes for k in ("tail", "tip", "start", "end") if (p := shape.get(k)) is not None]
    points += [flat(text["position"]) for text in texts]
    low, high = np.min(points, axis=0), np.max(points, axis=0)
    scale = 600 / max(*(high - low), 1e-9)  # Large enough that labels, at a fixed size, keep apart.
    # Room for the longest label beside its anchor, as labels run out from their anchors.
    longest = max((len(get_shown_text(t["text"])) for t in texts), default=0)
    margin = max(90, 20 + 8.2 * longest)
    to_svg = lambda point: (flat(point) - low) * scale + margin
    width, height = (high - low) * scale + 2 * margin
    # On white, as a figure on paper, so that its near-black lines read on dark pages too.
    elements = ['<rect width="100%" height="100%" fill="white"/>']
    placed: list[tuple[float, float, float, float]] = []
    # The arrows and solid lines drawn, which labels keep off.
    segments: list[tuple[np.ndarray, np.ndarray]] = []
    for shape in shapes:
        color, size = get_svg_color(shape["color"]), shape["size"] * scale
        if shape["type"] == "LINE":
            (x1, y1), (x2, y2) = to_svg(shape["start"]), to_svg(shape["end"])
            dash = f' stroke-dasharray="{size * 0.03:.1f} {size * 0.03:.1f}"' if shape["dashed"] else ""
            elements.append(
                f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" stroke-width="1"{dash}/>'
            )
            if not shape["dashed"]:
                segments.append(((x1, y1), (x2, y2)))  # Arcs and slope triangles; dashed guides may be crossed.
        else:
            tail, tip = to_svg(shape["tail"]), to_svg(shape["tip"])
            if not (length := np.linalg.norm(tip - tail)):
                continue
            direction = (tip - tail) / length
            across = np.array((-direction[1], direction[0]))
            # Its head scaled with its shaft, as in the viewport.
            head = min(size * shape["spacing"] * shape.get("thickness", 1.0) * 0.25, length * 0.5)
            base = tip - direction * head
            stroke = (3 if shape["spacing"] > 0.2 else 2) * shape.get("thickness", 1.0)
            corners = " ".join(
                f"{x:.1f},{y:.1f}" for x, y in (tip, base + across * head * 0.4, base - across * head * 0.4)
            )
            elements.append(
                f'<line x1="{tail[0]:.1f}" y1="{tail[1]:.1f}" x2="{base[0]:.1f}" y2="{base[1]:.1f}" '
                f'stroke="{color}" stroke-width="{stroke:.2f}"/>'
            )
            elements.append(f'<polygon points="{corners}" fill="{color}"/>')
            segments.append((tail, tip))
    for text in texts:
        found = "🔓" in text["text"] or (resultant_found and text["text"].startswith("R = "))
        elements.append(get_svg_label(text, to_svg(text["position"]), placed, found, segments))
    # Cropped to what is drawn, labels where they were placed, rather than margins wide enough for the longest
    # label on every side, which a page would scale down, and its labels with it.
    drawn = [to_svg(p) for shape in shapes for k in ("tail", "tip", "start", "end") if (p := shape.get(k)) is not None]
    drawn += [corner for x, y, w, h in placed for corner in ((x, y), (x + w, y + h))]
    (left, top), (right, bottom) = np.min(drawn, axis=0) - 12, np.max(drawn, axis=0) + 12
    width, height = right - left, bottom - top
    elements[0] = f'<rect x="{left:.1f}" y="{top:.1f}" width="{width:.1f}" height="{height:.1f}" fill="white"/>'
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width:.0f}" height="{height:.0f}" '
        f'viewBox="{left:.1f} {top:.1f} {width:.1f} {height:.1f}" font-family="sans-serif" font-size="13">\n'
        + "\n".join(elements)
        + "\n</svg>\n"
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(svg, encoding="utf-8")
    return True


def get_svg_color(color: tuple) -> str:
    """A viewport colour made to read on white paper: darkened, and white as near black"""
    rgb = [min(max(c, 0.0), 1.0) for c in color[:3]]
    if min(rgb) > 0.9:
        return NEUTRAL
    # Axis colours, of components, darkened would be too dark for dark pages, so take mid tones instead.
    if axis_color := AXIS_COLORS.get(tuple(round(c, 3) for c in rgb)):
        return axis_color
    return "#" + "".join(f"{round(c * 0.72 * 255):02x}" for c in rgb)


def get_shown_text(text: str) -> str:
    """A label as read, its subscripts inline, as they take about as much room as they show"""
    return SUBSCRIPT.sub(r"\1", text)


def get_svg_label(
    text: dict,
    anchor: np.ndarray,
    placed: list[tuple[float, float, float, float]],
    found: bool = False,
    segments: Iterable[tuple[Iterable, Iterable]] = (),
) -> str:
    """A label beside its anchor towards its away direction, moved further until it clears those placed.

    :param segments: Lines it should keep off too, such as arrows and arcs; if it cannot within reach, it keeps
        the nearest place clear of the other labels.
    """
    away = text.get("away")
    direction = np.array((away[0], -away[2])) if away is not None else np.array((1.0, 0.0))
    direction = direction / np.linalg.norm(direction) if np.linalg.norm(direction) else np.array((1.0, 0.0))
    content = str(text["text"])
    # Found values a little larger than the 13 px of the rest, rather than bold, which reads badly in SVG.
    font_size = (15 if found else 13) * tool.Structural.get_structural_props().label_size
    width, height = 7.5 * font_size / 13 * len(get_shown_text(content)), 14.0 * font_size / 13

    def get_layout(towards: np.ndarray, distance: float) -> tuple[np.ndarray, str, float, float]:
        """Where a label sits a distance from its anchor towards a direction: its anchor, alignment and box corner"""
        align = "start" if towards[0] > 0.3 else "end" if towards[0] < -0.3 else "middle"
        position = anchor + distance * towards
        left = position[0] - (0 if align == "start" else width if align == "end" else width / 2)
        top = position[1] - (0 if towards[1] > 0.3 else height if towards[1] < -0.3 else height / 2)
        return position, align, left, top

    # The nearest place clear of other labels and of lines, trying its own direction first at each distance,
    # then turning further from it, so that it moves round an arrow beside it rather than across it.
    turns = [np.radians(t) for t in (0, 30, -30, 60, -60, 90, -90, 135, -135, 180)]
    rotate = lambda v, t: np.array((v[0] * np.cos(t) - v[1] * np.sin(t), v[0] * np.sin(t) + v[1] * np.cos(t)))
    candidates = [rotate(direction, t) for t in turns]
    chosen = fallback = None  # Clear of all; clear of the labels only, if lines cannot be cleared too.
    for step in range(60):
        for towards in candidates:
            layout = get_layout(towards, 8 + 4 * step)
            left, top = layout[2], layout[3]
            if any(left < x + w and x < left + width and top < y + h and y < top + height for x, y, w, h in placed):
                continue
            fallback = fallback or layout
            if not box_crosses_segments(left - 2, top - 1, width + 4, height + 2, segments):  # As its backing.
                chosen = layout
                break
        if chosen:
            break
    position, align, left, top = chosen or fallback or get_layout(direction, 8)
    placed.append((left, top, width, height))
    # The label's middle line sits at the box's middle, which is its top plus half its height.
    color = get_svg_color(text.get("color", (0.3, 0.3, 0.3, 1)))
    escaped = content.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    # Symbols' subscripts, written F_{x1} as in the steps, set lower and smaller; Unicode has no subscript z.
    escaped = SUBSCRIPT.sub(r'<tspan baseline-shift="sub" font-size="75%">\1</tspan>', escaped)
    size = f' font-size="{font_size:.1f}"'
    # On a white box, so that lines running under it do not cross the text.
    return (
        f'<rect x="{left - 2:.1f}" y="{top - 1:.1f}" width="{width + 4:.1f}" height="{height + 2:.1f}" fill="white"/>'
        f'<text x="{position[0]:.1f}" y="{top + height / 2:.1f}" text-anchor="{align}" '
        f'dominant-baseline="central" fill="{color}"{size}>{escaped}</text>'
    )
