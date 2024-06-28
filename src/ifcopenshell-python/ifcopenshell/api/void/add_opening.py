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
import ifcopenshell.api.owner
import ifcopenshell.api.geometry
import ifcopenshell.guid
import ifcopenshell.util.element
import ifcopenshell.util.placement


def add_opening(
    file: ifcopenshell.file, opening: ifcopenshell.entity_instance, element: ifcopenshell.entity_instance
) -> ifcopenshell.entity_instance:
    """Create an opening in an element

    It is often necessary to cut out openings in elements like walls and
    slabs to make space to insert doors, windows, and other services that go
    through these penetrations.

    Whereas it is possible to simply draw the wall as a rectangle with a
    hole in it for the opening, often these openings have specific meanings.
    For example, an opening might be filled with a window, and so when the
    window moves, the opening should move with it. Alternatively, the
    opening itself might have fire or acoustic requirements, such that any
    service or equipment passing through that space must also comply with
    those requirements. For these types of semantic openings, you should
    have a distinct opening element which voids your regular element. For
    example, your wall will still be a rectangular prism with no hole in it,
    and a separate opening element will have a box representing the extents
    of the opening for a window. The opening element will automatically
    perform a geometric boolean operation to cut out the wall's geometry.

    Whenever you have an opening in you project, you should determine
    whether or not the opening is semantic (i.e. should be represented by a
    distinct opening object) or non-semantic (i.e. should simply be
    booleaned or be part of the shape of the object).

    :param opening: The IfcOpeningElement to cut out the element.
    :type opening: ifcopenshell.entity_instance
    :param element: The IfcElement to insert the opening into.
    :type element: ifcopenshell.entity_instance
    :return: The new IfcRelVoidsElement relationship
    :rtype: ifcopenshell.entity_instance

    Example:

    .. code:: python

        # A bit of preparation, let's create some geometric contexts since
        # we want to create some geometry for our wall and opening.
        model3d = ifcopenshell.api.context.add_context(model, context_type="Model")
        body = ifcopenshell.api.context.add_context(model,
            context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=model3d)

        # Create a wall
        wall = ifcopenshell.api.root.create_entity(model, ifc_class="IfcWall")

        # Let's use the "3D Body" representation we created earlier to add a
        # new wall-like body geometry, 5 meters long, 3 meters high, and
        # 200mm thick
        representation = ifcopenshell.api.geometry.add_wall_representation(model,
            context=body, length=5, height=3, thickness=0.2)
        ifcopenshell.api.geometry.assign_representation(model,
            product=wall, representation=representation)

        # Place our wall at the origin
        ifcopenshell.api.geometry.edit_object_placement(model, product=wall)

        # Create an opening, such as for a service penetration with fire and
        # acoustic requirements.
        opening = ifcopenshell.api.root.create_entity(model, ifc_class="IfcOpeningElement")

        # Let's create an opening representation of a 950mm x 2100mm door.
        # Notice how the thickness is greater than the wall thickness, this
        # helps resolve floating point resolution errors in 3D.
        representation = ifcopenshell.api.geometry.add_wall_representation(model,
            context=body, length=.95, height=2.1, thickness=0.4)
        ifcopenshell.api.geometry.assign_representation(model,
            product=opening, representation=representation)

        # Let's shift our door 1 meter along the wall and 100mm along the
        # wall, to create a nice overlap for the opening boolean.
        matrix = np.identity(4)
        matrix[:,3] = [1, -.1, 0, 0]
        ifcopenshell.api.geometry.edit_object_placement(model, product=opening, matrix=matrix)

        # The opening will now void the wall.
        ifcopenshell.api.void.add_opening(model, opening=opening, element=wall)
    """
    settings = {"opening": opening, "element": element}

    voids_elements = settings["opening"].VoidsElements

    if voids_elements:
        if voids_elements[0].RelatingBuildingElement == settings["element"]:
            return voids_elements[0]
        history = voids_elements[0].OwnerHistory
        file.remove(voids_elements[0])
        if history:
            ifcopenshell.util.element.remove_deep2(file, history)

    rel = file.create_entity(
        "IfcRelVoidsElement",
        **{
            "GlobalId": ifcopenshell.guid.new(),
            "OwnerHistory": ifcopenshell.api.owner.create_owner_history(file),
            "RelatingBuildingElement": settings["element"],
            "RelatedOpeningElement": settings["opening"],
        }
    )

    placement = getattr(settings["opening"], "ObjectPlacement", None)
    if placement and placement.is_a("IfcLocalPlacement"):
        ifcopenshell.api.geometry.edit_object_placement(
            file,
            product=settings["opening"],
            matrix=ifcopenshell.util.placement.get_local_placement(settings["opening"].ObjectPlacement),
            is_si=False,
        )

    return rel
