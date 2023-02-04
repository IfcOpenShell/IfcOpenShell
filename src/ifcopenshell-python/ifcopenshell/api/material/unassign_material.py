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
    def __init__(self, file, product=None):
        """Removes any material relationship with a product

        A product can only have one material assigned to it, which is why it is
        not necessary to specify the material to unassign. The material is not
        removed, only the relationship is removed.

        If the product does not have a material, nothing happens.

        :param product: The IfcProduct that may or may not have a material
        :type product: ifcopenshell.entity_instance.entity_instance
        :return: None
        :rtype: None

        Example:

        .. code:: python

            concrete = ifcopenshell.api.run("material.add_material", model, name="CON01", category="concrete")

            # Let's imagine a concrete bench made out of concrete.
            bench_type = ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcFurnitureType")
            ifcopenshell.api.run("material.assign_material", model,
                product=bench_type, type="IfcMaterial", material=concrete)

            # Let's change our mind and remove the concrete assignment. The
            # concrete material still exists, but the bench is no longer made
            # out of concrete now.
            ifcopenshell.api.run("material.unassign_material", model, product=bench_type)
        """
        self.file = file
        self.settings = {"product": product}

    def execute(self):
        if self.settings["product"].is_a("IfcTypeObject"):
            material = ifcopenshell.util.element.get_material(self.settings["product"])
            if material.is_a() in ["IfcMaterialLayerSet", "IfcMaterialProfileSet"]:
                for inverse in self.file.get_inverse(material):
                    if self.file.schema == "IFC2X3":
                        if not inverse.is_a("IfcMaterialLayerSetUsage"):
                            continue
                        for inverse2 in self.file.get_inverse(inverse):
                            if inverse2.is_a("IfcRelAssociatesMaterial"):
                                self.file.remove(inverse2)
                    else:
                        if not inverse.is_a("IfcMaterialUsageDefinition"):
                            continue
                        for rel in inverse.AssociatedTo:
                            self.file.remove(rel)
                    self.file.remove(inverse)

        for rel in self.settings["product"].HasAssociations:
            if rel.is_a("IfcRelAssociatesMaterial"):
                if rel.RelatingMaterial.is_a() in ["IfcMaterialLayerSetUsage", "IfcMaterialProfileSetUsage"]:
                    # Warning: this may leave the model in a non-compliant state.
                    self.file.remove(rel.RelatingMaterial)
                if len(rel.RelatedObjects) == 1:
                    self.file.remove(rel)
                    continue
                related_objects = set(rel.RelatedObjects)
                related_objects.remove(self.settings["product"])
                rel.RelatedObjects = list(related_objects)
