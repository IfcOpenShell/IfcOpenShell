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

"""Script to ensure ifcopenshell_wrapper.pyi and ifcopenshell_wrapper.py work in sync.

Things we do check:
- all symbols from the wrapper present in the stub and vice versa
- functions and methods signatures
- read-only and settable properties, staticmethods
- class hierarchy
"""

import ast
import difflib
from pathlib import Path
from typing import Union

from typing_extensions import assert_never


def format_diff(lines: list[str]) -> None:
    RED = "\033[91m"
    GREEN = "\033[92m"
    CYAN = "\033[96m"
    RESET = "\033[0m"
    for line in lines:
        if line.startswith("+") and not line.startswith("+++"):
            print(f"{GREEN}{line}{RESET}")
        elif line.startswith("-") and not line.startswith("---"):
            print(f"{RED}{line}{RESET}")
        elif line.startswith("@@"):
            print(f"{CYAN}{line}{RESET}")
        else:
            print(line)


SubnameType = Union[str, tuple[str, str]]


def get_function_node_name(node: ast.FunctionDef) -> Union[SubnameType, None]:
    """
    :return: Function node name as ``SubnameType``  or ``None``, if function wasn't processed and can be skipped.
    """
    node_name = node.name
    is_init = node_name == "__init__"

    arg_nodes = node.args.args
    defaults = [None] * (len(arg_nodes) - len(node.args.defaults)) + node.args.defaults
    args: list[str] = []
    for arg, default in zip(arg_nodes, defaults):
        if default is None:
            args.append(arg.arg)
        else:
            args.append(f"{arg.arg}={ast.unparse(default)}")

    if arg := node.args.vararg:
        args.append(f"*{arg.arg}")

    if arg := node.args.kwarg:
        args.append(f"**{arg.arg}")

    # Skip non-informative constructors.
    if is_init and args == ["self"]:
        return None

    node_name = f"def {node.name}"
    node_name = f"{node_name}({', '.join(args)}): ..."

    decorators = tuple(f"@{d.id}" for d in node.decorator_list if isinstance(d, ast.Name))
    if len(decorators) == 1:
        return decorators + (node_name,)
    return node_name


def _count_params(def_string: str) -> int:
    """Count parameters in a rendered ``def name(...): ...`` string.

    Used to tell a getter (typically just ``self``) apart from a setter
    (``self`` plus one more argument) when two same-named function
    definitions need to be resolved.
    """
    start = def_string.index("(")
    depth = 0
    count = 0
    has_params = False
    for ch in def_string[start:]:
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth -= 1
            if depth == 0:
                break
        elif depth == 1:
            if ch == ",":
                count += 1
            elif ch not in " \t":
                has_params = True
    return count + 1 if has_params else 0


def _is_hidden_def(entry: SubnameType) -> bool:
    text = entry if isinstance(entry, str) else entry[-1]
    if not text.startswith("def "):
        return False
    name = text[len("def ") :].split("(", 1)[0]
    return name.startswith("_") and name not in ("_is",) and name != "__init__"


