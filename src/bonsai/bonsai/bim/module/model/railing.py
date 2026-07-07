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


import json
import math
from typing import Any

import bmesh
import bpy
import ifcopenshell
import ifcopenshell.api.geometry
import ifcopenshell.api.pset
import ifcopenshell.util.representation
import ifcopenshell.util.unit
from mathutils import Matrix, Vector

import bonsai.core.geometry
import bonsai.core.root
import bonsai.tool as tool
from bonsai.bim.module.drawing import gizmos as gizmo
from bonsai.bim.module.drawing.gizmos import DimensionGizmoConfig
from bonsai.bim.module.model import prop
from bonsai.bim.module.model.data import RailingData, refresh
from bonsai.bim.module.model.decorator import ProfileDecorator
from bonsai.bim.parametric_lifecycle import (
    CycleTypeMixin,
    PathPreservingEditMixin,
    PickTypeMixin,
)
from bonsai.tool.cad import WELD_TOLERANCE

V_ = tool.Blender.V_

# reference:
# https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcRailing.htm
# https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcRailingType.htm


def bm_split_edge_at_offset(edge: bmesh.types.BMEdge, offset: float) -> dict[str, Any]:
    v0, v1 = edge.verts

    offset = offset / 2
    edge_len = (v0.co - v1.co).xy.length

    split_output_0 = bmesh.utils.edge_split(edge, v0, offset / edge_len)
    split_output_1 = bmesh.utils.edge_split(edge, v1, offset / (edge_len - offset))
    new_geometry = tool.Model.bm_sort_out_geom(split_output_0 + split_output_1)
    return new_geometry


def update_railing_modifier_ifc_data(context: bpy.types.Context) -> None:
    """should be called after new geometry settled
    since it's going to update ifc representation
    """
    obj = context.active_object
    assert obj
    props = tool.Model.get_railing_props(obj)
    element = tool.Ifc.get_entity(obj)
    assert element
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
        pset_common = ifcopenshell.api.pset.add_pset(ifc_file, product=element, name="Pset_RailingCommon")

    ifcopenshell.api.pset.edit_pset(
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
        model_representation = ifcopenshell.api.geometry.add_railing_representation(ifc_file, **representation_data)
        tool.Model.replace_object_ifc_representation(body, obj, model_representation)

        # recalculate normals to ensure correct shading
        mesh = obj.data
        if isinstance(mesh, bpy.types.Mesh):
            bm = tool.Blender.get_bmesh_for_mesh(mesh, clean=False)
            bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
            tool.Blender.apply_bmesh(mesh, bm)

    elif props.railing_type == "FRAMELESS_PANEL":
        tool.Model.add_body_representation(obj)


def update_bbim_railing_pset(element: ifcopenshell.entity_instance, railing_data: dict[str, Any]) -> None:
    pset = tool.Pset.get_element_pset(element, "BBIM_Railing")
    if not pset:
        pset = ifcopenshell.api.pset.add_pset(tool.Ifc.get(), product=element, name="BBIM_Railing")
    railing_data = tool.Ifc.get().createIfcText(json.dumps(railing_data, default=list))
    ifcopenshell.api.pset.edit_pset(tool.Ifc.get(), pset=pset, properties={"Data": railing_data})


def generate_wall_mounted_handrail_preview(
    obj: bpy.types.Object,
    props: "prop.BIMRailingProperties",
    path_data: dict[str, Any],
    si_conversion: float,
) -> None:
    """Viewport-only WALL_MOUNTED_HANDRAIL preview: rebuild ``obj.data`` from the same
    geometry helper the IFC representation builder uses, without writing any IFC."""
    railing_path = [Vector(v) * si_conversion for v in path_data["verts"]]
    looped_path = path_data["edges"][-1][-1] == path_data["edges"][0][0]

    geom = ifcopenshell.api.geometry.compute_wall_mounted_handrail_geometry(
        railing_path=railing_path,
        support_spacing=props.support_spacing,
        railing_diameter=props.railing_diameter,
        clear_width=props.clear_width,
        height=props.height,
        use_manual_supports=props.use_manual_supports,
        terminal_type=props.terminal_type,
        looped_path=looped_path,
        unit_scale=1.0,  # props are already SI; bypass the IFC project-units conversion
    )

    bm = tool.Blender.get_bmesh_for_mesh(obj.data, clean=True)

    tool.Cad.sweep_disk_along_polyline(
        bm,
        [Vector(p) for p in geom.handrail_polyline],
        geom.handrail_radius,
        arc_indices=geom.handrail_arc_point_indices,
    )

    for support in geom.supports:
        tool.Cad.sweep_disk_along_polyline(
            bm,
            [Vector(p) for p in support.arc_polyline],
            support.arc_radius,
        )
        tool.Cad.add_disk_extrusion(
            bm,
            Vector(support.disk_position),
            support.disk_radius,
            support.disk_depth,
            support.disk_z_rotation,
        )

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    tool.Blender.apply_bmesh(obj.data, bm)


def update_railing_modifier_bmesh(context: bpy.types.Context) -> None:
    """before using should make sure that Data contains up-to-date information.
    If BBIM Pset just changed should call refresh() before updating bmesh
    """
    obj = context.active_object
    assert obj
    props = tool.Model.get_railing_props(obj)
    V_ = tool.Blender.V_

    # NOTE: using Data since bmesh update will hapen very often
    if not RailingData.is_loaded:
        RailingData.load()
    path_data = RailingData.data["path_data"]

    si_conversion = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())

    # WALL_MOUNTED_HANDRAIL renders the preview from the compute helper; IFC stays
    # untouched until Finish Editing rebuilds the representation.
    if not props.is_editing_path and props.railing_type == "WALL_MOUNTED_HANDRAIL":
        generate_wall_mounted_handrail_preview(obj, props, path_data, si_conversion)
        return

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

            edge_dir = ((v1.co - v0.co) * V_(1, 1, 0)).normalized()
            ortho_vector = edge_dir.cross(V_(0, 0, 1))

            extruded_geom = bmesh.ops.extrude_edge_only(bm, edges=[main_edge])["geom"]
            extruded_verts = tool.Model.bm_sort_out_geom(extruded_geom)["verts"]
            bmesh.ops.translate(bm, vec=ortho_vector * (-thickness / 2), verts=extruded_verts)

            extruded_geom = bmesh.ops.extrude_edge_only(bm, edges=[main_edge])["geom"]
            extruded_verts = tool.Model.bm_sort_out_geom(extruded_geom)["verts"]
            bmesh.ops.translate(bm, vec=ortho_vector * (thickness / 2), verts=extruded_verts)

            # dissolve middle edge
            bmesh.ops.dissolve_edges(bm, edges=[main_edge])

        # height
        extruded_geom = bmesh.ops.extrude_face_region(bm, geom=bm.faces)["geom"]
        extruded_verts = tool.Model.bm_sort_out_geom(extruded_geom)["verts"]
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
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=WELD_TOLERANCE)

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

        # Vertical-only segments project to a degenerate XY edge; skip to avoid divide-by-zero downstream.
        if (v.co.xy - prev_v.co.xy).length <= WELD_TOLERANCE:
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
        tool.Blender.select_object(obj)
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
        assert obj
        element = tool.Ifc.get_entity(obj)
        assert element
        props = tool.Model.get_railing_props(obj)
        si_conversion = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())

        tool.Blender.get_addon_preferences().default_parameters.railing.copy_to(props)

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


