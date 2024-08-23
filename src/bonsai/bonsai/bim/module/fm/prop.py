# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2023 Dion Moult <dion@thinkmoult.com>
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
from bonsai.bim.module.fm.data import FMData
from bonsai.bim.prop import MultipleFileSelect, StrProperty
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


def get_engine(self, context):
    if not FMData.is_loaded:
        FMData.load()
    return FMData.data["engine"]


class BIMFMProperties(PropertyGroup):
    ifc_files: PointerProperty(type=MultipleFileSelect)
    spreadsheet_files: CollectionProperty(name="Spreadsheets", type=StrProperty)
    should_load_from_memory: BoolProperty(
        default=False,
        name="Load from Memory",
        description="Use IFC file currently loaded in Bonsai",
    )
    engine: EnumProperty(items=get_engine, name="Engine", options=set())
    format: EnumProperty(
        items=[
            ("csv", "csv", ""),
            ("xlsx", "xlsx", ""),
            ("ods", "ods", ""),
        ],
        name="Format",
        default="ods",
        options=set(),
    )
