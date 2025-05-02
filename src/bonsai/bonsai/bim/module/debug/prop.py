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
from typing import TYPE_CHECKING, Literal, get_args

DisplayType = Literal["BOUNDS", "WIRE", "SOLID", "TEXTURED"]


class BIMDebugProperties(PropertyGroup):
    step_id: IntProperty(name="STEP ID")
    number_of_polygons: IntProperty(name="Number of Polygons", min=0)
    percentile_of_polygons: IntProperty(name="Percentile of Polygons", min=0, max=100, default=90, subtype="PERCENTAGE")
    active_step_id: IntProperty(name="STEP ID", default=1, soft_min=1)
    step_id_breadcrumb: CollectionProperty(name="STEP ID Breadcrumb", type=StrProperty)
    attributes: CollectionProperty(name="Attributes", type=Attribute)
    inverse_attributes: CollectionProperty(name="Inverse Attributes", type=Attribute)
    inverse_references: CollectionProperty(name="Inverse References", type=Attribute)
    express_file: StringProperty(name="Express File")
    display_type: EnumProperty(
        items=[(display_type, display_type.capitalize(), "") for display_type in get_args(DisplayType)],
        name="Display Type",
        default="BOUNDS",
    )
    ifc_class_purge: StringProperty(name="Unused Elements IFC Class", default="")
    package_name: StringProperty(name="Package Name", default="")

    if TYPE_CHECKING:
        step_id: int
        number_of_polygons: int
        percentile_of_polygons: int
        active_step_id: int
        step_id_breadcrumb: bpy.types.bpy_prop_collection_idprop[StrProperty]
        attributes: bpy.types.bpy_prop_collection_idprop[Attribute]
        inverse_attributes: bpy.types.bpy_prop_collection_idprop[Attribute]
        inverse_references: bpy.types.bpy_prop_collection_idprop[Attribute]
        express_file: str
        display_type: str
        ifc_class_purge: str
        package_name: str
