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

import bonsai.core.drawing as subject
from test.core.bootstrap import ifc, drawing, collector


class TestEnableEditingText:
    def test_run(self, drawing):
        drawing.enable_editing_text("obj").should_be_called()
        drawing.import_text_attributes("obj").should_be_called()
        subject.enable_editing_text(drawing, obj="obj")


class TestDisableEditingText:
    def test_run(self, drawing):
        drawing.disable_editing_text("obj").should_be_called()
        subject.disable_editing_text(drawing, obj="obj")


class TestEditText:
    def test_run(self, ifc, drawing):
        drawing.synchronise_ifc_and_text_attributes("obj").should_be_called()
        drawing.update_text_size_pset("obj").should_be_called()
        drawing.update_text_value("obj").should_be_called()
        drawing.disable_editing_text("obj").should_be_called()
        subject.edit_text(drawing, obj="obj")


class TestEnableEditingAssignedProduct:
    def test_run(self, drawing):
        drawing.enable_editing_assigned_product("obj").should_be_called()
        drawing.import_assigned_product("obj").should_be_called()
        subject.enable_editing_assigned_product(drawing, obj="obj")


class TestDisableEditingAssignedProduct:
    def test_run(self, drawing):
        drawing.disable_editing_assigned_product("obj").should_be_called()
        subject.disable_editing_assigned_product(drawing, obj="obj")


class TestEditAssignedProduct:
    def test_text_annotation(self, ifc, drawing):
        ifc.get_entity("obj").should_be_called().will_return("element")
        drawing.get_assigned_product("element").should_be_called().will_return("existing_product")
        ifc.run(
            "drawing.unassign_product", relating_product="existing_product", related_object="element"
        ).should_be_called()
        ifc.run("drawing.assign_product", relating_product="product", related_object="element").should_be_called()
        drawing.is_annotation_object_type("element", ("TEXT", "TEXT_LEADER")).should_be_called().will_return(True)
        drawing.update_text_value("obj").should_be_called()
        drawing.disable_editing_assigned_product("obj").should_be_called()
        subject.edit_assigned_product(ifc, drawing, obj="obj", product="product")

    def test_non_text_annotation(self, ifc, drawing):
        ifc.get_entity("obj").should_be_called().will_return("element")
        drawing.get_assigned_product("element").should_be_called().will_return("existing_product")
        ifc.run(
            "drawing.unassign_product", relating_product="existing_product", related_object="element"
        ).should_be_called()
        ifc.run("drawing.assign_product", relating_product="product", related_object="element").should_be_called()
        drawing.is_annotation_object_type("element", ("TEXT", "TEXT_LEADER")).should_be_called().will_return(False)
        drawing.disable_editing_assigned_product("obj").should_be_called()
        subject.edit_assigned_product(ifc, drawing, obj="obj", product="product")


class TestLoadSheets:
    def test_run(self, drawing):
        drawing.import_sheets().should_be_called()
        drawing.enable_editing_sheets().should_be_called()
        subject.load_sheets(drawing)


class TestDisableEditingSheets:
    def test_run(self, drawing):
        drawing.disable_editing_sheets().should_be_called()
        subject.disable_editing_sheets(drawing)


