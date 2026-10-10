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
from pathlib import Path
from typing import Any, Union

import ifcopenshell
import ifcopenshell.util.unit
import numpy as np
import pystache

import bonsai.tool as tool
from bonsai.bim.module.structural.load_decoration_data import ShaderInfo

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
        for item in get_point_items(case):
            if items is not None and item not in items:
                continue
            activities = [a for a in tool.Structural.get_chain_activities(item, case) if is_point_force(a)]
            if not activities:
                continue
            if drawing is None:
                drawing = ShaderInfo(case)
                drawing.update()
            name = f"{get_slug(case.Name)}_{get_slug(item.Name)}_{item.id()}.svg"
            # Forces are numbered as they are drawn, tip to tail; the diagram names them so too.
            symbols = {a.id(): f"F{str(i).translate(SUBSCRIPTS)}" for i, a in enumerate(activities, 1)}
            resultant_found = bool(get_resultant_found([tool.Structural.get_locks(a) for a in activities]))
            has_diagram = write_diagram(drawing, item, directory / "diagrams" / name, symbols, resultant_found)
            point = {"name": item.Name or "Unnamed", "diagram": f"diagrams/{name}" if has_diagram else None}
            point.update(get_resultant_calculation(activities, unit, get_force_colors(drawing, item), detailed))
            points.append(point)
        if points:
            cases.append({"name": case.Name or "Unnamed", "points": points})
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


SUBSCRIPTS = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")


def get_force_colors(drawing: ShaderInfo, item: ifcopenshell.entity_instance) -> dict[int, str]:
    """The colour each activity's force is drawn in at an item, for paper"""
    if not (obj := tool.Ifc.get_object(item)):
        return {}
    return {
        text["force_of"]: get_svg_color(text["color"])
        for text in drawing.text_info
        if text.get("object") == obj.name and text.get("force_of")
    }


def get_point_items(case: ifcopenshell.entity_instance) -> list[ifcopenshell.entity_instance]:
    """The structural point connections with loads in a load case, directly or in its load groups, by name"""
    items, groups, seen = set(), [case], set()
    while groups:
        group = groups.pop()
        if group.id() in seen:
            continue
        seen.add(group.id())
        for rel in group.IsGroupedBy or []:
            for obj in rel.RelatedObjects:
                if obj.is_a("IfcStructuralLoadGroup") and not obj.is_a("IfcStructuralLoadCase"):
                    groups.append(obj)
                elif obj.is_a("IfcStructuralActivity") and (connects := obj.AssignedToStructuralItem):
                    if (item := connects[0].RelatingElement) and item.is_a("IfcStructuralPointConnection"):
                        items.add(item)
    return sorted(items, key=lambda item: (item.Name or "", item.id()))


def is_point_force(activity: ifcopenshell.entity_instance) -> bool:
    return bool(activity.AppliedLoad and activity.AppliedLoad.is_a("IfcStructuralLoadSingleForce"))


def get_force_unit_symbol() -> str:
    unit = ifcopenshell.util.unit.get_project_unit(tool.Ifc.get(), "FORCEUNIT")
    return ifcopenshell.util.unit.get_unit_symbol(unit) if unit else "N"


def get_slug(name: Union[str, None]) -> str:
    return re.sub(r"[^\w.-]+", "_", name or "").strip("_") or "Unnamed"


def get_resultant_found(locks: list[tuple[bool, bool]]) -> list[str]:
    """What of a resultant was found, from how many force values were: Edit Resultant finds two unknowns in all"""
    unknown = sum(not locked for lock in locks for locked in lock)
    return [["magnitude", "direction"], ["magnitude"]][unknown] if unknown < 2 else []


def bold(text: str, is_bold: bool = True, suffix: str = "") -> str:
    """A value in bold in LaTeX, for one found by solving, with its suffix, as a unit, bold too"""
    if not is_bold:
        return text + suffix
    return f"\\mathbf{{{text}}}" + suffix.replace("\\text{", "\\textbf{")


class Detail(str):
    """A step shown only in detailed reports: the working between the main steps"""


