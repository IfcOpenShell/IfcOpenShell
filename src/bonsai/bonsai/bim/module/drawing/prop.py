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

import enum
import json
from collections.abc import Callable
from typing import TYPE_CHECKING, Any, Literal, Union

import bpy
import ifcopenshell
import ifcopenshell.api.pset
import ifcopenshell.util.element
from bpy.props import (
    BoolProperty,
    CollectionProperty,
    EnumProperty,
    FloatProperty,
    IntProperty,
    PointerProperty,
    StringProperty,
)
from bpy.types import PropertyGroup
from mathutils import Matrix

import bonsai.bim.module.drawing.decoration as decoration
import bonsai.core.drawing as core
import bonsai.tool as tool
from bonsai.bim.module.drawing.data import (
    AnnotationData,
    DrawingsData,
    ElementValuesData,
    SheetsData,
)
from bonsai.bim.module.drawing.data import refresh as refresh_drawing_data
from bonsai.bim.prop import Attribute, BIMFilterGroup

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
    """``Drawing`` can be either a drawing or a drawing target view header."""
    is_expanded: BoolProperty(name="Is Expanded", default=True)
    """Whether target view header is expanded in UI. Should be just unset for the actual drawings."""

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

    if TYPE_CHECKING:
        name: str
        raster_style: str
        render_type: RenderType


class RasterStyleProperty(enum.Enum):
    # EVAL_PROP_ props will be evaluated explicitly
    EVAL_PROP_WORLD_COLOR = "bpy.data.worlds[0].color"
    EVAL_PROP_EEVEE_USE_SHADOWS = "scene.eevee.use_shadows"
    EVAL_PROP_EEVEE_SHADOW_RAY_COUNT = "scene.eevee.shadow_ray_count"
    EVAL_PROP_EEVEE_SHADOW_STEP_COUNT = "scene.eevee.shadow_step_count"
    EVAL_PROP_EEVEE_SHADOW_RES_SCALE = "scene.eevee.shadow_resolution_scale"

    # those props attributes used as a source for shading style properties
    RENDER = "scene.render"
    VIEW_SETTINGS = "scene.view_settings"
    SHADING = "scene.display.shading"
    DISPLAY = "scene.display"
    OVERLAY = "space.overlay"
    SPACE_SHADING = "space.shading"


RASTER_STYLE_PROPERTIES_EXCLUDE = ("scene.render.filepath",)


