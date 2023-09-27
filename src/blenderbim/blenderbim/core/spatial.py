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

import blenderbim.core
import bpy


def reference_structure(ifc, spatial, structure=None, element=None):
    if spatial.can_reference(structure, element):
        return ifc.run("spatial.reference_structure", product=element, relating_structure=structure)


def dereference_structure(ifc, spatial, structure=None, element=None):
    if spatial.can_reference(structure, element):
        return ifc.run("spatial.dereference_structure", product=element, relating_structure=structure)


def assign_container(ifc, collector, spatial, structure_obj=None, element_obj=None):
    if not spatial.can_contain(structure_obj, element_obj):
        return
    rel = ifc.run(
        "spatial.assign_container",
        product=ifc.get_entity(element_obj),
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
    ifc.run("spatial.remove_container", product=ifc.get_entity(obj))
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

#HERE STARTS SPATIAL TOOL

def generate_spaces_from_walls(ifc, spatial, collector):
    active_obj = bpy.context.active_object
    element = ifc.get_entity(active_obj)
    container = spatial.get_container(element)

    if not active_obj:
        self.report({"ERROR"}, "No active object. Please select a wall")
        return

    element = ifc.get_entity(active_obj)
    if element and not element.is_a("IfcWall"):
        return self.report({"ERROR"}, "The active object is not a wall. Please select a wall.")

    if not container:
        self.report({"ERROR"}, "The wall is not contained.")

    if not bpy.context.selected_objects:
        self.report({"ERROR"}, "No selected objects found. Please select walls.")
        return

    x, y, z = active_obj.matrix_world.translation.xyz
    mat = active_obj.matrix_world
    h = active_obj.dimensions.z
    selected_objects = bpy.context.selected_objects

    union = spatial.get_union_shape_from_selected_objects()

    for i, linear_ring in enumerate(union.interiors):
        poly = spatial.get_buffered_poly_from_linear_ring(linear_ring)

        bm = spatial.get_bmesh_from_polygon(poly, h)

        name = "Space" + str(i)
        mesh = bpy.data.meshes.new(name=name)
        bm.to_mesh(mesh)
        bm.free()

        obj = bpy.data.objects.new(name, mesh)
        obj.matrix_world = mat

        spatial.set_obj_origin_to_bboxcenter(obj)

        if z != 0:
            obj.location = obj.location + Vector((0, 0, z))

        bpy.context.view_layer.active_layer_collection.collection.objects.link(obj)
        bpy.ops.bim.assign_class(obj=obj.name, ifc_class="IfcSpace")
        container_obj = ifc.get_object(container)
        blenderbim.core.spatial.assign_container(
            ifc, collector, spatial, structure_obj=container_obj, element_obj=obj
        )

def toggle_space_visibility(ifc, spatial):
    model = ifc.get()
    spaces = model.by_type("IfcSpace")
    if not spaces:
        return
    spatial.toggle_spaces_visibility_wired_and_textured(spaces)

