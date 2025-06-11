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
    :type shape_representation: ifcopenshell.entity_instance
    :param styles: A list of presentation styles, typically IfcSurfaceStyle.
        The number of items in the list should correlate with the number of
        items in the shape_representation's Items attribute. If you have
        more items than styles, the last style is used.
    :type styles: list[ifcopenshell.entity_instance]
    :param should_use_presentation_style_assignment: This is a technical
        detail to accomodate a bug in Revit. This should always be left as
        the default of False, unless you are finding that colours aren't
        showing up in Revit. In that case, set it to True, but keep in mind
        that this is no longer a valid IFC. Blame Autodesk.
    :type should_use_presentation_style_assignment: bool
    :return: None
    :rtype: None

    Example:

    .. code:: python

        ifcopenshell.api.style.unassign_representation_styles(model,
            shape_representation=representation, styles=[style])
    """
    usecase = Usecase()
    usecase.file = file
    usecase.settings = {
        "shape_representation": shape_representation,
        "styles": styles or [],
        "should_use_presentation_style_assignment": should_use_presentation_style_assignment,
    }
    return usecase.execute()


class Usecase:
    file: ifcopenshell.file
    settings: dict[str, Any]

    def execute(self):
        if not self.settings["styles"]:
            return []
        self.results = []
        use_style_assignment = self.file.schema == "IFC2X3" or self.settings["should_use_presentation_style_assignment"]

        for element in self.file.traverse(self.settings["shape_representation"]):
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
                            self.remove_styles(style_)
                self.remove_styles(item)

    def remove_styles(self, item):
        """Removes styles from a styled item or a style assignment
        and purges item if doesn't have any styles after"""
        styles = [s for s in item.Styles if s not in self.settings["styles"]]
        if not styles:
            self.file.remove(item)
        elif len(styles) != len(item.Styles):
            item.Styles = styles
