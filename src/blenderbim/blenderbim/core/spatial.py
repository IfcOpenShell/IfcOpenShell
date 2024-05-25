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

from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Union

if TYPE_CHECKING:
    import bpy
    import ifcopenshell
    import blenderbim.tool as tool


def reference_structure(
    ifc: tool.Ifc,
    spatial: tool.Spatial,
    structure: Optional[ifcopenshell.entity_instance] = None,
    element: Optional[ifcopenshell.entity_instance] = None,
) -> Union[ifcopenshell.entity_instance, None]:
    if spatial.can_reference(structure, element):
        return ifc.run("spatial.reference_structure", products=[element], relating_structure=structure)


def dereference_structure(
    ifc: tool.Ifc,
    spatial: tool.Spatial,
    structure: Optional[ifcopenshell.entity_instance] = None,
    element: Optional[ifcopenshell.entity_instance] = None,
) -> None:
    if spatial.can_reference(structure, element):
        return ifc.run("spatial.dereference_structure", products=[element], relating_structure=structure)


def assign_container(
    ifc: tool.Ifc,
    collector: tool.Collector,
    spatial: tool.Spatial,
    structure_obj: Optional[bpy.types.Object] = None,
    element_obj: Optional[bpy.types.Object] = None,
) -> Union[ifcopenshell.entity_instance, None]:
    if not spatial.can_contain(structure_obj, element_obj):
        return
    rel = ifc.run(
        "spatial.assign_container",
        products=[ifc.get_entity(element_obj)],
        relating_structure=ifc.get_entity(structure_obj),
    )
    spatial.disable_editing(element_obj)
    collector.assign(element_obj)
    return rel


def enable_editing_container(spatial, obj=None):
    spatial.enable_editing(obj)
    spatial.import_containers()


def disable_editing_container(spatial, obj=None):
    spatial.disable_editing(obj)


def change_spatial_level(spatial, parent=None):
    spatial.import_containers(parent=parent)


def remove_container(ifc, collector, obj=None):
    ifc.run("spatial.unassign_container", products=[ifc.get_entity(obj)])
    collector.assign(obj)


def copy_to_container(ifc, collector, spatial, obj=None, containers=None):
    element = ifc.get_entity(obj)
    if not element:
        return
    collector.sync(obj)
    from_container = spatial.get_container(element)
    if from_container:
        matrix = spatial.get_relative_object_matrix(obj, ifc.get_object(from_container))
    else:
        matrix = spatial.get_object_matrix(obj)
    result_objs = []
    for to_container in containers:
        to_container_obj = ifc.get_object(to_container)
        copied_obj = spatial.duplicate_object_and_data(obj)
        spatial.set_relative_object_matrix(copied_obj, to_container_obj, matrix)
        result_objs.append(spatial.run_root_copy_class(obj=copied_obj))
        spatial.run_spatial_assign_container(structure_obj=to_container_obj, element_obj=copied_obj)
    spatial.disable_editing(obj)
    return result_objs


def select_container(ifc, spatial, obj=None):
    element = ifc.get_entity(obj)
    if not element:
        return
    spatial.set_active_object(ifc.get_object(spatial.get_container(element)))


def select_similar_container(ifc, spatial, obj=None):
    element = ifc.get_entity(obj)
    if element:
        spatial.select_products(spatial.get_decomposed_elements(spatial.get_container(element)))


def select_product(spatial, product):
    spatial.select_products([product])


def load_container_manager(spatial):
    spatial.load_container_manager()


def edit_container_attributes(spatial, entity=None):
    spatial.edit_container_attributes(entity)
    spatial.load_container_manager()


def contract_container(spatial, container=None):
    spatial.contract_container(container)
    spatial.load_container_manager()


def expand_container(spatial, container=None):
    spatial.expand_container(container)
    spatial.load_container_manager()


def delete_container(ifc, spatial, geometry, container=None):
    geometry.delete_ifc_object(ifc.get_object(container))
    spatial.load_container_manager()


def select_decomposed_elements(spatial):
    container = spatial.get_active_container()
    if container:
        spatial.select_products(spatial.get_decomposed_elements(container))


# HERE STARTS SPATIAL TOOL
def generate_space(ifc, spatial, model, Type):
    active_obj = spatial.get_active_obj()
    selected_objects = spatial.get_selected_objects()
    element = None
    relating_type_id = spatial.get_relating_type_id()

    relating_type = None
    if relating_type_id:
        relating_type = ifc.get().by_id(int(relating_type_id))
        if not relating_type.is_a("IfcSpaceType"):
            relating_type = None

    if selected_objects and active_obj:
        x, y, z, h, mat = spatial.get_x_y_z_h_mat_from_active_obj(active_obj)  ##mat
        element = ifc.get_entity(active_obj)

    else:
        x, y, z, h, mat = spatial.get_x_y_z_h_mat_from_cursor()  ##mat

    space_polygon = spatial.get_space_polygon_from_context_visible_objects(x, y)

    if not space_polygon:
        return

    bm = spatial.get_bmesh_from_polygon(space_polygon, h=h)  ##mat

    mesh = spatial.get_named_mesh_from_bmesh(name="Space", bmesh=bm)

    if element and element.is_a("IfcSpace"):
        mesh = spatial.get_transformed_mesh_from_local_to_global(mesh)
        spatial.edit_active_space_obj_from_mesh(mesh)
    else:
        if relating_type:
            name = model.generate_occurrence_name(relating_type, "IfcSpace")
        else:
            name = "Space"

        obj = spatial.get_named_obj_from_mesh(name, mesh)
        spatial.set_obj_origin_to_cursor_position_and_zero_elevation(obj)
        spatial.traslate_obj_to_z_location(obj, z)
        spatial.link_obj_to_active_collection(obj)
        spatial.assign_ifcspace_class_to_obj(obj)

        element = ifc.get_entity(obj)

        if relating_type:
            spatial.assign_relating_type_to_element(ifc, Type, element, relating_type)


def generate_spaces_from_walls(ifc, spatial, collector):
    z = spatial.get_active_obj_z()
    h = spatial.get_active_obj_height()

    union = spatial.get_union_shape_from_selected_objects()

    for i, linear_ring in enumerate(union.interiors):
        poly = spatial.get_buffered_poly_from_linear_ring(linear_ring)

        bm = spatial.get_bmesh_from_polygon(poly, h)

        name = "Space" + str(i)

        obj = spatial.get_named_obj_from_bmesh(name, bmesh=bm)

        spatial.set_obj_origin_to_bboxcenter_and_zero_elevation(obj)
        spatial.traslate_obj_to_z_location(obj, z)

        spatial.link_obj_to_active_collection(obj)
        spatial.assign_ifcspace_class_to_obj(obj)

        spatial.assign_container_to_obj(obj)


def toggle_space_visibility(ifc, spatial):
    model = ifc.get()
    spaces = model.by_type("IfcSpace")
    if not spaces:
        return
    spatial.toggle_spaces_visibility_wired_and_textured(spaces)


def toggle_hide_spaces(ifc, spatial):
    model = ifc.get()
    spaces = model.by_type("IfcSpace")
    if not spaces:
        return
    spatial.toggle_hide_spaces(spaces)
