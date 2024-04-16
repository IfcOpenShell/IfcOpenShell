# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
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

"""High level user-oriented IFC authoring capabilities"""

import json
import numpy
import importlib
import ifcopenshell
import ifcopenshell.api
from typing import Callable, Any, Optional
from functools import partial


pre_listeners = {}
post_listeners = {}


def batching_argument_deprecation(
    usecase_path: str, settings: dict, prev_argument: str, new_argument: str, replace_usecase: Optional[str] = None
) -> tuple[str, dict]:
    if replace_usecase is not None:
        print(f"WARNING. `{usecase_path}` api method is deprecated and should be replaced with `{replace_usecase}`.")

    if prev_argument in settings:
        print(
            f"WARNING. `{prev_argument}` argument is deprecated for API method "
            f'"{usecase_path}" and should be replaced with `{new_argument}`.'
        )
        settings = settings | {new_argument: [settings[prev_argument]]}
        settings.pop(prev_argument)
    return (replace_usecase or usecase_path, settings)


ARGUMENTS_DEPRECATION = {
    "spatial.assign_container": partial(
        batching_argument_deprecation, prev_argument="product", new_argument="products"
    ),
    "spatial.unassign_container": partial(
        batching_argument_deprecation, prev_argument="product", new_argument="products"
    ),
    "group.unassign_group": partial(batching_argument_deprecation, prev_argument="product", new_argument="products"),
    "aggregate.assign_object": partial(batching_argument_deprecation, prev_argument="product", new_argument="products"),
    "aggregate.unassign_object": partial(
        batching_argument_deprecation, prev_argument="product", new_argument="products"
    ),
    "layer.assign_layer": partial(batching_argument_deprecation, prev_argument="item", new_argument="items"),
    "layer.unassign_layer": partial(batching_argument_deprecation, prev_argument="item", new_argument="items"),
    "spatial.remove_container": partial(
        batching_argument_deprecation,
        prev_argument="product",
        new_argument="products",
        replace_usecase="spatial.unassign_container",
    ),
    "nest.assign_object": partial(
        batching_argument_deprecation, prev_argument="related_object", new_argument="related_objects"
    ),
    "nest.unassign_object": partial(
        batching_argument_deprecation, prev_argument="related_object", new_argument="related_objects"
    ),
    "type.assign_type": partial(
        batching_argument_deprecation, prev_argument="related_object", new_argument="related_objects"
    ),
    "type.unassign_type": partial(
        batching_argument_deprecation, prev_argument="related_object", new_argument="related_objects"
    ),
    "system.assign_system": partial(batching_argument_deprecation, prev_argument="product", new_argument="products"),
    "system.unassign_system": partial(batching_argument_deprecation, prev_argument="product", new_argument="products"),
    "material.assign_material": partial(
        batching_argument_deprecation, prev_argument="product", new_argument="products"
    ),
    "material.unassign_material": partial(
        batching_argument_deprecation, prev_argument="product", new_argument="products"
    ),
    "classification.add_reference": partial(
        batching_argument_deprecation, prev_argument="product", new_argument="products"
    ),
    "classification.remove_reference": partial(
        batching_argument_deprecation, prev_argument="product", new_argument="products"
    ),
    "library.assign_reference": partial(
        batching_argument_deprecation, prev_argument="product", new_argument="products"
    ),
    "library.unassign_reference": partial(
        batching_argument_deprecation, prev_argument="product", new_argument="products"
    ),
    "document.assign_document": partial(
        batching_argument_deprecation, prev_argument="product", new_argument="products"
    ),
    "document.unassign_document": partial(
        batching_argument_deprecation, prev_argument="product", new_argument="products"
    ),
    "spatial.reference_structure": partial(
        batching_argument_deprecation, prev_argument="product", new_argument="products"
    ),
    "spatial.dereference_structure": partial(
        batching_argument_deprecation, prev_argument="product", new_argument="products"
    ),
    "constraint.assign_constraint": partial(
        batching_argument_deprecation, prev_argument="product", new_argument="products"
    ),
    "constraint.unassign_constraint": partial(
        batching_argument_deprecation, prev_argument="product", new_argument="products"
    ),
}


CACHED_USECASE_CLASSES = dict()


