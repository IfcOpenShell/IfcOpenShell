# IfcQuery - IFC model interrogation CLI
# Copyright (C) 2025 Bruno Postle <bruno@postle.net>
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
import sys

import ifcopenshell

from ifcquery import info, relations, select, summary, tree


def parse_element_id(raw: str) -> int:
    """Parse an element ID from '#123' or '123' format."""
    raw = raw.strip().lstrip("#")
    return int(raw)


def format_output(data, fmt: str) -> str:
    if fmt == "json":
        return json.dumps(data, indent=2, ensure_ascii=False)
    elif fmt == "text":
        return _format_text(data)
    return json.dumps(data, indent=2, ensure_ascii=False)


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
        choices=["json", "text"],
        default="json",
        dest="output_format",
        help="Output format (default: json)",
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

    print(format_output(result, args.output_format))


if __name__ == "__main__":
    main()
