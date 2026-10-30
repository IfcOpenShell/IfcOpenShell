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
from typing import Any

import ifcopenshell


def edit_reference(
    file: ifcopenshell.file, reference: ifcopenshell.entity_instance, attributes: dict[str, Any]
) -> None:
    """Edits the attributes of an IfcClassificationReference

    For more information about the attributes and data types of an
    IfcClassificationReference, consult the IFC documentation.

    :param reference: The IfcClassificationReference entity you want to edit
    :param attributes: a dictionary of attribute names and values.
    :return: None

    Example:

    .. code:: python

        wall_type = ifcopenshell.api.root.create_entity(model, ifc_class="IfcWallType")
        classification = ifcopenshell.api.classification.add_classification(model,
            classification="MyCustomClassification")
        reference = ifcopenshell.api.classification.add_reference(model,
            products=[wall_type], classification=classification,
            identification="W_01", name="Interior Walls")
        # Change the name of the reference to "Foo"
        ifcopenshell.api.classification.edit_reference(model,
            reference=reference, attributes={"Name": "Foo"})
    """
    for name, value in attributes.items():
        setattr(reference, name, value)
