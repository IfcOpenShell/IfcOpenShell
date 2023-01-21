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


class Usecase:
    def __init__(self, file, material=None):
        """Removes a material

        If the material is used in a material set, the corresponding layer,
        profile, or constituent is also removed. Note that this may result in a
        material set with zero items in it, which is invalid, so the user must
        take care of this situation themselves.

        :param material: The IfcMaterial entity you want to remove
        :type material: ifcopenshell.entity_instance.entity_instance
        :return: None
        :rtype: None

        Example:

        .. code:: python

            # Create a material
            aluminium = ifcopenshell.api.run("material.add_material", model, name="AL01", category="aluminium")

            # ... and remove it
            ifcopenshell.api.run("material.remove_material", model, material=aluminium)
        """
        self.file = file
        self.settings = {"material": material}

    def execute(self):
        inverse_elements = self.file.get_inverse(self.settings["material"])
        self.file.remove(self.settings["material"])
        # TODO: Right now, we we choose only to delete set items (e.g. a layer) but not the material set
        # This can lead to invalid material sets, but we assume the user will deal with it
        for inverse in inverse_elements:
            if inverse.is_a("IfcMaterialConstituent"):
                self.file.remove(inverse)
            elif inverse.is_a("IfcMaterialLayer"):
                self.file.remove(inverse)
            elif inverse.is_a("IfcMaterialProfile"):
                self.file.remove(inverse)
            elif inverse.is_a("IfcRelAssociatesMaterial"):
                self.file.remove(inverse)
            elif inverse.is_a("IfcMaterialProperties"):
                for prop in inverse.Properties or []:
                    self.file.remove(prop)
                self.file.remove(inverse)
            elif inverse.is_a("IfcMaterialDefinitionRepresentation"):
                for representation in inverse.Representations:
                    for item in representation.Items:
                        self.file.remove(item)
                    self.file.remove(representation)
                self.file.remove(inverse)
