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


pre_listeners = {}
post_listeners = {}


def run(usecase_path, ifc_file=None, should_run_listeners=True, **settings):
    if should_run_listeners:
        for listener in pre_listeners.get(usecase_path, {}).values():
            listener(usecase_path, ifc_file, settings)

    def serialise_entity_instance(entity):
        return {"cast_type": "entity_instance", "value": entity.id(), "Name": getattr(entity, "Name", None)}

    vcs_settings = settings.copy()
    for key, value in settings.items():
        if isinstance(value, ifcopenshell.entity_instance):
            vcs_settings[key] = serialise_entity_instance(value)
        elif isinstance(value, numpy.ndarray):
            vcs_settings[key] = {"cast_type": "ndarray", "value": value.tolist()}
        elif isinstance(value, list) and value and isinstance(value[0], ifcopenshell.entity_instance):
            vcs_settings[key] = [serialise_entity_instance(i) for i in value]
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

    importlib.import_module(f"ifcopenshell.api.{usecase_path}")
    module, usecase = usecase_path.split(".")
    usecase_class = getattr(getattr(getattr(ifcopenshell.api, module), usecase), "Usecase")

    if ifc_file:
        result = usecase_class(ifc_file, **settings).execute()
    else:
        result = usecase_class(**settings).execute()

    if should_run_listeners:
        for listener in post_listeners.get(usecase_path, {}).values():
            listener(usecase_path, ifc_file, settings)

    return result


def add_pre_listener(usecase_path, name, callback):
    """Add a pre listener

    :param usecase_path: string, ifcopenshell api use case path
    :param name: string, name of listener
    :param callback: callback function
    """
    pre_listeners.setdefault(usecase_path, {})[name] = callback


def add_post_listener(usecase_path, name, callback):
    """Add a post listener

    :param usecase_path: string, ifcopenshell api use case path
    :param name: string, name of listener
    :param callback: callback function
    """
    post_listeners.setdefault(usecase_path, {})[name] = callback


def remove_pre_listener(usecase_path, name, callback):
    """Remove a pre listener

    :param usecase_path: string, ifcopenshell api use case path
    :param name: string, name of listener
    :param callback: callback function
    """
    pre_listeners.get(usecase_path, {}).pop(name, None)


def remove_post_listener(usecase_path, name, callback):
    """Remove a post listener

    :param usecase_path: string, ifcopenshell api use case path
    :param name: string, name of listener
    :param callback: callback function
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
