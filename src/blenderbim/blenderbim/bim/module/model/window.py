# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2023 @Andrej730
#
# This file is part of BlenderBIM Add-on.
#
# BlenderBIM Add-on is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BlenderBIM Add-on is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with BlenderBIM Add-on.  If not, see <http://www.gnu.org/licenses/>.


import bpy
import json
import bmesh
import collections
import ifcopenshell
import blenderbim.tool as tool
import blenderbim.core.root
import blenderbim.core.geometry
from ifcopenshell.api.geometry.add_window_representation import DEFAULT_PANEL_SCHEMAS
from ifcopenshell.util.shape_builder import V
from bpy.types import Operator
from bpy.props import FloatProperty, IntProperty, BoolProperty
from bmesh.types import BMVert
from blenderbim.bim.helper import convert_property_group_from_si
from blenderbim.bim.ifc import IfcStore
from mathutils import Vector


# TODO: move to some utils helpers/tool module
def update_simple_openings(element, opening_width, opening_height):
    ifc_file = tool.Ifc.get()
    fillings = tool.Ifc.get_all_element_occurences(element)

    voided_objs = set()
    has_replaced_opening_representation = False
    for filling in fillings:
        if not filling.FillsVoids:
            continue

        opening = filling.FillsVoids[0].RelatingOpeningElement
        voided_obj = tool.Ifc.get_object(opening.VoidsElements[0].RelatingBuildingElement)
        voided_objs.add(voided_obj)

        # we assume that the same element type (e.g. window)
        # will be used only for voiding objects of the same thickness (by y-dimension)
        # (e.g. all walls window's attached to will share the same thickness)
        # If that's not the case it will some linings will be too thick or too thin
        if has_replaced_opening_representation:
            continue

        old_representation = ifcopenshell.util.representation.get_representation(opening, "Model", "Body", "MODEL_VIEW")
        old_representation = tool.Geometry.resolve_mapped_representation(old_representation)
        ifcopenshell.api.run(
            "geometry.unassign_representation", ifc_file, product=opening, representation=old_representation
        )

        thickness = voided_obj.dimensions[1] + 0.1 + 0.1
        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(ifc_file)
        shape_builder = ifcopenshell.util.shape_builder.ShapeBuilder(ifc_file)
        context = ifcopenshell.util.representation.get_context(ifc_file, "Model", "Body", "MODEL_VIEW")

        extrusion = shape_builder.extrude(
            shape_builder.rectangle(size=Vector([opening_width, 0.0, opening_height]).xz),
            magnitude=thickness / unit_scale,
            position=Vector([0.0, -0.1 / unit_scale, 0.0]),
            position_x_axis=V(1, 0, 0),
            position_z_axis=V(0, -1, 0),
            extrusion_vector=V(0, 0, -1),
        )

        new_representation = shape_builder.get_representation(context, extrusion)

        for inverse in ifc_file.get_inverse(old_representation):
            ifcopenshell.util.element.replace_attribute(inverse, old_representation, new_representation)

        ifcopenshell.api.run("geometry.remove_representation", ifc_file, representation=old_representation)

        has_replaced_opening_representation = True

    for obj in voided_objs:
        element = tool.Ifc.get_entity(obj)
        body = ifcopenshell.util.representation.get_representation(element, "Model", "Body", "MODEL_VIEW")
        blenderbim.core.geometry.switch_representation(
            tool.Ifc,
            tool.Geometry,
            obj=obj,
            representation=body,
            should_reload=True,
            is_global=True,
            should_sync_changes_first=False,
        )


