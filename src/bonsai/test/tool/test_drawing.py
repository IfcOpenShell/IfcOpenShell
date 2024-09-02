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

import os
from pathlib import Path
import bpy
import mathutils
import ifcopenshell
import ifcopenshell.guid
import bonsai.core.tool
import bonsai.tool as tool
from test.bim.bootstrap import NewFile
from bonsai.tool.drawing import Drawing as subject
from bonsai.bim.ifc import IfcStore
from bonsai.bim.module.drawing.data import DecoratorData
from mathutils import Vector

import xml.etree.ElementTree as ET


class TestImplementsTool(NewFile):
    def test_run(self):
        assert isinstance(subject(), bonsai.core.tool.Drawing)


class TestCopyRepresentation(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        source = ifc.createIfcAnnotation(Representation=ifc.createIfcProductDefinitionShape())
        dest = ifc.createIfcAnnotation()
        subject.copy_representation(source, dest)
        assert dest.Representation.is_a("IfcProductDefinitionShape")


class TestCreateAnnotationObject(NewFile):
    def test_nothing(self):
        pass


class TestCreateCamera(NewFile):
    def test_run(self):
        obj = subject.create_camera("Name", mathutils.Matrix(), "PERSPECTIVE")
        assert obj.name == "Name"
        assert obj.matrix_world == mathutils.Matrix()
        assert obj.data.type == "PERSP"
        assert obj.data.ortho_scale == 50
        assert obj.data.clip_end == 10
        assert obj.users_collection == tuple()


class TestCreateSvgSheet(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcProject")
        tool.Ifc.set(ifc)
        ifc_path = Path("test/files/temp/test.ifc").absolute()
        bpy.ops.bim.save_project(filepath=str(ifc_path), should_save_as=True)
        document = ifc.createIfcDocumentInformation(
            Identification="X",
            Name="FOOBAR",
            Scope="SHEET",
            Location=(ifc_path.parent / "layouts" / "X - FOOBAR.svg").as_posix(),
        )
        uri = subject.create_svg_sheet(document, "A1")
        assert uri.endswith(".svg")
        assert os.path.isfile(uri)


class TestDeleteCollection(NewFile):
    def test_run(self):
        collection = bpy.data.collections.new("Foobar")
        subject.delete_collection(collection)
        assert not bpy.data.collections.get("Foobar")


class TestDeleteDrawingElements(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        obj = bpy.data.objects.new("Object", bpy.data.meshes.new("Mesh"))
        collection = bpy.data.collections.new("Collection")
        bpy.context.scene.collection.children.link(collection)
        collection.objects.link(obj)
        element = ifc.createIfcAnnotation(GlobalId=ifcopenshell.guid.new())
        tool.Ifc.link(element, obj)

        element_id = element.id()
        subject.delete_drawing_elements([element])
        try:
            ifc.by_id(element_id)
            assert False
        except:
            pass
        assert not bpy.data.objects.get("Object")


class TestDisableEditingDrawings(NewFile):
    def test_run(self):
        bpy.context.scene.DocProperties.is_editing_drawings = True
        subject.disable_editing_drawings()
        assert bpy.context.scene.DocProperties.is_editing_drawings == False


class TestDisableEditingSchedules(NewFile):
    def test_run(self):
        bpy.context.scene.DocProperties.is_editing_schedules = True
        subject.disable_editing_schedules()
        assert bpy.context.scene.DocProperties.is_editing_schedules == False


class TestDisableEditingReferences(NewFile):
    def test_run(self):
        bpy.context.scene.DocProperties.is_editing_references = True
        subject.disable_editing_references()
        assert bpy.context.scene.DocProperties.is_editing_references == False


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


class TestDisableEditingAssignedProduct(NewFile):
    def test_run(self):
        obj = bpy.data.objects.new("Object", None)
        obj.BIMAssignedProductProperties.is_editing_product = True
        subject.disable_editing_assigned_product(obj)
        assert obj.BIMAssignedProductProperties.is_editing_product == False


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


class TestEnableEditingSchedules(NewFile):
    def test_run(self):
        bpy.context.scene.DocProperties.is_editing_schedules = False
        subject.enable_editing_schedules()
        assert bpy.context.scene.DocProperties.is_editing_schedules == True


class TestEnableEditingReferences(NewFile):
    def test_run(self):
        bpy.context.scene.DocProperties.is_editing_references = False
        subject.enable_editing_references()
        assert bpy.context.scene.DocProperties.is_editing_references == True


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


class TestEnableEditingAssignedProduct(NewFile):
    def test_run(self):
        obj = bpy.data.objects.new("Object", None)
        subject.enable_editing_assigned_product(obj)
        assert obj.BIMAssignedProductProperties.is_editing_product == True


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
        ifc.createIfcDocumentInformation(Identification="FOOBAR", Scope="SHEET")
        assert subject.ensure_unique_identification("FOOBAR") == "FOOBAR-X"
        ifc.createIfcDocumentInformation(Identification="FOOBAR-X", Scope="SHEET")
        assert subject.ensure_unique_identification("FOOBAR") == "FOOBAR-X-X"

    def test_unique_document_id_ifc2x3(self):
        ifc = ifcopenshell.file(schema="IFC2X3")
        tool.Ifc.set(ifc)
        assert subject.ensure_unique_identification("FOOBAR") == "FOOBAR"
        ifc.createIfcDocumentInformation(DocumentId="FOOBAR", Scope="SHEET")
        assert subject.ensure_unique_identification("FOOBAR") == "FOOBAR-X"
        ifc.createIfcDocumentInformation(DocumentId="FOOBAR-X", Scope="SHEET")
        assert subject.ensure_unique_identification("FOOBAR") == "FOOBAR-X-X"


class TestExportTextLiteralAttributes(NewFile):
    def test_run(self):
        TestImportTextAttributes().test_run()
        assert subject.export_text_literal_attributes(bpy.data.objects.get("Object")) == [
            {
                "Literal": "Literal",
                "Path": "RIGHT",
                "BoxAlignment": "bottom-left",
            }
        ]


class TestGetAnnotationContext(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        context = ifc.createIfcGeometricRepresentationSubContext(
            ContextType="Plan", ContextIdentifier="Annotation", TargetView="PLAN_VIEW"
        )
        context2 = ifc.createIfcGeometricRepresentationSubContext(
            ContextType="Model", ContextIdentifier="Annotation", TargetView="ELEVATION_VIEW"
        )
        context3 = ifc.createIfcGeometricRepresentationSubContext(
            ContextType="Model", ContextIdentifier="Annotation", TargetView="PLAN_VIEW"
        )
        tool.Ifc.set(ifc)
        assert subject.get_annotation_context("PLAN_VIEW") == context
        assert subject.get_annotation_context("ELEVATION_VIEW") == context2
        assert subject.get_annotation_context("PLAN_VIEW", "FALL") == context3


class TestGetBodyContext(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        context = ifc.createIfcGeometricRepresentationSubContext(
            ContextType="Model", ContextIdentifier="Body", TargetView="MODEL_VIEW"
        )
        tool.Ifc.set(ifc)
        assert subject.get_body_context() == context


class TestGetDocumentUri(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        document = ifc.createIfcDocumentInformation(
            Identification="X", Name="FOOBAR", Scope="SHEET", Location="Location"
        )
        assert subject.get_document_uri(document) == os.path.abspath(os.path.join(tool.Ifc.get_path(), "Location"))

    def test_get_indirect_locations(self):
        ifc = ifcopenshell.file()
        document = ifc.createIfcDocumentInformation(Identification="X", Name="FOOBAR", Scope="SHEET")
        reference = ifc.createIfcDocumentReference(Location="Location", ReferencedDocument=document)
        assert subject.get_document_uri(document) == os.path.abspath(os.path.join(tool.Ifc.get_path(), "Location"))
        assert subject.get_document_uri(reference) == os.path.abspath(os.path.join(tool.Ifc.get_path(), "Location"))

    def test_run_ifc2x3(self):
        ifc = ifcopenshell.file(schema="IFC2X3")
        tool.Ifc.set(ifc)
        reference = ifc.createIfcDocumentReference(Location="Location")
        document = ifc.createIfcDocumentInformation(
            DocumentId="X", Name="FOOBAR", Scope="SHEET", DocumentReferences=[reference]
        )
        assert subject.get_document_uri(document) == os.path.abspath(os.path.join(tool.Ifc.get_path(), "Location"))
        assert subject.get_document_uri(reference) == os.path.abspath(os.path.join(tool.Ifc.get_path(), "Location"))


class TestGetDrawingCollection(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        obj = bpy.data.objects.new("Object", None)
        collection = bpy.data.collections.new("Collection")
        bpy.context.scene.collection.children.link(collection)
        collection.objects.link(obj)
        obj.BIMObjectProperties.collection = collection
        collection.BIMCollectionProperties.obj = obj

        element = ifc.createIfcAnnotation()
        tool.Ifc.link(element, obj)
        assert subject.get_drawing_collection(element) == collection


class TestGetDrawingGroup(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        element = ifc.createIfcAnnotation()
        group = ifcopenshell.api.run("group.add_group", ifc)
        group.ObjectType = "DRAWING"
        ifcopenshell.api.run("group.assign_group", ifc, products=[element], group=group)
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
        ifcopenshell.api.run("group.assign_group", ifc, products=[element], group=group)
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
            ((1, 0, 0, 0), (0, 1, 0, 0), (0, 0, -1, 0), (0, 0, 0, 1))
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
            ((1, 0, 0, 1), (0, 1, 0, 2), (0, 0, -1, 3 + 1.6), (0, 0, 0, 1))
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
        item = ifc.createIfcTextLiteralWithExtent(Literal="Literal", Path="RIGHT", BoxAlignment="bottom-left")
        representation = ifc.createIfcShapeRepresentation(ContextOfItems=context, Items=[item])
        element.Representation.Representations = [representation]
        element.ObjectType = "TEXT"  # TODO: double check if it's valid to set this
        tool.Ifc.link(element, obj)
        assert subject.get_text_literal(obj) == item


class TestGetAssignedProduct(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        wall = ifc.createIfcWall()
        label = ifc.createIfcAnnotation()
        ifcopenshell.api.run("drawing.assign_product", ifc, relating_product=wall, related_object=label)
        assert subject.get_assigned_product(label) == wall


class TestImportDrawings(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        drawing = ifc.createIfcAnnotation(Name="FOOBAR", ObjectType="DRAWING")
        pset = ifcopenshell.api.run("pset.add_pset", ifc, product=drawing, name="EPset_Drawing")
        ifcopenshell.api.run("pset.edit_pset", ifc, pset=pset, properties={"TargetView": "PLAN_VIEW"})
        subject.import_drawings()
        props = bpy.context.scene.DocProperties
        for d in props.drawings:
            d.is_expanded = True
        subject.import_drawings()
        assert props.drawings[1].target_view == "PLAN_VIEW"
        assert props.drawings[2].ifc_definition_id == drawing.id()
        assert props.drawings[2].name == "FOOBAR"


class TestImportSchedules(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        ifc.createIfcDocumentInformation(Identification="Y", Name="FOOBAZ")
        document = ifc.createIfcDocumentInformation(Identification="X", Name="FOOBAR", Scope="SCHEDULE")
        subject.import_documents("SCHEDULE")
        props = bpy.context.scene.DocProperties
        assert props.schedules[0].ifc_definition_id == document.id()
        assert props.schedules[0].identification == "X"
        assert props.schedules[0].name == "FOOBAR"

    def test_run_ifc2x3(self):
        ifc = ifcopenshell.file(schema="IFC2X3")
        tool.Ifc.set(ifc)
        ifc.createIfcDocumentInformation(DocumentId="Y", Name="FOOBAZ")
        document = ifc.createIfcDocumentInformation(DocumentId="X", Name="FOOBAR", Scope="SCHEDULE")
        subject.import_documents("SCHEDULE")
        props = bpy.context.scene.DocProperties
        assert props.schedules[0].ifc_definition_id == document.id()
        assert props.schedules[0].identification == "X"
        assert props.schedules[0].name == "FOOBAR"


class TestImportReferences(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        ifc.createIfcDocumentInformation(Identification="Y", Name="FOOBAZ")
        document = ifc.createIfcDocumentInformation(Identification="X", Name="FOOBAR", Scope="REFERENCE")
        subject.import_documents("REFERENCE")
        props = bpy.context.scene.DocProperties
        assert props.references[0].ifc_definition_id == document.id()
        assert props.references[0].identification == "X"
        assert props.references[0].name == "FOOBAR"

    def test_run_ifc2x3(self):
        ifc = ifcopenshell.file(schema="IFC2X3")
        tool.Ifc.set(ifc)
        ifc.createIfcDocumentInformation(DocumentId="Y", Name="FOOBAZ")
        document = ifc.createIfcDocumentInformation(DocumentId="X", Name="FOOBAR", Scope="REFERENCE")
        subject.import_documents("REFERENCE")
        props = bpy.context.scene.DocProperties
        assert props.references[0].ifc_definition_id == document.id()
        assert props.references[0].identification == "X"
        assert props.references[0].name == "FOOBAR"


class TestImportSheets(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        ifc.createIfcDocumentInformation(Identification="Y", Name="FOOBAZ")
        document = ifc.createIfcDocumentInformation(Identification="X", Name="FOOBAR", Scope="SHEET")
        subject.import_sheets()
        props = bpy.context.scene.DocProperties
        assert props.sheets[0].ifc_definition_id == document.id()
        assert props.sheets[0].identification == "X"
        assert props.sheets[0].name == "FOOBAR"

    def test_run_ifc2x3(self):
        ifc = ifcopenshell.file(schema="IFC2X3")
        tool.Ifc.set(ifc)
        ifc.createIfcDocumentInformation(DocumentId="Y", Name="FOOBAZ")
        document = ifc.createIfcDocumentInformation(DocumentId="X", Name="FOOBAR", Scope="SHEET")
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
        item = ifc.createIfcTextLiteralWithExtent(Literal="Literal", Path="RIGHT", BoxAlignment="bottom-left")
        representation = ifc.createIfcShapeRepresentation(ContextOfItems=context, Items=[item])
        element.Representation.Representations = [representation]
        element.ObjectType = "TEXT"  # TODO: double check if it's valid to set this
        tool.Ifc.link(element, obj)
        subject.import_text_attributes(obj)
        literal_props = obj.BIMTextProperties.literals[0]
        assert literal_props.attributes.get("Literal").string_value == "Literal"
        assert literal_props.attributes.get("Path").enum_value == "RIGHT"
        assert literal_props.attributes.get("BoxAlignment").string_value == "bottom-left"


class TestImportAssignedProduct(NewFile):
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
        subject.import_assigned_product(label_obj)
        assert label_obj.BIMAssignedProductProperties.relating_product == wall_obj

    def test_doing_nothing_if_no_product_to_import(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        label = ifc.createIfcAnnotation()
        label_obj = bpy.data.objects.new("Object", None)
        tool.Ifc.link(label, label_obj)
        subject.import_assigned_product(label_obj)
        assert label_obj.BIMAssignedProductProperties.relating_product is None


class TestOpenSchedule(NewFile):
    def open_spreadsheet(self):
        pass


class TestOpenReference(NewFile):
    def open_svg(self):
        pass


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


class TestSetName(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        drawing = ifc.createIfcAnnotation()
        subject.set_name(drawing, "Name")
        assert drawing.Name == "Name"


class TestShowDecorations(NewFile):
    def test_run(self):
        bpy.context.scene.DocProperties.should_draw_decorations = False
        subject.show_decorations()
        assert bpy.context.scene.DocProperties.should_draw_decorations is True


class TestDrawingMaintainingSheetPosition(NewFile):
    def get_sheet_drawing_data(self, layout_path):
        SVG = "{http://www.w3.org/2000/svg}"
        ET.register_namespace("", SVG)
        layout_tree = ET.parse(layout_path)
        layout_root = layout_tree.getroot()

        drawing_view = layout_root.findall(f'{SVG}g[@data-type="drawing"]')[0]

        drawing_data = {}
        for image in drawing_view.findall(f"{SVG}image"):
            attribs = ["x", "y", "width", "height"]
            image_type = image.attrib["data-type"]
            drawing_data[image_type] = tuple([round(float(image.attrib[attr]), 2) for attr in attribs])

        return drawing_data

    def test_run(self):
        props = bpy.context.scene.DocProperties
        bpy.ops.bim.create_project()
        ifc = tool.Ifc.get()
        sheet_path = Path.cwd() / "layouts" / "A00 - UNTITLED.svg"

        bpy.ops.mesh.primitive_cube_add(size=10, location=(0, 0, 4))
        obj = bpy.data.objects["Cube"]
        bpy.ops.bim.assign_class(ifc_class="IfcActuator", predefined_type="ELECTRICACTUATOR", userdefined_type="")

        bpy.ops.bim.load_sheets()
        bpy.ops.bim.add_sheet()

        bpy.ops.bim.load_drawings()
        for d in props.drawings:
            d.is_expanded = True
        bpy.ops.bim.add_drawing()

        drawing = ifc.by_type("IfcAnnotation")[0]
        for i, d in enumerate(props.drawings):
            if d.ifc_definition_id == drawing.id():
                props.active_drawing_index = i
        bpy.ops.bim.activate_drawing(drawing=drawing.id())
        bpy.ops.bim.create_drawing()
        bpy.ops.bim.add_drawing_to_sheet()
        bpy.ops.bim.open_sheet()

        # uncomment if debugging
        # without `sleep` `bim.open_sheet` tend to open sheet in browser
        # with PLAN_VIEW.svg that will be created only later
        # from time import sleep
        # sleep(0.1)

        # check drawing default position
        drawing_data = self.get_sheet_drawing_data(sheet_path)
        assert drawing_data["foreground"] == (30.0, 30.0, 500.0, 500.0)
        assert drawing_data["view-title"] == (30.0, 535.0, 50.22, 10.0)

        bpy.context.scene.camera.data.BIMCameraProperties.width = 25
        bpy.context.scene.camera.data.BIMCameraProperties.height = 25
        tool.Blender.force_depsgraph_update()

        bpy.ops.bim.create_drawing()
        bpy.ops.bim.open_sheet()

        assert sheet_path.is_file(), f"Sheet path {sheet_path} doesn't exist"

        # check drawing position on the sheet
        drawing_data = self.get_sheet_drawing_data(sheet_path)
        assert drawing_data["foreground"] == (155.0, 155.0, 250.0, 250.0)
        assert drawing_data["view-title"] == (155.0, 410.0, 50.22, 10.0)


class TestUpdateTextValue(NewFile):
    def test_updating_arbitrary_strings(self):
        TestGetTextLiteral().test_run()
        ifc = tool.Ifc.get()

        obj = bpy.data.objects.get("Object")
        subject.update_text_value(obj)
        literal = obj.BIMTextProperties.literals[0]

        assert obj.BIMTextProperties.font_size == "2.5"
        assert literal.value == "Literal"
        assert literal.box_alignment[:] == tuple([False] * 6 + [True] + [False] * 2)
        assert literal.ifc_definition_id == ifc.by_type("IfcTextLiteralWithExtent")[0].id()

    def test_using_attribute_variables(self):
        TestGetTextLiteral().test_run()

        obj = bpy.data.objects.get("Object")
        ifc = tool.Ifc.get()
        wall = ifc.createIfcWall(Name="Baz")
        label = ifc.by_type("IfcAnnotation")[0]
        ifcopenshell.api.run("drawing.assign_product", ifc, relating_product=wall, related_object=label)

        ifc.by_type("IfcTextLiteralWithExtent")[0].Literal = "Foo {{Name}} Bar"

        subject.update_text_value(obj)
        assert obj.BIMTextProperties.literals[0].value == "Foo Baz Bar"

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
        assert obj.BIMTextProperties.literals[0].value == "Foo Baz Bar"

    def test_update_text_font_size(self):
        TestGetTextLiteral().test_run()
        obj = bpy.data.objects.get("Object")
        with bpy.context.temp_override(active_object=obj):
            bpy.ops.bim.enable_editing_text()
            obj.BIMTextProperties.font_size = "7.0"
            bpy.ops.bim.edit_text()
        annotation_classes = ifcopenshell.util.element.get_pset(tool.Ifc.get_entity(obj), "EPset_Annotation", "Classes")
        assert "title" in annotation_classes
        assert DecoratorData.get_ifc_text_data(obj)["FontSize"] == 7.0

    def test_add_second_literal(self, setup=True):
        if setup:
            TestGetTextLiteral().test_run()
        obj = bpy.data.objects.get("Object")
        with bpy.context.temp_override(active_object=obj):
            bpy.ops.bim.enable_editing_text()
            bpy.ops.bim.add_text_literal()
            literal = obj.BIMTextProperties.literals[1]
            literal.attributes["Literal"].string_value = "test_value"
            bpy.ops.bim.edit_text()

        ifc = tool.Ifc.get()
        assert ifc.by_type("IfcTextLiteralWithExtent")[1].Literal == "test_value"

    def test_disable_text_editing(self):
        # add second literal and change font size to test changing them
        self.test_update_text_font_size()  # sets font size to "7.0"
        self.test_add_second_literal(setup=False)

        obj = bpy.data.objects.get("Object")
        props = obj.BIMTextProperties
        assert obj is not None, obj
        with bpy.context.temp_override(active_object=obj):
            bpy.ops.bim.enable_editing_text()
            bpy.ops.bim.remove_text_literal(literal_prop_id=1)
            props.literals[0].attributes["Literal"].string_value = "changed_value"
            props.font_size = "2.5"
            bpy.ops.bim.disable_editing_text()

        ifc = tool.Ifc.get()
        # test font size
        annotation_classes = ifcopenshell.util.element.get_pset(tool.Ifc.get_entity(obj), "EPset_Annotation", "Classes")
        assert props.font_size == "7.0"
        assert "title" in annotation_classes
        assert DecoratorData.get_ifc_text_data(obj)["FontSize"] == 7.0

        # test second literal is present
        assert props.literals[1].attributes["Literal"].string_value == "test_value"
        assert ifc.by_type("IfcTextLiteralWithExtent")[1].Literal == "test_value"

        # test first literal value is unchanged
        assert props.literals[0].attributes["Literal"].string_value == "Literal"
        assert ifc.by_type("IfcTextLiteralWithExtent")[0].Literal == "Literal"


class TestDrawingStyles(NewFile):
    def setup_project_with_drawing(self):
        bpy.ops.bim.create_project()
        bpy.ops.bim.load_drawings()
        bpy.ops.bim.add_drawing()
        ifc = tool.Ifc.get()
        drawing = ifc.by_type("IfcAnnotation")[0]
        bpy.ops.bim.activate_drawing(drawing=drawing.id())
        self.drawing_styles = bpy.context.scene.DocProperties.drawing_styles

    def test_drawing_styles_not_loaded_if_underlay_is_inactive(self):
        self.setup_project_with_drawing()
        assert len(self.drawing_styles) == 0

    def test_drawing_styles_loaded_on_underlay_enabled(self):
        self.setup_project_with_drawing()
        bpy.context.scene.camera.data.BIMCameraProperties.has_underlay = True
        assert len(self.drawing_styles) == 3

    def test_drawing_styles_reload(self):
        self.setup_project_with_drawing()
        bpy.ops.bim.reload_drawing_styles()
        assert len(self.drawing_styles) == 3


class TestAddReferenceImage(NewFile):
    def test_run(self):
        bpy.context.scene.BIMProjectProperties.template_file = "0"
        bpy.ops.bim.create_project()
        ifc_file = tool.Ifc.get()

        filepath = Path("test/files/image.jpg").absolute()
        bpy.ops.bim.add_reference_image(filepath=str(filepath))

        obj = bpy.data.objects["IfcAnnotation/image"]
        assert obj is not None
        assert tool.Cad.are_vectors_equal(obj.dimensions, Vector((3.53982, 2.0, 0.0)))

        material = obj.active_material
        assert material.name == "image"
        assert material.BIMStyleProperties.ifc_definition_id != 0

        style = ifc_file.by_id(material.BIMStyleProperties.ifc_definition_id)
        styled_items = set(tool.Style.get_styled_items(style))
        representation_items = set(tool.Geometry.get_active_representation(obj).Items)
        assert styled_items == representation_items

        material_nodes = material.node_tree.nodes
        texture_filepath = material_nodes["Image Texture"].image.filepath
        texture_filepath = Path(tool.Blender.blender_path_to_posix(texture_filepath))
        assert texture_filepath == filepath

        uv_node = material_nodes["Texture Coordinate"]
        assert len(uv_node.outputs["Generated"].links[:]) == 1
