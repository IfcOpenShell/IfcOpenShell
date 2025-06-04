# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of Bonsai.
#
# Bonsai is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Bonsai is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Bonsai.  If not, see <http://www.gnu.org/licenses/>.

import bpy
import bonsai.tool as tool
from bonsai.bim.prop import StrProperty, Attribute
from bpy.types import PropertyGroup
from bpy.props import (
    PointerProperty,
    StringProperty,
    EnumProperty,
    BoolProperty,
    IntProperty,
    FloatProperty,
    FloatVectorProperty,
    CollectionProperty,
)
from typing import TYPE_CHECKING


def update_layer_property(self: "Layer", context: bpy.types.Context, *, property: str) -> None:
    # TODO: make use of those attributes in Bonsai somehow?
    layer = tool.Ifc.get().by_id(self.ifc_definition_id)
    setattr(layer, f"Layer{property.capitalize()}", getattr(self, property))


class Layer(PropertyGroup):
    name: StringProperty(name="Name")
    ifc_definition_id: IntProperty(name="IFC Definition ID")
    with_style: BoolProperty(description="Whether it's IfcPresentationLayerWithStyle.", default=False)
    on: BoolProperty(
        name="Layer Visibility",
        description="Currently has no effect in Bonsai.",
        update=lambda self, context: update_layer_property(self, context, property="on"),
    )
    frozen: BoolProperty(
        name="Layer Frozen",
        description="Currently has no effect in Bonsai.",
        update=lambda self, context: update_layer_property(self, context, property="frozen"),
    )
    blocked: BoolProperty(
        name="Layer Blocked",
        description="Currently has not effect in Bonsai",
        update=lambda self, context: update_layer_property(self, context, property="blocked"),
    )

    if TYPE_CHECKING:
        name: str
        ifc_definition_id: int
        with_style: bool
        on: bool
        frozen: bool
        blocked: bool


class BIMLayerProperties(PropertyGroup):
    layer_attributes: CollectionProperty(name="Layer Attributes", type=Attribute)
    active_layer_id: IntProperty(name="Active Layer Id")
    layers: CollectionProperty(name="Layers", type=Layer)
    active_layer_index: IntProperty(name="Active Layer Index")
    is_editing: BoolProperty(name="Is Editing", default=False)
    layer_type: EnumProperty(
        name="Presentation Layer Type",
        description="Presentation layer type to add",
        items=(
            ("IfcPresentationLayerAssignment", "IfcPresentationLayerAssignment", ""),
            ("IfcPresentationLayerWithStyle", "IfcPresentationLayerWithStyle", ""),
        ),
        default="IfcPresentationLayerAssignment",
    )

    if TYPE_CHECKING:
        layer_attributes: bpy.types.bpy_prop_collection_idprop[Attribute]
        active_layer_id: int
        layers: bpy.types.bpy_prop_collection_idprop[Layer]
        active_layer_index: int
        is_editing: bool
        layer_type: str