def get_resultant_calculation(
    activities: list[ifcopenshell.entity_instance],
    unit: str,
    colors: Union[dict[int, str], None] = None,
    detailed: bool = False,
) -> dict[str, Any]:
    """The steps for concurrent point forces and their resultant.

    If some force values were unknown (unlocked) and found by Edit Resultant, the steps find them first, as
    the problem was posed, then add the forces up as a check. Edit Resultant solves two unknowns, so the
    number unlocked tells what was known of the resultant: with one, its direction; with two, all of it.
    """
    text_unit = r"\ \text{" + re.sub(r"([#$%&_{}])", r"\\\1", unit) + "}"
    forces = [get_force_terms(activity, i) for i, activity in enumerate(activities, 1)]
    # Each force in the colour of its arrow. Markdown keeps colour only in math, so symbols are coloured there.
    palette = [(colors or {}).get(activity.id(), "#222222") for activity in activities]
    rows = []
    for force, color in zip(forces, palette):
        found = [text for text, locked in zip(("magnitude", "direction"), force["locks"]) if not locked]
        rows.append(get_table_row(force["symbol"], force["name"], force["magnitude"], force["direction"], found, color))
        rows[-1]["magnitude"] += f" {unit}"
    solving, find = get_solving_steps(forces, text_unit)
    # Components first, then the unknowns found from them, then the resultant with what was found.
    found = {
        i: "MAGNITUDE" if force["locks"][1] else "WHOLE" for i, force in enumerate(forces) if not all(force["locks"])
    }
    resultant_found = get_resultant_found([force["locks"] for force in forces])
    components, steps, summary = get_sum_steps(forces, text_unit, unit, found if solving else None, resultant_found)
    # The resultant too. What of it was found follows from how many force values were: two unknowns in all.
    total = [sum(force["vector"][k] for force in forces) for k in range(3)]
    magnitude = math.sqrt(sum(c * c for c in total))
    direction = "components given"
    if not total[1] and magnitude > 1e-9:
        eighth, angle, _, _ = tool.Structural.get_eighth(total[0], total[2])
        direction = f"{angle:.1f}° {eighth}, {EIGHTH_AXES[eighth]}"
    found = resultant_found
    rows.append(get_table_row("R", "Resultant", magnitude, direction, found, "#222222"))
    rows[-1]["magnitude"] += f" {unit}"
    # Detailed steps in grey, applied in LaTeX so that both formats show it; force symbols keep their colours.
    gray = lambda step: f"{{\\color{{#8c8c8c}}\\qquad {step}}}" if isinstance(step, Detail) else step  # Indented.
    render = lambda steps: [
        {"latex": get_colored_symbols(gray(step), palette), "detail": isinstance(step, Detail)}
        for step in steps
        if detailed or not isinstance(step, Detail)
    ]
    return {
        "forces": rows,
        "find": get_colored_symbols(find, palette),  # With inline math, $F_{2}$, as both formats read.
        "solving": render(solving),
        "has_solving": bool(solving),
        "components": render(components),
        "steps": render(steps),
        "summary": summary,
    }


def get_table_row(
    symbol: str, name: str, magnitude: float, direction: str, found: list[str], color: str
) -> dict[str, str]:
    return {
        "color": color,
        "symbol": symbol,
        "colored_symbol": f"{{\\color{{{color}}}{symbol}}}",
        "name": name,
        "magnitude": f"{magnitude:.2f}",
        "direction": direction,
        "found": ", ".join(found),
        # Values found by solving are set in bold.
        "magnitude_found": "magnitude" in found,
        "direction_found": "direction" in found,
    }


def get_colored_symbols(step: str, palette: list[str]) -> str:
    """Colour each force's symbols in a step, F_{2}, F_{x2} and \\theta_{2}, as its arrow is coloured"""

    def colored(match: re.Match) -> str:
        i = int(match[2] or match[3]) - 1
        return f"{{\\color{{{palette[i]}}}{match[1]}}}" if 0 <= i < len(palette) else match[1]

    return re.sub(r"(F_\{[xyz]?(\d+)\}|\\theta_\{(\d+)\})", colored, step)


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
    return force


def get_component_terms(x: float, z: float, eighth: str, angle: float) -> dict[str, str]:
    """The trigonometry of the X and Z components of a direction, with signs, as -\\sin 40.0^\\circ"""
    # Measured from a horizontal axis, X takes the cosine; from a vertical one, the sine.
    trig_x, trig_z = (r"\cos", r"\sin") if eighth in ("Q1", "Q4", "Q5", "Q8") else (r"\sin", r"\cos")
    return {
        "x": f"{'-' if x < 0 else ''}{trig_x} {angle:.1f}^\\circ",
        "z": f"{'-' if z < 0 else ''}{trig_z} {angle:.1f}^\\circ",
    }


