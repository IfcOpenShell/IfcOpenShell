# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2021 Thomas Krijnen <thomas@aecgeeks.com>
#
# This file is part of IfcOpenShell.
#
# IfcOpenShell is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcOpenShell is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcOpenShell.  If not, see <http://www.gnu.org/licenses/>.

# This file was generated with the assistance of an AI coding tool.

"""Sync ifcopenshell_wrapper.pyi with the compiled ifcopenshell_wrapper.py by
editing only the entries that are unambiguous to add or remove - never by
regenerating the file wholesale.

Auto-applies:
  - top-level symbols (classes, functions, constants) present in the wrapper
    but missing from the stub -> inserted, alphabetically among neighbouring
    tracked entries. A brand-new class is rendered with its full member set
    (there's no existing curated body to preserve).
  - top-level symbols in the stub that no longer exist in the wrapper at all
    -> removed.
  - for a class whose own declaration (name + bases) matches on both sides
    and whose body isn't a single-line `...`: plain members (methods, bare
    attributes - not `@property`/`@staticmethod` wrappers) present in the
    wrapper's class but missing from the stub's -> inserted; members in the
    stub's class no longer present on the wrapper's -> removed.

Never auto-applies - reported instead, left completely untouched:
  - a top-level symbol whose declaration differs between stub and wrapper
    under the same name (e.g. a function's parameter list, or a class's
    base classes).
  - `__init__`, in every case (present on both sides with a different
    signature, or missing from one side entirely) - this is almost always
    where hand-curated constructor signatures live, since SWIG always emits
    generic `*args` for overloaded C++ constructors.
  - a class member that differs under the same name but isn't a plain
    def/attribute, or any member of a class whose own declaration didn't
    match.
  - anything that only *looks* addable/removable in the narrow view this
    tool parses but is actually still present on the other side in a form
    it doesn't parse (chiefly `property()`/`staticmethod()` wrapper
    assignments, and the raw getter/setter method(s) such a wrapper
    consumes) - checked against validate_stub.py's own fuller
    canonicalisation before anything is added or removed, so this never
    causes data loss.
  - any class where, after the safe edits above, its member set still
    doesn't fully match the wrapper's (typically for the property/
    staticmethod reason above) - reported so a human can look, using
    validate_stub.py's own diff for that class.

This is exactly where a hand-curated stub is *expected* to diverge from raw
SWIG output on purpose - a mechanical tool can't tell that apart from real
drift, so it leaves those lines untouched and reports them for a human to
judge instead of guessing.

Everything else in the file - the license header, comments, blank lines,
docstrings, curated signatures, import order - is left byte-for-byte
untouched: this script tracks a line cursor through the original source and
only ever substitutes the exact line ranges of the entries it's confident
about, it never rewrites the file from scratch.

Usage:
  python sync_stub.py            # dry run: prints a report, writes nothing
  python sync_stub.py --write    # applies the safe add/remove edits in place
"""

import ast
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Union

sys.path.insert(0, str(Path(__file__).parent))
from validate_stub import SubnameType, get_function_node_name, get_names_tree

LICENSE_HEADER_START = "# IfcOpenShell - IFC toolkit and geometry engine"


@dataclass
class Entry:
    node: ast.stmt
    identity: str
    canonical: SubnameType
    is_init: bool = False
    recursable: bool = False  # True for a multi-line ClassDef we may descend into


def _assign_identity(node: Union[ast.Assign, ast.AnnAssign]) -> Optional[str]:
    if isinstance(node, ast.AnnAssign):
        target = node.target
        return target.id if isinstance(target, ast.Name) else None
    targets = node.targets
    if len(targets) != 1 or not isinstance(targets[0], ast.Name):
        return None
    name = targets[0].id
    if name.startswith(("_", "thisown")):
        return None
    return name


