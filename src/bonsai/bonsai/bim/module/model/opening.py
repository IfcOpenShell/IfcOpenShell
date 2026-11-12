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

from collections.abc import Sequence
from math import radians
from typing import Any, Optional, Union

import bmesh
import bpy
import gpu
import ifcopenshell
import ifcopenshell.api.feature
import ifcopenshell.api.geometry
import ifcopenshell.api.root
import ifcopenshell.geom
import ifcopenshell.util.element
import ifcopenshell.util.representation
import ifcopenshell.util.shape
import ifcopenshell.util.shape_builder
import ifcopenshell.util.unit
import numpy as np
import shapely
from bpy.types import Operator, SpaceView3D
from gpu_extras.batch import batch_for_shader
from mathutils import Matrix, Vector

import bonsai.core.geometry
import bonsai.tool as tool
from bonsai.bim import decorator_cache
from bonsai.bim.module.drawing.decoration import DecoratorData

# Multi-entry cache for the opening preview's dissolved-edges fallback.
# Single-entry wouldn't fit: the draw handler iterates every active opening
# per frame, each with its own mesh. Bumped wholesale on the shared
# decorator-cache token (depsgraph / undo / redo / load), one slot per
# (mesh.session_uid, angle_limit). Outlier vs. the per-object caches below —
# consulted only on world-draw-data miss, so the global wipe rarely fires in
# steady state and the simpler invalidation is enough.
_dissolved_edges_cache: dict[
    tuple[int, float],
    tuple[list[Vector], list[tuple[int, int]]],
] = {}
_dissolved_edges_cache_token: int = -1


def _get_cached_dissolved_edges(
    mesh: bpy.types.Mesh,
    angle_limit: float = radians(1.0),
) -> tuple[list[Vector], list[tuple[int, int]]]:
    global _dissolved_edges_cache_token
    token = decorator_cache.get_decorator_cache_token()
    if token != _dissolved_edges_cache_token:
        _dissolved_edges_cache.clear()
        _dissolved_edges_cache_token = token
    key = (mesh.session_uid, angle_limit)
    cached = _dissolved_edges_cache.get(key)
    if cached is not None:
        return cached
    result = tool.Geometry.get_dissolved_edges(mesh, angle_limit=angle_limit)
    _dissolved_edges_cache[key] = result
    return result


# Per-object epoch: bumped only when this specific object's transform or geometry
# updates land in the depsgraph delta. Invalidation work scales with the number
# of changed objects, not total scene size — moving one object leaves every
# other entry valid. Bumped by the depsgraph handler below; cleared on
# undo/redo/load alongside the cache dicts.
_object_epochs: dict[int, int] = {}


@bpy.app.handlers.persistent
def _bump_object_epochs_for_decoration(*args) -> None:
    # depsgraph_update_post is called as (scene, depsgraph) in 4.x but the
    # *args signature follows decorator_cache's defensive idiom.
    depsgraph = args[1] if len(args) >= 2 else None
    if depsgraph is None or not hasattr(depsgraph, "updates"):
        return
    for u in depsgraph.updates:
        if not isinstance(u.id, bpy.types.Object):
            continue
        if not (u.is_updated_geometry or u.is_updated_transform):
            continue
        # u.id is the evaluated COW copy; the cache keys are written from the
        # original Object (read by the draw handler), and session_uid can
        # differ across the COW boundary. Resolve to the original before keying.
        original = getattr(u.id, "original", u.id)
        if original is None:
            continue
        uid = original.session_uid
        _object_epochs[uid] = _object_epochs.get(uid, 0) + 1


@bpy.app.handlers.persistent
def _clear_decoration_caches_globally(*args) -> None:
    # Undo/redo/load: depsgraph deltas can't be trusted to describe the
    # transition, so wipe every per-object cache state.
    _object_epochs.clear()
    _world_draw_data_cache.clear()
    _batch_cache.clear()


def _decoration_invalidation_hooks() -> tuple:
    return (
        bpy.app.handlers.undo_post,
        bpy.app.handlers.redo_post,
        bpy.app.handlers.load_post,
    )


def install_decoration_cache_handlers() -> None:
    if _bump_object_epochs_for_decoration not in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.append(_bump_object_epochs_for_decoration)
    for hook in _decoration_invalidation_hooks():
        if _clear_decoration_caches_globally not in hook:
            hook.append(_clear_decoration_caches_globally)


def uninstall_decoration_cache_handlers() -> None:
    try:
        bpy.app.handlers.depsgraph_update_post.remove(_bump_object_epochs_for_decoration)
    except ValueError:
        pass
    for hook in _decoration_invalidation_hooks():
        try:
            hook.remove(_clear_decoration_caches_globally)
        except ValueError:
            pass


# Per-object world-space draw payload: line_verts (dissolved or ios_edges-filtered),
# verts (full mesh, indexed by loop_triangles), edges_indices, tris. Entries are
# (epoch, payload) tuples; lookup compares epoch to _object_epochs[uid], so a
# stale entry for an object that didn't change since the last build still hits.
_world_draw_data_cache: dict[
    int,
    tuple[
        int,
        tuple[
            list[tuple[float, float, float]],
            list[tuple[float, float, float]],
            list[tuple[int, int]],
            list[tuple[int, ...]],
        ],
    ],
] = {}


def _get_cached_world_draw_data(
    obj: bpy.types.Object,
) -> tuple[
    list[tuple[float, float, float]],
    list[tuple[float, float, float]],
    list[tuple[int, int]],
    list[tuple[int, ...]],
]:
    uid = obj.session_uid
    epoch = _object_epochs.get(uid, 0)
    entry = _world_draw_data_cache.get(uid)
    if entry is not None and entry[0] == epoch:
        return entry[1]

    mw = obj.matrix_world
    verts = [tuple(mw @ v.co) for v in obj.data.vertices]
    obj.data.calc_loop_triangles()
    tris = [tuple(t.vertices) for t in obj.data.loop_triangles]

    ios_edges_attribute = obj.data.attributes.get("ios_edges")
    if ios_edges_attribute:
        # Loader-curated edges: read the attribute aligned with bm.edges order.
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        edges_indices = [
            tuple(v.index for v in e.verts) for i, e in enumerate(bm.edges) if ios_edges_attribute.data[i].value
        ]
        bm.free()
        line_verts = verts
    else:
        dissolved, edges_indices = _get_cached_dissolved_edges(obj.data)
        line_verts = [tuple(mw @ v) for v in dissolved]

    result = (line_verts, verts, edges_indices, tris)
    _world_draw_data_cache[uid] = (epoch, result)
    return result


# GPUBatch cache: skip per-frame batch_for_shader. Entries are (epoch, batch);
# lookup compares epoch to _object_epochs[uid] so other objects' batches stay
# alive when one object's depsgraph delta bumps only its own epoch. The cached
# batches reference GPU-side buffers tied to Blender's built-in shaders, which
# are themselves cached by name (gpu.shader.from_builtin returns the same
# handle each call), so they stay drawable across frames.
_batch_cache: dict[tuple[int, str], tuple[int, "gpu.types.GPUBatch"]] = {}

