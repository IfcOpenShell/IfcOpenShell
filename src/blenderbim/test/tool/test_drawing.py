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
from blenderbim.tool.drawing import Drawing as subject


class TestImplementsTool(NewFile):
    def test_run(self):
        assert isinstance(subject(), blenderbim.core.tool.Drawing)


class TestDisableEditingText(NewFile):
    def test_run(self):
        obj = bpy.data.objects.new("Object", None)
        obj.BIMTextProperties.is_editing = True
        subject.disable_editing_text(obj)
        assert obj.BIMTextProperties.is_editing == False


class TestDisableEditingTextProduct(NewFile):
    def test_run(self):
        obj = bpy.data.objects.new("Object", None)
        obj.BIMTextProperties.is_editing_product = True
        subject.disable_editing_text_product(obj)
        assert obj.BIMTextProperties.is_editing_product == False


class TestEnableEditingText(NewFile):
    def test_run(self):
        obj = bpy.data.objects.new("Object", None)
        subject.enable_editing_text(obj)
        assert obj.BIMTextProperties.is_editing == True


class TestEnableEditingTextProduct(NewFile):
    def test_run(self):
        obj = bpy.data.objects.new("Object", None)
        subject.enable_editing_text_product(obj)
        assert obj.BIMTextProperties.is_editing_product == True


class TestExportTextLiteralAttributes(NewFile):
    def test_run(self):
        TestImportTextAttributes().test_run()
        assert subject.export_text_literal_attributes(bpy.data.objects.get("Object")) == {
            "Literal": "Literal",
            "Path": "RIGHT",
            "BoxAlignment": "BoxAlignment",
        }


class TestGetTextLiteral(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        obj = bpy.data.objects.new("Object", None)
        element = ifc.createIfcAnnotation()
        element.Representation = ifc.createIfcProductDefinitionShape()
        context = ifc.createIfcGeometricRepresentationSubContext(ContextType="Plan", ContextIdentifier="Annotation")
        item = ifc.createIfcTextLiteralWithExtent(Literal="Literal", Path="RIGHT", BoxAlignment="BoxAlignment")
        representation = ifc.createIfcShapeRepresentation(ContextOfItems=context, Items=[item])
        element.Representation.Representations = [representation]
        tool.Ifc.link(element, obj)
        assert subject.get_text_literal(obj) == item


class TestGetTextProduct(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        wall = ifc.createIfcWall()
        label = ifc.createIfcAnnotation()
        ifcopenshell.api.run("drawing.assign_product", ifc, relating_product=wall, related_object=label)
        assert subject.get_text_product(label) == wall


class TestImportTextAttributes(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        obj = bpy.data.objects.new("Object", None)
        element = ifc.createIfcAnnotation()
        element.Representation = ifc.createIfcProductDefinitionShape()
        context = ifc.createIfcGeometricRepresentationSubContext(ContextType="Plan", ContextIdentifier="Annotation")
        item = ifc.createIfcTextLiteralWithExtent(Literal="Literal", Path="RIGHT", BoxAlignment="BoxAlignment")
        representation = ifc.createIfcShapeRepresentation(ContextOfItems=context, Items=[item])
        element.Representation.Representations = [representation]
        tool.Ifc.link(element, obj)
        subject.import_text_attributes(obj)
        props = obj.BIMTextProperties
        assert props.attributes.get("Literal").string_value == "Literal"
        assert props.attributes.get("Path").enum_value == "RIGHT"
        assert props.attributes.get("BoxAlignment").string_value == "BoxAlignment"


class TestImportTextProduct(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        wall = ifc.createIfcWall()
        label = ifc.createIfcAnnotation()
        ifcopenshell.api.run("drawing.assign_product", ifc, relating_product=wall, related_object=label)
        wall_obj = bpy.data.objects.new("Object", None)
        label_obj = bpy.data.objects.new("Object", None)
        tool.Ifc.link(wall, wall_obj)
        tool.Ifc.link(label, label_obj)
        subject.import_text_product(label_obj)
        assert label_obj.BIMTextProperties.relating_product == wall_obj

    def test_doing_nothing_if_no_product_to_import(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        label = ifc.createIfcAnnotation()
        label_obj = bpy.data.objects.new("Object", None)
        tool.Ifc.link(label, label_obj)
        subject.import_text_product(label_obj)
        assert label_obj.BIMTextProperties.relating_product is None


class TestUpdateTextValue(NewFile):
    def test_updating_arbitrary_strings(self):
        TestGetTextLiteral().test_run()
        obj = bpy.data.objects.get("Object")
        subject.update_text_value(obj)
        assert obj.BIMTextProperties.value == "Literal"

    def test_using_attribute_variables(self):
        TestGetTextLiteral().test_run()

        obj = bpy.data.objects.get("Object")
        ifc = tool.Ifc.get()
        wall = ifc.createIfcWall(Name="Baz")
        label = ifc.by_type("IfcAnnotation")[0]
        ifcopenshell.api.run("drawing.assign_product", ifc, relating_product=wall, related_object=label)

        ifc.by_type("IfcTextLiteralWithExtent")[0].Literal = "Foo {{Name}} Bar"

        subject.update_text_value(obj)
        assert obj.BIMTextProperties.value == "Foo Baz Bar"

    def test_using_property_variables(self):
        TestGetTextLiteral().test_run()

        obj = bpy.data.objects.get("Object")
        ifc = tool.Ifc.get()
        wall = ifc.createIfcWall()
        pset = ifcopenshell.api.run("pset.add_pset", ifc, name="Custom_Pset", product=wall)
        ifcopenshell.api.run("pset.edit_pset", ifc, pset=pset, properties={"Key": "Baz"})
        label = ifc.by_type("IfcAnnotation")[0]
        ifcopenshell.api.run("drawing.assign_product", ifc, relating_product=wall, related_object=label)

        ifc.by_type("IfcTextLiteralWithExtent")[0].Literal = "Foo {{Custom_Pset.Key}} Bar"

        subject.update_text_value(obj)
        assert obj.BIMTextProperties.value == "Foo Baz Bar"
