# IfcApi - CLI wrapper for ifcopenshell.api mutation functions
# Copyright (C) 2025 Bruno Postle <bruno@postle.net>
#
# This file is part of IfcApi.
#
# IfcApi is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcApi is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcApi.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import annotations

import argparse
import json
import sys

import ifcopenshell

from ifcapi.discover import function_docs, list_functions, list_modules
from ifcapi.run import run_api


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


def cmd_list(args):
    if args.module:
        try:
            functions = list_functions(args.module)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
        print(format_output(functions, args.output_format))
    else:
        modules = list_modules()
        print(format_output(modules, args.output_format))


def cmd_docs(args):
    parts = args.function_path.split(".")
    if len(parts) != 2:
        print("Error: function path must be 'module.function' (e.g. root.create_entity)", file=sys.stderr)
        sys.exit(1)
    module, function = parts
    try:
        docs = function_docs(module, function)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    print(format_output(docs, args.output_format))


def cmd_run(args, extra_args):
    try:
        model = ifcopenshell.open(args.ifc_file)
    except Exception as e:
        print(f"Error: Could not open IFC file: {e}", file=sys.stderr)
        sys.exit(1)

    parts = args.function_path.split(".")
    if len(parts) != 2:
        print("Error: function path must be 'module.function' (e.g. root.create_entity)", file=sys.stderr)
        sys.exit(1)
    module, function = parts

    # Parse extra --key value arguments into a dict
    raw_kwargs = _parse_extra_args(extra_args)

    if args.dry_run:
        result = {"ok": True, "dry_run": True, "module": module, "function": function, "args": raw_kwargs}
    else:
        result = run_api(model, module, function, raw_kwargs)

        if result["ok"]:
            output_path = args.output or args.ifc_file
            model.write(output_path)

    print(format_output(result, args.output_format))
    if not result["ok"]:
        sys.exit(1)


def _parse_extra_args(extra: list[str]) -> dict[str, str]:
    """Parse a list of ['--key', 'value', ...] into a dict."""
    kwargs = {}
    i = 0
    while i < len(extra):
        arg = extra[i]
        if arg.startswith("--"):
            key = arg[2:]
            if i + 1 < len(extra) and not extra[i + 1].startswith("--"):
                kwargs[key] = extra[i + 1]
                i += 2
            else:
                # Flag without value — treat as "true"
                kwargs[key] = "true"
                i += 1
        else:
            print(f"Error: Unexpected argument: {arg}", file=sys.stderr)
            sys.exit(1)
    return kwargs


def main():
    parser = argparse.ArgumentParser(
        prog="ifcapi",
        description="CLI wrapper for ifcopenshell.api IFC model mutation functions",
    )
    parser.add_argument(
        "--format",
        choices=["json", "text"],
        default="json",
        dest="output_format",
        help="Output format (default: json)",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # list
    list_parser = subparsers.add_parser("list", help="List API modules or functions in a module")
    list_parser.add_argument("module", nargs="?", help="Module name (omit to list all modules)")

    # docs
    docs_parser = subparsers.add_parser("docs", help="Show full documentation for an API function")
    docs_parser.add_argument("function_path", help="module.function (e.g. root.create_entity)")

    # run
    run_parser = subparsers.add_parser("run", help="Execute an API function on an IFC file")
    run_parser.add_argument("ifc_file", help="Path to the IFC file")
    run_parser.add_argument("function_path", help="module.function (e.g. root.create_entity)")
    run_parser.add_argument("-o", "--output", help="Output file path (default: overwrite input)")
    run_parser.add_argument("--dry-run", action="store_true", help="Validate without executing or saving")

    args, extra = parser.parse_known_args()

    if args.command == "list":
        cmd_list(args)
    elif args.command == "docs":
        cmd_docs(args)
    elif args.command == "run":
        cmd_run(args, extra)


if __name__ == "__main__":
    main()
