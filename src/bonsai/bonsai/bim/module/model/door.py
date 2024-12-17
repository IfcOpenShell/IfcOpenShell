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
from bmesh.types import BMVert, BMFace

import ifcopenshell
import ifcopenshell.api
import ifcopenshell.util.element
import ifcopenshell.util.representation
import ifcopenshell.util.schema
import ifcopenshell.util.unit
import bonsai.tool as tool
import bonsai.core.geometry
import bonsai.core.geometry as core
import bonsai.core.root
from bonsai.bim.module.model.window import create_bm_window, create_bm_box

from mathutils import Vector, Matrix
from typing import Union, Any, Optional

import json
import collections

V_ = tool.Blender.V_


def update_door_modifier_representation(context: bpy.types.Context) -> None:
    obj = context.active_object
    props = obj.BIMDoorProperties
    element = tool.Ifc.get_entity(obj)
    ifc_file = tool.Ifc.get()
    sliding_door = "SLIDING" in props.door_type
    si_conversion = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())

    representation_data = {
        "operation_type": props.door_type,
        "overall_height": props.overall_height / si_conversion,
        "overall_width": props.overall_width / si_conversion,
        "lining_properties": {
            "LiningDepth": props.lining_depth / si_conversion,
            "LiningThickness": props.lining_thickness / si_conversion,
            "LiningOffset": props.lining_offset / si_conversion,
            "LiningToPanelOffsetX": props.lining_to_panel_offset_x / si_conversion,
            "LiningToPanelOffsetY": props.lining_to_panel_offset_y / si_conversion,
            "TransomThickness": props.transom_thickness / si_conversion,
            "TransomOffset": props.transom_offset / si_conversion,
            "CasingThickness": props.casing_thickness / si_conversion,
            "CasingDepth": props.casing_depth / si_conversion,
            "ThresholdThickness": props.threshold_thickness / si_conversion,
            "ThresholdDepth": props.threshold_depth / si_conversion,
            "ThresholdOffset": props.threshold_offset / si_conversion,
        },
        "panel_properties": {
            "PanelDepth": props.panel_depth / si_conversion,
            "PanelWidth": props.panel_width_ratio,
            "FrameDepth": props.frame_depth / si_conversion,
            "FrameThickness": props.frame_thickness / si_conversion,
        },
    }

    previously_active_context = tool.Geometry.get_active_representation_context(obj)

    # ELEVATION_VIEW representation
    profile = ifcopenshell.util.representation.get_context(ifc_file, "Model", "Profile", "ELEVATION_VIEW")
    if profile:
        representation_data["context"] = profile
        elevation_representation = ifcopenshell.api.run(
            "geometry.add_door_representation", ifc_file, **representation_data
        )
        tool.Model.replace_object_ifc_representation(profile, obj, elevation_representation)

    # MODEL_VIEW representation
    # (Model/Body defined only BEFORE Plan/Body to prevent #2744)
    body = ifcopenshell.util.representation.get_context(ifc_file, "Model", "Body", "MODEL_VIEW")
    representation_data["context"] = body
    model_representation = ifcopenshell.api.run("geometry.add_door_representation", ifc_file, **representation_data)
    tool.Model.replace_object_ifc_representation(body, obj, model_representation)

    # Body/PLAN_VIEW representation
    plan_body = ifcopenshell.util.representation.get_context(ifc_file, "Plan", "Body", "PLAN_VIEW")
    if plan_body:
        representation_data["context"] = plan_body
        plan_representation = ifcopenshell.api.run("geometry.add_door_representation", ifc_file, **representation_data)
        tool.Model.replace_object_ifc_representation(plan_body, obj, plan_representation)

    # Annotation/PLAN_VIEW representation
    plan_annotation = ifcopenshell.util.representation.get_context(ifc_file, "Plan", "Annotation", "PLAN_VIEW")
    if plan_annotation:
        if not sliding_door:
            # only sliding doors have Annotation/PLAN_VIEW
            # for other types we just check for old representation and remove it if it's there
            old_representation = ifcopenshell.util.representation.get_representation(
                element, "Plan", "Annotation", "PLAN_VIEW"
            )
            if old_representation:
                core.remove_representation(
                    tool.Ifc,
                    tool.Geometry,
                    obj=obj,
                    representation=old_representation,
                )
        else:
            representation_data["context"] = plan_annotation
            plan_representation = ifcopenshell.api.run(
                "geometry.add_door_representation", ifc_file, **representation_data
            )
            tool.Model.replace_object_ifc_representation(plan_annotation, obj, plan_representation)

    # adding switch representation at the end instead of changing order of representations
    # to prevent #2744
    if tool.Geometry.get_active_representation_context(obj) != previously_active_context:
        previously_active_representation = ifcopenshell.util.representation.get_representation(
            element,
            previously_active_context.ContextType,
            previously_active_context.ContextIdentifier,
            previously_active_context.TargetView,
        )

        if not previously_active_representation:
            # we assume there is no representation because it was
            # Plan/Annotation/PLAN_VIEW
            previously_active_context = ifcopenshell.util.representation.get_context(
                ifc_file, "Plan", "Body", "PLAN_VIEW"
            )
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
        element.OperationType = props.door_type

    # occurrences attributes
    occurrences = tool.Ifc.get_all_element_occurrences(element)
    for occurrence in occurrences:
        occurrence.OverallWidth = props.overall_width / si_conversion
        occurrence.OverallHeight = props.overall_height / si_conversion

    tool.Model.update_simple_openings(element)


