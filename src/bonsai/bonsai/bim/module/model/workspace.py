# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021, 2022 Dion Moult <dion@thinkmoult.com>
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
import sys
import bpy
import bpy.utils.previews
import bonsai.bim
import bonsai.tool as tool
import bonsai.core.model as core
from bonsai.bim.module.model.wall import DumbWallJoiner
from bonsai.bim.helper import prop_with_search, draw_attribute
from bpy.types import WorkSpaceTool, Menu
from bonsai.bim.module.model.data import AuthoringData, ItemData
from bonsai.bim.module.system.data import PortData
from bonsai.bim.module.model.prop import get_ifc_class
from typing import Optional, Union
from functools import partial


def load_custom_icons():
    global custom_icon_previews, display_mode
    if display_mode is None:
        display_mode = tool.Blender.detect_icon_color_mode("user_interface.wcol_tool.text")

    icons_dir = os.path.join(os.path.dirname(__file__), "..", "..", "data", "icons")
    custom_icon_previews = bpy.utils.previews.new()

    prefix = f"{display_mode}_"

    for entry in os.scandir(icons_dir):
        if entry.name.endswith(".png") and entry.name.startswith(prefix):
            name = os.path.splitext(entry.name)[0].replace(prefix, "", 1)
            custom_icon_previews.load(name.upper(), entry.path, "IMAGE")


def unload_custom_icons():
    global custom_icon_previews
    if custom_icon_previews:
        bpy.utils.previews.remove(custom_icon_previews)
        custom_icon_previews = None


class BimTool(WorkSpaceTool):
    bl_space_type = "VIEW_3D"
    bl_context_mode = "OBJECT"
    bl_idname = "bim.bim_tool"
    bl_label = "Multi Object Tool"
    bl_description = "Create and edit elements by construction class"
    bl_icon = os.path.join(os.path.dirname(__file__), "ops.authoring.bim")
    bl_widget = None
    bl_keymap = tool.Blender.get_default_selection_keypmap() + (
        # ("bim.wall_tool_op", {"type": 'MOUSEMOVE', "value": 'ANY'}, {"properties": []}),
        # ("mesh.add_wall", {"type": 'LEFTMOUSE', "value": 'PRESS'}, {"properties": []}),
        # ("bim.sync_modeling", {"type": 'MOUSEMOVE', "value": 'ANY'}, {"properties": []}),
        ("bim.hotkey", {"type": "A", "value": "PRESS", "shift": True}, {"properties": [("hotkey", "S_A")]}),
        ("bim.hotkey", {"type": "B", "value": "PRESS", "shift": True}, {"properties": [("hotkey", "S_B")]}),
        ("bim.hotkey", {"type": "C", "value": "PRESS", "shift": True}, {"properties": [("hotkey", "S_C")]}),
        ("bim.hotkey", {"type": "E", "value": "PRESS", "shift": True}, {"properties": [("hotkey", "S_E")]}),
        ("bim.hotkey", {"type": "F", "value": "PRESS", "shift": True}, {"properties": [("hotkey", "S_F")]}),
        ("bim.hotkey", {"type": "G", "value": "PRESS", "shift": True}, {"properties": [("hotkey", "S_G")]}),
        ("bim.hotkey", {"type": "K", "value": "PRESS", "shift": True}, {"properties": [("hotkey", "S_K")]}),
        ("bim.hotkey", {"type": "M", "value": "PRESS", "shift": True}, {"properties": [("hotkey", "S_M")]}),
        ("bim.hotkey", {"type": "O", "value": "PRESS", "shift": True}, {"properties": [("hotkey", "S_O")]}),
        ("bim.hotkey", {"type": "L", "value": "PRESS", "shift": True}, {"properties": [("hotkey", "S_L")]}),
        ("bim.hotkey", {"type": "Q", "value": "PRESS", "shift": True}, {"properties": [("hotkey", "S_Q")]}),
        ("bim.hotkey", {"type": "R", "value": "PRESS", "shift": True}, {"properties": [("hotkey", "S_R")]}),
        ("bim.hotkey", {"type": "T", "value": "PRESS", "shift": True}, {"properties": [("hotkey", "S_T")]}),
        ("bim.hotkey", {"type": "U", "value": "PRESS", "shift": True}, {"properties": [("hotkey", "S_U")]}),
        ("bim.hotkey", {"type": "V", "value": "PRESS", "shift": True}, {"properties": [("hotkey", "S_V")]}),
        ("bim.hotkey", {"type": "X", "value": "PRESS", "shift": True}, {"properties": [("hotkey", "S_X")]}),
        ("bim.hotkey", {"type": "Y", "value": "PRESS", "shift": True}, {"properties": [("hotkey", "S_Y")]}),
        ("bim.hotkey", {"type": "D", "value": "PRESS", "alt": True}, {"properties": [("hotkey", "A_D")]}),
        ("bim.hotkey", {"type": "E", "value": "PRESS", "alt": True}, {"properties": [("hotkey", "A_E")]}),
        ("bim.hotkey", {"type": "O", "value": "PRESS", "alt": True}, {"properties": [("hotkey", "A_O")]}),
        ("bim.hotkey", {"type": "P", "value": "PRESS", "ctrl": True}, {"properties": [("hotkey", "C_P")]}),
        ("bim.hotkey", {"type": "P", "value": "PRESS", "alt": True}, {"properties": [("hotkey", "A_P")]}),
    )
    ifc_element_type = "all"

    @classmethod
    def draw_settings(
        cls, context: bpy.types.Context, layout: bpy.types.UILayout, ws_tool: bpy.types.WorkSpaceTool
    ) -> None:
        props = tool.Geometry.get_geometry_props()
        ifc_element_type = None if cls.ifc_element_type == "all" else cls.ifc_element_type
        if props.mode == "ITEM":
            EditItemUI.draw(context, layout)
        elif (
            active_ifc_object := (context.active_object and tool.Ifc.get_entity(context.active_object))
        ) and context.selected_objects:
            EditObjectUI.draw(context, layout, ifc_element_type=ifc_element_type)
        else:
            CreateObjectUI.draw(context, layout, ifc_element_type=ifc_element_type)


class WallTool(BimTool):
    bl_space_type = "VIEW_3D"
    bl_context_mode = "OBJECT"
    bl_idname = "bim.wall_tool"
    bl_label = "Wall Tool"
    bl_description = "Create and edit walls, including solid, movable, parapet, partitioning, plumbing, sheer, standard, polygonal, and elemented walls"
    bl_icon = os.path.join(os.path.dirname(__file__), "ops.authoring.wall")
    bl_widget = None
    ifc_element_type = "IfcWallType"


class RailingTool(BimTool):
    bl_space_type = "VIEW_3D"
    bl_context_mode = "OBJECT"
    bl_idname = "bim.railing_tool"
    bl_label = "Railing Tool"
    bl_description = "Create and edit handrail, guardrail, and balustrade railings"
    bl_icon = os.path.join(os.path.dirname(__file__), "ops.authoring.railing")
    bl_widget = None
    ifc_element_type = "IfcRailingType"


class SlabTool(BimTool):
    bl_space_type = "VIEW_3D"
    bl_context_mode = "OBJECT"
    bl_idname = "bim.slab_tool"
    bl_label = "Slab Tool"
    bl_description = "Create and edit slabs, including floor, roof, landing, and baseslab slabs"
    bl_icon = os.path.join(os.path.dirname(__file__), "ops.authoring.slab")
    bl_widget = None
    ifc_element_type = "IfcSlabType"


class RoofTool(BimTool):
    bl_space_type = "VIEW_3D"
    bl_context_mode = "OBJECT"
    bl_idname = "bim.roof_tool"
    bl_label = "Roof Tool"
    bl_description = "Create and edit roofs, including flat, shed, gable, hip, hipped gable, gambrel, mansard, barrel, rainbox, butterly, pavilion, dome, and freeform roofs"
    bl_icon = os.path.join(os.path.dirname(__file__), "ops.authoring.roof")
    bl_widget = None
    ifc_element_type = "IfcRoofType"


