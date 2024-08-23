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

import bonsai.core.brick as subject
from test.core.bootstrap import ifc, brick


class TestLoadBrickProject:
    def test_run(self, brick):
        brick.load_brick_file("filepath").should_be_called()
        brick.import_brick_classes("brick_root").should_be_called()
        brick.import_brick_classes("brick_root", split_screen=True).should_be_called()
        brick.set_active_brick_class("brick_root").should_be_called()
        brick.set_active_brick_class("brick_root", split_screen=True).should_be_called()
        subject.load_brick_project(brick, filepath="filepath", brick_root="brick_root")


class TestNewBrickFile:
    def test_run(self, brick):
        brick.new_brick_file().should_be_called()
        brick.import_brick_classes("brick_root").should_be_called()
        brick.import_brick_classes("brick_root", split_screen=True).should_be_called()
        brick.set_active_brick_class("brick_root").should_be_called()
        brick.set_active_brick_class("brick_root", split_screen=True).should_be_called()
        subject.new_brick_file(brick, brick_root="brick_root")


class TestViewBrickClass:
    def test_run(self, brick):
        brick.add_brick_breadcrumb(split_screen=False).should_be_called()
        brick.clear_brick_browser(split_screen=False).should_be_called()
        brick.import_brick_classes("brick_class", split_screen=False).should_be_called()
        brick.import_brick_items("brick_class", split_screen=False).should_be_called()
        brick.set_active_brick_class("brick_class", split_screen=False).should_be_called()
        subject.view_brick_class(brick, brick_class="brick_class", split_screen=False)

    def test_split_screen(self, brick):
        brick.add_brick_breadcrumb(split_screen=True).should_be_called()
        brick.clear_brick_browser(split_screen=True).should_be_called()
        brick.import_brick_classes("brick_class", split_screen=True).should_be_called()
        brick.import_brick_items("brick_class", split_screen=True).should_be_called()
        brick.set_active_brick_class("brick_class", split_screen=True).should_be_called()
        subject.view_brick_class(brick, brick_class="brick_class", split_screen=True)


class TestViewBrickItem:
    def test_run(self, brick):
        brick.get_item_class("item").should_be_called().will_return("brick_class")
        brick.run_view_brick_class(brick_class="brick_class", split_screen=False).should_be_called()
        brick.select_browser_item("item", split_screen=False).should_be_called()
        subject.view_brick_item(brick, item="item", split_screen=False)

    def test_split_screen(self, brick):
        brick.get_item_class("item").should_be_called().will_return("brick_class")
        brick.run_view_brick_class(brick_class="brick_class", split_screen=True).should_be_called()
        brick.select_browser_item("item", split_screen=True).should_be_called()
        subject.view_brick_item(brick, item="item", split_screen=True)


class TestRewindBrickClass:
    def test_run(self, brick):
        brick.pop_brick_breadcrumb(split_screen=False).should_be_called().will_return("previous_class")
        brick.clear_brick_browser(split_screen=False).should_be_called()
        brick.import_brick_classes("previous_class", split_screen=False).should_be_called()
        brick.import_brick_items("previous_class", split_screen=False).should_be_called()
        brick.set_active_brick_class("previous_class", split_screen=False).should_be_called()
        subject.rewind_brick_class(brick, split_screen=False)

    def test_split_screen(self, brick):
        brick.pop_brick_breadcrumb(split_screen=True).should_be_called().will_return("previous_class")
        brick.clear_brick_browser(split_screen=True).should_be_called()
        brick.import_brick_classes("previous_class", split_screen=True).should_be_called()
        brick.import_brick_items("previous_class", split_screen=True).should_be_called()
        brick.set_active_brick_class("previous_class", split_screen=True).should_be_called()
        subject.rewind_brick_class(brick, split_screen=True)


class TestCloseBrickProject:
    def test_run(self, brick):
        brick.clear_project().should_be_called()
        brick.clear_brick_browser().should_be_called()
        brick.clear_brick_browser(split_screen=True).should_be_called()
        brick.clear_breadcrumbs().should_be_called()
        brick.clear_breadcrumbs(split_screen=True).should_be_called()
        subject.close_brick_project(brick)


class TestConvertBrickProject:
    def test_run(self, ifc, brick):
        brick.get_brick_path_name().should_be_called().will_return("foo.ttl")
        ifc.run("library.add_library", name="foo.ttl").should_be_called().will_return("library")
        ifc.get_schema().should_be_called().will_return("IFC4")
        brick.get_brick_path().should_be_called().will_return("/path/to/foo.ttl")
        ifc.run(
            "library.edit_library", library="library", attributes={"Location": "/path/to/foo.ttl"}
        ).should_be_called()
        subject.convert_brick_project(ifc, brick)

    def test_not_editing_in_ifc2x3(self, ifc, brick):
        brick.get_brick_path_name().should_be_called().will_return("foo.ttl")
        ifc.run("library.add_library", name="foo.ttl").should_be_called().will_return("library")
        ifc.get_schema().should_be_called().will_return("IFC2X3")
        subject.convert_brick_project(ifc, brick)


