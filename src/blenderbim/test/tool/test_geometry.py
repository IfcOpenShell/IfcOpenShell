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
import numpy as np
import ifcopenshell
import blenderbim.core.tool
import blenderbim.tool as tool
from mathutils import Vector
from test.bim.bootstrap import NewFile
from blenderbim.tool.geometry import Geometry as subject
from blenderbim.bim.ifc import IfcStore


class TestImplementsTool(NewFile):
    def test_run(self):
        assert isinstance(subject(), blenderbim.core.tool.Geometry)


class TestChangeObjectData(NewFile):
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


class TestClearCache(NewFile):
    def test_nothing(self):
        pass  # TODO I don't know how to test this


class TestClearModifiers(NewFile):
    def test_run(self):
        obj = bpy.data.objects.new("Object", bpy.data.meshes.new("Mesh"))
        obj.modifiers.new("IfcOpeningElement", "BOOLEAN")
        subject.clear_modifiers(obj)
        assert len(obj.modifiers) == 0


class TestClearScale(NewFile):
    def test_run(self):
        obj = bpy.data.objects.new("Object", bpy.data.meshes.new("Mesh"))
        obj.scale[0] = 2
        subject.clear_scale(obj)
        assert list(obj.scale) == [1, 1, 1]


class TestDeleteData(NewFile):
    def test_run(self):
        data = bpy.data.meshes.new("Mesh")
        subject.delete_data(data)
        assert not bpy.data.meshes.get("Mesh")


