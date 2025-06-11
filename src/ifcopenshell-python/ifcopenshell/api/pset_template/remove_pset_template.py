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

import ifcopenshell.util.element


def remove_pset_template(file: ifcopenshell.file, pset_template: ifcopenshell.entity_instance) -> None:
    """Removes a property set template

    All property templates within the property set template are also removed
    along with it.

    :param pset_template: The IfcPropertySetTemplate to remove.
    :return: None

    Example:

    .. code:: python

        # Create a template.
        template = ifcopenshell.api.pset_template.add_pset_template(model, name="ABC_RiskFactors")

        # Let's remove the template.
        ifcopenshell.api.pset_template.remove_pset_template(model, pset_template=template)
    """
    ifcopenshell.util.element.remove_deep(file, pset_template)