def get_sum_steps(
    forces: list[dict[str, Any]],
    text_unit: str,
    unit: str,
    found: Union[dict[int, str], None] = None,
    resultant_found: tuple[str, ...] = (),
) -> tuple[list[str], list[str], str]:
    """Each force's components, then their sums, and the resultant's magnitude and angle.

    :param found: Forces whose values are found by solving, by index: MAGNITUDE if only that, else WHOLE.
        Their components come with the resultant, once found; before solving, an unknown magnitude's are
        written with its symbol, and an unknown force's not at all.
    :return: The component steps, the resultant steps, and the result in words.
    """
    number = lambda value: f"{value:.2f}" if value >= 0 else f"({value:.2f})"
    found = found or {}
    components, steps = [], []
    for i, force in enumerate(forces, 1):
        x, y, z = force["vector"]
        if force["in_plane"]:
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
        eighth, angle, _, _ = tool.Structural.get_eighth(totals["x"], totals["z"])
        angle_text, eighth_text = f"{angle:.1f}^\\circ", f"\\ \\text{{{eighth}}}"
        along, across = ("x", "z") if eighth in ("Q1", "Q4", "Q5", "Q8") else ("z", "x")
        ratio = abs(totals[across]) / abs(totals[along])
        steps.append(Detail(f"\\text{{Measured {EIGHTH_AXES[eighth].split(',')[0]}}}"))  # As "from −Z".
        steps.append(
            Detail(
                f"\\tan\\theta_R = \\frac{{|R_{across}|}}{{|R_{along}|}} = "
                f"\\frac{{{abs(totals[across]):.2f}}}{{{abs(totals[along]):.2f}}} = {ratio:.4f}"
            )
        )
        steps.append(
            f"\\theta_R = \\tan^{{-1}}\\left(\\frac{{|R_{across}|}}{{|R_{along}|}}\\right) = "
            f"\\tan^{{-1}}\\left(\\frac{{{abs(totals[across]):.2f}}}{{{abs(totals[along]):.2f}}}\\right) = "
            f"{bold(angle_text, 'direction' in resultant_found, eighth_text)}"
        )
        summary += f" at {angle:.1f}° {eighth}, {EIGHTH_AXES[eighth]}"
    elif resultant <= 1e-9:
        summary += ": the forces are in equilibrium"
    return components, steps, summary


def get_solving_steps(forces: list[dict[str, Any]], text_unit: str) -> tuple[list[str], str]:
    """The steps finding the unknown (unlocked) values, and what they find, or none if all were known.

    Each unknown magnitude is found by summing along an axis square to the other unknown's line, which
    leaves it out: X or Z when that line is vertical or horizontal, else an axis tilted to suit.
    """
    unknowns = [
        (i, kind)
        for i, force in enumerate(forces)
        for kind, locked in zip(("MAGNITUDE", "DIRECTION"), force["locks"])
        if not locked
    ]
    if not unknowns or len(unknowns) > 2 or not all(force["in_plane"] for force in forces):
        return [], ""
    vectors = [np.array((force["vector"][0], force["vector"][2])) for force in forces]
    resultant = sum(vectors)
    unit_of = lambda v: v / np.linalg.norm(v)
    steps = []
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
    if len(unknowns) == 1:
        # A force's magnitude, and the resultant's along its known direction.
        i = unknowns[0][0]
        if np.linalg.norm(resultant) < 1e-9:
            return [], ""
        steps += get_elimination_steps(forces, vectors, i, unit_of(resultant), "R", 0.0, text_unit)
        eighth, angle, _, _ = tool.Structural.get_eighth(resultant[0], resultant[1])
        find = (
            f"The magnitudes of ${forces[i]['symbol']}$ and $R$, "
            f"$R$ acting at ${angle:.1f}^\\circ$ {eighth}, {EIGHTH_AXES[eighth]}."
        )
        return steps, find
    # Two force magnitudes, the resultant being known: each found square to the other's line.
    (i, _), (j, _) = unknowns
    for found, other in ((i, j), (j, i)):
        line = unit_of(vectors[other])
        steps += get_elimination_steps(
            forces, vectors, found, line, forces[other]["symbol"], None, text_unit, exclude=other, resultant=resultant
        )
    find = f"The magnitudes of ${forces[i]['symbol']}$ and ${forces[j]['symbol']}$, $R$ being known."
    return steps, find


