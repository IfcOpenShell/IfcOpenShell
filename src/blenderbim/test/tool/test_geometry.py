# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
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
import math
import numpy
import ifcopenshell
import test.bim.bootstrap
import blenderbim.core.tool
import blenderbim.tool as tool
from mathutils import Vector
from blenderbim.tool.geometry import Geometry as subject
from blenderbim.bim.ifc import IfcStore


class TestImplementsTool(test.bim.bootstrap.NewFile):
    def test_run(self):
        assert isinstance(subject(), blenderbim.core.tool.Geometry)


class TestChangeObjectData(test.bim.bootstrap.NewFile):
    def test_change_single_object_data(self):
        data1 = bpy.data.meshes.new("Mesh")
        data2 = bpy.data.meshes.new("Mesh")
        obj1 = bpy.data.objects.new("Object", data1)
        obj2 = bpy.data.objects.new("Object", data1)
        subject.change_object_data(obj1, data2, is_global=False)
        assert obj1.data == data2
        assert obj2.data == data1

    def test_change_object_data_globally(self):
        data1 = bpy.data.meshes.new("Mesh")
        data2 = bpy.data.meshes.new("Mesh")
        obj1 = bpy.data.objects.new("Object", data1)
        obj2 = bpy.data.objects.new("Object", data1)
        subject.change_object_data(obj1, data2, is_global=True)
        assert obj1.data == data2
        assert obj2.data == data2


class TestClearModifiers(test.bim.bootstrap.NewFile):
    def test_run(self):
        obj = bpy.data.objects.new("Object", bpy.data.meshes.new("Mesh"))
        obj.modifiers.new("IfcOpeningElement", "BOOLEAN")
        subject.clear_modifiers(obj)
        assert len(obj.modifiers) == 0


