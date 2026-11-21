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

import ifcopenshell
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

    def test_ifc4x3_specification_and_null_nominal_value(self):
        ifc = ifcopenshell.file(schema="IFC4X3_ADD2")
        tool.Ifc.set(ifc)
        element = ifc.createIfcWall()
        pset = ifcopenshell.api.pset.add_pset(ifc, product=element, name="Pset_Custom")
        ifcopenshell.api.pset.edit_pset(ifc, pset=pset, properties={"PropA": "ValueA"})
        pset.HasProperties[0].Specification = "IFC4X3 spec text"
        prop_b = ifc.create_entity("IfcPropertySingleValue", Name="PropB", Specification="Null nominal")
        pset.HasProperties = list(pset.HasProperties) + [prop_b]

        library = ifcopenshell.file()
        pset_template = subject.add_pset_as_template("Pset_Custom", library)
        assert pset_template.is_a("IfcPropertySetTemplate")
        templates = {t.Name: t for t in pset_template.HasPropertyTemplates}
        assert set(templates.keys()) == {"PropA", "PropB"}
        assert templates["PropA"].Description == "IFC4X3 spec text"
        assert templates["PropA"].PrimaryMeasureType == "IfcLabel"
        assert templates["PropB"].Description == "Null nominal"
        assert templates["PropB"].PrimaryMeasureType == "IfcLabel"

