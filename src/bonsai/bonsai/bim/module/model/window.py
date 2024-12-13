# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2023 @Andrej730
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


import bpy
import json
import bmesh
import collections
import ifcopenshell
import bonsai.tool as tool
import bonsai.core.root
import bonsai.core.geometry
from ifcopenshell.api.geometry.add_window_representation import DEFAULT_PANEL_SCHEMAS
import ifcopenshell.api
import ifcopenshell.util.element
import ifcopenshell.util.representation
import ifcopenshell.util.shape_builder
import ifcopenshell.util.unit
from ifcopenshell.util.shape_builder import V
from bmesh.types import BMVert
from mathutils import Vector
from typing import Optional


def update_window_modifier_representation(context: bpy.types.Context) -> None:
    obj = context.active_object
    element = tool.Ifc.get_entity(obj)
    props = obj.BIMWindowProperties
    ifc_file = tool.Ifc.get()
    si_conversion = ifcopenshell.util.unit.calculate_unit_scale(ifc_file)

    representation_data = {
        "partition_type": props.window_type,
        "overall_height": props.overall_height / si_conversion,
        "overall_width": props.overall_width / si_conversion,
        "lining_properties": {
            "LiningDepth": props.lining_depth / si_conversion,
            "LiningThickness": props.lining_thickness / si_conversion,
            "LiningOffset": props.lining_offset / si_conversion,
            "LiningToPanelOffsetX": props.lining_to_panel_offset_x / si_conversion,
            "LiningToPanelOffsetY": props.lining_to_panel_offset_y / si_conversion,
            "MullionThickness": props.mullion_thickness / si_conversion,
            "FirstMullionOffset": props.first_mullion_offset / si_conversion,
            "SecondMullionOffset": props.second_mullion_offset / si_conversion,
            "TransomThickness": props.transom_thickness / si_conversion,
            "FirstTransomOffset": props.first_transom_offset / si_conversion,
            "SecondTransomOffset": props.second_transom_offset / si_conversion,
        },
        "panel_properties": [],
    }
    number_of_panels, panels_data = props.window_types_panels[props.window_type]
    for panel_i in range(number_of_panels):
        panel_data = {
            "FrameDepth": props.frame_depth[panel_i] / si_conversion,
            "FrameThickness": props.frame_thickness[panel_i] / si_conversion,
        }
        representation_data["panel_properties"].append(panel_data)

    previously_active_context = tool.Geometry.get_active_representation_context(obj)

    # ELEVATION_VIEW representation
    profile = ifcopenshell.util.representation.get_context(ifc_file, "Model", "Profile", "ELEVATION_VIEW")
    if profile:
        representation_data["context"] = profile
        elevation_representation = ifcopenshell.api.run(
            "geometry.add_window_representation", ifc_file, **representation_data
        )
        tool.Model.replace_object_ifc_representation(profile, obj, elevation_representation)

    # MODEL_VIEW representation
    # (Model/Body defined only BEFORE Plan/Body to prevent #2744)
    body = ifcopenshell.util.representation.get_context(ifc_file, "Model", "Body", "MODEL_VIEW")
    representation_data["context"] = body
    model_representation = ifcopenshell.api.run("geometry.add_window_representation", ifc_file, **representation_data)
    tool.Model.replace_object_ifc_representation(body, obj, model_representation)

    # PLAN_VIEW representation
    plan = ifcopenshell.util.representation.get_context(ifc_file, "Plan", "Body", "PLAN_VIEW")
    if plan:
        representation_data["context"] = plan
        plan_representation = ifcopenshell.api.run(
            "geometry.add_window_representation", ifc_file, **representation_data
        )
        tool.Model.replace_object_ifc_representation(plan, obj, plan_representation)

    # adding switch representation at the end instead of changing order of representations
    # to prevent #2744
    if tool.Geometry.get_active_representation_context(obj) != previously_active_context:
        previously_active_representation = ifcopenshell.util.representation.get_representation(
            element,
            previously_active_context.ContextType,
            previously_active_context.ContextIdentifier,
            previously_active_context.TargetView,
        )
        bonsai.core.geometry.switch_representation(
            tool.Ifc,
            tool.Geometry,
            obj=obj,
            representation=previously_active_representation,
            should_reload=True,
            is_global=True,
            should_sync_changes_first=True,
        )

    # type attributes
    if tool.Ifc.get_schema() != "IFC2X3":
        element.PartitioningType = props.window_type

    # occurrences attributes
    occurrences = tool.Ifc.get_all_element_occurrences(element)
    for occurrence in occurrences:
        occurrence.OverallWidth = props.overall_width / si_conversion
        occurrence.OverallHeight = props.overall_height / si_conversion

    tool.Model.update_simple_openings(element)


