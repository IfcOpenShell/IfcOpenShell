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
import json
import enum
import ifcopenshell
import ifcopenshell.api
import ifcopenshell.api.pset
import ifcopenshell.util.element
import bonsai.tool as tool
import bonsai.core.drawing as core
import bonsai.bim.module.drawing.annotation as annotation
import bonsai.bim.module.drawing.decoration as decoration
from mathutils import Matrix
from bonsai.bim.prop import BIMFilterGroup
from bonsai.bim.module.drawing.data import DrawingsData, DecoratorData, SheetsData, AnnotationData
from bonsai.bim.module.drawing.data import refresh as refresh_drawing_data
from pathlib import Path
from bonsai.bim.prop import Attribute, StrProperty
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
    BoolVectorProperty,
)
from typing import TYPE_CHECKING, Literal, Any, get_args, Union
from collections.abc import Callable


diagram_scales_enum = []


def purge():
    global diagram_scales_enum
    diagram_scales_enum = []


def update_target_view_doc(self: "DocProperties", context: bpy.types.Context) -> None:
    DrawingsData.data["location_hint"] = DrawingsData.location_hint()


def get_location_hint(self: "DocProperties", context: bpy.types.Context) -> list[tuple[str, str, str]]:
    if not DrawingsData.is_loaded:
        DrawingsData.load()
    return DrawingsData.data["location_hint"]


def update_diagram_scale(self: "BIMCameraProperties", context: bpy.types.Context) -> None:
    if not self.update_props:
        return
    assert context.scene
    if not (camera := context.scene.camera) or camera.data != self.id_data:
        return
    if not (element := tool.Ifc.get_entity(camera)):
        return
    try:
        element = (
            tool.Ifc.get()
            .by_id(tool.Geometry.get_mesh_props(self.id_data).ifc_definition_id)
            .OfProductRepresentation[0]
            .ShapeOfProduct[0]
        )
    except:
        return
    diagram_scale = tool.Drawing.get_diagram_scale(tool.Ifc.get_object(element))
    if not diagram_scale:
        return
    pset = ifcopenshell.util.element.get_pset(element, "EPset_Drawing")
    if pset:
        pset = tool.Ifc.get().by_id(pset["id"])
    else:
        pset = ifcopenshell.api.pset.add_pset(tool.Ifc.get(), product=element, name="EPset_Drawing")
    ifcopenshell.api.pset.edit_pset(tool.Ifc.get(), pset=pset, properties=diagram_scale)
    self.update_camera_resolution()


def update_is_nts(self: "BIMCameraProperties", context: bpy.types.Context) -> None:
    if not self.update_props:
        return
    assert context.scene
    if not context.scene.camera or context.scene.camera.data != self.id_data:
        return
    element = tool.Ifc.get_entity(context.scene.camera)
    if not element:
        return
    try:
        element = (
            tool.Ifc.get()
            .by_id(tool.Geometry.get_mesh_props(self.id_data).ifc_definition_id)
            .OfProductRepresentation[0]
            .ShapeOfProduct[0]
        )
    except:
        return
    pset = ifcopenshell.util.element.get_pset(element, "EPset_Drawing")
    if pset:
        pset = tool.Ifc.get().by_id(pset["id"])
    else:
        pset = ifcopenshell.api.pset.add_pset(tool.Ifc.get(), product=element, name="EPset_Drawing")
    ifcopenshell.api.pset.edit_pset(tool.Ifc.get(), pset=pset, properties={"IsNTS": self.is_nts})


