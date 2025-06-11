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

import ifcopenshell.api.style
import ifcopenshell.util.element
from collections.abc import Iterable


def remove_style(file: ifcopenshell.file, style: ifcopenshell.entity_instance) -> None:
    """Removes a presentation style

    All of the presentation items of the style will also be removed.

    :param style: The IfcPresentationStyle to remove.
    :return: None

    Example:

    .. code:: python

        # Create a new surface style
        style = ifcopenshell.api.style.add_style(model)

        # Not anymore!
        ifcopenshell.api.style.remove_style(model, style=style)
    """
    usecase = Usecase()
    usecase.file = file
    return usecase.execute(style)


class Usecase:
    file: ifcopenshell.file

    def execute(
        self, style: ifcopenshell.entity_instance, do_not_delete: Iterable[ifcopenshell.entity_instance] = ()
    ) -> None:
        self.purge_inverses(style)
        ifc_class = style.is_a()
        if ifc_class == "IfcSurfaceStyle":
            for style_ in style.Styles:
                ifcopenshell.api.style.remove_surface_style(self.file, style=style_)
        elif ifc_class == "IfcFillAreaStyle":
            for style_ in style.FillStyles:
                ifcopenshell.util.element.remove_deep2(
                    self.file, style_, also_consider=[style], do_not_delete=list(do_not_delete)
                )
        self.file.remove(style)

    def purge_inverses(self, style: ifcopenshell.entity_instance) -> None:
        for inverse in self.file.get_inverse(style):
            if inverse.is_a("IfcStyledItem"):
                if len(inverse.Styles) == 1:
                    self.purge_styled_representations(inverse)
                    self.file.remove(inverse)
            # IfcCurveStyle -> IfcFillAreaStyleHatching.
            elif inverse.is_a("IfcFillAreaStyleHatching"):
                self.purge_fill_area_style_hatching(inverse, style)

    def purge_styled_representations(self, styled_item: ifcopenshell.entity_instance) -> None:
        for inverse in self.file.get_inverse(styled_item):
            if inverse.is_a("IfcStyledRepresentation") and len(inverse.Items) == 1:
                self.purge_material_definition_representations(inverse)
                self.file.remove(inverse)

    def purge_material_definition_representations(self, styled_representation: ifcopenshell.entity_instance) -> None:
        for inverse in self.file.get_inverse(styled_representation):
            if inverse.is_a("IfcMaterialDefinitionRepresentation") and len(inverse.Representations) == 1:
                self.file.remove(inverse)

    def purge_fill_area_style_hatching(
        self, fill_area_style_hatching: ifcopenshell.entity_instance, style: ifcopenshell.entity_instance
    ) -> None:
        for inverse in self.file.get_inverse(fill_area_style_hatching):
            if inverse.is_a("IfcFillAreaStyle"):
                self.execute(inverse, do_not_delete=(fill_area_style_hatching, style))
        ifcopenshell.util.element.remove_deep2(self.file, fill_area_style_hatching, do_not_delete=[style])
