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

import blenderbim.core.drawing as subject
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
        drawing.get_text_literal("obj").should_be_called().will_return("text")
        drawing.export_text_literal_attributes("obj").should_be_called().will_return("attributes")
        ifc.run("drawing.edit_text_literal", text_literal="text", attributes="attributes").should_be_called()
        drawing.update_text_value("obj").should_be_called()
        drawing.disable_editing_text("obj").should_be_called()
        subject.edit_text(ifc, drawing, obj="obj")


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
    def test_run(self, ifc, drawing):
        ifc.get_entity("obj").should_be_called().will_return("element")
        drawing.get_assigned_product("element").should_be_called().will_return("existing_product")
        ifc.run(
            "drawing.unassign_product", relating_product="existing_product", related_object="element"
        ).should_be_called()
        ifc.run("drawing.assign_product", relating_product="product", related_object="element").should_be_called()
        drawing.update_text_value("obj").should_be_called()
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
        drawing.generate_sheet_identification().should_be_called().will_return("identification")
        drawing.ensure_unique_identification("identification").should_be_called().will_return("u_identification")
        ifc.get_schema().should_be_called().will_return("IFC4")
        ifc.run(
            "document.edit_information",
            information="sheet",
            attributes={"Identification": "u_identification", "Name": "UNTITLED", "Scope": "DOCUMENTATION"},
        ).should_be_called()
        drawing.create_svg_sheet("sheet", "titleblock").should_be_called()
        drawing.import_sheets().should_be_called()
        subject.add_sheet(ifc, drawing, titleblock="titleblock")

    def test_using_a_document_id_in_ifc2x3(self, ifc, drawing):
        ifc.run("document.add_information").should_be_called().will_return("sheet")
        drawing.generate_sheet_identification().should_be_called().will_return("identification")
        drawing.ensure_unique_identification("identification").should_be_called().will_return("u_identification")
        ifc.get_schema().should_be_called().will_return("IFC2X3")
        ifc.run(
            "document.edit_information",
            information="sheet",
            attributes={"DocumentId": "u_identification", "Name": "UNTITLED", "Scope": "DOCUMENTATION"},
        ).should_be_called()
        drawing.create_svg_sheet("sheet", "titleblock").should_be_called()
        drawing.import_sheets().should_be_called()
        subject.add_sheet(ifc, drawing, titleblock="titleblock")


class TestOpenSheet:
    def test_run(self, drawing):
        drawing.get_document_uri("sheet").should_be_called().will_return("uri")
        drawing.open_svg("uri").should_be_called()
        subject.open_sheet(drawing, sheet="sheet")


class TestRemoveSheet:
    def test_run(self, ifc, drawing):
        ifc.run("document.remove_information", information="sheet").should_be_called()
        drawing.import_sheets().should_be_called()
        subject.remove_sheet(ifc, drawing, sheet="sheet")


class TestLoadSchedules:
    def test_run(self, drawing):
        drawing.import_schedules().should_be_called()
        drawing.enable_editing_schedules().should_be_called()
        subject.load_schedules(drawing)


class TestDisableEditingSchedules:
    def test_run(self, drawing):
        drawing.disable_editing_schedules().should_be_called()
        subject.disable_editing_schedules(drawing)


class TestAddSchedule:
    def test_run(self, ifc, drawing):
        ifc.run("document.add_information").should_be_called().will_return("schedule")
        ifc.run("document.add_reference", information="schedule").should_be_called().will_return("reference")
        ifc.get_schema().should_be_called().will_return("IFC4")
        ifc.run(
            "document.edit_information",
            information="schedule",
            attributes={"Identification": "X", "Name": "UNTITLED", "Scope": "SCHEDULE", "Location": "uri"},
        ).should_be_called()
        drawing.import_schedules().should_be_called()
        subject.add_schedule(ifc, drawing, uri="uri")

    def test_using_a_document_id_in_ifc2x3(self, ifc, drawing):
        ifc.run("document.add_information").should_be_called().will_return("schedule")
        ifc.run("document.add_reference", information="schedule").should_be_called().will_return("reference")
        ifc.get_schema().should_be_called().will_return("IFC2X3")
        ifc.run(
            "document.edit_information",
            information="schedule",
            attributes={"DocumentId": "X", "Name": "UNTITLED", "Scope": "SCHEDULE"},
        ).should_be_called()
        ifc.run("document.edit_reference", reference="reference", attributes={"Location": "uri"}).should_be_called()
        drawing.import_schedules().should_be_called()
        subject.add_schedule(ifc, drawing, uri="uri")


