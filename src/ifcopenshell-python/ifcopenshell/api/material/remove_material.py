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


def remove_material(file: ifcopenshell.file, material: ifcopenshell.entity_instance) -> None:
    """Removes a material

    If the material is used in a material set, the corresponding layer,
    profile, or constituent is also removed. Note that this may result in a
    material set with zero items in it, which is invalid, so the user must
    take care of this situation themselves.

    :param material: The IfcMaterial entity you want to remove
    :return: None

    Example:

    .. code:: python

        # Create a material
        aluminium = ifcopenshell.api.material.add_material(model, name="AL01", category="aluminium")

        # ... and remove it
        ifcopenshell.api.material.remove_material(model, material=aluminium)
    """
    inverse_elements = file.get_inverse(material)
    file.remove(material)
    # TODO: Right now, we we choose only to delete set items (e.g. a layer) but not the material set
    # This can lead to invalid material sets, but we assume the user will deal with it
    for inverse in inverse_elements:
        if inverse.is_a("IfcMaterialConstituent"):
            file.remove(inverse)
        elif inverse.is_a("IfcMaterialLayer"):
            file.remove(inverse)
        elif inverse.is_a("IfcMaterialProfile"):
            file.remove(inverse)
        elif inverse.is_a("IfcRelAssociatesMaterial"):
            history = inverse.OwnerHistory
            file.remove(inverse)
            if history:
                ifcopenshell.util.element.remove_deep2(file, history)
        elif inverse.is_a("IfcMaterialProperties"):
            if file.schema != "IFC2X3":
                props = inverse.Properties
            else:
                # only IfcExtendedMaterialProperties have properties in IFC2X3
                props = getattr(inverse, "ExtendedProperties", None)
            props = props or []
            for prop in props:
                file.remove(prop)
            file.remove(inverse)
        elif inverse.is_a("IfcMaterialDefinitionRepresentation"):
            for representation in inverse.Representations:
                for item in representation.Items:
                    file.remove(item)
                file.remove(representation)
            file.remove(inverse)