def iter_simple_entries(body: "list") -> "list[Entry]":
    """The subset of a module's or class's statements this tool is willing
    to reason about for auto-add/auto-remove: classes, plain function defs
    (including directly `@decorated` ones), and plain (non-`property()`/
    `staticmethod()`-wrapped) assignments. Everything else - imports, bare
    docstrings/expressions, private names, trivial `__init__(self)`, a
    `property()`/`staticmethod()` wrapper assignment itself, and the raw
    getter/setter method(s) it wraps (SWIG emits both, e.g. a
    `calc_surface_area_` method alongside `surface_area =
    property(calc_surface_area_)`) - is left alone entirely by never being
    reported as an Entry at all.
    """
    consumed: set[str] = set()
    for node in body:
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Call):
            func = node.value.func
            if isinstance(func, ast.Name) and func.id in ("property", "staticmethod"):
                consumed.update(arg.id for arg in node.value.args if isinstance(arg, ast.Name))

    entries: list[Entry] = []
    for node in body:
        if isinstance(node, ast.ClassDef):
            bases = [b.id for b in node.bases if isinstance(b, ast.Name) and b.id not in ("_object", "object")]
            bases_str = f"({', '.join(bases)})" if bases else ""
            recursable = bool(node.body) and node.body[0].lineno > node.lineno
            entries.append(Entry(node, node.name, f"class {node.name}{bases_str}:", recursable=recursable))
        elif isinstance(node, ast.FunctionDef):
            if node.name in consumed:
                continue  # the raw getter/setter behind a property()/staticmethod() wrapper - see above
            rendered = get_function_node_name(node)
            if rendered is None:
                continue  # private, or a non-informative `__init__(self)` - matches validate_stub's own skip rule
            entries.append(Entry(node, node.name, rendered, is_init=(node.name == "__init__")))
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            if isinstance(node, ast.Assign) and isinstance(node.value, ast.Call):
                continue  # property()/staticmethod() wrapper - out of scope, see function docstring
            identity = _assign_identity(node)
            if identity is not None and identity not in consumed:
                entries.append(Entry(node, identity, identity))
    return entries


def node_lines(source_lines: "list[str]", node: ast.stmt) -> "list[str]":
    start = node.decorator_list[0].lineno if isinstance(node, ast.FunctionDef) and node.decorator_list else node.lineno
    return source_lines[start - 1 : node.end_lineno]


def render_entry(canonical: SubnameType, indent: str) -> "list[str]":
    """Render a canonical name/signature value as stub text, matching
    generate_stub.py's own per-line rendering so a freshly-inserted entry
    parses back to the same canonical value get_names_tree() would compute.
    """
    parts = canonical if isinstance(canonical, tuple) else (canonical,)
    lines = []
    for part in parts:
        if part.startswith(("class ", "def ", "@")):
            lines.append(f"{indent}{part}")
        else:
            lines.append(f"{indent}{part} = ...")
    return lines


def render_new_top_level(canonical: str, indent: str, wrapper_tree: dict) -> "list[str]":
    """Render a brand-new top-level entry. For a class this can't just be
    the header line - there's no existing curated body to preserve, so the
    whole class is rendered fresh from the wrapper's true canonical subname
    set (the same full set validate_stub.py itself would compute) - it's
    all new content either way, same as generate_stub.py would produce."""
    if not canonical.startswith("class "):
        return render_entry(canonical, indent)
    subnames = wrapper_tree.get(canonical, set())
    if not subnames:
        return [f"{indent}{canonical} ..."]
    lines = [f"{indent}{canonical}"]
    for sub in sorted(subnames, key=identity_of):
        lines.extend(render_entry(sub, indent + "    "))
    return lines


def _describe(canonical: SubnameType) -> str:
    return canonical if isinstance(canonical, str) else canonical[-1]


def identity_of(value: SubnameType) -> str:
    """Bare identity name for a get_names_tree()-style canonical value or
    top-level key, so entries can be matched by name even when their full
    signature differs (or when one side's form - e.g. a `property()`-wrapped
    Assign - isn't something iter_simple_entries() looks at directly)."""
    if isinstance(value, tuple):
        return identity_of(value[-1])
    if value.startswith("class "):
        return value[len("class ") :].split("(")[0].rstrip(":")
    if value.startswith("def "):
        return value[len("def ") :].split("(")[0]
    return value


