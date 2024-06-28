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


def add_constituent(
    file: ifcopenshell.file, constituent_set: ifcopenshell.entity_instance, material: ifcopenshell.entity_instance
) -> ifcopenshell.entity_instance:
    """Adds a new constituent to a constituent set

    A constituent describes how a portion of an object is made out of a
    material whereas other portions of the object is made out of other
    materials. For example, a window might be made out of an aluminium frame
    and a glass panel. The aluminium used for the frame is one constituent
    of the material, and glass would be another constituent. Another example
    might be concrete, where one constituent might be cement, and another
    constituent might be binder. In the case of the window, the constituent
    is represented explicitly by the geometry of the window frame and the
    geometry of the window panel. In the case of a concrete slab, the
    constituents might be represented in terms of percentages.

    Constituents are not available in IFC2X3.

    :param constituent_set: The IfcMaterialConstituentSet that the
        constituent is part of. The constituent set represents a group of
        constituents. See ifcopenshell.api.material.add_material_set for
        information on how to add a constituent set.
    :type constituent_set: ifcopenshell.entity_instance
    :param material: The IfcMaterial that the constituent is made out of.
    :type material: ifcopenshell.entity_instance
    :return: The newly created IfcMaterialConstituent
    :rtype: ifcopenshell.entity_instance

    Example:

    .. code:: python

        # Let's imagine we have a window type that has an aluminium frame
        # and a glass glazing panel. Notice we are assigning to the type
        # only, as all occurrences of that type will automatically inherit
        # the material.
        window_type = ifcopenshell.api.root.create_entity(model, ifc_class="IfcWindowType")

        # First, let's create a constituent set. This will later be assigned
        # to our window element.
        material_set = ifcopenshell.api.material.add_material_set(model,
            name="Window", set_type="IfcMaterialConstituentSet")

        # Let's create a few materials, it's important to also give them
        # categories. This makes it easy for model recipients to do things
        # like "show me everything made out of aluminium / concrete / steel
        # / glass / etc". The IFC specification states a list of categories
        # you can use.
        aluminium = ifcopenshell.api.material.add_material(model, name="AL01", category="aluminium")
        glass = ifcopenshell.api.material.add_material(model, name="GLZ01", category="glass")

        # Now let's use those materials as two constituents in our set.
        ifcopenshell.api.material.add_constituent(model,
            constituent_set=material_set, material=aluminium)
        ifcopenshell.api.material.add_constituent(model,
            constituent_set=material_set, material=glass)

        # Great! Let's assign our material set to our window type.
        # We're technically not done here, we might want to add geometry to
        # our window too, but to keep this example simple, geometry is
        # optional and it is enough to say that this window is made out of
        # aluminium and glass.
        ifcopenshell.api.material.assign_material(model, products=[window_type], material=material_set)
    """
    settings = {"constituent_set": constituent_set, "material": material}

    constituents = list(settings["constituent_set"].MaterialConstituents or [])
    constituent = file.create_entity("IfcMaterialConstituent", **{"Material": settings["material"]})
    constituents.append(constituent)
    settings["constituent_set"].MaterialConstituents = constituents
    return constituent
