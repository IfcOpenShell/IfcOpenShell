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

import ifcopenshell
import ifcopenshell.api.geometry
import ifcopenshell.util.element


def map_type_representations(
    file: ifcopenshell.file,
    related_object: ifcopenshell.entity_instance,
    relating_type: ifcopenshell.entity_instance,
) -> None:
    """Ensures that all occurrences has the same representation as the type

    If a type has a representation, all occurrences must have the same
    representation. If the type's representation changes, this function may
    be used to ensure consistency of the occurrence's representations.

    :param related_object: The IfcElement occurrence.
    :type related_object: ifcopenshell.entity_instance
    :param relating_type: The IfcElementType type.
    :type relating_type: ifcopenshell.entity_instance
    :return: None
    :rtype: None

    Example:

    .. code:: python

        # A furniture type. This would correlate to a particular model in a
        # manufacturer's catalogue. Like an Ikea sofa :)
        furniture_type = ifcopenshell.api.root.create_entity(model,
            ifc_class="IfcFurnitureType", name="FUN01")

        # An individual occurrence of a that sofa.
        furniture = ifcopenshell.api.root.create_entity(model, ifc_class="IfcFurniture")

        # Place our furniture at the origin
        ifcopenshell.api.geometry.edit_object_placement(model, product=furniture)

        # Assign the furniture to the furniture type. Right now, the
        # furniture type has no representation, so the furniture may also
        # have no representation, or any arbitrary representation that may
        # vary from occurrence to occurrence.
        ifcopenshell.api.type.assign_type(model, related_objects=[furniture], relating_type=furniture_type)

        # A bit of preparation, let's create some geometric contexts since
        # we want to create some geometry for our furniture type.
        model3d = ifcopenshell.api.context.add_context(model, context_type="Model")
        body = ifcopenshell.api.context.add_context(model,
            context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=model3d)

        # Let's create a mesh representation of an arbitrary 2m cube.
        representation = ifcopenshell.api.geometry.add_sverchok_representation(model, context=body,
            vertices=[[(-1.0, -1.0, 0.0), (-1.0, -1.0, 2.0), (-1.0, 1.0, 0.0), (-1.0, 1.0, 2.0),
                (1.0, -1.0, 0.0), (1.0, -1.0, 2.0), (1.0, 1.0, 0.0), (1.0, 1.0, 2.0)]],
            faces=[[[0, 1, 3, 2], [2, 3, 7, 6], [6, 7, 5, 4], [4, 5, 1, 0], [2, 6, 4, 0], [7, 3, 1, 5]]])

        # Assign our new body geometry back to our furniture type. In this
        # case, since we use the API, all occurrences automatically get the
        # representation mapped, so there is nothing more we need to do.
        ifcopenshell.api.geometry.assign_representation(model,
            product=furniture_type, representation=representation)

        # However, if you were doing some sort of manual IFC patching, like
        # assigning furniture_type.RepresentationMaps directly, then you
        # might make this call:
        # ifcopenshell.api.type.map_type_representations(model,
        #     related_object=furniture, relating_type=furniture_type)
    """
    settings = {
        "related_object": related_object,
        "relating_type": relating_type,
    }

    if not settings["relating_type"].RepresentationMaps:
        return
    representations = []
    if settings["related_object"].Representation:
        representations = settings["related_object"].Representation.Representations
    for representation in representations:
        ifcopenshell.api.geometry.unassign_representation(
            file,
            product=settings["related_object"],
            representation=representation,
        )
        ifcopenshell.api.geometry.remove_representation(file, **{"representation": representation})
    for representation_map in settings["relating_type"].RepresentationMaps:
        representation = representation_map.MappedRepresentation
        mapped_representation = ifcopenshell.api.geometry.map_representation(file, representation=representation)
        ifcopenshell.api.geometry.assign_representation(
            file,
            product=settings["related_object"],
            representation=mapped_representation,
        )
