# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
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
import ifcopenshell
import ifcopenshell.api
import ifcopenshell.api.aggregate
import ifcopenshell.api.feature
import ifcopenshell.api.nest
import ifcopenshell.api.root
import ifcopenshell.api.spatial
import ifcopenshell.util.representation
import numpy as np
import shapely
from mathutils import Matrix, Vector

import bonsai.core.tool
import bonsai.tool as tool
from bonsai.tool.spatial import Spatial as subject
from bonsai.tool.spatial import _bump_geom_cache_token
from test.bim.bootstrap import NewFile


class TestImplementsTool(NewFile):
    def test_run(self):
        assert isinstance(subject(), bonsai.core.tool.Spatial)


class TestCanContain(NewFile):
    def test_a_spatial_structure_element_can_contain_an_element(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        structure = ifc.createIfcSite()
        structure_obj = bpy.data.objects.new("Object", None)
        tool.Ifc.link(structure, structure_obj)
        element = ifc.createIfcWall()
        assert subject.can_contain(structure, element) is True

    def test_a_spatial_structure_element_can_contain_an_element_ifc2x3(self):
        ifc = ifcopenshell.file(schema="IFC2X3")
        tool.Ifc.set(ifc)
        structure = ifc.createIfcSite()
        structure_obj = bpy.data.objects.new("Object", None)
        tool.Ifc.link(structure, structure_obj)
        element = ifc.createIfcWall()
        assert subject.can_contain(structure, element) is True

    def test_a_spatial_zone_element_cannot_contain_an_element(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        structure = ifc.createIfcSpatialZone()
        structure_obj = bpy.data.objects.new("Object", None)
        tool.Ifc.link(structure, structure_obj)
        element = ifc.createIfcWall()
        assert subject.can_contain(structure, element) is False

    def test_a_non_spatial_element_cannot_contain_anything(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        structure = ifc.createIfcWall()
        structure_obj = bpy.data.objects.new("Object", None)
        tool.Ifc.link(structure, structure_obj)
        element = ifc.createIfcWall()
        assert subject.can_contain(structure, element) is False

    def test_a_non_element_cannot_be_contained(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        structure = ifc.createIfcSite()
        structure_obj = bpy.data.objects.new("Object", None)
        tool.Ifc.link(structure, structure_obj)
        element = ifc.createIfcTask()
        assert subject.can_contain(structure, element) is False

    def test_other_non_elements_that_have_a_contained_in_structure_attribute_can_be_contained(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        structure = ifc.createIfcSite()
        structure_obj = bpy.data.objects.new("Object", None)
        tool.Ifc.link(structure, structure_obj)
        element = ifc.createIfcGrid()
        assert subject.can_contain(structure, element) is True


class TestCanReference(NewFile):
    def test_an_element_can_reference_a_spatial_element(self):
        ifc = ifcopenshell.file()
        assert subject.can_reference(ifc.createIfcSite(), ifc.createIfcWall()) is True

    def test_an_element_can_reference_a_spatial_element_ifc2x3(self):
        ifc = ifcopenshell.file(schema="IFC2X3")
        tool.Ifc.set(ifc)
        assert subject.can_reference(ifc.createIfcSite(), ifc.createIfcWall()) is True

    def test_a_non_spatial_element_cannot_reference_anything(self):
        ifc = ifcopenshell.file()
        assert subject.can_reference(ifc.createIfcWall(), ifc.createIfcWall()) is False

    def test_a_non_element_cannot_reference_anything(self):
        ifc = ifcopenshell.file()
        assert subject.can_reference(ifc.createIfcSite(), ifc.createIfcTask()) is False


class TestDisableEditing(NewFile):
    def test_run(self):
        obj = bpy.data.objects.new("Object", None)
        subject.enable_editing(obj)
        subject.disable_editing(obj)
        props = tool.Spatial.get_object_spatial_props(obj)
        assert props.is_editing is False


class TestDuplicateObjectAndData(NewFile):
    def test_run(self):
        obj = bpy.data.objects.new("Object", bpy.data.meshes.new("Mesh"))
        new_obj = subject.duplicate_object_and_data(obj)
        assert new_obj != obj
        assert new_obj.data != obj.data
        obj = bpy.data.objects.new("Object", None)
        new_obj = subject.duplicate_object_and_data(obj)
        assert new_obj != obj
        assert new_obj.data is None


class TestEnableEditing(NewFile):
    def test_run(self):
        obj = bpy.data.objects.new("Object", None)
        subject.enable_editing(obj)
        props = tool.Spatial.get_object_spatial_props(obj)
        assert props.is_editing is True


class TestGetContainer(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        site = ifc.createIfcSite()
        wall = ifc.createIfcWall()
        ifcopenshell.api.spatial.assign_container(ifc, products=[wall], relating_structure=site)
        assert subject.get_container(wall) == site


class TestGetRootElement(NewFile):
    def test_a_door_filling_a_wall_is_its_own_root_element(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        wall = ifc.createIfcWall()
        opening = ifc.createIfcOpeningElement()
        door = ifc.createIfcDoor()
        ifcopenshell.api.feature.add_feature(ifc, feature=opening, element=wall)
        ifcopenshell.api.feature.add_filling(ifc, opening=opening, element=door)
        assert subject.get_root_element(door) == door

    def test_an_aggregated_element_walks_to_its_aggregate_root(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        assembly = ifc.createIfcElementAssembly()
        beam = ifc.createIfcBeam()
        ifcopenshell.api.aggregate.assign_object(ifc, products=[beam], relating_object=assembly)
        assert subject.get_root_element(beam) == assembly

    def test_a_nested_element_walks_to_its_nest_root(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        parent_task = ifc.createIfcTask()
        child_task = ifc.createIfcTask()
        ifcopenshell.api.nest.assign_object(ifc, related_objects=[child_task], relating_object=parent_task)
        assert subject.get_root_element(child_task) == parent_task

    def test_a_loose_element_is_its_own_root(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        wall = ifc.createIfcWall()
        assert subject.get_root_element(wall) == wall


class TestGetDecomposedElements(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        site = ifc.createIfcSite()
        wall = ifc.createIfcWall()
        ifcopenshell.api.spatial.assign_container(ifc, products=[wall], relating_structure=site)
        assert subject.get_decomposed_elements(site) == {wall}


class TestGetObjectMatrix(NewFile):
    def test_run(self):
        obj = bpy.data.objects.new("Object", None)
        assert subject.get_object_matrix(obj) == obj.matrix_world


class TestGetRelativeObjectMatrix(NewFile):
    def test_run(self):
        obj = bpy.data.objects.new("Object", None)
        relative_obj = bpy.data.objects.new("Object", None)
        relative_obj.matrix_world[0][3] = 1
        assert subject.get_relative_object_matrix(obj, relative_obj)[0][3] == -1


class TestRunRootCopyClass(NewFile):
    def test_nothing(self):
        pass


class TestRunSpatialAssignContainer(NewFile):
    def test_nothing(self):
        pass


class TestSelectObject(NewFile):
    def test_run(self):
        obj = bpy.data.objects.new("Object", None)
        bpy.context.scene.collection.objects.link(obj)
        subject.select_object(obj)
        assert obj in bpy.context.selected_objects


class TestSetActiveObject(NewFile):
    def test_run(self):
        obj = bpy.data.objects.new("Object", None)
        bpy.context.scene.collection.objects.link(obj)
        subject.set_active_object(obj)
        assert bpy.context.view_layer.objects.active == obj
        assert obj in bpy.context.selected_objects


class TestSetRelativeObjectMatrix(NewFile):
    def test_run(self):
        obj = bpy.data.objects.new("Object", None)
        relative_obj = bpy.data.objects.new("Object", None)
        relative_obj.matrix_world[0][3] = 1
        matrix = Matrix()
        matrix[0][3] = 1
        subject.set_relative_object_matrix(obj, relative_obj, matrix)
        assert obj.matrix_world[0][3] == 2


class TestSelectProducts(NewFile):
    def test_select_products(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        product = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcWall")
        obj = bpy.data.objects.new("Object", None)
        bpy.context.scene.collection.objects.link(obj)
        tool.Ifc.link(product, obj)
        subject.select_products([product])
        assert obj in bpy.context.selected_objects


class _BlockHelper:
    """Shared helpers for creating IFC walls/slabs with solid-block representations."""

    @staticmethod
    def create_wall(ifc, height=10.0):
        """Create an IFC wall with a 10x10x{height} block representation from z=0."""
        ctx = ifcopenshell.util.representation.get_context(ifc, "Model", "Body", "MODEL_VIEW")
        wall = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcWall")
        placement_2d = ifc.createIfcAxis2Placement2D(ifc.createIfcCartesianPoint([0.0, 0.0]))
        profile = ifc.createIfcRectangleProfileDef("AREA", None, placement_2d, 10.0, 10.0)
        placement_3d = ifc.createIfcAxis2Placement3D(ifc.createIfcCartesianPoint([0.0, 0.0, 0.0]))
        extrusion = ifc.createIfcExtrudedAreaSolid(
            profile, placement_3d, ifc.createIfcDirection([0.0, 0.0, 1.0]), height
        )
        shape_rep = ifc.createIfcShapeRepresentation(ctx, "Body", "SweptSolid", [extrusion])
        wall.Representation = ifc.createIfcProductDefinitionShape(None, None, [shape_rep])
        return wall, extrusion

    @staticmethod
    def create_thin_wall(ifc, cx, cy, width, depth, height=10.0):
        """Create an IFC wall with a thin block representation centered at (cx, cy)."""
        ctx = ifcopenshell.util.representation.get_context(ifc, "Model", "Body", "MODEL_VIEW")
        wall = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcWall")
        placement_2d = ifc.createIfcAxis2Placement2D(ifc.createIfcCartesianPoint([0.0, 0.0]))
        profile = ifc.createIfcRectangleProfileDef("AREA", None, placement_2d, width, depth)
        placement_3d = ifc.createIfcAxis2Placement3D(ifc.createIfcCartesianPoint([cx, cy, 0.0]))
        extrusion = ifc.createIfcExtrudedAreaSolid(
            profile, placement_3d, ifc.createIfcDirection([0.0, 0.0, 1.0]), height
        )
        shape_rep = ifc.createIfcShapeRepresentation(ctx, "Body", "SweptSolid", [extrusion])
        wall.Representation = ifc.createIfcProductDefinitionShape(None, None, [shape_rep])
        return wall

    @staticmethod
    def create_slab(ifc, z=4.0):
        """Create an IfcSlab with a 12x12x1.0 block representation at bottom_z={z}."""
        ctx = ifcopenshell.util.representation.get_context(ifc, "Model", "Body", "MODEL_VIEW")
        slab = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcSlab")
        placement_2d = ifc.createIfcAxis2Placement2D(ifc.createIfcCartesianPoint([0.0, 0.0]))
        profile = ifc.createIfcRectangleProfileDef("AREA", None, placement_2d, 12.0, 12.0)
        placement_3d = ifc.createIfcAxis2Placement3D(ifc.createIfcCartesianPoint([0.0, 0.0, z]))
        extrusion = ifc.createIfcExtrudedAreaSolid(profile, placement_3d, ifc.createIfcDirection([0.0, 0.0, 1.0]), 1.0)
        shape_rep = ifc.createIfcShapeRepresentation(ctx, "Body", "SweptSolid", [extrusion])
        slab.Representation = ifc.createIfcProductDefinitionShape(None, None, [shape_rep])


class TestGenerateSpace(NewFile):
    def test_generate_space_at_cursor(self):
        bpy.ops.bim.create_project()
        ifc = tool.Ifc.get()
        # The wall block spans z=0..10, bisects to a 10x10 polygon at cut_z.
        _BlockHelper.create_wall(ifc, height=10.0)
        bpy.context.scene.cursor.location = (0, 0, 0)

        bpy.ops.bim.generate_space()
        space = bpy.data.objects["IfcSpace/Space"]
        mesh = space.data
        assert isinstance(mesh, bpy.types.Mesh)
        assert len(mesh.vertices) == 8
        TEST_VERTS = sorted(
            (
                ((5.0, 5.0, 10.0)),
                ((-5.0, 5.0, 10.0)),
                ((-5.0, -5.0, 10.0)),
                ((5.0, -5.0, 10.0)),
                ((-5.0, 5.0, 0.0)),
                ((-5.0, -5.0, 0.0)),
                ((5.0, 5.0, 0.0)),
                ((5.0, -5.0, 0.0)),
            )
        )
        assert np.allclose(TEST_VERTS, sorted([tuple(v.co) for v in mesh.vertices]))

    def test_regenerate_space_preserves_z_location(self):
        bpy.ops.bim.create_project()
        ifc = tool.Ifc.get()
        _BlockHelper.create_wall(ifc, height=10.0)
        bpy.context.scene.cursor.location = (0, 0, 0)

        bpy.ops.bim.generate_space()
        space = bpy.data.objects["IfcSpace/Space"]
        space.location.z = 5
        bpy.context.view_layer.update()

        bpy.context.view_layer.objects.active = space
        space.select_set(True)

        bpy.ops.bim.generate_space()

        assert np.isclose(space.location.z, 5), f"Expected z=5, got {space.location.z}"

    def test_auto_space_height_from_slab_above(self):
        bpy.ops.bim.create_project()
        ifc = tool.Ifc.get()
        _BlockHelper.create_wall(ifc, height=10.0)
        _BlockHelper.create_slab(ifc, z=4.0)
        bpy.context.scene.cursor.location = (0, 0, 0)

        bpy.ops.bim.generate_space()
        space = bpy.data.objects["IfcSpace/Space"]
        assert np.isclose(space.dimensions.z, 4, atol=0.1), f"Expected height ~4, got {space.dimensions.z}"

    def test_forced_space_height(self):
        bpy.ops.bim.create_project()
        ifc = tool.Ifc.get()
        _BlockHelper.create_wall(ifc, height=10.0)
        bpy.context.scene.cursor.location = (0, 0, 0)

        spatial_props = tool.Spatial.get_spatial_props()
        spatial_props.force_space_height = True
        spatial_props.space_height = 5
        bpy.ops.bim.generate_space()
        space = bpy.data.objects["IfcSpace/Space"]
        assert np.isclose(space.dimensions.z, 5, atol=0.1), f"Expected height 5, got {space.dimensions.z}"

    def test_auto_space_height_fallback_no_slab(self):
        bpy.ops.bim.create_project()
        ifc = tool.Ifc.get()
        _BlockHelper.create_wall(ifc, height=10.0)
        bpy.context.scene.cursor.location = (0, 0, 0)

        spatial_props = tool.Spatial.get_spatial_props()
        spatial_props.force_space_height = False
        bpy.ops.bim.generate_space()
        space = bpy.data.objects["IfcSpace/Space"]
        assert space.dimensions.z > 0, f"Expected positive height, got {space.dimensions.z}"

    def test_apply_space_height_to_selection(self):
        bpy.ops.bim.create_project()
        ifc = tool.Ifc.get()
        _BlockHelper.create_wall(ifc, height=10.0)
        bpy.context.scene.cursor.location = (0, 0, 0)

        bpy.ops.bim.generate_space()
        space = bpy.data.objects["IfcSpace/Space"]

        spatial_props = tool.Spatial.get_spatial_props()
        spatial_props.space_height = 6
        bpy.context.view_layer.objects.active = space
        space.hide_viewport = False
        space.select_set(True)

        bpy.ops.bim.apply_space_height_to_selection()
        bpy.context.view_layer.update()
        assert np.isclose(space.dimensions.z, 6, atol=0.1), f"Expected height 6, got {space.dimensions.z}"

    def test_cache_survives_second_generation(self):
        bpy.ops.bim.create_project()
        ifc = tool.Ifc.get()
        _BlockHelper.create_wall(ifc, height=10.0)
        bpy.context.scene.cursor.location = (0, 0, 0)

        bpy.ops.bim.generate_space()
        space1 = bpy.data.objects["IfcSpace/Space"]
        height1 = space1.dimensions.z

        bpy.ops.bim.generate_space()
        space2 = bpy.data.objects["IfcSpace/Space"]
        height2 = space2.dimensions.z

        assert np.isclose(height1, height2, atol=0.1), f"Cache changed height: {height1} vs {height2}"

    def test_regenerate_after_wall_height_change(self):
        bpy.ops.bim.create_project()
        ifc = tool.Ifc.get()
        wall, extrusion = _BlockHelper.create_wall(ifc, height=10.0)
        bpy.context.scene.cursor.location = (0, 0, 0)

        bpy.ops.bim.generate_space()
        space = bpy.data.objects["IfcSpace/Space"]
        original_height = space.dimensions.z

        # Modify the IFC representation to change the wall height.
        extrusion.Depth = 15.0
        _bump_geom_cache_token()

        bpy.context.view_layer.objects.active = space
        space.select_set(True)

        bpy.ops.bim.generate_space()
        new_height = space.dimensions.z
        assert new_height != original_height or new_height > 0

    def test_regenerate_space_from_centered_cube_representation(self):
        bpy.ops.bim.create_project()
        ifc = tool.Ifc.get()
        _BlockHelper.create_wall(ifc, height=10.0)
        scene = bpy.context.scene
        scene.cursor.location = (0, 0, 0)

        # Create a space with a unit cube PolygonalFaceSet centered at local origin.
        ctx = ifcopenshell.util.representation.get_context(ifc, "Model", "Body", "MODEL_VIEW")
        points = ifc.createIfcCartesianPointList3D(
            [
                (-0.5, -0.5, -0.5),
                (-0.5, -0.5, 0.5),
                (-0.5, 0.5, -0.5),
                (-0.5, 0.5, 0.5),
                (0.5, -0.5, -0.5),
                (0.5, -0.5, 0.5),
                (0.5, 0.5, -0.5),
                (0.5, 0.5, 0.5),
            ]
        )
        faces = [
            ifc.createIfcIndexedPolygonalFace([1, 2, 4, 3]),
            ifc.createIfcIndexedPolygonalFace([3, 4, 8, 7]),
            ifc.createIfcIndexedPolygonalFace([7, 8, 6, 5]),
            ifc.createIfcIndexedPolygonalFace([5, 6, 2, 1]),
            ifc.createIfcIndexedPolygonalFace([3, 7, 5, 1]),
            ifc.createIfcIndexedPolygonalFace([8, 4, 2, 6]),
        ]
        face_set = ifc.createIfcPolygonalFaceSet(points, True, faces)
        shape_rep = ifc.createIfcShapeRepresentation(ctx, "Body", "Tessellation", [face_set])

        space_element = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcSpace")
        space_element.Representation = ifc.createIfcProductDefinitionShape(None, None, [shape_rep])

        bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 5))
        obj = bpy.data.objects["Cube"]
        scene.collection.objects.link(obj)
        tool.Ifc.link(space_element, obj)
        bpy.context.view_layer.update()
        obj.name = "MySpace"

        # Check the cube's world bottom Z before regeneration.
        bottom_z = (obj.matrix_world @ Vector(obj.bound_box[0])).z
        assert np.isclose(bottom_z, 4.5), f"Expected bottom_z=4.5, got {bottom_z}"

        # Regenerate the space.
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.bim.generate_space()

        mesh = obj.data
        assert isinstance(mesh, bpy.types.Mesh)
        verts = [v.co.z for v in mesh.vertices]
        min_z = min(verts)
        max_z = max(verts)
        assert min_z >= 0, f"Expected extrusion to start at local z>=0, got min_z={min_z}"
        assert max_z > 0, f"Expected extrusion to have positive height, got max_z={max_z}"
        assert np.isclose(obj.location.z, 4.5, atol=0.01), f"Expected location.z=4.5, got {obj.location.z}"


class TestGenerateSpaceSlopedRoof(NewFile):
    def _create_shed_roof(self, ifc, z=4.0, rise=3.0):
        """Create an IfcRoof whose underside is a sloped plane across the footprint.

        Triangular prism: vertical profile (in the y-z plane) extruded along +x.
        Profile points (u, v) with placement loc=(-5, 0, z), axis=(1,0,0),
        ref=(0,0,1). The local frame maps u to world +z (u=0 -> z, u=rise ->
        z+rise) and v to world -y (v=-5 -> y=+5, v=+5 -> y=-5):
                       (0,-5)    -> world (-5, +5, z)      eave (low) at north
                       (rise,-5) -> world (-5, +5, z+rise) vertical edge
                       (rise,5)  -> world (-5, -5, z+rise) ridge at south
        The underside is the sloped face from (y=+5, z) to (y=-5, z+rise).
        ExtrudedDirection (0,0,1) is local, mapping to world +x; depth 10 spans
        x in [-5, 5].
        """
        ctx = ifcopenshell.util.representation.get_context(ifc, "Model", "Body", "MODEL_VIEW")
        roof = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcRoof")
        pts = [
            ifc.createIfcCartesianPoint((0.0, -5.0)),
            ifc.createIfcCartesianPoint((float(rise), -5.0)),
            ifc.createIfcCartesianPoint((float(rise), 5.0)),
        ]
        polyline = ifc.createIfcPolyline(pts)
        profile = ifc.createIfcArbitraryClosedProfileDef(ProfileType="CURVE", OuterCurve=polyline)
        placement = ifc.createIfcAxis2Placement3D(
            ifc.createIfcCartesianPoint((-5.0, 0.0, z)),
            ifc.createIfcDirection((1.0, 0.0, 0.0)),
            ifc.createIfcDirection((0.0, 0.0, 1.0)),
        )
        extrude_dir = ifc.createIfcDirection((0.0, 0.0, 1.0))
        solid = ifc.createIfcExtrudedAreaSolid(profile, placement, extrude_dir, 10.0)
        rep = ifc.createIfcShapeRepresentation(ctx, "Body", "SweptSolid", [solid])
        ifcopenshell.api.geometry.assign_representation(ifc, product=roof, representation=rep)
        return roof

    def test_generate_space_under_shed_roof(self):
        bpy.ops.bim.create_project()
        ifc = tool.Ifc.get()
        _BlockHelper.create_thin_wall(ifc, 0.0, 4.8, 10.0, 0.4)
        _BlockHelper.create_thin_wall(ifc, 0.0, -4.8, 10.0, 0.4)
        _BlockHelper.create_thin_wall(ifc, 4.8, 0.0, 0.4, 10.0)
        _BlockHelper.create_thin_wall(ifc, -4.8, 0.0, 0.4, 10.0)
        self._create_shed_roof(ifc, z=4.0, rise=3.0)
        bpy.context.scene.cursor.location = (0, 0, 0)

        bpy.ops.bim.generate_space()
        space = bpy.data.objects["IfcSpace/Space"]
        mesh = space.data
        assert isinstance(mesh, bpy.types.Mesh)
        verts = np.array([v.co for v in mesh.vertices])
        min_z = verts[:, 2].min()
        max_z = verts[:, 2].max()
        assert min_z >= -0.1
        assert max_z > 0
        top_z_north = max([v[2] for v in verts if v[1] > 1])
        top_z_south = max([v[2] for v in verts if v[1] < -1])
        assert abs(top_z_north - top_z_south) > 0.05, f"Top should slope along y: {top_z_north} vs {top_z_south}"


class TestSpaceVolumeStrategy(NewFile):
    def test_vertical_box_returns_extrude_clip(self):
        bpy.ops.bim.create_project()
        ifc = tool.Ifc.get()
        _BlockHelper.create_wall(ifc, height=10.0)
        _BlockHelper.create_slab(ifc, z=4.0)
        space_polygon = shapely.box(-5, -5, 5, 5)
        strategy, top, bottom = subject.get_space_volume_strategy(space_polygon, 0.0, [ifc.by_type("IfcWall")[0]])
        assert strategy == "EXTRUDE_CLIP"
        assert len(top) == 1
        assert len(bottom) == 0

    @staticmethod
    def _create_sloped_slab(ifc, z=4.0, rise=3.0):
        """Create an IfcSlab whose underside is a sloped plane across the footprint."""
        ctx = ifcopenshell.util.representation.get_context(ifc, "Model", "Body", "MODEL_VIEW")
        slab = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcSlab")
        pts = [
            ifc.createIfcCartesianPoint((0.0, -5.0)),
            ifc.createIfcCartesianPoint((float(rise), -5.0)),
            ifc.createIfcCartesianPoint((float(rise), 5.0)),
        ]
        polyline = ifc.createIfcPolyline(pts)
        profile = ifc.createIfcArbitraryClosedProfileDef(ProfileType="CURVE", OuterCurve=polyline)
        placement = ifc.createIfcAxis2Placement3D(
            ifc.createIfcCartesianPoint((-5.0, 0.0, z)),
            ifc.createIfcDirection((1.0, 0.0, 0.0)),
            ifc.createIfcDirection((0.0, 0.0, 1.0)),
        )
        extrude_dir = ifc.createIfcDirection((0.0, 0.0, 1.0))
        solid = ifc.createIfcExtrudedAreaSolid(profile, placement, extrude_dir, 10.0)
        rep = ifc.createIfcShapeRepresentation(ctx, "Body", "SweptSolid", [solid])
        ifcopenshell.api.geometry.assign_representation(ifc, product=slab, representation=rep)
        return slab

    def test_sloped_slab_returns_extrude_clip(self):
        bpy.ops.bim.create_project()
        ifc = tool.Ifc.get()
        self._create_sloped_slab(ifc, z=4.0, rise=3.0)
        space_polygon = shapely.box(-5, -5, 5, 5)
        strategy, top, bottom = subject.get_space_volume_strategy(space_polygon, 0.0, [])
        assert strategy == "EXTRUDE_CLIP"
        assert len(top) == 1
        assert len(bottom) == 0

class TestGenerateSpaceSlopedRoof(NewFile):
