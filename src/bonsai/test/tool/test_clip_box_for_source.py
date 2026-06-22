# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026 Dion Moult <dion@thinkmoult.com>
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

import bpy
import ifcopenshell
import ifcopenshell.api.spatial
import ifcopenshell.api.type
import pytest
from mathutils import Vector

import bonsai.tool as tool
from test.bim.bootstrap import NewFile

pytestmark = pytest.mark.clip_box


def _make_ifc_cube(ifc, ifc_class, location=(0.0, 0.0, 0.0), size=2.0):
    """Real bpy cube + ifc entity, linked. ``size`` is the cube edge length."""
    bpy.ops.mesh.primitive_cube_add(size=size, location=location)
    obj = bpy.context.active_object
    entity = ifc.create_entity(ifc_class)
    tool.Ifc.link(entity, obj)
    return entity, obj


class TestWorldBboxMatrix(NewFile):
    def test_two_cubes_returns_centred_aabb_matrix(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        wall_a, _ = _make_ifc_cube(ifc, "IfcWall", location=(0.0, 0.0, 0.0), size=2.0)
        wall_b, _ = _make_ifc_cube(ifc, "IfcWall", location=(4.0, 0.0, 0.0), size=2.0)

        matrix = tool.ClipBox._world_bbox_matrix_for_elements([wall_a, wall_b])

        assert matrix is not None
        translation, _, scale = matrix.decompose()
        # World AABB: x in [-1, 5], y/z in [-1, 1] -> center (2, 0, 0), half (3, 1, 1).
        assert translation.x == pytest.approx(2.0)
        assert translation.y == pytest.approx(0.0)
        assert translation.z == pytest.approx(0.0)
        assert scale.x == pytest.approx(3.0)
        assert scale.y == pytest.approx(1.0)
        assert scale.z == pytest.approx(1.0)

    def test_empty_iterable_returns_none(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        assert tool.ClipBox._world_bbox_matrix_for_elements([]) is None

    def test_element_without_blender_object_is_skipped(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        wall_a, _ = _make_ifc_cube(ifc, "IfcWall", location=(0.0, 0.0, 0.0), size=2.0)
        unbound = ifc.create_entity("IfcWall")

        matrix = tool.ClipBox._world_bbox_matrix_for_elements([wall_a, unbound])

        assert matrix is not None
        translation, _, scale = matrix.decompose()
        assert translation.x == pytest.approx(0.0)
        assert translation.y == pytest.approx(0.0)
        assert translation.z == pytest.approx(0.0)
        assert scale.x == pytest.approx(1.0)

    def test_all_filtered_returns_none(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        unbound_a = ifc.create_entity("IfcWall")
        unbound_b = ifc.create_entity("IfcWall")
        assert tool.ClipBox._world_bbox_matrix_for_elements([unbound_a, unbound_b]) is None

    def test_coincident_cubes_return_invertible_matrix(self):
        # Two cubes at the same location collapse to a zero-volume AABB.
        # The half-extent floor must keep the matrix invertible so downstream
        # clip-plane math doesn't divide through a singular transform.
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        wall_a, _ = _make_ifc_cube(ifc, "IfcWall", location=(0.0, 0.0, 0.0), size=0.0001)
        wall_b, _ = _make_ifc_cube(ifc, "IfcWall", location=(0.0, 0.0, 0.0), size=0.0001)

        matrix = tool.ClipBox._world_bbox_matrix_for_elements([wall_a, wall_b])

        assert matrix is not None
        # A zero determinant means the matrix would map every point onto a
        # subspace — the floor must prevent that.
        assert matrix.determinant() != 0.0


class TestCameraFrustumMatrix(NewFile):
    def _make_camera(self, location=(0.0, 0.0, 0.0), rotation=None):
        cam_data = bpy.data.cameras.new("DrawingCam")
        cam_data.type = "ORTHO"
        obj = bpy.data.objects.new("DrawingCam", cam_data)
        bpy.context.scene.collection.objects.link(obj)
        obj.location = location
        if rotation is not None:
            obj.rotation_euler = rotation
        bpy.context.view_layer.update()
        return obj

    def test_identity_camera_width_height_drive_in_plane_extents(self):
        obj = self._make_camera()
        cam = obj.data
        cam.clip_start = 0.0
        cam.clip_end = 10.0
        cam.BIMCameraProperties.width = 8.0
        cam.BIMCameraProperties.height = 6.0

        matrix = tool.ClipBox._camera_frustum_matrix(obj)

        translation, _, scale = matrix.decompose()
        # Identity rotation: box centre at (0, 0, -5) in world (cameras look down -Z).
        assert translation.x == pytest.approx(0.0)
        assert translation.y == pytest.approx(0.0)
        assert translation.z == pytest.approx(-5.0)
        # Half-extents: width/2, height/2, (clip_end - clip_start) / 2.
        assert scale.x == pytest.approx(4.0)
        assert scale.y == pytest.approx(3.0)
        assert scale.z == pytest.approx(5.0)

    def test_rotated_camera_preserves_rotation_in_matrix(self):
        obj = self._make_camera(rotation=(0.0, math.radians(90), 0.0))
        cam = obj.data
        cam.clip_start = 0.0
        cam.clip_end = 4.0
        cam.BIMCameraProperties.width = 2.0
        cam.BIMCameraProperties.height = 2.0

        matrix = tool.ClipBox._camera_frustum_matrix(obj)

        _, rotation, scale = matrix.decompose()
        # Scale is rotation-invariant.
        assert scale.x == pytest.approx(1.0)
        assert scale.y == pytest.approx(1.0)
        assert scale.z == pytest.approx(2.0)
        # The rotation component matches the camera's own rotation; quaternion
        # dot product near unit magnitude means the orientations agree.
        cam_rot = obj.matrix_world.decompose()[1]
        assert abs(cam_rot.dot(rotation)) > 0.999

    def test_returns_none_when_width_height_zero(self):
        # A camera without usable drawing extents (width or height ≤ 0)
        # cannot define a clip volume — caller surfaces ERROR + CANCELLED.
        obj = self._make_camera()
        cam = obj.data
        cam.clip_start = 0.0
        cam.clip_end = 10.0
        cam.BIMCameraProperties.width = 8.0
        # height stays at the BIMCameraProperties default (50). We can't set
        # height=0 here because the update callback divides width/height.
        # Set width=0 directly via the underlying ID property instead, which
        # bypasses the registered FloatProperty update path.
        cam.BIMCameraProperties["width"] = 0.0

        assert tool.ClipBox._camera_frustum_matrix(obj) is None


class TestIterElementsForSource(NewFile):
    def test_no_ifc_file_returns_empty(self):
        # NewFile leaves IfcStore purged; tool.Ifc.get() is None here.
        assert tool.ClipBox.iter_elements_for_source("SPATIAL", "1") == []

    def test_unknown_kind_returns_empty(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        wall = ifc.create_entity("IfcWall")
        assert tool.ClipBox.iter_elements_for_source("UNKNOWN_KIND", str(wall.id())) == []

    def test_non_integer_source_id_returns_empty(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        assert tool.ClipBox.iter_elements_for_source("SPATIAL", "not_an_int") == []

    def test_unresolved_source_id_returns_empty(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        assert tool.ClipBox.iter_elements_for_source("SPATIAL", "999999") == []

    def test_spatial_returns_decomposition(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        storey = ifc.create_entity("IfcBuildingStorey")
        wall_a = ifc.create_entity("IfcWall")
        wall_b = ifc.create_entity("IfcWall")
        ifcopenshell.api.spatial.assign_container(ifc, products=[wall_a, wall_b], relating_structure=storey)

        result = tool.ClipBox.iter_elements_for_source("SPATIAL", str(storey.id()))

        assert set(result) == {wall_a, wall_b}

    def test_type_returns_occurrences(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        wall_type = ifc.create_entity("IfcWallType")
        wall_a = ifc.create_entity("IfcWall")
        wall_b = ifc.create_entity("IfcWall")
        ifcopenshell.api.type.assign_type(ifc, related_objects=[wall_a, wall_b], relating_type=wall_type)

        result = tool.ClipBox.iter_elements_for_source("TYPE", str(wall_type.id()))

        assert set(result) == {wall_a, wall_b}

    def test_drawing_returns_drawing_entity(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        drawing = ifc.create_entity("IfcAnnotation", ObjectType="DRAWING")

        result = tool.ClipBox.iter_elements_for_source("DRAWING", str(drawing.id()))

        assert result == [drawing]

    def test_status_invalid_value_returns_empty(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        assert tool.ClipBox.iter_elements_for_source("STATUS", "MADE_UP_STATUS") == []

    def test_class_returns_all_instances_of_ifc_class(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        wall_a = ifc.create_entity("IfcWall")
        wall_b = ifc.create_entity("IfcWall")
        window = ifc.create_entity("IfcWindow")

        result = tool.ClipBox.iter_elements_for_source("CLASS", "IfcWall")

        assert set(result) == {wall_a, wall_b}
        assert window not in result

    def test_class_unknown_ifc_class_returns_empty(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        ifc.create_entity("IfcWall")
        assert tool.ClipBox.iter_elements_for_source("CLASS", "IfcNotARealClass") == []


class TestComputeMatrixForSource(NewFile):
    def test_spatial_aggregates_contained_elements(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        storey = ifc.create_entity("IfcBuildingStorey")
        wall_a, _ = _make_ifc_cube(ifc, "IfcWall", location=(0.0, 0.0, 0.0), size=2.0)
        wall_b, _ = _make_ifc_cube(ifc, "IfcWall", location=(4.0, 0.0, 0.0), size=2.0)
        ifcopenshell.api.spatial.assign_container(ifc, products=[wall_a, wall_b], relating_structure=storey)

        matrix = tool.ClipBox.compute_matrix_for_source("SPATIAL", str(storey.id()))

        assert matrix is not None
        translation, _, scale = matrix.decompose()
        assert translation.x == pytest.approx(2.0)
        assert scale.x == pytest.approx(3.0)

    def test_no_match_returns_none(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        wall_type = ifc.create_entity("IfcWallType")
        # No occurrences linked.
        assert tool.ClipBox.compute_matrix_for_source("TYPE", str(wall_type.id())) is None

    def test_drawing_uses_camera_frustum(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        drawing = ifc.create_entity("IfcAnnotation", ObjectType="DRAWING")
        cam_data = bpy.data.cameras.new("Cam")
        cam_data.type = "ORTHO"
        cam_data.clip_start = 0.0
        cam_data.clip_end = 10.0
        cam_data.BIMCameraProperties.width = 4.0
        cam_data.BIMCameraProperties.height = 4.0
        obj = bpy.data.objects.new("Cam", cam_data)
        bpy.context.scene.collection.objects.link(obj)
        tool.Ifc.link(drawing, obj)

        matrix = tool.ClipBox.compute_matrix_for_source("DRAWING", str(drawing.id()))

        assert matrix is not None
        _, _, scale = matrix.decompose()
        assert scale.x == pytest.approx(2.0)
        assert scale.y == pytest.approx(2.0)
        assert scale.z == pytest.approx(5.0)

    def test_drawing_with_non_camera_returns_none(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        drawing = ifc.create_entity("IfcAnnotation", ObjectType="DRAWING")
        obj = bpy.data.objects.new("NotACamera", None)
        bpy.context.scene.collection.objects.link(obj)
        tool.Ifc.link(drawing, obj)

        assert tool.ClipBox.compute_matrix_for_source("DRAWING", str(drawing.id())) is None

    def test_status_with_no_matching_elements_returns_none(self):
        # STATUS pick with a valid status value but no element carrying that
        # status — the dispatcher must surface "nothing matched" the same way
        # an empty TYPE / MATERIAL pick does.
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        # Create a wall but never assign its Pset_WallCommon.Status — so a
        # STATUS=NEW query finds 0 elements.
        _make_ifc_cube(ifc, "IfcWall", location=(0.0, 0.0, 0.0), size=2.0)

        assert tool.ClipBox.compute_matrix_for_source("STATUS", "NEW") is None


class _FakeRegion:
    def __init__(self, width, height):
        self.width = width
        self.height = height


class _FakeRV3D:
    def __init__(self, view_matrix=()):  # () is a truthy-enough non-None stand-in
        self.view_matrix = view_matrix
        self.updated = False
        self.use_clip_planes = False
        self.clip_planes = None

    def update(self):
        self.updated = True


class TestRegionIsRenderable:
    """``_region_is_renderable`` gates the clip-plane arm against collapsed /
    initializing regions whose ``region_3d.update()`` would CTD Blender inside
    ``GPU_matrix_ortho_set`` (the timer-arm crash this guard fixes)."""

    def test_sized_region_with_view_matrix_is_renderable(self):
        assert tool.ClipBox._region_is_renderable(_FakeRegion(800, 600), _FakeRV3D()) is True

    def test_zero_width_is_not_renderable(self):
        assert tool.ClipBox._region_is_renderable(_FakeRegion(0, 600), _FakeRV3D()) is False

    def test_zero_height_is_not_renderable(self):
        assert tool.ClipBox._region_is_renderable(_FakeRegion(800, 0), _FakeRV3D()) is False

    def test_missing_view_matrix_is_not_renderable(self):
        rv3d = _FakeRV3D()
        rv3d.view_matrix = None
        assert tool.ClipBox._region_is_renderable(_FakeRegion(800, 600), rv3d) is False

    def test_arm_region_early_returns_on_zero_size(self):
        # A collapsed region must never reach temp_override / clip_border /
        # update() — _arm_region short-circuits at the size guard. Positively
        # assert update() was NOT called and no clip state was written, so a
        # regression that drops the guard fails here rather than passing on
        # "didn't crash".
        rv3d = _FakeRV3D()
        tool.ClipBox._arm_region(object(), _FakeRegion(0, 0), rv3d, ())
        assert rv3d.updated is False
        assert rv3d.use_clip_planes is False
        assert rv3d.clip_planes is None
