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
from typing import Optional


def add_material(
    file: ifcopenshell.file,
    name: Optional[str] = None,
    category: Optional[str] = None,
    description: Optional[str] = None,
) -> ifcopenshell.entity_instance:
    """Adds a new material

    A material in IFC represents a physical material, such as timber, steel,
    concrete, aluminium, etc. It may also contain physical properties used
    for structural or lighting simulation. Note that unlike the computer
    graphics industry, a material by itself does not define any colour or
    lighting information. Colours in IFC are known as "styles", and an IFC
    material may or may not have any style information associated with it.
    See ifcopenshell.api.style for more information.

    A material is typically given a code name which is used by architects in
    elevations and details when tagging finishes. Materials are also useful
    to structural engineers in specifying the exact types of concrete and
    steel to be used in structural simulations.

    In addition, materials can belong to a category. Specifying this
    category is critical to allow model recipients to make simple queries
    like "show me all concrete / steel" elements in the model. Without
    standardised category naming of all materials, this type of query
    becomes a bespoke and inefficient task. A list of categories are:
    'concrete', 'steel', 'aluminium', 'block', 'brick', 'stone', 'wood',
    'glass', 'gypsum', 'plastic', and 'earth'. The user is allowed to
    specify their own category instead if none of these categories are
    appropriate.

    Note that categories are not available in IFC2X3. This shortcoming is
    one of the big reasons projects should upgrade to IFC4.

    Additionally, a material's description provides more information beyond
    its name or category.

    :param name: The name of the material, typically tagged in a finishes
        drawing or schedule.
    :param category: The category of the material.
    :param description: A description of the material.
    :return: The newly created IfcMaterial

    Example:

    .. code:: python

        # Let's create two materials with their respective categories
        concrete = ifcopenshell.api.material.add_material(model, name="CON01", category="concrete", description="Garage Slab")
        steel = ifcopenshell.api.material.add_material(model, name="ST01", category="steel", description="Corten Steel")

        # Let's imagine an urban concrete bench which is purely made out of concrete
        concrete_bench = ifcopenshell.api.root.create_entity(model, ifc_class="IfcFurnitureType")

        # Assign the concrete material to that bench. Note that no colour
        # "Style" has been specified.
        ifcopenshell.api.material.assign_material(model, products=[concrete_bench], material=concrete)
    """
    material = file.create_entity("IfcMaterial", **{"Name": name or "Unnamed"})
    if category:
        material.Category = category
    if description:
        material.Description = description
    return material
