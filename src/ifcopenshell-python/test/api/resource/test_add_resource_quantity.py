# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2024 Dion Moult <dion@thinkmoult.com>
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
import ifcopenshell.api


class TestAddResourceQuantity(test.bootstrap.IFC4):
    def test_run(self):
        schema = ifcopenshell.schema_by_name(self.file.schema)
        quantity_types = [t.name() for t in schema.declaration_by_name("IfcPhysicalSimpleQuantity").subtypes()]
        self.file.create_entity("IfcProject")  # add_resource
        resource = ifcopenshell.api.run("resource.add_resource", self.file, ifc_class="IfcCrewResource")

        for quantity_type in quantity_types:
            quantity = ifcopenshell.api.run(
                "resource.add_resource_quantity", self.file, resource=resource, ifc_class=quantity_type
            )
            assert quantity.is_a(quantity_type)
            assert quantity.Name == "Unnamed"
            assert quantity[3] == 0.0
            # previous quantity is reassigned and removed
            assert resource.BaseQuantity == quantity
            assert len(self.file.by_type("IfcPhysicalSimpleQuantity")) == 1


class TestAddResourceQuantityIFC2X3(test.bootstrap.IFC2X3, TestAddResourceQuantity):
    pass


class TestAddResourceQuantityIFC4X3(test.bootstrap.IFC4X3, TestAddResourceQuantity):
    pass
