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
import bonsai.tool as tool
import bonsai.bim.helper
from bonsai.bim.module.project.data import ProjectData, ProjectLibraryData
from bonsai.bim.ifc import IfcStore
from bonsai.bim.prop import StrProperty, ObjProperty, Attribute
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
from typing import TYPE_CHECKING, Literal, Union, get_args
from typing_extensions import assert_never


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
        filepath = next(p for p in tool.Blender.get_data_dir_paths("libraries", "*.ifc") if p.name == self.library_file)
        bpy.ops.bim.select_library_file(filepath=filepath.__str__())
        ProjectLibraryData.load()
        props = tool.Project.get_project_props()
        library_file = IfcStore.library_file
        assert library_file
        project_library = next(iter(library_file.by_type("IfcProjectLibrary")), None)
        props.selected_project_library = str(project_library.id()) if project_library else "-"


def update_selected_project_library(self: "BIMProjectProperties", context: bpy.types.Context) -> None:
    # Ensure `.is_declared` up to date.
    tool.Project.update_current_library_page()


def get_project_libaries(self: "BIMProjectProperties", context: bpy.types.Context) -> list[tuple[str, str, str]]:
    if not ProjectLibraryData.is_loaded:
        ProjectLibraryData.load()
    return ProjectLibraryData.data["project_libraries_enum"]


def show_library_tree_update(self: "BIMProjectProperties", context: bpy.types.Context) -> None:
    bpy.ops.bim.refresh_library()


def is_editing_project_library_update(self: "BIMProjectProperties", context: bpy.types.Context) -> None:
    if self.is_editing_project_library:
        library_file = IfcStore.library_file
        assert library_file
        self.editing_project_library_id = int(self.selected_project_library)
        project_library = library_file.by_id(int(self.selected_project_library))
        self.project_library_attributes.clear()
        bonsai.bim.helper.import_attributes2(project_library, self.project_library_attributes)
        self.parent_library = str(tool.Project.get_parent_library(project_library).id())
        ProjectLibraryData.load()  # Show edit icon in enum.
        return

    del self["is_editing_project_library"]
    del self["editing_project_library_id"]
    self.project_library_attributes.clear()
    del self["parent_library"]
    ProjectLibraryData.load()  # Hide edit icon in enum.


def get_parent_libaries(self: "BIMProjectProperties", context: bpy.types.Context) -> list[tuple[str, str, str]]:
    if not ProjectLibraryData.is_loaded:
        ProjectLibraryData.load()
    edited_library = str(self.editing_project_library_id)
    # Prevent assigning library to itself.
    enum_items = [i for i in ProjectLibraryData.data["parent_libraries_enum"] if i[0] != edited_library]
    return enum_items


def update_filter_mode(self: "BIMProjectProperties", context: bpy.types.Context) -> None:
    self.filter_categories.clear()
    if self.filter_mode == "NONE":
        return
    file = tool.Ifc.get()
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


def update_library_element_name(self: "LibraryElement", context: bpy.types.Context) -> None:
    library_file = IfcStore.library_file
    assert library_file

    if self.element_type == "CLASS":
        raise Exception("Unexpected element type for rename: 'CLASS'.")

    def update_element_name(ifc_definition_id: int, name: str) -> None:
        element = library_file.by_id(ifc_definition_id)
        attr_name = tool.Project.get_library_element_attr_name(element)
        previous_name = getattr(element, attr_name)
        if name == previous_name:
            return
        setattr(element, attr_name, name)

    if self.element_type == "ASSET":
        update_element_name(self.ifc_definition_id, self.name)
    elif self.element_type == "LIBRARY":
        assert self.ifc_definition_id, "Renaming for unassigned elements library is not supported."
        update_element_name(self.ifc_definition_id, self.name)
    else:
        assert_never(self.element_type)


LibraryElementType = Literal["ASSET", "CLASS", "LIBRARY"]