@dataclass
class Report:
    added: "list[str]" = field(default_factory=list)
    removed: "list[str]" = field(default_factory=list)
    changed: "list[str]" = field(default_factory=list)  # not auto-applied
    residual: "list[str]" = field(default_factory=list)  # not auto-applied


def splice_body(
    nodes: "list[ast.stmt]",
    source_lines: "list[str]",
    stub_tree: dict,
    wrapper_tree: dict,
    wrapper_class_bodies: "dict[str, list]",
    wrapper_entries_by_id: "dict[str, Entry]",
    indent: str,
    report: Report,
    scope: str,
    start_line: int,
    scope_end_line: int,
    class_key: Optional[str] = None,
) -> "list[str]":
    stub_by_id = {e.identity: e for e in iter_simple_entries(nodes)}
    wrapper_by_id = wrapper_entries_by_id

    # The *complete*, correctly-canonicalised view of what's really on each
    # side (this scope's full subname sets, or the module's own top-level
    # keys) - includes property()/staticmethod()-wrapped members that
    # iter_simple_entries() deliberately doesn't parse. Used only to confirm
    # an id is genuinely absent before treating it as safe to add/remove -
    # never to decide *what* to add/remove, since that still comes from the
    # narrower, safely-renderable iter_simple_entries() view.
    if class_key is None:
        full_wrapper_ids = {identity_of(k) for k in wrapper_tree}
        full_stub_ids = {identity_of(k) for k in stub_tree}
    else:
        full_wrapper_ids = {identity_of(v) for v in wrapper_tree.get(class_key, set())}
        full_stub_ids = {identity_of(v) for v in stub_tree.get(class_key, set())}

    # __init__ is never auto-added or auto-removed, only ever compared+flagged.
    added_ids = sorted(
        i for i in (wrapper_by_id.keys() - stub_by_id.keys()) if not wrapper_by_id[i].is_init and i not in full_stub_ids
    )
    removed_ids = {
        i for i in (stub_by_id.keys() - wrapper_by_id.keys()) if not stub_by_id[i].is_init and i not in full_wrapper_ids
    }

    added_iter = iter(added_ids)
    next_added = next(added_iter, None)

    out: list[str] = []

    def flush_added_up_to(identity: Optional[str]):
        nonlocal next_added
        while next_added is not None and (identity is None or next_added < identity):
            wentry = wrapper_by_id[next_added]
            if isinstance(wentry.canonical, str) and wentry.canonical.startswith("class "):
                out.extend(render_new_top_level(wentry.canonical, indent, wrapper_tree))
            else:
                out.extend(render_entry(wentry.canonical, indent))
            report.added.append(f"{scope}: + {_describe(wentry.canonical)}")
            next_added = next(added_iter, None)

    cursor = start_line - 1  # 0-indexed: next source line not yet emitted

    for node in nodes:
        node_start = (
            node.decorator_list[0].lineno if isinstance(node, ast.FunctionDef) and node.decorator_list else node.lineno
        )
        out.extend(source_lines[cursor : node_start - 1])  # gap before this node: comments, blank lines, ...
        cursor = node.end_lineno

        entries_here = iter_simple_entries([node])
        if not entries_here:
            # Not a trackable entry at all (import, docstring, stray
            # statement, private name, trivial __init__) - always pass
            # through untouched, never eligible for removal.
            out.extend(node_lines(source_lines, node))
            continue

        entry = entries_here[0]
        flush_added_up_to(entry.identity)

        if entry.identity in removed_ids:
            report.removed.append(f"{scope}: - {_describe(entry.canonical)}")
            continue  # drop it: skip emitting its text entirely

        wrapper_entry = wrapper_by_id.get(entry.identity)

        if entry.is_init or wrapper_entry is None or wrapper_entry.canonical != entry.canonical:
            if wrapper_entry is not None and wrapper_entry.canonical != entry.canonical:
                report.changed.append(
                    f"{scope}: {entry.identity}\n    stub:    {entry.canonical}\n    wrapper: {wrapper_entry.canonical}"
                )
            out.extend(node_lines(source_lines, node))
            continue

        if entry.recursable and isinstance(node, ast.ClassDef):
            child_wrapper_body = wrapper_class_bodies.get(wrapper_entry.canonical, [])
            child_wrapper_entries = {e.identity: e for e in iter_simple_entries(child_wrapper_body)}
            out.extend(source_lines[node.lineno - 1 : node.body[0].lineno - 1])  # header line(s)
            out.extend(
                splice_body(
                    node.body,
                    source_lines,
                    stub_tree,
                    wrapper_tree,
                    wrapper_class_bodies,
                    child_wrapper_entries,
                    indent + "    ",
                    report,
                    f"class {entry.identity}",
                    node.body[0].lineno,
                    node.end_lineno,
                    class_key=wrapper_entry.canonical,
                )
            )

            # Residual check: does the fully-canonical (validate_stub-grade)
            # subname set still differ after the safe edits we just made?
            full_stub = stub_tree.get(wrapper_entry.canonical, set())
            full_wrapper = wrapper_tree.get(wrapper_entry.canonical, set())
            simple_stub_canon = {e.canonical for e in iter_simple_entries(node.body)}
            simple_wrapper_canon = {e.canonical for e in child_wrapper_entries.values()}
            hypothetical = (full_stub - simple_stub_canon) | simple_wrapper_canon
            if hypothetical != full_wrapper:
                report.residual.append(
                    f"class {entry.identity}: still differs after auto-edits "
                    "(likely @property/@staticmethod-wrapped members) - inspect with validate_stub.py"
                )
        else:
            out.extend(node_lines(source_lines, node))

    flush_added_up_to(None)
    out.extend(source_lines[cursor:scope_end_line])
    return out


