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

"""High level IFC authoring and editing functions

Authoring, editing, and deleting IFC data requires a detailed understanding of
the rules of the IFC schema. This API module provides simple to use authoring
functions that hide this complexity from you. Things like managing differences
between IFC versions, tracking owernship changes, or cleaning up after orphaned
relationships are all handled automatically.

If you're new to IFC authoring, start by looking at the following APIs:

- See :func:`ifcopenshell.api.project.create_file` to create a new IFC.
- See :func:`ifcopenshell.api.root.create_entity` to create new entities, like
  the mandatory IfcProject, and then an IfcSite, IfcWall, etc.
- See :func:`ifcopenshell.api.aggregate.assign_object` to create a spatial
  hierarchy.
- See :func:`ifcopenshell.api.spatial.assign_container` to place physical
  elements (e.g. walls) inside spatial elements (e.g. building storeys).

Also see how to `create a simple model from scratch
<https://docs.ifcopenshell.org/ifcopenshell-python/code_examples.html#create-a-simple-model-from-scratch>`_.
"""

import json
import numpy
import inspect
import importlib
import ifcopenshell
from typing import Callable, Any, Optional
from functools import partial


pre_listeners: dict[str, dict] = {}
post_listeners: dict[str, dict] = {}


def renamed_arguments_deprecation(
    usecase_path: str, settings: dict, arguments_remapped: dict[str, str]
) -> tuple[str, dict]:
    for prev_argument, new_argument in arguments_remapped.items():
        if prev_argument in settings:
            print(
                f"WARNING. `{prev_argument}` argument is deprecated for API method "
                f'"{usecase_path}" and should be replaced with `{new_argument}`.'
            )
            settings = settings | {new_argument: settings[prev_argument]}
            settings.pop(prev_argument)
    return (usecase_path, settings)


# Example item:
# "group.add_group": partial(
#     renamed_arguments_deprecation, arguments_remapped={"Name": "name", "Description": "description"}
# ),
ARGUMENTS_DEPRECATION: dict[str, Callable[[str, dict[str, Any]], tuple[str, dict[str, Any]]]] = {}


CACHED_USECASE_CLASSES: dict[str, Callable] = {}
CACHED_USECASES: dict[str, Callable] = {}


def run(
    usecase_path: str,
    ifc_file: Optional[ifcopenshell.file] = None,
    should_run_listeners: bool = True,
    **settings: Any,
) -> Any:
    usecase_function = CACHED_USECASES.get(usecase_path)
    if not usecase_function:
        importlib.import_module(f"ifcopenshell.api.{usecase_path}")
        module, usecase = usecase_path.split(".")
        usecase_function = getattr(getattr(ifcopenshell.api, module), usecase)
        CACHED_USECASES[usecase_path] = usecase_function
    if ifc_file:
        return usecase_function(ifc_file, should_run_listeners=should_run_listeners, **settings)
    return usecase_function(should_run_listeners=should_run_listeners, **settings)

    if should_run_listeners:
        for listener in pre_listeners.get(usecase_path, {}).values():
            listener(usecase_path, ifc_file, settings)

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
    import collections

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


def serialise_settings(settings):
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
        else:
            try:
                vcs_settings[key] = str(value)
            except:
                vcs_settings[key] = "n/a"
    try:
        return json.dumps(vcs_settings)
    except:
        return str(vcs_settings)


def wrap_usecase(usecase_path, usecase):
    """Wraps an API function in pre/post listeners."""

    def wrapper(*args, should_run_listeners: bool = True, **settings):
        ifc_file = args[0] if args else None
        nonlocal usecase_path
        if should_run_listeners:
            listeners = list(pre_listeners.get(usecase_path, {}).values())
            listeners += pre_listeners.get("*", {}).values()
            for listener in listeners:
                listener(usecase_path, ifc_file, settings)

        # see #4531
        if usecase_path in ARGUMENTS_DEPRECATION:
            usecase_path, settings = ARGUMENTS_DEPRECATION[usecase_path](usecase_path, settings)

        try:
            result = usecase(*args, **settings)
        except TypeError as e:
            if not e.args[0].startswith(f"{usecase.__name__}()"):
                # signature errors typically start with function name
                # e.g. "TypeError: edit_library() got an unexpected keyword argument 'test'"
                # otherwise it's an error inside api call and we shouldn't get in the way
                raise e
            msg = (
                f"Incorrect function arguments provided for {usecase_path}\n{str(e)}. "
                f"You specified args {args} and settings {settings}\n\n"
                f"Correct signature is {inspect.signature(usecase)}\n"
                f"See help(ifcopenshell.api.{usecase_path}) for documentation."
            )
            raise TypeError(msg) from e

        if should_run_listeners:
            listeners = list(post_listeners.get(usecase_path, {}).values())
            listeners += post_listeners.get("*", {}).values()
            for listener in listeners:
                listener(usecase_path, ifc_file, settings)

        return result

    wrapper.__signature__ = inspect.signature(usecase)
    wrapper.__doc__ = usecase.__doc__
    wrapper.__name__ = usecase_path
    return wrapper


def wrap_usecases(path, name):
    """This developer feature wraps an API module's usecases with listeners."""
    import sys
    import pkgutil

    module_name = name.split(".")[-1]
    module = sys.modules[name]
    for loader, usecase_name, is_pkg in pkgutil.iter_modules(path):
        # We may not be able to get the usecase if we are missing a dependency.
        usecase = getattr(module, usecase_name, None)
        if callable(usecase):
            usecase_path = f"{module_name}.{usecase_name}"
            setattr(module, usecase_name, wrap_usecase(usecase_path, usecase))