def create_bm_window_frame(
    bm: bmesh.types.BMesh, size: Vector, thickness: list, position: Vector = V(0, 0, 0).freeze()
) -> list[bmesh.types.BMVert]:
    """`thickness` of the profile is defined as list in the following order:
    `(LEFT, TOP, RIGHT, BOTTOM)`

    `thickness` can be also defined just as 1 float value.
    """

    if not isinstance(thickness, collections.abc.Iterable):
        thickness = [thickness] * 4

    th_left, th_up, th_right, th_bottom = thickness

    width, depth, height = size

    verts = [
        (0, [th_left, 0.0, th_bottom]),
        (1, [width - th_right, 0.0, th_bottom]),
        (2, [th_left, 0.0, height - th_up]),
        (3, [width - th_right, 0.0, height - th_up]),
        (4, [0.0, 0.0, 0.0]),
        (5, [0.0, 0.0, height]),
        (6, [width, 0.0, 0.0]),
        (7, [width, 0.0, height]),
    ]

    edges = [
        (0, (0, 1)),
        (1, (2, 3)),
        (2, (4, 5)),
        (3, (6, 7)),
        (4, (7, 5)),
        (5, (1, 3)),
        (6, (4, 6)),
        (7, (0, 2)),
        (8, (2, 5)),
        (9, (3, 7)),
        (10, (4, 0)),
        (11, (1, 6)),
    ]

    faces = [
        (0, (5, 7, 3, 2)),
        (1, (2, 0, 4, 5)),
        (2, (6, 4, 0, 1)),
        (3, (6, 1, 3, 7)),
    ]

    bm.verts.index_update()
    bm.edges.index_update()
    bm.faces.ensure_lookup_table()

    new_verts = [bm.verts.new(v[1]) for v in verts]
    new_edges = [bm.edges.new([new_verts[vi] for vi in edge[1]]) for edge in edges]
    new_faces = [bm.faces.new([new_verts[vi] for vi in face[1]]) for face in faces]

    extruded = bmesh.ops.extrude_face_region(bm, geom=new_faces)
    extrusion_vector = Vector((0, 1, 0)) * depth
    translate_verts = [v for v in extruded["geom"] if isinstance(v, BMVert)]
    bmesh.ops.translate(bm, vec=extrusion_vector, verts=translate_verts)

    bmesh.ops.translate(bm, vec=position, verts=new_verts + translate_verts)

    return new_verts + translate_verts


def create_bm_box(
    bm: bmesh.types.BMesh, size: Vector = V(1, 1, 1).freeze(), position: Vector = V(0, 0, 0).freeze()
) -> list[bmesh.types.BMVert]:
    """create a box of `size`, position box first vertex at `position`"""
    box_verts = bmesh.ops.create_cube(bm, size=1)["verts"]
    bmesh.ops.translate(bm, vec=-box_verts[0].co, verts=box_verts)
    bmesh.ops.scale(bm, vec=size, verts=box_verts)
    bmesh.ops.translate(bm, vec=position, verts=box_verts)
    return box_verts


