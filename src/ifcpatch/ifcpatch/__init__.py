#!/usr/bin/env python3

# IfcPatch - IFC patching utiliy
# Copyright (C) 2020, 2021, 2023 Dion Moult <dion@thinkmoult.com>
#
# This file is part of IfcPatch.
#
# IfcPatch is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcPatch is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcPatch.  If not, see <http://www.gnu.org/licenses/>.

import os
import shutil
import sys
import ifcopenshell
import logging
import typing
import inspect
import collections
import importlib
import importlib.util
import re
from pathlib import Path
from typing import Union, Optional, Any, TypedDict
from typing_extensions import NotRequired
from collections.abc import Sequence


__version__ = version = "0.0.0"


class ArgumentsDict(TypedDict):
    recipe: str
    file: NotRequired[ifcopenshell.file]
    input: NotRequired[str]
    log: NotRequired[str]
    arguments: NotRequired[Sequence[Any]]


class BasePatcher:
    def __init__(self, file: ifcopenshell.file, logger: Union[logging.Logger, None]):
        self.file = file
        self.logger = ensure_logger(logger)

    def patch(self) -> None:
        raise NotImplementedError

    def get_output(self) -> Union[ifcopenshell.file, str, None]:
        if hasattr(self, "file_patched"):
            return self.file_patched  # pyright: ignore[reportAttributeAccessIssue]
        return self.file


def ensure_logger(logger: Union[logging.Logger, None] = None) -> logging.Logger:
    if logger is not None:
        return logger
    return logging.getLogger("IFCPatch")


def execute(args: ArgumentsDict) -> Union[ifcopenshell.file, str, None]:
    """Execute a patch recipe

    The details of how the patch recipe is executed depends on the definition of
    the recipe, as well as the arguments passed to the recipe. See the
    documentation for each patch recipe separately to understand more.

    :param args: A dictionary of arguments, corresponding to the parameters
        listed subsequent to this in this docstring.
    :type args: ArgumentsDict
    :param file: An IFC model to apply the patch recipe to.
        Required for most recipes except the ones that require `input`.
    :type file: ifcopenshell.file, optional
    :param input: A filepath to the incoming IFC file.
        Required/supported only for some recipes, see specific recipes descriptions,
        in other cases will be ignored.
    :type input: str, optional
    :param recipe: The name of the recipe. This is the same as the filename of
        the recipe. E.g. "ExtractElements".
    :type recipe: str
    :param log: A filepath to a logfile.
    :type log: str,optional
    :param arguments: A list of zero or more positional arguments, depending on
        the patch recipe. Some patch recipes will require you to specify
        arguments, some won't.
    :type arguments: list
    :return: The result of the patch. This is typically a patched model, either
        as an object or as a string.

    Example:

    .. code:: python

        output = ifcpatch.execute({
            "input": "input.ifc",
            "file": ifcopenshell.open("input.ifc"),
            "recipe": "ExtractElements",
            "arguments": [".IfcWall"],
        })
        ifcpatch.write(output, "output.ifc")
    """
    if "log" in args:
        logging.basicConfig(filename=args["log"], filemode="a", level=logging.DEBUG)
    logger = ensure_logger()
    if recipe_dir := os.environ.get("IFCPATCH_RECIPE_DIR"):
        spec = importlib.util.spec_from_file_location(args["recipe"], os.path.join(recipe_dir, args["recipe"] + ".py"))
        recipe = importlib.util.module_from_spec(spec)
        sys.modules[args["recipe"]] = recipe
        spec.loader.exec_module(recipe)
    else:
        recipe = importlib.import_module(f"ifcpatch.recipes.{args['recipe']}")

    arguments = args.get("arguments", None) or []
    if recipe.Patcher.__init__.__doc__ is not None:
        patcher = recipe.Patcher(args.get("file"), logger, *arguments)
    else:
        patcher = recipe.Patcher(args.get("file"), logger, arguments)
    patcher.patch()
    output = BasePatcher.get_output(patcher)
    return output


def write(output: Union[ifcopenshell.file, str, None], filepath: Union[Path, str]) -> None:
    """Write the output of an IFC patch to a file

    Typically a patch output would be a patched IFC model file object, or as a
    string. This function lets you agnostically write that output to a filepath.

    :param output: The results from ``ifcpatch.execute()`` / ``Patcher.get_output()``
    :param filepath: A filepath to where the results of the patched model should
        be written to.
    :return: None
    """
    if output is None:
        return
    elif isinstance(output, str):
        if os.path.exists(output):
            shutil.move(output, filepath)
        else:
            with open(filepath, "w") as text_file:
                text_file.write(output)
    else:
        output.write(filepath)


def extract_docs(
    submodule_name: str, cls_name: str, method_name: str = "__init__", boilerplate_args: Optional[Sequence[str]] = None
) -> Union["PatcherDoc", None]:
    """Extract class docstrings and method arguments

    :param submodule_name: Submodule from which to extract the class
    :param cls_name: Class from which to extract the docstring and method arguments
    :param method_name: Class Method name from which to extract arguments
    :param boilerplate_args: String iterable containing arguments that shall not be parsed
    """
    spec = importlib.util.spec_from_file_location(
        submodule_name, f"{os.path.dirname(inspect.getabsfile(inspect.currentframe()))}/recipes/{submodule_name}.py"
    )
    submodule = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(submodule)
        try:
            return _extract_docs(getattr(submodule, cls_name), method_name, boilerplate_args)
        except AttributeError as e:
            print(e)
    except ModuleNotFoundError as e:
        print(f"Error : IFCPatch {str(submodule)} could not load because : {str(e)}")