# TODO: move it out to tools
def bm_sort_out_geom(
    geom_data: list[Union[bmesh.types.BMVert, bmesh.types.BMEdge, bmesh.types.BMFace]]
) -> dict[str, Any]:
    geom_dict = {"verts": [], "edges": [], "faces": []}

    for el in geom_data:
        if isinstance(el, BMVert):
            geom_dict["verts"].append(el)
        elif isinstance(el, BMFace):
            geom_dict["faces"].append(el)
        else:
            geom_dict["edges"].append(el)
    return geom_dict


def bm_mirror(
    bm: bmesh.types.BMesh,
    verts: list[bmesh.types.BMVert],
    mirror_axes: Vector = V_(1, 0, 0).freeze(),
    mirror_point: Vector = V_(0, 0, 0).freeze(),
    create_copy: bool = False,
) -> list[bmesh.types.BMVert]:
    matrix = Matrix.Translation(mirror_point)
    for i, v in enumerate(mirror_axes):
        if not v:
            continue
        mirror_axis = V_(0, 0, 0)
        mirror_axis[i] = 1.0
        matrix = matrix @ Matrix.Scale(-1, 4, mirror_axis)
    matrix = matrix @ Matrix.Translation(-mirror_point)

    # `bmesh.ops.mirror` has no option to mirror existing geometry without creating new
    # and matrix kind of work diffrently than transform so I chose `bmesh.ops.transform`
    if create_copy:
        faces = set()
        for v in verts:
            faces.update(v.link_faces)
        duplicated = bmesh.ops.duplicate(bm, geom=list(faces))
        verts = bm_sort_out_geom(duplicated["geom"])["verts"]

    bmesh.ops.transform(bm, verts=verts, matrix=matrix, space=Matrix.Identity(4))
    return verts