class DoorTool(BimTool):
    bl_space_type = "VIEW_3D"
    bl_context_mode = "OBJECT"
    bl_idname = "bim.door_tool"
    bl_label = "Door Tool"
    bl_description = "Create and edit doors, gates, and trap doors"
    bl_icon = os.path.join(os.path.dirname(__file__), "ops.authoring.door")
    bl_widget = None
    ifc_element_type = "IfcDoorType"


class WindowTool(BimTool):
    bl_space_type = "VIEW_3D"
    bl_context_mode = "OBJECT"
    bl_idname = "bim.window_tool"
    bl_label = "Window Tool"
    bl_description = "Create and edit windows, skylights, and lightdomes"
    bl_icon = os.path.join(os.path.dirname(__file__), "ops.authoring.window")
    bl_widget = None
    ifc_element_type = "IfcWindowType"


class StairFlightTool(BimTool):
    bl_space_type = "VIEW_3D"
    bl_context_mode = "OBJECT"
    bl_idname = "bim.stair_flight_tool"
    bl_label = "Stair Flight Tool"
    bl_description = "Create and edit stairs, including straight run, two straight run, quarter winding, quarter turn, half winding, half turn, two quarter winding, two wuarter turn, spiral, double return, curved run, and two curved run stairs"
    bl_icon = os.path.join(os.path.dirname(__file__), "ops.authoring.stairflight")
    bl_widget = None
    ifc_element_type = "IfcStairFlightType"


class RampFlightTool(BimTool):
    bl_space_type = "VIEW_3D"
    bl_context_mode = "OBJECT"
    bl_idname = "bim.ramp_flight_tool"
    bl_label = "Ramp Flight Tool"
    bl_description = "Create and edit straight and spiral ramps"
    bl_icon = os.path.join(os.path.dirname(__file__), "ops.authoring.rampflight")
    bl_widget = None
    ifc_element_type = "IfcRampFlightType"


class FurnitureTool(BimTool):
    bl_space_type = "VIEW_3D"
    bl_context_mode = "OBJECT"
    bl_idname = "bim.furniture_tool"
    bl_label = "Furniture Tool"
    bl_description = "Create and edit furniture, including table, desk, bed, file cabinet, shelve, and sofa"
    bl_icon = os.path.join(os.path.dirname(__file__), "ops.authoring.furniture")
    bl_widget = None
    ifc_element_type = "IfcFurnitureType"


class SanitaryTerminalTool(BimTool):
    bl_space_type = "VIEW_3D"
    bl_context_mode = "OBJECT"
    bl_idname = "bim.sanitary_terminal_tool"
    bl_label = "Sanitary Terminal Tool"
    bl_description = "Create and edit sanitary terminals, including bath, bidet, cister, shower, sink, sanitary fountain, toilet pan, urinal, wash hand basin, and wc seat"
    bl_icon = os.path.join(os.path.dirname(__file__), "ops.authoring.sanitaryterminal")
    bl_widget = None
    ifc_element_type = "IfcSanitaryTerminalType"


class LightFixtureTool(BimTool):
    bl_space_type = "VIEW_3D"
    bl_context_mode = "OBJECT"
    bl_idname = "bim.light_fixture_tool"
    bl_label = "Light Fixture Tool"
    bl_description = "Create and edit point source, direction source, and security lighting"
    bl_icon = os.path.join(os.path.dirname(__file__), "ops.authoring.lightfixture")
    bl_widget = None
    ifc_element_type = "IfcLightFixtureType"


class ElectricApplianceTool(BimTool):
    bl_space_type = "VIEW_3D"
    bl_context_mode = "OBJECT"
    bl_idname = "bim.electric_appliance_tool"
    bl_label = "Electric Appliance Tool"
    bl_description = "Create and edit electric appliances, including dishwasher, electric cooker, freezer, fridge freezer, microwave, refrigerator, kitchen machines, vending machines, washing machines, as well as freestanding electric heaters, fans, water heaters, and water coolers."
    bl_icon = os.path.join(os.path.dirname(__file__), "ops.authoring.electricappliance")
    bl_widget = None
    ifc_element_type = "IfcElectricApplianceType"


class GeographicElement(BimTool):
    bl_space_type = "VIEW_3D"
    bl_context_mode = "OBJECT"
    bl_idname = "bim.geographic_element_tool"
    bl_label = "Geographic Element Tool"
    bl_description = "Create and edit terrain and vegetation landscape geographic elements"
    bl_icon = os.path.join(os.path.dirname(__file__), "ops.authoring.geographicelement")
    bl_widget = None
    ifc_element_type = "IfcGeographicElementType"


class ColumnTool(BimTool):
    bl_space_type = "VIEW_3D"
    bl_context_mode = "OBJECT"
    bl_idname = "bim.column_tool"
    bl_label = "Column Tool"
    bl_description = "Create and edit columns and pilasters"
    bl_icon = os.path.join(os.path.dirname(__file__), "ops.authoring.column")
    bl_widget = None
    ifc_element_type = "IfcColumnType"


class BeamTool(BimTool):
    bl_space_type = "VIEW_3D"
    bl_context_mode = "OBJECT"
    bl_idname = "bim.beam_tool"
    bl_label = "Beam Tool"
    bl_description = "Create and edit beams, joists, hollowcores, lintels, spandrels, and  T-beams"
    bl_icon = os.path.join(os.path.dirname(__file__), "ops.authoring.beam")
    bl_widget = None
    ifc_element_type = "IfcBeamType"


class MemberTool(BimTool):
    bl_space_type = "VIEW_3D"
    bl_context_mode = "OBJECT"
    bl_idname = "bim.member_tool"
    bl_label = "Member Tool"
    bl_description = "Create and edit braces, chords, collars, members, mullions, plates, posts, purlins, rafters, stringers, struts, and studs"
    bl_icon = os.path.join(os.path.dirname(__file__), "ops.authoring.member")
    bl_widget = None
    ifc_element_type = "IfcMemberType"


class PlateTool(BimTool):
    bl_space_type = "VIEW_3D"
    bl_context_mode = "OBJECT"
    bl_idname = "bim.plate_tool"
    bl_label = "Plate Tool"
    bl_description = "Create and edit curtain panel and sheet plates"
    bl_icon = os.path.join(os.path.dirname(__file__), "ops.authoring.plate")
    bl_widget = None
    ifc_element_type = "IfcPlateType"


class PileTool(BimTool):
    bl_space_type = "VIEW_3D"
    bl_context_mode = "OBJECT"
    bl_idname = "bim.pile_tool"
    bl_label = "Pile Tool"
    bl_description = (
        "Create and edit piles, including bored, driven, jet grouting, cohesion, friction, and support piles"
    )
    bl_icon = os.path.join(os.path.dirname(__file__), "ops.authoring.pile")
    bl_widget = None
    ifc_element_type = "IfcPileType"


class FootingTool(BimTool):
    bl_space_type = "VIEW_3D"
    bl_context_mode = "OBJECT"
    bl_idname = "bim.footing_tool"
    bl_label = "Footing Tool"
    bl_description = (
        "Create and edit footings, including pad, beam and strip footings, as well as pile caps and caisson foundations"
    )
    bl_icon = os.path.join(os.path.dirname(__file__), "ops.authoring.footing")
    bl_widget = None
    ifc_element_type = "IfcFootingType"


class DuctTool(BimTool):
    bl_space_type = "VIEW_3D"
    bl_context_mode = "OBJECT"
    bl_idname = "bim.duct_tool"
    bl_label = "Duct Tool"
    bl_description = "Create and edit rigid and flexible duct segments"
    bl_icon = os.path.join(os.path.dirname(__file__), "ops.authoring.duct")
    bl_widget = None
    ifc_element_type = "IfcDuctSegmentType"


