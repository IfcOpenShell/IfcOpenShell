# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2023 Dion Moult <dion@thinkmoult.com>
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


def remove_styled_representation(file: ifcopenshell.file, representation: ifcopenshell.entity_instance) -> None:
    """Removes a styled representation

    Styled representations are typically associated with materials. This
    removes the representation but not the underlying styles.

    :param representation: The IfcStyledRepresentation to remove.
    :return: None

    Example:

    .. code:: python

        model3d = ifcopenshell.api.context.add_context(model, context_type="Model")
        body = ifcopenshell.api.context.add_context(model,
            context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=model3d)
        concrete = ifcopenshell.api.material.add_material(model, name="CON01", category="concrete")
        style = ifcopenshell.api.style.add_style(model)
        ifcopenshell.api.style.add_surface_style(model, style=style, ifc_class="IfcSurfaceStyleShading",
            attributes={"SurfaceColour": {"Name": None, "Red": 0.5, "Green": 0.5, "Blue": 0.5}})
        ifcopenshell.api.style.assign_material_style(model, material=concrete, style=style, context=body)
        representation = concrete.HasRepresentation[0].Representations[0]

        # Remove a styled representation
        ifcopenshell.api.style.remove_styled_representation(model, representation=representation)
    """
    for inverse in file.get_inverse(representation):
        if inverse.is_a("IfcMaterialDefinitionRepresentation") and len(inverse.Representations) == 1:
            file.remove(inverse)

    for item in representation.Items:
        if item.is_a("IfcStyledItem") and file.get_total_inverses(item) == 1:
            for style in item.Styles:
                if style.is_a("IfcPresentationStyleAssignment"):
                    file.remove(style)
            file.remove(item)

    file.remove(representation)
