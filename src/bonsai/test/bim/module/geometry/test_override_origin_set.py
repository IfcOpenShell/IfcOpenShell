# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026
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
# This file was generated with the assistance of an AI coding tool.

import math
import os

import bpy
import ifcopenshell.api.context
import ifcopenshell.api.geometry
import ifcopenshell.geom
import ifcopenshell.util.element
import ifcopenshell.util.placement
import ifcopenshell.util.representation
import ifcopenshell.util.shape_builder
import ifcopenshell.util.unit
import numpy as np
from mathutils import Vector

import bonsai
import bonsai.core.geometry
import bonsai.tool as tool
from bonsai.bim.module.model.slab import DumbSlabPlaner
from test.bim.bootstrap import NewIfc

CURSOR = (3.0, 0.0, 0.0)


def add_wall():
    bpy.ops.mesh.primitive_cube_add()
    obj = bpy.context.active_object
    root_props = tool.Root.get_root_props()
    root_props.ifc_product = "IfcElement"
    root_props.ifc_class = "IfcWall"
    bpy.ops.bim.assign_class()
    return obj


def add_extruded_wall():
    obj = add_wall()
    bpy.ops.bim.update_representation(ifc_representation_class="IfcExtrudedAreaSolid/IfcRectangleProfileDef")
    return obj


def body(obj):
    return tool.Ifc.get_entity(obj).Representation.Representations[0]


def world_bbox(element):
    settings = ifcopenshell.geom.settings()
    settings.set("use-world-coords", True)
    verts = np.array(ifcopenshell.geom.create_shape(settings, element).geometry.verts).reshape(-1, 3)
    return np.concatenate([verts.min(axis=0), verts.max(axis=0)])


def set_origin_to_cursor(obj, cursor=CURSOR):
    bpy.context.scene.cursor.location = cursor
    tool.Blender.select_and_activate_single_object(bpy.context, obj)
    return bpy.ops.bim.override_origin_set(origin_type="ORIGIN_CURSOR")


def close(a, b):
    return np.allclose(a, b, atol=1e-6)


def unit_scale():
    return ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())


def get_layered_slab_type():
    """A LAYER3 slab type, from the demo construction library if the project has none yet."""
    ifc_file = tool.Ifc.get()
    slab_types = [t for t in ifc_file.by_type("IfcSlabType") if tool.Model.get_usage_type(t) == "LAYER3"]
    if not slab_types:
        library = "IFC2X3 Demo Library.ifc" if ifc_file.schema == "IFC2X3" else "IFC4 Demo Library.ifc"
        path = os.path.join(os.path.dirname(bonsai.__file__), "bim", "data", "libraries", library)
        bpy.ops.bim.select_library_file(filepath=path, append_all=True)
        slab_types = [t for t in ifc_file.by_type("IfcSlabType") if tool.Model.get_usage_type(t) == "LAYER3"]
    assert slab_types, "No LAYER3 slab type in the project or the demo library"
    return slab_types[0]


def add_layered_slab(x_angle=0.0):
    slab_type = get_layered_slab_type()
    bpy.context.scene.cursor.location = (0.0, 0.0, 0.0)
    props = tool.Model.get_model_props()
    props.ifc_class = "IfcSlabType"
    props.x_angle = x_angle
    bpy.ops.bim.add_occurrence(relating_type_id=slab_type.id())
    obj = bpy.context.active_object
    assert tool.Model.get_usage_type(tool.Ifc.get_entity(obj)) == "LAYER3"
    if tool.Ifc.is_moved(obj):  # Write any pending rotation, as Save would, before measuring.
        bonsai.core.geometry.edit_object_placement(tool.Ifc, tool.Geometry, tool.Surveyor, obj=obj)
    return obj


def add_wall_type():
    bpy.ops.mesh.primitive_cube_add()
    type_obj = bpy.context.active_object
    root_props = tool.Root.get_root_props()
    root_props.ifc_product = "IfcElementType"
    root_props.ifc_class = "IfcWallType"
    bpy.ops.bim.assign_class()
    return type_obj


def add_occurrence(element_type, location, rotation_z=0.0):
    obj = add_wall()
    bpy.ops.bim.assign_type(relating_type=element_type.id(), related_object=obj.name)
    assert body(obj).RepresentationType == "MappedRepresentation"
    obj.location = location
    obj.rotation_euler = (0.0, 0.0, rotation_z)
    bpy.context.view_layer.update()
    bonsai.core.geometry.edit_object_placement(tool.Ifc, tool.Geometry, tool.Surveyor, obj=obj)
    return obj