class TestAddSheet:
    def test_run(self, ifc, drawing):
        ifc.run("document.add_information").should_be_called().will_return("sheet")
        ifc.run("document.add_reference", information="sheet").should_be_called().will_return("reference")
        drawing.generate_sheet_identification().should_be_called().will_return("identification")
        drawing.ensure_unique_identification("identification").should_be_called().will_return("u_identification")
        ifc.get_schema().should_be_called().will_return("IFC4")
        drawing.get_default_layout_path("u_identification", "UNTITLED").should_be_called().will_return("layout_path")
        drawing.get_default_titleblock_path("titleblock").should_be_called().will_return("titleblock_path")
        ifc.run(
            "document.edit_information",
            information="sheet",
            attributes={"Identification": "u_identification", "Name": "UNTITLED", "Scope": "SHEET"},
        ).should_be_called()
        drawing.generate_reference_attributes(
            "reference", Location="layout_path", Description="LAYOUT"
        ).should_be_called().will_return("attributes")
        ifc.run(
            "document.edit_reference",
            reference="reference",
            attributes="attributes",
        ).should_be_called()
        drawing.generate_reference_attributes(
            "reference", Location="titleblock_path", Description="TITLEBLOCK"
        ).should_be_called().will_return("attributes2")
        ifc.run(
            "document.edit_reference",
            reference="reference",
            attributes="attributes2",
        ).should_be_called()
        drawing.create_svg_sheet("sheet", "titleblock").should_be_called()
        drawing.import_sheets().should_be_called()
        subject.add_sheet(ifc, drawing, titleblock="titleblock")

    def test_using_a_document_id_in_ifc2x3(self, ifc, drawing):
        ifc.run("document.add_information").should_be_called().will_return("sheet")
        ifc.run("document.add_reference", information="sheet").should_be_called().will_return("reference")
        drawing.generate_sheet_identification().should_be_called().will_return("identification")
        drawing.ensure_unique_identification("identification").should_be_called().will_return("u_identification")
        ifc.get_schema().should_be_called().will_return("IFC2X3")
        drawing.get_default_layout_path("u_identification", "UNTITLED").should_be_called().will_return("layout_path")
        drawing.get_default_titleblock_path("titleblock").should_be_called().will_return("titleblock_path")
        ifc.run(
            "document.edit_information",
            information="sheet",
            attributes={"DocumentId": "u_identification", "Name": "UNTITLED", "Scope": "SHEET"},
        ).should_be_called()
        drawing.generate_reference_attributes(
            "reference", Location="layout_path", Description="LAYOUT"
        ).should_be_called().will_return("attributes")
        ifc.run(
            "document.edit_reference",
            reference="reference",
            attributes="attributes",
        ).should_be_called()
        drawing.generate_reference_attributes(
            "reference", Location="titleblock_path", Description="TITLEBLOCK"
        ).should_be_called().will_return("attributes2")
        ifc.run(
            "document.edit_reference",
            reference="reference",
            attributes="attributes2",
        ).should_be_called()
        drawing.create_svg_sheet("sheet", "titleblock").should_be_called()
        drawing.import_sheets().should_be_called()
        subject.add_sheet(ifc, drawing, titleblock="titleblock")


class TestOpenSheet:
    def test_run(self, drawing):
        drawing.get_document_uri("sheet", "LAYOUT").should_be_called().will_return("uri")
        drawing.open_layout_svg("uri").should_be_called()
        subject.open_sheet(drawing, sheet="sheet")


class TestRemoveSheet:
    def test_run(self, ifc, drawing):
        drawing.get_document_references("sheet").should_be_called().will_return(["reference"])
        drawing.get_reference_description("reference").should_be_called().will_return("LAYOUT")
        drawing.get_document_uri("reference").should_be_called().will_return("relative_uri")
        ifc.resolve_uri("relative_uri").should_be_called().will_return("absolute_uri")
        drawing.does_file_exist("absolute_uri").should_be_called().will_return(True)
        drawing.delete_file("absolute_uri").should_be_called()
        ifc.run("document.remove_information", information="sheet").should_be_called()
        drawing.import_sheets().should_be_called()
        subject.remove_sheet(ifc, drawing, sheet="sheet")


class TestLoadSchedules:
    def test_run(self, drawing):
        drawing.import_documents("SCHEDULE").should_be_called()
        drawing.enable_editing_schedules().should_be_called()
        subject.load_schedules(drawing)


class TestDisableEditingSchedules:
    def test_run(self, drawing):
        drawing.disable_editing_schedules().should_be_called()
        subject.disable_editing_schedules(drawing)


