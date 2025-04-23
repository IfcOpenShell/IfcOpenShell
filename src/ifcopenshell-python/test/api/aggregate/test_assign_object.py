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

import numpy
import pytest
import test.bootstrap
import ifcopenshell.api.root
import ifcopenshell.api.unit
import ifcopenshell.api.spatial
import ifcopenshell.api.geometry
import ifcopenshell.api.aggregate
import ifcopenshell.util.element
import ifcopenshell.util.placement


class TestAssignObject(test.bootstrap.IFC4):
    def test_assigning_an_aggregate(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcSite")
        subelement1 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcBuilding")
        subelement2 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcBuilding")
        rel = ifcopenshell.api.aggregate.assign_object(
            self.file, products=[subelement1, subelement2], relating_object=element
        )
        assert ifcopenshell.util.element.get_aggregate(subelement1) == element
        assert ifcopenshell.util.element.get_aggregate(subelement2) == element
        assert rel.is_a("IfcRelAggregates")

    def test_doing_nothing_if_the_aggregate_is_already_assigned(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcSite")
        subelement = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcBuilding")
        ifcopenshell.api.aggregate.assign_object(self.file, products=[subelement], relating_object=element)
        total_elements = len([e for e in self.file])
        ifcopenshell.api.aggregate.assign_object(self.file, products=[subelement], relating_object=element)
        assert len([e for e in self.file]) == total_elements

    def test_that_old_aggregate_relationships_are_updated_if_they_still_have_elements(self):
        element1 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcSite")
        element2 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcSite")
        subelement1 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcBuilding")
        subelement2 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcBuilding")
        ifcopenshell.api.aggregate.assign_object(self.file, products=[subelement1], relating_object=element1)
        ifcopenshell.api.aggregate.assign_object(self.file, products=[subelement2], relating_object=element1)
        rel = subelement1.Decomposes[0]
        assert len(rel.RelatedObjects) == 2
        ifcopenshell.api.aggregate.assign_object(self.file, products=[subelement1], relating_object=element2)
        assert len(rel.RelatedObjects) == 1

    def test_that_old_aggregate_relationships_are_purged_if_no_more_elements_are_contained(self):
        element1 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcSite")
        element2 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcSite")
        subelement1 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcBuilding")
        ifcopenshell.api.aggregate.assign_object(self.file, products=[subelement1], relating_object=element1)
        rel_id = subelement1.Decomposes[0].id()
        ifcopenshell.api.aggregate.assign_object(self.file, products=[subelement1], relating_object=element2)
        with pytest.raises(RuntimeError):
            self.file.by_id(rel_id)

    def test_assigning_a_container_does_not_shift_object_placements(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        ifcopenshell.api.unit.assign_unit(self.file)
        element1 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcSite")
        element2 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcSite")
        subelement = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcBuilding")
        ifcopenshell.api.aggregate.assign_object(self.file, products=[subelement], relating_object=element1)
        matrix1 = numpy.array(
            (
                (1.0, 0.0, 0.0, 1.0),
                (0.0, 1.0, 0.0, 1.0),
                (0.0, 0.0, 1.0, 1.0),
                (0.0, 0.0, 0.0, 1.0),
            )
        )
        matrix2 = numpy.array(
            (
                (1.0, 0.0, 0.0, 2.0),
                (0.0, 1.0, 0.0, 2.0),
                (0.0, 0.0, 1.0, 2.0),
                (0.0, 0.0, 0.0, 1.0),
            )
        )
        ifcopenshell.api.geometry.edit_object_placement(self.file, product=element1, matrix=matrix1.copy(), is_si=False)
        ifcopenshell.api.geometry.edit_object_placement(self.file, product=element2, matrix=matrix2.copy(), is_si=False)
        ifcopenshell.api.geometry.edit_object_placement(
            self.file, product=subelement, matrix=matrix1.copy(), is_si=False
        )
        ifcopenshell.api.aggregate.assign_object(self.file, products=[subelement], relating_object=element2)
        assert subelement.ObjectPlacement.PlacementRelTo.PlacesObject[0] == element2
        assert numpy.array_equal(ifcopenshell.util.placement.get_local_placement(subelement.ObjectPlacement), matrix1)

    def test_not_updating_placement_if_placement_is_not_relative(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        ifcopenshell.api.unit.assign_unit(self.file)
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcSite")
        subelement = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcBuilding")
        placement = self.file.createIfcGridPlacement()
        subelement.ObjectPlacement = placement
        ifcopenshell.api.aggregate.assign_object(self.file, products=[subelement], relating_object=element)
        assert subelement.ObjectPlacement == placement

    def test_removing_containment_if_it_exists(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        ifcopenshell.api.unit.assign_unit(self.file)
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcElementAssembly")
        container = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcBuildingStorey")
        subelement = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        ifcopenshell.api.spatial.assign_container(self.file, products=[subelement], relating_structure=container)
        ifcopenshell.api.aggregate.assign_object(self.file, products=[subelement], relating_object=element)
        assert not ifcopenshell.util.element.get_container(subelement, should_get_direct=True)


class TestAssignObjectIFC2X3(test.bootstrap.IFC2X3, TestAssignObject):
    pass