def main() -> None:
    write = "--write" in sys.argv

    package = Path(__file__).parent.parent.parent
    stub_path = package / "ifcopenshell_wrapper.pyi"
    wrapper_path = package / "ifcopenshell_wrapper.py"

    stub_source = stub_path.read_text()
    if not stub_source.startswith(LICENSE_HEADER_START):
        raise SystemExit(f"{stub_path} doesn't start with the expected license header - refusing to touch it.")

    stub_ast = ast.parse(stub_source)
    wrapper_ast = ast.parse(wrapper_path.read_text())

    stub_tree = get_names_tree(stub_ast)
    wrapper_tree = get_names_tree(wrapper_ast)

    wrapper_entries = {e.identity: e for e in iter_simple_entries(wrapper_ast.body)}
    wrapper_class_bodies = {e.canonical: e.node.body for e in wrapper_entries.values() if e.recursable}

    report = Report()
    stub_lines = stub_source.splitlines()
    new_lines = splice_body(
        stub_ast.body,
        stub_lines,
        stub_tree,
        wrapper_tree,
        wrapper_class_bodies,
        wrapper_entries,
        "",
        report,
        "module",
        1,
        len(stub_lines),
    )
    new_source = "\n".join(new_lines) + "\n"

    print(f"Added:   {len(report.added)}")
    for line in report.added:
        print(f"  {line}")
    print(f"Removed: {len(report.removed)}")
    for line in report.removed:
        print(f"  {line}")
    print(f"Left untouched, needs a human look ({len(report.changed)}):")
    for line in report.changed:
        print(f"  {line}")
    if report.residual:
        print(f"Residual (not auto-editable, {len(report.residual)}):")
        for line in report.residual:
            print(f"  {line}")

    if write:
        stub_path.write_text(new_source)
        print(f"\nWrote {stub_path}. Run `black` on it, then validate_stub.py to see what's left.")
    else:
        print("\nDry run - nothing written. Re-run with --write to apply the safe edits above.")
        if new_source != stub_source:
            import difflib

            print("\n--- would-be diff ---")
            sys.stdout.writelines(
                difflib.unified_diff(
                    stub_source.splitlines(keepends=True), new_source.splitlines(keepends=True), "before", "after"
                )
            )


if __name__ == "__main__":
    main()
