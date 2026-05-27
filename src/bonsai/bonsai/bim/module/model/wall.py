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
#
# This file was modified with the assistance of an AI coding tool.
#
# pyright: reportUnnecessaryTypeIgnoreComment=error

import copy
import math
from math import atan2, cos, degrees, pi, sin
from typing import TYPE_CHECKING, Any, ClassVar, Literal, Optional, Union, get_args

import bmesh
import bpy
import ifcopenshell
import ifcopenshell.api.feature
import ifcopenshell.api.geometry
import ifcopenshell.api.material
import ifcopenshell.api.pset
import ifcopenshell.api.root
import ifcopenshell.api.type
import ifcopenshell.geom
import ifcopenshell.util.element
import ifcopenshell.util.placement
import ifcopenshell.util.representation
import ifcopenshell.util.shape
import ifcopenshell.util.shape_builder
import ifcopenshell.util.type
import ifcopenshell.util.unit
import mathutils.geometry
import numpy as np
from mathutils import Matrix, Vector

import bonsai.core.geometry
import bonsai.core.model as core
import bonsai.core.root
import bonsai.tool as tool
from bonsai.bim.ifc import IfcStore
from bonsai.bim.module.drawing import gizmos as gizmo
from bonsai.bim.module.drawing.gizmos import DimensionGizmoConfig
from bonsai.bim.module.model.decorator import PolylineDecorator, ProductDecorator
from bonsai.bim.module.model.polyline import PolylineOperator

if TYPE_CHECKING:
    from bonsai.bim.module.model.prop import BIMWallProperties


def regenerate_wall_mesh_from_props(obj: bpy.types.Object) -> None:
    """Rebuild ``obj.data`` as a preview box from ``BIMWallProperties`` without touching IFC.

    The preview omits openings, layer materials, and connection joins; those are
    resolved on commit by ``recreate_wall`` / ``recalculate_walls``."""
    props = tool.Model.get_wall_props(obj)
    length = max(props.length, 0.001)
    height = max(props.height, 0.001)
    thickness = max(props.thickness, 0.001)
    offset = props.offset
    x_angle = props.x_angle
    x0 = props.anchor_x
    x1 = x0 + length
    y0 = offset
    y1 = offset + thickness
    # Slope shifts the top face along +Y by height * tan(x_angle), keeping the bottom fixed.
    y_top_shift = core.displacement_from_x_angle(height, x_angle) if x_angle else 0.0

    bm = bmesh.new()
    verts = [
        bm.verts.new((x0, y0, 0.0)),
        bm.verts.new((x1, y0, 0.0)),
        bm.verts.new((x1, y1, 0.0)),
        bm.verts.new((x0, y1, 0.0)),
        bm.verts.new((x0, y0 + y_top_shift, height)),
        bm.verts.new((x1, y0 + y_top_shift, height)),
        bm.verts.new((x1, y1 + y_top_shift, height)),
        bm.verts.new((x0, y1 + y_top_shift, height)),
    ]
    bm.faces.new([verts[0], verts[1], verts[2], verts[3]])
    bm.faces.new([verts[7], verts[6], verts[5], verts[4]])
    bm.faces.new([verts[0], verts[4], verts[5], verts[1]])
    bm.faces.new([verts[3], verts[2], verts[6], verts[7]])
    bm.faces.new([verts[0], verts[3], verts[7], verts[4]])
    bm.faces.new([verts[1], verts[5], verts[6], verts[2]])

    assert isinstance(obj.data, bpy.types.Mesh)
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()
    # Mark the mesh as having diverged from the IFC-derived geometry. cancel /
    # no-op-finish reads this and calls recreate_wall to restore openings & layers.
    tool.Model.get_wall_props(obj).mesh_dirty = True


def _restore_wall_mesh_if_dirty(obj: bpy.types.Object) -> None:
    """Re-derive the wall mesh from IFC if the bmesh preview replaced the real geometry.

    Idempotent: clears the dirty flag after restoring. Does call into
    ``ifcopenshell.api.geometry.regenerate_wall_representation`` (one ifc.run), which is
    acceptable here because cancel / no-op-finish are explicit user actions, not per-frame
    events. Skipping the call when no drag happened preserves the byte-identical guarantee
    for the common enable → ✓ no-drag round-trip."""
    props = tool.Model.get_wall_props(obj)
    if not props.mesh_dirty:
        return
    element = tool.Ifc.get_entity(obj)
    if element:
        tool.Model.recreate_wall(element, obj)
    props.mesh_dirty = False


def _validate_wall_for_parametric_edit(obj: bpy.types.Object) -> str | None:
    """Return ``None`` if the wall is parametrically editable, else a user-facing reason
    string explaining what's missing. Reports the *specific* gap rather than a generic
    'not parametric' so the user knows whether to fix the material layer set, swap the
    body representation, or pick a different object."""
    element = tool.Ifc.get_entity(obj)
    if not element:
        return "Object is not an IFC element."
    if not element.is_a("IfcWall"):
        return f"Object is an {element.is_a()}, not an IfcWall."
    if tool.Model.get_usage_type(element) != "LAYER2":
        return "Wall has no IfcMaterialLayerSetUsage with LayerSetDirection AXIS2 (required for parametric editing)."
    representation = ifcopenshell.util.representation.get_representation(element, "Model", "Body", "MODEL_VIEW")
    if not representation:
        return "Wall has no Model/Body/MODEL_VIEW representation to drive parametric dimensions."
    if not tool.Model.get_extrusion(representation):
        return (
            "Wall body is not an IfcExtrudedAreaSolid " "(e.g. a brep mesh or boolean result without a base extrusion)."
        )
    return None


def _read_wall_state_into_props(obj: bpy.types.Object, props: "BIMWallProperties") -> None:
    """Populate the draft props from current IFC state. Caller must have validated the
    wall via ``_validate_wall_for_parametric_edit`` first — this function assumes the
    wall has a LAYER2 usage and an extruded MODEL_VIEW body."""
    geom = _read_wall_geometry(obj)
    assert geom

    props.anchor_x = geom["anchor_x"]
    props.length = max(0.01, geom["length"])
    props.height = max(0.01, geom["height"])
    props.x_angle = geom["x_angle"]
    props.thickness = max(0.001, geom["thickness"])
    props.offset = geom["offset"]
    props.desired_offset_baseline = core.baseline_from_offset(props.offset, props.thickness)

    props.snap_length = props.length
    props.snap_height = props.height
    props.snap_thickness = props.thickness
    props.snap_offset = props.offset
    props.snap_x_angle = props.x_angle
    props.snap_offset_baseline = props.desired_offset_baseline


