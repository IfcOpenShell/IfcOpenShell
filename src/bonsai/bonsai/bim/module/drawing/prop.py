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
import ifcopenshell.util.element
import bonsai.tool as tool
import bonsai.core.drawing as core
import bonsai.bim.module.drawing.annotation as annotation
import bonsai.bim.module.drawing.decoration as decoration
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


diagram_scales_enum = []


def purge():
    global diagram_scales_enum
    diagram_scales_enum = []


def update_target_view(self, context):
    DrawingsData.data["location_hint"] = DrawingsData.location_hint()


def get_location_hint(self, context):
    if not DrawingsData.is_loaded:
        DrawingsData.load()
    return DrawingsData.data["location_hint"]


def update_diagram_scale(self, context):
    if not self.update_props:
        return
    if not context.scene.camera or context.scene.camera.data != self.id_data:
        return
    element = tool.Ifc.get_entity(context.scene.camera)
    if not element:
        return
    try:
        element = (
            tool.Ifc.get()
            .by_id(self.id_data.BIMMeshProperties.ifc_definition_id)
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
        pset = ifcopenshell.api.run("pset.add_pset", tool.Ifc.get(), product=element, name="EPset_Drawing")
    ifcopenshell.api.run("pset.edit_pset", tool.Ifc.get(), pset=pset, properties=diagram_scale)


def update_is_nts(self, context):
    if not self.update_props:
        return
    if not context.scene.camera or context.scene.camera.data != self.id_data:
        return
    element = tool.Ifc.get_entity(context.scene.camera)
    if not element:
        return
    try:
        element = (
            tool.Ifc.get()
            .by_id(self.id_data.BIMMeshProperties.ifc_definition_id)
            .OfProductRepresentation[0]
            .ShapeOfProduct[0]
        )
    except:
        return
    pset = ifcopenshell.util.element.get_pset(element, "EPset_Drawing")
    if pset:
        pset = tool.Ifc.get().by_id(pset["id"])
    else:
        pset = ifcopenshell.api.run("pset.add_pset", tool.Ifc.get(), product=element, name="EPset_Drawing")
    ifcopenshell.api.run("pset.edit_pset", tool.Ifc.get(), pset=pset, properties={"IsNTS": self.is_nts})


def get_diagram_scales(self, context):
    global diagram_scales_enum
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
    scene = bpy.context.scene
    drawing_styles = [s.name for s in scene.DocProperties.drawing_styles if s.name != self.name]
    new_value = tool.Blender.ensure_unique_name(new_value, drawing_styles)
    old_value = self.name
    self["name"] = new_value
    bpy.ops.bim.save_drawing_styles_data(rename_style=True, rename_style_from=old_value, rename_style_to=new_value)


def update_document_name(self, context):
    document = tool.Ifc.get().by_id(self.ifc_definition_id)
    core.update_document_name(tool.Ifc, tool.Drawing, document=document, name=self.name)


def update_has_underlay(self, context):
    update_layer(self, context, "HasUnderlay", self.has_underlay)
    # making sure that camera is active
    if self.has_underlay and (context.scene.camera and context.scene.camera.data == self.id_data):
        bpy.ops.bim.reload_drawing_styles()
        bpy.ops.bim.activate_drawing_style()


def update_has_linework(self, context):
    update_layer(self, context, "HasLinework", self.has_linework)


def update_has_annotation(self, context):
    update_layer(self, context, "HasAnnotation", self.has_annotation)


def update_layer(self, context, name, value):
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
        pset = ifcopenshell.api.run("pset.add_pset", tool.Ifc.get(), product=element, name="EPset_Drawing")
    ifcopenshell.api.run("pset.edit_pset", tool.Ifc.get(), pset=pset, properties={name: value})


def get_titleblocks(self, context):
    if not SheetsData.is_loaded:
        SheetsData.load()
    return SheetsData.data["titleblocks"]


def update_titleblocks(self, context):
    SheetsData.data["titleblocks"] = SheetsData.titleblocks()


def update_should_draw_decorations(self, context):
    if self.should_draw_decorations:
        # TODO: design a proper text variable templating renderer
        collection = context.scene.camera.BIMObjectProperties.collection
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


class Drawing(PropertyGroup):
    ifc_definition_id: IntProperty(name="IFC Definition ID")
    name: StringProperty(name="Name", update=update_drawing_name)
    target_view: StringProperty(name="Target View")
    is_selected: BoolProperty(name="Is Selected", default=True)
    is_drawing: BoolProperty(name="Is Drawing", default=False)
    is_expanded: BoolProperty(name="Is Expanded", default=True)


class Document(PropertyGroup):
    ifc_definition_id: IntProperty(name="IFC Definition ID")
    name: StringProperty(name="Name", update=update_document_name)
    identification: StringProperty(name="Identification")


class Sheet(PropertyGroup):
    ifc_definition_id: IntProperty(name="IFC Definition ID")
    identification: StringProperty(name="Identification")
    name: StringProperty(name="Name")
    is_sheet: BoolProperty(name="Is Sheet", default=False)
    reference_type: StringProperty(name="Reference Type")
    is_expanded: BoolProperty(name="Is Expanded", default=False)


class DrawingStyle(PropertyGroup):
    name: StringProperty(name="Name", get=get_drawing_style_name, set=set_drawing_style_name)
    raster_style: StringProperty(name="Raster Style", default="{}")
    render_type: EnumProperty(
        items=[
            ("NONE", "None", ""),
            ("DEFAULT", "Default", ""),
            ("VIEWPORT", "Viewport", ""),
        ],
        name="Render Type",
        default="VIEWPORT",
    )
    include_query: StringProperty(name="Include Query")
    exclude_query: StringProperty(name="Exclude Query")
    attributes: CollectionProperty(name="Attributes", type=StrProperty)


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
        items=[
            ("PLAN_VIEW", "Plan", ""),
            ("ELEVATION_VIEW", "Elevation", ""),
            ("SECTION_VIEW", "Section", ""),
            ("REFLECTED_PLAN_VIEW", "RCP", ""),
            ("MODEL_VIEW", "Model", ""),
        ],
        name="Target View",
        default="PLAN_VIEW",
        update=update_target_view,
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


class BIMCameraProperties(PropertyGroup):
    linework_mode: EnumProperty(
        items=[
            ("OPENCASCADE", "OpenCASCADE", "Slower, more accurate, with more features"),
            ("FREESTYLE", "Freestyle", "Faster, less accurate, no fill support"),
        ],
        default="OPENCASCADE",
        name="Linework Mode",
    )
    fill_mode: EnumProperty(
        items=[
            ("NONE", "None", "Disable filling areas seen in projection"),
            ("SHAPELY", "Shapely", "Recommended"),
            ("SVGFILL", "SVGFill", "Experimental"),
        ],
        default="NONE",
        name="Fill Mode",
    )
    cut_mode: EnumProperty(
        items=[
            ("BISECT", "Bisect", "Faster, more forgiving to bad geometry"),
            ("OPENCASCADE", "OpenCASCADE", "More technically correct"),
        ],
        default="BISECT",
        name="Cut Mode",
    )
    has_underlay: BoolProperty(name="Underlay", default=False, update=update_has_underlay)
    has_linework: BoolProperty(name="Linework", default=True, update=update_has_linework)
    has_annotation: BoolProperty(name="Annotation", default=True, update=update_has_annotation)
    representation: StringProperty(name="Representation")
    view_name: StringProperty(name="View Name")
    diagram_scale: EnumProperty(items=get_diagram_scales, name="Drawing Scale", update=update_diagram_scale)
    custom_scale_numerator: bpy.props.StringProperty(default="1", update=update_diagram_scale)
    custom_scale_denominator: bpy.props.StringProperty(default="100", update=update_diagram_scale)
    raster_x: IntProperty(name="Raster X", default=1000)
    raster_y: IntProperty(name="Raster Y", default=1000)
    dpi: IntProperty(name="DPI", default=75)
    width: FloatProperty(name="Width", default=50, subtype="DISTANCE")
    height: FloatProperty(name="Height", default=50, subtype="DISTANCE")
    is_nts: BoolProperty(name="Is NTS", update=update_is_nts)
    active_drawing_style_index: IntProperty(name="Active Drawing Style Index")
    filter_mode: StringProperty(name="Filter Mode", default="NONE")
    include_filter_groups: CollectionProperty(type=BIMFilterGroup, name="Include Filter")
    exclude_filter_groups: CollectionProperty(type=BIMFilterGroup, name="Exclude Filter")
    update_props: BoolProperty(name="Enable Props Auto Update", default=True)

    # For now, this JSON dump are all the parameters that determine a camera's "Block representation"
    # By checking this, you will know whether or not the camera IFC representation needs to be refreshed
    def update_representation(self, obj):
        representation = json.dumps(
            {
                "matrix": [list(x) for x in obj.matrix_world],
                "raster_x": self.raster_x,
                "raster_y": self.raster_y,
                "ortho_scale": obj.data.ortho_scale,
                "clip_end": obj.data.clip_end,
            }
        )
        if self.representation != representation:
            self.representation = representation
            return True
        return False


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


class Literal(PropertyGroup):
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
    # Current text value with evaluated experessions stored in `value`.
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


class BIMTextProperties(PropertyGroup):
    is_editing: BoolProperty(name="Is Editing", default=False)
    literals: CollectionProperty(name="Literals", type=Literal)
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

    def get_text_edited_data(self):
        """should be called only if `is_editing`
        otherwise should use `DecoratorData.get_ifc_text_data(obj)` instead
        because this data could be out of date
        """
        literals_data = []
        for literal in self.literals:
            literal_data = literal.get_literal_edited_data()
            literals_data.append(literal_data)
        text_data = {
            "Literals": literals_data,
            "FontSize": float(self.font_size),
        }
        return text_data


def relating_product_poll(self: "BIMAssignedProductProperties", obj: bpy.types.Object) -> bool:
    if not tool.Ifc.get_entity(obj):
        return False
    return True


class BIMAssignedProductProperties(PropertyGroup):
    is_editing_product: BoolProperty(name="Is Editing Product", default=False)
    relating_product: PointerProperty(name="Relating Product", type=bpy.types.Object, poll=relating_product_poll)


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
