# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
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
import ifcopenshell.api.material
import ifcopenshell.util.element
import ifcopenshell.util.representation


def set_shape_aspect_constituents(
    file: ifcopenshell.file,
    *,
    element: ifcopenshell.entity_instance,
    context: ifcopenshell.entity_instance,
    materials: dict[str, ifcopenshell.entity_instance],
) -> None:
    """Assigns a material constituent set and sets styles based on shape aspects

    An IFC element may be assigned to a set of material constituents. For
    example, a window may have a framing material and a glazing material. Each
    constituent may have a name, such as "Framing" (which may be assigned to an
    "Aluminium" material), and "Glazing" (assigned to a "Laminated Low-e Glass"
    material).

    An IFC element's geometry may be composed of multiple geometric items.
    These geometric items may have names, known as "Shape Aspects".  For
    example a solid extrusion for the framing named "Framing" and a solid
    extrusion for the glass panel named "Glazing".

    A material may be associated with a style (i.e. colour). For example, a
    grey style for the "Aluminium" material and a transparent blue style for
    the "Laminated Low-e Glass" material.

    These three concepts of material constituents, shape aspects, and
    associated styles are correlated. For example, if the name (e.g. "Framing")
    of a material constituent and a shape aspect correlate, that means that the
    geometric item inherits the style (i.e. grey).

    This function lets you specify named material constituents, and it'll
    create a constituent set assigned to the element with those names. It'll
    then find any geometric representation items with shape aspects matching
    those names, and assign the correlating style.

    If an assigned material constituent set already exists matching those
    values, it will be reused. If the values do not match, the existing
    material constituent set will be removed if it is not used by anything
    else.

    :param element: The IfcProduct or IfcTypeProduct
    :param context: The IfcGeometricRepresentationContext, typically the body
        context. You can get this via
        :func:`ifcopenshell.util.representation.get_context`.
    :param materials: The key is the name of the constituent, and the value is
        the IfcMaterial.

    Example:

    .. code:: python

        # Create two materials
        aluminium = ifcopenshell.api.material.add_material(model, name="AL01", category="aluminium")
        glass = ifcopenshell.api.material.add_material(model, name="GLZ01", category="glass")

        # Auto assign material constituents and styles to items based on shape aspects
        ifcopenshell.api.material.set_shape_aspect_constituents(
            model, element=window, context=body, materials={
                "Framing": aluminium
                "Lining": aluminium
                "Glazing": glass
            })
    """
    should_create_new_material_set = False
    if material := ifcopenshell.util.element.get_material(element):
        if (
            material.is_a("IfcMaterialConstituent")
            and len(names := [c.Name for c in material.MaterialConstituents]) == len(materials)
            and set(names) == set(materials.keys())
        ):
            should_create_new_material_set = False
        else:
            should_create_new_material_set = True
            ifcopenshell.api.material.unassign_material(file, products=[element])
            if not material.is_a("IfcMaterial") and not file.get_total_inverses(material):
                ifcopenshell.api.material.remove_material_set(file, material=material)
    else:
        should_create_new_material_set = True
    if should_create_new_material_set:
        material_set = ifcopenshell.api.material.add_material_set(file, set_type="IfcMaterialConstituentSet")
        for name, material in materials.items():
            ifcopenshell.api.material.add_constituent(file, constituent_set=material_set, material=material, name=name)
        ifcopenshell.api.material.assign_material(file, products=[element], material=material_set)

    styles = {n: ifcopenshell.util.representation.get_material_style(m, context) for n, m in materials.items()}
    representation = ifcopenshell.util.representation.get_representation(element, context=context)
    representation = ifcopenshell.util.representation.resolve_representation(representation)
    for item in representation.Items:
        if aspect := ifcopenshell.util.representation.get_item_shape_aspect(representation, item):
            if style := styles.get(aspect.Name, None):
                ifcopenshell.api.style.assign_item_style(file, item=item, style=style)