# CAD hidden-line convention for the occluded back-pass: world-space dashes so
# density stays coherent across zoom. Dash + gap = period; dash_width controls
# the "on" portion.
_DASH_PERIOD_METERS: float = 0.20
_DASH_WIDTH_METERS: float = 0.10
# Solid front pass is rendered wider than the dashed back pass so its halo
# overpowers the dashed center on visible edges even when the WIRE-display
# overlay biases the depth buffer at outline pixels.
_DASH_LINE_WIDTH: float = 1.5
_SOLID_LINE_WIDTH: float = 2.5
# Per-iteration default line width used by every non-occlusion draw call in
# this decorator's ``__call__``. Restored after each occlusion pair so the
# next draw isn't silently inheriting the wider solid-pass override.
_DEFAULT_LINE_WIDTH: float = 2.0


def _get_cached_batch_or_none(cache_key: tuple[int, str]) -> "gpu.types.GPUBatch | None":
    uid = cache_key[0]
    epoch = _object_epochs.get(uid, 0)
    entry = _batch_cache.get(cache_key)
    if entry is not None and entry[0] == epoch:
        return entry[1]
    return None


def _store_batch_in_cache(cache_key: tuple[int, str], batch: "gpu.types.GPUBatch") -> None:
    uid = cache_key[0]
    epoch = _object_epochs.get(uid, 0)
    _batch_cache[cache_key] = (epoch, batch)


def is_filling_supported(element) -> bool:
    """True when Bonsai's opening generator can derive an opening from this
    element. IFC's schema permits any IfcElement as a filling; Bonsai
    currently supports only IfcDoor and IfcWindow because those are the
    classes with OverallWidth/OverallHeight attributes (or their types'
    ELEVATION_VIEW profiles) that the generator can consume."""
    return element is not None and element.is_a() in ("IfcDoor", "IfcWindow")


