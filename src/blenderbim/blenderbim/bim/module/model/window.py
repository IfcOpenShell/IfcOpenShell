# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021, 2022 Dion Moult <dion@thinkmoult.com>, @Andrej730
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
from bpy.types import Operator
from bpy.props import FloatProperty, IntProperty, BoolProperty
from bpy_extras.object_utils import AddObjectHelper, object_data_add
import bmesh
from bmesh.types import BMVert

import ifcopenshell
from ifcopenshell.api.geometry.add_window_representation import DEFAULT_PANEL_SCHEMAS
import blenderbim
import blenderbim.tool as tool
import blenderbim.core.geometry as core
from blenderbim.bim.ifc import IfcStore

from mathutils import Vector
from pprint import pprint

from os.path import basename, dirname
import json


V = lambda *x: Vector([float(i) for i in x])


def update_window_modifier_representation(context):
    obj = context.active_object
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
        },
        "panel_properties": [],
    }
    number_of_panels = len(props.window_types_panels[props.window_type])
    for panel_i in range(number_of_panels):
        panel_data = {
            "FrameDepth": props.frame_depth[panel_i],
            "FrameThickness": props.frame_thickness[panel_i],
            "RelativeWidth": props.relative_width[panel_i],
            "RelativeHeight": props.relative_height[panel_i],
        }
        representation_data["panel_properties"].append(panel_data)

    # ELEVATION_VIEW representation
    ifc_context = ifcopenshell.util.representation.get_context(ifc_file, "Model", "Profile", "ELEVATION_VIEW")
    if not ifc_context:
        model_context = ifcopenshell.util.representation.get_context(ifc_file, "Model")
        ifc_context = ifcopenshell.api.run(
            "context.add_context",
            ifc_file,
            context_type="Model",
            context_identifier="Profile",
            target_view="ELEVATION_VIEW",
            parent=model_context,
        )

    representation_data["context"] = ifc_context
    elevation_representation = ifcopenshell.api.run(
        "geometry.add_window_representation", ifc_file, **representation_data
    )
    replace_representation_for_object(ifc_file, ifc_context, obj, elevation_representation)

    # MODEL_VIEW representation
    ifc_context = ifcopenshell.util.representation.get_context(ifc_file, "Model", "Body", "MODEL_VIEW")
    representation_data["context"] = ifc_context
    model_representation = ifcopenshell.api.run("geometry.add_window_representation", ifc_file, **representation_data)
    replace_representation_for_object(ifc_file, ifc_context, obj, model_representation)


def replace_representation_for_object(ifc_file, ifc_context, obj, new_representation):
    ifc_element = tool.Ifc.get_entity(obj)
    old_representation = ifcopenshell.util.representation.get_representation(
        ifc_element, 
        ifc_context.ContextType, 
        ifc_context.ContextIdentifier, 
        ifc_context.TargetView)

    if old_representation:
        for inverse in ifc_file.get_inverse(old_representation):
            ifcopenshell.util.element.replace_attribute(inverse, old_representation, new_representation)
        core.switch_representation(
            tool.Geometry,
            obj=obj,
            representation=new_representation,
            should_reload=True,
            is_global=False,
            should_sync_changes_first=True,
        )
        core.remove_representation(tool.Ifc, tool.Geometry, obj=obj, representation=old_representation)
    else:
        ifcopenshell.api.run(
            "geometry.assign_representation", ifc_file, product=ifc_element, representation=new_representation
        )


