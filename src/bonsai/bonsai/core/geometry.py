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

from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Sequence, Union

if TYPE_CHECKING:
    import bpy
    import ifcopenshell
    import bonsai.tool as tool


def edit_object_placement(
    ifc: tool.Ifc,
    geometry: tool.Geometry,
    surveyor: tool.Surveyor,
    obj: Optional[bpy.types.Object] = None,
    apply_scale: bool = True,
) -> None:
    """Sync current object placement.

    - apply and clear object scale;
    - write current object position to IFC;
    - update position checksums;
    """
    element = ifc.get_entity(obj)
    if not element:
        return
    geometry.clear_cache(element)
    if apply_scale:
        geometry.clear_scale(obj)
    geometry.get_blender_offset_type(obj)
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
) -> Union[ifcopenshell.entity_instance, None]:
    """Add IFC representation based on object `.data`."""
    element = ifc.get_entity(obj)
    if not element:
        return

    edit_object_placement(ifc, geometry, surveyor, obj=obj)
    data = geometry.get_object_data(obj)

    if not geometry.is_data_supported_for_adding_representation(data) and ifc_representation_class != "IfcTextLiteral":
        return

    representation = ifc.run(
        "geometry.add_representation",
        context=context,
        blender_object=obj,
        geometry=data,
        coordinate_offset=geometry.get_cartesian_point_offset(obj),
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

    :param should_sync_changes_first: sync ifc representation with current state of `obj.data`
    :param should_reload: reload `obj.data` from ifc representation
    :param is_global: replace mesh data for all users of `obj.data`, not just `obj`

    """
    if should_sync_changes_first and ifc.is_edited(obj) and not geometry.is_box_representation(representation):
        representation_id = geometry.get_representation_id(representation)
        geometry.run_geometry_update_representation(obj=obj)
        if not geometry.does_representation_id_exist(representation_id):
            return

    if not geometry.get_object_data(obj) and geometry.is_text_literal(representation):
        return

    geometry.reimport_element_representations(obj, representation, apply_openings=apply_openings)


def get_representation_ifc_parameters(
    geometry: tool.Geometry, obj: bpy.types.Object, should_sync_changes_first: bool = False
) -> None:
    geometry.import_representation_parameters(geometry.get_object_data(obj))


def remove_representation(
    ifc: tool.Ifc, geometry: tool.Geometry, obj: bpy.types.Object, representation: ifcopenshell.entity_instance
) -> None:
    """Remove IFC representation from an object.

    If removed representation is active will automatically change it to some other one.
    If it is the object's only representation, object will be recreated as an empty.
    """

    element = ifc.get_entity(obj)
    assert element
    element_type = geometry.get_element_type(element)
    data = None
    if element_type and (geometry.is_mapped_representation(representation) or geometry.is_type_product(element)):
        representation = geometry.resolve_mapped_representation(representation)
        data = geometry.get_representation_data(representation)
        if data and geometry.has_data_users(data):
            for element in geometry.get_elements_of_type(element_type):
                obj = ifc.get_object(element)
                if obj:
                    geometry.switch_from_representation(obj, representation)
            obj = ifc.get_object(element_type)
            if obj:
                geometry.switch_from_representation(obj, representation)
        ifc.run("geometry.unassign_representation", product=element_type, representation=representation)
    else:
        data = geometry.get_representation_data(representation)
        if data and geometry.has_data_users(data):
            geometry.switch_from_representation(obj, representation)
        ifc.run("geometry.unassign_representation", product=element, representation=representation)

    ifc.run("geometry.remove_representation", representation=representation)
    if data:
        geometry.delete_data(data)


def purge_unused_representations(ifc: tool.Ifc, geometry: tool.Geometry) -> int:
    """Purge representations without inverses.

    :return: A number of purged representations.
    """
    purged_representations = 0
    for representation in geometry.get_model_representations():
        if ifc.get().get_total_inverses(representation) == 0:
            ifc.run("geometry.remove_representation", representation=representation)
            purged_representations += 1
    return purged_representations


def select_connection(geometry: tool.Geometry, connection: ifcopenshell.entity_instance) -> None:
    geometry.select_connection(connection)


def remove_connection(geometry: tool.Geometry, connection: ifcopenshell.entity_instance) -> None:
    geometry.remove_connection(connection)


def get_similar_openings(ifc: tool.Ifc, opening: ifcopenshell.entity_instance) -> list[ifcopenshell.entity_instance]:
    model = ifc.get()
    all_openings = model.by_type("IfcOpeningElement")
    similar_openings = [o for o in all_openings if o.ObjectPlacement == opening.ObjectPlacement and o != opening]
    return similar_openings


def get_similar_openings_building_objs(
    ifc: tool.Ifc, similar_openings: list[ifcopenshell.entity_instance]
) -> list[bpy.types.Object]:
    building_objs = []
    for similar_opening in similar_openings:
        building_objs.append(ifc.get_object(similar_opening.VoidsElements[0].RelatingBuildingElement))
    return building_objs


def edit_similar_opening_placement(
    geometry: tool.Geometry,
    opening: Optional[ifcopenshell.entity_instance] = None,
    similar_openings: Sequence[ifcopenshell.entity_instance] = (),
) -> None:
    if not opening or not similar_openings:
        return
    for similar_opening in similar_openings:
        old_placement = similar_opening.ObjectPlacement
        similar_opening.ObjectPlacement = opening.ObjectPlacement
        geometry.delete_opening_object_placement(old_placement)


class IncompatibleRepresentationError(Exception):
    pass
