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


class Usecase:
    def __init__(self, file, material=None):
        """Removes a material set

        All set items, such as layers, profiles, or constituents will also be
        removed. However, the materials and profile curves used by the layers,
        profiles and constituents will not be removed.

        :param material: The IfcMaterialLayerSet, IfcMaterialConstituentSet,
            IfcMaterialProfileSet entity you want to remove.
        :type material: ifcopenshell.entity_instance.entity_instance
        :return: None
        :rtype: None

        Example:

        .. code:: python

            # Create a material set
            material_set = ifcopenshell.api.run("material.add_material_set", model,
                name="GYP-ST-GYP", set_type="IfcMaterialLayerSet")

            # Create some materials
            gypsum = ifcopenshell.api.run("material.add_material", model, name="PB01", category="gypsum")
            steel = ifcopenshell.api.run("material.add_material", model, name="ST01", category="steel")

            # Add some layers
            layer = ifcopenshell.api.run("material.add_layer", model, layer_set=material_set, material=gypsum)
            layer = ifcopenshell.api.run("material.add_layer", model, layer_set=material_set, material=steel)
            layer = ifcopenshell.api.run("material.add_layer", model, layer_set=material_set, material=gypsum)

            # Completely delete the set and all layers. The gypsum and steel
            # material still exist, though.
            ifcopenshell.api.run("material.remove_material_set", model, material=material_set)
        """

        self.file = file
        self.settings = {"material": material}

    def execute(self):
        inverse_elements = self.file.get_inverse(self.settings["material"])
        if self.settings["material"].is_a("IfcMaterialLayerSet"):
            set_items = self.settings["material"].MaterialLayers or []
        elif self.settings["material"].is_a("IfcMaterialProfileSet"):
            set_items = self.settings["material"].MaterialProfiles or []
        elif self.settings["material"].is_a("IfcMaterialConstituentSet"):
            set_items = self.settings["material"].MaterialConstituents or []
        elif self.settings["material"].is_a("IfcMaterialList"):
            set_items = []
        for set_item in set_items:
            self.file.remove(set_item)
        self.file.remove(self.settings["material"])
        for inverse in inverse_elements:
            if inverse.is_a("IfcRelAssociatesMaterial"):
                self.file.remove(inverse)
            elif inverse.is_a("IfcMaterialProperties"):
                for prop in inverse.Properties or []:
                    self.file.remove(prop)
                self.file.remove(inverse)
