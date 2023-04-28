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
import ifcopenshell.util.element


class Usecase:
    def __init__(self, file, material=None):
        """Copies a material

        All material psets and styles are copied. The copied material is not
        associated to any elements.

        :param material: The IfcMaterial to copy
        :type material: ifcopenshell.entity_instance.entity_instance
        :return: The new copy of the material
        :rtype: ifcopenshell.entity_instance.entity_instance

        Example:

        .. code:: python

            concrete = ifcopenshell.api.run("material.add_material", model, name="CON01", category="concrete")

            # Let's duplicate the concrete material
            concrete_copy = ifcopenshell.api.run("material.copy_material", model, material=concrete)
        """
        self.file = file
        self.settings = {"material": material}

    def execute(self):
        if self.settings["material"].is_a("IfcMaterial"):
            new = ifcopenshell.util.element.copy(self.file, self.settings["material"])
            for inverse in self.file.get_inverse(self.settings["material"]):
                if inverse.is_a("IfcMaterialProperties"):
                    # Properties must not be shared between objects for convenience of authoring
                    inverse = ifcopenshell.util.element.copy(self.file, inverse)
                    properties = []
                    for pset in inverse.Properties:
                        properties.append(ifcopenshell.util.element.copy_deep(self.file, pset))
                    inverse.Properties = properties
                    inverse.Material = new
                elif inverse.is_a("IfcMaterialDefinitionRepresentation"):
                    inverse = ifcopenshell.util.element.copy_deep(
                        self.file, inverse, exclude=["IfcRepresentationContext", "IfcMaterial"]
                    )
                    inverse.RepresentedMaterial = new
            return new
