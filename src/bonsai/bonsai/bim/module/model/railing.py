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
import bmesh
import ifcopenshell
import ifcopenshell.api
import ifcopenshell.util.representation
import ifcopenshell.util.unit
from ifcopenshell.util.shape_builder import V
import bonsai.core.root
import bonsai.core.geometry
import bonsai.tool as tool
from bonsai.bim.module.model.door import bm_sort_out_geom
from bonsai.bim.module.model.data import RailingData, refresh
from bonsai.bim.module.model.decorator import ProfileDecorator

from mathutils import Vector
import json
from typing import Any

# reference:
# https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcRailing.htm
# https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcRailingType.htm


def bm_split_edge_at_offset(edge: bmesh.types.BMEdge, offset: float) -> dict[str, Any]:
    v0, v1 = edge.verts

    offset = offset / 2
    edge_len = (v0.co - v1.co).xy.length

    split_output_0 = bmesh.utils.edge_split(edge, v0, offset / edge_len)
    split_output_1 = bmesh.utils.edge_split(edge, v1, offset / (edge_len - offset))
    new_geometry = bm_sort_out_geom(split_output_0 + split_output_1)
    return new_geometry


def update_railing_modifier_ifc_data(context: bpy.types.Context) -> None:
    """should be called after new geometry settled
    since it's going to update ifc representation
    """
    obj = context.active_object
    props = obj.BIMRailingProperties
    element = tool.Ifc.get_entity(obj)
    ifc_file = tool.Ifc.get()

    # type attributes
    element.PredefinedType = "USERDEFINED"
    # occurrences attributes
    occurrences = tool.Ifc.get_all_element_occurrences(element)
    for occurrence in occurrences:
        occurrence.ObjectType = props.railing_type

    # update pset
    pset_common = tool.Pset.get_element_pset(element, "Pset_RailingCommon")
    if not pset_common:
        pset_common = ifcopenshell.api.run("pset.add_pset", ifc_file, product=element, name="Pset_RailingCommon")

    ifcopenshell.api.run(
        "pset.edit_pset",
        ifc_file,
        pset=pset_common,
        properties={
            "Height": props.height,
        },
    )

    if props.railing_type == "WALL_MOUNTED_HANDRAIL":
        body = ifcopenshell.util.representation.get_context(ifc_file, "Model", "Body", "MODEL_VIEW")
        pset_data = tool.Model.get_modeling_bbim_pset_data(bpy.context.active_object, "BBIM_Railing")
        path_data = pset_data["data_dict"]["path_data"]
        railing_path = [Vector(v) for v in path_data["verts"]]
        looped_path = path_data["edges"][-1][-1] == path_data["edges"][0][0]
        si_conversion = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())

        representation_data = {
            "railing_type": props.railing_type,
            "context": body,
            "railing_path": railing_path,
            "use_manual_supports": props.use_manual_supports,
            "support_spacing": props.support_spacing / si_conversion,
            "railing_diameter": props.railing_diameter / si_conversion,
            "clear_width": props.clear_width / si_conversion,
            "terminal_type": props.terminal_type,
            "height": props.height / si_conversion,
            "looped_path": looped_path,
        }
        model_representation = ifcopenshell.api.run(
            "geometry.add_railing_representation", ifc_file, **representation_data
        )
        tool.Model.replace_object_ifc_representation(body, obj, model_representation)

    elif props.railing_type == "FRAMELESS_PANEL":
        tool.Model.add_body_representation(obj)


def update_bbim_railing_pset(element: ifcopenshell.entity_instance, railing_data: dict[str, Any]) -> None:
    pset = tool.Pset.get_element_pset(element, "BBIM_Railing")
    if not pset:
        pset = ifcopenshell.api.run("pset.add_pset", tool.Ifc.get(), product=element, name="BBIM_Railing")
    railing_data = tool.Ifc.get().createIfcText(json.dumps(railing_data, default=list))
    ifcopenshell.api.run("pset.edit_pset", tool.Ifc.get(), pset=pset, properties={"Data": railing_data})


