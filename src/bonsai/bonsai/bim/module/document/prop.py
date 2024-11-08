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


class Document(PropertyGroup):
    name: StringProperty(name="Name")
    identification: StringProperty(name="Identification")
    is_information: BoolProperty(name="Is Information")
    ifc_definition_id: IntProperty(name="IFC Definition ID")


class BIMDocumentProperties(PropertyGroup):
    document_attributes: CollectionProperty(name="Document Attributes", type=Attribute)
    active_document_id: IntProperty(name="Active Document Id")
    documents: CollectionProperty(name="Documents", type=Document)
    breadcrumbs: CollectionProperty(name="Breadcrumbs", type=StrProperty)
    active_document_index: IntProperty(name="Active Document Index")
    is_editing: BoolProperty(name="Is Editing", default=False)
