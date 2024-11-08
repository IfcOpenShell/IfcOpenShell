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
import bonsai.tool as tool
import ifcopenshell.util.schema
from bonsai.bim.prop import ObjProperty, BIMFilterGroup
from bonsai.bim.module.search.data import SearchData, ColourByPropertyData, SelectSimilarData
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


def get_element_key(self, context):
    if not SelectSimilarData.is_loaded:
        SelectSimilarData.load()
    return SelectSimilarData.data["element_key"]


def get_colourscheme_key(self, context):
    if not ColourByPropertyData.is_loaded:
        ColourByPropertyData.load()
    return ColourByPropertyData.data["colourscheme_key"]


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


def update_show_flat_colours(self, context):
    if self.show_flat_colours:
        space = tool.Blender.get_view3d_space()
        space.shading.light = "FLAT"
        space.shading.color_type = "OBJECT"
        space.shading.show_object_outline = True
        space.shading.show_cavity = True
    else:
        space = tool.Blender.get_view3d_space()
        space.shading.type = "SOLID"
        space.shading.light = "STUDIO"
        space.shading.show_object_outline = True
        space.shading.show_cavity = False


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
    colourscheme_key: EnumProperty(items=get_colourscheme_key, name="Colourscheme Key")
    colourscheme_query: StringProperty(name="Colourscheme Query", default="class")
    palette: EnumProperty(
        items=[
            ("tab10", "Default (Qualitative)", "10 Contrasting colours to distinguish categories"),
            ("paired", "Paired (Qualitative)", "12 Contrasting colour pairs to distinguish categories"),
            ("rocket", "Rocket (Quantitative - Sequential)", "A sequential range from black to red to white"),
            ("mako", "Mako (Quantitative - Sequential)", "A sequential range from black to blue to white"),
            (
                "coolwarm",
                "CoolWarm (Quantitative - Diverging)",
                "A diverging linear range from blue to red with white in the middle",
            ),
            (
                "spectral",
                "Spectral (Quantitative - Diverging)",
                "A diverging spectral range from red to blue with white in the middle",
            ),
        ],
        name="Palette",
    )
    min_mode: EnumProperty(
        items=[
            ("AUTO", "Automatic", "Automatically determine the minimum value"),
            ("MANUAL", "Manual", "Manually specify the minimum value"),
        ],
        name="Min Mode",
    )
    max_mode: EnumProperty(
        items=[
            ("AUTO", "Automatic", "Automatically determine the maximum value"),
            ("MANUAL", "Manual", "Manually specify the maximum value"),
        ],
        name="Max Mode",
    )
    min_value: FloatProperty(name="Min Value", default=0)
    max_value: FloatProperty(name="Max Value", default=100)
    colourscheme: CollectionProperty(type=BIMColour)
    active_colourscheme_index: IntProperty(name="Active Colourscheme Index")
    filter_type: StringProperty(name="Filter Type")
    filter_classes: CollectionProperty(type=BIMFilterClasses, name="Filter Classes")
    filter_classes_index: IntProperty(name="Filter Classes Index")
    filter_container: CollectionProperty(type=BIMFilterBuildingStoreys, name="Filter Level")
    filter_container_index: IntProperty(name="Filter Level Index")
    show_flat_colours: BoolProperty(name="Flat Colours", default=False, update=update_show_flat_colours)


def get_classes(self, ifc_product):
    declaration = tool.Ifc.schema().declaration_by_name(ifc_product)
    declarations = ifcopenshell.util.schema.get_subtypes(declaration)
    names = [d.name() for d in declarations]
    return [(c, c, "") for c in sorted(names)]