def create_bm_extruded_profile(
    bm: bmesh.types.BMesh,
    points: list[Vector],
    edges: Optional[list[tuple[int, int]]] = None,
    faces: Optional[list[list[int]]] = None,
    position: Vector = V_(0, 0, 0).freeze(),
    magnitude: float = 1.0,
    extrusion_vector: Vector = V_(0, 0, 1).freeze(),
) -> list[bmesh.types.BMVert]:
    bm.verts.index_update()
    bm.edges.index_update()
    bm.faces.ensure_lookup_table()

    if not edges:
        last_point = len(points) - 1
        edges = [(i, i + 1) for i in range(last_point)]
        edges.append((last_point, 0))

    new_verts = [bm.verts.new(v) for v in points]
    new_edges = [bm.edges.new([new_verts[vi] for vi in edge]) for edge in edges]

    if not faces:
        new_faces = bmesh.ops.contextual_create(bm, geom=new_edges)["faces"]
    else:
        new_faces = [bm.faces.new([new_verts[vi] for vi in face]) for face in faces]

    extruded = bmesh.ops.extrude_face_region(bm, geom=new_faces)
    extrusion_vector = extrusion_vector * magnitude
    extruded_verts = bm_sort_out_geom(extruded["geom"])["verts"]
    bmesh.ops.translate(bm, vec=extrusion_vector, verts=extruded_verts)

    bmesh.ops.translate(bm, vec=position, verts=new_verts + extruded_verts)
    return new_verts + extruded_verts