class DocProperties(PropertyGroup):
    # Note that options are global in descriptions to prevent confusion,
    # as options are available through Active Drawing UI, but they're actually global.
    should_use_underlay_cache: BoolProperty(
        name="Use Underlay Cache", description="Global option for all drawings.", default=False
    )
    should_use_linework_cache: BoolProperty(
        name="Use Linework Cache", description="Global option for all drawings.", default=False
    )
    should_use_annotation_cache: BoolProperty(
        name="Use Annotation Cache", description="Global option for all drawings.", default=False
    )
    should_draw_linked_projects: BoolProperty(
        name="Draw Linked Projects",
        description=("Whether to draw all currently loaded linked projects.\n\nGlobal option for all drawings."),
        default=True,
        options=set(),
    )
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
    drawing_styles: CollectionProperty(name="Drawing Styles", type=DrawingStyle)
    should_draw_decorations: BoolProperty(name="Should Draw Decorations", update=update_should_draw_decorations)

    if TYPE_CHECKING:
        should_use_underlay_cache: bool
        should_use_linework_cache: bool
        should_use_annotation_cache: bool
        should_draw_linked_projects: bool
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
        drawing_styles: bpy.types.bpy_prop_collection_idprop[DrawingStyle]
        should_draw_decorations: bool

    def get_active_drawing(self) -> Union[ifcopenshell.entity_instance, None]:
        drawing_id = self.active_drawing_id
        if drawing_id == 0:
            return None
        return tool.Ifc.get().by_id(drawing_id)

    def get_active_target_view(self) -> Union[str, None]:
        active_drawing = self.get_active_drawing()
        if not active_drawing:
            return None
        return tool.Drawing.get_drawing_target_view(active_drawing)


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
    generate_material_layers: bpy.props.BoolProperty(
        name="Generate Material Layers", description="Generate material layer linework in drawings", default=True
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
    # Perspective camera shift is stored in EPset_Drawing and intentionally excluded here.
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


class ElementValueRow(PropertyGroup):
    """Represents a single element value row with category, key, and formatted value"""

    category: EnumProperty(
        name="Category",
        items=[
            ("Basic", "Basic", "Basic element information"),
            ("Attributes", "Attributes", "IFC Attributes"),
            ("Property Sets", "Property Sets", "Property Sets"),
            ("Quantity Sets", "Quantity Sets", "Quantity Sets"),
            ("Type", "Type", "Type information"),
            ("Spatial", "Spatial", "Spatial relationships"),
            ("Parent", "Parent", "Parent relationships"),
            ("Classification", "Classification", "Classifications"),
            ("Groups", "Groups", "Group assignments"),
            ("Systems", "Systems", "System assignments"),
            ("Zones", "Zones", "Zone assignments"),
            ("Material", "Material", "Material information"),
            ("Styles", "Styles", "Style information"),
            ("Profiles", "Profiles", "Profile information"),
            ("Coordinates", "Coordinates", "Coordinate information"),
            ("Custom String", "Custom String", "Custom text (no element key)"),
        ],
        default="Basic",
    )

    element_key: StringProperty(
        name="Element Key",
        description="The element value key (e.g., 'id', 'Name', 'Pset_WallCommon.Reference')",
        default="",
    )

    formatted_value: StringProperty(
        name="Formatted Value",
        description="The formatted value string with selector syntax (e.g., '{{id}}' or '``upper({{Name}})``')",
        default="",
    )

    separator: StringProperty(
        name="Separator",
        description="Text to insert before this value when concatenating (e.g., ' - ', ', ', '\\n')",
        default=" - ",
    )

    if TYPE_CHECKING:
        category: str
        element_key: str
        formatted_value: str
        separator: str


def get_category_items_with_counts(self, context):
    """Generate category items with counts dynamically"""
    category_metadata = [
        ("Basic", "Basic", "Basic element information", "OBJECT_DATA"),
        ("Attributes", "Attributes", "IFC Attributes", "PROPERTIES"),
        ("Property Sets", "Property Sets", "Property Sets", "ALIGN_JUSTIFY"),
        ("Quantity Sets", "Quantity Sets", "Quantity Sets", "SNAP_VOLUME"),
        ("Type", "Type", "Type information", "FILE_VOLUME"),
        ("Spatial", "Spatial", "Spatial relationships", "HOME"),
        ("Parent", "Parent", "Parent relationships", "FILE_PARENT"),
        ("Classification", "Classification", "Classifications", "BOOKMARKS"),
        ("Groups", "Groups", "Group assignments", "OUTLINER_COLLECTION"),
        ("Systems", "Systems", "System assignments", "SYSTEM"),
        ("Zones", "Zones", "Zone assignments", "MESH_CIRCLE"),
        ("Material", "Material", "Material information", "MATERIAL"),
        ("Styles", "Styles", "Style information", "COLOR"),
        ("Profiles", "Profiles", "Profile information", "OUTLINER_DATA_CURVES"),
        ("Coordinates", "Coordinates", "Coordinate information", "EMPTY_ARROWS"),
        ("Custom String", "Custom String", "Add custom text (no element key)", "SMALL_CAPS"),
    ]

    obj = context.active_object

    if obj and tool.Ifc.get_entity(obj):
        try:
            element = tool.Ifc.get_entity(obj)
            text_element = element

            if hasattr(self, "product_used"):
                if self.product_used:
                    element = tool.Ifc.get_entity(self.product_used)
                else:
                    assigned = tool.Drawing.get_assigned_product(text_element)
                    if assigned:
                        element = assigned

            available_keys = ElementValuesData.get_available_element_value_keys(element)
            items = []
            for i, (identifier, base_name, description, icon) in enumerate(category_metadata):
                count = len(available_keys.get(identifier, []))
                display_name = f"{base_name} ({count})" if count > 0 else base_name
                items.append((identifier, display_name, description, icon, i))

            return items
        except Exception as e:
            pass

    return [(id, name, desc, icon, i) for i, (id, name, desc, icon) in enumerate(category_metadata)]


class LiteralProps(PropertyGroup):
    attributes: CollectionProperty(name="Attributes", type=Attribute)
    ifc_definition_id: IntProperty(name="IFC definition ID", default=0)
    align_horizontal: EnumProperty(
        items=[
            ("left", "Left", "", "ALIGN_LEFT", 0),
            ("middle", "Middle", "", "ALIGN_CENTER", 1),
            ("right", "Right", "", "ALIGN_RIGHT", 2),
        ],
        default="left",
        name="Horizontal Alignment",
    )
    align_vertical: EnumProperty(
        items=[
            ("top", "Top", "", "ALIGN_TOP", 0),
            ("middle", "Middle", "", "ALIGN_MIDDLE", 1),
            ("bottom", "Bottom", "", "ALIGN_BOTTOM", 2),
        ],
        default="middle",
        name="Vertical Alignment",
    )

    def get_box_alignment(self) -> str:
        alignment = self.align_vertical + "-" + self.align_horizontal
        if alignment == "middle-middle":
            alignment = "center"
        return alignment

    def get_literal_edited_data(self) -> dict[str, str]:
        text_data = {
            "CurrentValue": self.attributes["Literal"].string_value,
            "Literal": self.attributes["Literal"].string_value,
            "BoxAlignment": self.get_box_alignment(),
        }
        return text_data

    show_element_values: bpy.props.BoolProperty(
        name="Show Element Values", description="Show/hide the element values panel", default=False
    )

    expanded_category: bpy.props.StringProperty(
        name="Expanded Category", description="Currently expanded category in the element values panel", default=""
    )

    element_values_filter: bpy.props.StringProperty(
        name="Element Values Filter", description="Search filter for element values", default=""
    )

    product_used: PointerProperty(
        name="Product Used",
        type=bpy.types.Object,
        description="Object to use for fetching element values. If empty, uses assigned product",
    )

    element_value_rows: CollectionProperty(
        name="Element Value Rows",
        type=ElementValueRow,
        description="Collection of element value rows for building the literal value",
    )

    category_for_adding: EnumProperty(
        name="Category for Adding",
        items=get_category_items_with_counts,
        default=0,
        description="Category to use when adding a new element value row",
    )

    if TYPE_CHECKING:
        attributes: bpy.types.bpy_prop_collection_idprop[Attribute]
        value: str
        ifc_definition_id: int
        align_horizontal: str
        align_vertical: str
        element_value_rows: bpy.types.bpy_prop_collection_idprop[ElementValueRow]
        category_for_adding: str


def update_text_alignment(self, context):
    for literal_props in self.literals:
        literal_props.align_horizontal = self.align_horizontal
        literal_props.align_vertical = self.align_vertical


class BIMTextProperties(PropertyGroup):
    is_editing: BoolProperty(name="Is Editing", default=False)
    literals: CollectionProperty(name="Literals", type=LiteralProps)
    newline_at: IntProperty(name="Newline At")
    symbol: EnumProperty(
        name="Symbol",
        description="Symbol from symbols.svg to use for this text.",
        items=[(s, s, "") for s in ["NO SYMBOL", "CUSTOM SYMBOL"] + tool.Drawing.DEFAULT_SYMBOLS],
        default="NO SYMBOL",
    )
    custom_symbol: StringProperty(
        name="Custom Symbol",
        description="Non-default symbol to use for this text.",
    )
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
    align_horizontal: EnumProperty(
        items=[
            ("left", "Left", "", "ALIGN_LEFT", 0),
            ("middle", "Middle", "", "ALIGN_CENTER", 1),
            ("right", "Right", "", "ALIGN_RIGHT", 2),
        ],
        default="left",
        name="Horizontal Alignment",
        update=update_text_alignment,
    )
    align_vertical: EnumProperty(
        items=[
            ("top", "Top", "", "ALIGN_TOP", 0),
            ("middle", "Middle", "", "ALIGN_MIDDLE", 1),
            ("bottom", "Bottom", "", "ALIGN_BOTTOM", 2),
        ],
        default="middle",
        name="Vertical Alignment",
        update=update_text_alignment,
    )

    if TYPE_CHECKING:
        is_editing: bool
        literals: bpy.types.bpy_prop_collection_idprop[LiteralProps]
        newline_at: int
        symbol: Union[str, Literal["NO SYMBOL", "CUSTOM SYMBOL"]]
        custom_symbol: str
        font_size: str
        align_horizontal: str
        align_vertical: str

    def get_symbol(self) -> Union[str, None]:
        if self.symbol == "NO SYMBOL":
            return None
        elif self.symbol == "CUSTOM SYMBOL":
            return self.custom_symbol or None
        else:
            return self.symbol

    def set_symbol(self, symbol: Union[str, None]):
        if not symbol:
            self.property_unset("symbol")
            self.property_unset("custom_symbol")
        elif symbol in tool.Drawing.DEFAULT_SYMBOLS:
            self.symbol = symbol
            self.property_unset("custom_symbol")
        else:
            self.symbol = "CUSTOM SYMBOL"
            self.custom_symbol = symbol

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
            "Symbol": self.get_symbol(),
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
    tag_rotation_mode: bpy.props.EnumProperty(
        name="Tag Rotation Mode",
        description="How to orient the tag relative to the tagged object",
        items=[
            ("NONE", "No Rotation", "Keep tag in default orientation"),
            ("LOCAL_X", "Local X Axis", "Align tag with object's local X axis"),
            ("LOCAL_Y", "Local Y Axis", "Align tag with object's local Y axis"),
            ("LOCAL_Z", "Local Z Axis", "Align tag with object's local Z axis"),
            ("CAMERA_Horizontal", "Camera Horizontal", "Align tag with camera X axis"),
            ("CAMERA_Vertical", "Camera Vertical", "Align tag with camera Y axis"),
        ],
        default="NONE",
    )

    if TYPE_CHECKING:
        object_type: str
        relating_type_id: str
        create_representation_for_type: bool
        is_adding_type: bool
        type_name: str
