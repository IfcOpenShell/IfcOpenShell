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

import blenderbim.core.style


def edit_object_placement(ifc, geometry, surveyor, obj=None):
    element = ifc.get_entity(obj)
    if not element:
        return
    geometry.clear_cache(element)
    geometry.clear_scale(obj)
    ifc.run("geometry.edit_object_placement", product=element, matrix=surveyor.get_absolute_matrix(obj))
    geometry.record_object_position(obj)


def add_representation(
    ifc, geometry, style, surveyor, obj=None, context=None, ifc_representation_class=None, profile_set_usage=None
):
    element = ifc.get_entity(obj)
    if not element:
        return

    edit_object_placement(ifc, geometry, surveyor, obj=obj)
    data = geometry.get_object_data(obj)

    if not data and ifc_representation_class != "IfcTextLiteral":
        return

    representation = ifc.run(
        "geometry.add_representation",
        context=context,
        blender_object=obj,
        geometry=data,
        coordinate_offset=geometry.get_cartesian_point_coordinate_offset(obj),
        total_items=geometry.get_total_representation_items(obj),
        should_force_faceted_brep=geometry.should_force_faceted_brep(),
        should_force_triangulation=geometry.should_force_triangulation(),
        should_generate_uvs=geometry.should_generate_uvs(obj),
        ifc_representation_class=ifc_representation_class,
        profile_set_usage=profile_set_usage,
    )

    if geometry.is_body_representation(representation):
        [geometry.run_style_add_style(obj=mat) for mat in geometry.get_object_materials_without_styles(obj)]
        ifc.run(
            "style.assign_representation_styles",
            shape_representation=representation,
            styles=geometry.get_styles(obj),
            should_use_presentation_style_assignment=geometry.should_use_presentation_style_assignment(),
        )
        geometry.record_object_materials(obj)

    ifc.run("geometry.assign_representation", product=element, representation=representation)

    if data:
        data = geometry.duplicate_object_data(obj)
        geometry.change_object_data(obj, data, is_global=True)
        name = geometry.get_representation_name(representation)
        geometry.rename_object(data, name)
        geometry.link(representation, data)

    return representation


def switch_representation(
    geometry,
    obj=None,
    representation=None,
    should_reload=True,
    is_global=True,
    should_sync_changes_first=False,
):
    if should_sync_changes_first and geometry.is_edited(obj) and not geometry.is_box_representation(representation):
        representation_id = geometry.get_representation_id(representation)
        geometry.run_geometry_update_representation(obj=obj)
        if not geometry.does_representation_id_exist(representation_id):
            return

    representation = geometry.resolve_mapped_representation(representation)
    existing_data = geometry.get_representation_data(representation)

    if should_reload or not existing_data:
        data = geometry.import_representation(obj, representation)
        geometry.rename_object(data, geometry.get_representation_name(representation))
        geometry.link(representation, data)
    else:
        data = existing_data

    geometry.change_object_data(obj, data, is_global=is_global)

    if should_reload and existing_data:
        geometry.delete_data(existing_data)

    geometry.clear_modifiers(obj)


def get_representation_ifc_parameters(geometry, obj=None, should_sync_changes_first=False):
    geometry.import_representation_parameters(geometry.get_object_data(obj))


def remove_representation(ifc, geometry, obj=None, representation=None):
    element = ifc.get_entity(obj)
    type = geometry.get_element_type(element)
    if type and (geometry.is_mapped_representation(representation) or geometry.is_type_product(element)):
        representation = geometry.resolve_mapped_representation(representation)
        data = geometry.get_representation_data(representation)
        if data and geometry.has_data_users(data):
            for element in geometry.get_elements_of_type(type):
                obj = ifc.get_object(element)
                if obj:
                    obj = geometry.replace_object_with_empty(obj)
            obj = ifc.get_object(type)
            if obj:
                obj = geometry.replace_object_with_empty(obj)
        ifc.run("geometry.unassign_representation", product=type, representation=representation)
        ifc.run("geometry.remove_representation", representation=representation)
    else:
        data = geometry.get_representation_data(representation)
        if data and geometry.has_data_users(data):
            geometry.replace_object_with_empty(obj)
        ifc.run("geometry.unassign_representation", product=element, representation=representation)
        ifc.run("geometry.remove_representation", representation=representation)


def select_connection(geometry, connection=None):
    geometry.select_connection(connection)


def remove_connection(geometry, connection=None):
    geometry.remove_connection(connection)