def create_bm_window(
    bm: bmesh.types.BMesh,
    lining_size: Vector,
    lining_thickness: list,
    lining_to_panel_offset_x,
    lining_to_panel_offset_y_full,
    frame_size: Vector,
    frame_thickness: float,
    glass_thickness: float,
    position: Vector,
    x_offsets: Optional[list] = None,
) -> tuple[list[bmesh.types.BMVert], list[bmesh.types.BMVert], list[bmesh.types.BMVert]]:
    """`lining_thickness` and `x_offsets` are expected to be defined as a list,
    similarly to `create_bm_window_frame` `thickness` argument"""

    if x_offsets is None:
        x_offsets = [lining_to_panel_offset_x] * 4

    # window lining
    window_lining_verts = create_bm_window_frame(bm, lining_size, lining_thickness)

    # window frame
    frame_position = V(x_offsets[0], lining_to_panel_offset_y_full, x_offsets[3])
    frame_verts = create_bm_window_frame(bm, frame_size, frame_thickness, frame_position)

    # window glass
    glass_size = frame_size - V(frame_thickness * 2, 0, frame_thickness * 2)
    glass_size.y = glass_thickness
    glass_position = frame_position + V(frame_thickness, frame_size.y / 2 - glass_thickness / 2, frame_thickness)

    glass_verts = create_bm_box(bm, glass_size, glass_position)

    translated_verts = window_lining_verts + frame_verts + glass_verts
    bmesh.ops.translate(bm, vec=position, verts=translated_verts)

    return (window_lining_verts, frame_verts, glass_verts)


def update_window_modifier_bmesh(context: bpy.types.Context) -> None:
    obj = context.active_object
    props = obj.BIMWindowProperties
    panel_schema = DEFAULT_PANEL_SCHEMAS[props.window_type]
    accumulated_height = [0] * len(panel_schema[0])
    built_panels = []

    overall_width = props.overall_width
    lining_depth = props.lining_depth
    overall_height = props.overall_height
    lining_to_panel_offset_x = props.lining_to_panel_offset_x
    lining_to_panel_offset_y = props.lining_to_panel_offset_y
    lining_thickness = props.lining_thickness
    lining_offset = props.lining_offset

    mullion_thickness = props.mullion_thickness / 2
    first_mullion_offset = props.first_mullion_offset
    second_mullion_offset = props.second_mullion_offset
    transom_thickness = props.transom_thickness / 2
    first_transom_offset = props.first_transom_offset
    second_transom_offset = props.second_transom_offset

    glass_thickness = 0.01

    bm = bmesh.new()
    panel_schema = list(reversed(panel_schema))

    # TODO: need more readable way to define panel width and height
    unique_rows_in_col = [len(set(row[column_i] for row in panel_schema)) for column_i in range(len(panel_schema[0]))]
    for row_i, panel_row in enumerate(panel_schema):
        accumulated_width = 0
        unique_cols = len(set(panel_row))

        for column_i, panel_i in enumerate(panel_row):
            # detect mullion
            has_mullion = unique_cols > 1
            first_column = column_i == 0
            last_column = column_i == unique_cols - 1
            left_to_mullion = has_mullion and not last_column
            right_to_mullion = has_mullion and not first_column

            # detect transom
            has_transom = unique_rows_in_col[column_i] > 1
            first_row = row_i == 0
            last_row = row_i == unique_rows_in_col[column_i] - 1
            top_to_transom = has_transom and not first_row
            bottom_to_transom = has_transom and not last_row

            # calculate current panel dimensions
            if has_mullion:
                if first_column:
                    panel_width = first_mullion_offset
                elif last_column:
                    panel_width = overall_width - accumulated_width
                else:
                    panel_width = second_mullion_offset - accumulated_width
            else:
                panel_width = overall_width

            if has_transom:
                if first_row:
                    panel_height = first_transom_offset
                elif last_row:
                    panel_height = overall_height - accumulated_height[column_i]
                else:
                    panel_height = second_transom_offset - accumulated_height[column_i]
            else:
                panel_height = overall_height

            if panel_i in built_panels:
                accumulated_height[column_i] += panel_height
                accumulated_width += panel_width
                continue

            frame_depth = props.frame_depth[panel_i]
            frame_thickness = props.frame_thickness[panel_i]
            lining_to_panel_offset_y_full = (lining_depth - frame_depth) + lining_to_panel_offset_y
            # add window
            window_lining_size = V(
                panel_width,
                lining_depth,
                panel_height,
            )

            # calculate lining thickness and frame size / offset
            # taking into account mullions and transoms
            # fmt: off
            window_lining_thickness = [
                mullion_thickness if right_to_mullion  else lining_thickness,
                transom_thickness if bottom_to_transom else lining_thickness,
                mullion_thickness if left_to_mullion   else lining_thickness,
                transom_thickness if top_to_transom    else lining_thickness,
            ]

            # x offsets can differ if there are mullions or transoms because we're trying to maintain symmetry
            base_frame_clear = lining_to_panel_offset_x + frame_thickness - lining_thickness
            current_offset_x = base_frame_clear - frame_thickness + mullion_thickness
            current_offset_z = base_frame_clear - frame_thickness + transom_thickness
            # fmt: off
            x_offsets = [
                current_offset_x if right_to_mullion  else lining_to_panel_offset_x,  # LEFT
                current_offset_z if bottom_to_transom else lining_to_panel_offset_x,  # TOP
                current_offset_x if left_to_mullion   else lining_to_panel_offset_x,  # RIGHT
                current_offset_z if top_to_transom    else lining_to_panel_offset_x,  # BOTTOM
            ]
            # fmt: on

            frame_size = window_lining_size.copy()
            frame_size.y = frame_depth
            frame_size.x -= x_offsets[0] + x_offsets[2]
            frame_size.z -= x_offsets[1] + x_offsets[3]

            window_position = V(accumulated_width, 0, accumulated_height[column_i])
            lining_verts, panel_verts, glass_verts = create_bm_window(
                bm,
                window_lining_size,
                window_lining_thickness,
                lining_to_panel_offset_x,
                lining_to_panel_offset_y_full,
                frame_size,
                frame_thickness,
                glass_thickness,
                window_position,
                x_offsets,
            )

            built_panels.append(panel_i)

            accumulated_height[column_i] += panel_height
            accumulated_width += panel_width

    bmesh.ops.translate(bm, vec=V(0, lining_offset, 0), verts=bm.verts)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0001)

    if bpy.context.active_object.mode == "EDIT":
        bmesh.update_edit_mesh(obj.data)
    else:
        bm.to_mesh(obj.data)
        bm.free()
    obj.data.update()


