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

import ifcopenshell
import ifcopenshell.util.element


def remove_material_set(file: ifcopenshell.file, material: ifcopenshell.entity_instance) -> None:
    """Removes a material set

    All set items, such as layers, profiles, or constituents will also be
    removed. However, the materials and profile curves used by the layers,
    profiles and constituents will not be removed.

    :param material: The IfcMaterialLayerSet, IfcMaterialConstituentSet,
        IfcMaterialProfileSet entity you want to remove.
    :type material: ifcopenshell.entity_instance
    :return: None
    :rtype: None

    Example:

    .. code:: python

        # Create a material set
        material_set = ifcopenshell.api.material.add_material_set(model,
            name="GYP-ST-GYP", set_type="IfcMaterialLayerSet")

        # Create some materials
        gypsum = ifcopenshell.api.material.add_material(model, name="PB01", category="gypsum")
        steel = ifcopenshell.api.material.add_material(model, name="ST01", category="steel")

        # Add some layers
        layer = ifcopenshell.api.material.add_layer(model, layer_set=material_set, material=gypsum)
        layer = ifcopenshell.api.material.add_layer(model, layer_set=material_set, material=steel)
        layer = ifcopenshell.api.material.add_layer(model, layer_set=material_set, material=gypsum)

        # Completely delete the set and all layers. The gypsum and steel
        # material still exist, though.
        ifcopenshell.api.material.remove_material_set(model, material=material_set)
    """

    settings = {"material": material}

    inverse_elements = file.get_inverse(settings["material"])
    if settings["material"].is_a("IfcMaterialLayerSet"):
        set_items = settings["material"].MaterialLayers or []
    elif settings["material"].is_a("IfcMaterialProfileSet"):
        set_items = settings["material"].MaterialProfiles or []
    elif settings["material"].is_a("IfcMaterialConstituentSet"):
        set_items = settings["material"].MaterialConstituents or []
    elif settings["material"].is_a("IfcMaterialList"):
        set_items = []
    for set_item in set_items:
        file.remove(set_item)
    file.remove(settings["material"])
    for inverse in inverse_elements:
        if inverse.is_a("IfcRelAssociatesMaterial"):
            history = inverse.OwnerHistory
            file.remove(inverse)
            if history:
                ifcopenshell.util.element.remove_deep2(file, history)
        elif inverse.is_a("IfcMaterialProperties"):
            for prop in inverse.Properties or []:
                file.remove(prop)
            file.remove(inverse)
