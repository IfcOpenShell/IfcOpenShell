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
import math
import numpy as np
import ifcopenshell
import ifcopenshell.api.type
import bonsai.core.tool
import bonsai.tool as tool
from mathutils import Vector
from test.bim.bootstrap import NewFile
from bonsai.tool.geometry import Geometry as subject
from typing import Union


class TestImplementsTool(NewFile):
    def test_run(self):
        assert isinstance(subject(), bonsai.core.tool.Geometry)


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
        material3.BIMStyleProperties.ifc_definition_id = 1
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
        obj.BIMObjectProperties.cartesian_point_offset = "1,2,3"
        assert subject.get_cartesian_point_coordinate_offset(obj) == Vector((1.0, 2.0, 3.0))

    def test_get_null_if_not_a_cartesian_point_offset_type(self):
        obj = bpy.data.objects.new("Object", None)
        props = bpy.context.scene.BIMGeoreferenceProperties
        props.has_blender_offset = True
        obj.BIMObjectProperties.cartesian_point_offset = "1,2,3"
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
        ifcopenshell.api.run("type.assign_type", ifc, related_objects=[element], relating_type=type)
        assert subject.get_element_type(element) == type


class TestGetElementsOfType(NewFile):
    def test_run(self):
        bpy.ops.bim.create_project()
        ifc = tool.Ifc.get()
        element = ifc.createIfcWall()
        type = ifc.createIfcWallType()
        ifcopenshell.api.run("type.assign_type", ifc, related_objects=[element], relating_type=type)
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
        material.BIMStyleProperties.ifc_definition_id = 101
        element = ifc.by_type("IfcWall")[0]
        tool.Ifc.link(element, obj)
        representation = element.Representation.Representations[1]
        mesh = subject.import_representation(obj, representation)
        assert isinstance(mesh, bpy.types.Mesh)
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
        material.BIMStyleProperties.ifc_definition_id = style.id()
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
    def validate(
        self,
        element: ifcopenshell.entity_instance,
        obj: bpy.types.Object,
        new_obj: bpy.types.Object,
        new_data: Union[bpy.types.Mesh, None],
    ) -> None:
        assert not tool.Blender.is_valid_data_block(obj)
        assert new_obj.users_collection[0] == bpy.context.scene.collection
        assert tool.Ifc.get_entity(new_obj) == element
        assert tool.Ifc.get_object(element) == new_obj
        assert new_obj.data is new_data
        assert new_obj.matrix_world.translation.x == 1

    def create_object(
        self, name: str, data: Union[bpy.types.Mesh, None], ifc_class: str
    ) -> tuple[bpy.types.Object, ifcopenshell.entity_instance]:
        ifc = tool.Ifc.get()
        obj = bpy.data.objects.new(name, data)
        obj.matrix_world.translation.x = 1
        bpy.context.scene.collection.objects.link(obj)
        element = ifc.create_entity(ifc_class)
        tool.Ifc.link(element, obj)
        return obj, element

    def run_test_replace_non_global(
        self, from_data: Union[bpy.types.Mesh, None], to_data: Union[bpy.types.Mesh, None]
    ) -> None:
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)

        obj, element = self.create_object("Object", from_data, "IfcWall")
        new_obj = subject.recreate_object_with_data(obj, to_data)
        if from_data:
            assert tool.Blender.is_valid_data_block(from_data)
        self.validate(element, obj, new_obj, to_data)

    def test_replace_mesh_with_empty(self) -> None:
        self.run_test_replace_non_global(bpy.data.meshes.new("Mesh"), None)

    def test_replace_empty_with_mesh(self) -> None:
        self.run_test_replace_non_global(None, bpy.data.meshes.new("New Mesh"))

    def run_test_for_global_argument(
        self, from_data: Union[bpy.types.Mesh, None], to_data: Union[bpy.types.Mesh, None]
    ) -> None:
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)

        type_obj, element_type = self.create_object("IfcWallType", from_data, "IfcWallType")
        obj1, element1 = self.create_object("IfcWall1", from_data, "IfcWall")
        obj2, element2 = self.create_object("IfcWall2", from_data, "IfcWall")
        ifcopenshell.api.type.assign_type(ifc, related_objects=[element1, element2], relating_type=element_type)

        to_data = to_data
        new_obj = subject.recreate_object_with_data(type_obj, to_data, is_global=True)
        if from_data:
            assert tool.Blender.is_valid_data_block(from_data)

        self.validate(element_type, type_obj, new_obj, to_data)
        self.validate(element1, obj1, bpy.data.objects["IfcWall1"], to_data)
        self.validate(element2, obj2, bpy.data.objects["IfcWall2"], to_data)

    def test_replace_mesh_with_empty_global(self) -> None:
        self.run_test_for_global_argument(bpy.data.meshes.new("Mesh"), None)

    def test_replace_empty_with_mesh_global(self) -> None:
        self.run_test_for_global_argument(None, bpy.data.meshes.new("New Mesh"))


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

        bsdf = tool.Blender.get_material_node(material, "BSDF_PRINCIPLED")
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

        bsdf = tool.Blender.get_material_node(material, "BSDF_PRINCIPLED")
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


