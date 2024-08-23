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


def load_brick_project(brick, filepath=None, brick_root=None):
    brick.load_brick_file(filepath)
    brick.import_brick_classes(brick_root)
    brick.import_brick_classes(brick_root, split_screen=True)
    brick.set_active_brick_class(brick_root)
    brick.set_active_brick_class(brick_root, split_screen=True)


def new_brick_file(brick, brick_root=None):
    brick.new_brick_file()
    brick.import_brick_classes(brick_root)
    brick.import_brick_classes(brick_root, split_screen=True)
    brick.set_active_brick_class(brick_root)
    brick.set_active_brick_class(brick_root, split_screen=True)


def view_brick_class(brick, brick_class=None, split_screen=False):
    brick.add_brick_breadcrumb(split_screen=split_screen)
    brick.clear_brick_browser(split_screen=split_screen)
    brick.import_brick_classes(brick_class, split_screen=split_screen)
    brick.import_brick_items(brick_class, split_screen=split_screen)
    brick.set_active_brick_class(brick_class, split_screen=split_screen)


def view_brick_item(brick, item=None, split_screen=False):
    brick_class = brick.get_item_class(item)
    brick.run_view_brick_class(brick_class=brick_class, split_screen=split_screen)
    brick.select_browser_item(item, split_screen=split_screen)


def rewind_brick_class(brick, split_screen=False):
    previous_class = brick.pop_brick_breadcrumb(split_screen=split_screen)
    brick.clear_brick_browser(split_screen=split_screen)
    brick.import_brick_classes(previous_class, split_screen=split_screen)
    brick.import_brick_items(previous_class, split_screen=split_screen)
    brick.set_active_brick_class(previous_class, split_screen=split_screen)


def close_brick_project(brick):
    brick.clear_project()
    brick.clear_brick_browser()
    brick.clear_brick_browser(split_screen=True)
    brick.clear_breadcrumbs()
    brick.clear_breadcrumbs(split_screen=True)


def convert_brick_project(ifc, brick):
    library = ifc.run("library.add_library", name=brick.get_brick_path_name())
    if ifc.get_schema() != "IFC2X3":
        ifc.run("library.edit_library", library=library, attributes={"Location": brick.get_brick_path()})


def assign_brick_reference(ifc, brick, element=None, library=None, brick_uri=None):
    reference = brick.get_library_brick_reference(library, brick_uri)
    if not reference:
        reference = ifc.run("library.add_reference", library=library)
        ifc.run("library.edit_reference", reference=reference, attributes=brick.export_brick_attributes(brick_uri))
    ifc.run("library.assign_reference", products=[element], reference=reference)
    project = brick.get_brickifc_project()
    if not project:
        project = brick.add_brickifc_project(brick.get_namespace(brick_uri))
    brick.add_brickifc_reference(brick_uri, element, project)


def add_brick(ifc, brick, element=None, namespace=None, brick_class=None, library=None, label="Unnamed"):
    if element:
        brick_uri = brick.add_brick_from_element(element, namespace, brick_class)
        if library:
            brick.run_assign_brick_reference(element=element, library=library, brick_uri=brick_uri)
    else:
        brick.add_brick(namespace, brick_class, label)
    brick.run_refresh_brick_viewer()


def add_brick_relation(brick, brick_uri=None, predicate=None, object=None):
    brick.add_relation(brick_uri, predicate, object)
    brick.run_refresh_brick_viewer()


def convert_ifc_to_brick(brick, namespace=None, library=None):
    # convert spaces to brick
    spaces = brick.get_convertable_brick_spaces()
    space_uris = {}
    for space in spaces:
        brick_uri = brick.add_brick_from_element(space, namespace, brick.get_brick_class(space))
        space_uris[space] = brick_uri
        if library:
            brick.run_assign_brick_reference(element=space, library=library, brick_uri=brick_uri)
    for space in spaces:
        parent = brick.get_parent_space(space)
        if parent:
            brick.add_relation(space_uris[parent], "https://brickschema.org/schema/Brick#hasPart", space_uris[space])
    # convert systems to brick
    systems = brick.get_convertable_brick_systems()
    system_uris = {}
    for system in systems:
        brick_uri = brick.add_brick_from_element(system, namespace, brick.get_brick_class(system))
        system_uris[system] = brick_uri
        if library:
            brick.run_assign_brick_reference(element=system, library=library, brick_uri=brick_uri)
    # convert services to brick
    distribution_elements = brick.get_convertable_brick_elements()
    equipment_uris = {}
    for element in distribution_elements:
        brick_uri = brick.add_brick_from_element(element, namespace, brick.get_brick_class(element))
        equipment_uris[element] = brick_uri
        space = brick.get_element_container(element)
        brick.add_relation(brick_uri, "https://brickschema.org/schema/Brick#hasLocation", space_uris[space])
        systems = brick.get_element_systems(element)
        for system in systems:
            brick.add_relation(system_uris[system], "https://brickschema.org/schema/Brick#hasPart", brick_uri)
        if library:
            brick.run_assign_brick_reference(element=element, library=library, brick_uri=brick_uri)
    for element in distribution_elements:
        feeds = brick.get_element_feeds(element)
        for downstream_equipment in feeds:
            brick.add_relation(
                equipment_uris[element],
                "https://brickschema.org/schema/Brick#feeds",
                equipment_uris[downstream_equipment],
            )
    brick.run_refresh_brick_viewer()


def refresh_brick_viewer(brick):
    brick.run_view_brick_class(brick_class=brick.get_active_brick_class())
    brick.pop_brick_breadcrumb()
    brick.run_view_brick_class(brick_class=brick.get_active_brick_class(split_screen=True), split_screen=True)
    brick.pop_brick_breadcrumb(split_screen=True)


def remove_brick(ifc, brick, library=None, brick_uri=None):
    if library:
        reference = brick.get_library_brick_reference(library, brick_uri)
        if reference:
            ifc.run("library.remove_reference", reference=reference)
    brick.remove_brick(brick_uri)
    brick.run_refresh_brick_viewer()


def serialize_brick(brick):
    brick.serialize_brick()


def add_brick_namespace(brick, alias=None, uri=None):
    brick.add_namespace(alias, uri)


def set_brick_list_root(brick, brick_root=None, split_screen=False):
    brick.run_view_brick_class(brick_class=brick_root, split_screen=split_screen)
    brick.clear_breadcrumbs(split_screen=split_screen)


def remove_brick_relation(brick, brick_uri=None, predicate=None, object=None):
    brick.remove_relation(brick_uri, predicate, object)
