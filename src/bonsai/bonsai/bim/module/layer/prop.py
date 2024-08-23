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


class Layer(PropertyGroup):
    name: StringProperty(name="Name")
    ifc_definition_id: IntProperty(name="IFC Definition ID")


class BIMLayerProperties(PropertyGroup):
    layer_attributes: CollectionProperty(name="Layer Attributes", type=Attribute)
    active_layer_id: IntProperty(name="Active Layer Id")
    layers: CollectionProperty(name="Layers", type=Layer)
    active_layer_index: IntProperty(name="Active Layer Index")
    is_editing: BoolProperty(name="Is Editing", default=False)
