# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2023 Dion Moult <dion@thinkmoult.com>
#
# This file is part of Bonsai.
#
# Bonsai is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Bonsai is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Bonsai.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import annotations
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    import bpy
    import ifcopenshell
    import bonsai.tool as tool


def purge_unused_profiles(ifc: tool.Ifc, profile: tool.Profile) -> int:
    """Purge profiles that have no inverses.

    :return: Number of removed profiles.
    """
    purged_profiles = 0
    for element_profile in profile.get_model_profiles():
        if ifc.get().get_total_inverses(element_profile) > 0:
            continue
        ifc.run("profile.remove_profile", profile=element_profile)
        purged_profiles += 1
    return purged_profiles
