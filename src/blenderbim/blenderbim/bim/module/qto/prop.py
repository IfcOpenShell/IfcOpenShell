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

import bpy
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


class BIMQtoProperties(PropertyGroup):
    qto_result: StringProperty(default="", name="Qto Result")
    qto_methods: EnumProperty(
        items=[
            ("HEIGHT", "Height", "Calculate the Z height of an object"),
            ("VOLUME", "Volume", "Calculate the volume of an object"),
            (
                "FORMWORK",
                "Formwork",
                "Calculate the exposed formwork for all bottoms and sides (e.g. for beams and slabs) of one or more objects",
            ),
            (
                "SIDE_FORMWORK",
                "Side Formwork",
                "Calculate the exposed formwork for all sides only (e.g. for columns) of one or more objects",
            ),
            ("NetFootprintArea", "Net footprint area", "Calculate the net footprint area"),
            ("NetRoofprintArea", "Net roofprint area", "Calculate the net roofprint area"),
            ("LateralArea", "Lateral area", "Calculate the lateral area"),
            ("TotalSurfaceArea", "Total surface area", "Calculate the total surface area"),
            ("OpeningArea", "Opening area", "Calculate the opening area"),
            ("GrossTopArea", "Gross top area", "Calculate the gross top area"),
            ("NetTopArea", "Net top area", "Calculate the net top area"),
            ("ProjectedArea", "Projected area", "Calculate the projected area"),
            ("TotalContactArea", "Total contact area", "Get the total contact area"),
            ("ContactArea", "Contact area between two objects", "Get the contact area")
        ],
        name="Qto Methods",
    )
    qto_name: StringProperty(name="Qto Name")
    prop_name: StringProperty(name="Prop Name")
