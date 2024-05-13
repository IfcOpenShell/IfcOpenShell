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


def copy_material(file: ifcopenshell.file, material: ifcopenshell.entity_instance) -> ifcopenshell.entity_instance:
    """Copies a material

    All material psets and styles are copied. The copied material is not
    associated to any elements.

    :param material: The IfcMaterial to copy
    :type material: ifcopenshell.entity_instance
    :return: The new copy of the material
    :rtype: ifcopenshell.entity_instance

    Example:

    .. code:: python

        concrete = ifcopenshell.api.run("material.add_material", model, name="CON01", category="concrete")

        # Let's duplicate the concrete material
        concrete_copy = ifcopenshell.api.run("material.copy_material", model, material=concrete)
    """
    settings = {"material": material}

    if settings["material"].is_a("IfcMaterial"):
        new = ifcopenshell.util.element.copy(file, settings["material"])
        for inverse in file.get_inverse(settings["material"]):
            if inverse.is_a("IfcMaterialProperties"):
                # Properties must not be shared between objects for convenience of authoring
                inverse = ifcopenshell.util.element.copy(file, inverse)
                inverse.Material = new

                props_attribute = "Properties"
                if file.schema == "IFC2X3":
                    if not inverse.is_a("IfcExtendedMaterialProperties"):
                        continue
                    props_attribute = "ExtendedProperties"

                props = getattr(inverse, props_attribute)
                if not props:
                    continue

                copied_props = []
                for pset in props:
                    copied_props.append(ifcopenshell.util.element.copy_deep(file, pset))
                setattr(inverse, props_attribute, copied_props)

            elif inverse.is_a("IfcMaterialDefinitionRepresentation"):
                inverse = ifcopenshell.util.element.copy_deep(
                    file, inverse, exclude=["IfcRepresentationContext", "IfcMaterial"]
                )
                inverse.RepresentedMaterial = new
        return new