def create_bm_window_closed_profile(bm, size: Vector, thickness: float, position: Vector):
    width, depth, height = size

    verts = [
        (0, [thickness, 0.0, thickness]),
        (1, [width - thickness, 0.0, thickness]),
        (2, [thickness, 0.0, height - thickness]),
        (3, [width - thickness, 0.0, height - thickness]),
        (4, [0.0, 0.0, 0.0]),
        (5, [0.0, 0.0, height]),
        (6, [width, 0.0, 0.0]),
        (7, [width, 0.0, height]),
    ]

    edges = [
        (0,  (0, 1)),
        (1,  (2, 3)),
        (2,  (4, 5)),
        (3,  (6, 7)),
        (4,  (7, 5)),
        (5,  (1, 3)),
        (6,  (4, 6)),
        (7,  (0, 2)),
        (8,  (2, 5)),
        (9,  (3, 7)),
        (10, (4, 0)),
        (11, (1, 6)),
    ]

    faces = [
        (0, (2, 3, 7, 5)),
        (1, (5, 4, 0, 2)),
        (2, (1, 0, 4, 6)),
        (3, (7, 3, 1, 6)),
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


def update_window_modifier_bmesh(context):
    obj = context.object
    props = obj.BIMWindowProperties
    si_conversion = 0.001 / ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
    panel_schema = DEFAULT_PANEL_SCHEMAS[props.window_type]
    accumulated_height = [0] * len(panel_schema[0])
    built_panels = []

    overall_width = props.overall_width * si_conversion
    lining_depth = props.lining_depth * si_conversion
    overall_height = props.overall_height * si_conversion
    lining_to_panel_offset_x = props.lining_to_panel_offset_x * si_conversion

    bm = bmesh.new()

    for row_i, panel_row in enumerate(reversed(panel_schema)):
        accumulated_width = 0
        for column_i, panel_i in enumerate(panel_row):
            if panel_i in built_panels:
                accumulated_height[column_i] += props.relative_height[panel_i]
                accumulated_width += props.relative_width[panel_i]
                continue

            frame_depth = props.frame_depth[panel_i] * si_conversion
            frame_thickness = props.frame_thickness[panel_i] * si_conversion
            glass_thickness = 10 * si_conversion

            # create lining
            lining_size = V(
                overall_width * props.relative_width[panel_i],
                lining_depth,
                overall_height * props.relative_height[panel_i],
            )
            thickness = props.lining_thickness * si_conversion
            lining_verts = create_bm_window_closed_profile(bm, lining_size, thickness, V(0, 0, 0))

            # add panel
            panel_size = lining_size.copy()
            panel_size.y = frame_depth
            panel_size = panel_size - V(lining_to_panel_offset_x * 2, 0, lining_to_panel_offset_x * 2)

            panel_position = V(
                props.lining_to_panel_offset_x * si_conversion,
                ((props.lining_depth - props.frame_depth[panel_i]) + props.lining_to_panel_offset_y) * si_conversion,
                props.lining_to_panel_offset_x * si_conversion,
            )
            thickness = props.frame_thickness[panel_i] * si_conversion
            panel_verts = create_bm_window_closed_profile(bm, panel_size, thickness, panel_position)

            # add glass
            glass_verts = bmesh.ops.create_cube(bm, size=1)["verts"]
            bmesh.ops.translate(bm, vec=-glass_verts[0].co, verts=glass_verts)
            glass_size = panel_size
            glass_size.y = glass_thickness
            glass_size = glass_size - V(frame_thickness * 2, 0, frame_thickness)
            glass_position = panel_position + V(
                frame_thickness,
                frame_depth / 2 - glass_thickness / 2,
                frame_thickness,
            )
            bmesh.ops.scale(bm, vec=glass_size, verts=glass_verts)
            bmesh.ops.translate(bm, vec=glass_position, verts=glass_verts)

            # translate panel
            accumulated_offset = V(accumulated_width, 0, accumulated_height[column_i]) * V(
                overall_width, 0, overall_height
            )
            bmesh.ops.translate(bm, vec=accumulated_offset, verts=lining_verts + panel_verts + glass_verts)

            built_panels.append(panel_i)

            accumulated_height[column_i] += props.relative_height[panel_i]
            accumulated_width += props.relative_width[panel_i]

    bmesh.ops.translate(bm, vec=V(0, props.lining_offset * si_conversion, 0), verts=bm.verts)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0001)

    if bpy.context.object.mode == "EDIT":
        bmesh.update_edit_mesh(obj.data)
    else:
        bm.to_mesh(obj.data)
        bm.free()
    obj.data.update()


# UI operators
class AddWindow(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_window"
    bl_label = "Add Window"
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
        psets = ifcopenshell.util.element.get_psets(element)
        pset = psets.get("BBIM_Window", None)

        if pset:
            pset = tool.Ifc.get().by_id(pset["id"])
        else:
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
    bl_label = "Cancel editing Window"
    bl_options = {"REGISTER"}

    def _execute(self, context):
        obj = context.active_object
        element = tool.Ifc.get_entity(obj)
        psets = ifcopenshell.util.element.get_psets(element)
        data = json.loads(psets["BBIM_Window"]["Data"])
        props = obj.BIMWindowProperties
        # restore previous settings since editing was canceled
        for prop_name in data:
            setattr(props, prop_name, data[prop_name])
        update_window_modifier_representation(context)

        props.is_editing = -1

        return {"FINISHED"}


class FinishEditingWindow(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.finish_editing_window"
    bl_label = "Finish editing window"
    bl_options = {"REGISTER"}

    def _execute(self, context):
        obj = context.active_object
        element = tool.Ifc.get_entity(obj)
        props = obj.BIMWindowProperties

        psets = ifcopenshell.util.element.get_psets(element)
        pset = psets["BBIM_Window"]
        window_data = props.get_general_kwargs()
        lining_props = props.get_lining_kwargs()
        panel_props = props.get_panel_kwargs()

        window_data["lining_properties"] = lining_props
        window_data["panel_properties"] = panel_props

        props.is_editing = -1

        update_window_modifier_representation(context)

        pset = tool.Ifc.get().by_id(pset["id"])
        window_data = json.dumps(window_data, default=list)
        # TODO: debug two types of data in
        # from blenderbim.bim.module.model.data import WindowData
        # WindowData.data['parameters'].keys()
        # same thing could go for both stairs and arrays
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
        pset = ifcopenshell.util.element.get_psets(element)
        data = json.loads(pset["BBIM_Window"]["Data"])
        # required since we could load pset from .ifc and BIMWindowProperties won't be set
        for prop_name in data:
            setattr(props, prop_name, data[prop_name])

        props.is_editing = 1
        return {"FINISHED"}


class RemoveWindow(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_window"
    bl_label = "Remove Window"
    bl_options = {"REGISTER"}

    def _execute(self, context):
        obj = context.active_object
        element = tool.Ifc.get_entity(obj)
        obj.BIMWindowProperties.is_editing = -1

        pset = ifcopenshell.util.element.get_psets(element)
        pset = tool.Ifc.get().by_id(pset["BBIM_Window"]["id"])
        ifcopenshell.api.run("pset.remove_pset", tool.Ifc.get(), pset=pset)

        return {"FINISHED"}
