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

import pytest
import test.bootstrap
import ifcopenshell.api
import ifcopenshell.api.resource
import ifcopenshell.util.resource


class TestAddResourceQuantity(test.bootstrap.IFC4):
    def test_run(self):
        schema = ifcopenshell.schema_by_name(self.file.schema)
        assert (quantity_entity := schema.declaration_by_name("IfcPhysicalSimpleQuantity").as_entity())
        quantity_types = [t.name() for t in quantity_entity.subtypes()]
        assert (resource_entity := schema.declaration_by_name("IfcConstructionResource").as_entity())
        resource_types = [t.name() for t in resource_entity.subtypes()]

        self.file.create_entity("IfcProject")  # add_resource

        for resource_type in resource_types:
            resource = ifcopenshell.api.resource.add_resource(self.file, ifc_class=resource_type)
            available_quantities = ifcopenshell.util.resource.RESOURCES_TO_QUANTITIES[resource_type]

            for quantity_type in quantity_types:
                if quantity_type not in available_quantities:
                    with pytest.raises(ValueError):
                        quantity = ifcopenshell.api.resource.add_resource_quantity(
                            self.file, resource=resource, ifc_class=quantity_type
                        )
                    continue
                else:
                    quantity = ifcopenshell.api.resource.add_resource_quantity(
                        self.file, resource=resource, ifc_class=quantity_type
                    )

                assert quantity.is_a(quantity_type)
                assert quantity.Name == "Unnamed"
                assert quantity[3] == 0.0
                # previous quantity is reassigned and removed
                assert resource.BaseQuantity == quantity
                assert len(self.file.by_type("IfcPhysicalSimpleQuantity")) == 1

            ifcopenshell.api.resource.remove_resource(self.file, resource)


class TestAddResourceQuantityIFC2X3(test.bootstrap.IFC2X3, TestAddResourceQuantity):
    pass


class TestAddResourceQuantityIFC4X3(test.bootstrap.IFC4X3, TestAddResourceQuantity):
    pass
