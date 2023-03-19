# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of BlenderBIM Add-on.
#
# BlenderBIM Add-on is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BlenderBIM Add-on is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with BlenderBIM Add-on.  If not, see <http://www.gnu.org/licenses/>.

import bpy
import ifcopenshell
import blenderbim.core.tool
import blenderbim.tool as tool
from blenderbim.tool.pset import Pset as subject
from test.bim.bootstrap import NewFile


class TestImplementsTool(NewFile):
    def test_run(self):
        assert isinstance(subject(), blenderbim.core.tool.Pset)


class TestGetElementPset(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        element = ifc.createIfcWall()
        pset = ifcopenshell.api.run("pset.add_pset", ifc, product=element, name="Foo")
        assert subject.get_element_pset(element, "Foo") == pset


class TestIsPsetEmpty(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        element = ifc.createIfcWall()
        pset = ifcopenshell.api.run("pset.add_pset", ifc, product=element, name="Foo")
        assert subject.is_pset_empty(pset) is True
        ifcopenshell.api.run("pset.edit_pset", ifc, pset=pset, properties={"Foo": "Bar"})
        assert subject.is_pset_empty(pset) is False
        ifcopenshell.api.run("pset.edit_pset", ifc, pset=pset, properties={"Foo": None})
        assert subject.is_pset_empty(pset) is True
