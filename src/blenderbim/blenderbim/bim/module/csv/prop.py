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
from blenderbim.bim.module.search.prop import BIMFilterGroup
from blenderbim.bim.prop import StrProperty
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


class CsvAttribute(PropertyGroup):
    name: StringProperty(name="Query", default="class")
    header: StringProperty(name="Header Value", default="IFC Class")
    sort: EnumProperty(items=[("NONE", "None", ""), ("ASC", "Ascending", ""), ("DESC", "Descending", "")])


class CsvProperties(PropertyGroup):
    csv_ifc_file: StringProperty(default="", name="IFC File")
    ifc_selector: StringProperty(default="", name="IFC Selector")
    filter_groups: CollectionProperty(type=BIMFilterGroup, name="Filter Groups")
    facet: EnumProperty(
        items=[
            ("entity", "Class", "", "FILE_3D", 0),
            ("attribute", "Attribute", "", "COPY_ID", 1),
            ("property", "Property", "", "PROPERTIES", 2),
            ("material", "Material", "", "MATERIAL", 3),
            ("classification", "Classification", "", "OUTLINER", 4),
            ("location", "Location", "", "PACKAGE", 5),
            ("type", "Type", "", "FILE_VOLUME", 6),
            ("instance", "GlobalId", "", "GRIP", 7),
        ],
    )
    csv_attributes: CollectionProperty(name="CSV Attributes", type=CsvAttribute)
    should_preserve_existing: BoolProperty(default=False, name="Preserve Existing")
    include_global_id: BoolProperty(default=True, name="Include GlobalId")
    null_value: StringProperty(default="N/A", name="Null Value")
    true_value: StringProperty(default="YES", name="True Value")
    false_value: StringProperty(default="NO", name="False Value")
    csv_delimiter: EnumProperty(
        items=[
            (";", ";", ""),
            (",", ",", ""),
            (".", ".", ""),
            ("CUSTOM", "Custom", ""),
        ],
        name="IFC CSV Delimiter",
        default=",",
    )
    format: EnumProperty(
        items=[
            ("csv", "csv", ""),
            ("xlsx", "xlsx", ""),
            ("ods", "ods", ""),
        ],
        name="Output format",
        default="csv",
    )
    csv_custom_delimiter: StringProperty(default="", name="Custom Delimiter")
    should_show_settings: BoolProperty(default=False, name="Show Settings")
    should_show_sort: BoolProperty(default=False, name="Show Sort")
    should_load_from_memory: BoolProperty(default=False, name="Load from Memory")
