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
import ifcopenshell.api.pset
import ifcopenshell.util.element


def remove_profile(file: ifcopenshell.file, profile: ifcopenshell.entity_instance) -> None:
    """Removes a profile

    :param profile: The IfcProfileDef to remove.

    Example:

    .. code:: python

        circle = ifcopenshell.api.profile.add_parameterized_profile(model,
            ifc_class="IfcCircleProfileDef")
        circle = 1.
        ifcopenshell.api.profile.remove_profile(model, profile=circle)
    """
    is_ifc2x3 = file.schema == "IFC2X3"

    subelements = set()
    for attribute in profile:
        if isinstance(attribute, ifcopenshell.entity_instance):
            subelements.add(attribute)

    # Clean up profile proprty sets.
    profile_psets = []
    if is_ifc2x3:
        for pset in file.by_type("IfcProfileProperties"):
            if pset.ProfileDefinition != profile:
                continue
            profile_psets.append(pset)
    else:
        profile_psets = profile.HasProperties

    for pset in profile_psets:
        ifcopenshell.api.pset.remove_pset(file, product=profile, pset=pset)

    file.remove(profile)
    for subelement in subelements:
        ifcopenshell.util.element.remove_deep2(file, subelement)
