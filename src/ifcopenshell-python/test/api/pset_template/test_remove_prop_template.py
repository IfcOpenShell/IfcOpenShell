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

import ifcopenshell.api.pset_template
import test.bootstrap


class TestRemovePropTemplate(test.bootstrap.IFC4):
    def test_removing_a_prop_template(self):
        template = ifcopenshell.api.pset_template.add_pset_template(self.file, name="ABC_RiskFactors")
        prop1 = ifcopenshell.api.pset_template.add_prop_template(self.file, pset_template=template)
        prop2 = ifcopenshell.api.pset_template.add_prop_template(self.file, pset_template=template)
        ifcopenshell.api.pset_template.remove_prop_template(self.file, prop_template=prop2)
        assert len(self.file.by_type("IfcSimplePropertyTemplate")) == 1
        assert template.HasPropertyTemplates == (prop1,)

    def test_not_removing_the_last_prop_template(self):
        template = ifcopenshell.api.pset_template.add_pset_template(self.file, name="ABC_RiskFactors")
        prop = ifcopenshell.api.pset_template.add_prop_template(self.file, pset_template=template)
        ifcopenshell.api.pset_template.remove_prop_template(self.file, prop_template=prop)
        # The last prop template should not be removed to keep the pset template valid.
        assert len(self.file.by_type("IfcSimplePropertyTemplate")) == 1
        assert template.HasPropertyTemplates == (prop,)
