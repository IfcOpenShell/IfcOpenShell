# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
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
import ifcopenshell.api
import ifcopenshell.api.pset

import bonsai.core.tool
import bonsai.tool as tool
from bonsai.tool.pset_template import PsetTemplate as subject
from test.bim.bootstrap import NewFile


class TestImplementsTool(NewFile):
    def test_run(self):
        assert isinstance(subject(), bonsai.core.tool.PsetTemplate)


class TestAddPsetAsTemplate(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        element1 = ifc.createIfcWall()
        element2 = ifc.createIfcWall()
        pset = ifcopenshell.api.pset.add_pset(ifc, product=element1, name="Foo")
        prop = ifcopenshell.api.pset.edit_pset(ifc, pset=pset, properties={"Foo": "a"})
        pset = ifcopenshell.api.pset.add_pset(ifc, product=element2, name="Foo")
        prop = ifcopenshell.api.pset.edit_pset(ifc, pset=pset, properties={"Bar": "b"})
        library = ifcopenshell.file()
        assert (pset_template := subject.add_pset_as_template("Foo", library))
        assert pset_template.is_a("IfcPropertySetTemplate")
        assert len(templates := pset_template.HasPropertyTemplates) == 2
        assert set(t.Name for t in templates) == {"Foo", "Bar"}
