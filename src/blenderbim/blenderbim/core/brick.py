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
    ifc.run("library.edit_library", library=library, attributes={"Location": brick.get_brick_path()})


def assign_brick_reference(ifc, brick, obj=None, library=None, brick_uri=None):
    reference = brick.get_library_brick_reference(library, brick_uri)
    if not reference:
        reference = ifc.run("library.add_reference", library=library)
        ifc.run("library.edit_reference", reference=reference, attributes=brick.export_brick_attributes(brick_uri))
    ifc.run("library.assign_reference", product=ifc.get_entity(obj), reference=reference)