def extrusion_of(element):
    representation = ifcopenshell.util.representation.get_representation(element, "Model", "Body", "MODEL_VIEW")
    return tool.Model.get_extrusion(representation)


def world_footprint(element):
    representation = ifcopenshell.util.representation.get_representation(element, "Plan", "FootPrint", "SKETCH_VIEW")
    if not representation:
        return None
    matrix = ifcopenshell.util.placement.get_placement(element.ObjectPlacement)
    points = []
    for item in representation.Items:
        for entity in tool.Ifc.get().traverse(item):
            if entity.is_a("IfcCartesianPoint"):
                points.append(entity.Coordinates)
            elif entity.is_a("IfcCartesianPointList"):
                points.extend(entity.CoordList)
    world = [(matrix @ np.array([*p[:2], 0.0, 1.0]))[:2] for p in points]
    return np.array(sorted(map(tuple, np.round(world, 6))))


def add_structural_item(ifc_class, representation_template):
    root_props = tool.Root.get_root_props()
    root_props.ifc_product = "IfcStructuralItem"
    root_props.ifc_class = ifc_class
    root_props.representation_template = representation_template
    bpy.ops.bim.add_element(skip_dialog=True)
    # Structural items live in a collection that is hidden by default.
    tool.Blender.get_layer_collection(bpy.data.collections.get("IfcStructuralItem")).hide_viewport = False
    return bpy.context.active_object


def world_topology(element):
    """Every point of the element's topology, the face's plane included, in world coordinates."""
    matrix = ifcopenshell.util.placement.get_placement(element.ObjectPlacement)
    points = []
    for representation in element.Representation.Representations:
        for item in representation.Items:
            for entity in tool.Ifc.get().traverse(item):
                if entity.is_a("IfcCartesianPoint"):
                    points.append((matrix @ np.array([*entity.Coordinates, 1.0]))[:3])
    return np.array(sorted(map(tuple, np.round(points, 6))))


