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


class TestAddDynamicOpeningVoids(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)

        obj = bpy.data.objects.new("Object", bpy.data.meshes.new("Mesh"))
        element = ifc.createIfcOpeningElement()
        tool.Ifc.link(element, obj)

        wall_obj = bpy.data.objects.new("Object", bpy.data.meshes.new("Mesh"))
        wall_element = ifc.createIfcOpeningElement()
        tool.Ifc.link(wall_element, wall_obj)

        ifcopenshell.api.run("void.add_opening", ifc, opening=element, element=wall_element)

        subject.add_dynamic_opening_voids(element, obj)

        modifier = wall_obj.modifiers[0]
        assert modifier.type == "BOOLEAN"
        assert modifier.name == "IfcOpeningElement"
        assert modifier.operation == "DIFFERENCE"
        assert modifier.object == obj
        assert modifier.solver == "EXACT"
        assert modifier.use_self is True


class TestDoesTypeHaveRepresentations(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        element = ifc.createIfcWallType()
        assert subject.does_type_have_representations(element) is False
        element.RepresentationMaps = [ifc.createIfcRepresentationMap()]
        assert subject.does_type_have_representations(element) is True


class TestGetElementType(NewFile):
    def test_run(self):
        bpy.ops.bim.create_project()
        ifc = tool.Ifc.get()
        element = ifc.createIfcWall()
        type = ifc.createIfcWallType()
        ifcopenshell.api.run("type.assign_type", ifc, related_object=element, relating_type=type)
        assert subject.get_element_type(element) == type


class TestGetElementType(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        context = ifc.createIfcGeometricRepresentationContext()
        representation = ifc.createIfcShapeRepresentation(ContextOfItems=context)
        obj = bpy.data.objects.new("Object", bpy.data.meshes.new("Mesh"))
        obj.data.BIMMeshProperties.ifc_definition_id = representation.id()
        assert subject.get_object_context(obj) == context


class TestIsOpeningElement(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        assert subject.is_opening_element(ifc.createIfcWall()) is False
        assert subject.is_opening_element(ifc.createIfcOpeningElement()) is True


class TestRunGeometryAddRepresntation(NewFile):
    def test_nothing(self):
        pass
