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
import ifcopenshell
import blenderbim.core.tool
import blenderbim.tool as tool
from test.bim.bootstrap import NewFile
from blenderbim.tool.root import Root as subject


class TestImplementsTool(NewFile):
    def test_run(self):
        assert isinstance(subject(), blenderbim.core.tool.Root)


class TestAddTrackedOpening(NewFile):
    def test_run(self):
        obj = bpy.data.objects.new("Object", None)
        subject.add_tracked_opening(obj)
        props = bpy.context.scene.BIMModelProperties
        assert props.openings[0].obj == obj


class TestCopyRepresentation(NewFile):
    def test_copying_a_product(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        source = ifc.createIfcWall(Representation=ifc.createIfcProductDefinitionShape())
        dest = ifc.createIfcWall()
        subject.copy_representation(source, dest)
        assert dest.Representation.is_a("IfcProductDefinitionShape")

    def test_copying_a_type_product(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        source = ifc.createIfcWallType(RepresentationMaps=[ifc.createIfcRepresentationMap()])
        dest = ifc.createIfcWallType()
        subject.copy_representation(source, dest)
        assert dest.RepresentationMaps[0].is_a("IfcRepresentationMap")


class TestDoesTypeHaveRepresentations(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        element = ifc.createIfcWallType()
        assert subject.does_type_have_representations(element) is False
        element.RepresentationMaps = [ifc.createIfcRepresentationMap()]
        assert subject.does_type_have_representations(element) is True


class TestGetDecompositionRelationships(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)

        element = ifc.createIfcWall()
        opening = ifc.createIfcOpeningElement()
        fill = ifc.createIfcWindow()
        ifcopenshell.api.run("void.add_opening", ifc, opening=opening, element=element)
        ifcopenshell.api.run("void.add_filling", ifc, opening=opening, element=fill)

        obj = bpy.data.objects.new("Object", None)
        tool.Ifc.link(fill, obj)

        assert subject.get_decomposition_relationships([obj]) == {fill: {"type": "fill", "element": element}}


class TestGetElementRepresentation(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        context = ifc.createIfcGeometricRepresentationContext(ContextType="Model")
        representation = ifc.createIfcShapeRepresentation(ContextOfItems=context)
        wall = ifc.createIfcWall(Representation=ifc.createIfcProductDefinitionShape(Representations=[representation]))
        assert subject.get_element_representation(wall, context) == representation


class TestGetElementType(NewFile):
    def test_run(self):
        bpy.ops.bim.create_project()
        ifc = tool.Ifc.get()
        element = ifc.createIfcWall()
        type = ifc.createIfcWallType()
        ifcopenshell.api.run("type.assign_type", ifc, related_object=element, relating_type=type)
        assert subject.get_element_type(element) == type


class TestGetObjectName(NewFile):
    def test_run(self):
        obj = bpy.data.objects.new("Object", None)
        assert subject.get_object_name(obj) == "Object"

    def test_blender_number_suffixes_are_ignored(self):
        obj = bpy.data.objects.new("Object.001", None)
        assert subject.get_object_name(obj) == "Object"
        obj = bpy.data.objects.new("Object.foo.123", None)
        assert subject.get_object_name(obj) == "Object.foo"


class TestGetObjectRepresentation(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        representation = ifc.createIfcShapeRepresentation()
        obj = bpy.data.objects.new("Object", bpy.data.meshes.new("Mesh"))
        obj.data.BIMMeshProperties.ifc_definition_id = representation.id()
        assert subject.get_object_representation(obj) == representation


class TestGetRepresentationContext(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        context = ifc.createIfcGeometricRepresentationContext()
        representation = ifc.createIfcShapeRepresentation(ContextOfItems=context)
        assert subject.get_representation_context(representation) == context


class TestIsOpeningElement(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        assert subject.is_opening_element(ifc.createIfcWall()) is False
        assert subject.is_opening_element(ifc.createIfcOpeningElement()) is True


class TestLinkObjectData(NewFile):
    def test_run(self):
        data = bpy.data.meshes.new("Mesh")
        source = bpy.data.objects.new("Object", data)
        destination = bpy.data.objects.new("Object", bpy.data.meshes.new("Mesh"))
        subject.link_object_data(source, destination)
        assert source.data == data
        assert source.data == destination.data


class TestRunGeometryAddRepresntation(NewFile):
    def test_nothing(self):
        pass


class TestSetElementSpecificDisplaySettings(NewFile):
    def test_opening_elements_display_as_wire(self):
        ifc = ifcopenshell.file()
        obj = bpy.data.objects.new("Object", bpy.data.meshes.new("Mesh"))
        element = ifc.createIfcOpeningElement()
        subject.set_element_specific_display_settings(obj, element)
        assert obj.display_type == "WIRE"


class TestSetObjectName(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        obj = bpy.data.objects.new("Object", bpy.data.meshes.new("Mesh"))
        element = ifc.createIfcWall()
        subject.set_object_name(obj, element)
        assert obj.name == "IfcWall/Object"

    def test_existing_ifc_prefixes_are_not_repeated(self):
        ifc = ifcopenshell.file()
        obj = bpy.data.objects.new("IfcSlab/Object", bpy.data.meshes.new("Mesh"))
        element = ifc.createIfcWall()
        subject.set_object_name(obj, element)
        assert obj.name == "IfcWall/Object"