class TestCreateDynamicVoids(test.bim.bootstrap.NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        wall = ifc.createIfcWall()
        opening = ifc.createIfcOpeningElement()
        ifcopenshell.api.run("void.add_opening", ifc, opening=opening, element=wall)
        wall_obj = bpy.data.objects.new("Object", bpy.data.meshes.new("Mesh"))
        opening_obj = bpy.data.objects.new("Object", bpy.data.meshes.new("Mesh"))
        tool.Ifc.link(wall, wall_obj)
        tool.Ifc.link(opening, opening_obj)
        subject.create_dynamic_voids(wall_obj)
        modifier = wall_obj.modifiers[0]
        assert modifier.type == "BOOLEAN"
        assert modifier.name == "IfcOpeningElement"
        assert modifier.operation == "DIFFERENCE"
        assert modifier.object == opening_obj
        assert modifier.solver == "EXACT"
        assert modifier.use_self is True


class TestDoesObjectHaveMeshWithFaces(test.bim.bootstrap.NewFile):
    def test_empties_return_false(self):
        obj = bpy.data.objects.new("Object", None)
        assert subject.does_object_have_mesh_with_faces(obj) is False

    def test_non_meshes_return_false(self):
        obj = bpy.data.objects.new("Object", bpy.data.cameras.new("Curve"))
        assert subject.does_object_have_mesh_with_faces(obj) is False

    def test_meshes_without_faces_return_false(self):
        obj = bpy.data.objects.new("Object", bpy.data.meshes.new("Mesh"))
        assert subject.does_object_have_mesh_with_faces(obj) is False

    def test_meshes_with_faces_return_true(self):
        bpy.ops.mesh.primitive_cube_add()
        obj = bpy.data.objects.get("Cube")
        assert subject.does_object_have_mesh_with_faces(obj) is True


class TestDuplicateObjectData(test.bim.bootstrap.NewFile):
    def test_run(self):
        data = bpy.data.meshes.new("Mesh")
        obj = bpy.data.objects.new("Object", data)
        assert subject.duplicate_object_data(obj) == obj.data
        assert obj.data != data
        assert isinstance(obj.data, bpy.types.Mesh)


class TestGetObjectData(test.bim.bootstrap.NewFile):
    def test_run(self):
        data = bpy.data.meshes.new("Mesh")
        obj = bpy.data.objects.new("Object", data)
        assert subject.get_object_data(obj) == obj.data


class TestGetObjectMaterialsWithoutStyles(test.bim.bootstrap.NewFile):
    def test_run(self):
        material1 = bpy.data.materials.new("Material")
        material2 = bpy.data.materials.new("Material")
        material3 = bpy.data.materials.new("Material")
        material3.BIMMaterialProperties.ifc_style_id = 1
        obj = bpy.data.objects.new("Object", bpy.data.meshes.new("Mesh"))
        obj.data.materials.append(material1)
        obj.data.materials.append(material2)
        obj.data.materials.append(material3)
        assert subject.get_object_materials_without_styles(obj) == [material1, material2]


class TestGetRepresentationData(test.bim.bootstrap.NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        context = ifc.createIfcGeometricRepresentationContext()
        representation = ifc.createIfcShapeRepresentation()
        representation.ContextOfItems = context
        data = bpy.data.meshes.new("1/2")
        assert subject.get_representation_data(representation) == data


class TestGetRepresentationName(test.bim.bootstrap.NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        context = ifc.createIfcGeometricRepresentationContext()
        representation = ifc.createIfcShapeRepresentation()
        representation.ContextOfItems = context
        assert subject.get_representation_name(representation) == f"{context.id()}/{representation.id()}"


class TestGetCartesianPointCoordinateOffset(test.bim.bootstrap.NewFile):
    def test_run(self):
        obj = bpy.data.objects.new("Object", None)
        obj.BIMObjectProperties.blender_offset_type = "CARTESIAN_POINT"
        props = bpy.context.scene.BIMGeoreferenceProperties
        props.has_blender_offset = True
        props.blender_eastings = "1"
        props.blender_northings = "2"
        props.blender_orthogonal_height = "3"
        assert subject.get_cartesian_point_coordinate_offset(obj) == Vector((1.0, 2.0, 3.0))

    def test_get_null_if_not_a_cartesian_point_offset_type(self):
        obj = bpy.data.objects.new("Object", None)
        props = bpy.context.scene.BIMGeoreferenceProperties
        props.has_blender_offset = True
        props.blender_eastings = "1"
        props.blender_northings = "2"
        props.blender_orthogonal_height = "3"
        assert subject.get_cartesian_point_coordinate_offset(obj) is None

    def test_get_null_if_no_blender_offset(self):
        obj = bpy.data.objects.new("Object", None)
        obj.BIMObjectProperties.blender_offset_type = "CARTESIAN_POINT"
        props = bpy.context.scene.BIMGeoreferenceProperties
        props.has_blender_offset = False
        assert subject.get_cartesian_point_coordinate_offset(obj) is None


class TestGetTotalRepresentationItems(test.bim.bootstrap.NewFile):
    def test_run(self):
        material1 = bpy.data.materials.new("Material")
        material2 = bpy.data.materials.new("Material")
        obj = bpy.data.objects.new("Object", bpy.data.meshes.new("Mesh"))
        obj.data.materials.append(material1)
        obj.data.materials.append(material2)
        assert subject.get_total_representation_items(obj) == 2


class TestImportRepresentation(test.bim.bootstrap.NewFile):
    def test_importing_a_normal_shape(self):
        ifc = ifcopenshell.open("test/files/basic.ifc")
        tool.Ifc.set(ifc)
        obj = bpy.data.objects.new("Object", bpy.data.meshes.new("Mesh"))
        material = bpy.data.materials.new("Material")
        material.BIMMaterialProperties.ifc_style_id = 101
        element = ifc.by_type("IfcWall")[0]
        tool.Ifc.link(element, obj)
        representation = element.Representation.Representations[0]
        mesh = subject.import_representation(obj, representation, enable_dynamic_voids=False)
        assert len(mesh.polygons) == 12
        assert mesh.materials[0] == material

    def test_importing_non_body_curves(self):
        ifc = ifcopenshell.open("test/files/annotation.ifc")
        tool.Ifc.set(ifc)
        obj = bpy.data.objects.new("Object", bpy.data.meshes.new("Mesh"))
        element = ifc.by_type("IfcWall")[0]
        tool.Ifc.link(element, obj)
        representation = element.Representation.Representations[0]
        mesh = subject.import_representation(obj, representation, enable_dynamic_voids=False)
        assert len(mesh.polygons) == 0
        assert len(mesh.edges) == 4


class TestIsBodyRepresentation(test.bim.bootstrap.NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        context = ifc.createIfcGeometricRepresentationContext()
        representation = ifc.createIfcShapeRepresentation()
        representation.ContextOfItems = context
        context.ContextIdentifier = "Body"
        assert subject.is_body_representation(representation) is True
        context.ContextIdentifier = "Clearance"
        assert subject.is_body_representation(representation) is False


class TestLink(test.bim.bootstrap.NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        element = ifc.createIfcShapeRepresentation()
        obj = bpy.data.meshes.new("Mesh")
        subject.link(element, obj)
        assert obj.BIMMeshProperties.ifc_definition_id == element.id()


class TestRenameObjectData(test.bim.bootstrap.NewFile):
    def test_run(self):
        obj = bpy.data.meshes.new("Mesh")
        subject.rename_object(obj, "name")
        assert obj.name == "name"


class TestResolveMappedRepresentation(test.bim.bootstrap.NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        mapped_representation = ifc.createIfcShapeRepresentation()
        representation = ifc.createIfcShapeRepresentation()
        mapped_representation.RepresentationType = "MappedRepresentation"
        mapped_representation.Items = [
            ifc.createIfcMappedItem(MappingSource=ifc.createIfcRepresentationMap(MappedRepresentation=representation))
        ]
        assert subject.resolve_mapped_representation(mapped_representation) == representation

    def test_return_a_representation_if_not_mapped(self):
        ifc = ifcopenshell.file()
        representation = ifc.createIfcShapeRepresentation()
        assert subject.resolve_mapped_representation(representation) == representation


class TestShouldForceFacetedBrep(test.bim.bootstrap.NewFile):
    def test_run(self):
        result = bpy.context.scene.BIMGeometryProperties.should_force_faceted_brep
        assert subject.should_force_faceted_brep() is result


class TestShouldForceTriangulation(test.bim.bootstrap.NewFile):
    def test_run(self):
        result = bpy.context.scene.BIMGeometryProperties.should_force_triangulation
        assert subject.should_force_triangulation() is result


class TestShouldUsePresentationStyleAssignment(test.bim.bootstrap.NewFile):
    def test_run(self):
        result = bpy.context.scene.BIMGeometryProperties.should_use_presentation_style_assignment
        assert subject.should_use_presentation_style_assignment() is result
