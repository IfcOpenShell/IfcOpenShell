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

import os
import bpy
import ifcopenshell.util.element
import ifcopenshell.util.placement
from bonsai.bim.module.project.data import ProjectData
from bonsai.bim.ifc import IfcStore
from bonsai.bim.prop import StrProperty, ObjProperty
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


def get_export_schema(self: "BIMProjectProperties", context: bpy.types.Context) -> list[tuple[str, str, str]]:
    if not ProjectData.is_loaded:
        ProjectData.load()
    return ProjectData.data["export_schema"]


def update_export_schema(self: "BIMProjectProperties", context: bpy.types.Context) -> None:
    # Avoid breaking empty enum.
    self["template_file"] = 0


def get_template_file(self: "BIMProjectProperties", context: bpy.types.Context) -> list[tuple[str, str, str]]:
    if not ProjectData.is_loaded:
        ProjectData.load()
    return ProjectData.data["template_file"][self.export_schema]


def get_library_file(self: "BIMProjectProperties", context: bpy.types.Context) -> list[tuple[str, str, str]]:
    if not ProjectData.is_loaded:
        ProjectData.load()
    return ProjectData.data["library_file"]


def update_library_file(self: "BIMProjectProperties", context: bpy.types.Context) -> None:
    if self.library_file != "0":
        bpy.ops.bim.select_library_file(
            filepath=os.path.join(bpy.context.scene.BIMProperties.data_dir, "libraries", self.library_file)
        )


def update_filter_mode(self: "BIMProjectProperties", context: bpy.types.Context) -> None:
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
    name: StringProperty(
        name="Name",
        description="Filepath to linked .ifc file, stored in posix format (could be relative to .blend file, not to .ifc)",
    )
    is_loaded: BoolProperty(name="Is Loaded", default=False)
    is_selectable: BoolProperty(name="Is Selectable", default=True)
    is_wireframe: BoolProperty(name="Is Wireframe", default=False)
    is_hidden: BoolProperty(name="Is Hidden", default=False)
    empty_handle: PointerProperty(
        name="Empty Object Handle",
        description="We use empty object handle to allow simple manipulations with a linked model (moving, scaling, rotating)",
        type=bpy.types.Object,
    )


class EditedObj(PropertyGroup):
    obj: PointerProperty(type=bpy.types.Object)


class BIMProjectProperties(PropertyGroup):
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
    geometry_library: bpy.props.EnumProperty(
        items=[
            ("opencascade", "OpenCASCADE", "Best for stability and accuracy"),
            ("cgal", "CGAL", "Best for speed"),
            ("cgal-simple", "CGAL Simple", "CGAL without booleans"),
            ("hybrid-cgal-simple-opencascade", "Hybrid CGAL-OCC", "First CGAL then fallback to OCC"),
        ],
        name="Geometry Library",
        default="hybrid-cgal-simple-opencascade",
    )
    should_use_cpu_multiprocessing: BoolProperty(name="CPU Multiprocessing", default=True)
    should_merge_materials_by_colour: BoolProperty(name="Merge Materials by Colour", default=False)
    should_stream: BoolProperty(name="Stream Data From IFC-SPF (Only for advanced users)", default=False)
    should_load_geometry: BoolProperty(name="Load Geometry", default=True)
    should_clean_mesh: BoolProperty(name="Clean Meshes", default=False)
    should_cache: BoolProperty(name="Cache", default=False)
    deflection_tolerance: FloatProperty(name="Deflection Tolerance", default=0.001)
    angular_tolerance: FloatProperty(name="Angular Tolerance", default=0.5)
    void_limit: IntProperty(
        name="Void Limit",
        default=30,
        description="Maxium number of openings that object can have. If object has more openings, it will be loaded without openings",
    )
    distance_limit: FloatProperty(name="Distance Limit", default=1000, subtype="DISTANCE")
    false_origin_mode: bpy.props.EnumProperty(
        items=[
            (
                "AUTOMATIC",
                "Automatic",
                "An automatic false origin will be detected from geometry with large coordinates",
            ),
            ("MANUAL", "Manual", "You can specify the false origin coordinates"),
            ("DISABLED", "Disabled", "The model in original local coordinates will be shown as is"),
        ],
        name="False Origin Mode",
        default="AUTOMATIC",
    )
    false_origin: StringProperty(
        name="False Origin",
        description="False origin in project units that the Blender origin will correlate to",
        default="0,0,0",
    )
    project_north: StringProperty(
        name="Angle to Grid North",
        description="The angle (postive is anticlockwise) pointing to grid north relative to project north",
        default="0",
    )
    element_limit_mode: bpy.props.EnumProperty(
        items=[
            ("UNLIMITED", "Load Everything", "Load all elements"),
            ("RANGE", "Load Subset of Elements", "Only load the first N elements"),
        ],
        name="Element limit",
        default="UNLIMITED",
    )
    element_offset: IntProperty(name="Element Offset", default=0)
    element_limit: IntProperty(name="Element Offset", default=30000)
    load_indexed_maps: BoolProperty(
        name="Load Indexed Maps",
        description="Load indexed maps (UV and color maps)",
        default=True,
    )
    should_disable_undo_on_save: BoolProperty(
        name="Disable Undo When Saving (Faster saves, no undo for you!)", default=False
    )
    links: CollectionProperty(name="Links", type=Link)
    active_link_index: IntProperty(name="Active Link Index")
    export_schema: EnumProperty(items=get_export_schema, name="IFC Schema", update=update_export_schema)
    template_file: EnumProperty(items=get_template_file, name="Template File")
    library_file: EnumProperty(items=get_library_file, name="Library File", update=update_library_file)
    use_relative_project_path: BoolProperty(name="Use Relative Project Path", default=False)
    queried_obj: bpy.props.PointerProperty(type=bpy.types.Object)
    queried_obj_root: bpy.props.PointerProperty(type=bpy.types.Object)
    clipping_planes: bpy.props.CollectionProperty(type=ObjProperty)
    clipping_planes_active: bpy.props.IntProperty(min=0, default=0, max=5)
    edited_objs: bpy.props.CollectionProperty(type=EditedObj)

    @property
    def clipping_planes_objs(self):
        return list({cp.obj for cp in self.clipping_planes if cp.obj})

    def get_library_element_index(self, lib_element):
        return next((i for i in range(len(self.library_elements)) if self.library_elements[i] == lib_element))


class MeasureToolSettings(PropertyGroup):
    measurement_type_items = [
        ("SINGLE", "SINGLE", "Single", "FIXED_SIZE", 1),
        ("POLYLINE", "POLYLINE", "Polyline", "DRIVER_ROTATIONAL_DIFFERENCE", 2),
        ("AREA", "AREA", "Area", "OUTLINER_DATA_LIGHTPROBE", 3),
    ]

    measurement_type: bpy.props.EnumProperty(items=measurement_type_items, default="POLYLINE")