class LibraryElement(PropertyGroup):
    name: StringProperty(name="Name", update=update_library_element_name)
    element_type: EnumProperty(items=[(i, i, "") for i in get_args(LibraryElementType)], name="Element Type")
    # Asset group.
    asset_count: IntProperty(name="Asset Count")
    # Asset.
    ifc_definition_id: IntProperty(name="IFC Definition ID")
    is_declared: BoolProperty(name="Is Declared", default=False)
    is_appended: BoolProperty(name="Is Appended", default=False)
    is_declarable: BoolProperty(
        name="Is Declarable",
        description="Whether element support being declared as part of IfcProjectLibrary",
        default=False,
    )

    if TYPE_CHECKING:
        name: str
        element_type: LibraryElementType
        asset_count: int
        ifc_definition_id: int
        is_declared: bool
        is_appended: bool
        is_declarable: bool


class FilterCategory(PropertyGroup):
    name: StringProperty(name="Name")
    ifc_definition_id: IntProperty(name="IFC Definition ID")
    is_selected: BoolProperty(name="Is Selected", default=False)
    total_elements: IntProperty(name="Total Elements")

    if TYPE_CHECKING:
        name: str
        ifc_definition_id: int
        is_selected: bool
        total_elements: int


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

    if TYPE_CHECKING:
        name: str
        is_loaded: bool
        is_selectable: bool
        is_wireframe: bool
        is_hidden: bool
        empty_handle: Union[bpy.types.Object, None]


class EditedObj(PropertyGroup):
    obj: PointerProperty(type=bpy.types.Object)

    if TYPE_CHECKING:
        obj: Union[bpy.types.Object, None]


BreadcrumbType = Literal["LIBRARY", "CLASS"]


class LibraryBreadcrumb(PropertyGroup):
    breadcrumb_type: EnumProperty(items=[(i, i, "") for i in get_args(BreadcrumbType)])
    library_id: IntProperty(description="IFC Definition ID for libraries.")

    if TYPE_CHECKING:
        breadcrumb_type: BreadcrumbType
        library_id: int


