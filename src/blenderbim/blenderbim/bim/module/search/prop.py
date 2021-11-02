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
import blenderbim.tool as tool
from blenderbim.bim.prop import ObjProperty
from bpy.types import PropertyGroup
from . import ui, prop, operator
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


def update_is_selected(self, context):
    if self.is_selected:
        for obj in self.unselected_objects:
            obj.obj.select_set(True)
        self.unselected_objects.clear()
    else:
        for obj in context.selected_objects:
            element = tool.Ifc.get_entity(obj)
            if element and element.is_a() == self.name:
                obj.select_set(False)
                new = self.unselected_objects.add()
                new.obj = obj


class BIMFilterClasses(PropertyGroup):
    name: StringProperty(name="Name")
    is_selected: BoolProperty(name="Is Selected", default=True, update=update_is_selected)
    total: IntProperty(name="Total") 
    unselected_objects: CollectionProperty(type=ObjProperty, name="Unfiltered Objects")


class BIMSearchProperties(PropertyGroup):
    should_use_regex: BoolProperty(name="Search With Regex", default=False)
    should_ignorecase: BoolProperty(name="Search Ignoring Case", default=True)
    global_id: StringProperty(name="GlobalId")
    ifc_class: StringProperty(name="IFC Class")
    search_attribute_name: StringProperty(name="Search Attribute Name")
    search_attribute_value: StringProperty(name="Search Attribute Value")
    search_pset_name: StringProperty(name="Search Pset Name")
    search_prop_name: StringProperty(name="Search Prop Name")
    search_pset_value: StringProperty(name="Search Pset Value")
    filter_classes: CollectionProperty(type=BIMFilterClasses, name="Filter Classes")
    filter_classes_index: IntProperty(name="Filter Classes Index")
