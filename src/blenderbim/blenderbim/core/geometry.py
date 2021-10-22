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


def edit_object_placement(ifc, surveyor, obj=None):
    element = ifc.get_entity(obj)
    if element:
        ifc.run("geometry.edit_object_placement", product=element, matrix=surveyor.get_absolute_matrix(obj))


def add_representation(
    ifc, geometry, style, surveyor, obj=None, context=None, ifc_representation_class=None, profile_set_usage=None
):
    element = ifc.get_entity(obj)
    if not element:
        return

    edit_object_placement(ifc, surveyor, obj=obj)
    data = geometry.get_object_data(obj)

    if not data:
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
        ifc_representation_class=ifc_representation_class,
        profile_set_usage=profile_set_usage,
    )

    if geometry.does_object_have_mesh_with_faces(obj):
        styles = [
            blenderbim.core.style.add_style(ifc, style, obj=material)
            for material in geometry.get_object_materials_without_styles(obj)
        ]
        ifc.run(
            "style.assign_representation_styles",
            shape_representation=representation,
            styles=styles,
            should_use_presentation_style_assignment=geometry.should_use_presentation_style_assignment(),
        )

    ifc.run("geometry.assign_representation", product=element, representation=representation)

    data = geometry.duplicate_object_data(obj)
    name = geometry.get_representation_name(representation)
    geometry.rename_object(data, name)
    geometry.link(representation, data)

    return representation


def switch_representation(
    geometry, obj=None, representation=None, should_reload=True, enable_dynamic_voids=True, is_global=True
):
    representation = geometry.resolve_mapped_representation(representation)
    data = geometry.get_representation_data(representation)

    if not data or should_reload:
        data = geometry.import_representation(obj, representation, enable_dynamic_voids=enable_dynamic_voids)
        geometry.rename_object(data, geometry.get_representation_name(representation))
        geometry.link(representation, data)

    geometry.change_object_data(obj, data, is_global=is_global)
    geometry.clear_modifiers(obj)

    if enable_dynamic_voids and geometry.is_body_representation(representation):
        geometry.create_dynamic_voids(obj)