def update_railing_modifier_bmesh(context: bpy.types.Context) -> None:
    """before using should make sure that Data contains up-to-date information.
    If BBIM Pset just changed should call refresh() before updating bmesh
    """
    obj = context.active_object
    props = obj.BIMRailingProperties

    # NOTE: using Data since bmesh update will hapen very often
    if not RailingData.is_loaded:
        RailingData.load()
    path_data = RailingData.data["path_data"]

    si_conversion = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
    # need to make sure we support edit mode
    # since users will probably be in edit mode when they'll be changing railing path
    bm = tool.Blender.get_bmesh_for_mesh(obj.data, clean=True)

    # generating railing path
    bm.verts.index_update()
    bm.edges.index_update()
    new_verts = [bm.verts.new(Vector(v) * si_conversion) for v in path_data["verts"]]
    new_edges = [bm.edges.new((new_verts[e[0]], new_verts[e[1]])) for e in path_data["edges"]]
    bm.verts.index_update()
    bm.edges.index_update()

    if props.is_editing_path:
        tool.Blender.apply_bmesh(obj.data, bm)
        return

    if props.railing_type != "FRAMELESS_PANEL":
        return

    def generate_frameless_panel_railing() -> None:
        # generating FRAMELESS_PANEL railing
        height = props.height
        thickness = props.thickness
        spacing = props.spacing

        # spacing
        # split each edge in 3 segments by 0.5 * spacing by x-y plane
        main_edges = bm.edges[:]
        for main_edge in main_edges:
            bm_split_edge_at_offset(main_edge, spacing)

        # thickness
        # keep track of translated verts so we won't translate the same
        # vert twice
        edge_dissolving_verts = []
        for main_edge in main_edges:
            v0, v1 = main_edge.verts
            edge_dissolving_verts.extend([v0, v1])

            edge_dir = ((v1.co - v0.co) * V(1, 1, 0)).normalized()
            ortho_vector = edge_dir.cross(V(0, 0, 1))

            extruded_geom = bmesh.ops.extrude_edge_only(bm, edges=[main_edge])["geom"]
            extruded_verts = bm_sort_out_geom(extruded_geom)["verts"]
            bmesh.ops.translate(bm, vec=ortho_vector * (-thickness / 2), verts=extruded_verts)

            extruded_geom = bmesh.ops.extrude_edge_only(bm, edges=[main_edge])["geom"]
            extruded_verts = bm_sort_out_geom(extruded_geom)["verts"]
            bmesh.ops.translate(bm, vec=ortho_vector * (thickness / 2), verts=extruded_verts)

            # dissolve middle edge
            bmesh.ops.dissolve_edges(bm, edges=[main_edge])

        # height
        extruded_geom = bmesh.ops.extrude_face_region(bm, geom=bm.faces)["geom"]
        extruded_verts = bm_sort_out_geom(extruded_geom)["verts"]
        extrusion_vector = Vector((0, 0, 1)) * height
        bmesh.ops.translate(bm, vec=extrusion_vector, verts=extruded_verts)

        # dissolve middle edges
        edges_to_dissolve = []
        verts_to_dissolve = []
        for v in edge_dissolving_verts:
            for e in v.link_edges:
                other_vert = e.other_vert(v)
                if other_vert in extruded_verts:
                    edges_to_dissolve.append(e)
                    verts_to_dissolve.append(other_vert)
        bmesh.ops.dissolve_edges(bm, edges=edges_to_dissolve)
        bmesh.ops.dissolve_verts(bm, verts=verts_to_dissolve)
        # to remove unnecessary verts in 0 spacing case
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0001)

        bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])

        tool.Blender.apply_bmesh(obj.data, bm)

    generate_frameless_panel_railing()


def get_path_data(obj: bpy.types.Object) -> dict[str, Any]:
    si_conversion = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())

    bm = tool.Blender.get_bmesh_for_mesh(obj.data)

    if not bm.verts or not bm.edges:
        return

    end_points = [v for v in bm.verts if len(v.link_edges) == 1]
    looped = not end_points

    # TODO: check with previous data
    # if we have some previous data then we try to match
    # start or end of the path with the previous path
    previous_data = False
    if previous_data:
        previous_start = previous_data[0]
        previous_end = previous_data[-1]

        potential_start = min([(v, (v.co - previous_start).length) for v in end_points], key=lambda v_data: v_data[1])
        potential_end = min([(v, (v.co - previous_end).length) for v in end_points], key=lambda v_data: v_data[1])

        if potential_start[1] < potential_end[1]:
            start_point = potential_start[0]
        else:
            start_point = next(v for v in end_points if v != potential_start[0])
    elif not looped:
        start_point = min(end_points, key=lambda v: v.index)
    elif looped:
        start_point = bm.verts[:][0]

    # walking through the path
    # to make sure all verts are in consequent order
    edge = start_point.link_edges[0]
    v = edge.other_vert(start_point)
    points = [start_point.co, v.co]
    segments = [(0, 1)]
    i = 2

    other_edge = lambda edges, edge: next(e for e in edges if e != edge)

    while len(link_edges := v.link_edges) != 1:
        prev_v = v

        edge = other_edge(link_edges, edge)
        v = edge.other_vert(prev_v)

        if looped and v == start_point:
            segments.append((i - 1, 0))
            break

        # skip path verts if they just go vertical to avoid errors
        if (v.co.xy - prev_v.co.xy).length <= 0.0001:
            continue

        points.append(v.co)
        segments.append((i - 1, i))
        i += 1

    path_data = {"edges": segments, "verts": [p / si_conversion for p in points]}

    return path_data