class TestAddSchedule:
    def test_run(self, ifc, drawing):
        ifc.run("document.add_information").should_be_called().will_return("schedule")
        drawing.get_path_filename("uri").should_be_called().will_return("UNTITLED")
        ifc.run("document.add_reference", information="schedule").should_be_called().will_return("reference")
        ifc.get_schema().should_be_called().will_return("IFC4")
        ifc.run(
            "document.edit_information",
            information="schedule",
            attributes={"Identification": "X", "Name": "UNTITLED", "Scope": "SCHEDULE"},
        ).should_be_called()
        ifc.run("document.edit_reference", reference="reference", attributes={"Location": "uri"}).should_be_called()
        drawing.import_documents("SCHEDULE").should_be_called()
        subject.add_document(ifc, drawing, "SCHEDULE", uri="uri")

    def test_using_a_document_id_in_ifc2x3(self, ifc, drawing):
        ifc.run("document.add_information").should_be_called().will_return("schedule")
        drawing.get_path_filename("uri").should_be_called().will_return("UNTITLED")
        ifc.run("document.add_reference", information="schedule").should_be_called().will_return("reference")
        ifc.get_schema().should_be_called().will_return("IFC2X3")
        ifc.run(
            "document.edit_information",
            information="schedule",
            attributes={"DocumentId": "X", "Name": "UNTITLED", "Scope": "SCHEDULE"},
        ).should_be_called()
        ifc.run("document.edit_reference", reference="reference", attributes={"Location": "uri"}).should_be_called()
        drawing.import_documents("SCHEDULE").should_be_called()
        subject.add_document(ifc, drawing, "SCHEDULE", uri="uri")


class TestRemoveSchedule:
    def test_run(self, ifc, drawing):
        ifc.run("document.remove_information", information="schedule").should_be_called()
        drawing.import_documents("SCHEDULE").should_be_called()
        subject.remove_document(ifc, drawing, "SCHEDULE", document="schedule")


class TestOpenSchedule:
    def test_run(self, drawing):
        drawing.get_document_uri("schedule").should_be_called().will_return("uri")
        drawing.open_spreadsheet("uri").should_be_called()
        subject.open_schedule(drawing, schedule="schedule")


class TestUpdateScheduleName:
    def test_do_not_update_if_name_unchanged(self, ifc, drawing):
        drawing.get_name("schedule").should_be_called().will_return("name")
        subject.update_document_name(ifc, drawing, document="schedule", name="name")

    def test_run(self, ifc, drawing):
        drawing.get_name("schedule").should_be_called().will_return("oldname")
        ifc.run("document.edit_information", information="schedule", attributes={"Name": "name"}).should_be_called()
        subject.update_document_name(ifc, drawing, document="schedule", name="name")


class TestLoadReferences:
    def test_run(self, drawing):
        drawing.import_documents("REFERENCE").should_be_called()
        drawing.enable_editing_references().should_be_called()
        subject.load_references(drawing)


class TestDisableEditingReferences:
    def test_run(self, drawing):
        drawing.disable_editing_references().should_be_called()
        subject.disable_editing_references(drawing)