class CableCarrierTool(BimTool):
    bl_space_type = "VIEW_3D"
    bl_context_mode = "OBJECT"
    bl_idname = "bim.cable_carrier_tool"
    bl_label = "Cable Carrier Tool"
    bl_description = "Create and edit cable ladder, tray, trunking, and conduite segments"
    bl_icon = os.path.join(os.path.dirname(__file__), "ops.authoring.cablecarrier")
    bl_widget = None
    ifc_element_type = "IfcCableCarrierSegmentType"


class PipeTool(BimTool):
    bl_space_type = "VIEW_3D"
    bl_context_mode = "OBJECT"
    bl_idname = "bim.pipe_tool"
    bl_label = "Pipe Tool"
    bl_description = "Create and edit culvert, flexible, rigid, gutter, and spool pipe segments"
    bl_icon = os.path.join(os.path.dirname(__file__), "ops.authoring.pipe")
    bl_widget = None
    ifc_element_type = "IfcPipeSegmentType"


class CableTool(BimTool):
    bl_space_type = "VIEW_3D"
    bl_context_mode = "OBJECT"
    bl_idname = "bim.cable_tool"
    bl_label = "Cable Tool"
    bl_description = "Create and edit bus bar, cable, conductor, and core segments"
    bl_icon = os.path.join(os.path.dirname(__file__), "ops.authoring.cable")
    bl_widget = None
    ifc_element_type = "IfcCableSegmentType"


add_layout_hotkey_operator = partial(tool.Blender.add_layout_hotkey_operator, tool_name="bim", module_name=__name__)


def format_ifc_camel_case(string):
    string = string.replace("Ifc", "")
    return "".join(" " + char if char.isupper() else char for char in string).strip()


class EditItemUI:
    layout: bpy.types.UILayout

    @classmethod
    def draw(cls, context: bpy.types.Context, layout: bpy.types.UILayout) -> None:
        if not ItemData.is_loaded:
            ItemData.load()
        if not AuthoringData.is_loaded:
            AuthoringData.load()

        cls.layout = layout
        row = cls.layout.row()
        row.label(text="Item Mode", icon="MESH_DATA")
        row = cls.layout.row()
        row.label(text="Context: " + ItemData.data["representation_identifier"], icon="SCENE_DATA")
        row = cls.layout.row()
        row.label(text="Type: " + ItemData.data["representation_type"], icon="OUTLINER_OB_MESH")
        cls.layout.menu("BIM_MT_add_representation_item", icon="ADD")
        if not AuthoringData.data["is_representation_item_active"]:
            return
        obj = context.active_object
        assert obj

        mesh_props = tool.Geometry.get_mesh_props(obj.data)
        if AuthoringData.data["is_representation_item_swept_solid"]:
            # TODO: support EndSweptArea for IfcRevolvedAreaSolidTapered,
            # will need to add second attribute for this.
            row = cls.layout.row(align=True)
            row.prop(mesh_props, "item_profile")
            if mesh_props.item_profile == "-":
                op = row.operator("bim.name_profile", text="", icon="TAG")
                op.extrusion_item_obj = obj.name
            else:
                op = row.operator("bim.profiles_ui_select", icon="ZOOM_SELECTED", text="")
                op.profile_id = int(mesh_props.item_profile)

        for item_attribute in mesh_props.item_attributes:
            row = cls.layout.row()
            draw_attribute(item_attribute, cls.layout)
        if len(mesh_props.item_attributes) or AuthoringData.data["is_representation_item_swept_solid"]:
            row = cls.layout.row()
            row.operator("bim.update_item_attributes", icon="FILE_REFRESH", text="")


class BIM_MT_add_representation_item(Menu):
    bl_idname = "BIM_MT_add_representation_item"
    bl_label = "Add Item"

    def draw(self, context):
        if not ItemData.is_loaded:
            ItemData.load()

        if ItemData.data["representation_usage"]:
            self.layout.operator("bim.add_half_space_solid_item", icon="ORIENTATION_NORMAL", text="Half Space Solid")
        elif ItemData.data["representation_type"] in ("Tessellation", "Brep", "AdvancedBrep"):
            self.draw_meshlike()
            self.layout.separator()
            self.layout.operator("bim.add_half_space_solid_item", icon="ORIENTATION_NORMAL", text="Half Space Solid")
        elif ItemData.data["representation_type"] in ("SolidModel", "SweptSolid"):
            self.draw_swept_area()
            self.layout.separator()
            self.layout.operator("bim.add_half_space_solid_item", icon="ORIENTATION_NORMAL", text="Half Space Solid")
        elif ItemData.data["representation_type"] in ("CSG"):
            # Surprisingly, once something becomes a CSG, you can combine lots of things due to IfcBooleanOperand
            self.draw_swept_area()
            self.layout.separator()
            self.draw_meshlike()
            self.layout.separator()
            self.layout.operator("bim.add_half_space_solid_item", icon="ORIENTATION_NORMAL", text="Half Space Solid")
        elif ItemData.data["representation_type"] in ("Annotation2D"):
            self.layout.operator("bim.add_curvelike_item", icon="IPO_CONSTANT", text="Polycurve").shape = "LINE"
            self.layout.operator("bim.add_curvelike_item", icon="MESH_CIRCLE", text="Circle").shape = "CIRCLE"
            self.layout.operator("bim.add_curvelike_item", icon="MESH_CIRCLE", text="Ellipse").shape = "ELLIPSE"

    def draw_meshlike(self):
        self.layout.operator("bim.add_meshlike_item", icon="MESH_PLANE", text="Mesh Plane").shape = "PLANE"
        self.layout.operator("bim.add_meshlike_item", icon="MESH_CUBE", text="Mesh Cube").shape = "CUBE"
        self.layout.operator("bim.add_meshlike_item", icon="MESH_CIRCLE", text="Mesh Circle").shape = "CIRCLE"
        self.layout.operator("bim.add_meshlike_item", icon="MESH_UVSPHERE", text="Mesh UV Sphere").shape = "UVSPHERE"
        self.layout.operator("bim.add_meshlike_item", icon="MESH_ICOSPHERE", text="Mesh Icosphere").shape = "ICOSPHERE"
        self.layout.operator("bim.add_meshlike_item", icon="MESH_CYLINDER", text="Mesh Cylinder").shape = "CYLINDER"

    def draw_swept_area(self):
        self.layout.operator(
            "bim.add_swept_area_solid_item", icon="MESH_CUBE", text="Extruded Area Solid Cube"
        ).shape = "CUBE"
        self.layout.operator(
            "bim.add_swept_area_solid_item", icon="MESH_CYLINDER", text="Extruded Area Solid Cylinder"
        ).shape = "CYLINDER"