class TestRemoveRepresentationItem(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)

        context = ifc.createIfcGeometricRepresentationContext()
        element = ifc.createIfcWall()

        items = [ifc.createIfcExtrudedAreaSolid(), ifc.createIfcExtrudedAreaSolid()]
        representation = ifc.createIfcShapeRepresentation(Items=items, ContextOfItems=context)
        tool.Ifc.run("geometry.assign_representation", product=element, representation=representation)

        product_shape = element.Representation
        shape_aspect = subject.create_shape_aspect(product_shape, representation, items[:1], None)
        shape_aspect_id = shape_aspect.id()

        subject.remove_representation_item(items[0])
        assert tool.Ifc.get_entity_by_id(shape_aspect_id) is None
        assert set(representation.Items) == {items[1]}


class TestCreateShapeAspect(NewFile):
    def test_run(self):
        self.create_shape_aspect(use_element_type=False)
        self.create_shape_aspect(use_element_type=True)

    def create_shape_aspect(self, use_element_type):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)

        context = ifc.createIfcGeometricRepresentationContext()
        element = ifc.createIfcWallType() if use_element_type else ifc.createIfcWall()

        item = ifc.createIfcExtrudedAreaSolid()
        items = [item]
        representation = ifc.createIfcShapeRepresentation(Items=items, ContextOfItems=context)
        tool.Ifc.run("geometry.assign_representation", product=element, representation=representation)

        product_shape = element.RepresentationMaps[0] if use_element_type else element.Representation
        subject.create_shape_aspect(product_shape, representation, items, None)
        assert len(product_shape.HasShapeAspects) == 1
        representation = product_shape.HasShapeAspects[0].ShapeRepresentations[0]
        assert set(representation.Items) == set(items)


class TestAddRepresentationItemToShapeAspect(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)

        context = ifc.createIfcGeometricRepresentationContext()
        element = ifc.createIfcWall()

        items = [ifc.createIfcExtrudedAreaSolid(), ifc.createIfcExtrudedAreaSolid()]
        representation = ifc.createIfcShapeRepresentation(Items=items, ContextOfItems=context)
        tool.Ifc.run("geometry.assign_representation", product=element, representation=representation)
        product_shape = element.Representation
        shape_aspect0 = subject.create_shape_aspect(product_shape, representation, [items[0]], None)
        previous_shape_aspect_id = shape_aspect0.id()
        shape_aspect1 = subject.create_shape_aspect(product_shape, representation, [items[1]], None)

        subject.add_representation_item_to_shape_aspect([items[0]], shape_aspect1)
        # previous shape aspect removed as there won't be any items in it
        assert tool.Ifc.get_entity_by_id(previous_shape_aspect_id) is None
        representation = shape_aspect1.ShapeRepresentations[0]
        assert set(representation.Items) == set(items)


class TestRemoveRepresentationItemFromShapeAspect(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)

        context = ifc.createIfcGeometricRepresentationContext()
        element = ifc.createIfcWall()

        items = [ifc.createIfcExtrudedAreaSolid(), ifc.createIfcExtrudedAreaSolid()]
        representation = ifc.createIfcShapeRepresentation(Items=items, ContextOfItems=context)
        tool.Ifc.run("geometry.assign_representation", product=element, representation=representation)
        product_shape = element.Representation
        shape_aspect0 = subject.create_shape_aspect(product_shape, representation, [items[0]], None)
        previous_shape_aspect_id = shape_aspect0.id()
        previous_shape_aspect_rep_id = shape_aspect0.ShapeRepresentations[0].id()
        shape_aspect1 = subject.create_shape_aspect(product_shape, representation, [items[1]], None)

        subject.remove_representation_items_from_shape_aspect([items[0]], shape_aspect0)
        # previous shape aspect and representation are removed as there won't be any items in them
        assert tool.Ifc.get_entity_by_id(previous_shape_aspect_id) is None
        assert tool.Ifc.get_entity_by_id(previous_shape_aspect_rep_id) is None

        # items is removed from the representaiton
        subject.add_representation_item_to_shape_aspect([items[0]], shape_aspect1)
        subject.remove_representation_items_from_shape_aspect([items[1]], shape_aspect1)
        representation = shape_aspect1.ShapeRepresentations[0]
        assert set(representation.Items) == {items[0]}


class TestApplyItemIdsAsVertexGroups(NewFile):
    def test_run(self):
        bpy.ops.mesh.primitive_cube_add(size=10, location=(0, 0, 4))
        obj = bpy.data.objects["Cube"]
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.quads_convert_to_tris()
        bpy.ops.mesh.duplicate_move()
        bpy.ops.object.editmode_toggle()

        mesh = obj.data
        assert isinstance(mesh, bpy.types.Mesh)
        assert len(mesh.polygons) == 24

        mesh["ios_edges"] = []  # Method requirement.
        ios_item_ids = (95,) * 12 + (45,) * 12
        mesh["ios_item_ids"] = ios_item_ids
        unique = tuple(dict.fromkeys(ios_item_ids))
        ios_item_ids_unique = [unique.index(i) for i in ios_item_ids]

        tool.Geometry.apply_item_ids_as_vertex_groups(obj)

        vertex_group_names = [vg.name for vg in obj.vertex_groups]
        assert vertex_group_names == [f"ios_item_id_{i}" for i in unique]

        verts = mesh.vertices
        for i, polygon in enumerate(mesh.polygons):
            for vi in polygon.vertices:
                vert = verts[vi]
                groups = [g.group for g in vert.groups]
                assert groups == [ios_item_ids_unique[i]]