def run(
    usecase_path: str,
    ifc_file: Optional[ifcopenshell.file] = None,
    should_run_listeners=True,
    **settings: Any,
) -> Any:
    if should_run_listeners:
        for listener in pre_listeners.get(usecase_path, {}).values():
            listener(usecase_path, ifc_file, settings)

    # see #4531
    if usecase_path in ARGUMENTS_DEPRECATION:
        usecase_path, settings = ARGUMENTS_DEPRECATION[usecase_path](usecase_path, settings)

    # TODO: settings serialization for client-server systems
    # def serialise_entity_instance(entity):
    #     return {"cast_type": "entity_instance", "value": entity.id(), "Name": getattr(entity, "Name", None)}
    # vcs_settings = settings.copy()
    # for key, value in settings.items():
    #     if isinstance(value, ifcopenshell.entity_instance):
    #         vcs_settings[key] = serialise_entity_instance(value)
    #     elif isinstance(value, numpy.ndarray):
    #         vcs_settings[key] = {"cast_type": "ndarray", "value": value.tolist()}
    #     elif isinstance(value, list) and value and isinstance(value[0], ifcopenshell.entity_instance):
    #         vcs_settings[key] = [serialise_entity_instance(i) for i in value]
    if "add_representation" in usecase_path:
        pass
        # print(usecase_path, "{ ... settings too complex right now ... }")
    elif "owner." in usecase_path:
        pass
    else:
        pass
        # print(vcs_settings)
        # try:
        #    print(usecase_path, json.dumps(vcs_settings))
        # except:
        #    print(usecase_path, vcs_settings)

    usecase_class = CACHED_USECASE_CLASSES.get(usecase_path)
    if usecase_class is None:
        importlib.import_module(f"ifcopenshell.api.{usecase_path}")
        module, usecase = usecase_path.split(".")
        usecase_class = getattr(getattr(getattr(ifcopenshell.api, module), usecase), "Usecase")
        CACHED_USECASE_CLASSES[usecase_path] = usecase_class

    if ifc_file:
        result = usecase_class(ifc_file, **settings).execute()
    else:
        result = usecase_class(**settings).execute()

    if should_run_listeners:
        for listener in post_listeners.get(usecase_path, {}).values():
            listener(usecase_path, ifc_file, settings)

    return result


def add_pre_listener(usecase_path: str, name: str, callback: Callable[[str, ifcopenshell.file, dict], None]) -> None:
    """Add a pre listener

    :param usecase_path: string, ifcopenshell api use case path
    :param name: string, name of listener
    :param callback: callback function with 3 arguments: `usecase_path`, `ifc_file`, `settings`
    """
    pre_listeners.setdefault(usecase_path, {})[name] = callback


def add_post_listener(usecase_path: str, name: str, callback: Callable[[str, ifcopenshell.file, dict], None]) -> None:
    """Add a post listener

    :param usecase_path: string, ifcopenshell api use case path
    :param name: string, name of listener
    :param callback: callback function with 3 arguments: `usecase_path`, `ifc_file`, `settings`
    """
    post_listeners.setdefault(usecase_path, {})[name] = callback


def remove_pre_listener(usecase_path: str, name: str, callback: Callable[[str, ifcopenshell.file, dict], None]) -> None:
    """Remove a pre listener

    :param usecase_path: string, ifcopenshell api use case path
    :param name: string, name of listener
    :param callback: callback function with 3 arguments: `usecase_path`, `ifc_file`, `settings`
    """
    pre_listeners.get(usecase_path, {}).pop(name, None)


def remove_post_listener(
    usecase_path: str, name: str, callback: Callable[[str, ifcopenshell.file, dict], None]
) -> None:
    """Remove a post listener

    :param usecase_path: string, ifcopenshell api use case path
    :param name: string, name of listener
    :param callback: callback function with 3 arguments: `usecase_path`, `ifc_file`, `settings`
    """
    post_listeners.get(usecase_path, {}).pop(name, None)


def remove_all_listeners():
    pre_listeners.clear()
    post_listeners.clear()


def extract_docs(module, usecase):
    import typing
    import inspect
    import collections

    results = []

    inputs = collections.OrderedDict()

    function_init = getattr(getattr(ifcopenshell.api, module), usecase).Usecase.__init__
    function_execute = getattr(getattr(ifcopenshell.api, module), usecase).Usecase.execute

    node_data = {"module": module, "usecase": usecase}

    signature = inspect.signature(function_init)
    for name, parameter in signature.parameters.items():
        if name == "self":
            continue
        inputs[name] = {"name": name}
        if isinstance(parameter.default, (str, float, int, bool)):
            inputs[name]["default"] = parameter.default

    type_hints = typing.get_type_hints(function_init)
    for name, socket_data in inputs.items():
        type_hint = type_hints[name]
        if isinstance(type_hint, typing._UnionGenericAlias):
            inputs[name]["type"] = [t.__name__ for t in typing.get_args(type_hint)]
        else:
            inputs[name]["type"] = type_hint.__name__

    description = ""
    for i, line in enumerate(function_init.__doc__.split("\n")):
        line = line.strip()
        if i == 0:
            node_data["name"] = line
        elif line.startswith(":return:"):
            node_data["output"] = {"name": line.split(":")[2].strip(), "description": line.split(":")[3].strip()}
        elif line.startswith(":param"):
            param_name = line.split(":")[1].strip().replace("param ", "")
            inputs[param_name]["description"] = line.split(":")[2].strip()
        elif i >= 2:
            description += line

    if "output" in node_data:
        node_data["output"]["type"] = typing.get_type_hints(function_execute)["return"].__name__
    node_data["description"] = description.strip()
    node_data["inputs"] = inputs
    return node_data