class CreateObjectUI:
    layout: bpy.types.UILayout

    @classmethod
    def draw(cls, context: bpy.types.Context, layout: bpy.types.UILayout, ifc_element_type: Union[str, None]) -> None:
        cls.layout = layout
        cls.props = tool.Model.get_model_props()

        row = cls.layout.row(align=True)
        if not tool.Ifc.get():
            row.label(text="No IFC Project", icon="ERROR")
            return

        if not PortData.is_loaded:
            PortData.load()

        if not AuthoringData.is_loaded:
            AuthoringData.load(ifc_element_type)
        elif AuthoringData.data["ifc_element_type"] != ifc_element_type:
            AuthoringData.load(ifc_element_type)

        if context.region.type == "TOOL_HEADER":
            tool_name = (
                "Multi Object Tool"
                if ifc_element_type is None
                else format_ifc_camel_case(ifc_element_type.removesuffix("Type")) + " Tool"
            )
            cls.layout.label(text=tool_name, icon="TOOL_SETTINGS")

        if AuthoringData.data["ifc_classes"] and AuthoringData.data["relating_type_id"]:
            cls.draw_thumbnail(context)
            cls.draw_add_object_parameters(context)
            cls.draw_add_object(context)
            if len(context.selected_objects) == 2 and tool.Ifc.get_entity(context.selected_objects[0]):
                op_icon = custom_icon_previews["APPLY_VOID"].icon_id
                row = layout.row(align=True)
                row.operator("bim.add_opening", text="Apply Void", icon_value=op_icon)
        else:
            cls.draw_type_manager_launcher(context)

    @classmethod
    def draw_container_info(cls, context):
        text = AuthoringData.data["default_container"]
        if context.region.type == "UI":
            text = f"Container: {text}"

        cls.layout.row(align=True).label(text=text, icon="OUTLINER_COLLECTION")

    @classmethod
    def draw_type_manager_launcher(cls, context):
        ui_context = context.region.type
        props = tool.Model.get_model_props()
        row = cls.layout.row(align=True)
        box = cls.layout.box()
        row1 = box.row(align=True)
        row1.operator(
            "bim.launch_type_manager",
            icon="ERROR",
            text=f"No {AuthoringData.data['ifc_element_type'] or 'Type'}s Found",
            emboss=False,
        )
        row1.operator(
            "bim.launch_type_manager",
            icon=tool.Blender.TYPE_MANAGER_ICON,  # "DOWNARROW_HLT",
            text="",
            emboss=False,
        )

        if ui_context != "TOOL_HEADER":

            row = box.row(align=True)
            row.alignment = "CENTER"
            row.template_icon(icon_value=0, scale=3.3)

            row = box.row(align=True)
            row.alignment = "CENTER"
            op = row.operator(
                "bim.add_element", text=f"Create New {AuthoringData.data['ifc_element_type'] or 'Type'}", icon="ADD"
            )
            op.is_specific_tool = bool(AuthoringData.data["ifc_element_type"])
            op.ifc_product = "IfcElementType"
            op.ifc_class = AuthoringData.data["ifc_element_type"] or props.ifc_class or ""

            row = box.row(align=True)

            if not AuthoringData.data["ifc_element_type"]:
                row = box.row(align=True)
                row.alignment = "CENTER"
                row.template_icon(icon_value=0, scale=1)

            row = box.row(align=True)
            row.alignment = "CENTER"
            row.template_icon(icon_value=0, scale=3.5)
        elif AuthoringData.data["ifc_element_type"]:
            row = cls.layout.row(align=True)
            op = row.operator(
                "bim.add_default_type",
                icon_value=custom_icon_previews["QUICK_DEFAULT"].icon_id,
                text=f"Quick Create {AuthoringData.data['ifc_element_type']}",
            )
            op.ifc_element_type = AuthoringData.data["ifc_element_type"]

    @classmethod
    def draw_add_object(cls, context):
        ui_context = str(context.region.type)
        row = cls.layout.row(align=True)
        if AuthoringData.data["relating_type_id"]:
            row = cls.layout.row(align=True) if ui_context != "TOOL_HEADER" else row
            if context.space_data.type == "VIEW_3D":  # Wall polyline tool works only in 3D Space
                op = row.operator("bim.hotkey", text="Add", icon_value=custom_icon_previews["ADD"].icon_id)
                op.hotkey = "S_A"
        else:
            row.label(text="No Construction Type", icon="FILE_3D")

    @classmethod
    def draw_add_object_parameters(cls, context):
        ui_context = str(context.region.type)
        row = cls.layout.row(align=True)
        if not AuthoringData.data["relating_type_id"]:
            return

        ifc_class = AuthoringData.data["ifc_class_current"]
        if ifc_class == "IfcWallType":
            row.prop(data=cls.props, property="rl1", text="Relative Level" if ui_context != "TOOL_HEADER" else "RL")
            row = cls.layout.row(align=True) if ui_context != "TOOL_HEADER" else row
            row.prop(data=cls.props, property="extrusion_depth", text="Height" if ui_context != "TOOL_HEADER" else "H")
            row = cls.layout.row(align=True) if ui_context != "TOOL_HEADER" else row
            row.prop(data=cls.props, property="x_angle", text="Slope") if ui_context != "TOOL_HEADER" else "A"

        elif ifc_class in ("IfcSlabType", "IfcRampType", "IfcRoofType"):
            row.prop(
                data=cls.props, property="x_angle", text="Slope" if ui_context != "TOOL_HEADER" else "A", icon="FILE_3D"
            )

        elif ifc_class in ("IfcColumnType", "IfcPileType"):
            row.prop(data=cls.props, property="cardinal_point", text="Axis")
            row.prop(data=cls.props, property="extrusion_depth", text="Height" if ui_context != "TOOL_HEADER" else "H")

        elif ifc_class in ("IfcBeamType", "IfcMemberType"):
            row.prop(data=cls.props, property="cardinal_point", text="Axis")
            row.prop(data=cls.props, property="extrusion_depth", text="Length" if ui_context != "TOOL_HEADER" else "L")

        elif ifc_class in ("IfcDoorType", "IfcDoorStyle"):
            row.prop(data=cls.props, property="rl1", text="Relative Level" if ui_context != "TOOL_HEADER" else "RL")

        elif ifc_class in (
            "IfcWindowType",
            "IfcWindowStyle",
            "IfcDoorType",
            "IfcDoorStyle",
            "IfcDuctSegmentType",
            "IfcPipeSegmentType",
            "IfcCableCarrierSegmentType",
            "IfcCableSegmentType",
        ):
            row.prop(
                data=cls.props, property="rl2", text="Relative Level (rl2)" if ui_context != "TOOL_HEADER" else "RL"
            )

        ### this neeeds to move
        elif ifc_class in ("IfcSpaceType"):
            add_layout_hotkey_operator(cls.layout, "Generate", "S_G", bpy.ops.bim.generate_space.__doc__, ui_context)
        ###
        else:
            row = cls.layout.row(align=True)
            row.prop(data=cls.props, property="rl_mode", text="RL Mode" if ui_context != "TOOL_HEADER" else "RL")

    @classmethod
    def draw_thumbnail(cls, context):
        ui_context = context.region.type
        row = cls.layout.row(align=True)
        if not AuthoringData.data["ifc_element_type"]:
            prop_with_search(row, cls.props, "ifc_class", text="Type Class" if ui_context != "TOOL_HEADER" else "")
        if not AuthoringData.data["ifc_classes"]:
            return
        if not (ifc_class := AuthoringData.data["ifc_class_current"]):
            return

        relating_type_data = AuthoringData.data["relating_type_data"]
        box = cls.layout.box()

        row = box.row(align=True)
        thumbnail: int = AuthoringData.type_thumbnails.get(relating_type_data["id"], 0)
        row.template_icon(icon_value=thumbnail)
        row.operator("bim.launch_type_manager", text=relating_type_data["name"], emboss=False)
        row.operator(
            "bim.launch_type_manager",
            icon=tool.Blender.TYPE_MANAGER_ICON,
            text="",
            emboss=False,
        )

        if ui_context == "TOOL_HEADER":
            return
        row = box.row(align=True)
        row.alignment = "CENTER"
        row.operator(
            "bim.launch_type_manager",
            text=relating_type_data["description"],
            emboss=False,
        )

        if thumbnail != 0:
            row1 = box.row()
            row1.ui_units_y = 0.01
            row1.template_icon(icon_value=thumbnail, scale=4)
            row2 = box.column(align=True)
            row2.ui_units_y = 4
            for _ in range(4):
                row2.operator("bim.launch_type_manager", text="", emboss=False)
        else:
            box.operator(
                "bim.load_type_thumbnails",
                text="",
                icon="FILE_REFRESH",
                emboss=False,
            )

        row = box.row(align=True)
        row.alignment = "CENTER"
        row.operator(
            "bim.launch_type_manager",
            text=AuthoringData.data["relating_type_data"].get("predefined_type"),
            emboss=False,
        )


