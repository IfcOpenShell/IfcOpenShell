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


def remove_constituent(file: ifcopenshell.file, constituent: ifcopenshell.entity_instance) -> None:
    """Removes a constituent from a constituent set

    Note that it is invalid to have zero items in a set, so you should leave
    at least one constituent to ensure a valid IFC dataset.

    :param constituent: The IfcMaterialConstituent entity you want to remove
    :type constituent: ifcopenshell.entity_instance
    :return: None
    :rtype: None

    Example:

    .. code:: python

        # Create a material set for windows made out of aluminium and glass.
        material_set = ifcopenshell.api.material.add_material_set(model,
            name="Window", set_type="IfcMaterialConstituentSet")

        aluminium = ifcopenshell.api.material.add_material(model, name="AL01", category="aluminium")
        glass = ifcopenshell.api.material.add_material(model, name="GLZ01", category="glass")

        # Now let's use those materials as two constituents in our set.
        framing = ifcopenshell.api.material.add_constituent(model,
            constituent_set=material_set, material=aluminium)
        glazing = ifcopenshell.api.material.add_constituent(model,
            constituent_set=material_set, material=glass)

        # Let's remove the glass constituent. Note that we should not remove
        # the framing, at this would mean there are no constituents which is
        # invalid.
        ifcopenshell.api.material.remove_constituent(model, constituent=glazing)
    """
    settings = {"constituent": constituent}

    file.remove(settings["constituent"])
