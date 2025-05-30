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
    if node_name.startswith("_") and node_name not in ("_is",):
        return None
    args = [a.arg for a in node.args.args]
    if node.args.vararg:
        args.append("*args")

    node_name = f"def {node.name}"
    node_name = f"{node_name}({', '.join(args)}): ..."

    decorators = tuple(f"@{d.id}" for d in node.decorator_list if isinstance(d, ast.Name))
    if len(decorators) == 1:
        return decorators + (node_name,)
    return node_name


def get_names_tree_lines(tree: ast.Module) -> list[str]:
    # Get class tree.
    names_tree: dict[str, set[SubnameType]] = {}
    for node in tree.body:
        subnames: set[SubnameType] = set()
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

                            def find_method_by_name(name: str) -> Union[str, None]:
                                function_def = f"def {name}("
                                return next(
                                    (
                                        func_
                                        for func_ in subnames
                                        if isinstance(func_, str) and func_.startswith(function_def)
                                    ),
                                    None,
                                )

                            # Use `set` for cases like `description = property(description, description)`.
                            wrapped_function = None
                            for arg in set(args):
                                assert (wrapped_function := find_method_by_name(arg))
                                subnames.remove(wrapped_function)

                            # TODO: sort it out in wrapper.py
                            # There's one annoying case in Element.product
                            # when property is overriding existing function, without using it.
                            # We should probably just exclude that function from the wrapper.
                            overridden_name = find_method_by_name(subname_)
                            if overridden_name:
                                subnames.remove(overridden_name)

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
