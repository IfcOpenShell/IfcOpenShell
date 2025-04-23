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


def add_list_item(
    file: ifcopenshell.file, material_list: ifcopenshell.entity_instance, material: ifcopenshell.entity_instance
) -> None:
    """Adds a new material in a list of materials

    In IFC2X3, if you wanted an object to have multiple materials (i.e. a
    composite material) you would assign the object to a material list,
    which would contain a list of materials. For example, a window might
    have a list of 2 materials, one being aluminium for the frame, and
    another being glass for the panel.

    In IFC4 and above, this is deprecated and should not be used. Instead,
    you should use constituent sets instead, which achieve the same thing
    but are more powerful as they allow you to define the properties of the
    constituents too.

    However if you're stuck on IFC2X3, you have my condolences as well as
    this function.

    :param material_list: The IfcMaterialList the material should be added
        to.
    :param material: The IfcMaterial to add to the list
    :return: None

    Example:

    .. code:: python

        # Let's imagine we have a window type that has an aluminium frame
        # and a glass glazing panel. Notice we are assigning to the type
        # only, as all occurrences of that type will automatically inherit
        # the material.
        window_type = ifcopenshell.api.root.create_entity(model, ifc_class="IfcWindowType")

        # First, let's create a list. This will later be assigned to our
        # window element.
        material_set = ifcopenshell.api.material.add_material_set(model,
            name="Window", set_type="IfcMaterialList")

        # Let's create a few materials, it's important to also give them
        # categories. This makes it easy for model recipients to do things
        # like "show me everything made out of aluminium / concrete / steel
        # / glass / etc". The IFC specification states a list of categories
        # you can use.
        aluminium = ifcopenshell.api.material.add_material(model, name="AL01", category="aluminium")
        glass = ifcopenshell.api.material.add_material(model, name="GLZ01", category="glass")

        # Now let's use those materials as two items in our list.
        ifcopenshell.api.material.add_list_item(model, material_list=material_set, material=aluminium)
        ifcopenshell.api.material.add_list_item(model, material_list=material_set, material=glass)

        # Great! Let's assign our material set to our window type.
        # We're technically not done here, we might want to add geometry to
        # our window too, but to keep this example simple, geometry is
        # optional and it is enough to say that this window is made out of
        # aluminium and glass.
        ifcopenshell.api.material.assign_material(model, products=[window_type], material=material_set)
    """
    materials = list(material_list.Materials or [])
    materials.append(material)
    material_list.Materials = materials