class TestAddReference:
    def test_run(self, ifc, drawing):
        ifc.run("document.add_information").should_be_called().will_return("reference")
        drawing.get_path_filename("uri").should_be_called().will_return("UNTITLED")
        ifc.run("document.add_reference", information="reference").should_be_called().will_return("reference")
        ifc.get_schema().should_be_called().will_return("IFC4")
        ifc.run(
            "document.edit_information",
            information="reference",
            attributes={"Identification": "X", "Name": "UNTITLED", "Scope": "REFERENCE"},
        ).should_be_called()
        ifc.run("document.edit_reference", reference="reference", attributes={"Location": "uri"}).should_be_called()
        drawing.import_documents("REFERENCE").should_be_called()
        subject.add_document(ifc, drawing, "REFERENCE", uri="uri")

    def test_using_a_document_id_in_ifc2x3(self, ifc, drawing):
        ifc.run("document.add_information").should_be_called().will_return("reference")
        drawing.get_path_filename("uri").should_be_called().will_return("UNTITLED")
        ifc.run("document.add_reference", information="reference").should_be_called().will_return("reference")
        ifc.get_schema().should_be_called().will_return("IFC2X3")
        ifc.run(
            "document.edit_information",
            information="reference",
            attributes={"DocumentId": "X", "Name": "UNTITLED", "Scope": "REFERENCE"},
        ).should_be_called()
        ifc.run("document.edit_reference", reference="reference", attributes={"Location": "uri"}).should_be_called()
        drawing.import_documents("REFERENCE").should_be_called()
        subject.add_document(ifc, drawing, "REFERENCE", uri="uri")


class TestRemoveReference:
    def test_run(self, ifc, drawing):
        ifc.run("document.remove_information", information="reference").should_be_called()
        drawing.import_documents("REFERENCE").should_be_called()
        subject.remove_document(ifc, drawing, "REFERENCE", document="reference")


class TestOpenReference:
    def test_run(self, drawing):
        drawing.get_document_uri("reference").should_be_called().will_return("uri")
        drawing.open_svg("uri").should_be_called()
        subject.open_reference(drawing, reference="reference")


class TestUpdateReferenceName:
    def test_do_not_update_if_name_unchanged(self, ifc, drawing):
        drawing.get_name("reference").should_be_called().will_return("name")
        subject.update_document_name(ifc, drawing, document="reference", name="name")

    def test_run(self, ifc, drawing):
        drawing.get_name("reference").should_be_called().will_return("oldname")
        ifc.run("document.edit_information", information="reference", attributes={"Name": "name"}).should_be_called()
        subject.update_document_name(ifc, drawing, document="reference", name="name")


class TestLoadDrawings:
    def test_run(self, drawing):
        drawing.import_drawings().should_be_called()
        drawing.enable_editing_drawings().should_be_called()
        subject.load_drawings(drawing)


class TestDisableEditingDrawings:
    def test_run(self, drawing):
        drawing.disable_editing_drawings().should_be_called()
        subject.disable_editing_drawings(drawing)