class PatcherDoc(TypedDict):
    class_: type
    description: str
    output: Union[str, None]
    inputs: dict[str, "InputDoc"]


class InputDoc(TypedDict):
    name: str
    description: str
    type: Union[str, list[str]]
    default: NotRequired[Any]
    generic_type: NotRequired[str]
    enum_items: NotRequired[list[str]]
    filter_glob: NotRequired[str]


def _extract_docs(cls: type, method_name: str, boilerplate_args: Union[Sequence[str], None]) -> PatcherDoc:
    inputs: dict[str, InputDoc] = {}
    method = getattr(cls, method_name)
    if boilerplate_args is None:
        boilerplate_args = []

    signature = inspect.signature(method)
    for name, parameter in signature.parameters.items():
        if name == "self" or name in boilerplate_args:
            continue
        input_doc: InputDoc = {"name": name}
        inputs[name] = input_doc
        if isinstance(parameter.default, (str, float, int, bool)):
            input_doc["default"] = parameter.default

    # Parse data from type hints.
    type_hints = typing.get_type_hints(method)
    for input_name in inputs.keys():
        type_hint = type_hints.get(input_name, None)
        if type_hint is None:  # The argument is not type-hinted. (Or hinted to None ??)
            continue

        input_data = inputs[input_name]
        # E.g. list[str].
        if isinstance(type_hint, typing.GenericAlias):
            input_data["generic_type"] = type_hint.__name__
            type_hint = typing.get_args(type_hint)[0]

        if isinstance(type_hint, typing._UnionGenericAlias):
            inputs[input_name]["type"] = [t.__name__ for t in typing.get_args(type_hint)]
        elif type_hint.__name__ == "Literal":
            inputs[input_name]["type"] = "Literal"
            inputs[input_name]["enum_items"] = list(typing.get_args(type_hint))
        else:
            inputs[input_name]["type"] = type_hint.__name__

    # Parse the docstring.
    description = ""
    # `getdoc` instead of `__doc__` for sane indentation.
    doc = inspect.getdoc(method)

    def is_valid_param_name(param_name: str) -> bool:
        assert (
            param_name in inputs
        ), f"Unexpected param name '{param_name}' in {cls.__name__} docstring (missing from signature)."
        return True

    def is_valid_filter_glob(filter_glob: str) -> bool:
        # e.g. '*.ifc;*.ifczip;*.ifcxml'
        if len(filter_glob) < 3:
            return False
        for pattern in filter_glob.split(";"):
            if not re.fullmatch(r"\*\.\w+", pattern):
                return False
        return True

    if doc is None:
        doc_description = ""
        doc_output = None
    else:
        docstring_data = parse_docstring(doc)
        doc_description = docstring_data["description"]
        doc_output = docstring_data["output"]

        for param_name in docstring_data["param"]:
            if not is_valid_param_name(param_name):
                continue
            inputs[param_name]["description"] = docstring_data["param"][param_name]

        for param_name in docstring_data["filter_glob"]:
            if not is_valid_param_name(param_name):
                continue
            filter_glob = docstring_data["filter_glob"][param_name]
            assert is_valid_filter_glob(filter_glob), f"Invalid filter_glob pattern: '{filter_glob}'."
            inputs[param_name]["filter_glob"] = filter_glob

    for param_name in inputs:
        if "description" not in inputs[param_name]:
            inputs[param_name]["description"] = "Undocumented"

    docs = PatcherDoc(
        class_=cls,
        description=doc_description,
        output=doc_output,
        inputs=inputs,
    )
    return docs


class DocstringData(TypedDict):
    name: str
    description: str
    param: dict[str, str]
    filter_glob: dict[str, str]
    output: Union[str, None]


def parse_docstring(docstring: str) -> DocstringData:
    # Keep left indentation to recognize the sections.
    lines = docstring.split("\n")
    result = DocstringData(
        name=lines[0].strip(),
        description="",
        param={},
        filter_glob={},
        output=None,
    )

    current_section = None
    last_param = None

    PREFIXES = ("param", "filter_glob")

    for line in lines[1:]:
        if line.startswith(":"):
            line = line[1:]
            if line.startswith(PREFIXES):
                prefix = line.split(" ")[0]
                current_section = prefix
                match_ = re.match(rf"{prefix}\s+(\w+):\s+(.*)", line)
                assert match_, f"Invalid line: '{line}'."
                param_name, param_desc = match_.groups()
                result[prefix][param_name] = param_desc
                last_param = param_name
                continue
            elif line.startswith("return:"):
                current_section = "output"
                match_ = re.match(r"return:\s+(.*)", line)
                assert match_
                result["output"] = match_.groups()[0]
                continue
            elif line.startswith("type"):
                # Ignore types in favor of signature annotations.
                continue
        elif line.startswith("Example:"):
            # Ignore code example at the end of the docstring.
            break

        # Multiline sections start with indentation.
        if line.startswith(" ") and current_section:
            line = line.lstrip()
            if current_section == "output":
                assert result["output"]
                result["output"] += f"\n{line}"
            elif current_section in PREFIXES:
                assert last_param
                result[current_section][last_param] += f"\n{line}"
            continue

        line = line.lstrip()
        result["description"] += f"\n{line}"
        current_section = None
        last_param = None

    result["description"] = result["description"].strip()

    return result
