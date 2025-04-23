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
# pyright: reportUnnecessaryTypeIgnoreComment=error

import bpy
import copy
import math
import numpy as np
import ifcopenshell
import ifcopenshell.api
import ifcopenshell.api.geometry
import ifcopenshell.util.unit
import ifcopenshell.util.element
import ifcopenshell.util.placement
import ifcopenshell.util.representation
import ifcopenshell.util.shape_builder
import ifcopenshell.util.type
import mathutils.geometry
import bonsai.core.type
import bonsai.core.root
import bonsai.core.geometry
import bonsai.core.model as core
import bonsai.tool as tool
from bonsai.bim.ifc import IfcStore
from math import pi, sin, cos, degrees
from mathutils import Vector, Matrix
from bonsai.bim.module.model.opening import FilledOpeningGenerator
from bonsai.bim.module.model.decorator import PolylineDecorator, ProductDecorator
from bonsai.bim.module.model.polyline import PolylineOperator
from typing import Optional, assert_never, TYPE_CHECKING, get_args, Literal, Union, Any


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
        core.unjoin_walls(tool.Ifc, tool.Blender, tool.Geometry, DumbWallJoiner(), tool.Model)


class ExtendWallsToUnderside(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.extend_walls_to_underside"
    bl_label = "Extend Walls To Underside"
    bl_description = "Extend and clip selected walls at the bottom faces of an object"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
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


class AlignWall(bpy.types.Operator):
    bl_idname = "bim.align_wall"
    bl_label = "Align Wall"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = """ Align the selected walls to the active wall:
    'Ext.': align to the EXTERIOR face
    'C/L': align to wall CENTER
    'Int.': align to the INTERIOR face"""

    AlignType = Literal["CENTER", "EXTERIOR", "INTERIOR"]
    align_type: bpy.props.EnumProperty(  # type: ignore [reportRedeclaration]
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
                depth = extrusion.Depth / abs(1 / cos(existing_x_angle))
                perpendicular_depth = depth * abs(1 / cos(x_angle))
                print(extrusion.Depth, perpendicular_depth)
                extrusion.ExtrudedDirection.DirectionRatios = (0.0, sin(x_angle), cos(x_angle))
                layer2_objs.append(obj)
                extrusion.Depth = perpendicular_depth
            else:
                if tool.Model.get_usage_type(element) == "LAYER3":
                    existing_x_angle = obj.rotation_euler.x
                    existing_x_angle = 0 if tool.Cad.is_x(existing_x_angle, 0, tolerance=0.001) else existing_x_angle
                    existing_x_angle = 0 if tool.Cad.is_x(existing_x_angle, pi, tolerance=0.001) else existing_x_angle
                    # Reset the transformation and returns to the original points with 0 degrees
                    extrusion.SweptArea.OuterCurve.Points.CoordList = [
                        (p[0], p[1] * abs(cos(existing_x_angle)))
                        for p in extrusion.SweptArea.OuterCurve.Points.CoordList
                    ]

                    # Apply the transformation for the new x_angle
                    extrusion.SweptArea.OuterCurve.Points.CoordList = [
                        (p[0], p[1] * abs(1 / cos(x_angle))) for p in extrusion.SweptArea.OuterCurve.Points.CoordList
                    ]

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
                    should_reload=True,
                    is_global=True,
                    should_sync_changes_first=False,
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
            ifcopenshell.api.run("material.edit_layer_usage", model, usage=material_set_usage, attributes=attributes)
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
            ProductDecorator.uninstall()
            PolylineDecorator.uninstall()
            tool.Polyline.clear_polyline()
            tool.Blender.update_viewport()
            return {"FINISHED"}

        self.handle_keyboard_input(context, event)

        self.handle_inserting_polyline(context, event)

        self.get_product_preview_data(context, self.relating_type)

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
        polyline_data = bpy.context.scene.BIMPolylineProperties.insertion_polyline
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
        polyline_points = extrusion.SweptArea.OuterCurve.Points.CoordList
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
            # Round to nearest 5 degrees
            nearest_degree = (math.pi / 180) * 5
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
        ifcopenshell.api.run("type.assign_type", self.file, related_objects=[element], relating_type=self.relating_type)
        if self.axis_context:
            representation = ifcopenshell.api.run(
                "geometry.add_axis_representation",
                tool.Ifc.get(),
                context=self.axis_context,
                axis=[(0.0, 0.0), (self.length, 0.0)],
            )
            ifcopenshell.api.run(
                "geometry.assign_representation", tool.Ifc.get(), product=element, representation=representation
            )
        bonsai.core.geometry.edit_object_placement(tool.Ifc, tool.Geometry, tool.Surveyor, obj=obj)
        representation = ifcopenshell.api.run(
            "geometry.add_wall_representation",
            tool.Ifc.get(),
            context=self.body_context,
            thickness=self.layers["thickness"],
            direction_sense=self.layers["direction_sense"],
            offset=self.layers["offset"],
            length=self.length,
            height=self.height,
            x_angle=self.x_angle,
        )
        ifcopenshell.api.run(
            "geometry.assign_representation", tool.Ifc.get(), product=element, representation=representation
        )
        bonsai.core.geometry.switch_representation(
            tool.Ifc,
            tool.Geometry,
            obj=obj,
            representation=representation,
            should_reload=True,
            is_global=True,
            should_sync_changes_first=False,
        )
        pset = ifcopenshell.api.run("pset.add_pset", self.file, product=element, name="EPset_Parametric")
        ifcopenshell.api.run("pset.edit_pset", self.file, pset=pset, properties={"Engine": "Bonsai.DumbLayer2"})
        material = ifcopenshell.util.element.get_material(element)
        material.LayerSetDirection = "AXIS2"
        tool.Blender.select_object(obj)
        return obj

    def get_relating_type_class(self, relating_type):
        classes = ifcopenshell.util.type.get_applicable_entities(relating_type.is_a(), tool.Ifc.get().schema)
        return [c for c in classes if "StandardCase" not in c][0]


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

    def regenerate_from_type(self, usecase_path, ifc_file, settings):
        relating_type = settings["relating_type"]

        new_material = ifcopenshell.util.element.get_material(relating_type)
        if not new_material or not new_material.is_a("IfcMaterialLayerSet"):
            return

        parametric = ifcopenshell.util.element.get_psets(relating_type).get("EPset_Parametric")
        layer_set_direction = None
        if parametric:
            layer_set_direction = parametric.get("LayerSetDirection", layer_set_direction)

        self.unit_scale = ifcopenshell.util.unit.calculate_unit_scale(ifc_file)
        for related_object in settings["related_objects"]:
            self._regenerate_from_type(related_object, layer_set_direction)

    def _regenerate_from_type(
        self, related_object: ifcopenshell.entity_instance, layer_set_direction: Optional[str]
    ) -> None:
        obj = tool.Ifc.get_object(related_object)
        if not obj or not tool.Geometry.get_active_representation(obj):
            return

        material = ifcopenshell.util.element.get_material(related_object)
        if not material or not material.is_a("IfcMaterialLayerSetUsage"):
            return
        if layer_set_direction:
            material.LayerSetDirection = layer_set_direction
        if material.LayerSetDirection == "AXIS2":
            tool.Model.recalculate_walls([obj])


class DumbWallJoiner:
    def __init__(self):
        self.unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        self.axis_context = ifcopenshell.util.representation.get_context(tool.Ifc.get(), "Plan", "Axis", "GRAPH_VIEW")
        self.body_context = ifcopenshell.util.representation.get_context(tool.Ifc.get(), "Model", "Body", "MODEL_VIEW")

    def unjoin(self, wall1):
        element1 = tool.Ifc.get_entity(wall1)
        if not element1:
            return

        ifcopenshell.api.run("geometry.disconnect_path", tool.Ifc.get(), element=element1, connection_type="ATSTART")
        ifcopenshell.api.run("geometry.disconnect_path", tool.Ifc.get(), element=element1, connection_type="ATEND")

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
            if conn.RelatingConnectionType == "ATEND":
                relating_element = conn.RelatedElement
                description = conn.Description
        connections = element1.ConnectedFrom
        for conn in connections:
            if conn.RelatedConnectionType == "ATEND":
                relating_element = conn.RelatingElement
                description = conn.Description

        if relating_element:
            ifcopenshell.api.run(
                "geometry.connect_path",
                tool.Ifc.get(),
                relating_element=relating_element,
                related_element=element2,
                relating_connection="ATSTART",
                related_connection="ATEND",
                description=description,
            )

        # During the duplication process, unfilled voids are copied, so we need
        # to check openings on both element1 and element2. Let's check element1
        # first.
        for opening in [
            r.RelatedOpeningElement for r in element1.HasOpenings if not r.RelatedOpeningElement.HasFillings
        ]:
            opening_matrix = Matrix(ifcopenshell.util.placement.get_local_placement(opening.ObjectPlacement).tolist())
            opening_matrix.translation *= unit_scale
            opening_location = opening_matrix.translation
            _, opening_position = mathutils.geometry.intersect_point_line(opening_location.to_2d(), *axis1["reference"])
            if opening_position > cut_percentage:
                # The opening should be removed from element1.
                ifcopenshell.api.run("feature.remove_feature", tool.Ifc.get(), feature=opening)

        # Now let's check element2.
        for opening in [
            r.RelatedOpeningElement for r in element2.HasOpenings if not r.RelatedOpeningElement.HasFillings
        ]:
            opening_matrix = Matrix(ifcopenshell.util.placement.get_local_placement(opening.ObjectPlacement).tolist())
            opening_matrix.translation *= unit_scale
            opening_location = opening_matrix.translation
            _, opening_position = mathutils.geometry.intersect_point_line(opening_location.to_2d(), *axis1["reference"])
            if opening_position < cut_percentage:
                # The opening should be removed from element2.
                ifcopenshell.api.run("feature.remove_feature", tool.Ifc.get(), feature=opening)

        # During the duplication process, filled voids are not copied. So we
        # only need to check fillings on the original element1.
        for opening in [r.RelatedOpeningElement for r in element1.HasOpenings if r.RelatedOpeningElement.HasFillings]:
            rel = opening.HasFillings[0]
            filling = rel.RelatedBuildingElement
            filling_obj = tool.Ifc.get_object(filling)
            filling_location = filling_obj.matrix_world.translation
            _, filling_position = mathutils.geometry.intersect_point_line(filling_location.to_2d(), *axis1["reference"])
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

                rel.RelatedBuildingElement = element2

                # Remove the old opening
                ifcopenshell.api.run("feature.remove_feature", tool.Ifc.get(), feature=opening)

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

        if not np.isclose(p1[1], p4[1]) or not np.isclose(p3[1], p4[1]):
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

    def join_Z(self, wall1, slab2):
        element1 = tool.Ifc.get_entity(wall1)
        element2 = tool.Ifc.get_entity(slab2)

        for rel in element1.ConnectedFrom:
            if rel.is_a() == "IfcRelConnectsElements" and rel.Description == "TOP":
                ifcopenshell.api.run(
                    "geometry.disconnect_element",
                    tool.Ifc.get(),
                    relating_element=rel.RelatingElement,
                    related_element=element1,
                )

        ifcopenshell.api.run(
            "geometry.connect_element",
            tool.Ifc.get(),
            relating_element=element2,
            related_element=element1,
            description="TOP",
        )

        tool.Model.recreate_wall(element1, wall1)

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

    def extend(self, wall1, target):
        if tool.Ifc.is_moved(wall1):
            bonsai.core.geometry.edit_object_placement(tool.Ifc, tool.Geometry, tool.Surveyor, obj=wall1)
        element1 = tool.Ifc.get_entity(wall1)
        p1, p2 = ifcopenshell.util.representation.get_reference_line(element1)
        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        target = (wall1.matrix_world.inverted() @ target).to_2d() / unit_scale
        intersect, connection = mathutils.geometry.intersect_point_line(target, p1, p2)
        connection = "ATEND" if connection > 0.5 else "ATSTART"

        ifcopenshell.api.run("geometry.disconnect_path", tool.Ifc.get(), element=element1, connection_type=connection)

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

    def join_T(self, wall1: bpy.types.Object, wall2: bpy.types.Object) -> None:
        element1 = tool.Ifc.get_entity(wall1)
        element2 = tool.Ifc.get_entity(wall2)
        axis1 = tool.Model.get_wall_axis(wall1)
        axis2 = tool.Model.get_wall_axis(wall2)
        intersect = tool.Cad.intersect_edges(axis1["reference"], axis2["reference"])
        if intersect:
            intersect, _ = intersect
        else:
            return
        connection = "ATEND" if tool.Cad.edge_percent(intersect, axis1["reference"]) > 0.5 else "ATSTART"

        ifcopenshell.api.geometry.connect_path(
            tool.Ifc.get(),
            related_element=element1,
            relating_element=element2,
            relating_connection="ATPATH",
            related_connection=connection,
            description="BUTT",
        )

        tool.Model.recreate_wall(element1, wall1, axis1["reference"], axis1["reference"])

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
                results["height"] = (item.Depth * self.unit_scale) / abs(1 / cos(results["x_angle"]))
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