def get_diagram_scales(self: "BIMCameraProperties", context: bpy.types.Context) -> list[tuple[str, str, str]]:
    global diagram_scales_enum
    assert context.scene
    if (
        len(diagram_scales_enum) < 1
        or (context.scene.unit_settings.system == "IMPERIAL" and len(diagram_scales_enum) == 13)
        or (context.scene.unit_settings.system == "METRIC" and len(diagram_scales_enum) == 31)
    ):
        if context.scene.unit_settings.system == "IMPERIAL":
            diagram_scales_enum = [
                ("CUSTOM", "Custom", ""),
                ("1'=1'-0\"|1/1", "1'=1'-0\"", ""),
                ('6"=1\'-0"|1/2', '6"=1\'-0"', ""),
                ('3"=1\'-0"|1/4', '3"=1\'-0"', ""),
                ('1-1/2"=1\'-0"|1/8', '1-1/2"=1\'-0"', ""),
                ('1"=1\'-0"|1/12', '1"=1\'-0"', ""),
                ('3/4"=1\'-0"|1/16', '3/4"=1\'-0"', ""),
                ('1/2"=1\'-0"|1/24', '1/2"=1\'-0"', ""),
                ('3/8"=1\'-0"|1/32', '3/8"=1\'-0"', ""),
                ('1/4"=1\'-0"|1/48', '1/4"=1\'-0"', ""),
                ('3/16"=1\'-0"|1/64', '3/16"=1\'-0"', ""),
                ('1/8"=1\'-0"|1/96', '1/8"=1\'-0"', ""),
                ('3/32"=1\'-0"|1/128', '3/32"=1\'-0"', ""),
                ('1/16"=1\'-0"|1/192', '1/16"=1\'-0"', ""),
                ('1/32"=1\'-0"|1/384', '1/32"=1\'-0"', ""),
                ('1/64"=1\'-0"|1/768', '1/64"=1\'-0"', ""),
                ('1/128"=1\'-0"|1/1536', '1/128"=1\'-0"', ""),
                ("1\"=10'|1/120", "1\"=10'", ""),
                ("1\"=20'|1/240", "1\"=20'", ""),
                ("1\"=30'|1/360", "1\"=30'", ""),
                ("1\"=40'|1/480", "1\"=40'", ""),
                ("1\"=50'|1/600", "1\"=50'", ""),
                ("1\"=60'|1/720", "1\"=60'", ""),
                ("1\"=70'|1/840", "1\"=70'", ""),
                ("1\"=80'|1/960", "1\"=80'", ""),
                ("1\"=90'|1/1080", "1\"=90'", ""),
                ("1\"=100'|1/1200", "1\"=100'", ""),
                ("1\"=150'|1/1800", "1\"=150'", ""),
                ("1\"=200'|1/2400", "1\"=200'", ""),
                ("1\"=300'|1/3600", "1\"=300'", ""),
                ("1\"=400'|1/4800", "1\"=400'", ""),
                ("1\"=500'|1/6000", "1\"=500'", ""),
            ]
        else:
            diagram_scales_enum = [
                ("CUSTOM", "Custom", ""),
                ("1:5000|1/5000", "1:5000", ""),
                ("1:2000|1/2000", "1:2000", ""),
                ("1:1000|1/1000", "1:1000", ""),
                ("1:500|1/500", "1:500", ""),
                ("1:200|1/200", "1:200", ""),
                ("1:100|1/100", "1:100", ""),
                ("1:50|1/50", "1:50", ""),
                ("1:20|1/20", "1:20", ""),
                ("1:10|1/10", "1:10", ""),
                ("1:5|1/5", "1:5", ""),
                ("1:2|1/2", "1:2", ""),
                ("1:1|1/1", "1:1", ""),
            ]
    return diagram_scales_enum


def update_drawing_name(self: "Drawing", context: bpy.types.Context) -> None:
    if self.ifc_definition_id:
        drawing = tool.Ifc.get().by_id(self.ifc_definition_id)
        core.update_drawing_name(tool.Ifc, tool.Drawing, drawing=drawing, name=self.name)


def get_drawing_style_name(self: "DrawingStyle"):
    """needed to make `set_drawing_style_name` work"""
    return self.get("name", "")


def set_drawing_style_name(self: "DrawingStyle", new_value: str) -> None:
    """ensure the name is unique"""
    props = tool.Drawing.get_document_props()
    drawing_styles = [s.name for s in props.drawing_styles if s.name != self.name]
    new_value = tool.Blender.ensure_unique_name(new_value, drawing_styles)
    old_value = self.name
    self["name"] = new_value
    bpy.ops.bim.save_drawing_styles_data(rename_style=True, rename_style_from=old_value, rename_style_to=new_value)


def update_document_name(self: "Document", context: bpy.types.Context) -> None:
    document = tool.Ifc.get().by_id(self.ifc_definition_id)
    core.update_document_name(tool.Ifc, tool.Drawing, document=document, name=self.name)


def update_has_underlay(self: "BIMCameraProperties", context: bpy.types.Context) -> None:
    if not self.update_props:
        return
    update_layer(self, context, "HasUnderlay", self.has_underlay)
    assert context.scene
    # making sure that camera is active
    if self.has_underlay and (context.scene.camera and context.scene.camera.data == self.id_data):
        bpy.ops.bim.reload_drawing_styles()
        bpy.ops.bim.activate_drawing_style()


