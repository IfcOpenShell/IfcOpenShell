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


def update_active_reference_index(self, context):
    LibrariesData.is_loaded = False


class LibraryReference(PropertyGroup):
    name: StringProperty(name="Name")
    ifc_definition_id: IntProperty(name="IFC Definition ID")


class BIMLibraryProperties(PropertyGroup):
    editing_mode: StringProperty(name="Editing Mode")
    library_attributes: CollectionProperty(name="Library Attributes", type=Attribute)
    active_library_id: IntProperty(name="Active Library Id")
    reference_attributes: CollectionProperty(name="Library Attributes", type=Attribute)
    active_reference_id: IntProperty(name="Active Reference Id")
    references: CollectionProperty(type=LibraryReference, name="References")
    active_reference_index: IntProperty(name="Active Reference Index", update=update_active_reference_index)