class BIM_OT_add_window(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "mesh.add_window"
    bl_label = "Window"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return tool.Ifc.get() and context.mode == "OBJECT"

    def _execute(self, context):
        ifc_file = tool.Ifc.get()
        if not ifc_file:
            self.report({"ERROR"}, "You need to start IFC project first to create a window.")
            return {"CANCELLED"}

        if context.active_object is not None:
            spawn_location = context.active_object.location.copy()
            context.active_object.select_set(False)
        else:
            spawn_location = bpy.context.scene.cursor.location.copy()

        mesh = bpy.data.meshes.new("IfcWindow")
        obj = bpy.data.objects.new("IfcWindow", mesh)
        obj.location = spawn_location

        element = bonsai.core.root.assign_class(
            tool.Ifc, tool.Collector, tool.Root, obj=obj, ifc_class="IfcWindow", should_add_representation=False
        )
        bonsai.core.geometry.edit_object_placement(tool.Ifc, tool.Geometry, tool.Surveyor, obj=obj)
        if tool.Ifc.get_schema() != "IFC2X3":
            element.PredefinedType = "WINDOW"

        bpy.ops.object.select_all(action="DESELECT")
        bpy.context.view_layer.objects.active = None
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.bim.add_window()
        return {"FINISHED"}


# UI operators
class AddWindow(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_window"
    bl_label = "Add Window"
    bl_description = "Add Bonsai parametric window to the active IFC element"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        obj = context.active_object
        element = tool.Ifc.get_entity(obj)
        props = obj.BIMWindowProperties

        window_data = props.get_general_kwargs(convert_to_project_units=True)
        lining_props = props.get_lining_kwargs(convert_to_project_units=True)
        panel_props = props.get_panel_kwargs(convert_to_project_units=True)

        window_data["lining_properties"] = lining_props
        window_data["panel_properties"] = panel_props
        pset = tool.Pset.get_element_pset(element, "BBIM_Window")
        if not pset:
            pset = ifcopenshell.api.run("pset.add_pset", tool.Ifc.get(), product=element, name="BBIM_Window")

        ifcopenshell.api.run(
            "pset.edit_pset",
            tool.Ifc.get(),
            pset=pset,
            properties={"Data": tool.Ifc.get().createIfcText(json.dumps(window_data, default=list))},
        )
        update_window_modifier_representation(context)
        return {"FINISHED"}


class CancelEditingWindow(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.cancel_editing_window"
    bl_label = "Cancel Editing Window"
    bl_options = {"REGISTER"}

    def _execute(self, context):
        obj = context.active_object
        element = tool.Ifc.get_entity(obj)
        data = json.loads(ifcopenshell.util.element.get_pset(element, "BBIM_Window", "Data"))
        data.update(data.pop("lining_properties"))
        data.update(data.pop("panel_properties"))
        props = obj.BIMWindowProperties
        props.set_props_kwargs_from_ifc_data(data)

        body = ifcopenshell.util.representation.get_representation(element, "Model", "Body", "MODEL_VIEW")
        bonsai.core.geometry.switch_representation(
            tool.Ifc,
            tool.Geometry,
            obj=obj,
            representation=body,
            should_reload=True,
            is_global=True,
            should_sync_changes_first=False,
        )

        props.is_editing = False
        return {"FINISHED"}


class FinishEditingWindow(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.finish_editing_window"
    bl_label = "Finish Editing Window"
    bl_options = {"REGISTER"}

    def _execute(self, context):
        obj = context.active_object
        element = tool.Ifc.get_entity(obj)
        props = obj.BIMWindowProperties

        window_data = props.get_general_kwargs(convert_to_project_units=True)
        lining_props = props.get_lining_kwargs(convert_to_project_units=True)
        panel_props = props.get_panel_kwargs(convert_to_project_units=True)

        window_data["lining_properties"] = lining_props
        window_data["panel_properties"] = panel_props

        props.is_editing = False

        update_window_modifier_representation(context)

        pset = tool.Pset.get_element_pset(element, "BBIM_Window")
        window_data = tool.Ifc.get().createIfcText(json.dumps(window_data, default=list))
        ifcopenshell.api.run("pset.edit_pset", tool.Ifc.get(), pset=pset, properties={"Data": window_data})
        return {"FINISHED"}


class EnableEditingWindow(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.enable_editing_window"
    bl_label = "Enable Editing Window"
    bl_options = {"REGISTER"}

    def _execute(self, context):
        obj = context.active_object
        props = obj.BIMWindowProperties
        element = tool.Ifc.get_entity(obj)
        data = json.loads(ifcopenshell.util.element.get_pset(element, "BBIM_Window", "Data"))
        data.update(data.pop("lining_properties"))
        data.update(data.pop("panel_properties"))

        # required since we could load pset from .ifc and BIMWindowProperties won't be set
        props.set_props_kwargs_from_ifc_data(data)

        props.is_editing = True
        return {"FINISHED"}


class RemoveWindow(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_window"
    bl_label = "Remove Window"
    bl_options = {"REGISTER"}

    def _execute(self, context):
        obj = context.active_object
        props = obj.BIMWindowProperties
        element = tool.Ifc.get_entity(obj)
        obj.BIMWindowProperties.is_editing = False

        pset = tool.Pset.get_element_pset(element, "BBIM_Window")
        ifcopenshell.api.run("pset.remove_pset", tool.Ifc.get(), product=element, pset=pset)

        return {"FINISHED"}
