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


def unassign_representation_styles(
    file: ifcopenshell.file,
    shape_representation: ifcopenshell.entity_instance,
    styles: list[ifcopenshell.entity_instance],
    should_use_presentation_style_assignment: bool = False,
) -> None:
    """Unassigns styles directly assigned to an object representation

    This does the inverse of assign_representation_styles.

    :param shape_representation: The IfcShapeRepresentation of the object
        that you want to unassign styles from.
    :param styles: A list of presentation styles, typically IfcSurfaceStyle.
        The number of items in the list should correlate with the number of
        items in the shape_representation's Items attribute. If you have
        more items than styles, the last style is used.
    :param should_use_presentation_style_assignment: This is a technical
        detail to accomodate a bug in Revit. This should always be left as
        the default of False, unless you are finding that colours aren't
        showing up in Revit. In that case, set it to True, but keep in mind
        that this is no longer a valid IFC. Blame Autodesk.
    :return: None

    Example:

    .. code:: python

        model3d = ifcopenshell.api.context.add_context(model, context_type="Model")
        body = ifcopenshell.api.context.add_context(model,
            context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=model3d)
        wall = ifcopenshell.api.root.create_entity(model, ifc_class="IfcWall")
        representation = ifcopenshell.api.geometry.add_wall_representation(model,
            context=body, length=5, height=3, thickness=0.2)
        ifcopenshell.api.geometry.assign_representation(model,
            product=wall, representation=representation)
        style = ifcopenshell.api.style.add_style(model)
        ifcopenshell.api.style.add_surface_style(model, style=style, ifc_class="IfcSurfaceStyleShading",
            attributes={"SurfaceColour": {"Name": None, "Red": 0.5, "Green": 0.5, "Blue": 0.5}})
        ifcopenshell.api.style.assign_representation_styles(model,
            shape_representation=representation, styles=[style])
        ifcopenshell.api.style.unassign_representation_styles(model,
            shape_representation=representation, styles=[style])
    """
    usecase = Usecase()
    usecase.file = file
    return usecase.execute(shape_representation, styles, should_use_presentation_style_assignment)


class Usecase:
    file: ifcopenshell.file

    def execute(
        self,
        shape_representation: ifcopenshell.entity_instance,
        styles: list[ifcopenshell.entity_instance],
        should_use_presentation_style_assignment: bool,
    ) -> None:
        if not styles:
            return
        use_style_assignment = self.file.schema == "IFC2X3" or should_use_presentation_style_assignment

        for element in self.file.traverse(shape_representation):
            if not element.is_a("IfcShapeRepresentation"):
                continue
            for item in element.Items:
                if not item.is_a("IfcGeometricRepresentationItem"):
                    continue

                if not item.StyledByItem:
                    continue

                item = item.StyledByItem[0]
                if use_style_assignment:
                    for style_ in item.Styles:
                        if style_.is_a("IfcPresentationStyleAssignment"):
                            self.remove_styles(style_, styles)
                self.remove_styles(item, styles)

    def remove_styles(
        self, item: ifcopenshell.entity_instance, removed_styles: list[ifcopenshell.entity_instance]
    ) -> None:
        """Removes styles from a styled item or a style assignment
        and purges item if doesn't have any styles after"""
        styles = [s for s in item.Styles if s not in removed_styles]
        if not styles:
            self.file.remove(item)
        elif len(styles) != len(item.Styles):
            item.Styles = styles
