# This file was generated with the assistance of an AI coding tool.
# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026
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

import ifcopenshell
import ifcopenshell.api.pset
import ifcopenshell.api.root

import bonsai.tool as tool
from bonsai.bim.module.search.data import ColourByPropertyData
from test.bim.bootstrap import NewFile


class TestColourschemeKey(NewFile):
    def test_lists_psets_of_the_whole_file_with_nothing_selected(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcProject")
        wall = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcWall")
        pset = ifcopenshell.api.pset.add_pset(ifc, product=wall, name="Pset_Foo")
        ifcopenshell.api.pset.edit_pset(ifc, pset=pset, properties={"Bar": "x"})

        keys = [item[0] for item in ColourByPropertyData.colourscheme_key() if item]

        assert '"Pset_Foo"."Bar"' in keys
