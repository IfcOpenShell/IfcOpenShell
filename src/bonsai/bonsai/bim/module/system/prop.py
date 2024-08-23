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
from bonsai.bim.module.system.data import SystemData
import bonsai.bim.module.system.decorator as decorator
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


def get_system_class(self, context):
    if not SystemData.is_loaded:
        SystemData.load()
    return SystemData.data["system_class"]


class System(PropertyGroup):
    name: StringProperty(name="Name")
    ifc_class: StringProperty(name="IFC Class")
    ifc_definition_id: IntProperty(name="IFC Definition ID")


class Zone(PropertyGroup):
    name: StringProperty(name="Name")
    ifc_definition_id: IntProperty(name="IFC Definition ID")


def toggle_decorations(self, context):
    toggle = self.should_draw_decorations
    if toggle:
        decorator.SystemDecorator.install(context)
    else:
        decorator.SystemDecorator.uninstall()


class BIMSystemProperties(PropertyGroup):
    system_attributes: CollectionProperty(name="System Attributes", type=Attribute)
    is_editing: BoolProperty(name="Is Editing", default=False)
    is_adding: BoolProperty(name="Is Adding", default=False)
    systems: CollectionProperty(name="Systems", type=System)
    active_system_index: IntProperty(name="Active System Index")
    active_system_id: IntProperty(name="Active System Id")
    edited_system_id: IntProperty(name="Edited System Id")
    system_class: EnumProperty(items=get_system_class, name="Class")
    should_draw_decorations: BoolProperty(
        name="Should Draw Decorations", description="Toggle system decorations", update=toggle_decorations
    )


class BIMZoneProperties(PropertyGroup):
    attributes: CollectionProperty(name="Attributes", type=Attribute)
    is_loaded: BoolProperty(name="Is Loaded", default=False)
    is_editing: IntProperty(name="Is Editing", default=0)
    zones: CollectionProperty(name="Zones", type=Zone)
    active_zone_index: IntProperty(name="Active Zone Index")