def get_elimination_steps(
    forces: list[dict[str, Any]],
    vectors: list[np.ndarray],
    found: int,
    line: np.ndarray,
    line_symbol: str,
    line_value: Union[float, None],
    text_unit: str,
    exclude: Union[int, None] = None,
    resultant: Union[np.ndarray, None] = None,
) -> list[str]:
    """Find one force's magnitude by summing along an axis square to another unknown's line, leaving it out.

    :param line: The unit direction of the other unknown: the resultant, or another force.
    :param line_value: The resultant's component along the axis, if the other unknown is the resultant
        (zero, as the axis is square to it); else None, and the known resultant's component is used.
    :param exclude: The other unknown force, left out of the sum.
    """
    # Along X if the line is vertical, Z if horizontal, else an axis square to it.
    if abs(line[0]) < 1e-9:
        axis, name, k = np.array((1.0, 0.0)), "x", 0
    elif abs(line[1]) < 1e-9:
        axis, name, k = np.array((0.0, 1.0)), "z", 1
    else:
        axis, name, k = np.array((-line[1], line[0])), "n", None
    steps = []
    if k is None:
        eighth, angle, _, _ = tool.Structural.get_eighth(axis[0], axis[1])
        steps.append(
            f"\\text{{Axis }} n \\perp {line_symbol}:\\ {angle:.1f}^\\circ\\ \\text{{{eighth}, {EIGHTH_AXES[eighth]}}}"
        )
    rhs = line_value if line_value is not None else float(np.dot(resultant, axis))
    rhs_symbol = "R_" + name
    known, terms = 0.0, []
    for j, force in enumerate(forces):
        if j in (found, exclude):
            continue
        value = float(np.dot(vectors[j], axis))
        known += value
        terms.append(f"({value:.2f})" if value < 0 else f"{value:.2f}")
    direction = vectors[found] / np.linalg.norm(vectors[found])
    factor = float(np.dot(direction, axis))
    if k is None:
        between = math.degrees(math.acos(max(-1.0, min(1.0, factor))))
        trig = f"\\cos {between:.1f}^\\circ"
    else:
        trig = forces[found]["terms"][name]
    symbol = forces[found]["symbol"]
    unknown_term = f"- {symbol} {trig[1:]}" if trig.startswith("-") else f"+ {symbol} {trig}"
    left = (" + ".join(terms) + " " if terms else "") + unknown_term
    if not terms:
        left = left.lstrip("+ ")
    reason = f"n \\perp {line_symbol}" if k is None else f"{line_symbol} \\text{{ lies square to }} {name}"
    steps.append(Detail(f"{line_symbol} \\text{{ has no component along }} {name}"))
    steps.append(Detail(f"\\text{{as }} {reason}"))
    steps.append(f"\\Sigma F_{name} = {rhs_symbol}:\\quad {left} = {rhs:.2f}")
    steps.append(
        Detail(
            f"\\text{{Rearranged: }} {trig}\\, {symbol} = {rhs:.2f} - "
            f"{f'({known:.2f})' if known < 0 else f'{known:.2f}'} = {rhs - known:.2f}"
        )
    )
    steps.append(Detail(f"{trig} = {factor:.4f}"))
    magnitude = (rhs - known) / factor
    numerator, denominator = rhs - known, trig
    if numerator < 0 and trig.startswith("-"):
        numerator, denominator = -numerator, trig[1:]  # Both signs cancel.
    steps.append(f"{symbol} = \\frac{{{numerator:.2f}}}{{{denominator}}} = {bold(f'{magnitude:.2f}', True, text_unit)}")
    return steps


