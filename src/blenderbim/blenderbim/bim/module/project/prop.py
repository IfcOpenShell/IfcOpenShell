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
import ifcopenshell.util.placement
from blenderbim.bim.module.project.data import ProjectData
from blenderbim.bim.ifc import IfcStore
from blenderbim.bim.prop import StrProperty
from bpy.types import PropertyGroup
from bpy.props import (
    PointerProperty,
    BoolProperty,
    CollectionProperty,
    EnumProperty,
    FloatProperty,
    IntProperty,
    StringProperty,
)


def get_export_schema(self, context):
    if not ProjectData.is_loaded:
        ProjectData.load()
    return ProjectData.data["export_schema"]


def get_template_file(self, context):
    if not ProjectData.is_loaded:
        ProjectData.load()
    return ProjectData.data["template_file"]


def update_filter_mode(self, context):
    self.filter_categories.clear()
    if self.filter_mode == "NONE":
        return
    file = IfcStore.get_file()
    if self.filter_mode == "DECOMPOSITION":
        if file.schema == "IFC2X3":
            elements = file.by_type("IfcSpatialStructureElement")
        else:
            elements = file.by_type("IfcSpatialElement")
        elements = [(e, ifcopenshell.util.placement.get_storey_elevation(e)) for e in elements]
        elements = sorted(elements, key=lambda e: e[1])
        for element in elements:
            element = element[0]
            new = self.filter_categories.add()
            new.name = "{}/{}".format(element.is_a(), element.Name or "Unnamed")
            new.ifc_definition_id = element.id()
            new.total_elements = sum([len(r.RelatedElements) for r in element.ContainsElements])
    elif self.filter_mode == "IFC_CLASS":
        for ifc_class in sorted(list({e.is_a() for e in file.by_type("IfcElement")})):
            new = self.filter_categories.add()
            new.name = ifc_class
            new.total_elements = len(file.by_type(ifc_class, include_subtypes=False))
    elif self.filter_mode == "IFC_TYPE":
        for ifc_type in sorted(file.by_type("IfcElementType"), key=lambda e: e.Name or "Unnamed"):
            new = self.filter_categories.add()
            new.name = ifc_type.is_a() + "/" + (ifc_type.Name or "Unnamed")
            new.ifc_definition_id = ifc_type.id()
            new.total_elements = len(ifcopenshell.util.element.get_types(ifc_type))


class LibraryElement(PropertyGroup):
    name: StringProperty(name="Name")
    ifc_definition_id: IntProperty(name="IFC Definition ID")
    is_declared: BoolProperty(name="Is Declared", default=False)
    is_appended: BoolProperty(name="Is Appended", default=False)


class FilterCategory(PropertyGroup):
    name: StringProperty(name="Name")
    ifc_definition_id: IntProperty(name="IFC Definition ID")
    is_selected: BoolProperty(name="Is Selected", default=False)
    total_elements: IntProperty(name="Total Elements")


class Link(PropertyGroup):
    name: StringProperty(name="Name")
    is_loaded: BoolProperty(name="Is Loaded", default=False)
    is_wireframe: BoolProperty(name="Is Wireframe", default=False)
    is_hidden: BoolProperty(name="Is Hidden", default=False)


class BIMProjectProperties(PropertyGroup):
    is_authoring: BoolProperty(name="Enable Authoring Mode", default=True)
    is_editing: BoolProperty(name="Is Editing", default=False)
    is_loading: BoolProperty(name="Is Loading", default=False)
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
    collection_mode: bpy.props.EnumProperty(
        items=[
            ("DECOMPOSITION", "Decomposition", "Collections represent aggregates and spatial containers"),
            ("SPATIAL_DECOMPOSITION", "Spatial Decomposition", "Collections represent spatial containers"),
            ("IFC_CLASS", "IFC Class", "Collections represent IFC class"),
            ("NONE", "None", "No collections are created"),
        ],
        name="Collection Mode",
    )
    filter_mode: bpy.props.EnumProperty(
        items=[
            ("NONE", "None", "No filtering is performed"),
            ("DECOMPOSITION", "Decomposition", "Filter objects by decomposition"),
            ("IFC_CLASS", "IFC Class", "Filter objects by class"),
            ("IFC_TYPE", "IFC Type", "Filter objects by type"),
            ("WHITELIST", "Whitelist", "Filter objects using a custom whitelist query"),
            ("BLACKLIST", "Blacklist", "Filter objects using a custom blacklist query"),
        ],
        name="Filter Mode",
        update=update_filter_mode,
    )
    total_elements: IntProperty(name="Total Elements", default=0)
    filter_categories: CollectionProperty(name="Filter Categories", type=FilterCategory)
    active_filter_category_index: IntProperty(name="Active Filter Category Index")
    filter_query: StringProperty(name="Filter Query")
    should_filter_spatial_elements: BoolProperty(name="Filter Spatial Elements", default=False)
    should_use_cpu_multiprocessing: BoolProperty(name="CPU Multiprocessing", default=True)
    merge_mode: bpy.props.EnumProperty(
        items=[
            ("NONE", "None", "No objects are merged"),
            ("IFC_CLASS", "IFC Class", "One object per IFC class"),
            ("IFC_TYPE", "IFC Type", "One object per IFC construction type"),
            ("MATERIAL", "Material", "One object per material"),
        ],
        name="Merge Mode",
        default="NONE",
    )
    should_merge_materials_by_colour: BoolProperty(name="Merge Materials by Colour", default=False)
    should_use_native_meshes: BoolProperty(name="Native Meshes", default=False)
    should_clean_mesh: BoolProperty(name="Clean Meshes", default=True)
    should_cache: BoolProperty(name="Cache", default=False)
    is_coordinating: BoolProperty(name="For Coordination Only", default=False)
    deflection_tolerance: FloatProperty(name="Deflection Tolerance", default=0.001)
    angular_tolerance: FloatProperty(name="Angular Tolerance", default=0.5)
    distance_limit: FloatProperty(name="Distance Limit", default=1000)
    false_origin: StringProperty(name="False Origin", default="0,0,0")
    element_offset: IntProperty(name="Element Offset", default=0)
    element_limit: IntProperty(name="Element Offset", default=30000)
    should_disable_undo_on_save: BoolProperty(
        name="Disable Undo When Saving (Faster saves, no undo for you!)", default=False
    )
    links: CollectionProperty(name="Links", type=Link)
    active_link_index: IntProperty(name="Active Link Index")
    export_schema: EnumProperty(items=get_export_schema, name="IFC Schema")
    template_file: EnumProperty(items=get_template_file, name="Template File")

    def get_library_element_index(self, lib_element):
        return next((i for i in range(len(self.library_elements)) if self.library_elements[i] == lib_element))