class EditObjectUI:
    layout: bpy.types.UILayout

    @classmethod
    def draw(
        cls, context: bpy.types.Context, layout: bpy.types.UILayout, ifc_element_type: Optional[str] = None
    ) -> None:
        cls.layout = layout
        cls.props = tool.Model.get_model_props()

        row = cls.layout.row(align=True)
        row.separator()
        if not tool.Ifc.get():
            row.label(text="No IFC Project", icon="ERROR")
            return

        if not PortData.is_loaded:
            PortData.load()

        if not AuthoringData.is_loaded:
            AuthoringData.load(ifc_element_type)
        elif AuthoringData.data["ifc_element_type"] != ifc_element_type:
            AuthoringData.load(ifc_element_type)

        if context.region.type == "TOOL_HEADER":
            if context.scene.BIMAggregateProperties.in_aggregate_mode:
                layout.label(text=f"Aggregate Mode", icon="EMPTY_AXIS")
                row = cls.layout.row(align=True)
                op = row.operator("bim.disable_aggregate_mode", text="", icon="X")
                op = row.operator("bim.toggle_aggregate_mode_local_view", text="", icon="ZOOM_SELECTED")
            if context.scene.BIMNestProperties.in_nest_mode:
                layout.label(text=f"Nest Mode", icon="EMPTY_AXIS")
                row = cls.layout.row(align=True)
                op = row.operator("bim.disable_nest_mode", text="", icon="X")
                op = row.operator("bim.toggle_nest_mode_local_view", text="", icon="ZOOM_SELECTED")

            text = format_ifc_camel_case(AuthoringData.data["active_class"])
            layout.label(text=f"{text} Edit Tools:", icon="RESTRICT_SELECT_OFF")
            cls.draw_parameter_adjustments(context)
            row = cls.draw_operations(context)
            cls.draw_void(context, row)
            cls.draw_align(context)
            cls.draw_aggregation(context)
            cls.draw_qto(context)
            cls.draw_modes(context)

        if context.region.type in ("UI", "WINDOW"):
            text = format_ifc_camel_case(AuthoringData.data["active_class"])
            layout.label(text=f"{text} Edit Tools:", icon="RESTRICT_SELECT_OFF")
            cls.draw_parameter_adjustments(context)
            row = cls.draw_operations(context)
            cls.draw_void(context, row)
            cls.draw_align(context)
            cls.draw_aggregation(context)
            cls.draw_qto(context)
            cls.draw_modes(context)

    @classmethod
    def draw_parameter_adjustments(cls, context):
        ui_context = str(context.region.type)
        row = cls.layout.row(align=True)
        row.label(text="Parameter Adjustments") if ui_context != "TOOL_HEADER" else row
        row = cls.layout.row(align=True)

        if AuthoringData.data["active_material_usage"] == "LAYER2":
            row.prop(data=cls.props, property="extrusion_depth", text="Height" if ui_context != "TOOL_HEADER" else "H")
            op = row.operator("bim.change_extrusion_depth", icon="FILE_REFRESH", text="")
            op.depth = cls.props.extrusion_depth

            row = cls.layout.row(align=True) if ui_context != "TOOL_HEADER" else row
            row.prop(data=cls.props, property="length", text="Length" if ui_context != "TOOL_HEADER" else "L")
            op = row.operator("bim.change_layer_length", icon="FILE_REFRESH", text="")
            op.length = cls.props.length

            row = cls.layout.row(align=True) if ui_context != "TOOL_HEADER" else row
            row.prop(data=cls.props, property="x_angle", text="Slope" if ui_context != "TOOL_HEADER" else "A")
            op = row.operator("bim.change_extrusion_x_angle", icon="FILE_REFRESH", text="")
            op.x_angle = cls.props.x_angle

        elif AuthoringData.data["active_material_usage"] == "LAYER3":
            row.prop(data=cls.props, property="x_angle", text="Angle" if ui_context != "TOOL_HEADER" else "A")
            op = row.operator("bim.change_extrusion_x_angle", icon="FILE_REFRESH", text="")
            op.x_angle = cls.props.x_angle

        elif AuthoringData.data["active_material_usage"] == "PROFILE":
            row.prop(data=cls.props, property="cardinal_point", text="Axis" if ui_context != "TOOL_HEADER" else "")
            op = row.operator("bim.change_cardinal_point", icon="FILE_REFRESH", text="")
            op.cardinal_point = int(cls.props.cardinal_point)
            row = cls.layout.row(align=True) if ui_context != "TOOL_HEADER" else row
            label = (
                "Height"
                if AuthoringData.data["active_class"] in ("IfcColumn", "IfcColumnStandardCase", "IfcPile")
                else "Length"
            )
            row.prop(
                data=cls.props, property="extrusion_depth", text=label if ui_context != "TOOL_HEADER" else label[0]
            )
            op = row.operator("bim.change_profile_depth", icon="FILE_REFRESH", text="")
            op.depth = cls.props.extrusion_depth

        elif AuthoringData.data["active_class"] in (
            "IfcWindow",
            "IfcWindowStandardCase",
            "IfcDoor",
            "IfcDoorStandardCase",
        ):
            if AuthoringData.data["active_class"] in ("IfcWindow", "IfcWindowStandardCase"):
                row = cls.layout.row(align=True) if ui_context != "TOOL_HEADER" else row
                row.prop(
                    data=cls.props, property="rl2", text="Relative Level (rl2)" if ui_context != "TOOL_HEADER" else "RL"
                )
            elif AuthoringData.data["active_class"] in ("IfcDoor", "IfcDoorStandardCase"):
                row = cls.layout.row(align=True) if ui_context != "TOOL_HEADER" else row
                row.prop(
                    data=cls.props, property="rl1", text="Relative Level (rl1)" if ui_context != "TOOL_HEADER" else "RL"
                )

    @classmethod
    def draw_operations(cls, context):
        ui_context = str(context.region.type)

        row = cls.layout.row(align=True)
        row.separator()
        row.label(text="Operations") if ui_context != "TOOL_HEADER" else row
        cls.draw_regen_operations(row)

        if AuthoringData.data["active_material_usage"] == "LAYER2":
            row = cls.layout.row(align=True) if ui_context != "TOOL_HEADER" else row
            add_layout_hotkey_operator(row, "Extend", "S_E", "Extends/reduces element to 3D cursor", ui_context)
            row = cls.layout.row(align=True) if ui_context != "TOOL_HEADER" else row
            add_layout_hotkey_operator(
                row, "Trim", "S_T", "Connects and trims two non-parallel elements into a joint", ui_context
            )
            row = cls.layout.row(align=True) if ui_context != "TOOL_HEADER" else row
            add_layout_hotkey_operator(row, "Unjoin Walls", "S_U", "", ui_context)
            row = cls.layout.row(align=True) if ui_context != "TOOL_HEADER" else row
            add_layout_hotkey_operator(row, "Merge", "S_M", "Merge selected Elements", ui_context)
            row = cls.layout.row(align=True) if ui_context != "TOOL_HEADER" else row
            add_layout_hotkey_operator(
                row, "Split", "S_K", "Split selected Element into two Elements at the cursor location", ui_context
            )
            row = cls.layout.row(align=True) if ui_context != "TOOL_HEADER" else row
            add_layout_hotkey_operator(row, "Rotate 90", "S_R", "Rotate the selected Element by 90 degrees", ui_context)
            if AuthoringData.data["relating_type_data"].get("usage") == "LAYER3":
                row = cls.layout.row(align=True) if ui_context != "TOOL_HEADER" else row
                add_layout_hotkey_operator(
                    row,
                    "Add From Closed Loop",
                    "S_A",
                    "Generate an element from selected closed walls",
                    ui_context,
                )

        elif AuthoringData.data["active_material_usage"] == "LAYER3":
            if "LAYER2" in AuthoringData.data["selected_material_usages"]:
                row = cls.layout.row(align=True) if ui_context != "TOOL_HEADER" else row
                add_layout_hotkey_operator(cls.layout, "Extend To Underside", "S_E", "", ui_context)
            if AuthoringData.data["relating_type_data"].get("usage") == "LAYER2":
                row = cls.layout.row(align=True) if ui_context != "TOOL_HEADER" else row
                add_layout_hotkey_operator(
                    row,
                    "Add From Perimeter",
                    "S_A",
                    "Generate elements along the perimeter of the selected element",
                    ui_context,
                )

        elif AuthoringData.data["active_material_usage"] == "PROFILE":
            row = cls.layout.row(align=True) if ui_context != "TOOL_HEADER" else row
            add_layout_hotkey_operator(row, "Extend", "S_E", "", ui_context)

            row = cls.layout.row(align=True) if ui_context != "TOOL_HEADER" else row
            if AuthoringData.data["active_class"] in (
                "IfcCableCarrierSegment",
                "IfcCableSegment",
                "IfcDuctSegment",
                "IfcPipeSegment",
            ):
                add_layout_hotkey_operator(row, "Add Fitting", "S_Y", "", ui_context)
                row = cls.layout.row(align=True) if ui_context != "TOOL_HEADER" else row
                row.operator(
                    "bim.mep_add_bend",
                    text="Add Bend" if ui_context != "TOOL_HEADER" else "",
                    icon_value=custom_icon_previews["ADD_BEND"].icon_id,
                )
                row.label(text="", icon="BLANK1") if ui_context != "TOOL_HEADER" else row
                row.label(text="", icon="BLANK1") if ui_context != "TOOL_HEADER" else row

                row = cls.layout.row(align=True) if ui_context != "TOOL_HEADER" else row
                row.operator(
                    "bim.mep_add_transition",
                    text="Add Transition" if ui_context != "TOOL_HEADER" else "",
                    icon_value=custom_icon_previews["ADD_TRANSITION"].icon_id,
                )
                row.label(text="", icon="BLANK1") if ui_context != "TOOL_HEADER" else row
                row.label(text="", icon="BLANK1") if ui_context != "TOOL_HEADER" else row

                row = cls.layout.row(align=True) if ui_context != "TOOL_HEADER" else row
                row.operator(
                    "bim.mep_add_obstruction",
                    text="Add Obstruction" if ui_context != "TOOL_HEADER" else "",
                    icon_value=custom_icon_previews["IFC"].icon_id,
                )
                row.label(text="", icon="BLANK1") if ui_context != "TOOL_HEADER" else row
                row.label(text="", icon="BLANK1") if ui_context != "TOOL_HEADER" else row

            else:
                add_layout_hotkey_operator(row, "Edit Axis", "A_E", "", ui_context)
                row = cls.layout.row(align=True) if ui_context != "TOOL_HEADER" else row
                add_layout_hotkey_operator(row, "Butt", "S_T", "", ui_context)
                row = cls.layout.row(align=True) if ui_context != "TOOL_HEADER" else row
                add_layout_hotkey_operator(row, "Mitre", "S_Y", "", ui_context)
                row = cls.layout.row(align=True) if ui_context != "TOOL_HEADER" else row
                add_layout_hotkey_operator(row, "Rotate 90", "S_R", bpy.ops.bim.rotate_90.__doc__, ui_context)

        else:
            if "LAYER2" in AuthoringData.data["selected_material_usages"]:
                row = cls.layout.row(align=True) if ui_context != "TOOL_HEADER" else row
                add_layout_hotkey_operator(cls.layout, "Extend To Undersideb", "S_E", "", ui_context)

        if AuthoringData.data["is_flippable_element"]:
            cls.draw_flip(ui_context, row)

        if PortData.data["total_ports"] > 0:
            row = cls.layout.row(align=True) if ui_context != "TOOL_HEADER" else row
            row.operator(
                "bim.mep_connect_elements",
                text="Connect MEP Elements" if ui_context != "TOOL_HEADER" else "",
                icon_value=custom_icon_previews["CONNECT_MEP_ELEMENTS"].icon_id,
            )
            row.label(text="", icon="BLANK1") if ui_context != "TOOL_HEADER" else row
            row.label(text="", icon="BLANK1") if ui_context != "TOOL_HEADER" else row

        return row

    @classmethod
    def draw_regen_operations(cls, row):
        custom_icon = custom_icon_previews.get("REGEN", custom_icon_previews["IFC"]).icon_id

        if AuthoringData.data["is_regenable_element"]:
            op = row.operator("bim.hotkey", text="", icon_value=custom_icon)
            description = "Recalculate Element Geometry\nHotkey: S G"
            op.hotkey = "S_G"
            op.description = description.strip()

        if PortData.data["total_ports"] > 0:
            op = row.operator("bim.hotkey", text="", icon_value=custom_icon)
            description = f"{bpy.ops.bim.regenerate_distribution_element.__doc__}\n\nHotkey: S G"
            op.hotkey = "S_G"
            op.description = description.strip()

    @classmethod
    def draw_void(cls, context, row):
        ui_context = str(context.region.type)
        IS_TOOL_HEADER = ui_context == "TOOL_HEADER"

        if len(context.selected_objects) > 1:
            op_text = "Apply Void" if ui_context != "TOOL_HEADER" else ""
            op_icon = custom_icon_previews["APPLY_VOID"].icon_id
            row = cls.layout.row(align=True) if ui_context != "TOOL_HEADER" else row
            row.operator("bim.add_opening", text=op_text, icon_value=op_icon)
            if ui_context != "TOOL_HEADER":
                row.label(text="", icon="EVENT_SHIFT")
                row.label(text="", icon="EVENT_O")
        else:
            op_text = "Add Void" if ui_context != "TOOL_HEADER" else ""
            op_icon = custom_icon_previews["ADD_VOID"].icon_id
            row = cls.layout.row(align=True) if ui_context != "TOOL_HEADER" else row

        if AuthoringData.data["is_voidable_element"]:
            if AuthoringData.data["has_visible_openings"]:
                row = cls.layout.row(align=True)
                op_text = "" if IS_TOOL_HEADER else "Edit Openings"
                row.operator("bim.edit_openings", icon="CHECKMARK", text=op_text)
                row.operator("bim.hide_openings", icon="CANCEL", text="")

        if AuthoringData.data["active_class"] in ("IfcOpeningElement",):
            row = cls.layout.row(align=True)
            op_text = "" if IS_TOOL_HEADER else "Edit Openings"
            row.operator("bim.edit_openings", icon="CHECKMARK", text=op_text)
            row.operator("bim.hide_openings", icon="CANCEL", text="")
            row = cls.layout.row(align=True) if ui_context != "TOOL_HEADER" else row
            add_layout_hotkey_operator(row, "Clone Opening", "S_L", "", ui_context, operator="bim.clone_opening")

    @classmethod
    def draw_align(cls, context):
        ui_context = str(context.region.type)
        row = cls.layout.row(align=True)
        row.separator()
        row.label(text="Align") if ui_context != "TOOL_HEADER" else row
        row = cls.layout.row(align=True) if ui_context != "TOOL_HEADER" else row
        add_layout_hotkey_operator(row, "Exterior", "S_X", "", ui_context)
        row = cls.layout.row(align=True) if ui_context != "TOOL_HEADER" else row
        add_layout_hotkey_operator(row, "Centreline", "S_C", "", ui_context)
        row = cls.layout.row(align=True) if ui_context != "TOOL_HEADER" else row
        add_layout_hotkey_operator(row, "Interior", "S_V", "", ui_context)
        row = cls.layout.row(align=True) if ui_context != "TOOL_HEADER" else row
        add_layout_hotkey_operator(row, "Mirror", "S_M", bpy.ops.bim.mirror_elements.__doc__, ui_context)

    @classmethod
    def draw_aggregation(cls, context):
        ui_context = str(context.region.type)
        row = cls.layout.row(align=True)
        row.separator()
        row.label(text="Aggregation") if ui_context != "TOOL_HEADER" else row
        row = cls.layout.row(align=True) if ui_context != "TOOL_HEADER" else row
        add_layout_hotkey_operator(row, "Assign", "C_P", bpy.ops.bim.aggregate_assign_object.__doc__, ui_context)
        row = cls.layout.row(align=True) if ui_context != "TOOL_HEADER" else row
        add_layout_hotkey_operator(row, "Unassign", "A_P", bpy.ops.bim.aggregate_unassign_object.__doc__, ui_context)

    @classmethod
    def draw_qto(cls, context):
        ui_context = str(context.region.type)
        row = cls.layout.row(align=True)
        row.separator()
        row.label(text="Quantity Take-off") if ui_context != "TOOL_HEADER" else row
        row = cls.layout.row(align=True) if ui_context != "TOOL_HEADER" else row
        add_layout_hotkey_operator(
            row, "Perform Quantity Take-off", "S_Q", bpy.ops.bim.perform_quantity_take_off.__doc__, ui_context
        )

    @classmethod
    def draw_modes(cls, context: bpy.types.Context) -> None:
        obj = context.active_object
        ui_context = str(context.region.type)
        row = cls.layout.row(align=True)
        row.separator()
        row.label(text="Mode") if ui_context != "TOOL_HEADER" else row

        if AuthoringData.data["active_material_usage"] == "LAYER3":
            if len(context.selected_objects) == 1 and AuthoringData.data["has_extrusion"]:
                row = cls.layout.row(align=True) if ui_context != "TOOL_HEADER" else row
                add_layout_hotkey_operator(row, "Edit Profile", "S_E", "", ui_context)
        elif tool.Model.is_parametric_railing_active() and not tool.Model.get_railing_props(obj).is_editing_path:
            row = cls.layout.row(align=True) if ui_context != "TOOL_HEADER" else row
            row.operator(
                "bim.enable_editing_railing_path",
                text="Edit Path" if ui_context != "TOOL_HEADER" else "",
                icon_value=custom_icon_previews["EDIT_RAILING_PATH"].icon_id,
            )
        elif AuthoringData.data["active_material_usage"] == "PROFILE":
            row = cls.layout.row(align=True) if ui_context != "TOOL_HEADER" else row
            add_layout_hotkey_operator(row, "Edit Axis", "A_E", "", ui_context)

        row = cls.layout.row(align=True) if ui_context != "TOOL_HEADER" else row
        add_layout_hotkey_operator(row, "Toggle Openings", "A_O", "Toggle openings", ui_context)
        row = cls.layout.row(align=True) if ui_context != "TOOL_HEADER" else row
        add_layout_hotkey_operator(row, "Decomposition", "A_D", "Select decomposition", ui_context)

    @classmethod
    def draw_flip(cls, ui_context, layout) -> None:
        row = cls.layout.row(align=True) if ui_context != "TOOL_HEADER" else layout
        add_layout_hotkey_operator(row, "Flip", "S_F", bpy.ops.bim.flip_object.__doc__, ui_context)