class TestAssignBrickReference:
    def test_assigning_to_a_new_reference(self, ifc, brick):
        brick.get_library_brick_reference("library", "brick_uri").should_be_called().will_return(None)
        ifc.run("library.add_reference", library="library").should_be_called().will_return("reference")
        brick.export_brick_attributes("brick_uri").should_be_called().will_return("attributes")
        ifc.run("library.edit_reference", reference="reference", attributes="attributes").should_be_called()
        ifc.run("library.assign_reference", products=["element"], reference="reference").should_be_called()
        brick.get_brickifc_project().should_be_called().will_return("project")
        brick.add_brickifc_reference("brick_uri", "element", "project").should_be_called()
        subject.assign_brick_reference(ifc, brick, element="element", library="library", brick_uri="brick_uri")

    def test_assigning_to_an_existing_reference(self, ifc, brick):
        brick.get_library_brick_reference("library", "brick_uri").should_be_called().will_return("reference")
        ifc.run("library.assign_reference", products=["element"], reference="reference").should_be_called()
        brick.get_brickifc_project().should_be_called().will_return("project")
        brick.add_brickifc_reference("brick_uri", "element", "project").should_be_called()
        subject.assign_brick_reference(ifc, brick, element="element", library="library", brick_uri="brick_uri")

    def test_adding_a_brickifc_project_if_it_doesnt_exist(self, ifc, brick):
        brick.get_library_brick_reference("library", "brick_uri").should_be_called().will_return("reference")
        ifc.run("library.assign_reference", products=["element"], reference="reference").should_be_called()
        brick.get_brickifc_project().should_be_called().will_return(None)
        brick.get_namespace("brick_uri").should_be_called().will_return("namespace")
        brick.add_brickifc_project("namespace").should_be_called().will_return("project")
        brick.add_brickifc_reference("brick_uri", "element", "project").should_be_called()
        subject.assign_brick_reference(ifc, brick, element="element", library="library", brick_uri="brick_uri")


class TestAddBrick:
    def test_adding_a_brick_from_an_element(self, ifc, brick):
        brick.add_brick_from_element("element", "namespace", "brick_class").should_be_called().will_return("brick_uri")
        brick.run_refresh_brick_viewer().should_be_called()
        subject.add_brick(
            ifc, brick, element="element", namespace="namespace", brick_class="brick_class", library=None, label="label"
        )

    def test_adding_a_brick_and_auto_assigning_it_to_the_ifc_element(self, ifc, brick):
        brick.add_brick_from_element("element", "namespace", "brick_class").should_be_called().will_return("brick_uri")
        brick.run_assign_brick_reference(element="element", library="library", brick_uri="brick_uri").should_be_called()
        brick.run_refresh_brick_viewer().should_be_called()
        subject.add_brick(
            ifc,
            brick,
            element="element",
            namespace="namespace",
            brick_class="brick_class",
            library="library",
            label="label",
        )

    def test_adding_a_plain_brick(self, ifc, brick):
        brick.add_brick("namespace", "brick_class", "label").should_be_called()
        brick.run_refresh_brick_viewer().should_be_called()
        subject.add_brick(
            ifc, brick, element=None, namespace="namespace", brick_class="brick_class", library=None, label="label"
        )


class TestAddBrickRelation:
    def test_run(self, ifc, brick):
        brick.add_relation("brick_uri", "predicate", "object").should_be_called()
        brick.run_refresh_brick_viewer().should_be_called()
        subject.add_brick_relation(brick, brick_uri="brick_uri", predicate="predicate", object="object")


