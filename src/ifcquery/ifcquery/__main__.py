# This file was generated with the assistance of an AI coding tool.
# IfcQuery - IFC model interrogation CLI
# Copyright (C) 2026 Bruno Postle <bruno@postle.net>
#
# This file is part of IfcQuery.
#
# IfcQuery is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcQuery is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcQuery.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import annotations

import argparse
import json
import os
import sys

import ifcopenshell

from ifcquery import clash as clash_mod
from ifcquery import contexts as contexts_mod
from ifcquery import cost as cost_mod
from ifcquery import (
    info,
    plot,
    relations,
    schedule,
    schema,
    select,
    summary,
    tree,
)
from ifcquery import (
    materials as materials_mod,
)
from ifcquery import (
    render as render_mod,
)
from ifcquery import validate as validate_mod


def parse_element_id(raw: str) -> int:
    """Parse an element ID from '#123' or '123' format."""
    raw = raw.strip().lstrip("#")
    return int(raw)


def format_output(data, fmt: str) -> str:
    if fmt == "json":
        return json.dumps(data, indent=2, ensure_ascii=False)
    elif fmt == "text":
        return _format_text(data)
    elif fmt == "ids":
        return _format_ids(data)
    return json.dumps(data, indent=2, ensure_ascii=False)


def _format_ids(data) -> str:
    """Extract 'id' fields from a list of dicts and return as comma-separated string.

    For dicts with a top-level 'elements' key (e.g. clash, relations output),
    extracts from that flat summary list rather than the nested structure.
    """
    if isinstance(data, list):
        ids = [str(item["id"]) for item in data if isinstance(item, dict) and "id" in item]
        return ",".join(ids)
    if isinstance(data, dict):
        if "elements" in data and isinstance(data["elements"], list):
            return _format_ids(data["elements"])
        if "id" in data:
            return str(data["id"])
    return ""