class BIM_OT_add_railing(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "mesh.add_railing"
    bl_label = "Railing"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return tool.Ifc.get() and context.mode == "OBJECT"

    def _execute(self, context):
        ifc_file = tool.Ifc.get()
        if not ifc_file:
            self.report({"ERROR"}, "You need to start IFC project first to create a railing.")
            return {"CANCELLED"}

        if context.active_object is not None:
            spawn_location = context.active_object.location.copy()
            context.active_object.select_set(False)
        else:
            spawn_location = bpy.context.scene.cursor.location.copy()

        mesh = bpy.data.meshes.new("IfcRailing")
        obj = bpy.data.objects.new("IfcRailing", mesh)
        obj.location = spawn_location

        body_context = ifcopenshell.util.representation.get_context(ifc_file, "Model", "Body", "MODEL_VIEW")
        bonsai.core.root.assign_class(
            tool.Ifc,
            tool.Collector,
            tool.Root,
            obj=obj,
            ifc_class="IfcRailing",
            should_add_representation=True,
            context=body_context,
        )
        bpy.ops.object.select_all(action="DESELECT")
        bpy.context.view_layer.objects.active = None
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.bim.add_railing()
        return {"FINISHED"}


# UI operators
class AddRailing(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_railing"
    bl_label = "Add Railing"
    bl_description = "Add Bonsai parametric railing to the active IFC element"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        obj = context.active_object
        element = tool.Ifc.get_entity(obj)
        props = obj.BIMRailingProperties
        si_conversion = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())

        railing_data = props.get_general_kwargs(convert_to_project_units=True)
        path_data = get_path_data(obj)

        # NOTE: will occur only on meshes without edges or verts
        if not path_data:
            path_data = {
                "edges": [[0, 1], [1, 2]],
                "verts": [
                    Vector([-1.0, 0.0, 0.0]) / si_conversion,
                    Vector([0.0, 0.0, 0.0]) / si_conversion,
                    Vector([1.0, 0.0, 0.0]) / si_conversion,
                ],
            }
        railing_data["path_data"] = path_data

        update_bbim_railing_pset(element, railing_data)
        refresh()
        update_railing_modifier_bmesh(context)
        update_railing_modifier_ifc_data(context)
        tool.Model.add_body_representation(obj)


class EnableEditingRailing(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.enable_editing_railing"
    bl_label = "Enable Editing Railing"
    bl_options = {"REGISTER"}

    def _execute(self, context):
        obj = context.active_object
        props = obj.BIMRailingProperties
        data = tool.Model.get_modeling_bbim_pset_data(obj, "BBIM_Railing")["data_dict"]
        data["path_data"] = json.dumps(data["path_data"])

        # required since we could load pset from .ifc and BIMRailingProperties won't be set
        props.set_props_kwargs_from_ifc_data(data)

        props.is_editing = True
        return {"FINISHED"}


class CancelEditingRailing(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.cancel_editing_railing"
    bl_label = "Cancel Editing Railing"
    bl_options = {"REGISTER"}

    def _execute(self, context):
        obj = context.active_object
        data = tool.Model.get_modeling_bbim_pset_data(obj, "BBIM_Railing")["data_dict"]
        props = obj.BIMRailingProperties

        # restore previous settings since editing was canceled
        props.set_props_kwargs_from_ifc_data(data)
        update_railing_modifier_bmesh(context)

        props.is_editing = False
        return {"FINISHED"}


class FinishEditingRailing(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.finish_editing_railing"
    bl_label = "Finish Editing Railing"
    bl_options = {"REGISTER"}

    def _execute(self, context):
        obj = context.active_object
        element = tool.Ifc.get_entity(obj)
        props = obj.BIMRailingProperties

        pset_data = tool.Model.get_modeling_bbim_pset_data(bpy.context.active_object, "BBIM_Railing")
        path_data = pset_data["data_dict"]["path_data"]

        railing_data = props.get_general_kwargs(convert_to_project_units=True)
        railing_data["path_data"] = path_data
        props.is_editing = False

        update_bbim_railing_pset(element, railing_data)
        update_railing_modifier_ifc_data(context)
        return {"FINISHED"}


class FlipRailingPathOrder(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.flip_railing_path_order"
    bl_label = "Flip Railing Path Order"
    bl_description = "Can be useful to maintain railing supports direction"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        obj = context.active_object
        element = tool.Ifc.get_entity(obj)
        props = obj.BIMRailingProperties

        pset_data = tool.Model.get_modeling_bbim_pset_data(bpy.context.active_object, "BBIM_Railing")
        path_data = pset_data["data_dict"]["path_data"]

        # flip the vertex order and edges
        path_data["verts"] = path_data["verts"][::-1]
        last_vert_i = len(path_data["verts"]) - 1
        edges = []
        for edge in path_data["edges"][::-1]:
            edge = [abs(vi - last_vert_i) for vi in edge[::-1]]
            edges.append(edge)

        railing_data = props.get_general_kwargs(convert_to_project_units=True)
        railing_data["path_data"] = path_data

        update_bbim_railing_pset(element, railing_data)
        update_railing_modifier_ifc_data(context)
        return {"FINISHED"}


class EnableEditingRailingPath(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.enable_editing_railing_path"
    bl_label = "Edit Railing"
    bl_description = "Enable Editing Railing Path"
    bl_options = {"REGISTER"}

    def _execute(self, context):
        obj = context.active_object
        [o.select_set(False) for o in context.selected_objects if o != obj]
        props = obj.BIMRailingProperties
        data = tool.Model.get_modeling_bbim_pset_data(obj, "BBIM_Railing")["data_dict"]
        # required since we could load pset from .ifc and BIMRoofProperties won't be set
        props.set_props_kwargs_from_ifc_data(data)

        props.is_editing_path = True
        update_railing_modifier_bmesh(context)

        if bpy.context.active_object.mode != "EDIT":
            bpy.ops.object.mode_set(mode="EDIT")
        tool.Blender.set_viewport_tool("bim.cad_tool")
        ProfileDecorator.install(context, exit_edit_mode_callback=lambda: cancel_editing_railing_path(context))
        return {"FINISHED"}


def cancel_editing_railing_path(context: bpy.types.Context) -> set[str]:
    obj = context.active_object
    props = obj.BIMRailingProperties

    ProfileDecorator.uninstall()
    props.is_editing_path = False

    if bpy.context.active_object.mode == "EDIT":
        bpy.ops.object.mode_set(mode="OBJECT")

    if props.railing_type == "FRAMELESS_PANEL":
        update_railing_modifier_bmesh(context)
    else:
        element = tool.Ifc.get_entity(obj)
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

    return {"FINISHED"}


class CancelEditingRailingPath(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.cancel_editing_railing_path"
    bl_label = "Cancel Editing Railing Path"
    bl_options = {"REGISTER"}

    def _execute(self, context):
        return cancel_editing_railing_path(context)


class FinishEditingRailingPath(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.finish_editing_railing_path"
    bl_label = "Finish Editing Railing Path"
    bl_options = {"REGISTER"}

    def _execute(self, context):
        obj = context.active_object
        element = tool.Ifc.get_entity(obj)
        props = obj.BIMRailingProperties

        railing_data = props.get_general_kwargs(convert_to_project_units=True)
        path_data = get_path_data(obj)
        railing_data["path_data"] = path_data
        ProfileDecorator.uninstall()
        props.is_editing_path = False

        update_bbim_railing_pset(element, railing_data)
        # RailingData has to be updated before run update_railing_modifier_bmesh
        # since we know that BBIM_Railing could have changed
        refresh()
        update_railing_modifier_bmesh(context)
        if bpy.context.active_object.mode == "EDIT":
            bpy.ops.object.mode_set(mode="OBJECT")
        update_railing_modifier_ifc_data(context)
        return {"FINISHED"}


class RemoveRailing(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_railing"
    bl_label = "Remove Railing"
    bl_options = {"REGISTER"}

    def _execute(self, context):
        obj = context.active_object
        element = tool.Ifc.get_entity(obj)
        obj.BIMRailingProperties.is_editing = False

        pset = tool.Pset.get_element_pset(element, "BBIM_Railing")
        ifcopenshell.api.run("pset.remove_pset", tool.Ifc.get(), product=element, pset=pset)
        return {"FINISHED"}