class TestConvertIfcToBrick:
    def test_run(self, brick):
        brick.get_convertable_brick_spaces().should_be_called().will_return({"space", "parent"})
        brick.get_brick_class("space").should_be_called().will_return("space_class")
        brick.add_brick_from_element("space", "namespace", "space_class").should_be_called().will_return("space_uri")
        brick.run_assign_brick_reference(element="space", library="library", brick_uri="space_uri").should_be_called()

        brick.get_brick_class("parent").should_be_called().will_return("parent_class")
        brick.add_brick_from_element("parent", "namespace", "parent_class").should_be_called().will_return("parent_uri")
        brick.run_assign_brick_reference(element="parent", library="library", brick_uri="parent_uri").should_be_called()

        brick.get_parent_space("space").should_be_called().will_return("parent")
        brick.get_parent_space("parent").should_be_called().will_return(None)
        brick.add_relation("parent_uri", "https://brickschema.org/schema/Brick#hasPart", "space_uri").should_be_called()

        brick.get_convertable_brick_systems().should_be_called().will_return({"system"})
        brick.get_brick_class("system").should_be_called().will_return("system_class")
        brick.add_brick_from_element("system", "namespace", "system_class").should_be_called().will_return("system_uri")
        brick.run_assign_brick_reference(element="system", library="library", brick_uri="system_uri").should_be_called()

        brick.get_convertable_brick_elements().should_be_called().will_return({"element", "downstream_element"})
        brick.get_brick_class("element").should_be_called().will_return("element_class")
        brick.add_brick_from_element("element", "namespace", "element_class").should_be_called().will_return(
            "element_uri"
        )
        brick.get_element_container("element").should_be_called().will_return("space")
        brick.add_relation(
            "element_uri", "https://brickschema.org/schema/Brick#hasLocation", "space_uri"
        ).should_be_called()
        brick.get_element_systems("element").should_be_called().will_return(["system"])
        brick.add_relation(
            "system_uri", "https://brickschema.org/schema/Brick#hasPart", "element_uri"
        ).should_be_called()
        brick.run_assign_brick_reference(
            element="element", library="library", brick_uri="element_uri"
        ).should_be_called()

        brick.get_brick_class("downstream_element").should_be_called().will_return("downstream_element_class")
        brick.add_brick_from_element(
            "downstream_element", "namespace", "downstream_element_class"
        ).should_be_called().will_return("downstream_element_uri")
        brick.get_element_container("downstream_element").should_be_called().will_return("space")
        brick.add_relation(
            "downstream_element_uri", "https://brickschema.org/schema/Brick#hasLocation", "space_uri"
        ).should_be_called()
        brick.get_element_systems("downstream_element").should_be_called().will_return(["system"])
        brick.add_relation(
            "system_uri", "https://brickschema.org/schema/Brick#hasPart", "downstream_element_uri"
        ).should_be_called()
        brick.run_assign_brick_reference(
            element="downstream_element", library="library", brick_uri="downstream_element_uri"
        ).should_be_called()

        brick.get_element_feeds("element").should_be_called().will_return(["downstream_element"])
        brick.get_element_feeds("downstream_element").should_be_called().will_return([])
        brick.add_relation(
            "element_uri", "https://brickschema.org/schema/Brick#feeds", "downstream_element_uri"
        ).should_be_called()
        brick.run_refresh_brick_viewer().should_be_called()
        subject.convert_ifc_to_brick(brick, namespace="namespace", library="library")


class TestRefreshBrickViewer:
    def test_run(self, brick):
        brick.get_active_brick_class().should_be_called().will_return("brick_class")
        brick.run_view_brick_class(brick_class="brick_class").should_be_called()
        brick.pop_brick_breadcrumb().should_be_called()
        brick.get_active_brick_class(split_screen=True).should_be_called().will_return("brick_class")
        brick.run_view_brick_class(brick_class="brick_class", split_screen=True).should_be_called()
        brick.pop_brick_breadcrumb(split_screen=True).should_be_called()
        subject.refresh_brick_viewer(brick)


class TestRemoveBrick:
    def test_run(self, ifc, brick):
        brick.get_library_brick_reference("library", "brick_uri").should_be_called().will_return("reference")
        ifc.run("library.remove_reference", reference="reference").should_be_called()
        brick.remove_brick("brick_uri").should_be_called()
        brick.run_refresh_brick_viewer().should_be_called()
        subject.remove_brick(ifc, brick, library="library", brick_uri="brick_uri")

    def test_do_not_remove_reference_if_no_reference_exists(self, ifc, brick):
        brick.get_library_brick_reference("library", "brick_uri").should_be_called().will_return(None)
        brick.remove_brick("brick_uri").should_be_called()
        brick.run_refresh_brick_viewer().should_be_called()
        subject.remove_brick(ifc, brick, library="library", brick_uri="brick_uri")

    def test_do_not_check_references_if_no_library_specified(self, ifc, brick):
        brick.remove_brick("brick_uri").should_be_called()
        brick.run_refresh_brick_viewer().should_be_called()
        subject.remove_brick(ifc, brick, library=None, brick_uri="brick_uri")


class TestSerializeBrick:
    def test_run(self, brick):
        brick.serialize_brick().should_be_called()
        subject.serialize_brick(brick)


class TestAddBrickNamespace:
    def test_run(self, brick):
        brick.add_namespace("alias", "uri").should_be_called()
        subject.add_brick_namespace(brick, alias="alias", uri="uri")


class TestSetBrickListRoot:
    def test_run(self, brick):
        brick.run_view_brick_class(brick_class="brick_root", split_screen=False).should_be_called()
        brick.clear_breadcrumbs(split_screen=False).should_be_called()
        subject.set_brick_list_root(brick, brick_root="brick_root", split_screen=False)

    def test_split_screen(self, brick):
        brick.run_view_brick_class(brick_class="brick_root", split_screen=True).should_be_called()
        brick.clear_breadcrumbs(split_screen=True).should_be_called()
        subject.set_brick_list_root(brick, brick_root="brick_root", split_screen=True)


class TestRemoveBrickRelation:
    def test_run(self, brick):
        brick.remove_relation("brick_uri", "predicate", "object").should_be_called()
        subject.remove_brick_relation(brick, brick_uri="brick_uri", predicate="predicate", object="object")