class TestAddDrawing:
    def test_run(self, ifc, collector, drawing):
        drawing.generate_drawing_name("target_view", "location_hint").should_be_called().will_return("drawing_name")
        drawing.ensure_unique_drawing_name("drawing_name").should_be_called().will_return("name")
        drawing.generate_drawing_matrix("target_view", "location_hint").should_be_called().will_return("matrix")
        drawing.create_camera("name", "matrix", "location_hint").should_be_called().will_return("obj")
        drawing.get_body_context().should_be_called().will_return("context")
        drawing.run_root_assign_class(
            obj="obj",
            ifc_class="IfcAnnotation",
            predefined_type="DRAWING",
            should_add_representation=True,
            context="context",
            ifc_representation_class=None,
        ).should_be_called().will_return("element")
        ifc.run("group.add_group").should_be_called().will_return("group")
        ifc.run(
            "group.edit_group", group="group", attributes={"Name": "name", "ObjectType": "DRAWING"}
        ).should_be_called()
        ifc.run("group.assign_group", group="group", products=["element"]).should_be_called()
        collector.assign("obj").should_be_called()
        ifc.run("pset.add_pset", product="element", name="EPset_Drawing").should_be_called().will_return("pset")
        drawing.get_default_drawing_resource_path("Stylesheet").should_be_called().will_return("stylesheet.css")
        drawing.get_default_drawing_resource_path("Markers").should_be_called().will_return("markers.svg")
        drawing.get_default_drawing_resource_path("Symbols").should_be_called().will_return("symbols.svg")
        drawing.get_default_drawing_resource_path("Patterns").should_be_called().will_return("patterns.svg")
        drawing.get_default_drawing_resource_path("ShadingStyles").should_be_called().will_return("shading_styles.json")
        drawing.get_default_shading_style().should_be_called().will_return("Blender Default")
        drawing.setup_shading_styles_path("shading_styles.json").should_be_called()
        drawing.get_unit_system().should_be_called().will_return("METRIC")
        ifc.run(
            "pset.edit_pset",
            pset="pset",
            properties={
                "TargetView": "target_view",
                "Scale": "1/100",
                "HumanScale": "1:100",
                "HasUnderlay": False,
                "HasLinework": True,
                "HasAnnotation": True,
                "GlobalReferencing": True,
                "Stylesheet": "stylesheet.css",
                "Markers": "markers.svg",
                "Symbols": "symbols.svg",
                "Patterns": "patterns.svg",
                "ShadingStyles": "shading_styles.json",
                "CurrentShadingStyle": "Blender Default",
            },
        ).should_be_called()
        drawing.get_default_drawing_path("name").should_be_called().will_return("uri")
        ifc.run("document.add_information").should_be_called().will_return("information")
        ifc.run("document.add_reference", information="information").should_be_called().will_return("reference")
        ifc.get_schema().should_be_called().will_return("IFC4")
        ifc.run(
            "document.edit_information",
            information="information",
            attributes={"Identification": "X", "Name": "name", "Scope": "DRAWING"},
        ).should_be_called()
        ifc.run("document.edit_reference", reference="reference", attributes={"Location": "uri"}).should_be_called()
        ifc.run("document.assign_document", products=["element"], document="reference").should_be_called()
        drawing.import_drawings().should_be_called()
        subject.add_drawing(ifc, collector, drawing, target_view="target_view", location_hint="location_hint")


class TestDuplicateDrawing:
    def test_run(self, ifc, drawing):
        drawing.get_name("drawing").should_be_called().will_return("name")
        drawing.ensure_unique_drawing_name("name").should_be_called().will_return("unique_name")
        ifc.run("root.copy_class", product="drawing").should_be_called().will_return("new_drawing")
        drawing.copy_representation("drawing", "new_drawing").should_be_called()
        drawing.set_name("new_drawing", "unique_name").should_be_called()
        drawing.get_drawing_group("new_drawing").should_be_called().will_return("group")
        ifc.run("group.unassign_group", group="group", products=["new_drawing"]).should_be_called()
        ifc.run("group.add_group").should_be_called().will_return("new_group")
        ifc.run(
            "group.edit_group", group="new_group", attributes={"Name": "unique_name", "ObjectType": "DRAWING"}
        ).should_be_called()
        ifc.run("group.assign_group", group="new_group", products=["new_drawing"]).should_be_called()
        drawing.get_group_elements("group").should_be_called().will_return(["drawing", "annotation"])
        ifc.run("root.copy_class", product="annotation").should_be_called().will_return("new_annotation")
        drawing.copy_representation("annotation", "new_annotation").should_be_called()
        ifc.run("group.unassign_group", group="group", products=["new_annotation"]).should_be_called()
        ifc.run("group.assign_group", group="new_group", products=["new_annotation"]).should_be_called()

        drawing.get_drawing_document("new_drawing").should_be_called().will_return("old_reference")
        ifc.run("document.unassign_document", products=["new_drawing"], document="old_reference").should_be_called()

        ifc.run("document.add_information").should_be_called().will_return("information")
        ifc.run("document.add_reference", information="information").should_be_called().will_return("reference")
        ifc.get_schema().should_be_called().will_return("IFC4")
        drawing.get_default_drawing_path("unique_name").should_be_called().will_return("drawing_path")
        ifc.run(
            "document.edit_information",
            information="information",
            attributes={"Identification": "X", "Name": "unique_name", "Scope": "DRAWING"},
        ).should_be_called()
        ifc.run(
            "document.edit_reference", reference="reference", attributes={"Location": "drawing_path"}
        ).should_be_called()
        ifc.run("document.assign_document", products=["new_drawing"], document="reference").should_be_called()

        drawing.import_drawings().should_be_called()
        subject.duplicate_drawing(ifc, drawing, drawing="drawing", should_duplicate_annotations=True)