class FilledOpeningGenerator:
    def generate(
        self,
        filling_obj: bpy.types.Object,
        voided_obj: bpy.types.Object,
        target: Optional[Vector] = None,
        preserve_placement: bool = False,
    ) -> Union[None, str]:
        """
        :param target: Target opening position. If ommited, cursor position is used.
        :param preserve_placement: If True, keep ``filling_obj.matrix_world`` as-is
            and skip the snap-to-wall-axis / rl1-rl2 Z-default logic. The opening
            is still created at the filling's current world position. Useful
            when the caller (e.g. the SHIFT-add-opening gizmo flow) has
            already positioned the filling intentionally.
        :return: None if there was no errors, otherwise returns a string with error message.
        """
        props = tool.Model.get_model_props()
        opening_thickness_si = 0.0

        filling = tool.Ifc.get_entity(filling_obj)
        element = tool.Ifc.get_entity(voided_obj)

        assert filling and element
        if filling.FillsVoids:
            ifcopenshell.api.feature.remove_feature(
                tool.Ifc.get(), feature=filling.FillsVoids[0].RelatingOpeningElement
            )

        if target is None:
            should_set_z_level = True
            target = bpy.context.scene.cursor.location.copy()
        else:
            should_set_z_level = False

        # Sometimes, the voided_obj may be an aggregate, which won't have any representation.
        if not preserve_placement and voided_obj.data:
            raycast = voided_obj.closest_point_on_mesh(voided_obj.matrix_world.inverted() @ target, distance=0.01)
            if not raycast[0]:
                target = filling_obj.matrix_world.translation.copy()
                raycast = voided_obj.closest_point_on_mesh(voided_obj.matrix_world.inverted() @ target, distance=0.5)
                if not raycast[0]:
                    return "TARGET is too far away from the voided object's mesh."

            # In this prototype, we assume openings are only added to axis-based elements
            layers = tool.Model.get_material_layer_parameters(element)
            if layers["layer_set_direction"] == "AXIS2":
                opening_thickness_si = layers["thickness"] * 2
                axes = tool.Model.get_wall_axis(voided_obj, layers=layers)
                axis_base = axes["base"]
                axis_side = axes["side"]
                new_matrix = voided_obj.matrix_world.copy()
                point_on_base_axis = tool.Cad.point_on_edge(target, axis_base)
                point_on_side_axis = tool.Cad.point_on_edge(target, axis_side)
                if (point_on_base_axis - target).length <= (point_on_side_axis - target).length:
                    new_matrix.translation.x = point_on_base_axis.x
                    new_matrix.translation.y = point_on_base_axis.y
                else:
                    new_matrix.translation.x = point_on_side_axis.x
                    new_matrix.translation.y = point_on_side_axis.y
                    new_matrix = new_matrix @ Matrix.Rotation(radians(180.0), 4, "Z")

                if should_set_z_level:
                    if filling.is_a("IfcDoor"):
                        new_matrix.translation.z = voided_obj.matrix_world.translation.z + props.rl1
                    else:
                        new_matrix.translation.z = voided_obj.matrix_world.translation.z + props.rl2
                else:
                    new_matrix.translation.z = filling_obj.matrix_world.copy().translation.z
            elif layers["layer_set_direction"] == "AXIS3":
                new_matrix = voided_obj.matrix_world.copy()
                local_position_on_voided_obj = raycast[1]
                # Equivalent to "side Z" for a wall axis, so that stuff like skylights appear on the top.
                local_position_on_voided_obj.z = layers["offset"] + layers["thickness"]
                new_matrix.translation.xyz = voided_obj.matrix_world @ local_position_on_voided_obj
                rotation_matrix = Matrix.Rotation(radians(-90), 4, "X")
                new_matrix @= rotation_matrix
            else:
                assert False, f"Unexpected layer set direction: {layers['layer_set_direction']}"

            filling_obj.matrix_world = new_matrix
            bpy.context.view_layer.update()

        if tool.Ifc.is_moved(voided_obj):
            bonsai.core.geometry.edit_object_placement(tool.Ifc, tool.Geometry, tool.Surveyor, obj=voided_obj)

        existing_opening_occurrence = self.get_existing_opening_occurrence_if_any(filling)

        # CREATE THE OPENING FIRST
        opening = ifcopenshell.api.root.create_entity(
            tool.Ifc.get(),
            ifc_class="IfcOpeningElement",
            predefined_type="OPENING",
            name="Opening",
        )
        ifcopenshell.api.geometry.edit_object_placement(
            tool.Ifc.get(),
            product=opening,
            matrix=np.array(filling_obj.matrix_world),
            is_si=True,
        )

        # NOW HANDLE REPRESENTATION
        # Variables to track if we should reuse a mapped representation
        reuse_mapped_representation = False
        existing_mapping_source = None
        representation = None

        if existing_opening_occurrence:
            representation = ifcopenshell.util.representation.get_representation(
                existing_opening_occurrence, "Model", "Body", "MODEL_VIEW"
            )
            assert representation
            representation = ifcopenshell.util.representation.resolve_representation(representation)
        else:
            representation = self.generate_opening_from_filling(
                filling, filling_obj, opening_thickness_si=opening_thickness_si
            )

        # Create mapped representation
        if reuse_mapped_representation:
            # Reuse the existing RepresentationMap - don't create a new one!
            context = ifcopenshell.util.representation.get_context(tool.Ifc.get(), "Model", "Body", "MODEL_VIEW")
            new_mapped_item = tool.Ifc.get().create_entity(
                "IfcMappedItem",
                MappingSource=existing_mapping_source,
                MappingTarget=tool.Ifc.get().create_entity(
                    "IfcCartesianTransformationOperator3D",
                    Axis1=tool.Ifc.get().create_entity("IfcDirection", DirectionRatios=(1.0, 0.0, 0.0)),
                    Axis2=tool.Ifc.get().create_entity("IfcDirection", DirectionRatios=(0.0, 1.0, 0.0)),
                    LocalOrigin=tool.Ifc.get().create_entity("IfcCartesianPoint", Coordinates=(0.0, 0.0, 0.0)),
                    Scale=1.0,
                    Axis3=tool.Ifc.get().create_entity("IfcDirection", DirectionRatios=(0.0, 0.0, 1.0)),
                ),
            )
            mapped_representation = tool.Ifc.get().create_entity(
                "IfcShapeRepresentation",
                ContextOfItems=context,
                RepresentationIdentifier="Body",
                RepresentationType="MappedRepresentation",
                Items=[new_mapped_item],
            )
        else:
            mapped_representation = ifcopenshell.api.geometry.map_representation(
                tool.Ifc.get(), representation=representation
            )

        ifcopenshell.api.geometry.assign_representation(
            tool.Ifc.get(), product=opening, representation=mapped_representation
        )

        ifcopenshell.api.feature.add_feature(tool.Ifc.get(), feature=opening, element=element)
        ifcopenshell.api.feature.add_filling(tool.Ifc.get(), opening=opening, element=filling)

        voided_objs = [voided_obj]
        # Openings affect all subelements of an aggregate
        for subelement in tool.Aggregate.get_parts_recursively(element):
            subobj = tool.Ifc.get_object(subelement)
            if subobj:
                voided_objs.append(subobj)

        for voided_obj in voided_objs:
            if voided_obj.data:
                voided_element = tool.Ifc.get_entity(voided_obj)
                assert voided_element
                context = tool.Geometry.get_active_representation_context(voided_obj)
                representation = tool.Geometry.get_representation_by_context(voided_element, context)
                assert representation

                tool.Geometry.recut_host(voided_obj, representation)

    def regenerate_from_type(self, usecase_path: str, ifc_file: ifcopenshell.file, settings: dict[str, Any]) -> None:
        relating_type = settings["relating_type"]

        # Filling type-switch on an array of fillings fans out N host recuts —
        # one per related object — without batching. Coalesce them.
        with tool.Geometry.batch_host_recut():
            for related_object in settings["related_objects"]:
                self._regenerate_from_type(related_object)

    def _regenerate_from_type(self, related_object: ifcopenshell.entity_instance) -> None:
        filling = related_object
        if not getattr(filling, "FillsVoids", None):
            return

        opening = filling.FillsVoids[0].RelatingOpeningElement
        voided_element = opening.VoidsElements[0].RelatingBuildingElement

        opening_rep = ifcopenshell.util.representation.get_representation(opening, "Model", "Body", "MODEL_VIEW")
        ifcopenshell.api.geometry.unassign_representation(tool.Ifc.get(), product=opening, representation=opening_rep)
        ifcopenshell.api.geometry.remove_representation(tool.Ifc.get(), representation=opening_rep)

        existing_opening_occurrence = self.get_existing_opening_occurrence_if_any(filling)

        if existing_opening_occurrence:
            representation = ifcopenshell.util.representation.get_representation(
                existing_opening_occurrence, "Model", "Body", "MODEL_VIEW"
            )
            representation = ifcopenshell.util.representation.resolve_representation(representation)
            mapped_representation = ifcopenshell.api.geometry.map_representation(
                tool.Ifc.get(), representation=representation
            )
            ifcopenshell.api.geometry.assign_representation(
                tool.Ifc.get(), product=opening, representation=mapped_representation
            )
        else:
            opening_obj = tool.Ifc.get_object(opening)
            if opening_obj:
                tool.Ifc.unlink(element=opening)
                tool.Blender.remove_data_blocks([opening_obj], remove_unused_data=True)

            filling_obj = tool.Ifc.get_object(filling)
            representation = self.generate_opening_from_filling(filling, filling_obj)
            mapped_representation = ifcopenshell.api.geometry.map_representation(
                tool.Ifc.get(), representation=representation
            )
            ifcopenshell.api.geometry.assign_representation(
                tool.Ifc.get(), product=opening, representation=mapped_representation
            )

        # update voided object representation or all it's parts if it's an aggregate
        voided_elements = ifcopenshell.util.element.get_parts(voided_element) or [voided_element]
        for voided_element in voided_elements:
            voided_obj = tool.Ifc.get_object(voided_element)
            representation = tool.Geometry.get_active_representation(voided_obj)
            if not representation:
                continue
            tool.Geometry.recut_host(voided_obj, representation)

    def generate_opening_from_filling(
        self,
        filling: ifcopenshell.entity_instance,
        filling_obj: bpy.types.Object,
        opening_thickness_si: float = 0.0,
    ) -> ifcopenshell.entity_instance:
        # Since openings are reused later, we give a default thickness of 1.2m
        # which should cover the majority of curved, or super thick walls.
        thickness = max(1.2, opening_thickness_si)
        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        shape_builder = ifcopenshell.util.shape_builder.ShapeBuilder(tool.Ifc.get())

        profile = None
        filling_type = ifcopenshell.util.element.get_type(filling)
        if filling_type:
            profile = ifcopenshell.util.representation.get_representation(
                filling_type, "Model", "Profile", "ELEVATION_VIEW"
            )
            filling_obj = tool.Ifc.get_object(filling_type)
        context = ifcopenshell.util.representation.get_context(tool.Ifc.get(), "Model", "Body", "MODEL_VIEW")
        assert context

        if profile:
            profile = ifcopenshell.util.representation.resolve_representation(profile)

            def get_curve_2d_from_3d(profile: ifcopenshell.entity_instance) -> ifcopenshell.entity_instance:
                if len(profile.Items) == 1:
                    curve_3d = profile.Items[0]
                    if tool.Ifc.get_schema() == "IFC2X3":
                        coords = [Vector(p).xz for p in shape_builder.get_polyline_coords(curve_3d)]
                        return shape_builder.polyline(coords, closed=True)
                    # using different algorithm to keep arc segments possible in the future
                    ifc_segments = [shape_builder.deep_copy(s) for s in curve_3d.Segments]
                    ifc_points = tool.Ifc.get().createIfcCartesianPointList2D(
                        [Vector(p).xz for p in curve_3d.Points.CoordList]
                    )
                    return tool.Ifc.get().createIfcIndexedPolyCurve(Points=ifc_points, Segments=ifc_segments)

                settings = ifcopenshell.geom.settings()
                settings.set("dimensionality", ifcopenshell.ifcopenshell_wrapper.CURVES_SURFACES_AND_SOLIDS)
                geometry = ifcopenshell.geom.create_shape(settings, profile)
                verts = ifcopenshell.util.shape.get_vertices(geometry)
                # [0, 2] represents X and Z ordinates
                verts = [(np.around(v[[0, 2]], decimals=3) / unit_scale).tolist() for v in verts]
                edges = ifcopenshell.util.shape.get_edges(geometry)

                boundary_lines = [shapely.LineString([verts[v] for v in e]) for e in edges]
                unioned_boundaries = shapely.union_all(shapely.GeometryCollection(boundary_lines))
                closed_polygons = shapely.polygonize(boundary_lines)
                polygon = max(closed_polygons.geoms, key=lambda polygon: polygon.area)
                return shape_builder.polyline(list(polygon.exterior.coords))

            extrusion = shape_builder.extrude(
                get_curve_2d_from_3d(profile),
                magnitude=thickness / unit_scale,
                position=Vector([0.0, -thickness * 0.5 / unit_scale, 0.0]),
                **shape_builder.extrude_kwargs("Y"),
            )
            return shape_builder.get_representation(context, [extrusion])

        if (
            filling_rep := tool.Geometry.get_active_representation(filling_obj)
        ) and filling_rep.ContextOfItems == context:
            x, y, z = filling_obj.dimensions
        else:
            # The filling_obj's mesh data is not the body geometry.
            settings = ifcopenshell.geom.settings()
            filling_element = tool.Ifc.get_entity(filling_obj)
            filling_body = ifcopenshell.util.representation.get_representation(filling_element, context)
            filling_geometry = ifcopenshell.geom.create_shape(settings, filling_body)
            x = ifcopenshell.util.shape.get_x(filling_geometry)
            y = ifcopenshell.util.shape.get_y(filling_geometry)
            z = ifcopenshell.util.shape.get_z(filling_geometry)
        opening_position = Vector([0.0, -thickness * 0.5 / unit_scale, 0.0])
        opening_size = Vector([x, z]) / unit_scale

        # Windows and doors can have a casing that overlaps the wall
        # but shouldn't affect the size of the opening.
        # So we shouldn't use object dimensions in that case. More: #2784
        # Just keeping it for windows and doors for now to be safe
        has_width_attribute, has_height_attribute = False, False
        if filling.is_a() in ["IfcWindow", "IfcDoor"]:
            if filling.OverallWidth:
                opening_size.x = filling.OverallWidth
                has_width_attribute = True
            if filling.OverallHeight:
                opening_size.y = filling.OverallHeight
                has_height_attribute = True

        # making sure if min_x or min_z != 0 to shift the opening accordingly
        # to prevent something like #2784
        if not has_width_attribute:
            opening_position.x = min(v[0] for v in filling_obj.bound_box)

        if not has_height_attribute:
            opening_position.z = min(v[2] for v in filling_obj.bound_box)

        extrusion = shape_builder.extrude(
            shape_builder.rectangle(size=opening_size),
            magnitude=thickness / unit_scale,
            position=opening_position,
            **shape_builder.extrude_kwargs("Y"),
        )

        return shape_builder.get_representation(context, [extrusion])

    def has_visible_openings(self, element):
        for opening in [r.RelatedOpeningElement for r in tool.Geometry.get_openings(element)]:
            if tool.Ifc.get_object(opening):
                return True
        return False

    def get_existing_opening_occurrence_if_any(
        self, filling: ifcopenshell.entity_instance
    ) -> Union[ifcopenshell.entity_instance, None]:
        filling_type = ifcopenshell.util.element.get_type(filling)
        if filling_type:
            filling_occurrences = ifcopenshell.util.element.get_types(filling_type)
            for filling_occurrence in filling_occurrences:
                if filling_occurrence != filling and filling_occurrence.FillsVoids:
                    return filling_occurrence.FillsVoids[0].RelatingOpeningElement