class TestOverrideOriginSet(NewIfc):
    def test_an_extrusion_keeps_its_world_position_and_its_profile(self):
        obj = add_extruded_wall()
        element = tool.Ifc.get_entity(obj)
        profile = body(obj).Items[0].SweptArea
        before = world_bbox(element)
        set_origin_to_cursor(obj)
        assert tuple(obj.location) == CURSOR
        assert close(world_bbox(element), before)
        assert body(obj).RepresentationType == "SweptSolid"
        assert body(obj).Items[0].SweptArea == profile

    def test_a_tessellation_keeps_its_world_position(self):
        obj = add_wall()
        element = tool.Ifc.get_entity(obj)
        before = world_bbox(element)
        set_origin_to_cursor(obj)
        assert tuple(obj.location) == CURSOR
        assert close(world_bbox(element), before)
        assert body(obj).RepresentationType == "Tessellation"

    def test_a_clipped_extrusion_keeps_its_world_position(self):
        obj = add_extruded_wall()
        element = tool.Ifc.get_entity(obj)
        ifc_file = tool.Ifc.get()
        plane = ifc_file.createIfcPlane(
            ifc_file.createIfcAxis2Placement3D(
                ifc_file.createIfcCartesianPoint((0.0, 0.0, 0.5 / unit_scale())),
                ifc_file.createIfcDirection((0.0, 0.0, 1.0)),
                ifc_file.createIfcDirection((1.0, 0.0, 0.0)),
            )
        )
        half_space = ifc_file.createIfcHalfSpaceSolid(plane, False)
        ifcopenshell.api.geometry.add_boolean(ifc_file, body(obj).Items[0], [half_space], "DIFFERENCE")
        tool.Geometry.reload_representation(obj)
        before = world_bbox(element)
        set_origin_to_cursor(obj)
        assert tuple(obj.location) == CURSOR
        assert close(world_bbox(element), before)

    def test_other_representations_keep_their_world_position(self):
        obj = add_extruded_wall()
        element = tool.Ifc.get_entity(obj)
        ifc_file = tool.Ifc.get()
        axis_context = ifcopenshell.util.representation.get_context(ifc_file, "Plan", "Axis", "GRAPH_VIEW")
        if not axis_context:
            plan = ifcopenshell.util.representation.get_context(ifc_file, "Plan")
            axis_context = ifcopenshell.api.context.add_context(
                ifc_file, context_type="Plan", context_identifier="Axis", target_view="GRAPH_VIEW", parent=plan
            )
        builder = ifcopenshell.util.shape_builder.ShapeBuilder(ifc_file)
        length = 2.0 / unit_scale()
        axis = builder.get_representation(axis_context, [builder.polyline([(-length / 2, 0.0), (length / 2, 0.0)])])
        ifcopenshell.api.geometry.assign_representation(ifc_file, product=element, representation=axis)

        def world_axis():
            matrix = ifcopenshell.util.placement.get_placement(element.ObjectPlacement)
            points = axis.Items[0].Points.CoordList
            return [(matrix @ np.array([*p, 0.0, 1.0]))[:3] for p in points]

        before = world_axis()
        set_origin_to_cursor(obj)
        assert tuple(obj.location) == CURSOR
        assert close(world_axis(), before)

    def test_a_layered_slab_only_moves_its_origin_in_its_own_plane(self):
        obj = add_layered_slab()
        element = tool.Ifc.get_entity(obj)
        usage = ifcopenshell.util.element.get_material(element)
        offset = usage.OffsetFromReferenceLine
        height = obj.location.z
        position = extrusion_of(element).Position
        position_xy = tuple(position.Location.Coordinates[:2]) if position else (0.0, 0.0)
        before = world_bbox(element)
        set_origin_to_cursor(obj, (3.0, 1.0, 5.0))
        assert close(tuple(obj.location), (3.0, 1.0, height))
        assert close(world_bbox(element), before)
        assert usage.OffsetFromReferenceLine == offset
        # The profile moved, not the extrusion's placement, so it stays drawn in the slab's plane.
        position = extrusion_of(element).Position
        assert close(tuple(position.Location.Coordinates[:2]) if position else (0.0, 0.0), position_xy)

    def test_a_layered_slab_stays_in_place_when_its_thickness_changes_afterwards(self):
        obj = add_layered_slab()
        element = tool.Ifc.get_entity(obj)
        before = world_bbox(element)
        set_origin_to_cursor(obj, (3.0, 1.0, 5.0))
        DumbSlabPlaner().change_thickness(element, extrusion_of(element).Depth * 2)
        after = world_bbox(element)
        assert close(after[[0, 1, 3, 4]], before[[0, 1, 3, 4]])

    def test_a_layered_slab_footprint_stays_in_place_after_editing_its_profile(self):
        ifc_file = tool.Ifc.get()
        if not ifcopenshell.util.representation.get_context(ifc_file, "Plan", "FootPrint", "SKETCH_VIEW"):
            plan = ifcopenshell.util.representation.get_context(ifc_file, "Plan")
            ifcopenshell.api.context.add_context(
                ifc_file, context_type="Plan", context_identifier="FootPrint", target_view="SKETCH_VIEW", parent=plan
            )
        obj = add_layered_slab()
        element = tool.Ifc.get_entity(obj)
        before = world_bbox(element)
        set_origin_to_cursor(obj, (3.0, 1.0, 5.0))
        # Editing the profile regenerates the FootPrint from the profile's own coordinates.
        tool.Blender.select_and_activate_single_object(bpy.context, obj)
        bpy.ops.bim.enable_editing_extrusion_profile()
        bpy.ops.bim.edit_extrusion_profile()
        assert close(world_bbox(element), before)
        footprint = world_footprint(element)
        assert footprint is not None
        footprint = footprint * unit_scale()  # Project units, to compare with the SI bounding box.
        assert close([*footprint.min(axis=0), *footprint.max(axis=0)], before[[0, 1, 3, 4]])

    def test_a_sloped_slab_only_moves_its_origin_in_its_sloped_plane(self):
        obj = add_layered_slab(x_angle=0.3)
        element = tool.Ifc.get_entity(obj)
        usage = ifcopenshell.util.element.get_material(element)
        offset = usage.OffsetFromReferenceLine
        matrix = obj.matrix_world.copy()
        before = world_bbox(element)
        set_origin_to_cursor(obj, (3.0, 1.0, 5.0))
        local_move = matrix.inverted() @ obj.matrix_world.translation
        assert abs(local_move.z) < 1e-6
        assert local_move.length > 1.0
        assert close(world_bbox(element), before)
        assert usage.OffsetFromReferenceLine == offset

    def test_a_sloped_slab_matches_an_untouched_copy_after_a_thickness_change(self):
        moved = tool.Ifc.get_entity(add_layered_slab(x_angle=0.3))
        untouched = tool.Ifc.get_entity(add_layered_slab(x_angle=0.3))
        assert close(world_bbox(moved), world_bbox(untouched))
        set_origin_to_cursor(tool.Ifc.get_object(moved), (3.0, 1.0, 5.0))
        for element in (moved, untouched):
            DumbSlabPlaner().change_thickness(element, extrusion_of(element).Depth * 2)
        assert close(world_bbox(moved), world_bbox(untouched))

    def test_a_typed_element_moves_the_origin_of_its_type_and_every_occurrence(self):
        element_type = tool.Ifc.get_entity(add_wall_type())
        first = add_occurrence(element_type, (0.0, 0.0, 0.0))
        second = add_occurrence(element_type, (0.0, 10.0, 0.0))
        elements = [tool.Ifc.get_entity(o) for o in (first, second)]
        before = [world_bbox(e) for e in elements]
        set_origin_to_cursor(first)
        assert close(tuple(first.location), CURSOR)
        assert close(tuple(second.location), (3.0, 10.0, 0.0))
        assert all(close(world_bbox(e), b) for e, b in zip(elements, before))
        sources = {body(o).Items[0].MappingSource for o in (first, second)}
        assert sources == set(element_type.RepresentationMaps)

    def test_a_rotated_occurrence_moves_its_origin_in_its_own_frame(self):
        element_type = tool.Ifc.get_entity(add_wall_type())
        first = add_occurrence(element_type, (0.0, 0.0, 0.0))
        second = add_occurrence(element_type, (0.0, 10.0, 0.0), rotation_z=math.pi / 2)
        before = world_bbox(tool.Ifc.get_entity(second))
        set_origin_to_cursor(first)
        # The type's local X becomes the rotated occurrence's world Y.
        assert close(tuple(second.location), (0.0, 13.0, 0.0))
        assert close(world_bbox(tool.Ifc.get_entity(second)), before)

    def test_changing_the_origin_of_a_type_moves_every_occurrence(self):
        type_obj = add_wall_type()
        element_type = tool.Ifc.get_entity(type_obj)
        occurrence = add_occurrence(element_type, (0.0, 10.0, 0.0))
        before = world_bbox(tool.Ifc.get_entity(occurrence))
        local_move = type_obj.matrix_world.inverted() @ Vector(CURSOR)
        # Type objects live in a hidden collection and can't be selected here, so name it.
        bpy.context.scene.cursor.location = CURSOR
        bpy.ops.bim.override_origin_set(obj=type_obj.name, origin_type="ORIGIN_CURSOR")
        assert close(tuple(occurrence.location), tuple(Vector((0.0, 10.0, 0.0)) + local_move))
        assert close(world_bbox(tool.Ifc.get_entity(occurrence)), before)

    def test_a_structural_curve_member_keeps_its_world_position(self):
        obj = add_structural_item("IfcStructuralCurveMember", "EDGE")
        element = tool.Ifc.get_entity(obj)
        before = world_topology(element)
        set_origin_to_cursor(obj)
        assert tuple(obj.location) == CURSOR
        assert close(world_topology(element), before)
        assert body(obj).RepresentationType == "Edge"

    def test_a_structural_surface_member_keeps_its_world_position_and_plane(self):
        obj = add_structural_item("IfcStructuralSurfaceMember", "FACE")
        element = tool.Ifc.get_entity(obj)
        before = world_topology(element)
        plane = body(obj).Items[0].FaceSurface.Position
        axes = (plane.Axis, plane.RefDirection)
        set_origin_to_cursor(obj)
        assert tuple(obj.location) == CURSOR
        assert close(world_topology(element), before)
        face = body(obj).Items[0]
        assert face.is_a("IfcFaceSurface")
        assert (face.FaceSurface.Position.Axis, face.FaceSurface.Position.RefDirection) == axes

    def test_a_structural_point_connection_keeps_its_world_position(self):
        bpy.context.scene.cursor.location = (1.0, 2.0, 0.0)
        obj = add_structural_item("IfcStructuralPointConnection", "VERTEX")
        element = tool.Ifc.get_entity(obj)
        before = world_topology(element)
        set_origin_to_cursor(obj)
        assert tuple(obj.location) == CURSOR
        assert close(world_topology(element), before)
        assert body(obj).RepresentationType == "Vertex"