def get_update_layer_callback(
    camera_prop_name: str, pset_prop_name: str
) -> Callable[["BIMCameraProperties", bpy.types.Context], None]:
    def update_layer_callback(self: "BIMCameraProperties", context: bpy.types.Context) -> None:
        update_layer(self, context, pset_prop_name, getattr(self, camera_prop_name))

    return update_layer_callback


def update_target_view_camera(self: "BIMCameraProperties", context: bpy.types.Context) -> None:
    if self.update_props and self.target_view != "MODEL_VIEW":
        self.camera_type = "ORTHO"
    update_layer(self, context, "TargetView", self.target_view)


def update_layer(self: "BIMCameraProperties", context: bpy.types.Context, name: str, value: Any) -> None:
    assert context.scene
    if not self.update_props:
        return
    if not context.scene.camera or context.scene.camera.data != self.id_data:
        return
    element = tool.Ifc.get_entity(context.scene.camera)
    if not element:
        return
    pset = ifcopenshell.util.element.get_pset(element, "EPset_Drawing")
    if pset:
        pset = tool.Ifc.get().by_id(pset["id"])
    else:
        pset = ifcopenshell.api.pset.add_pset(tool.Ifc.get(), product=element, name="EPset_Drawing")
    ifcopenshell.api.pset.edit_pset(tool.Ifc.get(), pset=pset, properties={name: value})


def get_titleblocks(self, context):
    if not SheetsData.is_loaded:
        SheetsData.load()
    return SheetsData.data["titleblocks"]


def update_titleblocks(self, context):
    SheetsData.data["titleblocks"] = SheetsData.titleblocks()


def update_should_draw_decorations(self, context: bpy.types.Context) -> None:
    if self.should_draw_decorations:
        # TODO: design a proper text variable templating renderer
        collection = tool.Blender.get_object_bim_props(context.scene.camera).collection
        for obj in collection.objects:
            element = tool.Ifc.get_entity(obj)
            if not element or not tool.Drawing.is_annotation_object_type(element, ["TEXT", "TEXT_LEADER"]):
                continue
            tool.Drawing.update_text_value(obj)
        refresh_drawing_data()
        if bpy.app.background:
            return
        decoration.DecorationsHandler.install(context)
    else:
        if bpy.app.background:
            return
        decoration.DecorationsHandler.uninstall()


class Variable(PropertyGroup):
    name: StringProperty(name="Name")
    prop_key: StringProperty(name="Property Key")


TargetView = Literal["PLAN_VIEW", "ELEVATION_VIEW", "SECTION_VIEW", "REFLECTED_PLAN_VIEW", "MODEL_VIEW"]
TARGET_VIEW_ITEMS: list[tuple[TargetView, str, str]] = [
    ("PLAN_VIEW", "Plan", ""),
    ("ELEVATION_VIEW", "Elevation", ""),
    ("SECTION_VIEW", "Section", ""),
    ("REFLECTED_PLAN_VIEW", "RCP", ""),
    ("MODEL_VIEW", "Model", ""),
]


class Drawing(PropertyGroup):
    ifc_definition_id: IntProperty(name="IFC Definition ID")
    name: StringProperty(name="Name", update=update_drawing_name)
    target_view: EnumProperty(
        name="Target View",
        default="PLAN_VIEW",
        items=TARGET_VIEW_ITEMS,
    )
    is_selected: BoolProperty(name="Is Selected", default=True)
    is_drawing: BoolProperty(name="Is Drawing", default=False)
    is_expanded: BoolProperty(name="Is Expanded", default=True)

    if TYPE_CHECKING:
        ifc_definition_id: int
        name: str
        target_view: TargetView
        is_selected: bool
        is_drawing: bool
        is_expanded: bool


class Document(PropertyGroup):
    ifc_definition_id: IntProperty(name="IFC Definition ID")
    name: StringProperty(name="Name", update=update_document_name)
    identification: StringProperty(name="Identification")

    if TYPE_CHECKING:
        ifc_definition_id: int
        name: str
        identification: str


