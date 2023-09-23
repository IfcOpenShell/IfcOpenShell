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
from ifcopenshell import util
from ifcopenshell.util.selector import Selector
import blenderbim.tool as tool
from blenderbim.bim.prop import ObjProperty, StrProperty
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
            if (container and container.Name == self.name) or (not container and self.name== "None"):
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


class BIMFacet(PropertyGroup):
    name: StringProperty(name="Name")
    pset: StringProperty(name="Pset")
    value: StringProperty(name="Value")
    type: StringProperty(name="Type")
    comparison: StringProperty(name="Comparison")


class BIMFilterGroup(PropertyGroup):
    filters: CollectionProperty(type=BIMFacet, name="filters")


class BIMColour(PropertyGroup):
    name: StringProperty(name="Name")
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
            ("query", "Query", "", "POINTCLOUD_DATA", 7),
            ("instance", "GlobalId", "", "GRIP", 8),
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


def load_sub_options(self, context):
    if self.selector not in ["IfcClass"]:
        self.load_option = "sub_options"
        load_selection_options(self, context)


def load_selection_options(self, context):
    ifc = IfcStore.file
    load_option = self.load_option
    op = getattr(self, load_option)
    op.clear()
    options = []

    if load_option == "options":
        self.sub_options.clear()
        if self.selector == "IFC Class":
            options = get_classes(self, "IfcElement")
            options.append(("IfcSpace", "IfcSpace", ""))
        elif self.selector == "IfcSpatialElement":
            options = get_classes(self, "IfcSpatialElement")
        elif self.selector == "IfcElementType":
            options = get_classes(self, "IfcElementType")
        elif self.selector == "GlobalId":
            return
        elif self.selector == "IfcPropertySet":
            psets = Selector.parse(ifc, ".IfcPropertySet")
            options = set([o.Name for o in psets])
        elif self.selector == "Attribute":
            attributes = ["GlobalId", "Name", "Description", "ObjectType", "Tag", "PredefinedType"]
            for a in attributes:
                options.append((a, a, ""))

    elif load_option == "sub_options":
        if self.selector in ["IfcSpatialElement", "IfcElementType"]:
            active_option = self.active_option.split(": ")[1]
            options = Selector.parse(ifc, f".{active_option}")

        elif self.selector == "IfcPropertySet":
            options = set()
            active_pset = self.active_option.split(": ")[1]
            psets_in_file = Selector.parse(ifc, f'.IfcPropertySet[Name="{active_pset}"]')
            for pset in psets_in_file:
                for prop in pset.HasProperties:
                    options.add(prop.Name)

    for index, option in enumerate(options):
        new = op.add()
        if self.selector in ["IfcSpatialElement", "IfcElementType"]:
            if self.load_option == "sub_options":
                new.name = f"{index}: {option.Name}"
                new.global_id = option.GlobalId
            else:
                new.name = f"{index}: {option[0]}"
        elif self.selector == "IfcPropertySet":
            new.name = f"{index}: {option}"
        else:
            new.name = f"{index}: {option[0]}"
    self.load_option = "options"


def load_spatial_elements(self, context):
    ifc = IfcStore.file
    col_items = Selector.parse(ifc, f".{self.selected_spatial_element}")
    collection = getattr(self, "sub_spatial_elements", None)
    collection.clear()
    for index, c in enumerate(col_items):
        new = collection.add()
        new.name = f"{index}-{c.Name}"


class SearchCollection(PropertyGroup):
    name: StringProperty()
    long_name: StringProperty()
    global_id: StringProperty()
    query: StringProperty()


class IfcSelector:
    and_or: EnumProperty(
        items=[(i, i, i) for i in ["and", "or"]],
    )
    negation: BoolProperty(name="not")
    comparison: EnumProperty(
        items=[
            ("=", "equal to", ""),
            ("*=", "contains", ""),
            (">=", "greater than or equal to", ""),
            ("<=", "lesser than or equal to", ""),
            (">", "greater than", ""),
            ("<", "less than", ""),
        ],
    )
    load_option: StringProperty(
        default="options", description="controls whether or not options or sub_options are loaded"
    )
    options: CollectionProperty(type=SearchCollection)
    active_option: StringProperty(update=load_sub_options)
    sub_options: CollectionProperty(type=SearchCollection)
    active_sub_option: StringProperty()
    value: StringProperty(description="generic 'value' that can be used in multiple scenarios")


class SearchQueryFilter(PropertyGroup, IfcSelector):
    selector: EnumProperty(
        items=[(i, i, i) for i in ["-", "IfcPropertySet", "Attribute"]],
        name="Filter selection by",
        update=load_selection_options,
        default="-",
    )


class SearchQuery(PropertyGroup, IfcSelector):
    filters: CollectionProperty(type=SearchQueryFilter)
    selector: EnumProperty(
        items=[(i, i, i) for i in ["-", "IFC Class", "IfcSpatialElement", "IfcElementType", "GlobalId"]],
        name="Selector type",
        update=load_selection_options,
        default="-",
    )


class SearchQueryGroup(PropertyGroup, IfcSelector):
    queries: CollectionProperty(type=SearchQuery)


class IfcSelectorProperties(PropertyGroup, IfcSelector):
    groups: CollectionProperty(type=SearchQueryGroup)
    selector_query_syntax: StringProperty()

    query_library: CollectionProperty(type=SearchCollection)
    active_query: StringProperty()

    active_query: StringProperty()
    manual_override: BoolProperty(default=False, description="Toggle to allow manual typing of query-syntax")
