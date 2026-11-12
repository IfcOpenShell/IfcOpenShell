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

import ifcopenshell.api.resource
import test.bootstrap


class TestRemoveResourceQuantity(test.bootstrap.IFC4):
    def test_removing_a_resource_quantity(self):
        self.file.create_entity("IfcProject")
        resource = ifcopenshell.api.resource.add_resource(self.file, ifc_class="IfcLaborResource")
        ifcopenshell.api.resource.add_resource_quantity(self.file, resource=resource, ifc_class="IfcQuantityTime")
        assert resource.BaseQuantity is not None
        ifcopenshell.api.resource.remove_resource_quantity(self.file, resource=resource)
        assert resource.BaseQuantity is None
        assert len(self.file.by_type("IfcPhysicalSimpleQuantity")) == 0

    def test_removing_a_resource_quantity_when_none_exists(self):
        self.file.create_entity("IfcProject")
        resource = ifcopenshell.api.resource.add_resource(self.file, ifc_class="IfcLaborResource")
        # Should not raise.
        ifcopenshell.api.resource.remove_resource_quantity(self.file, resource=resource)
        assert resource.BaseQuantity is None


class TestRemoveResourceQuantityIFC2X3(test.bootstrap.IFC2X3, TestRemoveResourceQuantity):
    pass