class Sheet(PropertyGroup):
    ifc_definition_id: IntProperty(name="IFC Definition ID")
    identification: StringProperty(name="Identification")
    name: StringProperty(name="Name")
    is_sheet: BoolProperty(name="Is Sheet", default=False)
    is_selected: BoolProperty(name="Is Selected", default=True)
    reference_type: StringProperty(name="Reference Type")
    is_expanded: BoolProperty(name="Is Expanded", default=False)

    if TYPE_CHECKING:
        ifc_definition_id: int
        identification: str
        name: str
        is_sheet: bool
        is_selected: bool
        reference_type: str
        is_expanded: bool


RenderType = Literal["DEFAULT", "VIEWPORT"]
RENDER_TYPE_ENUM_ITEMS: dict[RenderType, tuple[str, str]] = {
    "DEFAULT": ("Default", "Use default Blender render."),
    "VIEWPORT": ("Viewport", "Render active viewport (using 'Rendered' viewport shading type)."),
}


class DrawingStyle(PropertyGroup):
    name: StringProperty(name="Name", get=get_drawing_style_name, set=set_drawing_style_name)
    raster_style: StringProperty(
        name="Raster Style",
        description="JSON string for drawing style settings.",
        default="{}",
    )
    render_type: EnumProperty(
        items=[(k, *v) for k, v in RENDER_TYPE_ENUM_ITEMS.items()],
        name="Render Type",
        default="VIEWPORT",
    )
    include_query: StringProperty(name="Include Query")
    exclude_query: StringProperty(name="Exclude Query")

    if TYPE_CHECKING:
        name: str
        raster_style: str
        render_type: RenderType
        include_query: str
        exclude_query: str


class RasterStyleProperty(enum.Enum):
    # EVAL_PROP_ props will be evaluated explicitly
    EVAL_PROP_WORLD_COLOR = "bpy.data.worlds[0].color"

    # those props attributes used as a source for shading style properties
    RENDER = "scene.render"
    VIEW_SETTINGS = "scene.view_settings"
    SHADING = "scene.display.shading"
    DISPLAY = "scene.display"
    OVERLAY = "space.overlay"
    SPACE_SHADING = "space.shading"


RASTER_STYLE_PROPERTIES_EXCLUDE = ("scene.render.filepath",)


