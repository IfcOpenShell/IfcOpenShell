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
from typing import Any


def assign_representation_styles(
    file: ifcopenshell.file,
    shape_representation: ifcopenshell.entity_instance,
    styles: list[ifcopenshell.entity_instance],
    replace_previous_same_type_style: bool = True,
    should_use_presentation_style_assignment: bool = False,
) -> list[ifcopenshell.entity_instance]:
    """Assigns a style directly to an object representation

    A style may either be assigned directly to an object's representation,
    or to a material which is then associated with the object. If both
    exist, then the style assigned directly to the object's representation
    takes precedence. It is recommended to use materials and assign styles
    to materials. However, sometimes you may want to assign colours directly
    to the object representation as an override. This API function provides
    that capability.

    This function assigns styles in bulk in an ordered manner to every item in
    the representation, so the order and total styles provided is significant.
    If you want more granular control, use
    :func:`ifcopenshell.api.style.assign_item_style`.

    If you want to assign styles to a material instead (recommended), then
    please see ifcopenshell.api.style.assign_material_style.

    :param shape_representation: The IfcShapeRepresentation of the object
        that you want to assign styles to. This implicitly defines the
        context at which the styles should be used.
    :type shape_representation: ifcopenshell.entity_instance
    :param styles: A list of presentation styles, typically IfcSurfaceStyle.
        The number of items in the list should correlate with the number of
        items in the shape_representation's Items attribute. If you have
        more items than styles, the last style is used.
    :type styles: list[ifcopenshell.entity_instance]
    :param replace_previous_same_type_style: Remove previously assigned styles
        of the same type as currently assign style`. Defaults to `True`.
    :type replace_previous_same_type_style: bool
    :param should_use_presentation_style_assignment: This is a technical
        detail to accomodate a bug in Revit. This should always be left as
        the default of False, unless you are finding that colours aren't
        showing up in Revit. In that case, set it to True, but keep in mind
        that this is no longer a valid IFC. Blame Autodesk.
    :type should_use_presentation_style_assignment: bool
    :return: List of created IfcStyledItems
    :rtype: list[ifcopenshell.entity_instance]

    Example:

    .. code:: python

        # A model context is needed to store 3D geometry
        model3d = ifcopenshell.api.context.add_context(model, context_type="Model")

        # Specifically, we want to store body geometry
        body = ifcopenshell.api.context.add_context(model,
            context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=model3d)

        # Let's create a new wall. The wall does not have any geometry yet.
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

        # Now specifically our wall only will be coloured grey.
        ifcopenshell.api.style.assign_representation_styles(model,
            shape_representation=representation, styles=[style])
    """
    usecase = Usecase()
    usecase.file = file
    usecase.settings = {
        "shape_representation": shape_representation,
        "styles": styles or [],
        "replace_previous_same_type_style": replace_previous_same_type_style,
        "should_use_presentation_style_assignment": should_use_presentation_style_assignment,
    }
    return usecase.execute()


class Usecase:
    file: ifcopenshell.file
    settings: dict[str, Any]
    results: list[ifcopenshell.entity_instance]

    def execute(self):
        if not self.settings["styles"]:
            return []
        self.settings["styles"] = self.settings["styles"].copy()
        self.results = []
        use_style_assignment = self.file.schema == "IFC2X3" or self.settings["should_use_presentation_style_assignment"]
        replace_previous_same_type_style = self.settings["replace_previous_same_type_style"]

        for element in self.file.traverse(self.settings["shape_representation"]):
            if not element.is_a("IfcShapeModel"):
                continue
            for item in element.Items:
                if not item.is_a("IfcGeometricRepresentationItem") and not item.is_a(
                    "IfcTopologicalRepresentationItem"
                ):
                    continue
                if self.settings["styles"]:
                    # If there are more items than styles, fallback to using the last style
                    style = self.settings["styles"].pop(0)
                name = style.Name
                current_style_type = style.is_a()

                # item may had previous styled item
                prev_styled_item = next((i for i in item.StyledByItem), None)
                style_assignment = None  # try to find some style assignment to reuse

                if prev_styled_item is None:
                    if use_style_assignment:
                        style_assignment = self.file.createIfcPresentationStyleAssignment([style])
                        self.results.append(self.file.createIfcStyledItem(item, [style_assignment], name))
                    else:
                        self.results.append(self.file.createIfcStyledItem(item, [style], name))
                    continue

                if replace_previous_same_type_style:
                    self.remove_same_type_styles(prev_styled_item, current_style_type, remove_item=False)
                    for style_ in prev_styled_item.Styles:
                        if style_.is_a("IfcPresentationStyleAssignment"):
                            if use_style_assignment and style_assignment is None:
                                style_assignment = style_
                                self.remove_same_type_styles(style_assignment, current_style_type, remove_item=False)
                            else:
                                self.remove_same_type_styles(style_assignment, current_style_type, remove_item=True)

                    if use_style_assignment:
                        if style_assignment:
                            style_assignment.Styles = style_assignment.Styles + (style,)
                        else:
                            style_assignment = self.file.createIfcPresentationStyleAssignment([style])
                            prev_styled_item.Styles = prev_styled_item.Styles + (style_assignment,)
                    else:
                        prev_styled_item.Styles = prev_styled_item.Styles + (style,)
                    continue

                # collect previously assigned styles
                assigned_styles = []
                for style_ in prev_styled_item.Styles:
                    if style_.is_a("IfcPresentationStyleAssignment"):
                        if style_assignment is None:
                            style_assignment = style_
                        assigned_styles.extend(style_.Styles)
                    else:  # IfcPresentationStyle
                        assigned_styles.append(style_)

                if style in assigned_styles:
                    continue

                if use_style_assignment:
                    if style_assignment is not None:
                        style_assignment.Styles = style_assignment.Styles + (style,)
                    else:
                        style_assignment = self.file.createIfcPresentationStyleAssignment([style])
                        prev_styled_item.Styles = prev_styled_item.Styles + (style_assignment,)
                else:
                    prev_styled_item.Styles = prev_styled_item.Styles + (style,)

        return self.results

    def remove_same_type_styles(self, style_item, current_style_type: str, remove_item: bool) -> None:
        styles = [s for s in style_item.Styles if s.is_a() != current_style_type]
        if remove_item and not styles:
            self.file.remove(style_item)
        else:
            style_item.Styles = styles