def update_window_modifier_representation(context):
    obj = context.active_object
    element = tool.Ifc.get_entity(obj)
    props = obj.BIMWindowProperties
    ifc_file = tool.Ifc.get()

    representation_data = {
        "partition_type": props.window_type,
        "overall_height": props.overall_height,
        "overall_width": props.overall_width,
        "lining_properties": {
            "LiningDepth": props.lining_depth,
            "LiningThickness": props.lining_thickness,
            "LiningOffset": props.lining_offset,
            "LiningToPanelOffsetX": props.lining_to_panel_offset_x,
            "LiningToPanelOffsetY": props.lining_to_panel_offset_y,
            "MullionThickness": props.mullion_thickness,
            "FirstMullionOffset": props.first_mullion_offset,
            "SecondMullionOffset": props.second_mullion_offset,
            "TransomThickness": props.transom_thickness,
            "FirstTransomOffset": props.first_transom_offset,
            "SecondTransomOffset": props.second_transom_offset,
        },
        "panel_properties": [],
    }
    number_of_panels, panels_data = props.window_types_panels[props.window_type]
    for panel_i in range(number_of_panels):
        panel_data = {
            "FrameDepth": props.frame_depth[panel_i],
            "FrameThickness": props.frame_thickness[panel_i],
        }
        representation_data["panel_properties"].append(panel_data)

    # ELEVATION_VIEW representation
    profile = ifcopenshell.util.representation.get_context(ifc_file, "Model", "Profile", "ELEVATION_VIEW")
    if profile:
        representation_data["context"] = profile
        elevation_representation = ifcopenshell.api.run(
            "geometry.add_window_representation", ifc_file, **representation_data
        )
        tool.Model.replace_object_ifc_representation(profile, obj, elevation_representation)

    # MODEL_VIEW representation
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
        blenderbim.core.geometry.switch_representation(
            tool.Ifc,
            tool.Geometry,
            obj=obj,
            representation=model_representation,
            should_reload=True,
            is_global=True,
            should_sync_changes_first=True,
        )

    # type attributes
    element.PartitioningType = props.window_type

    # occurences attributes
    occurences = tool.Ifc.get_all_element_occurences(element)
    for occurence in occurences:
        occurence.OverallWidth = props.overall_width
        occurence.OverallHeight = props.overall_height

    update_simple_openings(element, props.overall_width, props.overall_height)


def create_bm_window_frame(bm, size: Vector, thickness: list, position: Vector = V(0, 0, 0).freeze()):
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


def create_bm_box(bm, size: Vector = V(1, 1, 1).freeze(), position: Vector = V(0, 0, 0).freeze()):
    """create a box of `size`, position box first vertex at `position`"""
    box_verts = bmesh.ops.create_cube(bm, size=1)["verts"]
    bmesh.ops.translate(bm, vec=-box_verts[0].co, verts=box_verts)
    bmesh.ops.scale(bm, vec=size, verts=box_verts)
    bmesh.ops.translate(bm, vec=position, verts=box_verts)
    return box_verts


def create_bm_window(
    bm,
    lining_size: Vector,
    lining_thickness: list,
    lining_to_panel_offset_x,
    lining_to_panel_offset_y_full,
    frame_size: Vector,
    frame_thickness,
    glass_thickness,
    position: Vector,
):
    """`lining_thickness` expected to be defined as a list,
    similarly to `create_bm_window_frame` `thickness` argument"""
    # window lining
    window_lining_verts = create_bm_window_frame(bm, lining_size, lining_thickness)

    # window frame
    frame_position = V(lining_to_panel_offset_x, lining_to_panel_offset_y_full, lining_to_panel_offset_x)
    frame_verts = create_bm_window_frame(bm, frame_size, frame_thickness, frame_position)

    # window glass
    glass_size = frame_size - V(frame_thickness * 2, 0, frame_thickness * 2)
    glass_size.y = glass_thickness
    glass_position = frame_position + V(frame_thickness, frame_size.y / 2 - glass_thickness / 2, frame_thickness)

    glass_verts = create_bm_box(bm, glass_size, glass_position)

    translated_verts = window_lining_verts + frame_verts + glass_verts
    bmesh.ops.translate(bm, vec=position, verts=translated_verts)

    return (window_lining_verts, frame_verts, glass_verts)


