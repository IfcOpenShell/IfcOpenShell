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


class LibraryElement(PropertyGroup):
    name: StringProperty(name="Name")
    ifc_definition_id: IntProperty(name="IFC Definition ID")
    is_declared: BoolProperty(name="Is Declared", default=False)
    is_appended: BoolProperty(name="Is Appended", default=False)


class BIMProjectProperties(PropertyGroup):
    is_authoring: BoolProperty(name="Enable Authoring Mode", default=True)
    is_editing: BoolProperty(name="Is Editing", default=False)
    mvd: StringProperty(name="MVD")
    author_name: StringProperty(name="Author")
    author_email: StringProperty(name="Author Email")
    organisation_name: StringProperty(name="Organisation")
    organisation_email: StringProperty(name="Organisation Email")
    authorisation: StringProperty(name="Authoriser")
    active_library_element: StringProperty(name="Enable Authoring Mode", default="")
    library_breadcrumb: CollectionProperty(name="Library Breadcrumb", type=StrProperty)
    library_elements: CollectionProperty(name="Library Elements", type=LibraryElement)
    active_library_element_index: IntProperty(name="Active Library Element Index")

    def get_library_element_index(self, lib_element):
        return next((i for i in range(len(self.library_elements)) if self.library_elements[i] == lib_element))
