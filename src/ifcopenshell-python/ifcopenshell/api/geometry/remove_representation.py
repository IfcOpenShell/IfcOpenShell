# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of IfcOpenShell.
#
# IfcOpenShell is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcOpenShell is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcOpenShell.  If not, see <http://www.gnu.org/licenses/>.

import ifcopenshell.util.element


def remove_representation(
    file: ifcopenshell.file, representation: ifcopenshell.entity_instance, should_keep_named_profiles: bool = True
) -> None:
    """Remove a representation.

    Also purges representation items and their related elements
    like IfcStyledItem, tessellated facesets colours and UV map.

    By default, named profiles are assumed to be significant (i.e. curated as
    part of a profile library) and will not be removed.

    :param representation: IfcRepresentation to remove.
        Note that it's expected that IfcRepresentation won't be in use
        before calling this method (in such elements as IfcProductRepresentation, IfcShapeAspect)
        otherwise representation won't be removed.
    :param should_keep_named_profiles: If true, named profile defs will not be
        removed as they are assumed to be significant.
    """
    is_ifc2x3 = file.schema == "IFC2X3"
    styled_items = set()
    presentation_layer_assignments_items: set[ifcopenshell.entity_instance] = set()
    presentation_layer_assignments_reps: set[ifcopenshell.entity_instance] = set()
    textures = set()
    colours = set()
    named_profiles = set()
    for subelement in file.traverse(representation):
        if subelement.is_a("IfcRepresentationItem"):
            [styled_items.add(s) for s in subelement.StyledByItem or []]
            # IFC2X3 is using LayerAssignments
            for s in subelement.LayerAssignment if not is_ifc2x3 else subelement.LayerAssignments:
                presentation_layer_assignments_items.add(s)
            # IfcTessellatedFaceSet inverses
            [textures.add(t) for t in getattr(subelement, "HasTextures", []) or []]
            [colours.add(t) for t in getattr(subelement, "HasColours", []) or []]
        elif subelement.is_a("IfcRepresentation"):
            for layer in subelement.LayerAssignments:
                presentation_layer_assignments_reps.add(layer)
        elif subelement.is_a("IfcProfileDef") and subelement.ProfileName:
            named_profiles.add(subelement)

    do_not_delete = file.by_type("IfcGeometricRepresentationContext")
    if should_keep_named_profiles:
        do_not_delete += named_profiles

    # Order matters - layer assignments may reference representation directly.
    also_consider = list(presentation_layer_assignments_reps)
    also_consider.extend(presentation_layer_assignments_items - presentation_layer_assignments_reps)
    also_consider.extend(styled_items)
    also_consider.extend(textures)
    ifcopenshell.util.element.remove_deep2(
        file,
        representation,
        also_consider=also_consider,
        do_not_delete=set(do_not_delete),
    )

    for texture in textures:
        ifcopenshell.util.element.remove_deep2(file, texture)
    for colour in colours:
        ifcopenshell.util.element.remove_deep2(file, colour)

    to_delete = file.to_delete or set()
    for element in styled_items:
        item = element.Item
        if not item or item in to_delete:
            file.remove(element)
    presentation_layer_assignments = presentation_layer_assignments_reps | presentation_layer_assignments_items
    for element in presentation_layer_assignments:
        if all(item in to_delete for item in element.AssignedItems):
            file.remove(element)
