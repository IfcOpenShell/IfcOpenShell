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


def copy_to_container(ifc, spatial, obj=None, containers=None):
    element = ifc.get_entity(obj)
    if not element:
        return
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
    if not element:
        return
    for subelement in spatial.get_decomposed_elements(spatial.get_container(element)):
        obj = ifc.get_object(subelement)
        if obj:
            spatial.select_object(obj)
