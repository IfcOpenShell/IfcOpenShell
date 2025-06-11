# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
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

import bpy
import ifcopenshell
import ifcopenshell.util.date
import ifcopenshell.util.classification
import bonsai.tool as tool
from bonsai.bim.ifc import IfcStore


def refresh():
    BSDDData.is_loaded = False


class BSDDData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.is_loaded = True
        cls.data["active_dictionary"] = cls.active_dictionary()

    @classmethod
    def active_dictionary(cls):
        props = tool.Bsdd.get_bsdd_props()
        results = [("ALL", "All Dictionaries", "All active dictionaries")]
        results.extend([(d.uri, d.name, f"{d.status} - {d.version}") for d in props.dictionaries if d.is_active])
        return results
