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

import test.bootstrap
import ifcopenshell.api.pset_template


class TestEditPropTemplate(test.bootstrap.IFC4):
    def test_editing_a_simple_template(self):
        template = ifcopenshell.api.pset_template.add_pset_template(self.file, name="ABC_RiskFactors")
        prop = ifcopenshell.api.pset_template.add_prop_template(self.file, pset_template=template)
        ifcopenshell.api.pset_template.edit_prop_template(
            self.file,
            prop_template=prop,
            attributes={"Name": "DemoA", "PrimaryMeasureType": "IfcLabel"},
        )
        ifcopenshell.api.pset_template.edit_prop_template(self.file, prop_template=prop, attributes={"Name": "DemoB"})
        assert prop.Name == "DemoB"

    def test_editing_an_enumeration(self):
        template = ifcopenshell.api.pset_template.add_pset_template(self.file, name="ABC_RiskFactors")
        prop = ifcopenshell.api.pset_template.add_prop_template(self.file, pset_template=template)
        ifcopenshell.api.pset_template.edit_prop_template(
            self.file,
            prop_template=prop,
            attributes={"Name": "DemoA", "PrimaryMeasureType": "IfcLabel"},
        )
        ifcopenshell.api.pset_template.edit_prop_template(
            self.file,
            prop_template=prop,
            attributes={"Enumerators": ["FOO", "BAR"]},
        )
        assert prop.Enumerators.EnumerationValues == tuple(self.file.createIfcLabel(v) for v in ("FOO", "BAR"))
        ifcopenshell.api.pset_template.edit_prop_template(
            self.file,
            prop_template=prop,
            attributes={"Name": "DemoC", "Enumerators": ["BAZ", "BAR"]},
        )
        assert prop.Enumerators.Name == "DemoC"
        assert prop.Enumerators.EnumerationValues == tuple(self.file.createIfcLabel(v) for v in ("BAZ", "BAR"))
        assert len(self.file.by_type("IfcPropertyEnumeration")) == 1