def update_window_modifier_bmesh(context):
    obj = context.object
    props = obj.BIMWindowProperties
    si_conversion = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
    panel_schema = DEFAULT_PANEL_SCHEMAS[props.window_type]
    accumulated_height = [0] * len(panel_schema[0])
    built_panels = []

    overall_width = props.overall_width * si_conversion
    lining_depth = props.lining_depth * si_conversion
    overall_height = props.overall_height * si_conversion
    lining_to_panel_offset_x = props.lining_to_panel_offset_x * si_conversion
    lining_to_panel_offset_y = props.lining_to_panel_offset_y * si_conversion
    lining_thickness = props.lining_thickness * si_conversion
    lining_offset = props.lining_offset * si_conversion

    mullion_thickness = props.mullion_thickness * si_conversion / 2
    first_mullion_offset = props.first_mullion_offset * si_conversion
    second_mullion_offset = props.second_mullion_offset * si_conversion
    transom_thickness = props.transom_thickness * si_conversion / 2
    first_transom_offset = props.first_transom_offset * si_conversion
    second_transom_offset = props.second_transom_offset * si_conversion

    glass_thickness = 0.01 * si_conversion

    bm = bmesh.new()
    panel_schema = list(reversed(panel_schema))

    # TODO: need more readable way to define panel width and height
    unique_rows_in_col = [len(set(row[column_i] for row in panel_schema)) for column_i in range(len(panel_schema[0]))]
    for row_i, panel_row in enumerate(panel_schema):
        accumulated_width = 0
        unique_cols = len(set(panel_row))

        for column_i, panel_i in enumerate(panel_row):
            # calculate current panel dimensions
            if unique_cols > 1:
                if column_i == 0:
                    panel_width = first_mullion_offset
                elif column_i == unique_cols - 1:
                    panel_width = overall_width - accumulated_width
                else:
                    panel_width = second_mullion_offset - accumulated_width
            else:
                panel_width = overall_width

            if unique_rows_in_col[column_i] > 1:
                if row_i == 0:
                    panel_height = first_transom_offset
                elif row_i == unique_rows_in_col[column_i] - 1:
                    panel_height = overall_height - accumulated_height[column_i]
                else:
                    panel_height = second_transom_offset - accumulated_height[column_i]
            else:
                panel_height = overall_height

            if panel_i in built_panels:
                accumulated_height[column_i] += panel_height
                accumulated_width += panel_width
                continue

            frame_depth = props.frame_depth[panel_i] * si_conversion
            frame_thickness = props.frame_thickness[panel_i] * si_conversion

            # add window
            window_lining_size = V(
                panel_width,
                lining_depth,
                panel_height,
            )

            # calculate lining thickness
            # taking into account mullions and transoms
            window_lining_thickness = [lining_thickness] * 4
            # mullion thickness
            if unique_cols > 1:
                if column_i != 0:
                    window_lining_thickness[0] = mullion_thickness  # left column
                if column_i != unique_cols - 1:
                    window_lining_thickness[2] = mullion_thickness  # right column
            # transom thickness
            if unique_rows_in_col[column_i] > 1:
                if row_i != 0:
                    window_lining_thickness[3] = transom_thickness  # bottom row
                if row_i != unique_rows_in_col[column_i] - 1:
                    window_lining_thickness[1] = transom_thickness  # top row

            frame_size = window_lining_size.copy()
            frame_size.y = frame_depth
            frame_size = frame_size - V(lining_to_panel_offset_x * 2, 0, lining_to_panel_offset_x * 2)

            window_position = V(accumulated_width, 0, accumulated_height[column_i])
            lining_verts, panel_verts, glass_verts = create_bm_window(
                bm,
                window_lining_size,
                window_lining_thickness,
                lining_to_panel_offset_x,
                (lining_depth - frame_depth) + lining_to_panel_offset_y,
                frame_size,
                frame_thickness,
                glass_thickness,
                window_position,
            )

            built_panels.append(panel_i)

            accumulated_height[column_i] += panel_height
            accumulated_width += panel_width

    bmesh.ops.translate(bm, vec=V(0, lining_offset, 0), verts=bm.verts)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0001)

    if bpy.context.object.mode == "EDIT":
        bmesh.update_edit_mesh(obj.data)
    else:
        bm.to_mesh(obj.data)
        bm.free()
    obj.data.update()


