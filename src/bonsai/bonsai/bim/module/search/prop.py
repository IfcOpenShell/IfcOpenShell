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
from typing import TYPE_CHECKING, Literal, get_args


def get_element_key(self: "BIMSearchProperties", context: bpy.types.Context) -> list[tuple[str, str, str]]:
    if not SelectSimilarData.is_loaded:
        SelectSimilarData.load()
    return SelectSimilarData.data["element_key"]


def get_colourscheme_key(self: "BIMSearchProperties", context: bpy.types.Context) -> list[tuple[str, str, str]]:
    if not ColourByPropertyData.is_loaded:
        ColourByPropertyData.load()
    return ColourByPropertyData.data["colourscheme_key"]


def get_saved_searches(self: "BIMSearchProperties", context: bpy.types.Context) -> list[tuple[str, str, str]]:
    if not SearchData.is_loaded:
        SearchData.load()
    return SearchData.data["saved_searches"]


def get_saved_colourschemes(self: "BIMSearchProperties", context: bpy.types.Context) -> list[tuple[str, str, str]]:
    if not ColourByPropertyData.is_loaded:
        ColourByPropertyData.load()
    return ColourByPropertyData.data["saved_colourschemes"]


def update_is_filter_item_selected(self: "BIMFilterItem", context: bpy.types.Context) -> None:
    if self.is_selected:
        for obj in self.unselected_objects:
            assert obj.obj
            obj.obj.select_set(True)
        self.unselected_objects.clear()
        return

    props = tool.Search.get_search_props()
    for obj in context.selected_objects:
        element = tool.Ifc.get_entity(obj)
        if props.filter_type == "CLASS":
            if element and element.is_a() == self.name:
                obj.select_set(False)
                new = self.unselected_objects.add()
                new.obj = obj
        else:
            if not element:
                continue
            container = tool.Spatial.get_container(element)
            if (container and container.Name == self.name) or (not container and self.name == "None"):
                obj.select_set(False)
                new = self.unselected_objects.add()
                new.obj = obj


def update_show_flat_colours(self: "BIMSearchProperties", context: bpy.types.Context) -> None:
    space = tool.Blender.get_view3d_space()
    assert space
    if self.show_flat_colours:
        space.shading.light = "FLAT"
        space.shading.color_type = "OBJECT"
        space.shading.show_object_outline = True
        space.shading.show_cavity = True
    else:
        space.shading.type = "SOLID"
        space.shading.light = "STUDIO"
        space.shading.show_object_outline = True
        space.shading.show_cavity = False


class BIMFilterItem(PropertyGroup):
    is_selected: BoolProperty(name="Is Selected", default=True, update=update_is_filter_item_selected)
    total: IntProperty(name="Total")
    unselected_objects: CollectionProperty(type=ObjProperty, name="Unfiltered Objects")

    if TYPE_CHECKING:
        is_selected: bool
        total: int
        unselected_objects: bpy.types.bpy_prop_collection_idprop[ObjProperty]


class BIMColour(PropertyGroup):
    total: IntProperty(name="Total")
    colour: FloatVectorProperty(name="Colour", subtype="COLOR", default=(1, 0, 0), min=0.0, max=1.0)

    if TYPE_CHECKING:
        total: int
        colour: tuple[float, float, float]


FilterType = Literal["CLASS", "CONTAINER"]


class BIMSearchProperties(PropertyGroup):
    element_key: EnumProperty(items=get_element_key, name="Element Key")
    filter_query: StringProperty(name="Filter Query")
    filter_groups: CollectionProperty(type=BIMFilterGroup, name="Filter Groups")
    facet: EnumProperty(
        name="Facet",
        items=[
            ("entity", "Class", "Search by IFC class.\n\nExample: 'IfcWall'.", "FILE_3D", 0),
            (
                "attribute",
                "Attribute",
                "Search by IFC class attribute value.\n\nExample values: 'Name', 'Cube'.",
                "COPY_ID",
                1,
            ),
            (
                "property",
                "Property",
                "Search by Pset property value.\n\n"
                "Example values: 'Pset_WallCommon', 'FireRating', 'equal to', '2HR'.",
                "PROPERTIES",
                2,
            ),
            (
                "material",
                "Material",
                "Search by material name.\n\n"
                "Example: 'concrete'\n"
                "(to select all elements with material named 'concrete').",
                "MATERIAL",
                3,
            ),
            (
                "classification",
                "Classification",
                "Search by classification references.\n\n"
                "Example: 'MyReference'\n"
                "(to select all elements that have classification reference with Id 'MyReference').",
                "OUTLINER",
                4,
            ),
            (
                "location",
                "Location",
                "Search by spatial element.\n\n"
                "Example: 'My Storey'\n"
                "(to select all elements contained in 'My Storey' spatial element).",
                "PACKAGE",
                5,
            ),
            (
                "type",
                "Type",
                "Search by element type.\n\n"
                "Example: 'BaseType'\n(to select all elements that have element type named 'BaseType').",
                "FILE_VOLUME",
                6,
            ),
            (
                "group",
                "Group",
                "Search by IfcGroup name.\n\n"
                "Example: 'MyGroup'\n(to select all elements that are assigned to IfcGroup named 'MyGroup').",
                "OUTLINER_COLLECTION",
                7,
            ),
            (
                "parent",
                "Parent",
                "Search by parent element.\n\n"
                "Example: 'My Building'\n"
                "(to select all children elements of 'My Building').",
                "FILE_PARENT",
                8,
            ),
            (
                "query",
                "Query",
                "Search elements by special queries.\n\n"
                "Example values: 'types.count', '0' (to select all elements that have 0 occurrences).",
                "POINTCLOUD_DATA",
                9,
            ),
            ("instance", "GlobalId", "Search entity by guid.\n\nExample: '2W83_qKWvEGgeo5v66dTxG'.", "GRIP", 10),
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

    # Ideally those should be props on operators, but if we move them to operators,
    # then there's no way for suboperator to select/deselect all displayed items.
    filter_type: EnumProperty(name="Filter Type", items=[(i, i, "") for i in get_args(FilterType)])
    filter_items: CollectionProperty(type=BIMFilterItem, name="Filter Classes")
    filter_items_index: IntProperty(name="Filter Classes Index")

    show_flat_colours: BoolProperty(
        name="Flat Colours",
        description="Toggle flat shading in the active viewport.",
        default=False,
        update=update_show_flat_colours,
    )

    if TYPE_CHECKING:
        element_key: str
        filter_query: str
        filter_groups: bpy.types.bpy_prop_collection_idprop[BIMFilterGroup]
        facet: str
        saved_searches: str
        saved_colourschemes: str
        colourscheme_key: str
        colourscheme_query: str
        palette: str
        min_mode: Literal["AUTO", "MANUAL"]
        max_mode: Literal["AUTO", "MANUAL"]
        min_value: float
        max_value: float
        colourscheme: bpy.types.bpy_prop_collection_idprop[BIMColour]
        active_colourscheme_index: int
        filter_type: FilterType
        filter_items: bpy.types.bpy_prop_collection_idprop[BIMFilterItem]
        filter_items_index: int
        show_flat_colours: bool
