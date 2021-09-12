# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of BlenderBIM Add-on.
#
# BlenderBIM Add-on is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BlenderBIM Add-on is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with BlenderBIM Add-on.  If not, see <http://www.gnu.org/licenses/>.

from blenderbim.bim.prop import StrProperty, Attribute
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


class BIMDebugProperties(PropertyGroup):
    step_id: IntProperty(name="STEP ID")
    number_of_polygons: IntProperty(name="Number of Polygons", min=0)
    active_step_id: IntProperty(name="STEP ID")
    step_id_breadcrumb: CollectionProperty(name="STEP ID Breadcrumb", type=StrProperty)
    attributes: CollectionProperty(name="Attributes", type=Attribute)
    inverse_attributes: CollectionProperty(name="Inverse Attributes", type=Attribute)
    inverse_references: CollectionProperty(name="Inverse References", type=Attribute)
