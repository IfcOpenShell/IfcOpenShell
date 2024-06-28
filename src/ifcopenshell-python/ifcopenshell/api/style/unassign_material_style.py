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
import ifcopenshell.api.style
import ifcopenshell.util.element


def unassign_material_style(
    file: ifcopenshell.file,
    material: ifcopenshell.entity_instance,
    style: ifcopenshell.entity_instance,
    context: ifcopenshell.entity_instance,
) -> None:
    """Unassigns a style to a material

    This does the inverse of assign_material_style.

    :param material: The IfcMaterial which you want to unassign the style from.
    :type material: ifcopenshell.entity_instance
    :param style: The IfcPresentationStyle (typically IfcSurfaceStyle) that
        you want to unassign from material. This will then be applied to all
        objects that have that material.
    :type style: ifcopenshell.entity_instance
    :param context: The IfcGeometricRepresentationSubContext at which this
        style should be unassigned. Typically this is the Model BODY context.
    :type context: ifcopenshell.entity_instance
    :return: None
    :rtype: None

    Example:

    .. code:: python

        ifcopenshell.api.style.unassign_material_style(model, material=concrete, style=style, context=body)
    """
    settings = {
        "material": material,
        "style": style,
        "context": context,
    }

    for definition in settings["material"].HasRepresentation:
        for representation in definition.Representations:
            if not representation.is_a("IfcStyledRepresentation"):
                continue
            if representation.ContextOfItems != settings["context"]:
                continue
            for item in representation.Items:
                if not item.is_a("IfcStyledItem"):
                    continue
                styles = []
                for s in item.Styles:
                    if s == settings["style"]:
                        continue
                    if s.is_a("IfcPresentationStyleAssignment"):
                        if s.Styles == (settings["style"],):
                            continue
                    styles.append(s)
                if not styles:
                    file.remove(item)
                elif len(styles) != len(item.Styles):
                    item.Styles = styles
            if not representation.Items:
                file.remove(representation)
        if not definition.Representations:
            file.remove(definition)

    # handle material constituents and shape aspects
    material_constituents_names = []
    for inverse in file.get_inverse(settings["material"]):
        if inverse.is_a("IfcMaterialConstituent") and inverse.Name:
            material_constituents_names.append(inverse.Name)
    if not material_constituents_names:
        return

    elements = ifcopenshell.util.element.get_elements_by_material(file, settings["material"])
    shape_aspects = []
    for element in elements:
        shape_aspects += ifcopenshell.util.element.get_shape_aspects(element)

    for shape_aspect in shape_aspects:
        if shape_aspect.Name not in material_constituents_names:
            continue

        for rep in shape_aspect.ShapeRepresentations:
            ifcopenshell.api.style.unassign_representation_styles(
                file, shape_representation=rep, styles=[settings["style"]]
            )
