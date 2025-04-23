# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
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
from bonsai.bim.module.library.data import LibrariesData
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
from typing import TYPE_CHECKING, Literal


def update_active_reference_index(self, context):
    LibrariesData.is_loaded = False


def update_library_element_name(self: "LibraryReference", context: bpy.types.Context):
    ifc_file = tool.Ifc.get()
    element = ifc_file.by_id(self.ifc_definition_id)
    previous_name = element.Name
    if self.name == previous_name:
        return
    element.Name = self.name
    LibrariesData.is_loaded = False


class LibraryReference(PropertyGroup):
    name: StringProperty(name="Name", update=update_library_element_name)
    ifc_definition_id: IntProperty(name="IFC Definition ID")

    if TYPE_CHECKING:
        name: str
        ifc_definition_id: int


class BIMLibraryProperties(PropertyGroup):
    editing_mode: EnumProperty(
        name="Editing Mode",
        items=(
            ("NONE", "NONE", ""),
            ("LIBRARY", "LIBRARY", ""),
            ("REFERENCES", "REFERENCES", ""),
            ("REFERENCE", "REFERENCE", ""),
        ),
        default="NONE",
    )
    library_attributes: CollectionProperty(name="Library Attributes", type=Attribute)
    active_library_id: IntProperty(name="Active Library Id")
    reference_attributes: CollectionProperty(name="Library Attributes", type=Attribute)
    active_reference_id: IntProperty(name="Active Reference Id")
    references: CollectionProperty(type=LibraryReference, name="References")
    active_reference_index: IntProperty(name="Active Reference Index", update=update_active_reference_index)

    if TYPE_CHECKING:
        editing_mode: Literal["NONE", "LIBRARY", "REFERENCES", "REFERENCE"]
        library_attributes: bpy.types.bpy_prop_collection_idprop[Attribute]
        active_library_id: int
        reference_attributes: bpy.types.bpy_prop_collection_idprop[Attribute]
        active_reference_id: int
        references: bpy.types.bpy_prop_collection_idprop[LibraryReference]
        active_reference_index: int