def write_diagram(
    drawing: ShaderInfo,
    item: ifcopenshell.entity_instance,
    path: Path,
    symbols: Union[dict[int, str], None] = None,
    resultant_found: bool = False,
) -> bool:
    """Write a structural item's load diagram as an SVG, as the X-Z plane is seen from -Y, or nothing if none.

    Values found by solving are labelled larger: those marked unlocked, and the resultant's if it was found.
    """
    if not (obj := tool.Ifc.get_object(item)):
        return False
    shapes = [
        e["primitive"] | {"color": e["color"]} for e in drawing.info if e.get("object") == obj.name and "primitive" in e
    ]
    texts = [t for t in drawing.text_info if t.get("object") == obj.name]
    # Name each force's magnitude by its symbol in the calculations.
    texts = [
        t | {"text": f"{symbols[t['force_of']]} = {t['text']}"} if t.get("force_of") in (symbols or {}) else t
        for t in texts
    ]
    if not shapes:
        return False
    flat = lambda point: np.array((point[0], -point[2]))  # SVG's Y runs down.
    points = [flat(p) for shape in shapes for k in ("tail", "tip", "start", "end") if (p := shape.get(k)) is not None]
    points += [flat(text["position"]) for text in texts]
    low, high = np.min(points, axis=0), np.max(points, axis=0)
    scale = 420 / max(*(high - low), 1e-9)
    margin = 90
    to_svg = lambda point: (flat(point) - low) * scale + margin
    width, height = (high - low) * scale + 2 * margin
    elements = []
    for shape in shapes:
        color, size = get_svg_color(shape["color"]), shape["size"] * scale
        if shape["type"] == "LINE":
            (x1, y1), (x2, y2) = to_svg(shape["start"]), to_svg(shape["end"])
            dash = f' stroke-dasharray="{size * 0.03:.1f} {size * 0.03:.1f}"' if shape["dashed"] else ""
            elements.append(
                f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" stroke-width="1"{dash}/>'
            )
        else:
            tail, tip = to_svg(shape["tail"]), to_svg(shape["tip"])
            if not (length := np.linalg.norm(tip - tail)):
                continue
            direction = (tip - tail) / length
            across = np.array((-direction[1], direction[0]))
            head = min(size * shape["spacing"] * 0.25, length * 0.5)
            base = tip - direction * head
            stroke = 3 if shape["spacing"] > 0.2 else 2
            corners = " ".join(
                f"{x:.1f},{y:.1f}" for x, y in (tip, base + across * head * 0.4, base - across * head * 0.4)
            )
            elements.append(
                f'<line x1="{tail[0]:.1f}" y1="{tail[1]:.1f}" x2="{base[0]:.1f}" y2="{base[1]:.1f}" '
                f'stroke="{color}" stroke-width="{stroke}"/>'
            )
            elements.append(f'<polygon points="{corners}" fill="{color}"/>')
    placed: list[tuple[float, float, float, float]] = []
    for text in texts:
        found = "🔓" in text["text"] or (resultant_found and text["text"].startswith("R = "))
        elements.append(get_svg_label(text, to_svg(text["position"]), placed, found))
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width:.0f}" height="{height:.0f}" '
        f'viewBox="0 0 {width:.0f} {height:.0f}" font-family="sans-serif" font-size="13">\n'
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
        return "#222222"
    return "#" + "".join(f"{round(c * 0.72 * 255):02x}" for c in rgb)


def get_svg_label(
    text: dict, anchor: np.ndarray, placed: list[tuple[float, float, float, float]], found: bool = False
) -> str:
    """A label beside its anchor towards its away direction, moved further until it clears those placed"""
    away = text.get("away")
    direction = np.array((away[0], -away[2])) if away is not None else np.array((1.0, 0.0))
    direction = direction / np.linalg.norm(direction) if np.linalg.norm(direction) else np.array((1.0, 0.0))
    content = str(text["text"])
    # Found values a little larger than the 13 px of the rest, rather than bold, which reads badly in SVG.
    font_size = 15 if found else 13
    width, height = 7.5 * font_size / 13 * len(content), 14.0 * font_size / 13
    align = "start" if direction[0] > 0.3 else "end" if direction[0] < -0.3 else "middle"
    position = anchor + 8 * direction
    for _ in range(40):
        left = position[0] - (0 if align == "start" else width if align == "end" else width / 2)
        top = position[1] - (0 if direction[1] > 0.3 else height if direction[1] < -0.3 else height / 2)
        if not any(left < x + w and x < left + width and top < y + h and y < top + height for x, y, w, h in placed):
            break
        position = position + 4 * direction
    placed.append((left, top, width, height))
    # The label's middle line sits at the box's middle, which is its top plus half its height.
    color = get_svg_color(text.get("color", (0.3, 0.3, 0.3, 1)))
    escaped = content.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    size = f' font-size="{font_size}"' if found else ""
    # On a white box, so that lines running under it do not cross the text.
    return (
        f'<rect x="{left - 2:.1f}" y="{top - 1:.1f}" width="{width + 4:.1f}" height="{height + 2:.1f}" fill="white"/>'
        f'<text x="{position[0]:.1f}" y="{top + height / 2:.1f}" text-anchor="{align}" '
        f'dominant-baseline="central" fill="{color}"{size}>{escaped}</text>'
    )
