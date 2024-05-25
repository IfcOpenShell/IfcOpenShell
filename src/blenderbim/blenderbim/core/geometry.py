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
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    import bpy
    import ifcopenshell
    import blenderbim.tool as tool


def edit_object_placement(
    ifc: tool.Ifc, geometry: tool.Geometry, surveyor: tool.Surveyor, obj: Optional[bpy.types.Object] = None
) -> None:
    element = ifc.get_entity(obj)
    if not element:
        return
    geometry.clear_cache(element)
    geometry.clear_scale(obj)
    ifc.run("geometry.edit_object_placement", product=element, matrix=surveyor.get_absolute_matrix(obj))
    geometry.record_object_position(obj)


def add_representation(
    ifc: tool.Ifc,
    geometry: tool.Geometry,
    style: tool.Style,
    surveyor: tool.Surveyor,
    obj: bpy.types.Object,
    context: ifcopenshell.entity_instance,
    ifc_representation_class: Optional[str] = None,
    profile_set_usage: Optional[ifcopenshell.entity_instance] = None,
) -> ifcopenshell.entity_instance:
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

    if not representation:
        raise IncompatibleRepresentationError()

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
    ifc: tool.Ifc,
    geometry: tool.Geometry,
    obj: bpy.types.Object,
    representation: ifcopenshell.entity_instance,
    should_reload: bool = True,
    is_global: bool = True,
    should_sync_changes_first: bool = False,
    apply_openings: bool = True,
) -> None:
    """Function can switch to representation that wasn't yet assigned to that object. See #2766.

    `should_sync_changes_first` - sync ifc representation with current state of `obj.data`;

    `should_reload` - reload `obj.data` from ifc representation;

    `is_global` - replace mesh data for all users of `obj.data`, not just `obj`;

    """
    if should_sync_changes_first and geometry.is_edited(obj) and not geometry.is_box_representation(representation):
        representation_id = geometry.get_representation_id(representation)
        geometry.run_geometry_update_representation(obj=obj)
        if not geometry.does_representation_id_exist(representation_id):
            return

    entity = ifc.get_entity(obj)
    current_obj_data = geometry.get_object_data(obj)

    if not current_obj_data and geometry.is_text_literal(representation):
        return

    has_openings = apply_openings and getattr(entity, "HasOpenings", None)
    if has_openings:
        # if it has openings make sure to switch to element's mapped representation
        representation = geometry.unresolve_type_representation(representation, entity)
    else:
        # doesn't resolve mapped representations in case if it's going to have openings
        # otherwise we would also add openings to the type and other occurences mesh data
        representation = geometry.resolve_mapped_representation(representation)

    old_repr_data = geometry.get_representation_data(representation)
    if should_reload or not old_repr_data:
        new_repr_data = geometry.import_representation(obj, representation, apply_openings=apply_openings)
        geometry.rename_object(new_repr_data, geometry.get_representation_name(representation))
        geometry.link(representation, new_repr_data)
    else:
        new_repr_data = old_repr_data

    geometry.change_object_data(obj, new_repr_data, is_global=is_global and not has_openings)
    geometry.record_object_materials(obj)

    # we assume that all the occurences and the type have the same representation context active
    # so geometry.delete_data cannot remove the data that's still used by some other object
    if should_reload and old_repr_data:
        # if current object was using some temporary mesh (like during profile edit mode) instead of `old_repr_data`
        # then `change_object_data` won't switch the mesh for all the occurences and we need to do it explicitly
        if current_obj_data != old_repr_data and geometry.has_data_users(old_repr_data):
            geometry.replace_object_data_globally(old_repr_data, new_repr_data)
        geometry.delete_data(old_repr_data)

    geometry.clear_modifiers(obj)
    geometry.clear_cache(entity)


def get_representation_ifc_parameters(geometry, obj=None, should_sync_changes_first=False):
    geometry.import_representation_parameters(geometry.get_object_data(obj))


def remove_representation(ifc, geometry, obj=None, representation=None):
    """Consider changing obj representation before using the function,
    otherwise it will replace object with empty."""

    element = ifc.get_entity(obj)
    element_type = geometry.get_element_type(element)
    data = None
    if element_type and (geometry.is_mapped_representation(representation) or geometry.is_type_product(element)):
        representation = geometry.resolve_mapped_representation(representation)
        data = geometry.get_representation_data(representation)
        if data and geometry.has_data_users(data):
            for element in geometry.get_elements_of_type(element_type):
                obj = ifc.get_object(element)
                if obj:
                    obj = geometry.replace_object_with_empty(obj)
            obj = ifc.get_object(element_type)
            if obj:
                obj = geometry.replace_object_with_empty(obj)
        ifc.run("geometry.unassign_representation", product=element_type, representation=representation)
        ifc.run("geometry.remove_representation", representation=representation)
    else:
        data = geometry.get_representation_data(representation)
        if data and geometry.has_data_users(data):
            geometry.replace_object_with_empty(obj)
        ifc.run("geometry.unassign_representation", product=element, representation=representation)
        ifc.run("geometry.remove_representation", representation=representation)
    if data:
        geometry.delete_data(data)


def purge_unused_representations(ifc, geometry):
    purged_representations = 0
    for representation in geometry.get_model_representations():
        if ifc.get().get_total_inverses(representation) == 0:
            ifc.run("geometry.remove_representation", representation=representation)
            purged_representations += 1
    return purged_representations


def select_connection(geometry, connection=None):
    geometry.select_connection(connection)


def remove_connection(geometry, connection=None):
    geometry.remove_connection(connection)


def get_similar_openings(ifc, opening):
    model = ifc.get()
    all_openings = model.by_type("IfcOpeningElement")
    similar_openings = [o for o in all_openings if o.ObjectPlacement == opening.ObjectPlacement and o != opening]
    return similar_openings


def get_similar_openings_building_objs(ifc, similar_openings):
    building_objs = []
    for similar_opening in similar_openings:
        building_objs.append(ifc.get_object(similar_opening.VoidsElements[0].RelatingBuildingElement))
    return building_objs


def edit_similar_opening_placement(geometry, opening=None, similar_openings=None):
    if not opening or not similar_openings:
        return
    for similar_opening in similar_openings:
        old_placement = similar_opening.ObjectPlacement
        similar_opening.ObjectPlacement = opening.ObjectPlacement
        geometry.delete_opening_object_placement(old_placement)


class IncompatibleRepresentationError(Exception):
    pass