class TestRemoveDrawing:
    def test_run(self, ifc, drawing):
        drawing.is_active_drawing("drawing").should_be_called().will_return(True)
        drawing.run_drawing_activate_model().should_be_called()
        drawing.get_drawing_collection("drawing").should_be_called().will_return("collection")
        drawing.get_drawing_group("drawing").should_be_called().will_return("group")
        drawing.get_group_elements("group").should_be_called().will_return("elements")
        drawing.delete_drawing_elements("elements").should_be_called()
        ifc.run("group.remove_group", group="group").should_be_called()
        drawing.delete_collection("collection").should_be_called()
        drawing.get_drawing_references("drawing").should_be_called().will_return(["reference"])
        ifc.get_object("reference").should_be_called().will_return("reference_obj")
        drawing.delete_object("reference_obj").should_be_called()
        ifc.run("root.remove_product", product="reference").should_be_called()
        drawing.get_drawing_document("drawing").should_be_called().will_return("reference")
        drawing.get_reference_document("reference").should_be_called().will_return("information")
        drawing.get_document_uri("information").should_be_called().will_return("relative_uri")
        ifc.resolve_uri("relative_uri").should_be_called().will_return("absolute_uri")
        drawing.does_file_exist("absolute_uri").should_be_called().will_return(True)
        drawing.delete_file("absolute_uri").should_be_called()
        ifc.run("document.remove_information", information="information").should_be_called()
        drawing.import_drawings().should_be_called()
        subject.remove_drawing(ifc, drawing, drawing="drawing")


class TestUpdateDrawingName:
    def test_do_not_update_if_name_unchanged(self, ifc, drawing):
        drawing.get_name("drawing").should_be_called().will_return("name")
        drawing.get_drawing_group("drawing").should_be_called().will_return("group")
        drawing.get_name("group").should_be_called().will_return("name")
        drawing.get_drawing_collection("drawing").should_be_called().will_return("collection")
        drawing.set_drawing_collection_name("drawing", "collection").should_be_called()

        drawing.get_drawing_document("drawing").should_be_called().will_return("reference")
        drawing.get_reference_document("reference").should_be_called().will_return("information")
        ifc.run("document.edit_information", information="information", attributes={"Name": "name"}).should_be_called()
        drawing.get_reference_location("reference").should_be_called().will_return("location")
        drawing.get_default_drawing_path("name").should_be_called().will_return("location")

        subject.update_drawing_name(ifc, drawing, drawing="drawing", name="name")

    def test_run(self, ifc, drawing):
        drawing.get_name("drawing").should_be_called().will_return("oldname")
        ifc.run("attribute.edit_attributes", product="drawing", attributes={"Name": "name"}).should_be_called()
        drawing.get_drawing_group("drawing").should_be_called().will_return("group")
        drawing.get_name("group").should_be_called().will_return("oldname")
        ifc.run("attribute.edit_attributes", product="group", attributes={"Name": "name"}).should_be_called()
        drawing.get_drawing_collection("drawing").should_be_called().will_return("collection")
        drawing.set_drawing_collection_name("drawing", "collection").should_be_called()

        drawing.get_drawing_document("drawing").should_be_called().will_return("reference")
        drawing.get_reference_document("reference").should_be_called().will_return("information")
        ifc.run("document.edit_information", information="information", attributes={"Name": "name"}).should_be_called()
        drawing.get_reference_location("reference").should_be_called().will_return("old_location")
        drawing.get_default_drawing_path("name").should_be_called().will_return("new_location")

        ifc.run(
            "document.edit_reference", reference="reference", attributes={"Location": "new_location"}
        ).should_be_called()
        ifc.resolve_uri("old_location").should_be_called().will_return("old_uri")
        drawing.does_file_exist("old_uri").should_be_called().will_return(True)
        ifc.resolve_uri("new_location").should_be_called().will_return("new_uri")
        drawing.move_file("old_uri", "new_uri").should_be_called()

        drawing.get_references_with_location("old_location").should_be_called().will_return(
            ["reference_with_old_location"]
        )
        ifc.run(
            "document.edit_reference", reference="reference_with_old_location", attributes={"Location": "new_location"}
        ).should_be_called()
        drawing.get_reference_document("reference_with_old_location").should_be_called().will_return(
            "sheet_with_old_location"
        )

        drawing.get_document_uri("sheet_with_old_location", "LAYOUT").should_be_called().will_return(
            "relative_layout_uri"
        )
        ifc.resolve_uri("relative_layout_uri").should_be_called().will_return("absolute_layout_uri")
        drawing.does_file_exist("absolute_layout_uri").should_be_called().will_return(True)
        drawing.update_embedded_svg_location(
            "absolute_layout_uri", "reference_with_old_location", "new_uri"
        ).should_be_called()

        drawing.is_editing_sheets().should_be_called().will_return(True)
        drawing.import_sheets().should_be_called()

        subject.update_drawing_name(ifc, drawing, drawing="drawing", name="name")


