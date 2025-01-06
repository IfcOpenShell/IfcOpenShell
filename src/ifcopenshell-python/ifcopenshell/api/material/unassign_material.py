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
import ifcopenshell.api.owner
import ifcopenshell.util.element


def unassign_material(file: ifcopenshell.file, products: list[ifcopenshell.entity_instance]) -> None:
    """Removes any material relationship with the list of products

    A product can only have one material assigned to it, which is why it is
    not necessary to specify the material to unassign. The material is not
    removed, only the relationship is removed.

    If the product does not have a material, nothing happens.

    :param products: The list IfcProducts that may or may not have a material
    :type product: list[ifcopenshell.entity_instance]
    :return: None
    :rtype: None

    Example:

    .. code:: python

        concrete = ifcopenshell.api.material.add_material(model, name="CON01", category="concrete")

        # Let's imagine a concrete bench made out of concrete.
        bench_type = ifcopenshell.api.root.create_entity(model, ifc_class="IfcFurnitureType")
        ifcopenshell.api.material.assign_material(model,
            products=[bench_type], type="IfcMaterial", material=concrete)

        # Let's change our mind and remove the concrete assignment. The
        # concrete material still exists, but the bench is no longer made
        # out of concrete now.
        ifcopenshell.api.material.unassign_material(model, products=[bench_type])
    """
    usecase = Usecase()
    usecase.file = file
    usecase.settings = {"products": products}
    return usecase.execute()


class Usecase:
    def execute(self):
        self.products = set(self.settings["products"])
        if not self.products:
            return

        self.remove_material_usages_from_types()
        self.unassign_materials()

    def remove_material_usages_from_types(self) -> None:
        # remove material usages from types
        for product in self.products:
            if not product.is_a("IfcTypeObject"):
                continue
            material = ifcopenshell.util.element.get_material(product)
            if not material:
                continue
            if material.is_a() in ["IfcMaterialLayerSet", "IfcMaterialProfileSet"]:
                # Remove set usages
                for inverse in self.file.get_inverse(material):
                    if self.file.schema == "IFC2X3":
                        if not inverse.is_a("IfcMaterialLayerSetUsage"):
                            continue
                        # in IFC2X3 there is no .AssociatedTo
                        for inverse2 in self.file.get_inverse(inverse):
                            if inverse2.is_a("IfcRelAssociatesMaterial"):
                                history = inverse2.OwnerHistory
                                self.file.remove(inverse2)
                                if history:
                                    ifcopenshell.util.element.remove_deep2(self.file, history)
                    else:
                        if not inverse.is_a("IfcMaterialUsageDefinition"):
                            continue
                        for rel in inverse.AssociatedTo:
                            history = rel.OwnerHistory
                            self.file.remove(rel)
                            if history:
                                ifcopenshell.util.element.remove_deep2(self.file, history)
                    self.file.remove(inverse)

    def unassign_materials(self) -> None:
        associations: set[ifcopenshell.entity_instance] = set()
        for product in self.products:
            associations.update(product.HasAssociations)

        # we ensure that `associations` won't have removed elements
        # to avoid crash during `material_inverses.issubset(associations)`
        while associations:
            rel = next(iter(associations))

            if not rel.is_a("IfcRelAssociatesMaterial"):
                associations.remove(rel)
            else:
                material = rel.RelatingMaterial
                related_objects = set(rel.RelatedObjects) - self.products

                if material.is_a() in ["IfcMaterialLayerSetUsage", "IfcMaterialProfileSetUsage"]:
                    # Warning: this may leave the model in a non-compliant state.
                    material_inverses = set(self.file.get_inverse(material))
                    if material_inverses.issubset(associations) and not related_objects:
                        self.file.remove(material)
                associations.remove(rel)

                if not related_objects:
                    history = rel.OwnerHistory
                    self.file.remove(rel)
                    if history:
                        ifcopenshell.util.element.remove_deep2(self.file, history)
                    continue
                rel.RelatedObjects = list(related_objects)
                ifcopenshell.api.owner.update_owner_history(self.file, **{"element": rel})