class BIMProjectProperties(PropertyGroup):
    is_editing: BoolProperty(name="Is Editing", default=False)
    is_loading: BoolProperty(name="Is Loading", default=False)
    mvd: StringProperty(name="MVD")
    author_name: StringProperty(name="Author")
    author_email: StringProperty(name="Author Email")
    organisation_name: StringProperty(name="Organisation")
    organisation_email: StringProperty(name="Organisation Email")
    authorisation: StringProperty(name="Authoriser")
    library_breadcrumb: CollectionProperty(name="Library Breadcrumb", type=LibraryBreadcrumb)
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
    should_clean_mesh: BoolProperty(
        name="Clean Meshes",
        description=(
            "Convert all triangles to quads for meshes. "
            "By default Bonsai is importing meshes triangulated (even if they are not stored as triangulated in IFC)."
        ),
        default=False,
    )
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

    # Project library UI.
    library_file: EnumProperty(items=get_library_file, name="Library File", update=update_library_file)
    selected_project_library: EnumProperty(
        items=get_project_libaries,
        name="Selected Project Library",
        description="Selected project library to edit or to assign elements to",
        update=update_selected_project_library,
    )
    show_library_tree: BoolProperty(
        name="Show Library Tree",
        description="Show project libraries hierarchy or just show the assets classes.",
        default=True,
        update=show_library_tree_update,
    )
    is_editing_project_library: BoolProperty(
        name="Is Editing Project Library",
        description="Toggle editing for currently selected project library",
        update=is_editing_project_library_update,
    )
    editing_project_library_id: IntProperty(
        description="Needed to keep track of currently edited library when user changes currently selected library in dropdown."
    )
    project_library_attributes: CollectionProperty(name="Project Library Attributes", type=Attribute)
    parent_library: EnumProperty(
        name="Parent Library",
        description="Parent library that library is assigned to (either IfcProject or IfcProjectLibrary).",
        items=get_parent_libaries,
    )

    use_relative_project_path: BoolProperty(name="Use Relative Project Path", default=False)
    queried_obj: bpy.props.PointerProperty(type=bpy.types.Object)
    queried_obj_root: bpy.props.PointerProperty(type=bpy.types.Object)
    clipping_planes: bpy.props.CollectionProperty(type=ObjProperty)
    clipping_planes_active: bpy.props.IntProperty(min=0, default=0, max=5)
    edited_objs: bpy.props.CollectionProperty(type=EditedObj)

    @property
    def clipping_planes_objs(self) -> list[bpy.types.Object]:
        return list({cp.obj for cp in self.clipping_planes if cp.obj})

    def add_library_project_library(self, name: str, asset_count: int, ifc_definition_id: int) -> LibraryElement:
        new = self.library_elements.add()
        new["name"] = name
        new.asset_count = asset_count
        new.element_type = "LIBRARY"
        new.ifc_definition_id = ifc_definition_id
        return new

    def add_library_asset_class(self, name: str, asset_count: int) -> LibraryElement:
        new = self.library_elements.add()
        new["name"] = name
        new.asset_count = asset_count
        new.element_type = "CLASS"
        return new

    def get_library_element_index(self, lib_element: LibraryElement) -> int:
        return next((i for i in range(len(self.library_elements)) if self.library_elements[i] == lib_element))

    if TYPE_CHECKING:
        is_editing: bool
        is_loading: bool
        mvd: str
        author_name: str
        author_email: str
        organisation_name: str
        organisation_email: str
        authorisation: str
        library_breadcrumb: bpy.types.bpy_prop_collection_idprop[LibraryBreadcrumb]
        library_elements: bpy.types.bpy_prop_collection_idprop[LibraryElement]
        active_library_element_index: int
        filter_mode: Literal["NONE", "DECOMPOSITION", "IFC_CLASS", "IFC_TYPE", "WHITELIST", "BLACKLIST"]
        total_elements: int
        filter_categories: bpy.types.bpy_prop_collection_idprop[FilterCategory]
        active_filter_category_index: int
        filter_query: str
        should_filter_spatial_elements: bool
        geometry_library: Literal["opencascade", "cgal", "cgal-simple", "hybrid-cgal-simple-opencascade"]
        should_use_cpu_multiprocessing: bool
        should_merge_materials_by_colour: bool
        should_stream: bool
        should_load_geometry: bool
        should_clean_mesh: bool
        should_cache: bool
        deflection_tolerance: float
        angular_tolerance: float
        void_limit: int
        distance_limit: float
        false_origin_mode: Literal["AUTOMATIC", "MANUAL", "DISABLED"]
        false_origin: str
        project_north: str
        element_limit_mode: Literal["UNLIMITED", "RANGE"]
        element_offset: int
        element_limit: int
        load_indexed_maps: bool
        should_disable_undo_on_save: bool
        links: bpy.types.bpy_prop_collection_idprop[Link]
        active_link_index: int
        export_schema: str
        template_file: str

        library_file: str
        selected_project_library: Union[Literal["-"], str]
        show_library_tree: bool
        is_editing_project_library: bool
        editing_project_library_id: int
        project_library_attributes: bpy.types.bpy_prop_collection_idprop[Attribute]
        parent_library: str

        use_relative_project_path: bool
        queried_obj: Union[bpy.types.Object, None]
        queried_obj_root: Union[bpy.types.Object, None]
        clipping_planes: bpy.types.bpy_prop_collection_idprop[ObjProperty]
        clipping_planes_active: int
        edited_objs: bpy.types.bpy_prop_collection_idprop[EditedObj]

    def get_active_library_breadcrumb(self) -> Union[LibraryBreadcrumb, None]:
        if self.library_breadcrumb:
            return self.library_breadcrumb[-1]
        return None


class MeasureToolSettings(PropertyGroup):
    measurement_type_items = [
        ("SINGLE", "SINGLE", "Single", "FIXED_SIZE", 1),
        ("POLYLINE", "POLYLINE", "Polyline", "DRIVER_ROTATIONAL_DIFFERENCE", 2),
        ("AREA", "AREA", "Area", "OUTLINER_DATA_LIGHTPROBE", 3),
    ]

    measurement_type: bpy.props.EnumProperty(items=measurement_type_items, default="POLYLINE")

    if TYPE_CHECKING:
        measurement_type: Literal["SINGLE", "POLYLINE", "AREA"]
