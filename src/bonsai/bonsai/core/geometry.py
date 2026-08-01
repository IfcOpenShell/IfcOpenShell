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

from collections.abc import Sequence
from typing import TYPE_CHECKING, Optional, Union

if TYPE_CHECKING:
    import bpy
    import ifcopenshell

    import bonsai.tool as tool


def edit_object_placement(
    ifc: type[tool.Ifc],
    geometry: type[tool.Geometry],
    surveyor: type[tool.Surveyor],
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
    ifc: type[tool.Ifc],
    geometry: type[tool.Geometry],
    style: type[tool.Style],
    surveyor: type[tool.Surveyor],
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
    ifc: type[tool.Ifc],
    geometry: type[tool.Geometry],
    obj: bpy.types.Object,
    representation: ifcopenshell.entity_instance,
    apply_openings: bool = True,
) -> None:
    """Switch obj representation (even if not yet assigned to that object. See #2766.)"""
    if not geometry.get_object_data(obj) and geometry.is_text_literal(representation):
        return

    element = ifc.get_entity(obj)
    assert element
    geometry.clear_cache(element)
    geometry.reimport_element_representations(obj, representation, apply_openings=apply_openings)


def get_representation_ifc_parameters(geometry: type[tool.Geometry], obj: bpy.types.Object) -> None:
    geometry.import_representation_parameters(geometry.get_object_data(obj))


def remove_representation(
    ifc: type[tool.Ifc],
    geometry: type[tool.Geometry],
    obj: bpy.types.Object,
    representation: ifcopenshell.entity_instance,
) -> None:
    """Remove IFC representation from an object.

    If removed representation is active will automatically change it to some other one.
    If it is the object's only representation, object will be recreated as an empty.
    """

    element = ifc.get_entity(obj)
    assert element
    element_type = geometry.get_element_type(element)
    data = None
    data_removed_by_switch_representation = False
    if element_type and (geometry.is_mapped_representation(representation) or geometry.is_type_product(element)):
        representation = geometry.resolve_mapped_representation(representation)
        data = geometry.get_representation_data(representation)
        if data and geometry.has_data_users(data):
            for element in geometry.get_elements_of_type(element_type):
                obj = ifc.get_object(element)
                if obj:
                    data_removed_by_switch_representation = True
                    geometry.switch_from_representation(obj, representation)
            obj = ifc.get_object(element_type)
            if obj:
                geometry.switch_from_representation(obj, representation)
        ifc.run("geometry.unassign_representation", product=element_type, representation=representation)
    else:
        data = geometry.get_representation_data(representation)
        if data and geometry.has_data_users(data):
            data_removed_by_switch_representation = True
            geometry.switch_from_representation(obj, representation)
        ifc.run("geometry.unassign_representation", product=element, representation=representation)

    ifc.run("geometry.remove_representation", representation=representation)

    if data and not data_removed_by_switch_representation:
        geometry.delete_data(data)