class UnjoinWalls(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.unjoin_walls"
    bl_label = "Unjoin Walls"
    bl_description = "Unjoin the selected walls"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if not tool.Model.has_selected_ifc_objects():
            cls.poll_message_set("No IFC objects selected.")
            return False
        return True

    def _execute(self, context):
        _commit_pending_wall_edits_for_selection(context)
        core.unjoin_walls(tool.Ifc, tool.Blender, tool.Geometry, DumbWallJoiner(), tool.Model)


class ExtendWallsToUnderside(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.extend_walls_to_underside"
    bl_label = "Extend Walls To Underside"
    bl_description = "Extend and clip selected walls at the bottom faces of an object"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if not tool.Model.has_selected_ifc_objects():
            cls.poll_message_set("No IFC objects selected.")
            return False
        return True

    def _execute(self, context):
        # Match the sibling ops (UnjoinWalls / MergeWall / ExtendWallsToWall): if any
        # of the selected walls has an in-progress parametric draft, commit it before
        # extending, so the slab clip operates on the just-finalised IFC state.
        _commit_pending_wall_edits_for_selection(context)
        slab = None
        walls: list[bpy.types.Object] = []
        if (obj := tool.Blender.get_active_object(is_selected=True)) and (element := tool.Ifc.get_entity(obj)):
            slab = obj
        for obj in tool.Blender.get_selected_objects(include_active=False):
            if (element := tool.Ifc.get_entity(obj)) and tool.Model.get_usage_type(element) == "LAYER2":
                walls.append(obj)
        if slab and walls:
            core.extend_wall_to_slab(tool.Ifc, tool.Geometry, tool.Model, slab, walls)
        else:
            self.report({"ERROR"}, "Please select at least one LAYER2 element and an active element")


class ExtendWallsToWall(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.extend_walls_to_wall"
    bl_label = "Extend Walls To Wall"
    bl_description = "Extend and trim selected walls to another wall"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        _commit_pending_wall_edits_for_selection(context)
        target_obj = None
        objs = []
        if (
            (obj := tool.Blender.get_active_object(is_selected=True))
            and (element := tool.Ifc.get_entity(obj))
            and tool.Model.get_usage_type(element) == "LAYER2"
        ):
            target_obj = obj
        for obj in tool.Blender.get_selected_objects(include_active=False):
            if (
                obj != target_obj
                and (element := tool.Ifc.get_entity(obj))
                and tool.Model.get_usage_type(element) == "LAYER2"
            ):
                objs.append(obj)
        if target_obj and objs:
            if tool.Ifc.is_moved(target_obj):
                bonsai.core.geometry.edit_object_placement(tool.Ifc, tool.Geometry, tool.Surveyor, obj=target_obj)
            joiner = DumbWallJoiner()
            target_element = tool.Ifc.get_entity(target_obj)
            for obj in objs:
                if tool.Ifc.is_moved(obj):
                    bonsai.core.geometry.edit_object_placement(tool.Ifc, tool.Geometry, tool.Surveyor, obj=obj)
                element = tool.Ifc.get_entity(obj)
                ifcopenshell.api.geometry.connect_wall(
                    tool.Ifc.get(), wall1=element, wall2=target_element, is_atpath=True
                )
                tool.Model.recreate_wall(element, obj)
            tool.Model.recreate_wall(target_element, target_obj)
        else:
            self.report({"ERROR"}, "Please select at least one LAYER2 element and one active LAYER2 element")


class ExtendWallsToPolylinePoint(bpy.types.Operator, PolylineOperator, tool.Ifc.Operator):
    bl_idname = "bim.extend_walls_to_polyline_point"
    bl_label = "Extend Walls To Polyline Point"
    bl_description = "Extend and trim selected walls to another wall"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if not (space := context.space_data) or space.type != "VIEW_3D":
            return False
        for obj in context.selected_objects:
            if not (element := tool.Ifc.get_entity(obj)) or not element.is_a("IfcWall"):
                return False
        return bool(context.selected_objects)

    def __init__(self):
        super().__init__()
        self.connection = "ATEND"

    def set_origin(self, context, event, connection="ATSTART"):
        obj = context.active_object
        element = tool.Ifc.get_entity(obj)
        layers = tool.Model.get_material_layer_parameters(element)
        axis = tool.Model.get_wall_axis(obj, layers)
        start = Vector((axis["reference"][0][0], axis["reference"][0][1], obj.location.z))
        end = Vector((axis["reference"][1][0], axis["reference"][1][1], obj.location.z))
        direcion = end - start
        value = end if connection == "ATSTART" else start
        self.input_ui.set_value("X", value[0])
        self.input_ui.set_value("Y", value[1])
        self.input_ui.set_value("Z", value[2])
        result = tool.Polyline.insert_polyline_point(self.input_ui, self.tool_state)
        PolylineDecorator.update(event, self.tool_state, self.input_ui, self.snapping_points[0])
        tool.Blender.update_viewport()
        # Point related to the mouse
        polyline_props = tool.Model.get_polyline_props()
        snap_prop = polyline_props.snap_mouse_point[0]
        mouse_point = Vector((snap_prop.x, snap_prop.y, snap_prop.z))

        angle = atan2(direcion.y, direcion.x)

        self.tool_state.lock_axis = True
        self.tool_state.snap_angle = degrees(angle)

    def modal(self, context, event):
        return IfcStore.execute_ifc_operator(self, context, event, method="MODAL")

    def _modal(self, context, event):
        PolylineDecorator.update(event, self.tool_state, self.input_ui, self.snapping_points[0])
        tool.Blender.update_viewport()
        self.handle_lock_axis(context, event)  # Must come before "PASS_THROUGH"
        self.handle_mouse_move(context, event)

        if event.type in {"MIDDLEMOUSE", "WHEELUPMOUSE", "WHEELDOWNMOUSE"}:
            self.handle_mouse_move(context, event)
            return {"PASS_THROUGH"}

        custom_instructions = {
            "Cycle Input": {"icons": True, "keys": ["EVENT_TAB"]},
            "Distance Input": {"icons": True, "keys": ["EVENT_D"]},
            "Flip starting point": {"icons": True, "keys": ["EVENT_F"]},
            "Confirm": {"icons": True, "keys": ["MOUSE_LMB"]},
            "Cancel": {"icons": True, "keys": ["MOUSE_RMB", "EVENT_ESC"]},
        }
        custom_info = []
        self.handle_instructions(context, custom_instructions, custom_info, overwrite=True)
        self.handle_mouse_move(context, event, should_round=True)
        self.choose_axis(event)
        self.handle_snap_selection(context, event)

        if event.value == "RELEASE" and event.type == "F":
            tool.Polyline.clear_polyline()
            self.connection = "ATSTART" if self.connection == "ATEND" else "ATEND"
            self.set_origin(context, event, self.connection)

        if event.value == "RELEASE" and event.type in {"RET", "NUMPAD_ENTER", "RIGHTMOUSE", "LEFTMOUSE"}:
            if self.tool_state.is_input_on:
                is_valid = self.recalculate_inputs(context)
                if is_valid:
                    result = tool.Polyline.insert_polyline_point(self.input_ui, self.tool_state)
                    if result:
                        self.report({"WARNING"}, result)
            else:
                result = tool.Polyline.insert_polyline_point(self.input_ui, self.tool_state)
                if result:
                    self.report({"WARNING"}, result)

            polyline_props = tool.Model.get_polyline_props()
            snap_prop = polyline_props.snap_mouse_point[0]
            snap_obj = bpy.data.objects.get(snap_prop.snap_object)
            if snap_obj and tool.Ifc.get_entity(snap_obj).is_a("IfcWall"):
                tool.Blender.set_active_object(snap_obj)
                ExtendWallsToWall._execute(self, context)
            else:
                point = polyline_props.insertion_polyline[0].polyline_points[1]
                core.extend_walls(
                    tool.Ifc,
                    tool.Blender,
                    tool.Geometry,
                    DumbWallJoiner(),
                    tool.Model,
                    Vector((point.x, point.y, point.z)),
                    self.connection,
                )

            tool.Polyline.clear_polyline()
            context.workspace.status_text_set(text=None)
            PolylineDecorator.uninstall()
            tool.Blender.update_viewport()
            return {"FINISHED"}

        self.handle_keyboard_input(context, event)

        cancel = self.handle_cancelation(context, event)
        if cancel is not None:
            return cancel

        return {"RUNNING_MODAL"}

    def invoke(self, context, event):
        super().invoke(context, event)
        self.set_origin(context, event, self.connection)
        self.tool_state.use_default_container = True
        self.tool_state.plane_method = "XY"
        # Update snaps after changing plane_method
        detected_snaps = tool.Snap.detect_snapping_points(context, event, self.objs_2d_bbox, self.tool_state)
        self.snapping_points = tool.Snap.select_snapping_points(context, event, self.tool_state, detected_snaps)
        tool.Polyline.calculate_distance_and_angle(context, self.input_ui, self.tool_state)
        tool.Blender.update_viewport()
        return {"RUNNING_MODAL"}


class AlignWall(bpy.types.Operator):
    bl_idname = "bim.align_wall"
    bl_label = "Align Wall"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = """ Align the selected walls to the active wall:
    'Ext.': align to the EXTERIOR face
    'C/L': align to wall CENTER
    'Int.': align to the INTERIOR face"""

    AlignType = Literal["CENTER", "EXTERIOR", "INTERIOR"]
    align_type: bpy.props.EnumProperty(  # pyright: ignore [reportRedeclaration]
        items=((i, i, "") for i in get_args(AlignType))
    )

    if TYPE_CHECKING:
        align_type: AlignType

    def execute(self, context):
        try:
            core.align_walls(tool.Ifc, tool.Blender, tool.Model, DumbWallAligner(), self.align_type)
        except core.RequireAtLeastTwoLayeredElements as e:
            self.report({"ERROR"}, str(e))
        return {"FINISHED"}


class FlipWall(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.flip_wall"
    bl_label = "Flip Wall"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Switch the origin from the min XY corner to the max XY corner, and rotates the origin by 180"

    @classmethod
    def poll(cls, context):
        if not tool.Model.has_selected_ifc_objects():
            cls.poll_message_set("No IFC objects selected.")
            return False
        return True

    def _execute(self, context):
        selected_objs = tool.Model.get_selected_mesh_objects()
        joiner = DumbWallJoiner()
        for obj in selected_objs:
            joiner.flip(obj)
        return {"FINISHED"}


class SplitWall(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.split_wall"
    bl_label = "Split Wall"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = (
        "Split selected wall into two walls in correspondence of Blender cursor. The cursor must be in the wall volume"
    )

    @classmethod
    def poll(cls, context):
        if not tool.Model.has_selected_ifc_objects():
            cls.poll_message_set("No IFC objects selected.")
            return False
        return True

    def _execute(self, context):
        _commit_pending_wall_edits_for_selection(context)
        selected_objs = tool.Model.get_selected_mesh_objects()
        for obj in selected_objs:
            DumbWallJoiner().split(obj, context.scene.cursor.location)
        return {"FINISHED"}


class MergeWall(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.merge_wall"
    bl_label = "Merge Wall"
    bl_description = "Merge selected walls into one object"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if not context.active_object:
            cls.poll_message_set("No active object selected.")
            return False
        elif not tool.Model.has_selected_ifc_objects():
            cls.poll_message_set("No mesh IFC objects selected.")
            return False
        mesh_objects = [o for o in tool.Model.get_selected_ifc_objects() if o.type == "MESH"]
        if len(mesh_objects) != 2:
            cls.poll_message_set("Please select exactly two mesh IFC objects.")
            return False
        return True

    def _execute(self, context):
        _commit_pending_wall_edits_for_selection(context)
        active_obj = context.active_object
        assert active_obj
        selected_objs = tool.Model.get_selected_mesh_objects()
        DumbWallJoiner().merge(next(o for o in selected_objs if o != active_obj), active_obj)
        return {"FINISHED"}


class RecalculateWall(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.recalculate_wall"
    bl_label = "Recalculate Wall"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if not tool.Model.has_selected_mesh_ifc_objects():
            cls.poll_message_set("No mesh IFC objects selected.")
            return False
        return True

    def _execute(self, context):
        objects = tool.Model.get_selected_mesh_ifc_objects()
        tool.Model.recalculate_walls(objects)
        return {"FINISHED"}


class ChangeExtrusionDepth(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.change_extrusion_depth"
    bl_label = "Update"
    bl_description = "Update height for the selected objects."
    bl_options = {"REGISTER", "UNDO"}
    depth: bpy.props.FloatProperty()

    @classmethod
    def poll(cls, context):
        if not tool.Model.has_selected_mesh_ifc_objects():
            cls.poll_message_set("No mesh IFC objects selected.")
            return False
        return True

    def _execute(self, context):
        layer2_objs: list[bpy.types.Object] = []
        ifc_file = tool.Ifc.get()
        si_conversion = ifcopenshell.util.unit.calculate_unit_scale(ifc_file)
        selected_objs = tool.Model.get_selected_mesh_ifc_objects()

        for obj in selected_objs:
            element = tool.Ifc.get_entity(obj)
            assert element

            representation = ifcopenshell.util.representation.get_representation(element, "Model", "Body", "MODEL_VIEW")
            if not representation:
                continue
            extrusion = tool.Model.get_extrusion(representation)
            if not extrusion:
                continue
            x, y, z = extrusion.ExtrudedDirection.DirectionRatios
            x_angle = Vector((0, 1)).angle_signed(Vector((y, z)))
            extrusion.Depth = self.depth / si_conversion * (1 / cos(x_angle))
            if tool.Model.get_usage_type(element) == "LAYER2":
                for rel in element.ConnectedFrom:
                    if rel.is_a() == "IfcRelConnectsElements":
                        ifcopenshell.api.geometry.disconnect_element(
                            ifc_file,
                            relating_element=rel.RelatingElement,
                            related_element=element,
                        )
                layer2_objs.append(obj)

        if layer2_objs:
            tool.Model.recalculate_walls(layer2_objs)
        return {"FINISHED"}


class ChangeExtrusionXAngle(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.change_extrusion_x_angle"
    bl_label = "Update"
    bl_description = "Update angle for the selected objects."
    bl_options = {"REGISTER", "UNDO"}
    x_angle: bpy.props.FloatProperty(name="X Angle", default=0, subtype="ANGLE")

    @classmethod
    def poll(cls, context):
        if not tool.Model.has_selected_mesh_ifc_objects():
            cls.poll_message_set("No mesh IFC objects selected.")
            return False
        return True

    def _execute(self, context):
        layer2_objs: list[bpy.types.Object] = []
        x_angle = 0 if tool.Cad.is_x(self.x_angle, 0, tolerance=0.001) else self.x_angle
        x_angle = 0 if tool.Cad.is_x(self.x_angle, pi, tolerance=0.001) else self.x_angle
        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        selected_objs = tool.Model.get_selected_mesh_ifc_objects()
        builder = ifcopenshell.util.shape_builder.ShapeBuilder(tool.Ifc.get())

        for obj in selected_objs:
            element = tool.Ifc.get_entity(obj)
            assert element
            representation = ifcopenshell.util.representation.get_representation(element, "Model", "Body", "MODEL_VIEW")
            if not representation:
                continue
            extrusion = tool.Model.get_extrusion(representation)
            if not extrusion:
                continue
            existing_x_angle = tool.Model.get_existing_x_angle(extrusion)
            existing_x_angle = 0 if tool.Cad.is_x(existing_x_angle, 0, tolerance=0.001) else existing_x_angle
            existing_x_angle = 0 if tool.Cad.is_x(existing_x_angle, pi, tolerance=0.001) else existing_x_angle
            if tool.Model.get_usage_type(element) == "LAYER2":
                x, y, z = extrusion.ExtrudedDirection.DirectionRatios
                depth = core.vertical_height_from_extrusion_depth(extrusion.Depth, existing_x_angle)
                perpendicular_depth = depth * abs(1 / cos(x_angle))
                extrusion.ExtrudedDirection.DirectionRatios = (0.0, sin(x_angle), cos(x_angle))
                layer2_objs.append(obj)
                extrusion.Depth = perpendicular_depth
            else:
                if tool.Model.get_usage_type(element) == "LAYER3":
                    existing_x_angle = obj.rotation_euler.x
                    existing_x_angle = 0 if tool.Cad.is_x(existing_x_angle, 0, tolerance=0.001) else existing_x_angle
                    existing_x_angle = 0 if tool.Cad.is_x(existing_x_angle, pi, tolerance=0.001) else existing_x_angle

                    profiles = (
                        extrusion.SweptArea.Profiles
                        if extrusion.SweptArea.is_a("IfcCompositeProfileDef")
                        else [extrusion.SweptArea]
                    )
                    for profile in profiles:
                        coord_list = builder.get_polyline_coords(profile.OuterCurve)
                        coord_list = [
                            (p[0], p[1] * abs(cos(existing_x_angle))) for p in coord_list
                        ]  # Reset the transformation and returns to the original points with 0 degrees
                        coord_list = [
                            (p[0], p[1] * abs(1 / cos(x_angle))) for p in coord_list
                        ]  # Apply the transformation for the new x_angle
                        builder.set_polyline_coords(profile.OuterCurve, coord_list)

                    # The extrusion direction calculated previously default to the positive direction
                    # Here we set the extrusion direction to negative if that's the case
                    direction_ratios = Vector((0.0, sin(x_angle), cos(x_angle)))
                    # direction_ratios = Vector(extrusion.ExtrudedDirection.DirectionRatios)
                    layer_params = tool.Model.get_material_layer_parameters(element)
                    perpendicular_depth = layer_params["thickness"] * abs(1 / cos(x_angle)) / unit_scale
                    perpendicular_offset = layer_params["offset"] * abs(1 / cos(x_angle)) / unit_scale
                    offset_direction = direction_ratios.copy()

                    # Check angle and z direction to determine whether the extrusion direction is positive or negative
                    if (abs(x_angle) < (pi / 2) and direction_ratios.z > 0) or (
                        abs(x_angle) > (pi / 2) and direction_ratios.z < 0
                    ):
                        # The extrusion direction is positive. If the layer_parameter is set to negative,
                        # then the we change the extrusion direction.
                        if layer_params["direction_sense"] == "NEGATIVE":
                            direction_ratios *= -1
                    elif ((x_angle) > (pi / 2) and direction_ratios.z > 0) or (
                        (x_angle) < (pi / 2) and direction_ratios.z < 0
                    ):
                        # The extrusion direction is negative. If the layer_parameter is set to positive,
                        # then the we change the extrusion direction.
                        # then the we change the extrusion direction. And the offset direction should remain positive
                        # for either direction sense, so we change it.
                        offset_direction *= -1
                        if layer_params["direction_sense"] == "POSITIVE":
                            direction_ratios *= -1

                    extrusion.ExtrudedDirection.DirectionRatios = tuple(direction_ratios)
                    extrusion.Depth = perpendicular_depth

                    if extrusion.Position or perpendicular_offset != 0:
                        position = offset_direction * perpendicular_offset
                        tool.Model.add_extrusion_position(extrusion, position)

                bonsai.core.geometry.switch_representation(
                    tool.Ifc,
                    tool.Geometry,
                    obj=obj,
                    representation=representation,
                )

                # Object rotation
                current_z_rot = obj.rotation_euler.z
                rot_mat = mathutils.Matrix.Rotation(x_angle, 4, "X")
                obj.rotation_euler = rot_mat.to_euler()
                obj.rotation_euler.z = current_z_rot

        if layer2_objs:
            tool.Model.recalculate_walls(layer2_objs)
        return {"FINISHED"}


class ChangeLayerLength(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.change_layer_length"
    bl_label = "Update"
    bl_description = "Update length for the selected objects."
    bl_options = {"REGISTER", "UNDO"}
    length: bpy.props.FloatProperty()

    @classmethod
    def poll(cls, context):
        if not tool.Model.has_selected_mesh_ifc_objects():
            cls.poll_message_set("No mesh IFC objects selected.")
            return False
        return True

    def _execute(self, context):
        joiner = DumbWallJoiner()
        selected_objs = tool.Model.get_selected_mesh_ifc_objects()
        for obj in selected_objs:
            joiner.set_length(obj, self.length)


class OffsetWalls(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.offset_walls"
    bl_label = "Offset Walls"
    bl_description = "Offset selected objects from their reference line."
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if not tool.Model.has_selected_mesh_ifc_objects():
            cls.poll_message_set("No mesh IFC objects selected.")
            return False
        return True

    def _execute(self, context):
        props = tool.Model.get_model_props()
        core.offset_walls(tool.Ifc, tool.Blender, tool.Model, props.offset_type_vertical)


class AddWallsFromSlab(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.draw_walls_from_slab"
    bl_label = "Draw Slab From Wall"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.space_data.type == "VIEW_3D"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.relating_type = None
        props = tool.Model.get_model_props()
        relating_type_id = props.relating_type_id
        if relating_type_id:
            self.relating_type = tool.Ifc.get().by_id(int(relating_type_id))

    def _execute(self, context):
        if not self.relating_type:
            return {"FINISHED"}
        slab = tool.Ifc.get_entity(context.active_object)
        if not slab.is_a("IfcSlab"):
            self.report(
                {"WARNING"},
                "Please select a slab.",
            )
            return {"FINISHED"}
        walls = DumbWallGenerator(self.relating_type).generate("SLAB")

        if walls:
            for wall1, wall2 in zip(walls, walls[1:] + [walls[0]]):
                DumbWallJoiner().connect(wall2["obj"], wall1["obj"])


class DrawPolylineWall(bpy.types.Operator, PolylineOperator, tool.Ifc.Operator):
    bl_idname = "bim.draw_polyline_wall"
    bl_label = "Draw Polyline Wall"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.space_data.type == "VIEW_3D"

    def __init__(self, *args, **kwargs):
        bpy.types.Operator.__init__(self, *args, **kwargs)
        PolylineOperator.__init__(self)
        self.relating_type = None
        props = tool.Model.get_model_props()
        relating_type_id = props.relating_type_id
        if relating_type_id:
            self.relating_type = tool.Ifc.get().by_id(int(relating_type_id))

    def create_walls_from_polyline(self, context: bpy.types.Context) -> Union[set[str], None]:
        if not self.relating_type:
            return {"FINISHED"}

        model_props = tool.Model.get_model_props()
        direction_sense = model_props.direction_sense
        offset = model_props.offset

        walls, is_polyline_closed = DumbWallGenerator(self.relating_type).generate("POLYLINE")
        for wall in walls:
            model = tool.Ifc.get()
            element = tool.Ifc.get_entity(wall["obj"])
            material = ifcopenshell.util.element.get_material(element)
            material_set_usage = model.by_id(material.id())
            # if material.is_a("IfcMaterialLayerSetUsage"):
            attributes = {"OffsetFromReferenceLine": offset, "DirectionSense": direction_sense}
            ifcopenshell.api.material.edit_layer_usage(model, usage=material_set_usage, attributes=attributes)
            tool.Model.recalculate_walls([wall["obj"]])

        if walls:
            if is_polyline_closed:
                for wall1, wall2 in zip(walls, walls[1:] + [walls[0]]):
                    DumbWallJoiner().connect(wall2["obj"], wall1["obj"])
            else:
                for wall1, wall2 in zip(walls[:-1], walls[1:]):
                    DumbWallJoiner().connect(wall2["obj"], wall1["obj"])

    def modal(self, context, event):
        return IfcStore.execute_ifc_operator(self, context, event, method="MODAL")

    def _modal(self, context, event):
        if not self.relating_type:
            self.report({"WARNING"}, "You need to select a wall type.")
            PolylineDecorator.uninstall()
            tool.Blender.update_viewport()
            return {"FINISHED"}

        PolylineDecorator.update(event, self.tool_state, self.input_ui, self.snapping_points[0])
        tool.Blender.update_viewport()

        self.handle_lock_axis(context, event)  # Must come before "PASS_TRHOUGH"

        if event.type in {"MIDDLEMOUSE", "WHEELUPMOUSE", "WHEELDOWNMOUSE"}:
            self.handle_mouse_move(context, event)
            return {"PASS_THROUGH"}

        props = tool.Model.get_model_props()
        # Wall axis settings
        if event.value == "RELEASE" and event.type == "F":
            direction_sense = props.direction_sense
            props.direction_sense = "NEGATIVE" if direction_sense == "POSITIVE" else "POSITIVE"
            self.set_offset(context, self.relating_type)

        if event.value == "RELEASE" and event.type == "O":
            items = ("EXTERIOR", "CENTER", "INTERIOR")
            index = items.index(props.offset_type_vertical)
            size = len(items)
            props.offset_type_vertical = items[((index + 1) % size)]
            self.set_offset(context, self.relating_type)

        custom_instructions = {"Choose Axis": {"icons": True, "keys": ["EVENT_X", "EVENT_Y"]}}

        wall_config = [
            f"Direction: {props.direction_sense}",
            f"Offset Type: {props.offset_type_vertical}",
            f"Offset Value: {tool.Polyline.format_input_ui_units(props.offset * self.unit_scale)}",
        ]

        self.handle_instructions(context, custom_instructions, wall_config)

        self.handle_mouse_move(context, event, should_round=True)

        self.choose_axis(event)

        self.handle_snap_selection(context, event)

        if (
            not self.tool_state.is_input_on
            and event.value == "RELEASE"
            and event.type in {"RET", "NUMPAD_ENTER", "RIGHTMOUSE"}
        ):
            self.create_walls_from_polyline(context)
            context.workspace.status_text_set(text=None)
            self.tool_state.plane_method = None
            ProductDecorator.uninstall()
            PolylineDecorator.uninstall()
            tool.Polyline.clear_polyline()
            tool.Blender.update_viewport()
            return {"FINISHED"}

        self.handle_keyboard_input(context, event)
        self.handle_inserting_polyline(context, event)

        cancel = self.handle_cancelation(context, event)
        if cancel is not None:
            ProductDecorator.uninstall()
            return cancel

        return {"RUNNING_MODAL"}

    def invoke(self, context, event):
        return IfcStore.execute_ifc_operator(self, context, event, method="INVOKE")

    def _invoke(self, context, event):
        super().invoke(context, event)
        ProductDecorator.install(context)
        self.tool_state.use_default_container = True
        self.tool_state.plane_method = "XY"
        self.set_offset(context, self.relating_type)
        return {"RUNNING_MODAL"}


class DumbWallAligner:
    # An alignment shifts the origin of all walls to the closest point on the
    # local X axis of the reference wall. In addition, the Z rotation is copied.
    # Z translations are ignored for alignment.
    def set_reference_wall(self, reference_wall: bpy.types.Object):
        self.reference_wall = reference_wall

    def align_centerline(self, wall: bpy.types.Object) -> None:
        self.wall = wall
        self.align_rotation()

        l_start = Vector(self.reference_wall.bound_box[0]).lerp(Vector(self.reference_wall.bound_box[3]), 0.5)
        l_end = Vector(self.reference_wall.bound_box[4]).lerp(Vector(self.reference_wall.bound_box[7]), 0.5)

        start = self.reference_wall.matrix_world @ l_start
        end = self.reference_wall.matrix_world @ l_end

        l_snap_point = Vector(self.wall.bound_box[0]).lerp(Vector(self.wall.bound_box[3]), 0.5)
        snap_point = self.wall.matrix_world @ l_snap_point
        offset = snap_point - self.wall.matrix_world.translation

        point, _ = mathutils.geometry.intersect_point_line(snap_point, start, end)

        new_origin = point - offset
        self.wall.matrix_world.translation[0], self.wall.matrix_world.translation[1] = new_origin.xy

    def align_last_layer(self, wall: bpy.types.Object) -> None:
        self.wall = wall
        self.align_rotation()

        if self.is_rotation_flipped():
            element = tool.Ifc.get_entity(self.wall)
            if tool.Model.get_usage_type(element) == "LAYER2":
                DumbWallJoiner().flip(self.wall)
                bpy.context.view_layer.update()
                snap_point = self.wall.matrix_world @ Vector(self.wall.bound_box[3])
            else:
                snap_point = self.wall.matrix_world @ Vector(self.wall.bound_box[0])
        else:
            snap_point = self.wall.matrix_world @ Vector(self.wall.bound_box[3])

        start = self.reference_wall.matrix_world @ Vector(self.reference_wall.bound_box[3])
        end = self.reference_wall.matrix_world @ Vector(self.reference_wall.bound_box[7])

        point, _ = mathutils.geometry.intersect_point_line(snap_point, start, end)

        offset = snap_point - self.wall.matrix_world.translation
        new_origin = point - offset
        self.wall.matrix_world.translation[0], self.wall.matrix_world.translation[1] = new_origin.xy

    def align_first_layer(self, wall: bpy.types.Object) -> None:
        self.wall = wall
        self.align_rotation()

        if self.is_rotation_flipped():
            element = tool.Ifc.get_entity(self.wall)
            if tool.Model.get_usage_type(element) == "LAYER2":
                DumbWallJoiner().flip(self.wall)
                bpy.context.view_layer.update()
                snap_point = self.wall.matrix_world @ Vector(self.wall.bound_box[0])
            else:
                snap_point = self.wall.matrix_world @ Vector(self.wall.bound_box[3])
        else:
            snap_point = self.wall.matrix_world @ Vector(self.wall.bound_box[0])

        start = self.reference_wall.matrix_world @ Vector(self.reference_wall.bound_box[0])
        end = self.reference_wall.matrix_world @ Vector(self.reference_wall.bound_box[4])

        point, _ = mathutils.geometry.intersect_point_line(snap_point, start, end)

        offset = snap_point - self.wall.matrix_world.translation
        new_origin = point - offset
        self.wall.matrix_world.translation[0], self.wall.matrix_world.translation[1] = new_origin.xy

    def align_rotation(self) -> None:
        reference = (self.reference_wall.matrix_world.to_quaternion() @ Vector((1, 0, 0))).to_2d()
        wall = (self.wall.matrix_world.to_quaternion() @ Vector((1, 0, 0))).to_2d()
        angle = reference.angle_signed(wall)
        if round(degrees(angle) % 360) in (0, 180):
            return
        elif angle > (pi / 2):
            self.wall.rotation_euler[2] -= pi - angle
        else:
            self.wall.rotation_euler[2] += angle
        bpy.context.view_layer.update()

    def is_rotation_flipped(self) -> bool:
        reference = (self.reference_wall.matrix_world.to_quaternion() @ Vector((1, 0, 0))).to_2d()
        wall = (self.wall.matrix_world.to_quaternion() @ Vector((1, 0, 0))).to_2d()
        angle = reference.angle_signed(wall)
        return round(degrees(angle) % 360) == 180


class DumbWallGenerator:
    def __init__(self, relating_type):
        self.relating_type = relating_type
        self.unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())

    def generate(self, insertion_type="CURSOR"):
        self.file = tool.Ifc.get()
        self.layers = tool.Model.get_material_layer_parameters(self.relating_type)
        if not self.layers["thickness"]:
            return

        self.body_context = ifcopenshell.util.representation.get_context(tool.Ifc.get(), "Model", "Body", "MODEL_VIEW")
        self.axis_context = ifcopenshell.util.representation.get_context(tool.Ifc.get(), "Plan", "Axis", "GRAPH_VIEW")

        props = tool.Model.get_model_props()

        self.container = None
        self.container_obj = None
        if container := tool.Root.get_default_container():
            self.container = container
            self.container_obj = tool.Ifc.get_object(container)

        self.width = self.layers["thickness"]
        self.height = props.extrusion_depth
        self.length = props.length
        self.rotation = 0.0
        self.location = Vector((0, 0, 0))
        self.x_angle = 0 if tool.Cad.is_x(props.x_angle, 0, tolerance=0.001) else props.x_angle

        if insertion_type == "POLYLINE":
            return self.derive_from_polyline()
        elif insertion_type == "SLAB":
            return self.derive_from_slab()
        elif insertion_type == "CURSOR":
            return self.derive_from_cursor()

    def derive_from_polyline(self) -> tuple[list[Union[dict[str, Any], None]], bool]:
        polyline_props = tool.Model.get_polyline_props()
        polyline_data = polyline_props.insertion_polyline
        polyline_points = polyline_data[0].polyline_points if polyline_data else []
        is_polyline_closed = False
        if len(polyline_points) > 3:
            first_vec = Vector((polyline_points[0].x, polyline_points[0].y, polyline_points[0].z))
            last_vec = Vector((polyline_points[-1].x, polyline_points[-1].y, polyline_points[-1].z))
            if first_vec == last_vec:
                is_polyline_closed = True

        walls = []
        for i in range(len(polyline_points) - 1):
            vec1 = Vector((polyline_points[i].x, polyline_points[i].y, polyline_points[i].z))
            vec2 = Vector((polyline_points[i + 1].x, polyline_points[i + 1].y, polyline_points[i + 1].z))
            coords = (vec1, vec2)
            walls.append(self.create_wall_from_2_points(coords))
        return walls, is_polyline_closed

    def derive_from_slab(self):
        slab_obj = bpy.context.active_object
        slab = tool.Ifc.get_entity(slab_obj)
        container = ifcopenshell.util.element.get_container(slab)
        self.container_obj = tool.Ifc.get_object(container)
        elevation = self.container_obj.location.z
        representation = ifcopenshell.util.representation.get_representation(slab, "Model", "Body", "MODEL_VIEW")
        extrusion = tool.Model.get_extrusion(representation)
        builder = ifcopenshell.util.shape_builder.ShapeBuilder(tool.Ifc.get())
        polyline_points = builder.get_polyline_coords(extrusion.SweptArea.OuterCurve)
        polyline_points = [[(v * self.unit_scale) for v in p] for p in polyline_points]
        polyline_points = [slab_obj.matrix_world @ Vector((p[0], p[1], elevation)) for p in polyline_points]
        if not tool.Cad.is_counter_clockwise_order(polyline_points[0], polyline_points[1], polyline_points[2]):
            polyline_points = polyline_points[::-1]
        walls = []
        for i in range(len(polyline_points) - 1):
            vec1 = polyline_points[i]
            vec2 = polyline_points[i + 1]
            coords = (vec1, vec2)
            walls.append(self.create_wall_from_2_points(coords))
        return walls

    def create_wall_from_2_points(self, coords, should_round=False) -> Union[dict[str, Any], None]:
        direction = coords[1] - coords[0]
        length = direction.length
        data = {"coords": coords}

        self.length = length
        self.rotation = math.atan2(direction[1], direction[0])
        if should_round:
            # Round to nearest 50mm (yes, metric for now)
            self.length = 0.05 * round(length / 0.05)
            angle_snap = tool.Snap.get_angle_snap_value(bpy.context)
            nearest_degree = math.radians(angle_snap)
            self.rotation = nearest_degree * round(self.rotation / nearest_degree)
        self.location = coords[0]
        data["obj"] = self.create_wall()
        return data

    def derive_from_cursor(self) -> bpy.types.Object:
        RAYCAST_PRECISION = 0.01
        self.location = bpy.context.scene.cursor.location
        if self.container:
            for subelement in ifcopenshell.util.element.get_decomposition(self.container):
                if not subelement.is_a("IfcWall"):
                    continue
                sibling_obj = tool.Ifc.get_object(subelement)
                if not sibling_obj or not isinstance(sibling_obj.data, bpy.types.Mesh):
                    continue
                inv_obj_matrix = sibling_obj.matrix_world.inverted()
                local_location = inv_obj_matrix @ self.location
                try:
                    raycast = sibling_obj.closest_point_on_mesh(local_location, distance=RAYCAST_PRECISION)
                except:
                    # If the mesh has no faces
                    raycast = [None]
                if not raycast[0]:
                    continue
                for face in sibling_obj.data.polygons:
                    normal = (sibling_obj.matrix_world.to_quaternion() @ face.normal).normalized()
                    face_center = sibling_obj.matrix_world @ face.center
                    if (
                        normal.z != 0
                        or abs(mathutils.geometry.distance_point_to_plane(self.location, face_center, normal)) > 0.01
                    ):
                        continue

                    rotation = math.atan2(normal[1], normal[0])
                    rotated_y_axis = Matrix.Rotation(-rotation, 4, "Z")[1].xyz

                    # since wall thickness goes by local Y+ axis
                    # we find best position for the next wall
                    # by finding the face of another wall that will be very close to the some test point.
                    # test point is calculated by applying to cursor position some little offset along the face
                    #
                    # a bit different offset to be safe on raycast
                    test_pos = self.location + rotated_y_axis * RAYCAST_PRECISION * 1.1
                    test_pos_local = inv_obj_matrix @ test_pos
                    raycast = sibling_obj.closest_point_on_mesh(test_pos_local, distance=RAYCAST_PRECISION)

                    if not raycast[0]:
                        continue
                    self.rotation = rotation
                    break

                if self.rotation != 0:
                    break
        return self.create_wall()

    def create_wall(self) -> bpy.types.Object:
        props = tool.Model.get_model_props()
        ifc_class = self.get_relating_type_class(self.relating_type)
        mesh = bpy.data.meshes.new("Dummy")
        obj = bpy.data.objects.new(tool.Model.generate_occurrence_name(self.relating_type, ifc_class), mesh)

        matrix_world = Matrix.Rotation(self.rotation, 4, "Z")
        matrix_world.translation = self.location
        if self.container_obj:
            matrix_world.translation.z = self.container_obj.location.z + props.rl1
        obj.matrix_world = matrix_world
        bpy.context.view_layer.update()

        element = bonsai.core.root.assign_class(
            tool.Ifc,
            tool.Collector,
            tool.Root,
            obj=obj,
            ifc_class=ifc_class,
            should_add_representation=False,
        )
        ifcopenshell.api.type.assign_type(self.file, related_objects=[element], relating_type=self.relating_type)
        if self.axis_context:
            representation = ifcopenshell.api.geometry.add_axis_representation(
                tool.Ifc.get(),
                context=self.axis_context,
                axis=[(0.0, 0.0), (self.length, 0.0)],
            )
            ifcopenshell.api.geometry.assign_representation(
                tool.Ifc.get(), product=element, representation=representation
            )
        bonsai.core.geometry.edit_object_placement(tool.Ifc, tool.Geometry, tool.Surveyor, obj=obj)
        representation = ifcopenshell.api.geometry.add_wall_representation(
            tool.Ifc.get(),
            context=self.body_context,
            thickness=self.layers["thickness"],
            direction_sense=self.layers["direction_sense"],
            offset=self.layers["offset"],
            length=self.length,
            height=self.height,
            x_angle=self.x_angle,
        )
        ifcopenshell.api.geometry.assign_representation(tool.Ifc.get(), product=element, representation=representation)
        bonsai.core.geometry.switch_representation(
            tool.Ifc,
            tool.Geometry,
            obj=obj,
            representation=representation,
        )
        pset = ifcopenshell.api.pset.add_pset(self.file, product=element, name="EPset_Parametric")
        ifcopenshell.api.pset.edit_pset(self.file, pset=pset, properties={"Engine": "Bonsai.DumbLayer2"})
        material = ifcopenshell.util.element.get_material(element)
        material.LayerSetDirection = "AXIS2"
        tool.Blender.select_object(obj)
        return obj

    def get_relating_type_class(self, relating_type: ifcopenshell.entity_instance) -> str:
        classes = ifcopenshell.util.type.get_applicable_entities(relating_type.is_a(), tool.Ifc.get().schema)
        return next(c for c in classes if "StandardCase" not in c)


class DumbWallPlaner:
    def regenerate_from_layer(self, layer: ifcopenshell.entity_instance) -> None:
        for layer_set in layer.ToMaterialLayerSet:
            self.regenerate_from_layer_set(layer_set)

    def regenerate_from_layer_set(self, layer_set: ifcopenshell.entity_instance) -> None:
        walls = []
        total_thickness = sum([l.LayerThickness for l in layer_set.MaterialLayers])
        if not total_thickness:
            return
        for inverse in tool.Ifc.get().get_inverse(layer_set):
            if not inverse.is_a("IfcMaterialLayerSetUsage") or inverse.LayerSetDirection != "AXIS2":
                continue
            if tool.Ifc.get().schema == "IFC2X3":
                for rel in tool.Ifc.get().get_inverse(inverse):
                    if not rel.is_a("IfcRelAssociatesMaterial"):
                        continue
                    walls.extend([tool.Ifc.get_object(e) for e in rel.RelatedObjects])
            else:
                for rel in inverse.AssociatedTo:
                    walls.extend([tool.Ifc.get_object(e) for e in rel.RelatedObjects])
        tool.Model.recalculate_walls([w for w in set(walls) if w])


def _opening_axis_extent(opening, axis_reference, unit_scale):
    """Return ``(min_t, max_t)``: the opening's world-space footprint
    projected onto ``axis_reference`` as parametric positions along the
    wall axis (``0`` is the start of the axis line, ``1`` is its end).
    Used to detect openings whose footprint straddles a cut.

    Computed via ``ifcopenshell.geom.create_shape`` so the result is
    correct for any representation type Bonsai may produce — mapped
    representations, swept-area solids, breps, boolean clips, etc. —
    without needing a Blender object (Bonsai hides openings after
    ``bim.add_opening``). Falls back to a degenerate single-point range
    at the placement origin only when the geometry kernel cannot build
    a shape from the opening."""
    verts = None
    shape_matrix: Optional[Matrix] = None
    try:
        settings = ifcopenshell.geom.settings()
        shape = ifcopenshell.geom.create_shape(settings, opening)
        verts = ifcopenshell.util.shape.get_vertices(shape.geometry)
        shape_matrix = Matrix(ifcopenshell.util.shape.get_shape_matrix(shape).tolist())
    except Exception:
        verts = None
        shape_matrix = None

    if verts is None or shape_matrix is None or len(verts) == 0:
        placement = Matrix(ifcopenshell.util.placement.get_local_placement(opening.ObjectPlacement).tolist())
        placement.translation *= unit_scale
        _, t = mathutils.geometry.intersect_point_line(placement.translation.to_2d(), *axis_reference)
        return t, t

    positions = []
    for v in verts:
        world = (shape_matrix @ Vector((float(v[0]), float(v[1]), float(v[2])))).to_2d()
        _, t = mathutils.geometry.intersect_point_line(world, *axis_reference)
        positions.append(t)
    return min(positions), max(positions)


def _add_void_copy(building_element, source_opening):
    """Add an unfilled IfcOpeningElement to ``building_element`` whose
    geometry and placement mirror ``source_opening``. Used when a filled
    opening's void straddles a wall split — the filling stays on its wall,
    but the void must also apply to the neighbour so its body gets cut."""
    void_copy = ifcopenshell.api.root.copy_class(tool.Ifc.get(), product=source_opening)
    for fill_rel in list(void_copy.HasFillings or ()):
        tool.Ifc.get().remove(fill_rel)
    void_copy.VoidsElements[0].RelatingBuildingElement = building_element
    if void_copy.ObjectPlacement and void_copy.ObjectPlacement.is_a("IfcLocalPlacement"):
        if building_element.ObjectPlacement:
            void_copy.ObjectPlacement.PlacementRelTo = building_element.ObjectPlacement
    if source_opening.Representation:
        void_copy.Representation = ifcopenshell.util.element.copy_deep(
            tool.Ifc.get(), source_opening.Representation, exclude=["IfcGeometricRepresentationContext"]
        )


class DumbWallJoiner:
    def __init__(self):
        self.unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        self.axis_context = ifcopenshell.util.representation.get_context(tool.Ifc.get(), "Plan", "Axis", "GRAPH_VIEW")
        self.body_context = ifcopenshell.util.representation.get_context(tool.Ifc.get(), "Model", "Body", "MODEL_VIEW")

    def unjoin(self, wall1):
        element1 = tool.Ifc.get_entity(wall1)
        if not element1:
            return

        ifcopenshell.api.geometry.disconnect_path(tool.Ifc.get(), element=element1, connection_type="ATSTART")
        ifcopenshell.api.geometry.disconnect_path(tool.Ifc.get(), element=element1, connection_type="ATEND")

        axis1 = tool.Model.get_wall_axis(wall1)
        axis = copy.deepcopy(axis1["reference"])
        body = copy.deepcopy(axis1["reference"])
        tool.Model.recreate_wall(element1, wall1)

    def split(self, wall1: bpy.types.Object, target: Vector) -> None:
        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())

        element1 = tool.Ifc.get_entity(wall1)
        if not element1:
            return

        if tool.Ifc.is_moved(wall1):
            bonsai.core.geometry.edit_object_placement(tool.Ifc, tool.Geometry, tool.Surveyor, obj=wall1)

        axis1 = tool.Model.get_wall_axis(wall1)
        intersect, cut_percentage = mathutils.geometry.intersect_point_line(target.to_2d(), *axis1["reference"])
        if cut_percentage < 0 or cut_percentage > 1 or tool.Cad.is_x(cut_percentage, (0, 1)):
            return

        wall2 = self.duplicate_wall(wall1)
        element2 = tool.Ifc.get_entity(wall2)

        # Get the ATEND connection from wall1 to use it in wall2
        relating_element = None
        connections = element1.ConnectedTo
        for conn in connections:
            if conn.is_a("IfcRelConnectsPathElements") and conn.RelatingConnectionType == "ATEND":
                relating_element = conn.RelatedElement
                relating_connection = conn.RelatedConnectionType
                description = conn.Description
                bonsai.core.geometry.remove_connection(tool.Geometry, connection=conn)
        connections = element1.ConnectedFrom
        for conn in connections:
            if conn.is_a("IfcRelConnectsPathElements") and conn.RelatedConnectionType == "ATEND":
                relating_element = conn.RelatingElement
                relating_connection = conn.RelatingConnectionType
                description = conn.Description
                bonsai.core.geometry.remove_connection(tool.Geometry, connection=conn)
        if relating_element:
            ifcopenshell.api.geometry.connect_path(
                tool.Ifc.get(),
                relating_element=relating_element,
                related_element=element2,
                relating_connection=relating_connection,
                related_connection="ATEND",
                description=description,
            )

        # During the duplication process, unfilled voids are copied, so we need
        # to check openings on both element1 and element2. Each wall keeps the
        # opening when the opening's axis-projected extent overlaps that wall's
        # portion of the axis — straddling openings are intentionally kept on
        # both walls so each wall body gets the appropriate cut. Strict
        # inequalities mean a boundary-only touch (or a degenerate single-point
        # extent at the cut) keeps the opening on both walls — the safer
        # default when the helper cannot resolve a true bounding range.
        for opening in [
            r.RelatedOpeningElement for r in element1.HasOpenings if not r.RelatedOpeningElement.HasFillings
        ]:
            min_t, _ = _opening_axis_extent(opening, axis1["reference"], unit_scale)
            if min_t > cut_percentage:
                # Opening lies entirely past the cut — only element2 should keep it.
                ifcopenshell.api.feature.remove_feature(tool.Ifc.get(), feature=opening)

        for opening in [
            r.RelatedOpeningElement for r in element2.HasOpenings if not r.RelatedOpeningElement.HasFillings
        ]:
            _, max_t = _opening_axis_extent(opening, axis1["reference"], unit_scale)
            if max_t < cut_percentage:
                # Opening lies entirely before the cut — only element1 should keep it.
                ifcopenshell.api.feature.remove_feature(tool.Ifc.get(), feature=opening)

        # During the duplication process, filled voids are not copied. So we
        # only need to check fillings on the original element1. The filling
        # (door/window) belongs to whichever wall contains its center, but the
        # void may need to apply to both walls when the void's extent straddles
        # the cut — otherwise the neighbour wall's body would not be cut.
        for opening in [
            r.RelatedOpeningElement for r in list(element1.HasOpenings) if r.RelatedOpeningElement.HasFillings
        ]:
            rel = opening.HasFillings[0]
            filling = rel.RelatedBuildingElement
            filling_obj = tool.Ifc.get_object(filling)
            filling_location = filling_obj.matrix_world.translation
            _, filling_position = mathutils.geometry.intersect_point_line(filling_location.to_2d(), *axis1["reference"])
            min_t, max_t = _opening_axis_extent(opening, axis1["reference"], unit_scale)
            void_straddles = min_t < cut_percentage < max_t
            if filling_position > cut_percentage:
                # The filling should be moved from element1 to element2.
                new_opening = ifcopenshell.api.root.copy_class(tool.Ifc.get(), product=opening)
                new_opening.VoidsElements[0].RelatingBuildingElement = element2
                if new_opening.ObjectPlacement and new_opening.ObjectPlacement.is_a("IfcLocalPlacement"):
                    if element2.ObjectPlacement:
                        new_opening.ObjectPlacement.PlacementRelTo = element2.ObjectPlacement
                # For now, we do copy opening representations
                if opening.Representation:
                    new_opening.Representation = ifcopenshell.util.element.copy_deep(
                        tool.Ifc.get(), opening.Representation, exclude=["IfcGeometricRepresentationContext"]
                    )

                rel.RelatingOpeningElement = new_opening

                # Remove the old opening
                ifcopenshell.api.feature.remove_feature(tool.Ifc.get(), feature=opening)

                if void_straddles:
                    # Filling moved to element2, but void straddles — add a
                    # pure-void copy back to element1 so its body still gets cut.
                    _add_void_copy(element1, new_opening)
            elif void_straddles:
                # Filling stays on element1, but void straddles — add a pure-void
                # copy to element2 so its body gets cut.
                _add_void_copy(element2, opening)

        p1, p2 = ifcopenshell.util.representation.get_reference_line(element1)
        p3 = (wall1.matrix_world.inverted() @ intersect.to_3d()).to_2d() / unit_scale
        self.set_axis(element1, p1, p3)
        self.set_axis(element2, p3, p2)

        tool.Model.recreate_wall(element1, wall1)
        tool.Model.recreate_wall(element2, wall2)

    def flip(self, wall1: bpy.types.Object) -> None:
        if tool.Ifc.is_moved(wall1):
            bonsai.core.geometry.edit_object_placement(tool.Ifc, tool.Geometry, tool.Surveyor, obj=wall1)

        if (
            not (element1 := tool.Ifc.get_entity(wall1))
            or not (usage := ifcopenshell.util.element.get_material(element1))
            or not usage.is_a("IfcMaterialLayerSetUsage")
            or usage.LayerSetDirection != "AXIS2"
        ):
            return

        thickness = sum([l.LayerThickness for l in usage.ForLayerSet.MaterialLayers])
        if usage.DirectionSense == "POSITIVE":
            usage.DirectionSense = "NEGATIVE"
        else:
            thickness *= -1
            usage.DirectionSense = "POSITIVE"

        matrix = ifcopenshell.util.placement.get_local_placement(element1.ObjectPlacement)
        offset = matrix[:, 1] * thickness
        matrix[:, 3] += offset
        ifcopenshell.api.geometry.edit_object_placement(
            tool.Ifc.get(), product=element1, matrix=matrix, is_si=False, should_transform_children=False
        )
        tool.Model.recreate_wall(element1, wall1)

    def merge(self, wall1: bpy.types.Object, wall2: bpy.types.Object) -> None:
        if tool.Ifc.is_moved(wall1):
            bonsai.core.geometry.edit_object_placement(tool.Ifc, tool.Geometry, tool.Surveyor, obj=wall1)
        if tool.Ifc.is_moved(wall2):
            bonsai.core.geometry.edit_object_placement(tool.Ifc, tool.Geometry, tool.Surveyor, obj=wall2)

        element1 = tool.Ifc.get_entity(wall1)
        element2 = tool.Ifc.get_entity(wall2)
        assert element1 and element2

        p1, p2 = ifcopenshell.util.representation.get_reference_line(element1)
        p3, p4 = ifcopenshell.util.representation.get_reference_line(element2)

        matrix1i = np.linalg.inv(ifcopenshell.util.placement.get_local_placement(element1.ObjectPlacement))
        matrix2 = ifcopenshell.util.placement.get_local_placement(element2.ObjectPlacement)

        p3 = (matrix1i @ matrix2 @ np.concatenate((p3, (0, 1))))[:2]
        p4 = (matrix1i @ matrix2 @ np.concatenate((p4, (0, 1))))[:2]

        if not np.isclose(p1[1], p4[1], atol=1e-02) or not np.isclose(p3[1], p4[1], atol=1e-02):
            return

        x_ordinates = tuple(co[0] for co in (p1, p2, p3, p4))
        p1[0] = min(x_ordinates)
        p2[0] = max(x_ordinates)
        self.set_axis(element1, p1, p2)

        for rel in element2.ConnectedTo:
            ifcopenshell.api.geometry.disconnect_path(
                tool.Ifc.get(), element=element1, connection_type=rel.RelatingConnectionType
            )
            ifcopenshell.api.geometry.connect_path(
                tool.Ifc.get(),
                relating_element=element1,
                related_element=rel.RelatedElement,
                relating_connection=rel.RelatingConnectionType,
                related_connection=rel.RelatedConnectionType,
            )

        for rel in element2.ConnectedFrom:
            ifcopenshell.api.geometry.disconnect_path(
                tool.Ifc.get(), element=element1, connection_type=rel.RelatedConnectionType
            )
            ifcopenshell.api.geometry.connect_path(
                tool.Ifc.get(),
                relating_element=rel.RelatingElement,
                related_element=element1,
                relating_connection=rel.RelatingConnectionType,
                related_connection=rel.RelatedConnectionType,
            )

        tool.Model.recreate_wall(element1, wall1)

        tool.Geometry.delete_ifc_object(wall2)

    def duplicate_wall(self, wall1):
        wall2 = wall1.copy()
        wall2.data = wall2.data.copy()
        for collection in wall1.users_collection:
            collection.objects.link(wall2)
        bonsai.core.root.copy_class(tool.Ifc, tool.Collector, tool.Geometry, tool.Root, obj=wall2)
        return wall2

    def set_axis(self, wall, p1, p2):
        axis = ifcopenshell.util.representation.get_context(tool.Ifc.get(), "Plan", "Axis", "GRAPH_VIEW")
        builder = ifcopenshell.util.shape_builder.ShapeBuilder(tool.Ifc.get())
        item = builder.polyline([p1, p2])
        rep = builder.get_representation(axis, items=[item])
        if old_rep := ifcopenshell.util.representation.get_representation(wall, axis):
            ifcopenshell.util.element.replace_element(old_rep, rep)
            ifcopenshell.util.element.remove_deep2(tool.Ifc.get(), old_rep)
        else:
            ifcopenshell.api.geometry.assign_representation(tool.Ifc.get(), product=wall, representation=rep)

    def extend(self, wall1, target, connection=False):
        if tool.Ifc.is_moved(wall1):
            bonsai.core.geometry.edit_object_placement(tool.Ifc, tool.Geometry, tool.Surveyor, obj=wall1)
        element1 = tool.Ifc.get_entity(wall1)
        p1, p2 = ifcopenshell.util.representation.get_reference_line(element1)
        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        target = (wall1.matrix_world.inverted() @ target).to_2d() / unit_scale
        intersect, intersection_point = mathutils.geometry.intersect_point_line(target, p1, p2)
        if not connection:
            connection = "ATEND" if intersection_point > 0.5 else "ATSTART"

        ifcopenshell.api.geometry.disconnect_path(tool.Ifc.get(), element=element1, connection_type=connection)

        if connection == "ATEND":
            self.set_axis(element1, p1, intersect)
        else:
            self.set_axis(element1, intersect, p2)
        tool.Model.recreate_wall(element1, wall1)

    def set_length(self, wall1: bpy.types.Object, si_length: float) -> None:
        element1 = tool.Ifc.get_entity(wall1)
        assert element1
        if tool.Ifc.is_moved(wall1):
            bonsai.core.geometry.edit_object_placement(tool.Ifc, tool.Geometry, tool.Surveyor, obj=wall1)

        ifcopenshell.api.geometry.disconnect_path(tool.Ifc.get(), element=element1, connection_type="ATEND")

        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        p1, p2 = ifcopenshell.util.representation.get_reference_line(element1)
        p2[0] = p1[0] + si_length / unit_scale
        self.set_axis(element1, p1, p2)
        tool.Model.recreate_wall(element1, wall1)

    def connect(self, obj1: bpy.types.Object, obj2: bpy.types.Object) -> None:
        wall1 = tool.Ifc.get_entity(obj1)
        wall2 = tool.Ifc.get_entity(obj2)
        if tool.Ifc.is_moved(obj1):
            bonsai.core.geometry.edit_object_placement(tool.Ifc, tool.Geometry, tool.Surveyor, obj=obj1)
        if tool.Ifc.is_moved(obj2):
            bonsai.core.geometry.edit_object_placement(tool.Ifc, tool.Geometry, tool.Surveyor, obj=obj2)
        ifcopenshell.api.geometry.connect_wall(tool.Ifc.get(), wall1=wall1, wall2=wall2)
        tool.Model.recreate_wall(wall1, obj1)
        tool.Model.recreate_wall(wall2, obj2)

    def create_matrix(self, p, x, y, z):
        return Matrix([x, y, z, p]).to_4x4().transposed()

    def get_extrusion_data(self, representation):
        results = {"item": None, "height": 3.0, "x_angle": 0, "is_sloped": False, "direction": Vector((0, 0, 1))}
        item = representation.Items[0]
        while True:
            if item.is_a("IfcExtrudedAreaSolid"):
                results["item"] = item
                x, y, z = item.ExtrudedDirection.DirectionRatios
                if not tool.Cad.is_x(x, 0) or not tool.Cad.is_x(y, 0) or not tool.Cad.is_x(z, 1):
                    results["direction"] = Vector(item.ExtrudedDirection.DirectionRatios)
                    results["x_angle"] = Vector((0, 1)).angle_signed(Vector((y, z)))
                    results["is_sloped"] = True
                results["height"] = core.vertical_height_from_extrusion_depth(
                    item.Depth * self.unit_scale, results["x_angle"]
                )
                break
            elif item.is_a("IfcBooleanClippingResult"):  # should be before IfcBooleanResult check
                item = item.FirstOperand
            elif item.is_a("IfcBooleanResult"):
                if item.FirstOperand.is_a("IfcExtrudedAreaSolid") or item.FirstOperand.is_a("IfcBooleanResult"):
                    item = item.FirstOperand
                else:
                    item = item.SecondOperand
            else:
                break
        return results

    # TODO reimplement in new version and deprecate
    def clip(self, wall1: bpy.types.Object, slab2: bpy.types.Object) -> float:
        """returns height of the clipped wall, adds clipping plane to `clippings`"""
        element1 = tool.Ifc.get_entity(wall1)
        element2 = tool.Ifc.get_entity(slab2)
        assert element1 and element2

        layers1 = tool.Model.get_material_layer_parameters(element1)
        axis1 = tool.Model.get_wall_axis(wall1, layers1)

        bases = [axis1["base"][0].to_3d(), axis1["base"][1].to_3d(), axis1["side"][0].to_3d(), axis1["side"][1].to_3d()]
        bases = [Vector((v[0], v[1], wall1.matrix_world.translation.z)) for v in bases]  # add wall Z location

        representation = tool.Geometry.get_active_representation(wall1)
        assert representation
        extrusion = self.get_extrusion_data(representation)
        wall_dir = wall1.matrix_world.to_quaternion() @ extrusion["direction"]

        slab_element = tool.Ifc.get_entity(slab2)
        slab_params = tool.Model.get_material_layer_parameters(slab_element)
        slab_representation = ifcopenshell.util.representation.get_representation(
            slab_element, "Model", "Body", "MODEL_VIEW"
        )
        assert slab_representation
        slab_extrusion = tool.Model.get_extrusion(slab_representation)
        existing_x_angle = tool.Model.get_existing_x_angle(slab_extrusion)
        existing_x_angle = 0 if tool.Cad.is_x(existing_x_angle, 0, tolerance=0.001) else existing_x_angle
        existing_x_angle = 0 if tool.Cad.is_x(existing_x_angle, pi, tolerance=0.001) else existing_x_angle
        offset = slab_params["offset"]
        if slab_params["direction_sense"] == "NEGATIVE":
            offset -= slab_params["thickness"]
        slab_pt = slab2.matrix_world @ Vector((0, 0, 0)) + Vector((0, 0, offset * abs(1 / cos(existing_x_angle))))
        slab_dir = slab2.matrix_world.to_quaternion() @ Vector((0, 0, -1))

        tops = [mathutils.geometry.intersect_line_plane(b, b + wall_dir, slab_pt, slab_dir) for b in bases]
        top_index = max(range(4), key=lambda i: tops[i].z)
        i_top = tops[top_index]
        i_bottom = bases[top_index]

        quaternion = slab2.matrix_world.to_quaternion()
        x_axis = quaternion @ Vector((1, 0, 0))
        y_axis = quaternion @ Vector((0, 1, 0))
        z_axis = quaternion @ Vector((0, 0, 1))
        self.clippings.append(
            {
                "type": "IfcBooleanClippingResult",
                "operand_type": "IfcHalfSpaceSolid",
                "matrix": self.create_matrix(i_top, x_axis, y_axis, z_axis),
            }
        )

        return (i_top - i_bottom).length


class EnableEditingWall(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.enable_editing_wall"
    bl_label = "Edit Wall"
    bl_description = "Show wall edit gizmos"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context: bpy.types.Context) -> set[str]:
        obj = context.active_object
        if not obj:
            return {"CANCELLED"}
        reason = _validate_wall_for_parametric_edit(obj)
        if reason:
            self.report({"WARNING"}, f"Cannot edit wall parametrically: {reason}")
            return {"CANCELLED"}
        # If openings are currently shown for editing (via the Toggle Openings gizmo
        # or the Alt+O hotkey), apply them before entering wall edit mode. Otherwise
        # the wall enters edit mode with floating opening previews that don't reflect
        # the IFC state the gizmos read from.
        if tool.Model.get_model_props().openings:
            bpy.ops.bim.edit_openings(apply_all=True)
        props = tool.Model.get_wall_props(obj)
        # Force is_editing False before populating so update_wall stays a no-op
        # while we copy IFC state into the draft properties.
        props.is_editing = False
        _read_wall_state_into_props(obj, props)
        # Mesh stays as the existing IFC-derived geometry until the first gizmo drag
        # — that way an enable → ✓ round-trip with no drag is a true no-op.
        props.mesh_dirty = False
        props.is_editing = True
        return {"FINISHED"}


class CancelEditingWall(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.cancel_editing_wall"
    bl_label = "Discard Wall Edits"
    bl_description = "Discard wall edits"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context: bpy.types.Context) -> set[str]:
        obj = context.active_object
        if not obj:
            return {"CANCELLED"}
        props = tool.Model.get_wall_props(obj)
        # Disable update_wall first so the snap restores don't redraw the preview.
        props.is_editing = False
        props.length = props.snap_length
        props.height = props.snap_height
        props.thickness = props.snap_thickness
        props.offset = props.snap_offset
        # If the user dragged before cancelling, the visible mesh is the simplified
        # preview box (openings/layers stripped). Restore the real IFC-derived geometry
        # so cancel feels like a true undo — equivalent to the user hitting S_G manually.
        _restore_wall_mesh_if_dirty(obj)
        return {"FINISHED"}


class FinishEditingWall(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.finish_editing_wall"
    bl_label = "Apply Wall Edits"
    bl_description = "Apply wall edits"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context: bpy.types.Context) -> set[str]:
        obj = context.active_object
        if not obj:
            return {"CANCELLED"}
        element = tool.Ifc.get_entity(obj)
        if not element:
            return {"CANCELLED"}
        props = tool.Model.get_wall_props(obj)

        length_changed = not tool.Cad.is_x(props.length, props.snap_length, tolerance=1e-5)
        height_changed = not tool.Cad.is_x(props.height, props.snap_height, tolerance=1e-5)
        x_angle_changed = not tool.Cad.is_x(props.x_angle, props.snap_x_angle, tolerance=1e-5)
        baseline_changed = props.desired_offset_baseline != props.snap_offset_baseline
        any_change = length_changed or height_changed or x_angle_changed or baseline_changed

        # Order matters: baseline shifts the layer-set reference line, then length
        # adjusts endpoints relative to that, then x_angle changes the slope (and
        # recomputes extrusion direction), and height is applied LAST so it reads the
        # final x_angle when converting vertical-height ↔ extrusion-depth. Running
        # height before x_angle made the slope op overwrite the just-set height.
        # temp_override scopes each sub-op to this wall so the delegated operators
        # don't fan out to other selected walls.
        with bpy.context.temp_override(active_object=obj, selected_objects=[obj]):
            if baseline_changed:
                tool.Model.offset_wall(obj, props.desired_offset_baseline)
                tool.Model.recalculate_walls([obj])
                tool.Model.get_model_props().offset_type_vertical = props.desired_offset_baseline
            if length_changed:
                DumbWallJoiner().set_length(obj, props.length)
                tool.Model.recalculate_walls([obj])
            if x_angle_changed:
                bpy.ops.bim.change_extrusion_x_angle(x_angle=props.x_angle)
            if height_changed:
                bpy.ops.bim.change_extrusion_depth(depth=props.height)

        if any_change:
            props.mesh_dirty = False
        else:
            _restore_wall_mesh_if_dirty(obj)
        # Set only on success: if any sub-op above raised, the draft survives for retry.
        props.is_editing = False
        return {"FINISHED"}


class CycleWallOffset(bpy.types.Operator):
    bl_idname = "bim.cycle_wall_offset"
    bl_label = "Cycle Wall Baseline"
    bl_description = "Cycle wall baseline through Exterior, Centreline, Interior. Shift+click reverses"
    bl_options = {"REGISTER", "UNDO"}
    # Deliberately NOT a tool.Ifc.Operator: this operator never calls into
    # ifcopenshell.api. Inheriting from Ifc.Operator would drag a draft-only
    # property cycle into Bonsai's IFC undo transaction system.

    @classmethod
    def poll(cls, context):
        if not tool.Model.has_selected_ifc_objects():
            cls.poll_message_set("No IFC objects selected.")
            return False
        return True

    # Same order the offset_type_vertical EnumProperty uses in prop.py.
    _ORDER = ("EXTERIOR", "CENTER", "INTERIOR")
    reverse: bpy.props.BoolProperty(name="Reverse", default=False, options={"HIDDEN", "SKIP_SAVE"})

    def invoke(self, context: bpy.types.Context, event: bpy.types.Event) -> set[str]:
        self.reverse = event.shift
        return self.execute(context)

    def execute(self, context: bpy.types.Context) -> set[str]:
        obj = context.active_object
        if not obj:
            return {"CANCELLED"}
        props = tool.Model.get_wall_props(obj)
        if not props.is_editing:
            self.report({"WARNING"}, "Cycle wall offset only works in wall edit mode.")
            return {"CANCELLED"}
        current = props.desired_offset_baseline
        idx = self._ORDER.index(current) if current in self._ORDER else 0
        direction = -1 if self.reverse else 1
        props.desired_offset_baseline = self._ORDER[(idx + direction) % len(self._ORDER)]
        return {"FINISHED"}


class GizmoWallEdition(bpy.types.GizmoGroup, gizmo.BaseParametricGizmoGroup):
    bl_idname = "OBJECT_GGT_bim_wall_edition"
    bl_label = "Wall Editing Gizmo"
    bl_space_type = "VIEW_3D"
    bl_region_type = "WINDOW"
    bl_options = {"3D", "PERSISTENT"}

    enable_editing_operator = "bim.enable_editing_wall"
    finish_editing_operator = "bim.finish_editing_wall"
    cancel_editing_operator = "bim.cancel_editing_wall"
    # Empty disables the base class's auto-created cycle_gizmo at ICON_CYCLE_X.
    # We render three state-specific baseline icons at that slot instead — see
    # ``setup_element_specific_gizmos`` / ``_update_icon_row_extras``.
    cycle_type_operator = ""

    # Threshold (SI meters) above which a second height gizmo is drawn at the far end of
    # the wall so the user doesn't have to pan across long walls to reach a height handle.
    LONG_WALL_THRESHOLD = 5.0

    dimension_gizmo_props = [
        # length / height / height_end positions are recomputed per frame in
        # ``_update_dimension_gizmo_positions`` so they flip to the camera-facing
        # side of the wall as the viewport is orbited. No static ``matrix_position``
        # here means the base class falls back to Identity, which the override
        # then replaces with the view-dependent coordinates.
        DimensionGizmoConfig(
            attr_name="length",
            axis=(1, 0, 0),
            min_value=0.01,
            text_offset_sign=-1,
        ),
        DimensionGizmoConfig(
            attr_name="height",
            axis=(0, 0, 1),
            min_value=0.01,
        ),
        # Second height gizmo at the far end of long walls. Distinct attr_name so it
        # doesn't collide with the first height gizmo in self.dimension_*_gizmo storage;
        # compute/apply tunnel through to the same props.height.
        DimensionGizmoConfig(
            attr_name="height_end",
            axis=(0, 0, 1),
            min_value=0.01,
            # default-arg captures the class const because lambda body can't see class scope.
            visibility_condition=lambda p, _t=LONG_WALL_THRESHOLD: p.length > _t,
            compute_value=lambda p: p.height,
            apply_value=lambda p, v: setattr(p, "height", max(0.01, v)),
            color="BLUE",
        ),
        # Slope: a Y-axis dimension at the top edge measuring horizontal displacement
        # of the top face. compute/apply translate between displacement (what the user
        # sees & drags) and x_angle (what's stored). Drag toward +Y → positive slope.
        DimensionGizmoConfig(
            attr_name="x_angle",
            axis=(0, 1, 0),
            prop_name="Slope",
            matrix_position=lambda p: Vector((p.anchor_x + p.length / 2, p.offset + p.thickness / 2, p.height)),
            compute_value=lambda p: core.displacement_from_x_angle(p.height, p.x_angle),
            apply_value=lambda p, displacement: setattr(
                p, "x_angle", core.x_angle_from_displacement(p.height, displacement)
            ),
            color="GREEN",
            min_value=-1e6,  # apply_value clamps via atan2; allow negative displacement
            text_formatter=lambda p, displacement: (
                f"{'-' if displacement < 0 else ''}{tool.Unit.format_distance(abs(displacement))} "
                f"({math.degrees(p.x_angle):.1f}°)"
            ),
        ),
    ]

    props_getter = "get_wall_props"
    gizmo_pref_name = "wall"

    @classmethod
    def is_element_type(cls, element: ifcopenshell.entity_instance) -> bool:
        return tool.Blender.Modifier.is_wall(element)

    def get_icon_y_extent(self, props: "BIMWallProperties") -> tuple[float, float]:
        far = props.offset + props.thickness + 2 * self.GIZMO_OFFSET
        near = -props.offset + 2 * self.GIZMO_OFFSET
        return (far, near)

    def _update_dimension_gizmo_positions(
        self, context: bpy.types.Context, mw: Matrix, props: "BIMWallProperties"  # noqa: ARG002
    ) -> None:
        """Re-position length / height / height_end dimensions to the camera-facing
        Y-side of the wall every frame. Mirrors the door & stair pattern: when the
        viewport is orbited past the wall, the handles jump to the visible face
        instead of being stranded behind it.

        - When viewing from -Y: place handles at wall-local Y = ``offset - GIZMO_OFFSET``.
        - When viewing from +Y: place handles at wall-local Y = ``offset + thickness + GIZMO_OFFSET``.

        Slope (``x_angle``) is intentionally NOT view-flipped — it lives at the wall
        axis centerline because the gizmo IS the Y-displacement indicator. Flipping
        it would invert the drag direction relative to the user's pointer motion."""
        viewing_from_neg_y, _ = self._frame_view_dir
        y_camera_side = self.get_camera_facing_outer_y(
            viewing_from_neg_y,
            props.offset,
            props.offset + props.thickness,
            self.GIZMO_OFFSET,
        )
        # Length: along X axis at half-height, on the camera-facing edge.
        self.set_dimension_gizmo_position(
            "length",
            mw,
            Vector((props.anchor_x, y_camera_side, props.height / 2)),
            (1, 0, 0),
        )
        # Height (start of wall): along Z, at the start endpoint, camera-facing side.
        self.set_dimension_gizmo_position(
            "height",
            mw,
            Vector((props.anchor_x, y_camera_side, 0)),
            (0, 0, 1),
        )
        # Height (far end of long walls): along Z, at the end endpoint, camera-facing side.
        self.set_dimension_gizmo_position(
            "height_end",
            mw,
            Vector((props.anchor_x + props.length, y_camera_side, 0)),
            (0, 0, 1),
        )

    # X offsets in the editing icon row, additive from ICON_VALIDATE_X (0.0).
    # Matches the cadence used by the base class (0.0 / 0.5 / 0.87 = step ≈ 0.37).
    # The baseline icons (EXT / CEN / INT) all share ICON_CYCLE_X — only one is
    # ever visible at a time so they don't overlap.
    ICON_ROTATE_X = 1.24

    # Mapping from BIMWallProperties.desired_offset_baseline value to the
    # attribute on `self` that holds the corresponding state icon.
    _BASELINE_GIZMO_ATTRS: ClassVar[dict[str, str]] = {
        "EXTERIOR": "offset_exterior_gizmo",
        "CENTER": "offset_center_gizmo",
        "INTERIOR": "offset_interior_gizmo",
    }

    def setup_element_specific_gizmos(self, context: bpy.types.Context) -> None:
        """Wall-specific gizmos.

        Cursor-anchored (always visible during edit mode, conditional position):

        - ``split_gizmo`` — at the 3D cursor's exact world position when cursor is
          within the wall's X range. Clicking splits the wall there.
        - ``extend_x_gizmo`` — at the wall-local X of the cursor, projected to the
          floor plane (Z=0 in wall-local). Clicking extends/trims the wall's length.
        - ``extend_z_gizmo`` — at the wall-local X of the cursor, projected to the
          wall top (Z=height in wall-local). Clicking extends the wall's height to
          the cursor's Z.

        Icon-row (always visible during edit mode, fixed position):

        - ``offset_{exterior,center,interior}_gizmo`` — three state-specific icons,
          only one visible at a time. Reflects ``props.desired_offset_baseline``.
          Clicking any of them cycles the baseline (the operator is the same).
        - ``rotate_gizmo`` — rotates the wall 90° around Z (Shift+R). Uses the
          revolving-arrows icon now that the cycle slot is occupied by the
          stateful baseline icons.
        - ``toggle_openings_gizmo`` — toggles opening fill visibility (Alt+O).
        """
        default_color, highlight_color = self.get_decoration_colors()
        self.split_gizmo = self._setup_icon_gizmo(
            "VIEW3D_GT_split",
            default_color,
            "bim.split_wall_at_cursor",
            highlight_color,
        )
        self.extend_x_gizmo = self._setup_icon_gizmo(
            "VIEW3D_GT_extend",
            default_color,
            "bim.extend_wall_to_cursor",
            highlight_color,
        )
        self.extend_z_gizmo = self._setup_icon_gizmo(
            "VIEW3D_GT_extend_vertical",
            default_color,
            "bim.extend_wall_height_to_cursor",
            highlight_color,
        )
        # Three baseline-state icons — only one is visible at a time, picked by
        # the current props.desired_offset_baseline. All point to the same cycle
        # operator so clicking any of them advances the cycle.
        for baseline, attr_name in self._BASELINE_GIZMO_ATTRS.items():
            setattr(
                self,
                attr_name,
                self._setup_icon_gizmo(
                    f"VIEW3D_GT_offset_{baseline.lower()}",
                    default_color,
                    "bim.cycle_wall_offset",
                    highlight_color,
                ),
            )
        self.rotate_gizmo = self._setup_icon_gizmo(
            "VIEW3D_GT_cycle",
            default_color,
            "bim.rotate_wall_90",
            highlight_color,
        )
        self.toggle_openings_gizmo = self._setup_icon_gizmo(
            "VIEW3D_GT_add_opening",
            default_color,
            "bim.toggle_wall_openings",
            highlight_color,
        )

    def _refresh_element_specific(self, context: bpy.types.Context, mw: Matrix, props: "BIMWallProperties") -> None:
        """Position cursor-anchored gizmos and the wall-specific icon-row extras."""
        self._update_cursor_gizmos(context, mw, props)
        self._update_icon_row_extras(context, mw, props)

    # World-Z spacing between stacked cursor icons. ~0.3m is ~1.5× icon diameter
    # at default scale, leaving a small visual gap between consecutive icons.
    CURSOR_STACK_OFFSET = 0.3

    def _update_cursor_gizmos(self, context: bpy.types.Context, mw: Matrix, props: "BIMWallProperties") -> None:
        """Position the cursor-anchored icons (extend-X / extend-Z / split) on the wall
        axis at the cursor's projected X, each at the Z its action would land at.

        When two icons want the same Z (within ``CURSOR_STACK_OFFSET``), bump the
        lower-priority one upward so both stay clickable. Priority low → high:
        extend-X, extend-Z, split. Bumps cascade — bumping extend-Z up can in turn
        collide with split, so extend-Z gets bumped further to clear it."""
        if not hasattr(self, "split_gizmo"):
            return
        gizmo_prefs = self.get_gizmo_prefs()
        all_gizmos = (self.extend_x_gizmo, self.extend_z_gizmo, self.split_gizmo)
        if not props.is_editing:
            for gz in all_gizmos:
                gz.hide = True
            return
        cursor_world = context.scene.cursor.location
        cursor_local = mw.inverted() @ cursor_world
        in_range = props.anchor_x < cursor_local.x < props.anchor_x + props.length
        billboard_rot = self._frame_billboard_rot

        # Candidates ordered by priority (lowest first). Each is (gizmo, local_z).
        # The local X and Y are common: at the cursor's projected X on the axis.
        # Only "active" gizmos (enabled + applicable) participate in placement.
        candidates: list[tuple[bpy.types.Gizmo, float]] = []
        if gizmo_prefs.extend:
            candidates.append((self.extend_x_gizmo, 0.0))
        if gizmo_prefs.extend_height:
            candidates.append((self.extend_z_gizmo, cursor_local.z))
        if in_range and gizmo_prefs.scissors:
            candidates.append((self.split_gizmo, props.height))

        # Resolve collisions: walk in priority order and ensure each gizmo's
        # final Z is at least CURSOR_STACK_OFFSET above the previous one (when
        # the previous one's final Z is higher).
        resolved: list[tuple[bpy.types.Gizmo, float]] = []
        for gz, desired_z in candidates:
            final_z = desired_z
            for _, prev_z in resolved:
                if abs(final_z - prev_z) < self.CURSOR_STACK_OFFSET:
                    # Bump up to clear the previous gizmo's slot.
                    final_z = prev_z + self.CURSOR_STACK_OFFSET
            resolved.append((gz, final_z))

        for gz in all_gizmos:
            gz.hide = True
        for gz, local_z in resolved:
            gz.hide = self.is_gizmo_hidden_by_modal(gz)
            world_pos = mw @ Vector((cursor_local.x, 0.0, local_z))
            gz.matrix_basis = gizmo.billboarded_at(world_pos, billboard_rot)

    def _update_icon_row_extras(self, context: bpy.types.Context, mw: Matrix, props: "BIMWallProperties") -> None:
        """Position the wall-specific icons in the icon row.

        Edit-mode icons (visible only when ``props.is_editing``):

        - Three baseline icons (Exterior / Centreline / Interior) share the cycle
          slot — only the one matching ``props.desired_offset_baseline`` shows.
        - Rotate-90 icon at ``ICON_ROTATE_X``.

        Non-edit-mode icons (visible alongside the pen icon, hidden during edit):

        - Toggle-openings icon next to the pen. Lives outside edit mode because
          opening visibility is a viewport-display concern, not a wall-edit action.

        Calls ``billboarded_at`` directly rather than routing through
        ``set_icon_gizmo_position`` because the icon row has wall-specific
        visibility/state branching (baseline-indicator selection, edit-mode
        toggle for opening-visibility) that the helper does not model."""
        if not hasattr(self, "rotate_gizmo"):
            return
        gizmo_prefs = self.get_gizmo_prefs()
        icon_z = self.get_element_height(props) + self.ICON_Z_OFFSET
        icon_y = self.get_icon_y_offset(context, mw)
        billboard_rot = self._frame_billboard_rot

        # --- Edit-mode icons (baseline indicator + rotate-90) ---
        if props.is_editing:
            # Stateful baseline indicator at the cycle slot. Show exactly one of the
            # three icons (the one matching the current baseline), hide the others.
            for baseline, attr in self._BASELINE_GIZMO_ATTRS.items():
                gz = getattr(self, attr)
                if gizmo_prefs.cycle and baseline == props.desired_offset_baseline:
                    gz.hide = self.is_gizmo_hidden_by_modal(gz)
                    world_pos = mw @ Vector((self.ICON_VALIDATE_X + self.ICON_CYCLE_X, icon_y, icon_z))
                    gz.matrix_basis = gizmo.billboarded_at(world_pos, billboard_rot)
                else:
                    gz.hide = True
            if gizmo_prefs.rotate:
                self.rotate_gizmo.hide = self.is_gizmo_hidden_by_modal(self.rotate_gizmo)
                world_pos = mw @ Vector((self.ICON_VALIDATE_X + self.ICON_ROTATE_X, icon_y, icon_z))
                # VIEW3D_GT_cycle is authored for the base class's 0.30 scale; at 0.5
                # it looks roughly 2x too big next to the validate / cancel icons.
                self.rotate_gizmo.matrix_basis = gizmo.billboarded_at(world_pos, billboard_rot, scale=0.30)
            else:
                self.rotate_gizmo.hide = True
        else:
            for attr in self._BASELINE_GIZMO_ATTRS.values():
                getattr(self, attr).hide = True
            self.rotate_gizmo.hide = True

        # --- Non-edit-mode icons (toggle openings) ---
        # Sits at the slot the cancel icon occupies during editing — that way the
        # pen + openings pair is compact and visually grouped.
        if not props.is_editing and gizmo_prefs.toggle_openings:
            self.toggle_openings_gizmo.hide = self.is_gizmo_hidden_by_modal(self.toggle_openings_gizmo)
            world_pos = mw @ Vector((self.ICON_VALIDATE_X + self.ICON_CANCEL_X, icon_y, icon_z))
            self.toggle_openings_gizmo.matrix_basis = gizmo.billboarded_at(world_pos, billboard_rot)
        else:
            self.toggle_openings_gizmo.hide = True


def _commit_active_wall_edit_if_any(context: bpy.types.Context) -> bpy.types.Object | None:
    """Return the active object, committing any in-progress wall edit first.

    Used by the scissors/extend gizmo operators: clicking either icon implicitly
    validates the current edit (✓ semantics) before running the follow-up action.
    Returns None when there's no active object — callers should treat that as CANCELLED."""
    obj = context.active_object
    if not obj:
        return None
    props = tool.Model.get_wall_props(obj)
    if props.is_editing:
        bpy.ops.bim.finish_editing_wall()
    return obj


def _commit_pending_wall_edits_for_selection(context: bpy.types.Context) -> None:  # noqa: ARG001
    """Thin wall-scoped alias for `tool.Parametric.commit_pending_edits_for_selection`.

    Kept as a named helper because every multi-wall operator (split / join / merge /
    unjoin / extend-to-wall …) calls it at the top of ``_execute``; centralising the
    ``names=("wall",)`` filter here means the registry name is touched in one place."""
    tool.Parametric.commit_pending_edits_for_selection(names=("wall",))


class SplitWallAtCursor(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.split_wall_at_cursor"
    bl_label = "Split Wall at Cursor"
    bl_description = "Split wall at 3D cursor location"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if not tool.Model.has_selected_ifc_objects():
            cls.poll_message_set("No IFC objects selected.")
            return False
        return True

    def _execute(self, context: bpy.types.Context) -> set[str]:
        # Applies any pending wall edit first so the split operates on the committed
        # geometry rather than the draft preview box.
        if _commit_active_wall_edit_if_any(context) is None:
            return {"CANCELLED"}
        bpy.ops.bim.split_wall()
        return {"FINISHED"}


class ExtendWallToCursor(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.extend_wall_to_cursor"
    bl_label = "Extend Wall to Cursor"
    bl_description = "Extend wall length to 3D cursor location"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if not tool.Model.has_selected_ifc_objects():
            cls.poll_message_set("No IFC objects selected.")
            return False
        return True

    def _execute(self, context: bpy.types.Context) -> set[str]:
        if _commit_active_wall_edit_if_any(context) is None:
            return {"CANCELLED"}
        core.extend_walls(
            tool.Ifc,
            tool.Blender,
            tool.Geometry,
            DumbWallJoiner(),
            tool.Model,
            context.scene.cursor.location,
        )
        return {"FINISHED"}


class ExtendWallHeightToCursor(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.extend_wall_height_to_cursor"
    bl_label = "Extend Wall Height to Cursor Z"
    bl_description = "Extend wall height to 3D cursor Z location"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if not tool.Model.has_selected_ifc_objects():
            cls.poll_message_set("No IFC objects selected.")
            return False
        return True

    def _execute(self, context: bpy.types.Context) -> set[str]:
        obj = _commit_active_wall_edit_if_any(context)
        if obj is None:
            return {"CANCELLED"}
        cursor_z = context.scene.cursor.location.z
        base_z = obj.matrix_world.translation.z
        new_height = cursor_z - base_z
        if new_height <= 0:
            self.report(
                {"WARNING"},
                f"Cursor Z ({cursor_z:.2f}m) must be above wall base ({base_z:.2f}m).",
            )
            return {"CANCELLED"}
        with bpy.context.temp_override(active_object=obj, selected_objects=[obj]):
            bpy.ops.bim.change_extrusion_depth(depth=new_height)
        return {"FINISHED"}


class RotateWall90(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.rotate_wall_90"
    bl_label = "Rotate Wall 90°"
    bl_description = "Rotate wall 90° around Z axis"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if not tool.Model.has_selected_ifc_objects():
            cls.poll_message_set("No IFC objects selected.")
            return False
        return True

    def _execute(self, context: bpy.types.Context) -> set[str]:
        obj = _commit_active_wall_edit_if_any(context)
        if obj is None:
            return {"CANCELLED"}
        with bpy.context.temp_override(active_object=obj, selected_objects=[obj]):
            bpy.ops.bim.rotate_90(axis="Z")
        return {"FINISHED"}


class ToggleWallOpenings(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.toggle_wall_openings"
    bl_label = "Toggle Openings"
    bl_description = "Show or hide opening fills (doors and windows) in the viewport"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if not tool.Model.has_selected_ifc_objects():
            cls.poll_message_set("No IFC objects selected.")
            return False
        return True

    def _execute(self, context: bpy.types.Context) -> set[str]:
        # Opening visibility is independent of wall geometry — don't commit the
        # active wall edit; the user can keep editing the wall.
        if tool.Model.get_model_props().openings:
            bpy.ops.bim.edit_openings(apply_all=True)
        else:
            bpy.ops.bim.show_openings()
        return {"FINISHED"}


def _read_wall_geometry(obj: bpy.types.Object) -> dict | None:
    """Live-read wall geometry from IFC. Returns ``None`` if the wall is not a LAYER2 extruded wall."""
    element = tool.Ifc.get_entity(obj)
    if not element or not tool.Blender.Modifier.is_wall(element):
        return None
    representation = ifcopenshell.util.representation.get_representation(element, "Model", "Body", "MODEL_VIEW")
    if not representation:
        return None
    extrusion = tool.Model.get_extrusion(representation)
    if not extrusion:
        return None
    unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
    p1, p2 = ifcopenshell.util.representation.get_reference_line(element)
    layer_params = tool.Model.get_material_layer_parameters(element)
    x_angle = tool.Model.get_existing_x_angle(extrusion)
    return {
        "anchor_x": p1[0] * unit_scale,
        "length": (p2[0] - p1[0]) * unit_scale,
        "height": core.vertical_height_from_extrusion_depth(extrusion.Depth * unit_scale, x_angle),
        "x_angle": x_angle,
        "thickness": layer_params["thickness"],
        "offset": layer_params["offset"],
    }


def _wall_axis_world_segment_from_geom(obj: bpy.types.Object, geom: dict) -> tuple[Vector, Vector]:
    """Compose the world-space axis segment from an already-read ``geom`` dict.
    Used by the billboarding gizmo groups so a single cached IFC read drives both
    ``_read_wall_geometry`` *and* the segment, avoiding two reads per wall per frame."""
    p1_local = Vector((geom["anchor_x"], 0.0, 0.0))
    p2_local = Vector((geom["anchor_x"] + geom["length"], 0.0, 0.0))
    return obj.matrix_world @ p1_local, obj.matrix_world @ p2_local


class _WallGeomCachedBillboardingMixin(gizmo.BillboardingGizmoGroupMixin):
    """Adds IFC-read caching to `BillboardingGizmoGroupMixin` for wall-driven
    gizmo groups. ``refresh()`` is Blender's "something state-relevant changed"
    signal — that's when we drop the cache. ``draw_prepare()`` (every redraw) reuses
    whatever ``_get_wall_geom_cached`` populated, so plain camera orbits don't re-hit
    IFC. ``_get_wall_geom_cached`` also drops entries on its own when
    `tool.Parametric.get_geom_generation` advances (any ``tool.Ifc.Operator``
    commit) so external ``bpy.ops`` mutations on the same selection don't leave
    stale geometry behind."""

    def refresh(self, context: bpy.types.Context) -> None:
        self._wall_geom_cache = None
        self.position_gizmos(context)


def _get_wall_geom_cached(group: "bpy.types.GizmoGroup", obj: bpy.types.Object) -> dict | None:
    """Per-gizmo-group memoised ``_read_wall_geometry``. Without this, a
    billboarding gizmo group re-runs the IFC read on every camera orbit frame —
    ~120 IFC queries per second per wall, which is unwieldy on dense models.

    Two invalidation paths:

    - ``GizmoGroup.refresh()`` (Blender's state-change hook — selection,
      gizmo modal exit, …) clears ``_wall_geom_cache`` directly.
    - ``tool.Parametric.refresh_post_commit()`` bumps a generation counter on
      every IFC operator commit; the cache stores the generation it was filled
      at and drops on mismatch. This catches ``bpy.ops.bim.*`` mutations that
      edit the wall while the same selection is held (the case Blender's
      ``refresh()`` doesn't fire on)."""
    current_gen = tool.Parametric.get_geom_generation()
    cache_gen = getattr(group, "_wall_geom_cache_gen", None)
    cache = getattr(group, "_wall_geom_cache", None)
    if cache is None or cache_gen != current_gen:
        cache = {}
        group._wall_geom_cache = cache
        group._wall_geom_cache_gen = current_gen
    key = obj.name
    if key not in cache:
        cache[key] = _read_wall_geometry(obj)
    return cache[key]


def _wall_camera_facing_icon_y(context: bpy.types.Context, mw: Matrix, geom: dict) -> float:
    """Wall-local Y for an icon that should sit just outside the camera-facing face.
    Centralised so the billboarding wall gizmos (add-opening, extend-vertically, …)
    share one source of truth for "where does the icon go on the visible side"."""
    viewing_from_negative_y, _ = gizmo.BaseParametricGizmoGroup.get_local_view_direction(context, mw)
    return gizmo.BaseParametricGizmoGroup.get_camera_facing_outer_y(
        viewing_from_negative_y,
        geom["offset"],
        geom["offset"] + geom["thickness"],
        gizmo.BaseParametricGizmoGroup.GIZMO_OFFSET,
    )


def _are_walls_joined(elem_a: ifcopenshell.entity_instance, elem_b: ifcopenshell.entity_instance) -> bool:
    """True if there's an ``IfcRelConnectsPathElements`` relating these two walls.

    Bonsai's wall joiner creates ``IfcRelConnectsPathElements`` (a specialization of
    ``IfcRelConnectsElements``) whenever walls share a corner or mitre. We walk both
    inverse arrays of the first wall and look for the second wall on the other side
    of any path-element rel."""
    for rel in getattr(elem_a, "ConnectedTo", []):
        if rel.is_a("IfcRelConnectsPathElements") and rel.RelatedElement == elem_b:
            return True
    for rel in getattr(elem_a, "ConnectedFrom", []):
        if rel.is_a("IfcRelConnectsPathElements") and rel.RelatingElement == elem_b:
            return True
    return False


def _are_walls_collinear(
    seg_a: tuple[Vector, Vector],
    seg_b: tuple[Vector, Vector],
    parallel_threshold: float = 0.9994,
    line_tolerance: float = 0.05,
) -> bool:
    """Vector wrapper around `core.are_axes_collinear` — converts Vector
    endpoints to plain tuples at the boundary so the math stays unit-testable in
    ``test/core/`` without a mathutils dependency."""
    return core.are_axes_collinear(
        (tuple(seg_a[0]), tuple(seg_a[1])),
        (tuple(seg_b[0]), tuple(seg_b[1])),
        parallel_threshold,
        line_tolerance,
    )


def _collinear_boundary_world(seg_a: tuple[Vector, Vector], seg_b: tuple[Vector, Vector]) -> Vector:
    """Vector wrapper around `core.closest_endpoint_midpoint`."""
    return Vector(
        core.closest_endpoint_midpoint(
            (tuple(seg_a[0]), tuple(seg_a[1])),
            (tuple(seg_b[0]), tuple(seg_b[1])),
        )
    )


class GizmoWallAddOpening(bpy.types.GizmoGroup, _WallGeomCachedBillboardingMixin):
    """Activates when a wall (active) and one non-wall blender object are co-selected.

    Renders a single icon above the wall at the wall-local X corresponding to the other
    object's projected origin. Clicking dispatches `bim.add_opening`, which lets the
    existing FilledOpeningGenerator decide how the opening is applied.

    Per-frame positioning via `BillboardingGizmoGroupMixin` ensures the icon
    keeps facing the camera as the viewport is orbited."""

    bl_idname = "OBJECT_GGT_bim_wall_add_opening"
    bl_label = "Wall Add Opening Gizmo"
    bl_space_type = "VIEW_3D"
    bl_region_type = "WINDOW"
    bl_options = {"3D", "PERSISTENT"}

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        prefs = tool.Blender.get_addon_preferences()
        if not prefs.gizmos.draw_gizmos_in_3d_viewport:
            return False
        selected = tool.Blender.get_selected_objects()
        if len(selected) != 2:
            return False
        active = context.active_object
        if active is None or active not in selected:
            return False
        element = tool.Ifc.get_entity(active)
        if not element or not tool.Blender.Modifier.is_wall(element):
            return False
        other = next(o for o in selected if o is not active)
        # If the other object is also a wall, the wall-join gizmo handles it instead.
        other_element = tool.Ifc.get_entity(other)
        if other_element and tool.Blender.Modifier.is_wall(other_element):
            return False
        return True

    def setup(self, context: bpy.types.Context) -> None:
        prefs = tool.Blender.get_addon_preferences()
        default_color = prefs.decorations_colour[:3]
        highlight_color = prefs.decorator_color_selected[:3]
        self.add_opening_icon = self.setup_icon_gizmo(
            "VIEW3D_GT_add_opening", default_color, highlight_color, "bim.add_opening"
        )

    def position_gizmos(self, context: bpy.types.Context) -> None:
        wall_obj = context.active_object
        if not wall_obj:
            return
        selected = tool.Blender.get_selected_objects()
        other = next((o for o in selected if o is not wall_obj), None)
        if not other:
            return
        geom = _get_wall_geom_cached(self, wall_obj)
        if not geom:
            return
        mw = wall_obj.matrix_world
        wall_local = mw.inverted() @ other.matrix_world.translation
        local_x = max(geom["anchor_x"], min(wall_local.x, geom["anchor_x"] + geom["length"]))
        # Place the icon on the camera-facing side of the wall, like the pen icon
        # does for parametric edits — orbit the camera past the wall and the icon
        # jumps to the visible face instead of being stranded behind it.
        icon_y = _wall_camera_facing_icon_y(context, mw, geom)
        icon_z = geom["height"] + gizmo.BaseParametricGizmoGroup.ICON_Z_OFFSET
        world_pos = mw @ Vector((local_x, icon_y, icon_z))
        self.add_opening_icon.matrix_basis = gizmo.billboarded_at(world_pos, gizmo.get_billboard_rotation(context))


class GizmoWallExtendVertically(bpy.types.GizmoGroup, _WallGeomCachedBillboardingMixin):
    """Activates when a LAYER3 element (typically a slab) is active and a LAYER2
    wall is co-selected. Mirrors the N-panel ``Extend To Underside`` button (which
    shows under the same active-LAYER3 + LAYER2-in-selection rule). Clicking
    dispatches ``bim.extend_walls_to_underside``, which extends the wall up to the
    active element's bottom faces.

    Anchored at the wall's local X = 0 (wall origin endpoint), wall-local Y on the
    camera-facing side, and the world Z of the active object — so the icon visually
    sits at the elevation the wall will reach after extending."""

    bl_idname = "OBJECT_GGT_bim_wall_extend_vertically"
    bl_label = "Wall Extend Vertically Gizmo"
    bl_space_type = "VIEW_3D"
    bl_region_type = "WINDOW"
    bl_options = {"3D", "PERSISTENT"}

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        prefs = tool.Blender.get_addon_preferences()
        if not prefs.gizmos.draw_gizmos_in_3d_viewport:
            return False
        selected = tool.Blender.get_selected_objects()
        if len(selected) != 2:
            return False
        active = context.active_object
        if active is None or active not in selected:
            return False
        active_element = tool.Ifc.get_entity(active)
        if not active_element or tool.Model.get_usage_type(active_element) != "LAYER3":
            return False
        other = next(o for o in selected if o is not active)
        other_element = tool.Ifc.get_entity(other)
        if not other_element or tool.Model.get_usage_type(other_element) != "LAYER2":
            return False
        return True

    def setup(self, context: bpy.types.Context) -> None:
        prefs = tool.Blender.get_addon_preferences()
        default_color = prefs.decorations_colour[:3]
        highlight_color = prefs.decorator_color_selected[:3]
        self.extend_vertical_icon = self.setup_icon_gizmo(
            "VIEW3D_GT_extend_vertical",
            default_color,
            highlight_color,
            "bim.extend_walls_to_underside",
        )

    def position_gizmos(self, context: bpy.types.Context) -> None:
        active = context.active_object
        if active is None:
            return
        wall_obj = next((o for o in tool.Blender.get_selected_objects() if o is not active), None)
        if wall_obj is None:
            return
        geom = _get_wall_geom_cached(self, wall_obj)
        if not geom:
            return
        mw = wall_obj.matrix_world
        icon_y = _wall_camera_facing_icon_y(context, mw, geom)
        # X = 0 in wall-local, Y on the camera-facing outer side, world Z lifted to
        # the active object's elevation — the height the wall is about to reach.
        world_pos = mw @ Vector((0.0, icon_y, 0.0))
        world_pos.z = active.matrix_world.translation.z
        self.extend_vertical_icon.matrix_basis = gizmo.billboarded_at(world_pos, gizmo.get_billboard_rotation(context))


class GizmoWallJoinIntersection(bpy.types.GizmoGroup, _WallGeomCachedBillboardingMixin):
    """Activates when exactly two LAYER2 walls are selected. Dispatches between four
    state-specific icons based on the geometric + IFC relationship of the walls:

    - **Joined** (``IfcRelConnectsPathElements`` between them):
      ``unjoin_icon`` (``VIEW3D_GT_split``, outward arrows) at the shared corner.
      Clicking dispatches ``bim.unjoin_walls``.
    - **Collinear** (axes on the same infinite line, not joined):
      ``merge_icon`` (``VIEW3D_GT_merge``, inward arrows) at the midpoint of the
      closest endpoint pair. Clicking dispatches ``bim.merge_wall``.
    - **Joinable corner** (non-parallel, axes meet near endpoints, not joined):
      ``join_icon`` (``VIEW3D_GT_merge``) at the projected intersection on the
      floor, PLUS ``extend_to_wall_icon`` (``VIEW3D_GT_extend``) at the
      intersection at the active wall's Z=height. The Z difference disambiguates
      "join the corner" vs "extend this wall into the other."
    - **None of the above**: all icons hidden.

    Per-frame positioning via `BillboardingGizmoGroupMixin` ensures the icons
    keep facing the camera as the viewport is orbited."""

    bl_idname = "OBJECT_GGT_bim_wall_join_intersection"
    bl_label = "Wall Join Intersection Gizmo"
    bl_space_type = "VIEW_3D"
    bl_region_type = "WINDOW"
    bl_options = {"3D", "PERSISTENT"}

    # Hide the gizmo when walls are nearly parallel (intersection would be unreasonably far).
    # cos(2°) ≈ 0.9994 → walls within ~2° of parallel are treated as parallel for this purpose.
    PARALLEL_DOT_THRESHOLD = 0.9994
    # The intersection must be within this many *wall-lengths* of the NEAREST endpoint
    # of each wall. This filters out the case where two walls are offset from world
    # origin and their extrapolated axes happen to cross at a point that isn't near
    # either wall's actual endpoints (which previously caused the icon to land at
    # world origin for walls whose axes coincidentally converged there).
    MAX_DISTANCE_TO_ENDPOINT_FACTOR = 0.75
    # Perpendicular tolerance (m) for treating two parallel wall axes as collinear.
    COLLINEAR_LINE_TOLERANCE = 0.05

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        prefs = tool.Blender.get_addon_preferences()
        if not prefs.gizmos.draw_gizmos_in_3d_viewport:
            return False
        selected = tool.Blender.get_selected_objects()
        if len(selected) != 2:
            return False
        for o in selected:
            element = tool.Ifc.get_entity(o)
            if not element or not tool.Blender.Modifier.is_wall(element):
                return False
        return True

    def setup(self, context: bpy.types.Context) -> None:
        prefs = tool.Blender.get_addon_preferences()
        default_color = prefs.decorations_colour[:3]
        highlight_color = prefs.decorator_color_selected[:3]
        self.unjoin_icon = self.setup_icon_gizmo("VIEW3D_GT_split", default_color, highlight_color, "bim.unjoin_walls")
        self.merge_icon = self.setup_icon_gizmo("VIEW3D_GT_merge", default_color, highlight_color, "bim.merge_wall")
        self.join_icon = self.setup_icon_gizmo(
            "VIEW3D_GT_merge", default_color, highlight_color, "bim.join_walls_intersection"
        )
        self.extend_to_wall_icon = self.setup_icon_gizmo(
            "VIEW3D_GT_extend", default_color, highlight_color, "bim.extend_walls_to_wall"
        )

    def _all_icons(self) -> tuple[bpy.types.Gizmo, ...]:
        return (self.unjoin_icon, self.merge_icon, self.join_icon, self.extend_to_wall_icon)

    def _hide_all(self) -> None:
        for icon in self._all_icons():
            icon.hide = True

    def position_gizmos(self, context: bpy.types.Context) -> None:
        selected = list(tool.Blender.get_selected_objects())
        if len(selected) != 2:
            self._hide_all()
            return
        elem_a = tool.Ifc.get_entity(selected[0])
        elem_b = tool.Ifc.get_entity(selected[1])
        geom_a = _get_wall_geom_cached(self, selected[0])
        geom_b = _get_wall_geom_cached(self, selected[1])
        if elem_a is None or elem_b is None or geom_a is None or geom_b is None:
            self._hide_all()
            return
        seg_a = _wall_axis_world_segment_from_geom(selected[0], geom_a)
        seg_b = _wall_axis_world_segment_from_geom(selected[1], geom_b)
        billboard_rot = gizmo.get_billboard_rotation(context)

        # State 1: walls are already joined → show Unjoin only, at the shared
        # corner's floor Z (no visibility lift — user expects the icon to sit
        # exactly at the corner, not floating above it).
        if _are_walls_joined(elem_a, elem_b):
            corner = _collinear_boundary_world(seg_a, seg_b)
            self.unjoin_icon.matrix_basis = gizmo.billboarded_at(corner, billboard_rot)
            self.unjoin_icon.hide = False
            self.merge_icon.hide = True
            self.join_icon.hide = True
            self.extend_to_wall_icon.hide = True
            return

        # State 2: walls are collinear (parallel axes on the same line) → show Merge
        # at the boundary midpoint between them, at floor Z (no visibility lift).
        if _are_walls_collinear(seg_a, seg_b, self.PARALLEL_DOT_THRESHOLD, self.COLLINEAR_LINE_TOLERANCE):
            boundary = _collinear_boundary_world(seg_a, seg_b)
            self.merge_icon.matrix_basis = gizmo.billboarded_at(boundary, billboard_rot)
            self.merge_icon.hide = False
            self.unjoin_icon.hide = True
            self.join_icon.hide = True
            self.extend_to_wall_icon.hide = True
            return

        # State 3: non-parallel walls whose axes meet near each wall's endpoint
        # → show Join at the floor + Extend-to-Wall at the active wall's top.
        intersection_tuple = core.project_axis_intersection(
            (tuple(seg_a[0]), tuple(seg_a[1])),
            (tuple(seg_b[0]), tuple(seg_b[1])),
            self.PARALLEL_DOT_THRESHOLD,
        )
        if intersection_tuple is None:
            self._hide_all()
            return
        intersection = Vector(intersection_tuple)
        len_a = (seg_a[1] - seg_a[0]).length
        len_b = (seg_b[1] - seg_b[0]).length
        near_a = min((intersection - seg_a[0]).length, (intersection - seg_a[1]).length)
        near_b = min((intersection - seg_b[0]).length, (intersection - seg_b[1]).length)
        if (
            near_a > len_a * self.MAX_DISTANCE_TO_ENDPOINT_FACTOR
            or near_b > len_b * self.MAX_DISTANCE_TO_ENDPOINT_FACTOR
        ):
            self._hide_all()
            return

        # Join sits on the floor (lowest endpoint Z across both wall axes), exactly
        # where the corner meets the ground — no visibility lift.
        floor_z = min(seg_a[0].z, seg_a[1].z, seg_b[0].z, seg_b[1].z)
        join_world = Vector((intersection.x, intersection.y, floor_z))
        self.join_icon.matrix_basis = gizmo.billboarded_at(join_world, billboard_rot)
        self.join_icon.hide = False

        # Extend-to-Wall sits at the active wall's top, same XY as the join icon —
        # the Z gap is what differentiates "join at corner" from "extend into other".
        active = context.active_object if context.active_object in selected else None
        geom = _read_wall_geometry(active) if active else None
        if geom is None:
            self.extend_to_wall_icon.hide = True
        else:
            active_top_z = active.matrix_world.translation.z + geom["height"]
            extend_world = Vector((intersection.x, intersection.y, active_top_z))
            self.extend_to_wall_icon.matrix_basis = gizmo.billboarded_at(extend_world, billboard_rot)
            self.extend_to_wall_icon.hide = False

        self.unjoin_icon.hide = True
        self.merge_icon.hide = True


class JoinWallsIntersection(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.join_walls_intersection"
    bl_label = "Join Walls at Corner"
    bl_description = "Join two walls at their corner"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if not tool.Model.has_selected_ifc_objects():
            cls.poll_message_set("No IFC objects selected.")
            return False
        return True

    def _execute(self, context: bpy.types.Context) -> set[str]:
        _commit_pending_wall_edits_for_selection(context)
        try:
            core.join_walls_LV(tool.Ifc, tool.Blender, tool.Geometry, DumbWallJoiner(), tool.Model)
        except core.RequireTwoWallsError as e:
            self.report({"ERROR"}, str(e))
            return {"CANCELLED"}
        return {"FINISHED"}