def create_bm_door_lining(
    bm: bmesh.types.BMesh, size: Vector, thickness: list, position: Vector = V_(0, 0, 0).freeze()
) -> list[bmesh.types.BMVert]:
    """`thickness` of the profile is defined as list in the following order: `(SIDE, TOP)`

    `thickness` can be also defined just as 1 float value.
    """

    if not isinstance(thickness, collections.abc.Iterable):
        thickness = [thickness] * 2

    th_side, th_up = thickness

    width, depth, height = size

    verts = [
        (0, [width - th_side, 0.0, height - th_up]),
        (1, [0.0, 0.0, height]),
        (2, [th_side, 0.0, height - th_up]),
        (3, [0.0, 0.0, 0.0]),
        (4, [width - th_side, 0.0, 0.0]),
        (5, [width, 0.0, height]),
        (6, [th_side, 0.0, 0.0]),
        (7, [width, 0.0, 0.0]),
    ]

    edges = [
        (0, [5, 7]),
        (1, [0, 2]),
        (2, [1, 5]),
        (3, [4, 0]),
        (4, [2, 1]),
        (5, [0, 5]),
        (6, [4, 7]),
        (7, [3, 1]),
        (8, [3, 6]),
        (9, [2, 6]),
    ]

    faces = [
        (0, [5, 0, 2, 1]),
        (1, [4, 0, 5, 7]),
        (2, [3, 1, 2, 6]),
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


def update_door_modifier_bmesh(context: bpy.types.Context) -> None:
    obj = context.active_object
    props = obj.BIMDoorProperties

    overall_width = props.overall_width
    overall_height = props.overall_height
    door_type = props.door_type
    double_swing_door = "DOUBLE_SWING" in door_type
    double_door = "DOUBLE_DOOR" in door_type
    sliding_door = "SLIDING" in door_type

    # lining params
    lining_depth = props.lining_depth
    lining_thickness_default = props.lining_thickness
    lining_offset = props.lining_offset
    lining_to_panel_offset_x = props.lining_to_panel_offset_x if not sliding_door else lining_thickness_default
    panel_depth = props.panel_depth
    lining_to_panel_offset_y = props.lining_to_panel_offset_y if not sliding_door else -panel_depth

    transom_thickness = props.transom_thickness / 2
    transfom_offset = props.transom_offset
    if transom_thickness == 0:
        transfom_offset = 0
    window_lining_height = overall_height - transfom_offset - transom_thickness

    side_lining_thickness = lining_thickness_default
    panel_lining_overlap_x = max(lining_thickness_default - lining_to_panel_offset_x, 0) if not sliding_door else 0

    top_lining_thickness = transom_thickness or lining_thickness_default
    panel_top_lining_overlap_x = max(top_lining_thickness - lining_to_panel_offset_x, 0) if not sliding_door else 0
    door_opening_width = overall_width - lining_to_panel_offset_x * 2
    if double_swing_door:
        side_lining_thickness = side_lining_thickness - panel_lining_overlap_x
        top_lining_thickness = top_lining_thickness - panel_top_lining_overlap_x

    threshold_thickness = props.threshold_thickness
    threshold_depth = props.threshold_depth
    threshold_offset = props.threshold_offset
    threshold_width = overall_width - side_lining_thickness * 2

    casing_thickness = props.casing_thickness
    casing_depth = props.casing_depth

    # panel params
    panel_width = door_opening_width * props.panel_width_ratio
    frame_depth = props.frame_depth
    frame_thickness = props.frame_thickness
    frame_height = window_lining_height - lining_to_panel_offset_x * 2
    glass_thickness = 0.01

    # handle dimensions (hardcoded)
    handle_size = V_(120, 40, 20) * 0.001
    handle_offset = V_(60, 0, 1000) * 0.001  # to the handle center
    handle_center_offset = V_(handle_size.y / 2, 0, handle_size.z) / 2

    if transfom_offset:
        panel_height = transfom_offset + transom_thickness - lining_to_panel_offset_x - threshold_thickness
        lining_height = transfom_offset + transom_thickness
    else:
        panel_height = overall_height - lining_to_panel_offset_x - threshold_thickness
        lining_height = overall_height

    bm = bmesh.new()

    # add lining
    lining_size = V_(overall_width, lining_depth, lining_height)
    lining_thickness = [side_lining_thickness, top_lining_thickness]
    lining_verts = create_bm_door_lining(bm, lining_size, lining_thickness)

    # add threshold
    if not threshold_thickness:
        threshold_verts = []
    else:
        threshold_size = V_(threshold_width, threshold_depth, threshold_thickness)
        threshold_position = V_(side_lining_thickness, threshold_offset, 0)
        threshold_verts = create_bm_box(bm, threshold_size, threshold_position)

    # add casings
    casing_verts = []
    if not lining_offset and casing_thickness:
        casing_wall_overlap = max(casing_thickness - lining_thickness_default, 0)

        inner_casing_thickness = [
            casing_thickness - panel_lining_overlap_x,
            casing_thickness - panel_top_lining_overlap_x,
        ]
        outer_casing_thickness = inner_casing_thickness.copy() if double_swing_door else casing_thickness

        casing_size = V_(overall_width + casing_wall_overlap * 2, casing_depth, overall_height + casing_wall_overlap)
        casing_position = V_(-casing_wall_overlap, -casing_depth, 0)
        outer_casing_verts = create_bm_door_lining(bm, casing_size, outer_casing_thickness, casing_position)
        casing_verts.extend(outer_casing_verts)

        inner_casing_position = V_(-casing_wall_overlap, lining_depth, 0)
        inner_casing_verts = create_bm_door_lining(bm, casing_size, inner_casing_thickness, inner_casing_position)
        casing_verts.extend(inner_casing_verts)

    def create_bm_door_panel(
        panel_size: Vector, panel_position: Vector, door_swing_type: str
    ) -> list[bmesh.types.BMVert]:
        door_verts = []
        # add door panel
        door_verts.extend(create_bm_box(bm, panel_size, panel_position))
        # add door handle
        handle_points = [
            V_(0, 0, 0),
            V_(0, -handle_size.y, 0),
            V_(handle_size.x, -handle_size.y, 0),
            V_(handle_size.x, -handle_size.y / 2, 0),
            V_(handle_size.y / 2, -handle_size.y / 2, 0),
            V_(handle_size.y / 2, 0, 0),
        ]
        handle_position = panel_position + handle_offset - handle_center_offset
        door_handle_verts = create_bm_extruded_profile(
            bm, handle_points, magnitude=handle_size.z, position=handle_position
        )
        door_verts.extend(door_handle_verts)

        if door_swing_type == "LEFT":
            bm_mirror(
                bm, door_handle_verts, mirror_axes=V_(1, 0, 0), mirror_point=panel_position + V_(panel_size.x / 2, 0, 0)
            )

        door_handle_mirrored_verts = bm_mirror(
            bm,
            door_handle_verts,
            mirror_axes=V_(0, 1, 0),
            mirror_point=handle_position + V_(0, panel_size.y / 2, 0),
            create_copy=True,
        )
        door_verts.extend(door_handle_mirrored_verts)
        return door_verts

    door_verts = []
    panel_size = V_(panel_width, panel_depth, panel_height)
    panel_position = V_(lining_to_panel_offset_x, lining_to_panel_offset_y, threshold_thickness)

    if double_door:
        # keeping a little space between doors for readibility
        double_door_offset = 0.001
        panel_size.x = panel_size.x / 2 - double_door_offset
        door_verts.extend(create_bm_door_panel(panel_size, panel_position, "LEFT"))

        mirror_point = panel_position + V_(door_opening_width / 2, 0, 0)
        door_verts.extend(bm_mirror(bm, door_verts, V_(1, 0, 0), mirror_point, create_copy=True))
    else:
        door_swing_type = "LEFT" if door_type.endswith("LEFT") else "RIGHT"
        door_verts.extend(create_bm_door_panel(panel_size, panel_position, door_swing_type))

    # add on top window
    if not transom_thickness:
        window_lining_verts = []
        frame_verts = []
        glass_verts = []
    else:
        window_lining_thickness = [
            side_lining_thickness,
            lining_thickness_default,
            side_lining_thickness,
            transom_thickness,
        ]
        window_lining_thickness.append(transom_thickness)
        window_lining_size = V_(overall_width, lining_depth, window_lining_height)
        window_position = V_(0, 0, overall_height - window_lining_height)
        frame_size = V_(door_opening_width, frame_depth, frame_height)
        window_lining_verts, frame_verts, glass_verts = create_bm_window(
            bm,
            window_lining_size,
            window_lining_thickness,
            lining_to_panel_offset_x,
            lining_to_panel_offset_y,
            frame_size,
            frame_thickness,
            glass_thickness,
            window_position,
        )

    lining_offset_verts = lining_verts + door_verts + window_lining_verts + frame_verts + glass_verts
    bmesh.ops.translate(bm, vec=V_(0, lining_offset, 0), verts=lining_offset_verts)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0001)

    if bpy.context.active_object.mode == "EDIT":
        bmesh.update_edit_mesh(obj.data)
    else:
        bm.to_mesh(obj.data)
        bm.free()
    obj.data.update()