def promote_representation_to_type(
    ifc: type[tool.Ifc],
    geometry: type[tool.Geometry],
    obj: bpy.types.Object,
    representation: ifcopenshell.entity_instance,
) -> dict[str, int]:
    """Move an occurrence-local representation onto its type (slot-based, type wins).

    The representation is copied onto the type as a mapped representation. Then,
    for every occurrence of the type, **any** existing representation in the same
    *slot* — same context (context/subcontext/target view), same
    ``RepresentationIdentifier`` and same ``RepresentationType`` — is removed and
    replaced by the type's mapped representation. This covers both a local
    (non-mapped) rep and an already-mapped rep the occurrence inherited from
    another map (e.g. a floating ``IfcRepresentationMap`` not anchored to the
    type, as Revit exports), so no duplicate is left. If the type already holds a
    rep in the slot it is removed too, so promoting is idempotent / replaces
    rather than accumulating maps.

    Geometry is NOT compared: the type's representation replaces the
    occurrence's for that slot, even when the occurrence's geometry differs
    (e.g. an independently meshed / mirrored / rotated instance) — such
    occurrences visibly adopt the type's geometry.

    :return: counts dict with ``replaced`` (occurrence reps removed) and
        ``occurrences`` (occurrences that now reference the type's mapped rep).
    """
    element = ifc.get_entity(obj)
    assert element
    element_type = geometry.get_element_type(element)
    assert element_type, "Cannot promote a representation without a type."
    context = representation.ContextOfItems
    identifier = representation.RepresentationIdentifier
    # Compare the *resolved* type: an inherited rep is a "MappedRepresentation"
    # whose real type lives on the map's target, so matching the raw
    # RepresentationType would miss it and leave a duplicate.
    rep_type = geometry.resolve_mapped_representation(representation).RepresentationType

    def _in_slot(r: ifcopenshell.entity_instance) -> bool:
        return (
            r.ContextOfItems == context
            and r.RepresentationIdentifier == identifier
            and geometry.resolve_mapped_representation(r).RepresentationType == rep_type
        )

    # Copy the promoted geometry for the type up front, before any removal below
    # can touch the source occurrence's representation.
    type_representation = geometry.copy_representation_deep(representation)

    # Snapshot every occurrence's reps in the slot (local AND mapped) so we can
    # replace them -- an occurrence may already inherit a mapped rep in the slot,
    # which would otherwise be left behind as a duplicate.
    occurrence_reps: dict[ifcopenshell.entity_instance, list[ifcopenshell.entity_instance]] = {}
    for occurrence in geometry.get_elements_of_type(element_type):
        occurrence_reps[occurrence] = [r for r in geometry.get_representations_iter(occurrence) if _in_slot(r)]

    counts = {"replaced": 0, "occurrences": 0}
    # 1. Drop every existing rep in the slot from each occurrence.
    for occurrence, reps_in_slot in occurrence_reps.items():
        occurrence_obj = ifc.get_object(occurrence)
        for rep in reps_in_slot:
            if occurrence_obj is not None and not geometry.is_mapped_representation(rep):
                # Blender-aware removal for a local mesh the object may display.
                remove_representation(ifc, geometry, obj=occurrence_obj, representation=rep)
            else:
                # Mapped wrapper (or object not loaded): remove from this
                # occurrence only. remove_representation's remove_deep2 keeps a
                # shared map alive until its last user is gone.
                ifc.run("geometry.unassign_representation", product=occurrence, representation=rep)
                ifc.run("geometry.remove_representation", representation=rep)
            counts["replaced"] += 1

    # 2. Drop any rep the type already holds in this slot, so we replace rather
    #    than accumulate maps. (Must run before adding the new map below.)
    for rm in list(element_type.RepresentationMaps or []):
        mapped = rm.MappedRepresentation
        if mapped and _in_slot(mapped):
            ifc.run("geometry.unassign_representation", product=element_type, representation=mapped)
            ifc.run("geometry.remove_representation", representation=mapped)

    # 3. Add the promoted geometry to the type and map it onto every occurrence.
    geometry.add_type_representation_map(element_type, type_representation)
    for occurrence in occurrence_reps:
        mapped_representation = ifc.run("geometry.map_representation", representation=type_representation)
        ifc.run("geometry.assign_representation", product=occurrence, representation=mapped_representation)
        counts["occurrences"] += 1

    return counts


def purge_unused_representations(ifc: type[tool.Ifc], geometry: type[tool.Geometry]) -> int:
    """Purge representations without inverses.

    :return: A number of purged representations.
    """
    purged_representations = 0
    for representation in geometry.get_model_representations():
        if ifc.get().get_total_inverses(representation) == 0:
            ifc.run("geometry.remove_representation", representation=representation)
            purged_representations += 1
    return purged_representations


def select_connection(geometry: type[tool.Geometry], connection: ifcopenshell.entity_instance) -> None:
    geometry.select_connection(connection)


def remove_connection(geometry: type[tool.Geometry], connection: ifcopenshell.entity_instance) -> None:
    geometry.remove_connection(connection)


def get_similar_openings(
    ifc: type[tool.Ifc], opening: ifcopenshell.entity_instance
) -> list[ifcopenshell.entity_instance]:
    model = ifc.get()
    all_openings = model.by_type("IfcOpeningElement")
    similar_openings = [o for o in all_openings if o.ObjectPlacement == opening.ObjectPlacement and o != opening]
    return similar_openings


def get_similar_openings_building_objs(
    ifc: type[tool.Ifc], similar_openings: list[ifcopenshell.entity_instance]
) -> list[bpy.types.Object]:
    building_objs = []
    for similar_opening in similar_openings:
        building_objs.append(ifc.get_object(similar_opening.VoidsElements[0].RelatingBuildingElement))
    return building_objs


def edit_similar_opening_placement(
    geometry: type[tool.Geometry],
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
