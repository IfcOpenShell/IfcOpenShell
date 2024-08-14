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
from bonsai.bim.module.spatial.data import SpatialData
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


def update_relating_object(self, context):
    def message(self, context):
        self.layout.label(text="Please select a valid IFC Element")

    if self.relating_object:
        self.related_object = None
        if not self.relating_object.BIMObjectProperties.ifc_definition_id:
            context.window_manager.popup_menu(message, title="Invalid Element Selected", icon="INFO")
            self.relating_object = None


def update_related_object(self, context):
    def message(self, context):
        self.layout.label(text="Please select a valid IFC Element")

    if self.related_object:
        self.relating_object = None
        if not self.related_object.BIMObjectProperties.ifc_definition_id:
            context.window_manager.popup_menu(message, title="Invalid Element Selected", icon="INFO")
            self.related_object = None


class BIMObjectAggregateProperties(PropertyGroup):
    is_editing: BoolProperty(name="Is Editing")
    relating_object: PointerProperty(name="Relating Whole", type=bpy.types.Object, update=update_relating_object)
    related_object: PointerProperty(name="Related Part", type=bpy.types.Object, update=update_related_object)