class BIM_OT_add_door(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "mesh.add_door"
    bl_label = "Door"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return tool.Ifc.get() and context.mode == "OBJECT"

    def _execute(self, context):
        ifc_file = tool.Ifc.get()
        if not ifc_file:
            self.report({"ERROR"}, "You need to start IFC project first to create a door.")
            return {"CANCELLED"}

        if context.active_object is not None:
            spawn_location = context.active_object.location.copy()
            context.active_object.select_set(False)
        else:
            spawn_location = bpy.context.scene.cursor.location.copy()

        mesh = bpy.data.meshes.new("IfcDoor")
        obj = bpy.data.objects.new("IfcDoor", mesh)
        obj.location = spawn_location

        element = bonsai.core.root.assign_class(
            tool.Ifc, tool.Collector, tool.Root, obj=obj, ifc_class="IfcDoor", should_add_representation=False
        )
        bonsai.core.geometry.edit_object_placement(tool.Ifc, tool.Geometry, tool.Surveyor, obj=obj)
        if tool.Ifc.get_schema() != "IFC2X3":
            element.PredefinedType = "DOOR"

        bpy.ops.object.select_all(action="DESELECT")
        bpy.context.view_layer.objects.active = None
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.bim.add_door()
        return {"FINISHED"}


# UI operators
class AddDoor(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_door"
    bl_label = "Add Door"
    bl_description = "Add Bonsai parametric door to the active IFC element"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        obj = context.active_object
        element = tool.Ifc.get_entity(obj)
        props = obj.BIMDoorProperties

        door_data = props.get_general_kwargs(convert_to_project_units=True)
        lining_props = props.get_lining_kwargs(convert_to_project_units=True)
        panel_props = props.get_panel_kwargs(convert_to_project_units=True)

        door_data["lining_properties"] = lining_props
        door_data["panel_properties"] = panel_props
        pset = tool.Pset.get_element_pset(element, "BBIM_Door")

        if not pset:
            pset = ifcopenshell.api.run("pset.add_pset", tool.Ifc.get(), product=element, name="BBIM_Door")

        ifcopenshell.api.run(
            "pset.edit_pset",
            tool.Ifc.get(),
            pset=pset,
            properties={"Data": tool.Ifc.get().createIfcText(json.dumps(door_data, default=list))},
        )
        update_door_modifier_representation(context)
        return {"FINISHED"}


class CancelEditingDoor(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.cancel_editing_door"
    bl_label = "Cancel Editing Door"
    bl_options = {"REGISTER"}

    def _execute(self, context):
        obj = context.active_object
        element = tool.Ifc.get_entity(obj)
        props = obj.BIMDoorProperties
        data = json.loads(ifcopenshell.util.element.get_pset(element, "BBIM_Door", "Data"))
        data.update(data.pop("lining_properties"))
        data.update(data.pop("panel_properties"))

        # restore previous settings since editing was canceled
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


class FinishEditingDoor(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.finish_editing_door"
    bl_label = "Finish Editing Door"
    bl_options = {"REGISTER"}

    def _execute(self, context):
        obj = context.active_object
        element = tool.Ifc.get_entity(obj)
        props = obj.BIMDoorProperties

        door_data = props.get_general_kwargs(convert_to_project_units=True)
        lining_props = props.get_lining_kwargs(convert_to_project_units=True)
        panel_props = props.get_panel_kwargs(convert_to_project_units=True)

        door_data["lining_properties"] = lining_props
        door_data["panel_properties"] = panel_props

        props.is_editing = False

        update_door_modifier_representation(context)

        pset = tool.Pset.get_element_pset(element, "BBIM_Door")
        door_data = tool.Ifc.get().createIfcText(json.dumps(door_data, default=list))
        ifcopenshell.api.run("pset.edit_pset", tool.Ifc.get(), pset=pset, properties={"Data": door_data})
        return {"FINISHED"}


class EnableEditingDoor(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.enable_editing_door"
    bl_label = "Enable Editing Door"
    bl_options = {"REGISTER"}

    def _execute(self, context):
        obj = context.active_object
        props = obj.BIMDoorProperties
        element = tool.Ifc.get_entity(obj)
        data = json.loads(ifcopenshell.util.element.get_pset(element, "BBIM_Door", "Data"))
        data.update(data.pop("lining_properties"))
        data.update(data.pop("panel_properties"))

        # required since we could load pset from .ifc and BIMDoorProperties won't be set
        props.set_props_kwargs_from_ifc_data(data)
        props.is_editing = True
        return {"FINISHED"}


class RemoveDoor(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_door"
    bl_label = "Remove Door"
    bl_options = {"REGISTER"}

    def _execute(self, context):
        obj = context.active_object
        props = obj.BIMDoorProperties
        element = tool.Ifc.get_entity(obj)
        obj.BIMDoorProperties.is_editing = False

        pset = tool.Pset.get_element_pset(element, "BBIM_Door")
        ifcopenshell.api.run("pset.remove_pset", tool.Ifc.get(), product=element, pset=pset)

        return {"FINISHED"}