class DocProperties(PropertyGroup):
    should_use_underlay_cache: BoolProperty(name="Use Underlay Cache", default=False)
    should_use_linework_cache: BoolProperty(name="Use Linework Cache", default=False)
    should_use_annotation_cache: BoolProperty(name="Use Annotation Cache", default=False)
    is_editing_drawings: BoolProperty(name="Is Editing Drawings", default=False)
    is_editing_schedules: BoolProperty(name="Is Editing Schedules", default=False)
    is_editing_references: BoolProperty(name="Is Editing References", default=False)
    target_view: EnumProperty(
        items=TARGET_VIEW_ITEMS,
        name="Target View",
        default="PLAN_VIEW",
        update=update_target_view_doc,
    )
    location_hint: EnumProperty(items=get_location_hint, name="Location Hint")
    drawings: CollectionProperty(name="Drawings", type=Drawing)
    active_drawing_id: IntProperty(name="Active Drawing Id")
    active_drawing_index: IntProperty(name="Active Drawing Index")
    current_drawing_index: IntProperty(name="Current Drawing Index")
    schedules: CollectionProperty(name="Schedules", type=Document)
    active_schedule_index: IntProperty(name="Active Schedule Index")
    references: CollectionProperty(name="References", type=Document)
    active_reference_index: IntProperty(name="Active Reference Index")
    titleblock: EnumProperty(items=get_titleblocks, name="Titleblock", update=update_titleblocks)
    is_editing_sheets: BoolProperty(name="Is Editing Sheets", default=False)
    sheets: CollectionProperty(name="Sheets", type=Sheet)
    active_sheet_index: IntProperty(name="Active Sheet Index")
    ifc_files: CollectionProperty(name="IFCs", type=StrProperty)
    drawing_styles: CollectionProperty(name="Drawing Styles", type=DrawingStyle)
    should_draw_decorations: BoolProperty(name="Should Draw Decorations", update=update_should_draw_decorations)
    sheets_dir: StringProperty(default=os.path.join("sheets") + os.path.sep, name="Default Sheets Directory")
    layouts_dir: StringProperty(default=os.path.join("layouts") + os.path.sep, name="Default Layouts Directory")
    titleblocks_dir: StringProperty(
        default=os.path.join("layouts", "titleblocks") + os.path.sep, name="Default Titleblocks Directory"
    )
    drawings_dir: StringProperty(default=os.path.join("drawings") + os.path.sep, name="Default Drawings Directory")
    stylesheet_path: StringProperty(
        default=os.path.join("drawings", "assets", "default.css"), name="Default Stylesheet"
    )
    schedules_stylesheet_path: StringProperty(
        default=os.path.join("drawings", "assets", "schedule.css"), name="Default Stylesheet for Schedules"
    )
    markers_path: StringProperty(default=os.path.join("drawings", "assets", "markers.svg"), name="Default Markers")
    symbols_path: StringProperty(default=os.path.join("drawings", "assets", "symbols.svg"), name="Default Symbols")
    patterns_path: StringProperty(default=os.path.join("drawings", "assets", "patterns.svg"), name="Default Patterns")
    shadingstyles_path: StringProperty(
        default=os.path.join("drawings", "assets", "shading_styles.json"), name="Default Shading Styles"
    )
    shadingstyle_default: StringProperty(default="Blender Default", name="Default Shading Style")
    drawing_font: StringProperty(default="OpenGost Type B TT.ttf", name="Drawing Font")
    magic_font_scale: bpy.props.FloatProperty(default=0.004118616, name="Font Scale Factor")
    imperial_precision: StringProperty(default="1/32", name="Imperial Precision")
    tolerance: bpy.props.FloatProperty(default=0.00001, name="A tolerance used when selecting objects")
    classes_to_wireframe: StringProperty(
        default="IfcVirtualElement",
        name="Classes to Wireframe",
        description="Upon import, these classes will display as wireframe.\nEx: IfcVirtualelement, IfcSpace",
    )
    classes_no_cut: StringProperty(
        default="IfcVirtualElement, IfcSpace",
        name="Classes that are not cut",
        description="The cut decoractor will be turned off for these classes\nEx: IfcVirtualelement, IfcSpace",
    )

    if TYPE_CHECKING:
        should_use_underlay_cache: bool
        should_use_linework_cache: bool
        should_use_annotation_cache: bool
        is_editing_drawings: bool
        is_editing_schedules: bool
        is_editing_references: bool
        target_view: Literal["PLAN_VIEW", "ELEVATION_VIEW", "SECTION_VIEW", "REFLECTED_PLAN_VIEW", "MODEL_VIEW"]
        location_hint: tool.Drawing.LocationHintType
        drawings: bpy.types.bpy_prop_collection_idprop[Drawing]
        active_drawing_id: int
        active_drawing_index: int
        current_drawing_index: int
        schedules: bpy.types.bpy_prop_collection_idprop[Document]
        active_schedule_index: int
        references: bpy.types.bpy_prop_collection_idprop[Document]
        active_reference_index: int
        titleblock: str
        is_editing_sheets: bool
        sheets: bpy.types.bpy_prop_collection_idprop[Sheet]
        active_sheet_index: int
        ifc_files: bpy.types.bpy_prop_collection_idprop[StrProperty]
        drawing_styles: bpy.types.bpy_prop_collection_idprop[DrawingStyle]
        should_draw_decorations: bool
        sheets_dir: str
        layouts_dir: str
        titleblocks_dir: str
        drawings_dir: str
        stylesheet_path: str
        schedules_stylesheet_path: str
        markers_path: str
        symbols_path: str
        patterns_path: str
        shadingstyles_path: str
        shadingstyle_default: str
        drawing_font: str
        magic_font_scale: float
        imperial_precision: str
        tolerance: float
        classes_to_wireframe: str
        classes_no_cut: str

    def get_active_drawing(self) -> Union[ifcopenshell.entity_instance, None]:
        drawing_id = self.active_drawing_id
        if drawing_id == 0:
            return None
        return tool.Ifc.get().by_id(drawing_id)


def update_width_height(self: "BIMCameraProperties", context: bpy.types.Context) -> None:
    self.update_camera_resolution()


def update_camera_type(self: "BIMCameraProperties", context: bpy.types.Context) -> None:
    assert isinstance(camera := self.id_data, bpy.types.Camera)
    camera.type = self.camera_type


CameraType = Literal["PERSP", "ORTHO"]
CAMERA_TYPE_ENUM_ITEMS: dict[CameraType, tuple[str, str]] = {
    "ORTHO": ("Orthographic", "Most common camera for the drawings, supporting all of the features."),
    "PERSP": ("Perspective", "The only avilable features for perspective camera: freestyle linework, underlay."),
}


