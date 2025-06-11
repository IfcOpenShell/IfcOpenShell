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
from typing import Optional, Any


def edit_constituent(
    file: ifcopenshell.file,
    constituent: ifcopenshell.entity_instance,
    attributes: Optional[dict[str, Any]] = None,
    material: Optional[ifcopenshell.entity_instance] = None,
) -> None:
    """Edits the attributes of an IfcMaterialConstituent

    For more information about the attributes and data types of an
    IfcMaterialConstituent, consult the IFC documentation.

    :param constituent: The IfcMaterialConstituent entity you want to edit
    :param attributes: a dictionary of attribute names and values.
    :param material: The IfcMaterial entity you want to change the constituent to
    :return: None

    Example:

    .. code:: python

        # Let's add two materials
        aluminium1 = ifcopenshell.api.material.add_material(model, name="AL01", category="aluminium")
        aluminium2 = ifcopenshell.api.material.add_material(model, name="AL02", category="aluminium")
        glass = ifcopenshell.api.material.add_material(model, name="GLZ01", category="glass")

        material_set = ifcopenshell.api.material.add_material_set(model,
            name="Window", set_type="IfcMaterialConstituentSet")

        # Set up two constituents, one for the frame and the other for the glazing.
        framing = ifcopenshell.api.material.add_constituent(model,
            constituent_set=material_set, material=aluminium1)
        glazing = ifcopenshell.api.material.add_constituent(model,
            constituent_set=material_set, material=glass)

        # Let's make sure this constituent refers to the framing of the
        # window and uses the second aluminium material instead.
        ifcopenshell.api.material.edit_constituent(model,
            constituent=framing, attributes={"Name": "Framing"}, material=aluminium2)

        ifcopenshell.api.material.edit_constituent(model,
            constituent=constituent, attributes={"Name": "Glazing"})
    """
    for name, value in (attributes or {}).items():
        setattr(constituent, name, value)
    constituent.Material = material
