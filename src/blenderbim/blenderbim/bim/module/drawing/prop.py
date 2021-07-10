import os
import bpy
import blenderbim.bim.module.drawing.annotation as annotation
import blenderbim.bim.module.drawing.decoration as decoration
from pathlib import Path
from blenderbim.bim.prop import Attribute, StrProperty
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
)


diagram_scales_enum = []
titleblocks_enum = []
sheets_enum = []
vector_styles_enum = []


def purge():
    global diagram_scales_enum
    global titleblocks_enum
    global sheets_enum
    global vector_styles_enum
    diagram_scales_enum = []
    titleblocks_enum = []
    sheets_enum = []
    vector_styles_enum = []


def getDiagramScales(self, context):
    global diagram_scales_enum
    if (
        len(diagram_scales_enum) < 1
        or (bpy.context.scene.unit_settings.system == "IMPERIAL" and len(diagram_scales_enum) == 13)
        or (bpy.context.scene.unit_settings.system == "METRIC" and len(diagram_scales_enum) == 31)
    ):
        if bpy.context.scene.unit_settings.system == "IMPERIAL":
            diagram_scales_enum = [
                ("CUSTOM", "Custom", ""),
                ("1'=1'-0\"|1/1", "1'=1'-0\"", ""),
                ('6"=1\'-0"|1/6', '6"=1\'-0"', ""),
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


def updateDrawingName(self, context):
    if not self.camera:
        return
    if self.camera.name == self.name:
        return
    self.camera.name = "IfcAnnotation/{}".format(self.name)
    unique_name = "/".join(self.camera.name.split("/")[1:])
    self.camera.users_collection[0].name = "IfcGroup/{}".format(unique_name)
    if self.name != unique_name:
        self.name = unique_name


def refreshActiveDrawingIndex(self, context):
    bpy.ops.bim.activate_view(drawing_index=context.scene.DocProperties.active_drawing_index)


def getTitleblocks(self, context):
    global titleblocks_enum
    if len(titleblocks_enum) < 1:
        titleblocks_enum.clear()
        for filename in Path(os.path.join(context.scene.BIMProperties.data_dir, "templates", "titleblocks")).glob(
            "*.svg"
        ):
            f = str(filename.stem)
            titleblocks_enum.append((f, f, ""))
    return titleblocks_enum


def refreshTitleblocks(self, context):
    global titleblocks_enum
    titleblocks_enum.clear()
    getTitleblocks(self, context)


def toggleDecorations(self, context):
    toggle = self.should_draw_decorations
    if toggle:
        decoration.DecorationsHandler.install(context)
    else:
        decoration.DecorationsHandler.uninstall()


def getVectorStyles(self, context):
    global vector_styles_enum
    if len(vector_styles_enum) < 1:
        sheets_enum.clear()
        for filename in Path(os.path.join(context.scene.BIMProperties.data_dir, "styles")).glob("*.css"):
            f = str(filename.stem)
            vector_styles_enum.append((f, f, ""))
    return vector_styles_enum


def refreshFontSize(self, context):
    annotation.Annotator.resize_text(context.active_object)


class Variable(PropertyGroup):
    name: StringProperty(name="Name")
    prop_key: StringProperty(name="Property Key")


class Drawing(PropertyGroup):
    name: StringProperty(name="Name", update=updateDrawingName)
    camera: PointerProperty(name="Camera", type=bpy.types.Object)


class Schedule(PropertyGroup):
    name: StringProperty(name="Name")
    file: StringProperty(name="File")


class Sheet(PropertyGroup):
    def set_name(self, new):
        old = self.get("name")
        path = os.path.join(bpy.context.scene.BIMProperties.data_dir, "sheets")
        if old and os.path.isfile(os.path.join(path, old + ".svg")):
            os.rename(os.path.join(path, old + ".svg"), os.path.join(path, new + ".svg"))
        self["name"] = new

    def get_name(self):
        return self.get("name")

    name: StringProperty(name="Name", get=get_name, set=set_name)
    drawings: CollectionProperty(name="Drawings", type=Drawing)
    active_drawing_index: IntProperty(name="Active Drawing Index")


class DrawingStyle(PropertyGroup):
    name: StringProperty(name="Name")
    raster_style: StringProperty(name="Raster Style")
    render_type: EnumProperty(
        items=[
            ("NONE", "None", ""),
            ("DEFAULT", "Default", ""),
            ("VIEWPORT", "Viewport", ""),
        ],
        name="Render Type",
        default="VIEWPORT",
    )
    vector_style: EnumProperty(items=getVectorStyles, name="Vector Style")
    include_query: StringProperty(name="Include Query")
    exclude_query: StringProperty(name="Exclude Query")
    attributes: CollectionProperty(name="Attributes", type=StrProperty)


class DocProperties(PropertyGroup):
    has_underlay: BoolProperty(name="Underlay", default=False)
    has_linework: BoolProperty(name="Linework", default=True)
    has_annotation: BoolProperty(name="Annotation", default=True)
    should_use_underlay_cache: BoolProperty(name="Use Underlay Cache", default=False)
    should_use_linework_cache: BoolProperty(name="Use Linework Cache", default=False)
    should_use_annotation_cache: BoolProperty(name="Use Annotation Cache", default=False)
    should_extract: BoolProperty(name="Should Extract", default=True)
    drawings: CollectionProperty(name="Drawings", type=Drawing)
    active_drawing_index: IntProperty(name="Active Drawing Index", update=refreshActiveDrawingIndex)
    current_drawing_index: IntProperty(name="Current Drawing Index")
    schedules: CollectionProperty(name="Schedules", type=Schedule)
    active_schedule_index: IntProperty(name="Active Schedule Index")
    titleblock: EnumProperty(items=getTitleblocks, name="Titleblock", update=refreshTitleblocks)
    sheets: CollectionProperty(name="Sheets", type=Sheet)
    active_sheet_index: IntProperty(name="Active Sheet Index")
    ifc_files: CollectionProperty(name="IFCs", type=StrProperty)
    drawing_styles: CollectionProperty(name="Drawing Styles", type=DrawingStyle)
    should_draw_decorations: BoolProperty(name="Should Draw Decorations", update=toggleDecorations)
    decorations_colour: FloatVectorProperty(
        name="Decorations Colour", subtype="COLOR", default=(1, 0, 0, 1), min=0.0, max=1.0, size=4
    )


class BIMCameraProperties(PropertyGroup):
    view_name: StringProperty(name="View Name")
    target_view: EnumProperty(
        items=[
            ("PLAN_VIEW", "PLAN_VIEW", ""),
            ("ELEVATION_VIEW", "ELEVATION_VIEW", ""),
            ("SECTION_VIEW", "SECTION_VIEW", ""),
            ("REFLECTED_PLAN_VIEW", "REFLECTED_PLAN_VIEW", ""),
            ("MODEL_VIEW", "MODEL_VIEW", ""),
        ],
        name="Target View",
        default="PLAN_VIEW",
    )
    diagram_scale: EnumProperty(items=getDiagramScales, name="Drawing Scale")
    custom_diagram_scale: StringProperty(name="Custom Scale")
    raster_x: IntProperty(name="Raster X", default=1000)
    raster_y: IntProperty(name="Raster Y", default=1000)
    is_nts: BoolProperty(name="Is NTS")
    cut_objects: EnumProperty(
        items=[
            (
                ".IfcWall|.IfcSlab|.IfcCurtainWall|.IfcStair|.IfcStairFlight|.IfcColumn|.IfcBeam|.IfcMember|.IfcCovering|.IfcSpace",
                "Overall Plan / Section",
                "",
            ),
            (".IfcElement", "Detail Drawing", ""),
            ("CUSTOM", "Custom", ""),
        ],
        name="Cut Objects",
    )
    cut_objects_custom: StringProperty(name="Custom Cut")
    active_drawing_style_index: IntProperty(name="Active Drawing Style Index")


class BIMTextProperties(PropertyGroup):
    font_size: EnumProperty(
        items=[
            ("1.8", "1.8 - Small", ""),
            ("2.5", "2.5 - Regular", ""),
            ("3.5", "3.5 - Large", ""),
            ("5.0", "5.0 - Header", ""),
            ("7.0", "7.0 - Title", ""),
        ],
        update=refreshFontSize,
        name="Font Size",
    )
    symbol: EnumProperty(
        items=[
            ("None", "None", ""),
            ("rectangle-tag", "Rectangle Tag", ""),
            ("door-tag", "Door Tag", ""),
        ],
        update=refreshFontSize,
        name="Symbol",
    )
    related_element: PointerProperty(name="Related Element", type=bpy.types.Object)
    variables: CollectionProperty(name="Variables", type=Variable)
