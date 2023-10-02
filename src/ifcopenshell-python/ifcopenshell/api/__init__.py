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
import os
from pathlib import Path
import importlib
import inspect
from types import ModuleType
from typing import Any, Optional, DefaultDict
from dataclasses import dataclass, field
from collections import defaultdict
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


class ApiCaller:
    """Object containing ifcopenshell.api.run module / action calls, including source signatures and docstrings"""

    def __init__(self):
        self.patch_api()

    def patch_api(self) -> None:
        """Monkey-patches ifcopenshell.api.run calls"""

        actions_to_exclude: list[str] = ["__init__", "settings"]

        @dataclass
        class ApiModule:
            _module: str

            def __post_init__(self):
                self.__name__ = self._module
                self.__qualname__ = self._module
                self.__doc__ = f"IfcOpenShell API module {self._module}"

            def __repr__(self) -> str:
                return f"<class 'ifcopenshell.file.{self._module}'> (patched)"

        @dataclass(slots=True)
        class ApiAction:
            file: ifcopenshell.file
            module: str
            action: str
            __name__: str = ""
            __qualname__: str = ""
            __signature__: inspect.Signature = field(init=False)
            __doc__: str = ""

            def __post_init__(self):
                self.__name__ = self.action
                self.__qualname__ = f"{self.module}.{self.action}"
                self.update_signature()

            def __repr__(self) -> str:
                return f"<class 'ifcopenshell.file.{self.module}.{self.action}'> (patched)"

            def __call__(self, *args, **kwargs) -> Any:
                return ifcopenshell.api.run(f"{self.module}.{self.action}", *args, **kwargs)

            def update_signature(self) -> None:
                try:
                    python_module: ModuleType = importlib.import_module(f"ifcopenshell.api.{self.module}.{self.action}")
                except ModuleNotFoundError:
                    return
                else:
                    self.__doc__ = python_module.Usecase.__init__.__doc__
                    api_signature: inspect.Signature = inspect.signature(python_module.Usecase.__init__)
                    parameters: list[inspect.Parameter] = list(api_signature.parameters.values())
                    if parameters:
                        parameters = parameters[1:]  # discarding self from the signature
                    return_annotation: Any = api_signature.return_annotation
                    self.__signature__ = inspect.signature(self).replace(
                        parameters=parameters, return_annotation=return_annotation
                    )

        api_calls: DefaultDict[str, list[str]] = defaultdict(list)
        ios_dir = Path(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))

        for path in ios_dir.glob("*/*.py"):
            if (action := path.stem) in actions_to_exclude:
                continue
            module = path.parent.name
            api_calls[module].append(action)

        for module, actions in api_calls.items():
            action_functors: dict[str, ApiAction] = {
                action: ApiAction(file=self, module=module, action=action) for action in actions
            }
            api_module = ApiModule(_module=module)
            for action, functor in action_functors.items():
                setattr(api_module, action, functor)
            setattr(self, module, api_module)


if "ifc" not in globals() or not isinstance(globals()["ifc"], ApiCaller):
    ifc = ApiCaller()
