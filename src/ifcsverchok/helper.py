# IfcSverchok - IFC Sverchok extension
# Copyright (C) 2020, 2021, 2022 Dion Moult <dion@thinkmoult.com>
#
# This file is part of IfcSverchok.
#
# IfcSverchok is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcSverchok is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with IfcSverchok.  If not, see <http://www.gnu.org/licenses/>.

import bpy
import ifcopenshell
import sverchok.core.sockets
from sverchok.data_structure import zip_long_repeat
from typing import Any, Union, TypeVar

T_socket = TypeVar("T_socket", bound=sverchok.core.sockets.SvSocketCommon)

ifc_files: dict[str, ifcopenshell.file] = {}


class SvIfcCore:
    sv_input_names: list[str]

    def process(self) -> None:
        """Process inputs from `self.sv_input_names` and call `process_ifc()`.

        For `process()` inputs are supposed to be double nested.
        E.g. file input should have type `list[list[ifcopenshell.file]]`.

        Similarly, outputs should also be double nested,
        so they can be easily passed as inputs to other nodes.
        """
        sv_inputs_nested = []
        for name in self.sv_input_names:
            sv_inputs_nested.append(self.inputs[name].sv_get())
        for sv_input_nested in zip_long_repeat(*sv_inputs_nested):
            for sv_input in zip_long_repeat(*sv_input_nested):
                sv_input = list(sv_input)
                self.process_ifc(*sv_input)

    def process_ifc(self, *args: Any, **kwargs: Any) -> None:
        raise NotImplementedError


def get_selected_nodes() -> list[bpy.types.Node]:
    """Get nodes selected in the currently opened editor.

    Mainly for debugging.
    """
    screen = bpy.context.screen
    assert screen
    area = next(a for a in screen.areas if a.type == "NODE_EDITOR")
    space = area.spaces.active
    assert isinstance(space, bpy.types.SpaceNodeEditor)
    node_tree = space.node_tree
    assert node_tree
    return [n for n in node_tree.nodes if n.select]


def create_socket(
    inputs_or_outputs: Union[bpy.types.NodeInputs, bpy.types.NodeOutputs],
    name: str,
    *,
    description: str = "",
    data_type: str = "",
    prop_name: str = "",
    socket_type: type[T_socket] = sverchok.core.sockets.SvStringsSocket,
) -> T_socket:
    socket = inputs_or_outputs.new(socket_type.bl_idname, name)
    assert isinstance(socket, socket_type)

    if data_type:
        data_type = f"Type: `{data_type}`."
    description = "\n\n".join(filter(None, [description, data_type]))
    socket.description = description

    if prop_name:
        socket.prop_name = prop_name
    return socket