def get_names_tree(tree: ast.Module) -> dict[str, set[SubnameType]]:
    # Get class tree.
    names_tree: dict[str, set[SubnameType]] = {}
    for node in tree.body:
        subnames: set[SubnameType] = set()
        # Raw function definitions seen so far in this class, keyed by short
        # name, in source order. Used to resolve which definition a
        # `property(getter, setter)` / `staticmethod(func)` wrapper refers
        # to without depending on `set` iteration order, which is randomized
        # per-process and previously made this lookup nondeterministic.
        functions_by_name: dict[str, list[str]] = {}
        node_name = None
        if isinstance(node, ast.ClassDef):
            # Skip `object_` as it's just a reference to `object`,
            # which is implied by default.
            bases = [b.id for b in node.bases if isinstance(b, ast.Name) and b.id not in ("_object", "object")]
            bases_str = f"({', '.join(bases)})" if bases else ""
            node_name = f"class {node.name}{bases_str}:"

            for subnode in node.body:
                subname = None

                if isinstance(subnode, ast.AnnAssign):
                    target = subnode.target
                    assert isinstance(target, ast.Name)
                    subname = target.id

                elif isinstance(subnode, ast.FunctionDef):
                    subname = get_function_node_name(subnode)

                elif isinstance(subnode, ast.Assign):
                    targets = subnode.targets
                    if not len(targets) == 1 or not isinstance(target := targets[0], ast.Name):
                        continue
                    subname_ = target.id

                    if subname_.startswith(("_", "thisown")):
                        continue

                    value = subnode.value
                    if not isinstance(value, ast.Call):
                        subname = subname_
                    else:
                        # Catching wrappers like:
                        # - `matrix = property(matrix_getter)`
                        # - `matrix = property(matrix_getter, matrix_setter)`
                        # - `operation_str = staticmethod(operation_str)`
                        func = value.func
                        if not isinstance(func, ast.Name) or ((func_id := func.id) not in ("property", "staticmethod")):
                            continue
                        args = [arg.id for arg in value.args if isinstance(arg, ast.Name)]
                        len_args = len(args)
                        if len_args in (1, 2):

                            def claim_function(name: str, prefer_min_arity: bool) -> Union[str, None]:
                                candidates = functions_by_name.get(name)
                                if not candidates:
                                    return None
                                picked = (min if prefer_min_arity else max)(candidates, key=_count_params)
                                candidates.remove(picked)
                                subnames.discard(picked)
                                return picked

                            # `args` preserves declaration order: the first distinct name is the
                            # getter (or the sole wrapped function for `staticmethod`), the
                            # second, when present, is the setter (e.g. `description =
                            # property(description, description)` only names one distinct
                            # function and is claimed once, same as before). Resolving by
                            # position, and preferring the lower-arity definition for the
                            # getter, disambiguates getter/setter pairs that share a name,
                            # instead of picking whichever same-named definition a
                            # hash-ordered lookup happened to yield first.
                            distinct_names = list(dict.fromkeys(args))
                            wrapped_function = None
                            for i, name in enumerate(distinct_names):
                                found = claim_function(name, prefer_min_arity=(i == 0))
                                assert found is not None, f"Could not resolve wrapped function {name!r}."
                                wrapped_function = found

                            # TODO: sort it out in wrapper.py
                            # There's one annoying case in Element.product
                            # when property is overriding existing function, without using it.
                            # We should probably just exclude that function from the wrapper.
                            overridden_candidates = functions_by_name.get(subname_)
                            if overridden_candidates:
                                subnames.discard(overridden_candidates.pop(0))

                            if len_args == 2:
                                # Has both getter and setter, can be defined as a simple attribute.
                                subname = subname_
                            elif len_args == 1:
                                if func_id == "property":
                                    # Has just getter, read-only, need to define it using a wrapper.
                                    subname = (f"@{func_id}", f"def {subname_}(self): ...")
                                elif func_id == "staticmethod":
                                    assert wrapped_function is not None
                                    subname = (f"@{func_id}", f"def {subname_}({wrapped_function.split('(')[1]}")
                                else:
                                    assert_never(func_id)
                            else:
                                assert_never(len_args)
                        else:
                            attr_args = [
                                arg
                                for arg in value.args
                                if isinstance(arg, ast.Attribute)
                                and isinstance(arg.value, ast.Name)
                                and arg.value.id == "_ifcopenshell_wrapper"
                            ]
                            assert len(attr_args) == 2
                            subname = subname_

                if subname is not None:
                    subnames.add(subname)
                    text = subname if isinstance(subname, str) else subname[-1]
                    if text.startswith("def "):
                        functions_by_name.setdefault(text[len("def ") :].split("(", 1)[0], []).append(text)

            # Function definitions that are still underscore-prefixed at this point
            # were never claimed by a `property()`/`staticmethod()` wrapper above,
            # so they're genuinely private and can be hidden from the output.
            subnames = {s for s in subnames if not _is_hidden_def(s)}
            if not subnames:
                node_name += " ..."

        elif isinstance(node, ast.FunctionDef):
            if node.name.startswith("_"):
                continue
            node_name = get_function_node_name(node)
            assert isinstance(node_name, str)

        elif isinstance(node, ast.Assign):
            targets = node.targets
            if not len(targets) == 1 or not isinstance(target := targets[0], ast.Name):
                continue
            node_name = target.id

        elif isinstance(node, ast.AnnAssign):
            target = node.target
            assert isinstance(target, ast.Name)
            node_name = target.id

        if node_name is not None:
            names_tree[node_name] = subnames

    return names_tree


def get_names_tree_lines(tree: ast.Module) -> list[str]:
    names_tree = get_names_tree(tree)

    # Convert names tree to lines.
    lines: list[str] = []
    indent = " " * 4

    def subname_sort(subname: SubnameType) -> str:
        if isinstance(subname, str):
            if subname.startswith("def "):
                return subname.split("(")[0].removeprefix("def ")
            return subname
        return subname_sort(subname[1])

    for name, subnames in sorted(names_tree.items(), key=lambda x: x[0]):
        lines.append(name)
        for subname in sorted(subnames, key=subname_sort):
            subitems = (subname,) if isinstance(subname, str) else subname
            for item in subitems:
                lines.append(f"{indent}{item}")

    return lines


def main() -> None:
    package = Path(__file__).parent.parent.parent
    stub_path = package / "ifcopenshell_wrapper.pyi"
    wrapper_path = package / "ifcopenshell_wrapper.py"

    # Parse files
    stub_tree = ast.parse(stub_path.read_text())
    wrapper_tree = ast.parse(wrapper_path.read_text())

    # Extract class names
    stub_classes = get_names_tree_lines(stub_tree)
    wrapper_classes = get_names_tree_lines(wrapper_tree)

    # Use difflib to create a unified diff of class names
    diff = difflib.unified_diff(
        stub_classes,
        wrapper_classes,
        fromfile="stub.pyi classes",
        tofile="wrapper.py classes",
        lineterm="",
        n=10,
    )
    diff = list(diff)

    format_diff(diff)
    diff_no_header = diff[2:]
    added = len([l for l in diff_no_header if l.startswith("+")])
    removed = len([l for l in diff_no_header if l.startswith("-")])

    if added or removed:
        print(f"Added lines: {added}")
        print(f"Removed lines: {removed}")
        raise Exception("Found discrepancies between stub and wrapper.")
    else:
        print(f"All good, no discrepancies between stub and wrapper. 🎉🎉")


if __name__ == "__main__":
    main()
