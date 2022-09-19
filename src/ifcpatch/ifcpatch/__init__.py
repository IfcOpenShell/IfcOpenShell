#!/usr/bin/env python3

# IfcPatch - IFC patching utiliy
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
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

import ifcopenshell
import logging
import os
import typing
import inspect
import collections
import importlib


def execute(args):
    if "log" in args:
        logging.basicConfig(filename=args["log"], filemode="a", level=logging.DEBUG)
    logger = logging.getLogger("IFCPatch")
    ifc_file = args["input"]
    recipes = getattr(__import__("ifcpatch.recipes.{}".format(args["recipe"])), "recipes")
    recipe = getattr(recipes, args["recipe"])
    if recipe.Patcher.__init__.__doc__ is not None:
        patcher = recipe.Patcher(args["input"], ifc_file, logger, *args["arguments"])
    else:
        patcher = recipe.Patcher(args["input"], ifc_file, logger, args["arguments"])
    patcher.patch()
    output = getattr(patcher, "file_patched", patcher.file)
    if isinstance(output, str):
        with open(args["output"], "w") as text_file:
            text_file.write(output)
    return output


def write(output, filepath):
    if isinstance(output, str):
        with open(filepath, "w") as text_file:
            text_file.write(output)
    else:
        output.write(filepath)


def extract_docs(
    submodule_name: str, cls_name: str, method_name: str = "__init__", boilerplate_args: typing.Iterable[str] = None
):
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


def _extract_docs(cls, method_name, boilerplate_args):
    inputs = collections.OrderedDict()
    method = getattr(cls, method_name)
    docs = {"class": cls}
    if boilerplate_args is None:
        boilerplate_args = []

    signature = inspect.signature(method)
    for name, parameter in signature.parameters.items():
        if name == "self" or name in boilerplate_args:
            continue
        inputs[name] = {"name": name}
        if isinstance(parameter.default, (str, float, int, bool)):
            inputs[name]["default"] = parameter.default

    type_hints = typing.get_type_hints(method)
    for input_name in inputs.keys():
        type_hint = type_hints.get(input_name, None)
        if type_hint is None:  # The argument is not type-hinted. (Or hinted to None ??)
            continue
        if isinstance(type_hint, typing._UnionGenericAlias):
            inputs[input_name]["type"] = [t.__name__ for t in typing.get_args(type_hint)]
        else:
            inputs[input_name]["type"] = type_hint.__name__

    description = ""
    doc = method.__doc__
    if doc is not None:
        for i, line in enumerate(doc.split("\n")):
            line = line.strip()
            if i == 0:
                docs["name"] = line
            elif line.startswith(":return:"):
                docs["output"] = {"name": line.split(":")[2].strip(), "description": line.split(":")[3].strip()}
            elif line.startswith(":param"):
                param_name = line.split(":")[1].strip().replace("param ", "")
                if param_name in inputs:
                    inputs[param_name]["description"] = line.split(":")[2].strip()
            elif i == 2:
                description += line
            elif i > 2:
                description += "\n" + line

        docs["description"] = description.strip()
    docs["inputs"] = inputs
    return docs
