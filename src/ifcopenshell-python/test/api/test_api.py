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
import ifcopenshell.api
import ifcopenshell.util.element
from datetime import datetime


def deprecation_check(test):
    def new_test(self):
        assert datetime.now().date() < datetime(2024, 6, 1).date(), "API arguments are completely deprecated"
        test(self)

    return new_test


class TestTemporarySupportForDeprecatedAPIArguments(test.bootstrap.IFC4):
    @deprecation_check
    def test_assigning_a_container(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcBuilding")
        subelement = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        rel = ifcopenshell.api.run(
            "spatial.assign_container", self.file, product=subelement, relating_structure=element
        )
        assert ifcopenshell.util.element.get_container(subelement) == element
        assert rel.is_a("IfcRelContainedInSpatialStructure")

    @deprecation_check
    def test_unassigning_a_container_with_other_elements(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcBuilding")
        subelement = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        subelement2 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        ifcopenshell.api.run(
            "spatial.assign_container", self.file, products=[subelement, subelement2], relating_structure=element
        )
        ifcopenshell.api.run("spatial.unassign_container", self.file, product=subelement)
        rel = self.file.by_type("IfcRelContainedInSpatialStructure")[0]
        assert list(rel.RelatedElements) == [subelement2]

    @deprecation_check
    def test_group_unassignment(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcPump")
        element2 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcPump")
        group = ifcopenshell.api.run("group.add_group", self.file)
        ifcopenshell.api.run("group.assign_group", self.file, products=[element, element2], group=group)
        ifcopenshell.api.run("group.unassign_group", self.file, product=element2, group=group)

        assert len(rels := self.file.by_type("IfcRelAssignsToGroup")) == 1
        rel = rels[0]
        assert rel.RelatingGroup == group
        assert rel.RelatedObjects == (element,)

    @deprecation_check
    def test_assign_layer_to_items(self):
        item = self.file.createIfcExtrudedAreaSolid()
        layer = self.file.createIfcPresentationLayerAssignment()

        ifcopenshell.api.run("layer.assign_layer", self.file, item=item, layer=layer)
        assert layer.AssignedItems == (item,)

    @deprecation_check
    def test_unassign_layer_from_items(self):
        items = [self.file.createIfcExtrudedAreaSolid() for i in range(3)]
        layer = self.file.createIfcPresentationLayerAssignment()

        ifcopenshell.api.run("layer.assign_layer", self.file, items=items, layer=layer)
        ifcopenshell.api.run("layer.unassign_layer", self.file, item=items[2], layer=layer)
        assert len(layer.AssignedItems) == 2
        assert set(layer.AssignedItems) == set(items[:2])

    @deprecation_check
    def test_assigning_an_aggregate(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcSite")
        subelement = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcBuilding")
        rel = ifcopenshell.api.run("aggregate.assign_object", self.file, product=subelement, relating_object=element)
        assert ifcopenshell.util.element.get_aggregate(subelement) == element
        assert rel.is_a("IfcRelAggregates")

    @deprecation_check
    def test_unassigning_an_aggregate(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcSite")
        subelement = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcBuilding")
        ifcopenshell.api.run("aggregate.assign_object", self.file, product=subelement, relating_object=element)
        ifcopenshell.api.run("aggregate.unassign_object", self.file, product=subelement)
        assert ifcopenshell.util.element.get_aggregate(subelement) is None

    @deprecation_check
    def test_removing_a_container(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcBuilding")
        subelement = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        ifcopenshell.api.run("spatial.assign_container", self.file, products=[subelement], relating_structure=element)
        ifcopenshell.api.run("spatial.remove_container", self.file, product=subelement)
        assert ifcopenshell.util.element.get_container(subelement) is None