class TestRemoveSchedule:
    def test_run(self, ifc, drawing):
        ifc.run("document.remove_information", information="schedule").should_be_called()
        drawing.import_schedules().should_be_called()
        subject.remove_schedule(ifc, drawing, schedule="schedule")


class TestOpenSchedule:
    def test_run(self, drawing):
        drawing.get_schedule_location("schedule").should_be_called().will_return("uri")
        drawing.open_spreadsheet("uri").should_be_called()
        subject.open_schedule(drawing, schedule="schedule")


class TestUpdateScheduleName:
    def test_do_not_update_if_name_unchanged(self, ifc, drawing):
        drawing.get_name("schedule").should_be_called().will_return("name")
        subject.update_schedule_name(ifc, drawing, schedule="schedule", name="name")

    def test_run(self, ifc, drawing):
        drawing.get_name("schedule").should_be_called().will_return("oldname")
        ifc.run("document.edit_information", information="schedule", attributes={"Name": "name"}).should_be_called()
        subject.update_schedule_name(ifc, drawing, schedule="schedule", name="name")


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
        drawing.create_camera("name", "matrix").should_be_called().will_return("obj")
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
            },
        ).should_be_called()
        drawing.import_drawings().should_be_called()
        subject.add_drawing(ifc, collector, drawing, target_view="target_view", location_hint="location_hint")


class TestRemoveDrawing:
    def test_run(self, ifc, drawing):
        drawing.get_drawing_collection("drawing").should_be_called().will_return("collection")
        drawing.get_drawing_group("drawing").should_be_called().will_return("group")
        drawing.get_group_elements("group").should_be_called().will_return("elements")
        drawing.delete_drawing_elements("elements").should_be_called()
        ifc.run("group.remove_group", group="group").should_be_called()
        drawing.delete_collection("collection").should_be_called()
        ifc.run("root.remove_product", product="drawing").should_be_called()
        drawing.import_drawings().should_be_called()
        subject.remove_drawing(ifc, drawing, drawing="drawing")


class TestUpdateDrawingName:
    def test_do_not_update_if_name_unchanged(self, ifc, drawing):
        drawing.get_name("drawing").should_be_called().will_return("name")
        drawing.get_drawing_group("drawing").should_be_called().will_return("group")
        drawing.get_name("group").should_be_called().will_return("name")
        drawing.get_drawing_collection("drawing").should_be_called().will_return("collection")
        drawing.set_drawing_collection_name("group", "collection").should_be_called()
        subject.update_drawing_name(ifc, drawing, drawing="drawing", name="name")

    def test_run(self, ifc, drawing):
        drawing.get_name("drawing").should_be_called().will_return("oldname")
        ifc.run("attribute.edit_attributes", product="drawing", attributes={"Name": "name"}).should_be_called()
        drawing.get_drawing_group("drawing").should_be_called().will_return("group")
        drawing.get_name("group").should_be_called().will_return("oldname")
        ifc.run("attribute.edit_attributes", product="group", attributes={"Name": "name"}).should_be_called()
        drawing.get_drawing_collection("drawing").should_be_called().will_return("collection")
        drawing.set_drawing_collection_name("group", "collection").should_be_called()
        subject.update_drawing_name(ifc, drawing, drawing="drawing", name="name")


class TestAddAnnotation:
    def test_run(self, ifc, collector, drawing):
        drawing.show_decorations().should_be_called()
        drawing.get_drawing_target_view("drawing").should_be_called().will_return("target_view")
        drawing.get_annotation_context("target_view").should_be_called().will_return("context")
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

    def test_do_not_add_without_an_annotation_context(self, ifc, collector, drawing):
        drawing.get_drawing_target_view("drawing").should_be_called().will_return("target_view")
        drawing.get_annotation_context("target_view").should_be_called().will_return(None)
        subject.add_annotation(ifc, collector, drawing, drawing="drawing", object_type="object_type")