class BIMCameraProperties(PropertyGroup):
    linework_mode: EnumProperty(
        items=[
            ("OPENCASCADE", "OpenCASCADE", "Slower, more accurate, with more features"),
            ("FREESTYLE", "Freestyle", "Faster, less accurate, no fill support"),
        ],
        default="OPENCASCADE",
        name="Linework Mode",
        update=get_update_layer_callback("linework_mode", "LineworkMode"),
    )
    fill_mode: EnumProperty(
        items=[
            ("NONE", "None", "Disable filling areas seen in projection"),
            ("SHAPELY", "Shapely", "Recommended"),
            ("SVGFILL", "SVGFill", "Experimental"),
        ],
        default="NONE",
        name="Fill Mode",
        update=get_update_layer_callback("fill_mode", "FillMode"),
    )
    cut_mode: EnumProperty(
        items=[
            ("BISECT", "Bisect", "Faster, more forgiving to bad geometry"),
            ("OPENCASCADE", "OpenCASCADE", "More technically correct"),
        ],
        default="BISECT",
        name="Cut Mode",
        update=get_update_layer_callback("cut_mode", "CutMode"),
    )

    # EPset_Drawing.
    has_underlay: BoolProperty(
        name="Underlay",
        default=False,
        update=update_has_underlay,
    )
    has_linework: BoolProperty(
        name="Linework",
        default=True,
        update=get_update_layer_callback("has_linework", "HasLinework"),
    )
    has_annotation: BoolProperty(
        name="Annotation",
        default=True,
        update=get_update_layer_callback("has_annotation", "HasAnnotation"),
    )
    target_view: EnumProperty(
        name="Target View",
        default="PLAN_VIEW",
        items=TARGET_VIEW_ITEMS,
        update=update_target_view_camera,
    )

    representation: StringProperty(name="Representation")
    view_name: StringProperty(name="View Name")
    diagram_scale: EnumProperty(items=get_diagram_scales, name="Drawing Scale", update=update_diagram_scale)
    custom_scale_numerator: bpy.props.StringProperty(default="1", update=update_diagram_scale)
    custom_scale_denominator: bpy.props.StringProperty(default="100", update=update_diagram_scale)
    raster_x: IntProperty(name="Raster X", default=1000)
    raster_y: IntProperty(name="Raster Y", default=1000)
    dpi: IntProperty(name="DPI", default=75, update=get_update_layer_callback("dpi", "DPI"))
    width: FloatProperty(name="Width", default=50, subtype="DISTANCE", update=update_width_height)
    height: FloatProperty(name="Height", default=50, subtype="DISTANCE", update=update_width_height)
    # Bonsai property is needed to prevent user from using unsupported panoramic camera.
    camera_type: EnumProperty(
        name="Camera Type",
        default="ORTHO",
        items=[(k, *v) for k, v in CAMERA_TYPE_ENUM_ITEMS.items()],
        update=update_camera_type,
    )
    is_nts: BoolProperty(name="Is NTS", update=update_is_nts)
    active_drawing_style_index: IntProperty(name="Active Drawing Style Index")
    filter_mode: StringProperty(name="Filter Mode", default="NONE")
    include_filter_groups: CollectionProperty(type=BIMFilterGroup, name="Include Filter")
    exclude_filter_groups: CollectionProperty(type=BIMFilterGroup, name="Exclude Filter")
    update_props: BoolProperty(
        name="Enable Props Auto Update",
        description="Update related EPset_Drawing pset on any change in camera properties.",
        default=True,
    )

    if TYPE_CHECKING:
        linework_mode: Literal["OPENCASCADE", "FREESTYLE"]
        fill_mode: Literal["NONE", "SHAPELY", "SVGFILL"]
        cut_mode: Literal["BISECT", "OPENCASCADE"]

        has_underlay: bool
        has_linework: bool
        has_annotation: bool
        target_view: TargetView

        representation: str
        view_name: str
        diagram_scale: str
        custom_scale_numerator: str
        custom_scale_denominator: str
        raster_x: int
        raster_y: int
        dpi: int
        width: float
        height: float
        camera_type: CameraType
        is_nts: bool
        active_drawing_style_index: int
        filter_mode: str
        include_filter_groups: bpy.types.bpy_prop_collection_idprop[BIMFilterGroup]
        exclude_filter_groups: bpy.types.bpy_prop_collection_idprop[BIMFilterGroup]
        update_props: bool

    def get_active_drawing_style(self) -> Union[DrawingStyle, None]:
        dprops = tool.Drawing.get_document_props()
        return tool.Blender.get_active_uilist_element(dprops.drawing_styles, self.active_drawing_style_index)

    # For now, this JSON dump are all the parameters that determine a camera's "Block representation"
    # By checking this, you will know whether or not the camera IFC representation needs to be refreshed
    def update_representation(self, matrix_world: Matrix) -> bool:
        """Update ``representation`` based on current camera properties and the provided world matrix.

        :return: ``True`` if ``representation`` was updated and
            representation should also be updated in IFC.
        """
        # Matrix is used instead of Object so this works before the Object exists,
        # allowing all camera initialization to stay encapsulated in `create_camera`.
        camera = self.id_data
        assert isinstance(camera, bpy.types.Camera)

        # Rounding is necessary to avoid float garbage differences
        # forcing unnecessary representation update.
        def round_(f: float) -> float:
            return round(f, 6)

        representation = json.dumps(
            {
                "type": self.camera_type,
                "matrix": [[round_(v) for v in row] for row in matrix_world],
                "raster_x": self.raster_x,
                "raster_y": self.raster_y,
                "ortho_scale": round_(camera.ortho_scale),
                "clip_end": round_(camera.clip_end),
            }
        )
        if self.representation != representation:
            self.representation = representation
            return True
        return False

    def update_camera_resolution(self) -> tuple[int, int]:
        """Update ``camera.ortho_scale``, ``raster_x`` and ``raster_y``
        based on current ``width`` and ``height`` and diagram scale props.

        :return: tuple[resolution_x, resolution_y]
        """
        assert isinstance(camera := self.id_data, bpy.types.Camera)
        ortho_scale, aspect_ratio = self.get_scale_and_aspect_ratio()
        aspect_ratio = self.width / self.height

        camera.ortho_scale = ortho_scale
        diagram_scale = tool.Drawing.get_diagram_scale(camera)
        scale_ratio = tool.Drawing.get_scale_ratio(diagram_scale["Scale"])

        if self.width > self.height:
            aspect_ratio = self.height / self.width
            raster_x = ortho_scale * scale_ratio * self.dpi / 0.0254
            raster_y = ortho_scale * aspect_ratio * scale_ratio * self.dpi / 0.0254
        else:
            aspect_ratio = self.width / self.height
            raster_x = ortho_scale * aspect_ratio * scale_ratio * self.dpi / 0.0254
            raster_y = ortho_scale * scale_ratio * self.dpi / 0.0254

        raster_x, raster_y = int(raster_x), int(raster_y)
        self.raster_x, self.raster_y = raster_x, raster_y
        return raster_x, raster_y

    def get_scale_and_aspect_ratio(self) -> tuple[float, float]:
        """
        :return: A tuple of calculated ortho scale and aspect ratio values.
        """
        ortho_scale = max(self.width, self.height)
        aspect_ratio = self.width / self.height
        return ortho_scale, aspect_ratio


