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
from typing import Optional, Union


def assign_item_style(
    file: ifcopenshell.file,
    item: ifcopenshell.entity_instance,
    style: Optional[ifcopenshell.entity_instance],
    should_use_presentation_style_assignment: bool = False,
) -> Union[ifcopenshell.entity_instance, None]:
    """Assigns a style directly to a representation item

    A style may either be assigned directly to an object's representation
    items, or to a material which is then associated with the object. If both
    exist, then the style assigned directly to the object's representation
    takes precedence. It is recommended to use materials and assign styles to
    materials. However, sometimes you may want to assign colours directly to
    the object representation as an override. This API function provides that
    capability.

    If you want to assign styles to a material instead (recommended), then
    please see ifcopenshell.api.style.assign_material_style.

    :param item: The IfcRepresentationItem of the object
        that you want to assign styles to.
    :param style: A presentation style, typically IfcSurfaceStyle. None if you
        want to remove an existing style from the item.
    :return: Created or existing IfcStyledItem, or None if the style was removed.

    Example:

    .. code:: python

        # A model context is needed to store 3D geometry
        model3d = ifcopenshell.api.context.add_context(model, context_type="Model")

        # Specifically, we want to store body geometry
        body = ifcopenshell.api.context.add_context(model,
            context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=model3d)

        # Let's create a new block shaped furniture. The furniture does not have any geometry yet.
        wall = ifcopenshell.api.root.create_entity(model, ifc_class="IfcWall")

        # Let's use the "3D Body" representation we created earlier to add a
        # new wall-like body geometry, 5 meters long, 3 meters high, and
        # 200mm thick
        representation = ifcopenshell.api.geometry.add_wall_representation(model,
            context=body, length=5, height=3, thickness=0.2)

        # Assign our new body geometry back to our wall
        ifcopenshell.api.geometry.assign_representation(model,
            product=wall, representation=representation)

        # Place our wall at the origin
        ifcopenshell.api.geometry.edit_object_placement(model, product=wall)

        # Create a new surface style
        style = ifcopenshell.api.style.add_style(model)

        # Create a simple grey shading colour and transparency.
        ifcopenshell.api.style.add_surface_style(model,
            style=style, ifc_class="IfcSurfaceStyleShading", attributes={
                "SurfaceColour": { "Name": None, "Red": 0.5, "Green": 0.5, "Blue": 0.5 },
                "Transparency": 0., # 0 is opaque, 1 is transparent
            })

        # Now specifically our wall's only item only will be coloured grey.
        ifcopenshell.api.style.assign_item_style(model,
            shape_representation=representation, style=style, item=representation.Items[0])
    """
    if not (styled_item := next(iter(item.StyledByItem), None)):
        if style is None:
            return
        if file.schema == "IFC2X3":
            style = file.create_entity("IfcPresentationStyleAssignment", (style,))
        return file.create_entity("IfcStyledItem", item, (style,))

    styled_item_styles = styled_item.Styles
    if style and styled_item_styles == (style,):
        return styled_item

    if file.schema == "IFC4X3":
        if style is None:
            file.remove(styled_item)
            return
        styled_item.Styles = (style,)
        return styled_item

    # < IFC4X3
    # Can't just remove a styled item or assign a style
    # since we need to remove/change the possible style assignments.
    assignment = None
    for style_ in styled_item_styles:
        if not style_.is_a("IfcPresentationStyleAssignment"):
            continue
        # Remove second assignment.
        if style is None or assignment:
            file.remove(style_)
        else:
            assignment = style_
            if assignment.Styles != (style,):
                assignment.Styles = (style,)

    if style is None:
        file.remove(styled_item)
        return

    if assignment:
        if styled_item_styles == (assignment,):
            return styled_item
        styled_item.Styles = (assignment,)
        return styled_item

    styled_item.Styles = (style,)
    return styled_item
