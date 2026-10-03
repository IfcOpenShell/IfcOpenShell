# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2024 Dion Moult <dion@thinkmoult.com>
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

# This file was generated with the assistance of an AI coding tool.

import ifcopenshell
import ifcopenshell.api.material


def merge_materials(
    file: ifcopenshell.file,
    materials: list[ifcopenshell.entity_instance],
    merge_into: ifcopenshell.entity_instance,
) -> None:
    """Merges one or more redundant materials into a single designated material

    This is typically used to clean up models (often from import processes)
    that end up with many duplicate or near-duplicate IfcMaterial
    definitions. Every product, type, material layer, material profile,
    material constituent, and material list item that currently references
    one of `materials` will be repointed to `merge_into` instead. Once a
    material has no more references, it is removed, along with any
    properties or styles that belonged only to that redundant material (the
    definition of `merge_into` "wins").

    If `merge_into` is included in `materials`, it is simply skipped, so it
    is safe to pass the designated material as part of a "select all, merge"
    workflow.

    :param materials: The list of redundant IfcMaterial entities to merge and
        remove.
    :param merge_into: The IfcMaterial entity that should be used instead of
        all of `materials`.
    :return: None

    Example:

    .. code:: python

        # Two suspiciously similar materials, perhaps from a bad import.
        m1 = ifcopenshell.api.material.add_material(model, name="Concrete")
        m2 = ifcopenshell.api.material.add_material(model, name="Concrete_2")

        wall1 = ifcopenshell.api.root.create_entity(model, ifc_class="IfcWall")
        wall2 = ifcopenshell.api.root.create_entity(model, ifc_class="IfcWall")
        ifcopenshell.api.material.assign_material(model, products=[wall1], material=m1)
        ifcopenshell.api.material.assign_material(model, products=[wall2], material=m2)

        # Both walls will now use m1, and m2 will no longer exist.
        ifcopenshell.api.material.merge_materials(model, materials=[m1, m2], merge_into=m1)
    """
    materials_to_remove = [m for m in materials if m != merge_into]
    if not materials_to_remove:
        return

    for material in materials_to_remove:
        # Repoint any direct "this product is made of this material" relationship.
        rel = next(
            (
                r
                for r in file.get_inverse(material)
                if r.is_a("IfcRelAssociatesMaterial") and r.RelatingMaterial == material
            ),
            None,
        )
        if rel is not None and rel.RelatedObjects:
            ifcopenshell.api.material.assign_material(
                file, products=list(rel.RelatedObjects), type="IfcMaterial", material=merge_into
            )

        # Repoint material set membership (layers, profiles, constituents, lists).
        for inverse in file.get_inverse(material):
            if (
                inverse.is_a("IfcMaterialLayer")
                or inverse.is_a("IfcMaterialProfile")
                or inverse.is_a("IfcMaterialConstituent")
            ):
                inverse.Material = merge_into
            elif inverse.is_a("IfcMaterialList"):
                new_materials = []
                for item in inverse.Materials or []:
                    item = merge_into if item == material else item
                    if item not in new_materials:
                        new_materials.append(item)
                inverse.Materials = new_materials

        # Whatever is left (e.g. properties or a style definition that
        # belonged only to this now-redundant material) is discarded along
        # with the material itself.
        ifcopenshell.api.material.remove_material(file, material=material)
