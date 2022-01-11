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


def convert_brick_project(ifc, brick):
    library = ifc.run("library.add_library", name=brick.get_brick_path_name())
    if ifc.get_schema() != "IFC2X3":
        ifc.run("library.edit_library", library=library, attributes={"Location": brick.get_brick_path()})


def assign_brick_reference(ifc, brick, obj=None, library=None, brick_uri=None):
    reference = brick.get_library_brick_reference(library, brick_uri)
    if not reference:
        reference = ifc.run("library.add_reference", library=library)
        ifc.run("library.edit_reference", reference=reference, attributes=brick.export_brick_attributes(brick_uri))
    product = ifc.get_entity(obj)
    ifc.run("library.assign_reference", product=product, reference=reference)
    project = brick.get_brickifc_project()
    if not project:
        project = brick.add_brickifc_project(brick.get_namespace(brick_uri))
    brick.add_brickifc_reference(brick_uri, product, project)


def add_brick(ifc, brick, obj=None, namespace=None, brick_class=None, library=None):
    product = ifc.get_entity(obj)
    brick_uri = brick.add_brick(product, namespace, brick_class)
    if library:
        brick.run_assign_brick_reference(obj=obj, library=library, brick_uri=brick_uri)


def add_brick_feed(ifc, brick, source=None, destination=None):
    source_element = ifc.get_entity(source)
    destination_element = ifc.get_entity(destination)
    brick.add_feed(brick.get_brick(source_element), brick.get_brick(destination_element))


def convert_ifc_to_brick(brick, namespace=None, library=None):
    for obj, element in brick.get_convertable_brick_objects_and_elements():
        brick_class = brick.get_brick_class(element)
        if not brick_class:
            continue
        brick.run_add_brick(obj=obj, namespace=namespace, brick_class=brick_class, library=library)


def new_brick_file(brick):
    brick.new_brick_file()
