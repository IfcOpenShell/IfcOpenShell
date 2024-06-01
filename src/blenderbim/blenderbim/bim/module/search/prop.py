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
from ifcopenshell import util
from ifcopenshell.util.selector import Selector
from blenderbim.bim.prop import ObjProperty, StrProperty, BIMFilterGroup
from blenderbim.bim.ifc import IfcStore
from blenderbim.bim.module.search.data import SearchData, ColourByPropertyData, SelectSimilarData
from bpy.types import PropertyGroup
from blenderbim.tool.ifc import Ifc
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


def get_element_key(self, context):
    if not SelectSimilarData.is_loaded:
        SelectSimilarData.load()
    return SelectSimilarData.data["element_key"]


def get_saved_searches(self, context):
    if not SearchData.is_loaded:
        SearchData.load()
    return SearchData.data["saved_searches"]


def get_saved_colourschemes(self, context):
    if not ColourByPropertyData.is_loaded:
        ColourByPropertyData.load()
    return ColourByPropertyData.data["saved_colourschemes"]


def update_is_class_selected(self, context):
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


def update_is_container_selected(self, context):
    if self.is_selected:
        for obj in self.unselected_objects:
            obj.obj.select_set(True)
        self.unselected_objects.clear()
    else:
        for obj in context.selected_objects:
            container = tool.Spatial.get_container(tool.Ifc.get_entity(obj))
            if (container and container.Name == self.name) or (not container and self.name == "None"):
                obj.select_set(False)
                new = self.unselected_objects.add()
                new.obj = obj


class BIMFilterClasses(PropertyGroup):
    name: StringProperty(name="Name")
    is_selected: BoolProperty(name="Is Selected", default=True, update=update_is_class_selected)
    total: IntProperty(name="Total")
    unselected_objects: CollectionProperty(type=ObjProperty, name="Unfiltered Objects")


class BIMFilterBuildingStoreys(PropertyGroup):
    name: StringProperty(name="Name")
    is_selected: BoolProperty(name="Is Level Selected", default=True, update=update_is_container_selected)
    total: IntProperty(name="Total")
    unselected_objects: CollectionProperty(type=ObjProperty, name="Unfiltered Objects")


class BIMColour(PropertyGroup):
    name: StringProperty(name="Name")
    total: IntProperty(name="Total")
    colour: FloatVectorProperty(name="Colour", subtype="COLOR", default=(1, 0, 0), min=0.0, max=1.0)


class BIMSearchProperties(PropertyGroup):
    element_key: EnumProperty(items=get_element_key, name="Element Key")
    filter_query: StringProperty(name="Filter Query")
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
            ("group", "Group", "", "OUTLINER_COLLECTION", 7),
            ("parent", "Parent", "", "FILE_PARENT", 8),
            ("query", "Query", "", "POINTCLOUD_DATA", 9),
            ("instance", "GlobalId", "", "GRIP", 10),
        ],
    )
    saved_searches: EnumProperty(items=get_saved_searches, name="Saved Searches")
    saved_colourschemes: EnumProperty(items=get_saved_colourschemes, name="Saved Colourschemes")
    colourscheme_query: StringProperty(name="Colourscheme Query", default="class")
    colourscheme: CollectionProperty(type=BIMColour)
    active_colourscheme_index: IntProperty(name="Active Colourscheme Index")
    filter_type: StringProperty(name="Filter Type")
    filter_classes: CollectionProperty(type=BIMFilterClasses, name="Filter Classes")
    filter_classes_index: IntProperty(name="Filter Classes Index")
    filter_container: CollectionProperty(type=BIMFilterBuildingStoreys, name="Filter Level")
    filter_container_index: IntProperty(name="Filter Level Index")


def get_classes(self, ifc_product):
    declaration = tool.Ifc.schema().declaration_by_name(ifc_product)
    declarations = util.schema.get_subtypes(declaration)
    names = [d.name() for d in declarations]
    return [(c, c, "") for c in sorted(names)]
