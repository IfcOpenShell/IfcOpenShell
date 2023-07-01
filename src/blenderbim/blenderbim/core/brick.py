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


def load_brick_project(brick, filepath=None):
    brick.load_brick_file(filepath)
    brick.import_brick_classes("Class")
    brick.set_active_brick_class("Class")


def view_brick_class(brick, brick_class=None):
    brick.add_brick_breadcrumb()
    brick.clear_brick_browser()
    brick.import_brick_classes(brick_class)
    brick.import_brick_items(brick_class)
    brick.set_active_brick_class(brick_class)


def view_brick_item(brick, item=None):
    brick_class = brick.get_item_class(item)
    view_brick_class(brick, brick_class=brick_class)
    brick.select_browser_item(item)


def rewind_brick_class(brick):
    previous_class = brick.pop_brick_breadcrumb()
    brick.clear_brick_browser()
    brick.import_brick_classes(previous_class)
    brick.import_brick_items(previous_class)
    brick.set_active_brick_class(previous_class)


def close_brick_project(brick):
    brick.clear_project()
    brick.clear_brick_browser()


def convert_brick_project(ifc, brick):
    library = ifc.run("library.add_library", name=brick.get_brick_path_name())
    if ifc.get_schema() != "IFC2X3":
        ifc.run("library.edit_library", library=library, attributes={"Location": brick.get_brick_path()})


def assign_brick_reference(ifc, brick, element=None, library=None, brick_uri=None):
    reference = brick.get_library_brick_reference(library, brick_uri)
    if not reference:
        reference = ifc.run("library.add_reference", library=library)
        ifc.run("library.edit_reference", reference=reference, attributes=brick.export_brick_attributes(brick_uri))
    ifc.run("library.assign_reference", product=element, reference=reference)
    project = brick.get_brickifc_project()
    if not project:
        project = brick.add_brickifc_project(brick.get_namespace(brick_uri))
    brick.add_brickifc_reference(brick_uri, element, project)


def add_brick(ifc, brick, element=None, namespace=None, brick_class=None, library=None):
    if element:
        brick_uri = brick.add_brick_from_element(element, namespace, brick_class)
        if library:
            brick.run_assign_brick_reference(element=element, library=library, brick_uri=brick_uri)
    else:
        brick_uri = brick.add_brick(namespace, brick_class)
    brick.run_refresh_brick_viewer()


def add_brick_feed(ifc, brick, source=None, destination=None):
    brick.add_feed(brick.get_brick(source), brick.get_brick(destination))
    brick.run_refresh_brick_viewer()


def convert_ifc_to_brick(brick, namespace=None, library=None):
    distribution_elements = brick.get_convertable_brick_elements()
    for element in distribution_elements:
        brick_uri = brick.add_brick_from_element(element, namespace, brick.get_brick_class(element))
        if library:
            brick.run_assign_brick_reference(element=element, library=library, brick_uri=brick_uri)
    brick.run_refresh_brick_viewer()


def new_brick_file(brick):
    brick.new_brick_file()
    brick.import_brick_classes("Class")
    brick.set_active_brick_class("Class")


def refresh_brick_viewer(brick):
    brick.run_view_brick_class(brick_class=brick.get_active_brick_class())
    brick.pop_brick_breadcrumb()


def remove_brick(ifc, brick, library=None, brick_uri=None):
    if library:
        reference = brick.get_library_brick_reference(library, brick_uri)
        if reference:
            ifc.run("library.remove_reference", reference=reference)
    brick.remove_brick(brick_uri)
    brick.run_refresh_brick_viewer()


def undo_brick(brick):
    brick.undo_brick()
    brick.run_refresh_brick_viewer()


def redo_brick(brick):
    brick.redo_brick()
    brick.run_refresh_brick_viewer()


def serialize_brick(brick):
    brick.serialize_brick()