class BIM_OT_add_window(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "mesh.add_window"
    bl_label = "Window"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        ifc_file = tool.Ifc.get()
        if not ifc_file:
            self.report({"ERROR"}, "You need to start IFC project first to create a window.")
            return {"CANCELLED"}

        if context.object is not None:
            spawn_location = context.object.location.copy()
            context.object.select_set(False)
        else:
            spawn_location = bpy.context.scene.cursor.location.copy()

        mesh = bpy.data.meshes.new("IfcWindow")
        obj = bpy.data.objects.new("IfcWindow", mesh)
        obj.location = spawn_location
        element = blenderbim.core.root.assign_class(
            tool.Ifc, tool.Collector, tool.Root, obj=obj, ifc_class="IfcWindow", should_add_representation=False
        )
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
    bl_options = {"REGISTER"}

    def _execute(self, context):
        obj = context.active_object
        element = tool.Ifc.get_entity(obj)
        props = obj.BIMWindowProperties

        if element.is_a() not in ("IfcWindow", "IfcWindowType"):
            self.report({"ERROR"}, "Object has to be IfcWindow/IfcWindowType type to add a window.")
            return {"CANCELLED"}

        # need to make sure all default props will have correct units
        if not props.window_added_previously:
            convert_property_group_from_si(props, skip_props=("is_editing", "window_type", "window_added_previously"))

        window_data = props.get_general_kwargs()
        lining_props = props.get_lining_kwargs()
        panel_props = props.get_panel_kwargs()

        window_data["lining_properties"] = lining_props
        window_data["panel_properties"] = panel_props
        pset = tool.Pset.get_element_pset(element, "BBIM_Window")
        if not pset:
            pset = ifcopenshell.api.run("pset.add_pset", tool.Ifc.get(), product=element, name="BBIM_Window")

        ifcopenshell.api.run(
            "pset.edit_pset",
            tool.Ifc.get(),
            pset=pset,
            properties={"Data": json.dumps(window_data, default=list)},
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
        props = obj.BIMWindowProperties
        for prop_name in data:
            setattr(props, prop_name, data[prop_name])

        body = ifcopenshell.util.representation.get_representation(element, "Model", "Body", "MODEL_VIEW")
        blenderbim.core.geometry.switch_representation(
            tool.Ifc,
            tool.Geometry,
            obj=obj,
            representation=body,
            should_reload=True,
            is_global=True,
            should_sync_changes_first=False,
        )

        props.is_editing = -1
        return {"FINISHED"}


class FinishEditingWindow(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.finish_editing_window"
    bl_label = "Finish Editing Window"
    bl_options = {"REGISTER"}

    def _execute(self, context):
        obj = context.active_object
        element = tool.Ifc.get_entity(obj)
        props = obj.BIMWindowProperties

        window_data = props.get_general_kwargs()
        lining_props = props.get_lining_kwargs()
        panel_props = props.get_panel_kwargs()

        window_data["lining_properties"] = lining_props
        window_data["panel_properties"] = panel_props

        props.is_editing = -1

        update_window_modifier_representation(context)

        pset = tool.Pset.get_element_pset(element, "BBIM_Window")
        window_data = json.dumps(window_data, default=list)
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
        for prop_name in data:
            setattr(props, prop_name, data[prop_name])

        # need to make sure all props that weren't used before
        # will have correct units
        skip_props = ("is_editing", "window_type", "window_added_previously")
        skip_props += tuple(data.keys())
        convert_property_group_from_si(props, skip_props=skip_props)

        props.is_editing = 1
        return {"FINISHED"}


class RemoveWindow(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_window"
    bl_label = "Remove Window"
    bl_options = {"REGISTER"}

    def _execute(self, context):
        obj = context.active_object
        props = obj.BIMWindowProperties
        element = tool.Ifc.get_entity(obj)
        obj.BIMWindowProperties.is_editing = -1

        pset = tool.Pset.get_element_pset(element, "BBIM_Window")
        ifcopenshell.api.run("pset.remove_pset", tool.Ifc.get(), pset=pset)
        props.window_added_previously = True

        return {"FINISHED"}


def add_object_button(self, context):
    self.layout.operator(BIM_OT_add_window.bl_idname, icon="PLUGIN")