DEFAULT_BOX_ALIGNMENT = [False] * 6 + [True] + [False] * 2
BOX_ALIGNMENT_POSITIONS = [
    "top-left",
    "top-middle",
    "top-right",
    "middle-left",
    "center",
    "middle-right",
    "bottom-left",
    "bottom-middle",
    "bottom-right",
]


class LiteralProps(PropertyGroup):
    def set_box_alignment(self, new_value):
        markers = new_value.count(True)
        if not markers:
            return

        if markers > 1:
            prev_value = self.get("box_alignment", DEFAULT_BOX_ALIGNMENT)
            # looking for the first value changed to positive
            first_changed_value = next((i for i in range(9) if new_value[i] and new_value[i] != prev_value[i]), None)

            # if nothing have changed we just keep the previous value
            if first_changed_value is None:
                return
            new_value = [False] * 9
            new_value[first_changed_value] = True

        self["box_alignment"] = new_value
        position_string = BOX_ALIGNMENT_POSITIONS[next(i for i in range(9) if new_value[i])]
        self.attributes["BoxAlignment"].set_value(position_string)

    def get_box_alignment(self):
        return self.get("box_alignment", DEFAULT_BOX_ALIGNMENT)

    attributes: CollectionProperty(name="Attributes", type=Attribute)
    # Current text value with evaluated expressions stored in `value`.
    # The original (Literal) value stored in `attributes['Literal']`
    # and can be accessed with `get_text()`
    value: StringProperty(name="Value", default="TEXT")
    box_alignment: BoolVectorProperty(
        name="Box alignment", size=9, set=set_box_alignment, get=get_box_alignment, default=DEFAULT_BOX_ALIGNMENT
    )
    ifc_definition_id: IntProperty(name="IFC definition ID", default=0)

    def get_literal_edited_data(self):
        text_data = {
            "CurrentValue": self.attributes["Literal"].string_value,
            "Literal": self.attributes["Literal"].string_value,
            "BoxAlignment": self.attributes["BoxAlignment"].string_value,
        }
        return text_data

    if TYPE_CHECKING:
        attributes: bpy.types.bpy_prop_collection_idprop[Attribute]
        value: str
        box_alignment: str
        ifc_definition_id: int


