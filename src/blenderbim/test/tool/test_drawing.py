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
from blenderbim.bim.ifc import IfcStore


class TestImplementsTool(NewFile):
    def test_run(self):
        assert isinstance(subject(), blenderbim.core.tool.Drawing)


class TestCreateAnnotationObject(NewFile):
    def test_nothing(self):
        pass


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


class TestDeleteCollection(NewFile):
    def test_run(self):
        collection = bpy.data.collections.new("Foobar")
        subject.delete_collection(collection)
        assert not bpy.data.collections.get("Foobar")


class TestDeleteDrawingElements(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        obj = bpy.data.objects.new("Object", None)
        collection = bpy.data.collections.new("Collection")
        bpy.context.scene.collection.children.link(collection)
        collection.objects.link(obj)
        element = ifc.createIfcAnnotation()
        tool.Ifc.link(element, obj)

        element_id = element.id()
        subject.delete_drawing_elements([element])
        assert element_id in IfcStore.deleted_ids
        assert not bpy.data.objects.get("Object")


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


class TestEnableEditing(NewFile):
    def test_run(self):
        obj = bpy.data.objects.new("Object", None)
        bpy.context.scene.collection.objects.link(obj)
        subject.enable_editing(obj)
        assert obj in bpy.context.selected_objects


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


class TestGetAnnotationContext(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        context = ifc.createIfcGeometricRepresentationSubContext(
            ContextType="Plan", ContextIdentifier="Annotation", TargetView="PLAN_VIEW"
        )
        tool.Ifc.set(ifc)
        assert subject.get_annotation_context("PLAN_VIEW") == context


class TestGetBodyContext(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        context = ifc.createIfcGeometricRepresentationSubContext(
            ContextType="Model", ContextIdentifier="Body", TargetView="MODEL_VIEW"
        )
        tool.Ifc.set(ifc)
        assert subject.get_body_context() == context


class TestGetDrawingCollection(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        obj = bpy.data.objects.new("Object", None)
        collection = bpy.data.collections.new("Collection")
        bpy.context.scene.collection.children.link(collection)
        collection.objects.link(obj)
        element = ifc.createIfcAnnotation()
        tool.Ifc.link(element, obj)
        assert subject.get_drawing_collection(element) == collection


class TestGetDrawingGroup(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        element = ifc.createIfcAnnotation()
        group = ifcopenshell.api.run("group.add_group", ifc)
        ifcopenshell.api.run("group.assign_group", ifc, product=element, group=group)
        assert subject.get_drawing_group(element) == group


class TestGetDrawingTargetView(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        element = ifc.createIfcAnnotation()
        pset = ifcopenshell.api.run("pset.add_pset", ifc, product=element, name="EPset_Drawing")
        ifcopenshell.api.run("pset.edit_pset", ifc, pset=pset, properties={"TargetView": "PLAN_VIEW"})
        assert subject.get_drawing_target_view(element) == "PLAN_VIEW"


class TestGetGroupElements(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        element = ifc.createIfcAnnotation()
        group = ifcopenshell.api.run("group.add_group", ifc)
        ifcopenshell.api.run("group.assign_group", ifc, product=element, group=group)
        assert subject.get_group_elements(group) == (element,)


class TestGetIfcRepresentationClass(NewFile):
    def test_run(self):
        assert subject.get_ifc_representation_class("TEXT") == "IfcTextLiteral"
        assert subject.get_ifc_representation_class("TEXT_LEADER") == "IfcGeometricCurveSet/IfcTextLiteral"
        assert subject.get_ifc_representation_class("FOOBAR") == ""


class TestGetName(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        assert subject.get_name(ifc.createIfcWall(Name="Foobar")) == "Foobar"


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

    def test_creating_a_plan_view_at_the_cursor_at_a_storey(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        obj = bpy.data.objects.new("Object", None)
        element = ifc.createIfcBuildingStorey()
        tool.Ifc.link(element, obj)
        bpy.context.scene.collection.objects.link(obj)
        obj.matrix_world[2][3] = 3
        bpy.context.scene.cursor.location = (1.0, 2.0, 0.0)
        m = subject.generate_drawing_matrix("PLAN_VIEW", element.id())
        assert round(m[0][3], 3) == 1
        assert round(m[1][3], 3) == 2
        assert round(m[2][3], 3) == 4.6

    def test_creating_an_rcp_at_the_origin(self):
        assert subject.generate_drawing_matrix("REFLECTED_PLAN_VIEW", None) == mathutils.Matrix(
            ((-1, 0, 0, 0), (0, 1, 0, 0), (0, 0, -1, 0), (0, 0, 0, 1))
        )

    def test_creating_an_rcp_at_the_cursor_at_a_storey(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        obj = bpy.data.objects.new("Object", None)
        element = ifc.createIfcBuildingStorey()
        tool.Ifc.link(element, obj)
        bpy.context.scene.collection.objects.link(obj)
        obj.matrix_world[2][3] = 3
        bpy.context.scene.cursor.location = (1.0, 2.0, 0.0)
        assert subject.generate_drawing_matrix("REFLECTED_PLAN_VIEW", element.id()) == mathutils.Matrix(
            ((-1, 0, 0, 1), (0, 1, 0, 2), (0, 0, -1, 3 + 1.6), (0, 0, 0, 1))
        )

    def test_creating_a_north_elevation_at_the_cursor(self):
        bpy.context.scene.cursor.location = (1.0, 2.0, 3.0)
        assert subject.generate_drawing_matrix("ELEVATION_VIEW", "NORTH") == mathutils.Matrix(
            ((-1, 0, 0, 1), (0, 0, 1, 2), (0, 1, 0, 3), (0, 0, 0, 1))
        )

    def test_creating_a_south_elevation_at_the_cursor(self):
        bpy.context.scene.cursor.location = (1.0, 2.0, 3.0)
        assert subject.generate_drawing_matrix("ELEVATION_VIEW", "SOUTH") == mathutils.Matrix(
            ((1, 0, 0, 1), (0, 0, -1, 2), (0, 1, 0, 3), (0, 0, 0, 1))
        )

    def test_creating_an_east_elevation_at_the_cursor(self):
        bpy.context.scene.cursor.location = (1.0, 2.0, 3.0)
        assert subject.generate_drawing_matrix("ELEVATION_VIEW", "EAST") == mathutils.Matrix(
            ((0, 0, 1, 1), (1, 0, 0, 2), (0, 1, 0, 3), (0, 0, 0, 1))
        )

    def test_creating_a_west_elevation_at_the_cursor(self):
        bpy.context.scene.cursor.location = (1.0, 2.0, 3.0)
        assert subject.generate_drawing_matrix("ELEVATION_VIEW", "WEST") == mathutils.Matrix(
            ((0, 0, -1, 1), (-1, 0, 0, 2), (0, 1, 0, 3), (0, 0, 0, 1))
        )

    def test_creating_a_north_section_at_the_cursor(self):
        bpy.context.scene.cursor.location = (1.0, 2.0, 3.0)
        assert subject.generate_drawing_matrix("SECTION_VIEW", "NORTH") == mathutils.Matrix(
            ((1, 0, 0, 1), (0, 0, -1, 2), (0, 1, 0, 3), (0, 0, 0, 1))
        )

    def test_creating_a_south_section_at_the_cursor(self):
        bpy.context.scene.cursor.location = (1.0, 2.0, 3.0)
        assert subject.generate_drawing_matrix("SECTION_VIEW", "SOUTH") == mathutils.Matrix(
            ((-1, 0, 0, 1), (0, 0, 1, 2), (0, 1, 0, 3), (0, 0, 0, 1))
        )

    def test_creating_an_east_section_at_the_cursor(self):
        bpy.context.scene.cursor.location = (1.0, 2.0, 3.0)
        assert subject.generate_drawing_matrix("SECTION_VIEW", "EAST") == mathutils.Matrix(
            ((0, 0, -1, 1), (-1, 0, 0, 2), (0, 1, 0, 3), (0, 0, 0, 1))
        )

    def test_creating_a_west_section_at_the_cursor(self):
        bpy.context.scene.cursor.location = (1.0, 2.0, 3.0)
        assert subject.generate_drawing_matrix("SECTION_VIEW", "WEST") == mathutils.Matrix(
            ((0, 0, 1, 1), (1, 0, 0, 2), (0, 1, 0, 3), (0, 0, 0, 1))
        )


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
        pset = ifcopenshell.api.run("pset.add_pset", ifc, product=drawing, name="EPset_Drawing")
        ifcopenshell.api.run("pset.edit_pset", ifc, pset=pset, properties={"TargetView": "PLAN_VIEW"})
        subject.import_drawings()
        props = bpy.context.scene.DocProperties
        assert props.drawings[0].ifc_definition_id == drawing.id()
        assert props.drawings[0].name == "FOOBAR"
        assert props.drawings[0].target_view == "PLAN_VIEW"


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


class TestRunRootAssignClassOperator(NewFile):
    def test_nothing(self):
        pass


class TestSetDrawingCollectionName(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        group = ifc.createIfcGroup(Name="Foobaz")
        collection = bpy.data.collections.new("Foobar")
        subject.set_drawing_collection_name(group, collection)
        assert collection.name == "IfcGroup/Foobaz"


class TestShowDecorations(NewFile):
    def test_run(self):
        bpy.context.scene.DocProperties.should_draw_decorations = False
        subject.show_decorations()
        assert bpy.context.scene.DocProperties.should_draw_decorations is True


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