def _format_text(data, indent: int = 0) -> str:
    prefix = "  " * indent
    lines = []
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                lines.append(f"{prefix}{key}:")
                lines.append(_format_text(value, indent + 1))
            else:
                lines.append(f"{prefix}{key}: {value}")
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                lines.append(_format_text(item, indent))
                lines.append("")
            else:
                lines.append(f"{prefix}- {item}")
    else:
        lines.append(f"{prefix}{data}")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        prog="ifcquery",
        description="Query and inspect IFC building models",
    )
    parser.add_argument("ifc_file", help="Path to the IFC file")
    parser.add_argument(
        "--format",
        choices=["json", "text", "ids"],
        default="json",
        dest="output_format",
        help="Output format: json (default), text (human-readable), ids (comma-separated step IDs)",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("summary", help="Model overview: schema, element counts, project info")

    subparsers.add_parser("tree", help="Spatial hierarchy tree")

    info_parser = subparsers.add_parser("info", help="Deep inspection of a specific element")
    info_parser.add_argument("element_id", help="Element step ID (e.g. 123 or #123)")

    select_parser = subparsers.add_parser("select", help="Filter elements using selector syntax")
    select_parser.add_argument("query", help="Selector query string")

    relations_parser = subparsers.add_parser("relations", help="Show relationships for an element")
    relations_parser.add_argument("element_id", help="Element step ID (e.g. 123 or #123)")
    relations_parser.add_argument("--traverse", choices=["up"], help="Traverse hierarchy (up: walk to IfcProject)")

    clash_parser = subparsers.add_parser("clash", help="Check element placement for clashes")
    clash_parser.add_argument("element_id", help="Element step ID (e.g. 123 or #123)")
    clash_parser.add_argument("--clearance", type=float, help="Minimum clearance distance")
    clash_parser.add_argument("--tolerance", type=float, default=0.002, help="Intersection tolerance (default: 0.002)")
    clash_parser.add_argument(
        "--scope", choices=["storey", "all"], default="storey", help="Scope of elements to check (default: storey)"
    )

    validate_parser = subparsers.add_parser("validate", help="Schema/constraint validation")
    validate_parser.add_argument(
        "--rules", action="store_true", help="Also check EXPRESS rules (slower, default: false)"
    )

    schedule_parser = subparsers.add_parser("schedule", help="List work plans and tasks from the model")
    schedule_parser.add_argument(
        "--depth", type=int, default=None, metavar="N", help="Limit subtask expansion to N levels (default: unlimited)"
    )

    cost_parser = subparsers.add_parser("cost", help="List cost schedules and cost items from the model")
    cost_parser.add_argument(
        "--depth",
        type=int,
        default=None,
        metavar="N",
        help="Limit cost item expansion to N levels (default: unlimited)",
    )

    subparsers.add_parser("contexts", help="List geometric representation contexts and subcontexts")

    subparsers.add_parser("materials", help="List materials and material sets")

    schema_parser = subparsers.add_parser("schema", help="IFC class documentation")
    schema_parser.add_argument("entity_type", help="IFC entity type (e.g. IfcWall)")

    render_parser = subparsers.add_parser("render", help="Render model geometry to a PNG image")
    render_parser.add_argument(
        "-o", "--output", default="", metavar="FILE", help="Output PNG path (default: <ifc_file>.png)"
    )
    render_parser.add_argument(
        "--selector", default="", metavar="QUERY", help="ifcopenshell selector to restrict rendered elements"
    )
    render_parser.add_argument(
        "--element",
        default="",
        metavar="ID[,ID...]",
        help="Comma-separated step IDs of elements to highlight (rest rendered in grey)",
    )
    render_parser.add_argument(
        "--view",
        choices=render_mod.VIEWS,
        default="iso",
        help="Camera angle (default: iso)",
    )

    plot_parser = subparsers.add_parser(
        "plot", help="Plot model drawing (SVG via ifcopenshell.draw; optional PNG via CairoSVG)"
    )
    plot_parser.add_argument(
        "-o",
        "--output",
        default="",
        metavar="FILE",
        help="Output file path. Default depends on --out-format: <ifc_file>.svg/.png",
    )
    plot_parser.add_argument(
        "--out-format",
        choices=["svg", "png", "base64"],
        default="png",
        help="Output format: svg (write SVG), png (write PNG), base64 (print base64 in JSON/text). Default: png",
    )
    plot_parser.add_argument(
        "--selector", default="", metavar="QUERY", help="ifcopenshell selector to restrict plotted elements"
    )
    plot_parser.add_argument(
        "--element", default="", metavar="ID[,ID...]", help="Comma-separated step IDs of elements to highlight"
    )
    plot_parser.add_argument(
        "--view",
        choices=getattr(plot, "VIEWS", ("floorplan", "elevation", "section", "auto")),
        default="floorplan",
        help="Drawing view (default: floorplan)",
    )
    plot_parser.add_argument(
        "--width-mm",
        type=float,
        default=297.0,
        metavar="MM",
        help="Paper width in mm (default: 297)",
    )
    plot_parser.add_argument(
        "--height-mm",
        type=float,
        default=420.0,
        metavar="MM",
        help="Paper height in mm (default: 420)",
    )
    plot_parser.add_argument(
        "--scale",
        type=float,
        default=1.0 / 100.0,
        metavar="S",
        help="Model-to-paper scale (default: 0.01 = 1:100)",
    )
    plot_parser.add_argument(
        "--png-width",
        type=int,
        default=1024,
        metavar="PX",
        help="PNG width in pixels (default: 1024)",
    )
    plot_parser.add_argument(
        "--png-height",
        type=int,
        default=1024,
        metavar="PX",
        help="PNG height in pixels (default: 1024)",
    )

    args = parser.parse_args()

    try:
        model = ifcopenshell.open(args.ifc_file)
    except Exception as e:
        print(f"Error: Could not open IFC file: {e}", file=sys.stderr)
        sys.exit(1)

    if args.command == "summary":
        result = summary.summary(model)
    elif args.command == "tree":
        result = tree.tree(model)
    elif args.command == "info":
        try:
            element_id = parse_element_id(args.element_id)
        except ValueError:
            print(f"Error: Invalid element ID: {args.element_id}", file=sys.stderr)
            sys.exit(1)
        try:
            element = model.by_id(element_id)
        except RuntimeError:
            print(f"Error: Element #{element_id} not found", file=sys.stderr)
            sys.exit(1)
        result = info.info(model, element)
    elif args.command == "select":
        result = select.select(model, args.query)
    elif args.command == "relations":
        try:
            element_id = parse_element_id(args.element_id)
        except ValueError:
            print(f"Error: Invalid element ID: {args.element_id}", file=sys.stderr)
            sys.exit(1)
        try:
            element = model.by_id(element_id)
        except RuntimeError:
            print(f"Error: Element #{element_id} not found", file=sys.stderr)
            sys.exit(1)
        result = relations.relations(model, element, traverse=args.traverse)
    elif args.command == "clash":
        try:
            element_id = parse_element_id(args.element_id)
        except ValueError:
            print(f"Error: Invalid element ID: {args.element_id}", file=sys.stderr)
            sys.exit(1)
        try:
            element = model.by_id(element_id)
        except RuntimeError:
            print(f"Error: Element #{element_id} not found", file=sys.stderr)
            sys.exit(1)
        try:
            result = clash_mod.clash(
                model, element, clearance=args.clearance, tolerance=args.tolerance, scope=args.scope
            )
        except ImportError:
            print("Error: ifcopenshell geometry engine not available (C++ bindings required)", file=sys.stderr)
            sys.exit(1)
    elif args.command == "validate":
        result = validate_mod.validate(model, express_rules=args.rules)
    elif args.command == "schedule":
        result = schedule.schedule(model, max_depth=args.depth)
    elif args.command == "cost":
        result = cost_mod.cost(model, max_depth=args.depth)
    elif args.command == "contexts":
        result = contexts_mod.contexts(model)
    elif args.command == "materials":
        result = materials_mod.materials(model)
    elif args.command == "schema":
        result = schema.schema(model, args.entity_type)
    elif args.command == "render":
        element_ids = None
        if args.element:
            try:
                element_ids = [parse_element_id(part) for part in args.element.split(",")]
            except ValueError:
                print(f"Error: Invalid element ID(s): {args.element}", file=sys.stderr)
                sys.exit(1)
        out_path = args.output or (os.path.splitext(args.ifc_file)[0] + ".png")
        try:
            png_bytes = render_mod.render(
                model,
                selector=args.selector or None,
                element_ids=element_ids,
                view=args.view,
            )
        except ImportError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
        with open(out_path, "wb") as f:
            f.write(png_bytes)
        print(f"Saved render to {out_path}", file=sys.stderr)
        return
    elif args.command == "plot":
        element_ids = None
        if args.element:
            try:
                element_ids = [parse_element_id(part) for part in args.element.split(",")]
            except ValueError:
                print(f"Error: Invalid element ID(s): {args.element}", file=sys.stderr)
                sys.exit(1)

        try:
            result = plot.plot(
                model,
                selector=args.selector or None,
                element_ids=element_ids,
                view=args.view,
                width_mm=args.width_mm,
                height_mm=args.height_mm,
                scale=args.scale,
                output_format=args.out_format,
            )
        except ImportError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

        if args.out_format == "base64":
            # result is a dict; serialise to stdout so callers can consume it
            print(format_output(result, args.output_format))
            return

        # svg or png: write to a file
        base = os.path.splitext(args.ifc_file)[0]
        if args.out_format == "svg":
            out_path = args.output or (base + ".svg")
        else:
            out_path = args.output or (base + ".png")

        with open(out_path, "wb") as f:
            f.write(result)

        print(f"Saved drawing to {out_path}", file=sys.stderr)
        return

    print(format_output(result, args.output_format))


if __name__ == "__main__":
    main()