class Hotkey(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.hotkey"
    bl_label = ""
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}
    hotkey: bpy.props.StringProperty()
    description: bpy.props.StringProperty()
    x: bpy.props.FloatProperty(name="X", default=0.5)
    y: bpy.props.FloatProperty(name="Y", default=0.5)
    z: bpy.props.FloatProperty(name="Z", default=0.5)

    @classmethod
    def poll(cls, context):
        return tool.Ifc.get()

    @classmethod
    def description(cls, context, operator):
        return operator.description or ""

    def _execute(self, context):
        self.props = tool.Model.get_model_props()
        self.has_ifc_class = True

        self.active_class = None
        self.active_material_usage = None
        element = tool.Ifc.get_entity(context.active_object)
        if element:
            self.active_class = element.is_a()
            self.active_material_usage = tool.Model.get_usage_type(element)

        if get_ifc_class(None, None):
            try:
                self.has_ifc_class = bool(tool.Blender.get_enum_safe(self.props, "ifc_class"))
            except:
                pass
        getattr(self, f"hotkey_{self.hotkey}")()

    def invoke(self, context, event):
        # https://blender.stackexchange.com/questions/276035/how-do-i-make-operators-remember-their-property-values-when-called-from-a-hotkey
        self.props = tool.Model.get_model_props()
        self.x = self.props.x
        self.y = self.props.y
        self.z = self.props.z
        return self.execute(context)

    def draw(self, context):
        if self.hotkey == "S_O":
            row = self.layout.row()
            row.prop(self, "x")
            row = self.layout.row()
            row.prop(self, "y")
            row = self.layout.row()
            row.prop(self, "z")

    def hotkey_S_A(self):
        gprops = tool.Geometry.get_geometry_props()
        if gprops.mode == "ITEM":
            bpy.ops.wm.call_menu(name="BIM_MT_add_representation_item")
            return

        props = tool.Model.get_model_props()
        relating_type_class = AuthoringData.data["ifc_class_current"]
        if not (relating_type_id := tool.Blender.get_enum_safe(props, "relating_type_id")):
            self.report({"ERROR"}, "No relating type selected")
            return

        relating_type = tool.Ifc.get().by_id(int(relating_type_id))

        has_only_walls_selected = tool.Blender.get_selected_objects(include_active=False) and all(
            (e := tool.Ifc.get_entity(o)) and e.is_a("IfcWall")
            for o in tool.Blender.get_selected_objects(include_active=False)
        )

        if tool.Model.get_usage_type(relating_type) == "LAYER3" and has_only_walls_selected:
            return bpy.ops.bim.draw_slab_from_wall("INVOKE_DEFAULT")
        elif (
            (active_obj := tool.Blender.get_active_object(is_selected=True))
            and (active_element := tool.Ifc.get_entity(active_obj))
            and active_element.is_a("IfcSlab")
            and tool.Model.get_usage_type(relating_type) == "LAYER2"
        ):
            return bpy.ops.bim.draw_walls_from_slab("INVOKE_DEFAULT")

        for obj in tool.Blender.get_selected_objects():
            obj.select_set(False)

        if tool.Model.get_usage_type(relating_type) == "LAYER2":
            return bpy.ops.bim.draw_polyline_wall("INVOKE_DEFAULT")
        elif tool.Model.get_usage_type(relating_type) == "LAYER3":
            return bpy.ops.bim.draw_polyline_slab("INVOKE_DEFAULT")
        elif tool.Model.get_usage_type(relating_type) == "PROFILE" and relating_type_class not in (
            "IfcColumnType",
            "IfcPileType",
        ):
            return bpy.ops.bim.draw_polyline_profile("INVOKE_DEFAULT")
        return bpy.ops.bim.draw_occurrence("INVOKE_DEFAULT")

    def hotkey_S_Q(self):
        if not bpy.context.selected_objects:
            return

        bpy.ops.bim.perform_quantity_take_off()

    def hotkey_C_P(self):
        if not bpy.context.selected_objects:
            return
        bpy.ops.bim.aggregate_assign_object()

    def hotkey_A_P(self):
        if not bpy.context.selected_objects:
            return
        bpy.ops.bim.aggregate_unassign_object()

    def hotkey_S_C(self):
        if not bpy.context.selected_objects:
            return
        if self.active_material_usage == "LAYER2":
            if bpy.ops.bim.align_wall.poll():
                bpy.ops.bim.align_wall(align_type="CENTERLINE")
        else:
            bpy.ops.bim.align_product(align_type="CENTERLINE")

    def hotkey_S_E(self):
        if not bpy.context.selected_objects or not (active_object := bpy.context.active_object):
            return

        selected_usages: dict[str, list[bpy.types.Object]] = {}
        for obj in bpy.context.selected_objects:
            element = tool.Ifc.get_entity(obj)
            if not element:
                obj.select_set(False)
                continue
            usage = tool.Model.get_usage_type(element)
            if not usage:
                representation = tool.Geometry.get_active_representation(obj)
                representation = tool.Geometry.resolve_mapped_representation(representation)
            selected_usages.setdefault(usage, []).append(obj)

        if len(bpy.context.selected_objects) == 1:
            # Active object was probably unselected because it doesn't have a usage.
            if bpy.context.selected_objects[0] != active_object:
                return

            if self.active_material_usage == "LAYER3":
                # Edit LAYER3 profile
                if (
                    active_object.mode == "OBJECT"
                    and (representation := tool.Geometry.get_active_representation(active_object))
                    and tool.Model.get_extrusion(representation)
                ):
                    bpy.ops.bim.enable_editing_extrusion_profile()
            elif self.active_material_usage == "LAYER2":
                # Extend LAYER2 to cursor
                core.extend_walls(
                    tool.Ifc,
                    tool.Blender,
                    tool.Geometry,
                    DumbWallJoiner(),
                    tool.Model,
                    bpy.context.scene.cursor.location,
                )
            elif self.active_material_usage == "PROFILE":
                # Extend PROFILE to cursor
                bpy.ops.bim.extend_profile(join_type="T")

        elif self.active_material_usage == "LAYER2" and selected_usages.get("PROFILE", []):
            # Extend PROFILEs to LAYER2
            [o.select_set(False) for o in selected_usages.get("LAYER3", [])]
            [o.select_set(False) for o in selected_usages.get("LAYER2", []) if o != bpy.context.active_object]
            bpy.ops.bim.extend_profile(join_type="T")

        elif self.active_material_usage == "LAYER2":
            bpy.ops.bim.extend_walls_to_wall()

        elif self.active_material_usage == "PROFILE":
            # Extend PROFILEs to PROFILE
            [o.select_set(False) for o in selected_usages.get("LAYER3", [])]
            [o.select_set(False) for o in selected_usages.get("LAYER2", [])]
            bpy.ops.bim.extend_profile(join_type="T")

        else:
            bpy.ops.bim.extend_walls_to_underside()

    def hotkey_S_F(self):
        if not bpy.context.selected_objects:
            return
        if self.active_material_usage == "LAYER2":
            bpy.ops.bim.flip_wall()
        elif self.active_class in ("IfcWindow", "IfcWindowStandardCase", "IfcDoor", "IfcDoorStandardCase"):
            bpy.ops.bim.flip_fill()
        elif self.active_material_usage == "PROFILE":
            bpy.ops.bim.flip_object(flip_local_axes="XZ")

    def hotkey_S_G(self):
        obj = bpy.context.active_object
        element = tool.Ifc.get_entity(obj)
        if not bpy.context.selected_objects:
            if self.props.ifc_class == "IfcSpaceType":
                bpy.ops.bim.generate_space()
            return
        if self.active_material_usage == "LAYER2":
            bpy.ops.bim.recalculate_wall()
        elif self.active_material_usage == "LAYER3":
            bpy.ops.bim.recalculate_slab()
        elif tool.System.get_ports(element):
            bpy.ops.bim.regenerate_distribution_element()
        elif self.active_material_usage == "PROFILE":
            if self.active_class not in (
                "IfcCableCarrierSegment",
                "IfcCableSegment",
                "IfcDuctSegment",
                "IfcPipeSegment",
            ):
                bpy.ops.bim.recalculate_profile()
        elif self.active_class in ("IfcWindow", "IfcWindowStandardCase", "IfcDoor", "IfcDoorStandardCase"):
            bpy.ops.bim.recalculate_fill()
        elif self.active_class in ("IfcSpace"):
            bpy.ops.bim.generate_space()

    def hotkey_S_M(self):
        if not bpy.context.selected_objects:
            return
        if self.active_material_usage == "LAYER2":
            bpy.ops.bim.merge_wall()
        else:
            if len(bpy.context.selected_objects) == 1:
                self.report(
                    {"ERROR"},
                    "At least two objects must be selected: an object to be mirrored, and a mirror axis as the active object.",
                )
            else:
                bpy.ops.bim.mirror_elements()

    def hotkey_S_R(self):
        if not bpy.context.selected_objects:
            return
        if self.active_material_usage == "LAYER2":
            bpy.ops.bim.rotate_90(axis="Z")
        elif self.active_class in ("IfcColumn", "IfcColumnStandardCase", "IfcPile"):
            bpy.ops.bim.rotate_90(axis="Z")
        elif self.active_class in ("IfcBeam", "IfcBeamStandardCase", "IfcMember", "IfcMemberStandardCase"):
            bpy.ops.bim.rotate_90(axis="Y")

    def hotkey_S_K(self):
        if not bpy.context.selected_objects:
            return
        if self.active_material_usage == "LAYER2":
            bpy.ops.bim.split_wall()

    def hotkey_S_T(self):
        if not bpy.context.selected_objects:
            return
        if self.active_material_usage == "LAYER2":
            try:
                core.join_walls_LV(tool.Ifc, tool.Blender, tool.Geometry, DumbWallJoiner(), tool.Model)
            except core.RequireTwoWallsError as e:
                self.report({"ERROR"}, str(e))
        elif self.active_material_usage == "PROFILE":
            bpy.ops.bim.extend_profile(join_type="L")

    def hotkey_S_V(self):
        if not bpy.context.selected_objects:
            return
        elif self.active_material_usage == "LAYER2":
            bpy.ops.bim.align_wall(align_type="INTERIOR")
        else:
            bpy.ops.bim.align_product(align_type="POSITIVE")

    def hotkey_S_X(self):
        if not bpy.context.selected_objects:
            return
        if self.active_material_usage == "LAYER2":
            if bpy.ops.bim.align_wall.poll():
                bpy.ops.bim.align_wall(align_type="EXTERIOR")
        else:
            bpy.ops.bim.align_product(align_type="NEGATIVE")

    def hotkey_S_Y(self):
        if not bpy.context.selected_objects:
            return
        if self.active_class in ("IfcDuctSegment", "IfcPipeSegment", "IfcCableCarrierSegment", "IfcCableSegment"):
            bpy.ops.bim.fit_flow_segments()
        elif self.active_material_usage == "PROFILE":
            bpy.ops.bim.extend_profile(join_type="V")

    def hotkey_S_B(self):
        bpy.ops.bim.add_boundary()

    def hotkey_S_O(self):
        if len(bpy.context.selected_objects) == 2:
            bpy.ops.bim.add_opening()

    def hotkey_S_L(self):
        if AuthoringData.data["active_class"] in ("IfcOpeningElement",):
            if len(bpy.context.selected_objects) == 2:
                bpy.ops.bim.clone_opening()

    def hotkey_S_U(self):
        if not bpy.context.selected_objects:
            return
        bpy.ops.bim.unjoin_walls()

    def hotkey_A_D(self):
        if not tool.Blender.get_selected_objects():
            return
        bpy.ops.bim.select_decomposition()

    def hotkey_A_E(self):
        if not bpy.context.selected_objects:
            return
        if self.active_material_usage == "PROFILE":
            bpy.ops.bim.enable_editing_extrusion_axis()

    def hotkey_A_O(self):
        if tool.Model.get_model_props().openings:
            bpy.ops.bim.edit_openings(apply_all=True)
        else:
            bpy.ops.bim.show_openings()


custom_icon_previews = None
display_mode = None
