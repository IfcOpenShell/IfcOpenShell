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


def copy_profile(file: ifcopenshell.file, profile: ifcopenshell.entity_instance) -> ifcopenshell.entity_instance:
    """Copies a profile

    All profile's psets are copied. The copied profile is not
    associated to any elements.

    :param profile: The IfcProfileDef to copy
    :return: The new copy of the profile

    Example:

    .. code:: python

        profile = ifcopenshell.api.profile.add_profile(model, ifc_class="IfcRectangleProfileDef")

        # Let's duplicate the rectangle profile
        profile_copy = ifcopenshell.api.profile.copy_profile(model, profile=profile)
    """
    new_profile = ifcopenshell.util.element.copy_deep(file, profile)
    inverses = file.get_inverse(profile)
    psets = [i for i in inverses if i.is_a("IfcProfileProperties")]
    for pset in psets:
        new_pset = ifcopenshell.util.element.copy(file, pset)
        new_pset.ProfileDefinition = new_profile
    return new_profile
