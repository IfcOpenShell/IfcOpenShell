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

import os
import bpy
import mathutils
import ifcopenshell
import blenderbim.core.tool
import blenderbim.tool as tool
from test.bim.bootstrap import NewFile
from blenderbim.tool.drawing import Drawing as subject


class TestImplementsTool(NewFile):
    def test_run(self):
        assert isinstance(subject(), blenderbim.core.tool.Drawing)


class TestCreateCamera(NewFile):
    def test_run(self):
        obj = subject.create_camera("Name", mathutils.Matrix())
        assert obj.name == "Name"
        assert obj.matrix_world == mathutils.Matrix()
        assert obj.data.type == "ORTHO"
        assert obj.data.ortho_scale == 50
        assert obj.data.clip_end == 10
        assert obj.users_collection[0] == bpy.context.scene.collection


class TestCreateSvgSheet(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        document = ifc.createIfcDocumentInformation(Identification="X", Name="FOOBAR")
        subject.create_svg_sheet(document, "A1")
        assert os.path.isfile(os.path.join(bpy.context.scene.BIMProperties.data_dir, "sheets", "X - FOOBAR.svg"))


class TestDisableEditingDrawings(NewFile):
    def test_run(self):
        bpy.context.scene.DocProperties.is_editing_drawings = True
        subject.disable_editing_drawings()
        assert bpy.context.scene.DocProperties.is_editing_drawings == False


class TestDisableEditingSheets(NewFile):
    def test_run(self):
        bpy.context.scene.DocProperties.is_editing_sheets = True
        subject.disable_editing_sheets()
        assert bpy.context.scene.DocProperties.is_editing_sheets == False


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


class TestEnableEditingDrawings(NewFile):
    def test_run(self):
        bpy.context.scene.DocProperties.is_editing_drawings = False
        subject.enable_editing_drawings()
        assert bpy.context.scene.DocProperties.is_editing_drawings == True


class TestEnableEditingSheets(NewFile):
    def test_run(self):
        bpy.context.scene.DocProperties.is_editing_sheets = False
        subject.enable_editing_sheets()
        assert bpy.context.scene.DocProperties.is_editing_sheets == True


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


class TestEnsureUniqueDrawingName(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        assert subject.ensure_unique_drawing_name("FOOBAR") == "FOOBAR"
        ifc.createIfcAnnotation(Name="FOOBAR", ObjectType="DRAWING")
        assert subject.ensure_unique_drawing_name("FOOBAR") == "FOOBAR-X"
        ifc.createIfcAnnotation(Name="FOOBAR-X", ObjectType="DRAWING")
        assert subject.ensure_unique_drawing_name("FOOBAR") == "FOOBAR-X-X"


class TestEnsureUniqueIdentification(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        assert subject.ensure_unique_identification("FOOBAR") == "FOOBAR"
        ifc.createIfcDocumentInformation(Identification="FOOBAR", Scope="DOCUMENTATION")
        assert subject.ensure_unique_identification("FOOBAR") == "FOOBAR-X"
        ifc.createIfcDocumentInformation(Identification="FOOBAR-X", Scope="DOCUMENTATION")
        assert subject.ensure_unique_identification("FOOBAR") == "FOOBAR-X-X"

    def test_unique_document_id_ifc2x3(self):
        ifc = ifcopenshell.file(schema="IFC2X3")
        tool.Ifc.set(ifc)
        assert subject.ensure_unique_identification("FOOBAR") == "FOOBAR"
        ifc.createIfcDocumentInformation(DocumentId="FOOBAR", Scope="DOCUMENTATION")
        assert subject.ensure_unique_identification("FOOBAR") == "FOOBAR-X"
        ifc.createIfcDocumentInformation(DocumentId="FOOBAR-X", Scope="DOCUMENTATION")
        assert subject.ensure_unique_identification("FOOBAR") == "FOOBAR-X-X"


class TestExportTextLiteralAttributes(NewFile):
    def test_run(self):
        TestImportTextAttributes().test_run()
        assert subject.export_text_literal_attributes(bpy.data.objects.get("Object")) == {
            "Literal": "Literal",
            "Path": "RIGHT",
            "BoxAlignment": "BoxAlignment",
        }


class TestGetBodyContext(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        context = ifc.createIfcGeometricRepresentationSubContext(
            ContextType="Model", ContextIdentifier="Body", TargetView="MODEL_VIEW"
        )
        tool.Ifc.set(ifc)
        assert subject.get_body_context() == context


class TestGetSheetFilename(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        document = ifc.createIfcDocumentInformation(Identification="X", Name="FOOBAR", Scope="DOCUMENTATION")
        subject.get_sheet_filename(document) == "X - FOOBAR"

    def test_run_ifc2x3(self):
        ifc = ifcopenshell.file(schema="IFC2X3")
        document = ifc.createIfcDocumentInformation(DocumentId="X", Name="FOOBAR", Scope="DOCUMENTATION")
        subject.get_sheet_filename(document) == "X - FOOBAR"


class TestGenerateDrawingMatrix(NewFile):
    def test_returning_the_origin_as_a_fallback(self):
        assert subject.generate_drawing_matrix("PLAN_VIEW", None) == mathutils.Matrix()


class TestGenerateSheetIdentification(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        subject.generate_sheet_identification() == "A01"
        document = ifc.createIfcDocumentInformation()
        subject.generate_sheet_identification() == "A02"


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


class TestImportDrawings(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        drawing = ifc.createIfcAnnotation(Name="FOOBAR", ObjectType="DRAWING")
        subject.import_drawings()
        props = bpy.context.scene.DocProperties
        assert props.drawings[0].ifc_definition_id == drawing.id()
        assert props.drawings[0].name == "FOOBAR"


class TestImportSheets(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        ifc.createIfcDocumentInformation(Identification="Y", Name="FOOBAZ")
        document = ifc.createIfcDocumentInformation(Identification="X", Name="FOOBAR", Scope="DOCUMENTATION")
        subject.import_sheets()
        props = bpy.context.scene.DocProperties
        assert props.sheets[0].ifc_definition_id == document.id()
        assert props.sheets[0].identification == "X"
        assert props.sheets[0].name == "FOOBAR"

    def test_run_ifc2x3(self):
        ifc = ifcopenshell.file(schema="IFC2X3")
        tool.Ifc.set(ifc)
        ifc.createIfcDocumentInformation(DocumentId="Y", Name="FOOBAZ")
        document = ifc.createIfcDocumentInformation(DocumentId="X", Name="FOOBAR", Scope="DOCUMENTATION")
        subject.import_sheets()
        props = bpy.context.scene.DocProperties
        assert props.sheets[0].ifc_definition_id == document.id()
        assert props.sheets[0].identification == "X"
        assert props.sheets[0].name == "FOOBAR"


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


class TestOpenSvg(NewFile):
    def test_nothing(self):
        pass


class TestRunAssignClassOperator(NewFile):
    def test_nothing(self):
        pass


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