class CopyRailingParameters(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.copy_railing_parameters"
    bl_label = "Copy Railing Parameters from Active to Selected"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if not context.active_object or len(context.selected_objects) < 1:
            cls.poll_message_set("At least 2 objects must be selected.")
            return False
        return True

    def _execute(self, context):
        source_obj = context.active_object
        assert source_obj
        source_props = tool.Model.get_railing_props(source_obj)
        railing_data = source_props.get_general_kwargs(convert_to_project_units=True)

        for target_obj in context.selected_objects:
            if target_obj == source_obj:
                continue
            context.view_layer.objects.active = target_obj
            RailingData.load()
            if not "path_data" in RailingData.data:
                continue
            railing_data["path_data"] = RailingData.data["path_data"]
            target_element = tool.Ifc.get_entity(target_obj)
            assert target_element
            target_props = tool.Model.get_railing_props(target_obj)

            target_props.set_props_kwargs_from_ifc_data(railing_data)
            update_bbim_railing_pset(target_element, railing_data)
            refresh()
            update_railing_modifier_bmesh(context)
            update_railing_modifier_ifc_data(context)

        context.view_layer.objects.active = source_obj
        return {"FINISHED"}


class _RailingEditMixin(PathPreservingEditMixin):
    """Single-object (active_object) railing-edit hooks; path_data is preserved
    through the edit (path editing is a separate operator family)."""

    pset_name = "BBIM_Railing"

    @classmethod
    def _is_element_type(cls, element):
        return tool.Parametric.is_railing(element)

    @classmethod
    def _get_props(cls, obj: bpy.types.Object):
        return tool.Model.get_railing_props(obj)

    @classmethod
    def _post_load_data(cls, data: dict) -> dict:
        # BIMRailingProperties.path_data is a StringProperty holding JSON.
        data["path_data"] = json.dumps(data["path_data"])
        return data

    @classmethod
    def _update_pset(cls, element, data: dict) -> None:
        update_bbim_railing_pset(element, data)

    @classmethod
    def _update_modifier_ifc_data(cls, obj: bpy.types.Object, context: bpy.types.Context) -> None:
        update_railing_modifier_ifc_data(context)

    @classmethod
    def _restore_viewport_after_cancel(cls, obj: bpy.types.Object, context: bpy.types.Context) -> None:
        """WALL_MOUNTED_HANDRAIL reloads the committed Body; others rebuild the preview bmesh."""
        props = tool.Model.get_railing_props(obj)
        if props.railing_type == "WALL_MOUNTED_HANDRAIL":
            element = tool.Ifc.get_entity(obj)
            assert element
            body = ifcopenshell.util.representation.get_representation(element, "Model", "Body", "MODEL_VIEW")
            if body:
                bonsai.core.geometry.switch_representation(
                    tool.Ifc,
                    tool.Geometry,
                    obj=obj,
                    representation=body,
                )
            return
        update_railing_modifier_bmesh(context)


class EnableEditingRailing(_RailingEditMixin, bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.enable_editing_railing"
    bl_label = "Enable Editing Railing"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        return self._enable_targets(context)


class CancelEditingRailing(_RailingEditMixin, bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.cancel_editing_railing"
    bl_label = "Cancel Editing Railing"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        return self._cancel_targets(context)


class FinishEditingRailing(_RailingEditMixin, bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.finish_editing_railing"
    bl_label = "Finish Editing Railing"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        return self._finish_targets(context)


class CycleRailingType(bpy.types.Operator, tool.Ifc.Operator, CycleTypeMixin):
    """Cycle railing_type (FRAMELESS_PANEL ↔ WALL_MOUNTED_HANDRAIL). Shift+click reverses."""

    bl_idname = "bim.cycle_railing_type"
    bl_label = "Cycle Railing Type"
    bl_options = {"REGISTER", "UNDO"}

    element_checker = tool.Parametric.is_railing
    props_getter = tool.Model.get_railing_props
    type_literal = tool.Model.RailingType
    type_attr = "railing_type"

    def _execute(self, context: bpy.types.Context) -> set[str]:
        return self._cycle_type(context)


class ToggleRailingUseManualSupports(bpy.types.Operator):
    """Flip use_manual_supports on the active WALL_MOUNTED_HANDRAIL railing.

    No-op unless a parametric edit is active and the railing is wall-mounted.
    """

    bl_idname = "bim.toggle_railing_use_manual_supports"
    bl_label = "Toggle Railing Manual Supports"
    bl_description = "Switch between automatic support spacing and manual per-vertex placement"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        resolved = tool.Model.resolve_active_props_for_edit(
            context,
            tool.Model.get_railing_props,
            subtype=("railing_type", "WALL_MOUNTED_HANDRAIL"),
        )
        if resolved is None:
            return {"CANCELLED"}
        _obj, props = resolved
        props.use_manual_supports = not props.use_manual_supports
        return {"FINISHED"}


class PickRailingTerminalType(bpy.types.Operator, tool.Ifc.Operator, PickTypeMixin):
    """Pick ``terminal_type`` for the active WALL_MOUNTED_HANDRAIL railing."""

    bl_idname = "bim.pick_railing_terminal_type"
    bl_label = "Pick Railing Terminal Type"
    bl_description = "Pick the cap geometry applied at the rail ends"
    bl_options = {"REGISTER", "UNDO"}

    skip_element_check = True
    props_getter = tool.Model.get_railing_props
    type_literal = prop.CapType
    type_attr = "terminal_type"

    def _execute(self, context: bpy.types.Context) -> set[str]:
        if (
            tool.Model.resolve_active_props_for_edit(
                context,
                tool.Model.get_railing_props,
                subtype=("railing_type", "WALL_MOUNTED_HANDRAIL"),
            )
            is None
        ):
            return {"CANCELLED"}
        return self._pick_type(context)


def _format_attr_distance(attr_name: str):
    """text_formatter that renders the named property as a distance, ignoring the
    dimension's visible-length argument (which is fixed for schematic gizmos)."""
    return lambda p, _v: tool.Unit.format_distance(getattr(p, attr_name))


class GizmoRailingSchematic(bpy.types.GizmoGroup, gizmo.BaseSchematicGizmoGroup):
    """Schematic-frame parametric editor for railings. Mutually exclusive with path-edit mode."""

    bl_idname = "OBJECT_GGT_bim_railing_edition"
    bl_label = "Railing Editing Gizmo"
    bl_space_type = "VIEW_3D"
    bl_region_type = "WINDOW"
    bl_options = {"3D", "PERSISTENT"}

    enable_editing_operator = "bim.enable_editing_railing"
    finish_editing_operator = "bim.finish_editing_railing"
    cancel_editing_operator = "bim.cancel_editing_railing"
    cycle_type_operator = "bim.cycle_railing_type"

    props_getter = tool.Model.get_railing_props
    gizmo_pref_name = "railing"

    # Schematic-local layout. +X → screen RIGHT, +Y → screen UP, +Z → toward viewer
    # (post billboard rotation). Each dimension is anchored alongside the feature it
    # measures so the label, not the bar length, carries the value.
    SCHEMATIC_MESH_HEIGHT_FRAC = 0.9  # Mesh top edge in schematic-local +Y
    SCHEMATIC_MESH_WIDTH_FRAC = 0.7  # Mesh side edges in schematic-local ±X
    SCHEMATIC_MESH_RAIL_Y_FRAC = SCHEMATIC_MESH_HEIGHT_FRAC / 2  # WALL_MOUNTED_HANDRAIL rail centreline
    SCHEMATIC_MESH_DEPTH_FRAC = 0.06  # Panel depth — small so the schematic reads as slabs not boxes
    # WALL_MOUNTED_HANDRAIL dimensions — fractions of schematic_box_size so they
    # scale with the host group's box size.
    SCHEMATIC_RAIL_RADIUS_FRAC = 0.05
    SCHEMATIC_RAIL_CLEAR_FRAC = 0.5  # Stylised — wider than real-world for visible bracket arm
    SCHEMATIC_RAIL_INSET_FRAC = 0.08  # Wall extends past the outermost support on both sides

    @classmethod
    def schematic_rail_radius(cls) -> float:
        return cls.schematic_box_size * cls.SCHEMATIC_RAIL_RADIUS_FRAC

    @classmethod
    def schematic_rail_clear(cls) -> float:
        return cls.schematic_box_size * cls.SCHEMATIC_RAIL_CLEAR_FRAC

    # Axonometric 3/4 view: +Z projects down-and-left so the depth axis
    # is visibly separated from the back face. Without the X tilt, panel
    # thickness (schematic-local Z) collapses to a near-horizontal bar.
    schematic_view_rotation = Matrix.Rotation(math.radians(20), 4, "X") @ Matrix.Rotation(math.radians(-25), 4, "Y")

    # Hover a dimension → highlight the schematic edges tagged with the matching feature.
    # Tags are written by the mesh builders. "spacing" is empty space (no edges) so it's
    # absent from this map and gracefully no-ops on hover.
    schematic_attr_to_feature = {
        "height": "panel_height",
        "thickness": "panel_thickness",
        "railing_diameter": "rail_tube",
        "clear_width": "bracket",
        "support_spacing": "bracket",
    }

    schematic_dimension_props = [
        # ── FRAMELESS_PANEL ─────────────────────────────────────────────
        DimensionGizmoConfig(
            attr_name="height",
            axis=(0, 1, 0),
            min_value=0.01,
            # Gated to FRAMELESS_PANEL: in WALL_MOUNTED_HANDRAIL, height only
            # feeds TO_FLOOR / TO_END_POST_AND_FLOOR terminals so dragging it
            # is a no-op under the default "180" terminal.
            visibility_condition=lambda p: p.railing_type == "FRAMELESS_PANEL",
            matrix_position=lambda p: Vector((-GizmoRailingSchematic.SCHEMATIC_MESH_WIDTH_FRAC / 2 - 0.08, 0.0, 0.0)),
            schematic_visible_length=SCHEMATIC_MESH_HEIGHT_FRAC,
            text_formatter=_format_attr_distance("height"),
        ),
        DimensionGizmoConfig(
            attr_name="thickness",
            axis=(0, 0, 1),  # panel depth — projects to a true depth direction under the 3/4 tilt
            min_value=0.005,
            visibility_condition=lambda p: p.railing_type == "FRAMELESS_PANEL",
            matrix_position=lambda p: Vector(
                (
                    (
                        -GizmoRailingSchematic.SCHEMATIC_MESH_WIDTH_FRAC / 2
                        - GizmoRailingSchematic.SCHEMATIC_MESH_GAP_HALF_WIDTH
                    )
                    / 2,
                    GizmoRailingSchematic.SCHEMATIC_MESH_HEIGHT_FRAC + 0.05,
                    -GizmoRailingSchematic.SCHEMATIC_MESH_DEPTH_FRAC / 2,
                )
            ),
            schematic_visible_length=0.4,  # longer than default to survive depth foreshortening
            text_formatter=_format_attr_distance("thickness"),
        ),
        DimensionGizmoConfig(
            attr_name="spacing",
            axis=(1, 0, 0),
            min_value=0.0,  # zero-spacing collapses the picket gap into a single continuous panel
            visibility_condition=lambda p: p.railing_type == "FRAMELESS_PANEL",
            matrix_position=lambda p: Vector((0.0, -0.1, 0.0)),
            text_formatter=_format_attr_distance("spacing"),
        ),
        # ── WALL_MOUNTED_HANDRAIL ──────────────────────────────────────
        DimensionGizmoConfig(
            attr_name="railing_diameter",
            axis=(0, 1, 0),
            min_value=0.001,
            visibility_condition=lambda p: p.railing_type == "WALL_MOUNTED_HANDRAIL",
            matrix_position=lambda p: Vector(
                (
                    -GizmoRailingSchematic.SCHEMATIC_MESH_WIDTH_FRAC / 2 - 0.05,
                    GizmoRailingSchematic.SCHEMATIC_MESH_RAIL_Y_FRAC - 0.09,
                    GizmoRailingSchematic.schematic_rail_clear(),
                )
            ),
            text_formatter=_format_attr_distance("railing_diameter"),
        ),
        DimensionGizmoConfig(
            attr_name="clear_width",
            axis=(0, 0, 1),  # +Z is the wall-to-rail perpendicular axis under the 3/4 tilt
            min_value=0.001,
            visibility_condition=lambda p: p.railing_type == "WALL_MOUNTED_HANDRAIL",
            matrix_position=lambda p: Vector(
                (
                    0.0,
                    GizmoRailingSchematic.SCHEMATIC_MESH_RAIL_Y_FRAC,
                    0.0,
                )
            ),
            schematic_visible_length=0.36,  # 2× default so the call-out survives depth projection
            text_formatter=_format_attr_distance("clear_width"),
        ),
        DimensionGizmoConfig(
            attr_name="support_spacing",
            axis=(1, 0, 0),
            min_value=0.05,
            visibility_condition=lambda p: (p.railing_type == "WALL_MOUNTED_HANDRAIL" and not p.use_manual_supports),
            matrix_position=lambda p: Vector(
                (
                    -GizmoRailingSchematic.SCHEMATIC_MESH_WIDTH_FRAC / 2
                    + GizmoRailingSchematic.SCHEMATIC_RAIL_INSET_FRAC,
                    -0.18,
                    0.0,
                )
            ),
            # Bare names (not Gizmo…SCHEMATIC_…) because the class is still under construction here.
            schematic_visible_length=SCHEMATIC_MESH_WIDTH_FRAC - 2 * SCHEMATIC_RAIL_INSET_FRAC,
            text_formatter=_format_attr_distance("support_spacing"),
        ),
    ]

    @classmethod
    def is_element_type(cls, element: ifcopenshell.entity_instance) -> bool:
        return tool.Parametric.is_railing(element)

    @classmethod
    def schematic_cache_key(cls, props) -> tuple:
        """Cache the schematic mesh by ``railing_type`` — proportions are fixed
        per type, so the bmesh build runs at most twice across a session
        (once for ``FRAMELESS_PANEL``, once for ``WALL_MOUNTED_HANDRAIL``)
        rather than once per draw call."""
        return (props.railing_type,)

    def setup_element_specific_gizmos(self, context: bpy.types.Context) -> None:
        """Create the WALL_MOUNTED_HANDRAIL-only affordances on the schematic.

        Two static lock glyphs (open/closed) for toggling
        ``use_manual_supports``: instantiate both and let the per-frame state
        query pick which one to show. State-aware icons use a static pair
        rather than a single dynamic gizmo to avoid ``prop_path`` resolution
        in the render path.

        Plus a cycle-glyph at the rail end that opens the ``terminal_type``
        popup when clicked.
        """
        default_color, highlight_color = self.get_decoration_colors()

        self.lock_open_gizmo, self.lock_closed_gizmo = self.create_icon_gizmo_lock_pair(
            "bim.toggle_railing_use_manual_supports",
            open_color=default_color,
        )

        self.terminal_gizmo = self.gizmos.new("VIEW3D_GT_menu")
        self.terminal_gizmo.color = default_color
        self.terminal_gizmo.color_highlight = highlight_color
        self.terminal_gizmo.use_draw_scale = False
        self.terminal_gizmo.alpha = 0.8
        self.terminal_gizmo.target_set_operator("bim.pick_railing_terminal_type")

    def _refresh_element_specific(self, context: bpy.types.Context, mw: "Matrix", props) -> None:
        """Position and gate the WALL_MOUNTED_HANDRAIL-only gizmos.

        - Lock glyphs: only WALL_MOUNTED_HANDRAIL while editing. Show
          ``lock_open`` when ``use_manual_supports`` is True, the closed
          padlock when False ("auto-spacing is locked to support_spacing").
        - Terminal gizmo: same gating, positioned just past the right rail
          end so it reads as "configure the rail's end cap".
        """
        super()._refresh_element_specific(context, mw, props)

        # ``draw_prepare`` can fire on a freshly recreated GizmoGroup instance
        # before ``setup_element_specific_gizmos`` has populated the lock /
        # terminal attributes (Blender 5.x recreates per-region groups on
        # reload). Bail out cheaply; the next refresh after setup completes
        # will reposition them correctly.
        if not hasattr(self, "lock_open_gizmo"):
            return

        # Single gate for all WALL_MOUNTED_HANDRAIL extras.
        active = props.is_editing and not props.is_editing_path and props.railing_type == "WALL_MOUNTED_HANDRAIL"

        if not active:
            self.lock_open_gizmo.hide = True
            self.lock_closed_gizmo.hide = True
            self.terminal_gizmo.hide = True
            return

        billboard_rot = self._frame_billboard_rot
        view_rotation = self.schematic_view_rotation
        anchor = self._compute_schematic_anchor(props, mw, billboard_rot)

        # ── Lock glyphs for use_manual_supports ──────────────────────────
        # Sit just above the wall's bottom line, near the centre of the
        # schematic — visually grouped with the dimension it controls
        # (support_spacing) without overlapping the arrow tail below.
        is_manual = bool(props.use_manual_supports)
        self.lock_open_gizmo.hide = not is_manual
        self.lock_closed_gizmo.hide = is_manual
        lock_local = Vector((0.0, 0.05, 0.0))
        lock_world = anchor + billboard_rot @ view_rotation @ lock_local
        lock_matrix = gizmo.billboarded_at(lock_world, billboard_rot, 0.09)
        self.lock_open_gizmo.matrix_basis = lock_matrix
        self.lock_closed_gizmo.matrix_basis = lock_matrix

        # ── Terminal-type popup gizmo at the right rail end ──────────────
        # Pushed well past the right wall edge so the icon doesn't crowd
        # the wall outline or the bracket attach point. At rail height and
        # rail depth so it reads as "attached to the rail terminal".
        self.terminal_gizmo.hide = False
        terminal_local = Vector(
            (
                self.SCHEMATIC_MESH_WIDTH_FRAC / 2 + 0.25,
                self.SCHEMATIC_MESH_RAIL_Y_FRAC,
                self.schematic_rail_clear(),
            )
        )
        terminal_world = anchor + billboard_rot @ view_rotation @ terminal_local
        self.terminal_gizmo.matrix_basis = gizmo.billboarded_at(terminal_world, billboard_rot, 0.18)

    def update_editing_gizmos(
        self, context: bpy.types.Context, mw: "Matrix", props: "prop.BIMRailingProperties"
    ) -> None:
        """Hide the pen gizmo while polyline path-edit is active; reposition the cycle icon.

        The base class shows the pen gizmo whenever ``is_editing`` is False,
        which is the case during path-edit too. Allowing the user to click
        through into parametric edit while the polyline mesh is open in EDIT
        mode mixes two distinct editing states and leaves a stale draft if
        they cancel out — block the entry point instead. The operator itself
        is intentionally not guarded (callers via scripting can still invoke
        it); this is the UX-level enforcement.

        The cycle icon defaults to the editing icon row (next to validate /
        cancel) via the parent's positioning. We move it to just above the
        schematic mesh so it reads as "cycle the railing type *shown here*"
        — associated with the preview the user is interacting with, not a
        generic editing button at the bottom of the schematic.
        """
        super().update_editing_gizmos(context, mw, props)
        if props.is_editing_path:
            self.pen_gizmo.hide = True

        if props.is_editing and not props.is_editing_path:
            billboard_rot = self._frame_billboard_rot
            view_rotation = self.schematic_view_rotation
            anchor = self._compute_schematic_anchor(props, mw, billboard_rot)
            # Comfortably above the mesh top edge so the icon doesn't crowd
            # the ``thickness`` / ``clear_width`` dimension callouts that
            # already sit just above the panel/wall.
            cycle_local = Vector((0.0, self.SCHEMATIC_MESH_HEIGHT_FRAC + 0.25, 0.0))
            world_pos = anchor + billboard_rot @ view_rotation @ cycle_local
            # 30% smaller than the editing-icon-row default (0.30 → 0.21):
            # the cycle is a tertiary affordance compared to pen/validate/cancel.
            self.cycle_gizmo.matrix_basis = gizmo.billboarded_at(world_pos, billboard_rot, 0.21)

    @classmethod
    def build_schematic_mesh(cls, props) -> "bmesh.types.BMesh":
        """Build a wireframe preview of the railing in schematic-local coordinates.

        FRAMELESS_PANEL renders as a box whose proportions track the bound
        properties (height / thickness / spacing); WALL_MOUNTED_HANDRAIL
        renders as a horizontal tube with two L-shaped supports whose
        proportions track railing_diameter / clear_width / support_spacing.
        Both are scaled to fit inside ``[-schematic_box_size, +schematic_box_size]``
        on each axis so the schematic reads the same regardless of absolute
        property values.

        The mesh is decorative — clicks land on the labeled sliders, not on
        the preview geometry. See ``BaseSchematicGizmoGroup`` for the
        draw-handler lifecycle.
        """
        bm = bmesh.new()
        if props.railing_type == "FRAMELESS_PANEL":
            cls._build_frameless_panel_schematic(bm, props)
        else:
            cls._build_wall_mounted_handrail_schematic(bm, props)
        return bm

    # Schematic-local half-width of the visible gap between the two panel boxes.
    # Conveys the "spacing" semantic at a glance — the user sees two pickets
    # separated by air, with the spacing dimension emerging from that gap.
    SCHEMATIC_MESH_GAP_HALF_WIDTH = 0.05

    @classmethod
    def _build_frameless_panel_schematic(cls, bm: "bmesh.types.BMesh", props) -> None:
        """Stylised panel: two wireframe boxes with a visible gap between them.

        The box edges sit at the ``SCHEMATIC_MESH_*_FRAC`` positions
        (matching where the dimension gizmos anchor), so each dimension line
        visually starts at the geometry feature it measures. Internal
        proportions are stable across drags — the actual values are shown
        through the dimension labels, while the schematic communicates
        which feature each label refers to. The gap between the two boxes
        (set by ``SCHEMATIC_MESH_GAP_HALF_WIDTH``) gives the "spacing"
        dimension a real visual referent.

        Edges are tagged on a string layer so hover-highlight can colour
        the geometric feature being measured: vertical edges → height,
        depth edges → thickness. The X-aligned edges along the panel
        width are untagged (they don't correspond to a single dimension).
        """
        hw = cls.SCHEMATIC_MESH_WIDTH_FRAC / 2
        hd = cls.SCHEMATIC_MESH_DEPTH_FRAC / 2
        h_top = cls.SCHEMATIC_MESH_HEIGHT_FRAC
        gap = cls.SCHEMATIC_MESH_GAP_HALF_WIDTH

        layer_name = cls.SCHEMATIC_FEATURE_LAYER_NAME
        feat_layer = bm.edges.layers.string.get(layer_name) or bm.edges.layers.string.new(layer_name)

        # Edge index → feature tag for one box. Order matches the (a, b)
        # tuple order below: bottom ring (4) + top ring (4) + verticals (4).
        edge_tags_per_box = (
            b"",  # (0,1) bottom-back, X-aligned
            b"panel_thickness",  # (1,2) bottom-right, Z-aligned
            b"",  # (2,3) bottom-front, X-aligned
            b"panel_thickness",  # (3,0) bottom-left, Z-aligned
            b"",  # (4,5) top-back, X-aligned
            b"panel_thickness",  # (5,6) top-right, Z-aligned
            b"",  # (6,7) top-front, X-aligned
            b"panel_thickness",  # (7,4) top-left, Z-aligned
            b"panel_height",  # (0,4) vertical back-left
            b"panel_height",  # (1,5) vertical back-right
            b"panel_height",  # (2,6) vertical front-right
            b"panel_height",  # (3,7) vertical front-left
        )

        # Build two separate wireframe boxes — one on each side of the central
        # gap. The boxes share the same Y range (0..h_top) and Z range (±hd)
        # but split the X range so the gap from -gap to +gap stays empty.
        for x_left, x_right in ((-hw, -gap), (gap, hw)):
            corners = [
                bm.verts.new((x_left, 0.0, -hd)),
                bm.verts.new((x_right, 0.0, -hd)),
                bm.verts.new((x_right, 0.0, hd)),
                bm.verts.new((x_left, 0.0, hd)),
                bm.verts.new((x_left, h_top, -hd)),
                bm.verts.new((x_right, h_top, -hd)),
                bm.verts.new((x_right, h_top, hd)),
                bm.verts.new((x_left, h_top, hd)),
            ]
            for tag, (a, b) in zip(
                edge_tags_per_box,
                (
                    (0, 1),
                    (1, 2),
                    (2, 3),
                    (3, 0),  # bottom ring
                    (4, 5),
                    (5, 6),
                    (6, 7),
                    (7, 4),  # top ring
                    (0, 4),
                    (1, 5),
                    (2, 6),
                    (3, 7),  # vertical edges
                ),
            ):
                edge = bm.edges.new((corners[a], corners[b]))
                if tag:
                    edge[feat_layer] = tag

    @classmethod
    def _build_wall_mounted_handrail_schematic(cls, bm: "bmesh.types.BMesh", props) -> None:
        """Stylised wall-mounted handrail: wall outline, hex tube, two L-brackets.

        Three visual elements convey "rail mounted on a wall":

        - **Wall outline** — a wireframe rectangle in the YZ plane at ``z=0``,
          extending slightly past the rail ends so the wall reads as a
          surface the rail is *attached to* rather than a coincident frame.
        - **Handrail tube** — a hexagonal cross-section extruded along ±X
          at ``z=+clear_s`` (in front of the wall), at ``y=rail_y``.
        - **L-shaped brackets** at each rail end — from the rail centreline
          drop a short distance, then run perpendicular back to the wall
          plane. Mirrors the standard wall-mount bracket geometry: a
          horizontal arm holding the rail off the wall, a vertical drop
          attaching to the rail.

        Like ``_build_frameless_panel_schematic``, the schematic uses fixed
        proportions so the dimension gizmos' anchor points stay aligned
        with the geometry features regardless of property values.
        """
        half_len = cls.SCHEMATIC_MESH_WIDTH_FRAC / 2
        wall_top = cls.SCHEMATIC_MESH_HEIGHT_FRAC
        rail_y = cls.SCHEMATIC_MESH_RAIL_Y_FRAC  # rail sits at half wall height
        radius_s = cls.schematic_rail_radius()
        clear_s = cls.schematic_rail_clear()

        layer_name = cls.SCHEMATIC_FEATURE_LAYER_NAME
        feat_layer = bm.edges.layers.string.get(layer_name) or bm.edges.layers.string.new(layer_name)

        # ── Wall outline (rectangle at z=0, slightly wider than the rail) ──
        # Spans the full schematic height; the rail attaches in the middle,
        # so the wall reads as "continuing past the rail above and below".
        # Wall edges stay untagged — they're background context, not a
        # feature any dimension measures.
        wall_extra = 0.08
        wall_x_left = -half_len - wall_extra
        wall_x_right = half_len + wall_extra
        wall_corners = [
            bm.verts.new((wall_x_left, 0.0, 0.0)),
            bm.verts.new((wall_x_right, 0.0, 0.0)),
            bm.verts.new((wall_x_right, wall_top, 0.0)),
            bm.verts.new((wall_x_left, wall_top, 0.0)),
        ]
        for a, b in ((0, 1), (1, 2), (2, 3), (3, 0)):
            bm.edges.new((wall_corners[a], wall_corners[b]))

        # ── Handrail tube (hex cross-section in YZ, extruded along X) ──────
        # Centred on the rail centreline at (±(half_len - rail_inset),
        # rail_y, +clear_s) — in front of the wall plane at z=0. The tube
        # is shorter than the wall so the wall visibly extends past it on
        # both sides; the L-brackets sit at the tube ends, so the leftmost
        # bracket no longer coincides with the wall's left edge.
        rail_inset = cls.SCHEMATIC_RAIL_INSET_FRAC
        rail_x_left = -half_len + rail_inset
        rail_x_right = half_len - rail_inset
        segments = 6
        ring_left, ring_right = [], []
        for i in range(segments):
            theta = 2 * math.pi * i / segments
            dy = math.cos(theta) * radius_s
            dz = math.sin(theta) * radius_s
            ring_left.append(bm.verts.new((rail_x_left, rail_y + dy, clear_s + dz)))
            ring_right.append(bm.verts.new((rail_x_right, rail_y + dy, clear_s + dz)))
        # All hex-tube edges tagged "rail_tube" so they highlight together
        # when the railing_diameter dimension is hovered.
        for i in range(segments):
            j = (i + 1) % segments
            e_left = bm.edges.new((ring_left[i], ring_left[j]))
            e_right = bm.edges.new((ring_right[i], ring_right[j]))
            e_axial = bm.edges.new((ring_left[i], ring_right[i]))
            e_left[feat_layer] = b"rail_tube"
            e_right[feat_layer] = b"rail_tube"
            e_axial[feat_layer] = b"rail_tube"

        # ── L-brackets at each rail end (rail → drop → wall) ───────────────
        # Bracket attach points follow the rail ends, so they're pulled
        # inward by ``rail_inset`` from the wall edges. From the rail
        # centreline, drop ``bracket_drop`` in Y, then run perpendicular
        # back to the wall plane (z=0). The L shape reads as a wall-mount
        # bracket under the 3/4 tilt. Both bracket segments tagged
        # "bracket" so they highlight when clear_width OR support_spacing
        # is hovered (both dimensions measure features of the supports).
        bracket_drop = 0.06
        for x in (rail_x_left, rail_x_right):
            v_rail = bm.verts.new((x, rail_y, clear_s))
            v_corner = bm.verts.new((x, rail_y - bracket_drop, clear_s))
            v_wall = bm.verts.new((x, rail_y - bracket_drop, 0.0))
            e1 = bm.edges.new((v_rail, v_corner))
            e2 = bm.edges.new((v_corner, v_wall))
            e1[feat_layer] = b"bracket"
            e2[feat_layer] = b"bracket"


class FlipRailingPathOrder(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.flip_railing_path_order"
    bl_label = "Flip Railing Path Order"
    bl_description = "Can be useful to maintain railing supports direction"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        obj = context.active_object
        assert obj
        element = tool.Ifc.get_entity(obj)
        assert element
        props = tool.Model.get_railing_props(obj)

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
        assert obj
        props = tool.Model.get_railing_props(obj)

        # Auto-commit any in-progress parametric draft before switching to
        # path-edit. ``set_props_kwargs_from_ifc_data`` a few lines below
        # overwrites props with the pset's stored values — without committing
        # first, anything the user dragged on a dimension gizmo (height,
        # diameter, …) would be silently discarded the moment path-edit
        # starts.
        if props.is_editing:
            tool.Parametric.commit_object_draft(obj, "bim.finish_editing_railing")

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
    assert obj
    props = tool.Model.get_railing_props(obj)

    ProfileDecorator.uninstall()
    props.is_editing_path = False

    if bpy.context.active_object.mode == "EDIT":
        bpy.ops.object.mode_set(mode="OBJECT")

    if props.railing_type == "FRAMELESS_PANEL":
        update_railing_modifier_bmesh(context)
    else:
        element = tool.Ifc.get_entity(obj)
        assert element
        body = ifcopenshell.util.representation.get_representation(element, "Model", "Body", "MODEL_VIEW")
        bonsai.core.geometry.switch_representation(
            tool.Ifc,
            tool.Geometry,
            obj=obj,
            representation=body,
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
        assert obj
        element = tool.Ifc.get_entity(obj)
        props = tool.Model.get_railing_props(obj)

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
        assert obj
        element = tool.Ifc.get_entity(obj)
        assert element
        props = tool.Model.get_railing_props(obj)
        props.is_editing = False

        pset = tool.Pset.get_element_pset(element, "BBIM_Railing")
        ifcopenshell.api.pset.remove_pset(tool.Ifc.get(), product=element, pset=pset)
        return {"FINISHED"}
