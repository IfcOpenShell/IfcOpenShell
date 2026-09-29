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

import ifcopenshell.api.pset
import ifcopenshell.api.root
import test.bootstrap


class TestEditPsetBoundedValue(test.bootstrap.IFC4):
    def test_adding_a_bounded_valued_property(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcElectricDistributionBoard")
        pset = ifcopenshell.api.pset.add_pset(self.file, product=element, name="Pset_ElectricalDeviceCommon")
        ifcopenshell.api.pset.edit_pset(
            self.file,
            pset=pset,
            properties={"RatedCurrent": {"LowerBoundValue": 1.0, "UpperBoundValue": 2.5}},
        )
        prop = pset.HasProperties[0]
        assert prop.is_a("IfcPropertyBoundedValue")
        assert prop.Name == "RatedCurrent"
        assert prop.LowerBoundValue.is_a("IfcElectricCurrentMeasure")
        assert prop.LowerBoundValue.wrappedValue == 1.0
        assert prop.UpperBoundValue.wrappedValue == 2.5
        assert prop.SetPointValue is None

    def test_editing_an_existing_bounded_valued_property(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcElectricDistributionBoard")
        pset = ifcopenshell.api.pset.add_pset(self.file, product=element, name="Pset_ElectricalDeviceCommon")
        ifcopenshell.api.pset.edit_pset(
            self.file,
            pset=pset,
            properties={"RatedCurrent": {"LowerBoundValue": 1.0, "UpperBoundValue": 2.5}},
        )
        ifcopenshell.api.pset.edit_pset(self.file, pset=pset, properties={"RatedCurrent": {"SetPointValue": 3.3}})
        prop = pset.HasProperties[0]
        assert prop.LowerBoundValue.wrappedValue == 1.0
        assert prop.UpperBoundValue.wrappedValue == 2.5
        assert prop.SetPointValue.wrappedValue == 3.3

    def test_removing_a_bounded_valued_property_if_specified(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcElectricDistributionBoard")
        pset = ifcopenshell.api.pset.add_pset(self.file, product=element, name="Pset_ElectricalDeviceCommon")
        ifcopenshell.api.pset.edit_pset(self.file, pset=pset, properties={"RatedCurrent": {"LowerBoundValue": 1.0}})
        assert len(pset.HasProperties) == 1
        ifcopenshell.api.pset.edit_pset(self.file, pset=pset, properties={"RatedCurrent": None})
        pset = element.IsDefinedBy[0].RelatingPropertyDefinition
        assert len(pset.HasProperties) == 0