class RecalculateFill(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.recalculate_fill"
    bl_label = "Recalculate Fill"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.selected_objects

    def _execute(self, context):
        # N selected fillings × M voided host parts would fire N×M host recuts
        # without batching. Coalesce per host.
        with tool.Geometry.batch_host_recut():
            return self._recalculate_fills(context)

    def _recalculate_fills(self, context):
        # Refresh each selected filling's mapped opening source before
        # recutting the host. Dedup by source id covers the common shared-
        # source case in one rewrite while leaving unrelated sibling sources
        # untouched.
        seen_source_ids: set[int] = set()
        for obj in context.selected_objects:
            element = tool.Ifc.get_entity(obj)
            if not element or not element.FillsVoids:
                continue
            opening = element.FillsVoids[0].RelatingOpeningElement
            body = tool.Geometry.get_body_representation(opening)
            if body is None:
                continue
            source = tool.Geometry.resolve_mapped_representation(body)
            if source.id() in seen_source_ids:
                continue
            seen_source_ids.add(source.id())
            tool.Model.regenerate_filling_opening_body(element)

        for obj in context.selected_objects:
            element = tool.Ifc.get_entity(obj)
            if not element or not element.FillsVoids:
                continue
            openings = [r.RelatingOpeningElement for r in element.FillsVoids or []]
            building_elements = []
            for opening in openings:
                building_elements.extend([r.RelatingBuildingElement for r in opening.VoidsElements or []])
            for building_element in building_elements:
                building_obj = tool.Ifc.get_object(building_element)
                if tool.Ifc.is_moved(building_obj):
                    bonsai.core.geometry.edit_object_placement(tool.Ifc, tool.Geometry, tool.Surveyor, obj=building_obj)
            for opening in openings:
                bonsai.core.geometry.edit_object_placement(tool.Ifc, tool.Geometry, tool.Surveyor, obj=obj)
                ifcopenshell.api.geometry.edit_object_placement(
                    tool.Ifc.get(), product=opening, matrix=obj.matrix_world
                )

            decomposed_building_elements = set()
            for building_element in building_elements:
                decomposed_building_elements.add(building_element)
                decomposed_building_elements.update(ifcopenshell.util.element.get_decomposition(building_element))

            for building_element in decomposed_building_elements:
                building_obj = tool.Ifc.get_object(building_element)
                if building_obj and building_obj.data:
                    representation = tool.Geometry.get_active_representation(building_obj)
                    if representation:
                        tool.Geometry.recut_host(building_obj, representation)

        # Refresh cut decorator
        DecoratorData.cut_cache.clear()
        DecoratorData.fill_cache.clear()
        DecoratorData.slice_cache.clear()

        return {"FINISHED"}


class FlipFill(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.flip_fill"
    bl_label = "Flip Fill"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.selected_objects

    def _execute(self, context):
        for obj in context.selected_objects:
            element = tool.Ifc.get_entity(obj)
            if not element or not element.FillsVoids:
                continue

            filled_opening = element.FillsVoids[0].RelatingOpeningElement
            filled_element = filled_opening.VoidsElements[0].RelatingBuildingElement
            filled_object = tool.Ifc.get_object(filled_element)

            if filled_element.is_a() in ["IfcWall", "IfcWallStandardCase"]:
                # if the filled element is a wall, move the filling in such a way
                # that it will have the same relative position, but to the other
                # side of the wall
                #
                # For example, if a door frame protudes 1cm out of the wall,
                # it will produde 1cm out of the other side of the wall.

                layers = tool.Model.get_material_layer_parameters(filled_element)
                axes = tool.Model.get_wall_axis(filled_object, layers=layers)

                center_axis = [(axes["base"][0] + axes["side"][0]) * 0.5, (axes["base"][1] + axes["side"][1]) * 0.5]

                original_pos = obj.matrix_world.translation
                bb = tool.Blender.get_object_bounding_box(obj)
                min_y = min(bb["min_y"], 0)
                max_y = max(bb["max_y"], 0)

                point_on_center_axis = tool.Cad.point_on_edge(original_pos, center_axis)
                offset_to_center_axis = point_on_center_axis - original_pos
                offset_to_center_axis.z = 0
                depth_offset = max_y + min_y
                depth_correction_vec = offset_to_center_axis.normalized() * depth_offset

                mirrored_point = original_pos + offset_to_center_axis * 2.0 - depth_correction_vec

                obj.matrix_world.translation = mirrored_point
                bonsai.core.geometry.edit_object_placement(tool.Ifc, tool.Geometry, tool.Surveyor, obj=obj)

            tool.Geometry.flip_object(obj, "XY")
            ifcopenshell.api.geometry.edit_object_placement(tool.Ifc.get(), filled_opening, obj.matrix_world)
            tool.Geometry.reload_representation(filled_object)

        return {"FINISHED"}


class AddBoolean(Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_boolean"
    bl_label = "Add Boolean"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Applies a boolean to the selected IFC object using the other selected blender object as a void"

    @classmethod
    def poll(cls, context):
        if not len(context.selected_objects) >= 2:
            cls.poll_message_set("At least 2 objects need to be selected.")
            return False
        return True

    def _execute(self, context):
        first_obj = tool.Blender.get_active_object()
        if not first_obj or not tool.Geometry.is_boolean_operand(first_obj):
            self.report({"INFO"}, "At least two valid objects must be selected to add a boolean.")
            return {"CANCELLED"}
        second_objs = [
            o for o in tool.Blender.get_selected_objects() if o != first_obj and tool.Geometry.is_boolean_operand(o)
        ]
        if not second_objs:
            self.report({"INFO"}, "At least two representation items must be selected to add a boolean.")
            return {"CANCELLED"}

        props = tool.Feature.get_boolean_props()

        first_item = tool.Geometry.get_active_representation(first_obj)
        assert first_item
        second_items = [
            representation for o in second_objs if (representation := tool.Geometry.get_active_representation(o))
        ]
        booleans = ifcopenshell.api.geometry.add_boolean(tool.Ifc.get(), first_item, second_items, props.operator)

        rep_obj = tool.Geometry.get_geometry_props().representation_obj
        if booleans:
            # Users typically select two top-level items and expect the
            # operand to be absorbed into the boolean, not remain as a
            # standalone item alongside it.
            representation = tool.Geometry.get_active_representation(rep_obj)
            representation = ifcopenshell.util.representation.resolve_representation(representation)
            second_items_set = set(second_items)
            new_items = [i for i in representation.Items if i not in second_items_set]
            if new_items:
                representation.Items = new_items
        rep_element = tool.Ifc.get_entity(rep_obj)
        tool.Model.mark_manual_booleans(rep_element, booleans)
        tool.Geometry.reload_representation(rep_obj)
        if props.is_editing:
            bpy.ops.bim.enable_editing_booleans()
        tool.Root.reload_item_decorator()


class ToggleHostOpenings(Operator, tool.Ifc.Operator):
    bl_idname = "bim.toggle_host_openings"
    bl_label = "Toggle Openings"
    bl_description = "Show or hide opening fills (doors and windows) in the viewport\n\nHotkey: Alt+O"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if not tool.Model.has_selected_ifc_objects():
            cls.poll_message_set("No IFC objects selected.")
            return False
        return True

    def _execute(self, context: bpy.types.Context) -> set[str]:
        # Opening visibility is independent of host geometry — don't commit any
        # active parametric edit; the user can keep editing the host.
        if tool.Model.get_model_props().openings:
            bpy.ops.bim.edit_openings(apply_all=True)
        else:
            bpy.ops.bim.show_openings()
        return {"FINISHED"}


class ShowOpenings(Operator, tool.Ifc.Operator):
    bl_idname = "bim.show_openings"
    bl_label = "Show Openings"
    bl_description = "Show openings for selected objects"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        for obj in tool.Blender.get_selected_objects():
            element = tool.Ifc.get_entity(obj)
            if element is None:
                continue
            self.show_object_openings(obj, element)
        DecorationsHandler.install(bpy.context)
        bpy.ops.bim.update_openings_focus()
        return {"FINISHED"}

    def show_object_openings(self, obj: bpy.types.Object, element: ifcopenshell.entity_instance) -> None:
        openings_elements = [rel.RelatedOpeningElement for rel in tool.Geometry.get_openings(element)]
        if not openings_elements:
            return
        if tool.Ifc.is_moved(obj):
            bonsai.core.geometry.edit_object_placement(tool.Ifc, tool.Geometry, tool.Surveyor, obj=obj)
        openings_elements_to_load = [o for o in openings_elements if not tool.Ifc.get_object(o)]
        openings_objects = tool.Model.load_openings(openings_elements_to_load)
        for obj in openings_objects:
            tool.Root.add_tracked_opening(obj, "OPENING")


class UpdateOpeningsFocus(Operator):
    bl_idname = "bim.update_openings_focus"
    bl_label = "Update Openings Focus"
    bl_description = "Show objects that are not part of the object or its openings as transparent"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        preferences = tool.Blender.get_addon_preferences()
        if preferences.opening_focus_opacity == 100:
            return {"FINISHED"}
        openings: set[bpy.types.Object] = set()
        building_objects: set[bpy.types.Object] = set()
        props = tool.Model.get_model_props()
        for opening in props.openings:
            if opening.obj:
                openings.add(opening.obj)
                opening_element = tool.Ifc.get_entity(opening.obj)
                assert opening_element
                building_element = opening_element.VoidsElements[0].RelatingBuildingElement
                building_obj = tool.Ifc.get_object(building_element)
                assert isinstance(building_obj, bpy.types.Object)
                building_objects.add(building_obj)

        for obj in context.scene.objects:
            obj.color = [
                obj.color[0],
                obj.color[1],
                obj.color[2],
                (
                    1
                    if not props.openings
                    or not building_objects
                    or obj in openings
                    or obj in building_objects
                    or obj in context.selected_objects
                    else preferences.opening_focus_opacity / 100
                ),
            ]
        return {"FINISHED"}


def hide_openings(context: bpy.types.Context, objects: Sequence[bpy.types.Object]) -> None:
    objects_to_remove = set()
    props = tool.Model.get_model_props()
    for opening_prop in props.openings:
        opening_obj = opening_prop.obj
        if not opening_obj:
            continue
        opening_element = tool.Ifc.get_entity(opening_obj)
        if opening_element:
            if not opening_element.is_a("IfcOpeningElement"):
                # This opening has been assigned to another ifc class. Remove it from the openings pool. See #3854
                opening_prop.obj = None
                continue
            building_element = opening_element.VoidsElements[0].RelatingBuildingElement
            if building_element:
                building_obj = tool.Ifc.get_object(building_element)
                if building_obj in objects:
                    tool.Ifc.unlink(element=opening_element)
                    objects_to_remove.add(opening_obj)
        if opening_obj in objects:
            objects_to_remove.add(opening_obj)

    tool.Blender.remove_data_blocks(objects_to_remove, remove_unused_data=True)
    tool.Model.purge_scene_openings()
    bpy.ops.bim.update_openings_focus()


class HideAllOpenings(Operator, tool.Ifc.Operator):
    bl_idname = "bim.hide_all_openings"
    bl_label = "Hide All Openings"
    bl_description = "Hide every single opening"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        hide_openings(context, context.scene.objects[:])
        return {"FINISHED"}


class HideOpenings(Operator, tool.Ifc.Operator):
    bl_idname = "bim.hide_openings"
    bl_label = "Hide"
    bl_description = "Hide Openings"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        hide_openings(context, context.selected_objects[:])
        return {"FINISHED"}


class EditOpenings(Operator, tool.Ifc.Operator):
    bl_idname = "bim.edit_openings"
    bl_label = "Edit"
    bl_description = "Edit Openings"
    bl_options = {"REGISTER", "UNDO"}
    apply_all: bpy.props.BoolProperty(default=False)

    def _execute(self, context):
        building_objs, opening_elements = self.get_buildings_and_openings(context)
        self.edit_openings(building_objs, opening_elements)

        tool.Model.purge_scene_openings()
        tool.Model.reload_body_representation(building_objs)
        bpy.ops.bim.update_openings_focus()
        return {"FINISHED"}

    def get_buildings_and_openings(
        self, context: bpy.types.Context
    ) -> tuple[set[bpy.types.Object], set[ifcopenshell.entity_instance]]:
        props = tool.Model.get_model_props()
        building_objs: set[bpy.types.Object] = set()
        opening_elements: set[ifcopenshell.entity_instance] = set()
        objects_to_remove = set()
        if self.apply_all:
            for opening_prop in props.openings:
                opening_obj = opening_prop.obj
                if opening_obj is None:
                    continue
                opening_element = tool.Ifc.get_entity(opening_obj)
                if opening_element is None:
                    objects_to_remove.add(opening_obj)
                    continue
                opening_elements.add(opening_element)
                building_element = opening_element.VoidsElements[0].RelatingBuildingElement
                building_objs.add(tool.Ifc.get_object(building_element))
        else:
            for obj in context.selected_objects:
                element = tool.Ifc.get_entity(obj)
                if element.is_a("IfcOpeningElement"):
                    opening_element = element
                    opening_elements.add(opening_element)
                    if opening_element.VoidsElements:
                        building_element = opening_element.VoidsElements[0].RelatingBuildingElement
                        building_obj = tool.Ifc.get_object(building_element)
                        if building_obj:
                            building_objs.add(building_obj)
                else:
                    for relation in tool.Geometry.get_openings(element):
                        opening_element = relation.RelatedOpeningElement
                        if tool.Ifc.get_object(opening_element):
                            opening_elements.add(opening_element)
                        building_objs.add(obj)
        tool.Blender.remove_data_blocks(objects_to_remove, remove_unused_data=True)
        return building_objs, opening_elements

    def edit_openings(
        self, building_objs: set[bpy.types.Object], opening_elements: set[ifcopenshell.entity_instance]
    ) -> None:
        props = tool.Geometry.get_geometry_props()
        objects_to_remove: set[bpy.types.Object] = set()
        for opening_element in opening_elements:
            opening_obj = tool.Ifc.get_object(opening_element)

            if opening_obj:
                opening_edited = tool.Ifc.is_edited(opening_obj)
                opening_moved = tool.Ifc.is_moved(opening_obj)
                # Sibling walls only need a viewport-level refresh when the
                # opening's shape or placement actually changed — a pure
                # show/hide toggle leaves them in their existing state.
                if opening_edited or opening_moved:
                    similar_openings = bonsai.core.geometry.get_similar_openings(tool.Ifc, opening_element)
                    similar_openings_building_objs = bonsai.core.geometry.get_similar_openings_building_objs(
                        tool.Ifc, similar_openings
                    )
                    building_objs.update(similar_openings_building_objs)
                    if opening_edited:
                        tool.Geometry.run_geometry_update_representation(obj=opening_obj)
                    else:
                        bonsai.core.geometry.edit_object_placement(
                            tool.Ifc, tool.Geometry, tool.Surveyor, obj=opening_obj
                        )
                    bonsai.core.geometry.edit_similar_opening_placement(
                        tool.Geometry, opening_element, similar_openings
                    )
                    building_objs.update(self.get_all_building_objects_of_similar_openings(opening_element))

                tool.Ifc.unlink(element=opening_element)
                if props.representation_obj == opening_obj:
                    props.representation_obj = None
                objects_to_remove.add(opening_obj)
        tool.Blender.remove_data_blocks(objects_to_remove, remove_unused_data=True)

    def get_all_building_objects_of_similar_openings(self, opening):
        if not opening.is_a("IfcOpeningElement") or not opening.HasFillings:
            return []
        results = set()
        for rel in opening.HasFillings:
            filling_type = ifcopenshell.util.element.get_type(rel.RelatedBuildingElement)
            if not filling_type:
                continue
            for occurrence in ifcopenshell.util.element.get_types(filling_type):
                for rel2 in occurrence.FillsVoids:
                    for rel3 in rel2.RelatingOpeningElement.VoidsElements:
                        obj = tool.Ifc.get_object(rel3.RelatingBuildingElement)
                        if obj:
                            results.add(obj)
        return results


class CloneOpening(Operator, tool.Ifc.Operator):
    bl_idname = "bim.clone_opening"
    bl_label = "Clone Opening"
    bl_description = "Clone the active Opening object and assign to the selected Element"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if len(context.selected_objects) != 2:
            cls.poll_message_set("Exactly 2 objects must be selected.")
            return False
        return True

    def _execute(self, context):
        # The voided host may be an aggregate whose parts each get recut.
        # Coalesce per host so a many-parts aggregate doesn't fan out.
        with tool.Geometry.batch_host_recut():
            return self._clone_opening(context)

    def _clone_opening(self, context):
        # NOTE: Operator displayed in UI only with IfcOpeningElement being active.
        ifc_file = tool.Ifc.get()
        objects = bpy.context.selected_objects
        opening_obj = context.active_object
        assert opening_obj
        opening = tool.Ifc.get_entity(opening_obj)
        assert opening and opening.is_a("IfcOpeningElement")

        voided_obj = next(o for o in objects if o != opening_obj)
        voided_element = tool.Ifc.get_entity(voided_obj)
        assert voided_element

        opening_placement = opening.ObjectPlacement
        opening_representation = opening.Representation

        new_opening = ifcopenshell.api.root.create_entity(tool.Ifc.get(), ifc_class="IfcOpeningElement")
        new_opening.Representation = opening_representation

        ifcopenshell.api.feature.add_feature(ifc_file, feature=new_opening, element=voided_element)
        new_opening.ObjectPlacement = opening_placement

        # Update affected representations.
        elements_to_update = tool.Aggregate.get_parts_recursively(voided_element)
        for element in elements_to_update:
            obj = tool.Ifc.get_object(element)
            if not isinstance(obj, bpy.types.Object) or not isinstance(obj.data, bpy.types.Mesh):
                continue
            representation = tool.Geometry.get_active_representation(obj)
            assert representation
            tool.Geometry.recut_host(obj, representation)

        return {"FINISHED"}


class PurgeUnusedOpenings(Operator, tool.Ifc.Operator):
    bl_idname = "bim.purge_unused_openings"
    bl_label = "Purge Unused Openings"
    bl_description = "Purge Openings that do not intersect with their related building element"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        poll = any(
            tool.Geometry.has_openings(element)
            for element in [tool.Ifc.get_entity(obj) for obj in context.selected_objects]
            if element
        )
        if not poll:
            cls.poll_message_set("No objects with openings selected.")
            return False
        return True

    def _execute(self, context):
        bpy.ops.bim.show_openings()
        objects = context.selected_objects[:]
        [o.select_set(False) for o in objects]
        active_object = context.active_object
        purged = 0
        for obj in objects:
            element = tool.Ifc.get_entity(obj)
            if not element or not tool.Geometry.has_openings(element):
                continue
            obj_bvh_tree = tool.Geometry.get_bvh_tree(obj)
            for opening_rel in tool.Geometry.get_openings(element):
                opening_elt = opening_rel.RelatedOpeningElement
                opening_obj = tool.Ifc.get_object(opening_elt)
                opening_bvh_tree = tool.Geometry.get_bvh_tree(opening_obj)
                if not opening_bvh_tree.overlap(obj_bvh_tree):
                    opening_obj.select_set(True)
                    purged += 1
        if context.selected_objects:
            bpy.ops.bim.override_object_delete(is_batch=False)
        bpy.ops.bim.edit_openings(apply_all=True)
        [o.select_set(True) for o in objects]
        context.view_layer.objects.active = active_object
        self.report({"INFO"}, f"{purged} unused openings were purged.")
        return {"FINISHED"}


class RemoveBoolean(Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_boolean"
    bl_label = "Remove Boolean"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Removes the actively selected boolean"

    @classmethod
    def poll(cls, context):
        props = tool.Feature.get_boolean_props()
        return props.active_boolean

    def _execute(self, context):
        props = tool.Feature.get_boolean_props()
        ifcopenshell.api.geometry.remove_boolean(
            tool.Ifc.get(), tool.Ifc.get().by_id(props.active_boolean.ifc_definition_id)
        )
        bpy.ops.bim.enable_editing_booleans()
        rep_obj = tool.Geometry.get_geometry_props().representation_obj
        assert rep_obj
        tool.Geometry.reload_representation(rep_obj)
        tool.Root.reload_item_decorator()


class SelectBoolean(Operator):
    bl_idname = "bim.select_boolean"
    bl_label = "Select Boolean"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Selects operands of the active boolean\nSHIFT-CLICK to select all operands recursively"
    is_recursive: bpy.props.BoolProperty(name="Is Recursive", default=False, options={"SKIP_SAVE"})

    @classmethod
    def poll(cls, context):
        props = tool.Feature.get_boolean_props()
        return props.active_boolean

    def invoke(self, context, event):
        if event.type == "LEFTMOUSE" and event.shift:
            self.is_recursive = True
        return self.execute(context)

    def execute(self, context):
        props = tool.Feature.get_boolean_props()
        queue = [tool.Ifc.get().by_id(props.active_boolean.ifc_definition_id)]
        items = {i.ifc_definition_id: i.obj for i in tool.Geometry.get_geometry_props().item_objs}
        while queue:
            item = queue.pop()
            if item.is_a("IfcBooleanResult"):
                if self.is_recursive:
                    queue.append(item.FirstOperand)
                    queue.append(item.SecondOperand)
                else:
                    if obj := items.get(item.FirstOperand.id()):
                        tool.Blender.select_object(obj)
                    if obj := items.get(item.SecondOperand.id()):
                        tool.Blender.select_object(obj)
            elif obj := items.get(item.id()):
                tool.Blender.select_object(obj)
        return {"FINISHED"}


class DecorationsHandler:
    installed = None

    @classmethod
    def install(cls, context):
        if cls.installed:
            cls.uninstall()
        handler = cls()
        cls.installed = SpaceView3D.draw_handler_add(handler, (context,), "WINDOW", "POST_VIEW")
        install_decoration_cache_handlers()

    @classmethod
    def uninstall(cls):
        try:
            SpaceView3D.draw_handler_remove(cls.installed, "WINDOW")
        except ValueError:
            pass
        cls.installed = None
        uninstall_decoration_cache_handlers()

    def _get_or_build_batch(self, shader, shader_type, content_pos, indices=None, cache_key=None):
        if cache_key is not None:
            cached = _get_cached_batch_or_none(cache_key)
            if cached is not None:
                return cached
        if not tool.Blender.validate_shader_batch_data(content_pos, indices):
            return None
        batch = batch_for_shader(shader, shader_type, {"pos": content_pos}, indices=indices)
        if cache_key is not None:
            _store_batch_in_cache(cache_key, batch)
        return batch

    def draw_batch(self, shader_type, content_pos, color, indices=None, cache_key=None):
        shader = self.line_shader if shader_type == "LINES" else self.shader
        batch = self._get_or_build_batch(shader, shader_type, content_pos, indices, cache_key=cache_key)
        if batch is None:
            return
        shader.uniform_float("color", color)
        batch.draw(shader)

    def _draw_lines_with_occlusion(self, verts, color, edges_indices, cache_key=None):
        # Two-pass CAD hidden-line convention. Both passes use POLYLINE_UNIFORM_COLOR.
        #
        # The solid front pass is rendered WIDER than the dashed back pass so it
        # produces a halo around the line center, beyond the depth-bias zone that
        # Blender's overlay engine writes when an opening is set to WIRE display.
        # Without the width difference, the wire bias makes the center-pixel
        # ``LESS_EQUAL`` comparison fail (line ends up slightly behind the biased
        # wire depth) so the solid pass would lose to the dashed back pass even
        # on visible edges. The halo gives the solid pass enough screen-space to
        # overpower the dashed pattern visually.
        #
        # Dashed renders first at the standard width so the solid overlay's wider
        # halo cleanly hides it on visible edges; on occluded edges the solid
        # ``LESS_EQUAL`` pass fails against the wall depth and the dashed remains.
        front_batch = self._get_or_build_batch(self.line_shader, "LINES", verts, edges_indices, cache_key=cache_key)
        if front_batch is None:
            return

        dashed_cache_key = (cache_key[0], cache_key[1] + "_dashed") if cache_key is not None else None
        dash_batch = None
        if dashed_cache_key is not None:
            dash_batch = _get_cached_batch_or_none(dashed_cache_key)
        if dash_batch is None:
            dash_verts, dash_edges = tool.Blender.build_dashed_line_segments(
                verts, edges_indices, _DASH_PERIOD_METERS, _DASH_WIDTH_METERS
            )
            dash_batch = self._get_or_build_batch(self.line_shader, "LINES", dash_verts, dash_edges)
            if dash_batch is not None and dashed_cache_key is not None:
                _store_batch_in_cache(dashed_cache_key, dash_batch)

        original_depth_test = gpu.state.depth_test_get()
        front_color = list(color)
        front_color[3] = 1.0
        self.line_shader.uniform_float("color", front_color)

        if dash_batch is not None:
            self.line_shader.uniform_float("lineWidth", _DASH_LINE_WIDTH)
            gpu.state.depth_test_set("ALWAYS")
            dash_batch.draw(self.line_shader)

        self.line_shader.uniform_float("lineWidth", _SOLID_LINE_WIDTH)
        gpu.state.depth_test_set("LESS_EQUAL")
        front_batch.draw(self.line_shader)

        # Restore the per-iteration default set at the top of __call__ so
        # subsequent draws (the HalfSpaceSolid arrow, future call-sites) are
        # not silently affected by the front-pass width override.
        self.line_shader.uniform_float("lineWidth", _DEFAULT_LINE_WIDTH)
        gpu.state.depth_test_set(original_depth_test)

    def __call__(self, context):
        props = tool.Model.get_model_props()
        if not props.openings:
            return
        self.addon_prefs = tool.Blender.get_addon_preferences()
        selected_elements_color = self.addon_prefs.decorator_color_selected
        unselected_elements_color = self.addon_prefs.decorator_color_unselected
        special_elements_color = self.addon_prefs.decorator_color_special

        def transparent_color(color, alpha=0.1):
            color = [i for i in color]
            color[3] = alpha
            return color

        gpu.state.point_size_set(6)
        gpu.state.blend_set("ALPHA")

        gprops = tool.Geometry.get_geometry_props()
        for opening in props.openings:
            obj = opening.obj
            if gprops.representation_obj == obj:
                # We are editing the representation of the opening :
                for item in gprops.item_objs:
                    if item.obj.mode == "EDIT":
                        obj = item.obj
                        break
            if not obj:
                continue

            self.line_shader = gpu.shader.from_builtin("POLYLINE_UNIFORM_COLOR")
            self.line_shader.bind()  # required to be able to change uniforms of the shader
            # POLYLINE_UNIFORM_COLOR specific uniforms
            self.line_shader.uniform_float("viewportSize", (context.region.width, context.region.height))
            self.line_shader.uniform_float("lineWidth", _DEFAULT_LINE_WIDTH)

            # general shader
            self.shader = gpu.shader.from_builtin("UNIFORM_COLOR")

            verts = []
            selected_edges = []
            unselected_edges = []
            selected_vertices = []
            unselected_vertices = []

            if obj.mode == "EDIT":
                bm = bmesh.from_edit_mesh(obj.data)

                for vertex in bm.verts:
                    co = tuple(obj.matrix_world @ vertex.co)
                    verts.append(co)
                    if vertex.hide:
                        continue

                    if vertex.select:
                        selected_vertices.append(co)
                    else:
                        unselected_vertices.append(co)

                for edge in bm.edges:
                    edge_indices = [v.index for v in edge.verts]
                    if edge.hide:
                        continue
                    if edge.select:
                        selected_edges.append(edge_indices)
                    else:
                        unselected_edges.append(edge_indices)

                self.draw_batch("LINES", verts, transparent_color(unselected_elements_color, 0.5), unselected_edges)
                self.draw_batch("LINES", verts, selected_elements_color, selected_edges)
                self.draw_batch("POINTS", unselected_vertices, unselected_elements_color)
                self.draw_batch("POINTS", selected_vertices, selected_elements_color)
                tool.Blender.draw_bmesh_face_tris(bm, verts, transparent_color(special_elements_color), self.draw_batch)
            else:
                line_verts, verts, edges_indices, tris = _get_cached_world_draw_data(obj)
                color = selected_elements_color if obj in context.selected_objects else special_elements_color
                self._draw_lines_with_occlusion(line_verts, color, edges_indices, cache_key=(obj.session_uid, "lines"))
                self.draw_batch(
                    "TRIS",
                    verts,
                    transparent_color(special_elements_color),
                    tris,
                    cache_key=(obj.session_uid, "tris"),
                )

            if "HalfSpaceSolid" in obj.name:
                # Arrow shape
                verts = [
                    tuple(obj.matrix_world @ Vector((0, 0, 0))),
                    tuple(obj.matrix_world @ Vector((0, 0, 0.5))),
                    tuple(obj.matrix_world @ Vector((0.05, 0, 0.45))),
                    tuple(obj.matrix_world @ Vector((-0.05, 0, 0.45))),
                    tuple(obj.matrix_world @ Vector((0, 0.05, 0.45))),
                    tuple(obj.matrix_world @ Vector((0, -0.05, 0.45))),
                ]
                edges = [(0, 1), (1, 2), (1, 3), (1, 4), (1, 5)]
                color = selected_elements_color if obj in context.selected_objects else special_elements_color
                self._draw_lines_with_occlusion(verts, color, edges, cache_key=(obj.session_uid, "arrow"))