class TestDoesRepresentationIdExist(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        representation = ifc.createIfcShapeRepresentation()
        assert subject.does_representation_id_exist(representation.id()) is True
        assert subject.does_representation_id_exist(12345) is False


class TestDuplicateObjectData(NewFile):
    def test_run(self):
        data = bpy.data.meshes.new("Mesh")
        obj = bpy.data.objects.new("Object", data)
        new_data = subject.duplicate_object_data(obj)
        assert obj.data == data
        assert isinstance(new_data, bpy.types.Mesh)


class TestGetObjectData(NewFile):
    def test_run(self):
        data = bpy.data.meshes.new("Mesh")
        obj = bpy.data.objects.new("Object", data)
        assert subject.get_object_data(obj) == obj.data


class TestGetObjectMaterialsWithoutStyles(NewFile):
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


class TestGetRepresentationData(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        context = ifc.createIfcGeometricRepresentationContext()
        representation = ifc.createIfcShapeRepresentation()
        representation.ContextOfItems = context
        data = bpy.data.meshes.new("1/2")
        assert subject.get_representation_data(representation) == data


class TestGetRepresentationId(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        representation = ifc.createIfcShapeRepresentation()
        assert subject.get_representation_id(representation) == representation.id()


class TestGetRepresentationName(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        context = ifc.createIfcGeometricRepresentationContext()
        representation = ifc.createIfcShapeRepresentation()
        representation.ContextOfItems = context
        assert subject.get_representation_name(representation) == f"{context.id()}/{representation.id()}"


class TestGetStyles(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        style = ifc.createIfcSurfaceStyle()
        material = bpy.data.materials.new("Material")
        tool.Ifc.link(style, material)
        obj = bpy.data.objects.new("Object", bpy.data.meshes.new("Mesh"))
        obj.data.materials.append(material)
        assert subject.get_styles(obj) == [style]


class TestGetTextLiteral(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        item = ifc.createIfcTextLiteralWithExtent()
        representation = ifc.createIfcShapeRepresentation(Items=[item])
        assert subject.get_text_literal(representation) == item


class TestGetCartesianPointCoordinateOffset(NewFile):
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


class TestGetElementType(NewFile):
    def test_run(self):
        bpy.ops.bim.create_project()
        ifc = tool.Ifc.get()
        element = ifc.createIfcWall()
        type = ifc.createIfcWallType()
        ifcopenshell.api.run("type.assign_type", ifc, related_object=element, relating_type=type)
        assert subject.get_element_type(element) == type


class TestGetElementsOfType(NewFile):
    def test_run(self):
        bpy.ops.bim.create_project()
        ifc = tool.Ifc.get()
        element = ifc.createIfcWall()
        type = ifc.createIfcWallType()
        ifcopenshell.api.run("type.assign_type", ifc, related_object=element, relating_type=type)
        assert subject.get_elements_of_type(type) == (element,)


class TestGetTotalRepresentationItems(NewFile):
    def test_run(self):
        material1 = bpy.data.materials.new("Material")
        material2 = bpy.data.materials.new("Material")
        obj = bpy.data.objects.new("Object", bpy.data.meshes.new("Mesh"))
        obj.data.materials.append(material1)
        obj.data.materials.append(material2)
        assert subject.get_total_representation_items(obj) == 2


class TestHasDataUsers(NewFile):
    def test_run(self):
        data = bpy.data.meshes.new("Mesh")
        assert subject.has_data_users(data) is False
        bpy.data.objects.new("Object", data)
        assert subject.has_data_users(data) is True


class TestImportRepresentation(NewFile):
    def test_importing_a_normal_shape(self):
        ifc = ifcopenshell.open("test/files/basic.ifc")
        tool.Ifc.set(ifc)
        obj = bpy.data.objects.new("Object", bpy.data.meshes.new("Mesh"))
        material = bpy.data.materials.new("Material")
        material.BIMMaterialProperties.ifc_style_id = 101
        element = ifc.by_type("IfcWall")[0]
        tool.Ifc.link(element, obj)
        representation = element.Representation.Representations[0]
        mesh = subject.import_representation(obj, representation)
        assert len(mesh.polygons) == 12
        assert mesh.materials[0] == material

    def test_importing_non_body_curves(self):
        ifc = ifcopenshell.open("test/files/annotation.ifc")
        tool.Ifc.set(ifc)
        obj = bpy.data.objects.new("Object", bpy.data.meshes.new("Mesh"))
        element = ifc.by_type("IfcWall")[0]
        tool.Ifc.link(element, obj)
        representation = element.Representation.Representations[0]
        mesh = subject.import_representation(obj, representation)
        assert len(mesh.polygons) == 0
        assert len(mesh.edges) == 4


class TestImportRepresentationParameters(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        swept_area = ifc.createIfcCircleProfileDef(Radius=1)
        item = ifc.createIfcExtrudedAreaSolid(SweptArea=swept_area, Depth=2)
        representation = ifc.createIfcShapeRepresentation(Items=[item])
        data = bpy.data.meshes.new("Mesh")
        data.BIMMeshProperties.ifc_definition_id = representation.id()
        subject.import_representation_parameters(data)
        assert data.BIMMeshProperties.ifc_parameters[0].name == "IfcExtrudedAreaSolid/Depth"
        assert data.BIMMeshProperties.ifc_parameters[0].step_id == item.id()
        assert data.BIMMeshProperties.ifc_parameters[0].index == 3
        assert data.BIMMeshProperties.ifc_parameters[1].name == "IfcCircleProfileDef/Radius"
        assert data.BIMMeshProperties.ifc_parameters[1].step_id == swept_area.id()
        assert data.BIMMeshProperties.ifc_parameters[1].index == 3


class TestIsBodyRepresentation(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        context = ifc.createIfcGeometricRepresentationContext()
        representation = ifc.createIfcShapeRepresentation()
        representation.ContextOfItems = context
        context.ContextIdentifier = "Body"
        assert subject.is_body_representation(representation) is True
        context.ContextIdentifier = "Clearance"
        assert subject.is_body_representation(representation) is False


class TestIsBoxRepresentation(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        context = ifc.createIfcGeometricRepresentationContext()
        representation = ifc.createIfcShapeRepresentation()
        representation.ContextOfItems = context
        context.ContextIdentifier = "Box"
        assert subject.is_box_representation(representation) is True
        context.ContextIdentifier = "Clearance"
        assert subject.is_box_representation(representation) is False


class TestIsEdited(NewFile):
    def test_run(self):
        obj = bpy.data.objects.new("Object", bpy.data.meshes.new("Mesh"))
        assert subject.is_edited(obj) is False
        obj.scale[0] = 2
        assert subject.is_edited(obj) is True
        obj.scale[0] = 1
        assert subject.is_edited(obj) is False
        IfcStore.edited_objs.add(obj)
        assert subject.is_edited(obj) is True


class TestIsMappedRepresentation(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        representation = ifc.createIfcShapeRepresentation()
        assert subject.is_mapped_representation(representation) is False
        representation.RepresentationType = "MappedRepresentation"
        assert subject.is_mapped_representation(representation) is True


class TestIsTypeProduct(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        assert subject.is_type_product(ifc.createIfcWall()) is False
        assert subject.is_type_product(ifc.createIfcWallType()) is True


class TestLink(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        element = ifc.createIfcShapeRepresentation()
        obj = bpy.data.meshes.new("Mesh")
        subject.link(element, obj)
        assert obj.BIMMeshProperties.ifc_definition_id == element.id()


class TestRecordObjectMaterials(NewFile):
    def test_run(self):
        obj = bpy.data.objects.new("Object", bpy.data.meshes.new("Mesh"))
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        style = ifc.createIfcSurfaceStyle()
        material = bpy.data.materials.new("Material")
        material.BIMMaterialProperties.ifc_style_id = style.id()
        obj.data.materials.append(material)
        subject.record_object_materials(obj)
        assert obj.data.BIMMeshProperties.material_checksum == str([style.id()])


class TestRecordObjectPosition(NewFile):
    def test_run(self):
        obj = bpy.data.objects.new("Object", None)
        subject.record_object_position(obj)
        assert obj.BIMObjectProperties.location_checksum == repr(np.array(obj.matrix_world.translation).tobytes())
        assert obj.BIMObjectProperties.rotation_checksum == repr(np.array(obj.matrix_world.to_3x3()).tobytes())


class TestRemoveConnection(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc().set(ifc)
        element1 = ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcWall")
        element2 = ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcWall")
        rel = ifcopenshell.api.run("geometry.connect_path", ifc, relating_element=element1, related_element=element2)
        subject.remove_connection(rel)
        assert not tool.Ifc.get().by_type("IfcRelConnectsPathElements")


class TestRenameObject(NewFile):
    def test_run(self):
        obj = bpy.data.meshes.new("Mesh")
        subject.rename_object(obj, "name")
        assert obj.name == "name"


class TestReplaceObjectWithEmpty(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        obj = bpy.data.objects.new("Object", bpy.data.meshes.new("Mesh"))
        obj.matrix_world[0][3] = 1
        bpy.context.scene.collection.objects.link(obj)
        element = ifc.createIfcWall()
        tool.Ifc.link(element, obj)
        subject.replace_object_with_empty(obj)
        obj = bpy.data.objects.get("Object")
        assert obj.users_collection[0] == bpy.context.scene.collection
        assert tool.Ifc.get_entity(obj) == element
        assert tool.Ifc.get_object(element) == obj
        assert obj.data is None
        assert obj.matrix_world[0][3] == 1


class TestResolveMappedRepresentation(NewFile):
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


class TestRunGeometryUpdateRepresentation(NewFile):
    def test_nothing(self):
        pass


class TestRunStyleAddStyle(NewFile):
    def test_nothing(self):
        pass


class TestSelectConnection(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc().set(ifc)

        element1 = ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcWall")
        obj1 = bpy.data.objects.new("Object", None)
        bpy.context.scene.collection.objects.link(obj1)
        tool.Ifc.link(element1, obj1)

        element2 = ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcWall")
        obj2 = bpy.data.objects.new("Object", None)
        bpy.context.scene.collection.objects.link(obj2)
        tool.Ifc.link(element2, obj2)

        rel = ifcopenshell.api.run("geometry.connect_path", ifc, relating_element=element1, related_element=element2)

        subject.select_connection(rel)
        assert obj1 in bpy.context.selected_objects
        assert obj2 in bpy.context.selected_objects


class TestShouldForceFacetedBrep(NewFile):
    def test_run(self):
        result = bpy.context.scene.BIMGeometryProperties.should_force_faceted_brep
        assert subject.should_force_faceted_brep() is result


class TestShouldForceTriangulation(NewFile):
    def test_run(self):
        result = bpy.context.scene.BIMGeometryProperties.should_force_triangulation
        assert subject.should_force_triangulation() is result


class TestShouldGenerateUVs(NewFile):
    def test_needs_mesh_data(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        obj = bpy.data.objects.new("Object", None)
        assert subject.should_generate_uvs(obj) is False

    def test_needs_nodes(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        obj = bpy.data.objects.new("Object", bpy.data.meshes.new("Mesh"))
        material = bpy.data.materials.new("Material")
        obj.data.materials.append(material)
        material.use_nodes = False
        assert subject.should_generate_uvs(obj) is False

    def test_needs_texture_coordinates_with_a_uv_output(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        obj = bpy.data.objects.new("Object", bpy.data.meshes.new("Mesh"))
        material = bpy.data.materials.new("Material")
        obj.data.materials.append(material)
        material.use_nodes = True

        bsdf = material.node_tree.nodes["Principled BSDF"]
        node = material.node_tree.nodes.new(type="ShaderNodeTexImage")
        material.node_tree.links.new(bsdf.inputs["Base Color"], node.outputs["Color"])

        coords = material.node_tree.nodes.new(type="ShaderNodeTexCoord")
        material.node_tree.links.new(node.inputs["Vector"], coords.outputs["UV"])
        assert subject.should_generate_uvs(obj) is True

    def test_accepts_a_uv_map_node(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        obj = bpy.data.objects.new("Object", bpy.data.meshes.new("Mesh"))
        material = bpy.data.materials.new("Material")
        obj.data.materials.append(material)
        material.use_nodes = True

        bsdf = material.node_tree.nodes["Principled BSDF"]
        node = material.node_tree.nodes.new(type="ShaderNodeTexImage")
        material.node_tree.links.new(bsdf.inputs["Base Color"], node.outputs["Color"])

        coords = material.node_tree.nodes.new(type="ShaderNodeUVMap")
        coords.uv_map = "UVMap"
        material.node_tree.links.new(node.inputs["Vector"], coords.outputs["UV"])
        assert subject.should_generate_uvs(obj) is True


class TestShouldUsePresentationStyleAssignment(NewFile):
    def test_run(self):
        result = bpy.context.scene.BIMGeometryProperties.should_use_presentation_style_assignment
        assert subject.should_use_presentation_style_assignment() is result


class TestGetProfileSetUsage(NewFile):
    def test_getting_a_profile_set_usage(self):
        ifc = ifcopenshell.file()
        element = ifc.createIfcColumn()
        assert subject.get_profile_set_usage(element) is None
        usage = ifc.createIfcMaterialProfileSetUsage()
        ifc.createIfcRelAssociatesMaterial(RelatingMaterial=usage, RelatedObjects=[element])
        assert subject.get_profile_set_usage(element) == usage


class TestGetIfcRepresentationClass(NewFile):
    def test_detecting_profile_set_representations(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        element = ifc.createIfcColumn()
        ifc.createIfcRelAssociatesMaterial(
            RelatingMaterial=ifc.createIfcMaterialProfileSetUsage(), RelatedObjects=[element]
        )
        representation = ifc.createIfcShapeRepresentation()
        assert (
            subject.get_ifc_representation_class(element, representation)
            == "IfcExtrudedAreaSolid/IfcMaterialProfileSetUsage"
        )

    def test_detecting_rectangular_extrusions(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        element = ifc.createIfcColumn()
        representation = ifc.createIfcShapeRepresentation(
            Items=[ifc.createIfcExtrudedAreaSolid(SweptArea=ifc.createIfcRectangleProfileDef())]
        )
        assert (
            subject.get_ifc_representation_class(element, representation)
            == "IfcExtrudedAreaSolid/IfcRectangleProfileDef"
        )

    def test_detecting_circle_extrusions(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        element = ifc.createIfcColumn()
        representation = ifc.createIfcShapeRepresentation(
            Items=[ifc.createIfcExtrudedAreaSolid(SweptArea=ifc.createIfcCircleProfileDef())]
        )
        assert (
            subject.get_ifc_representation_class(element, representation) == "IfcExtrudedAreaSolid/IfcCircleProfileDef"
        )

    def test_detecting_text_representations(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        element = ifc.createIfcAnnotation()
        element.ObjectType = "TEXT"
        assert subject.get_ifc_representation_class(element, None) == "IfcTextLiteral"

    def test_detecting_text_and_geometric_representations(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        element = ifc.createIfcAnnotation()
        element.ObjectType = "TEXT_LEADER"
        assert subject.get_ifc_representation_class(element, None) == "IfcGeometricCurveSet/IfcTextLiteral"

    def test_returning_null_for_non_parametric_representations(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        assert subject.get_ifc_representation_class(ifc.createIfcColumn(), ifc.createIfcShapeRepresentation()) is None