class BIMTextProperties(PropertyGroup):
    is_editing: BoolProperty(name="Is Editing", default=False)
    literals: CollectionProperty(name="Literals", type=LiteralProps)
    font_size: EnumProperty(
        items=[
            ("1.8", "1.8 - Small", ""),
            ("2.5", "2.5 - Regular", ""),
            ("3.5", "3.5 - Large", ""),
            ("5.0", "5.0 - Header", ""),
            ("7.0", "7.0 - Title", ""),
        ],
        default="2.5",
        name="Font Size",
    )
    newline_at: IntProperty(name="Newline At")

    if TYPE_CHECKING:
        is_editing: bool
        literals: bpy.types.bpy_prop_collection_idprop[LiteralProps]
        font_size: str
        newline_at: int

    def get_text_edited_data(self) -> dict[str, Any]:
        """should be called only if `is_editing`
        otherwise should use `DecoratorData.get_text_data(obj)` instead
        because this data could be out of date
        """
        literals_data = []
        for literal in self.literals:
            literal_data = literal.get_literal_edited_data()
            literals_data.append(literal_data)
        text_data = {
            "Literals": literals_data,
            "FontSize": float(self.font_size),
            "Newline_At": int(self.newline_at),
        }
        return text_data


def relating_product_poll(self: "BIMAssignedProductProperties", obj: bpy.types.Object) -> bool:
    if not tool.Ifc.get_entity(obj):
        return False
    return True


class BIMAssignedProductProperties(PropertyGroup):
    is_editing_product: BoolProperty(name="Is Editing Product", default=False)
    relating_product: PointerProperty(name="Relating Product", type=bpy.types.Object, poll=relating_product_poll)

    if TYPE_CHECKING:
        is_editing_product: bool
        relating_product: Union[bpy.types.Object, None]


annotation_classes = [
    (x, *tool.Drawing.ANNOTATION_TYPES_DATA[x][:3], i) for i, x in enumerate(tool.Drawing.ANNOTATION_TYPES_DATA)
]


def get_relating_type_id(self, context):
    if not AnnotationData.is_loaded:
        AnnotationData.load()
    return AnnotationData.data["relating_type_id"]


def update_annotation_object_type(self, context):
    # Refresh enum items before changing property,
    # otherwise it might map to the wrong item.
    AnnotationData.is_loaded = False
    self.relating_type_id = "0"


def update_sheet_data(self, context):
    SheetsData.is_loaded = False


class BIMAnnotationProperties(PropertyGroup):
    object_type: bpy.props.EnumProperty(
        name="Annotation Object Type", items=annotation_classes, default="TEXT", update=update_annotation_object_type
    )
    relating_type_id: bpy.props.EnumProperty(name="Relating Annotation Type", items=get_relating_type_id)
    create_representation_for_type: bpy.props.BoolProperty(
        name="Create Representation For Type",
        default=False,
        description='Whether "Add type" should define a representation for the type \n'
        "or allow occurrences to have their own",
    )
    is_adding_type: bpy.props.BoolProperty(default=False)
    type_name: bpy.props.StringProperty(name="Name", default="TYPEX")

    if TYPE_CHECKING:
        object_type: str
        relating_type_id: str
        create_representation_for_type: bool
        is_adding_type: bool
        type_name: str