class TestAddAnnotation:
    def test_run(self, ifc, collector, drawing):
        drawing.get_drawing_target_view("drawing").should_be_called().will_return("target_view")
        drawing.get_annotation_context("target_view", "object_type").should_be_called().will_return("context")
        drawing.show_decorations().should_be_called()
        drawing.create_annotation_object("drawing", "object_type").should_be_called().will_return("obj")
        ifc.get_entity("obj").should_be_called().will_return(None)
        drawing.get_ifc_representation_class("object_type").should_be_called().will_return("ifc_representation_class")
        drawing.run_root_assign_class(
            obj="obj",
            ifc_class="IfcAnnotation",
            predefined_type="object_type",
            should_add_representation=True,
            context="context",
            ifc_representation_class="ifc_representation_class",
        ).should_be_called().will_return("element")
        drawing.get_drawing_group("drawing").should_be_called().will_return("group")
        ifc.run("group.assign_group", group="group", products=["element"]).should_be_called()
        collector.assign("obj").should_be_called()
        drawing.enable_editing("obj").should_be_called()
        subject.add_annotation(ifc, collector, drawing, drawing="drawing", object_type="object_type")

    def test_create_a_missing_annotation_context_on_the_fly(self, ifc, collector, drawing):
        drawing.get_drawing_target_view("drawing").should_be_called().will_return("target_view")
        drawing.get_annotation_context("target_view", "object_type").should_be_called().will_return(None)
        drawing.create_annotation_context("target_view", "object_type").should_be_called().will_return("context")
        drawing.show_decorations().should_be_called()
        drawing.create_annotation_object("drawing", "object_type").should_be_called().will_return("obj")
        ifc.get_entity("obj").should_be_called().will_return(None)
        drawing.get_ifc_representation_class("object_type").should_be_called().will_return("ifc_representation_class")
        drawing.run_root_assign_class(
            obj="obj",
            ifc_class="IfcAnnotation",
            predefined_type="object_type",
            should_add_representation=True,
            context="context",
            ifc_representation_class="ifc_representation_class",
        ).should_be_called().will_return("element")
        drawing.get_drawing_group("drawing").should_be_called().will_return("group")
        ifc.run("group.assign_group", group="group", products=["element"]).should_be_called()
        collector.assign("obj").should_be_called()
        drawing.enable_editing("obj").should_be_called()
        subject.add_annotation(ifc, collector, drawing, drawing="drawing", object_type="object_type")
