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


class TestAssignContainer(test.bootstrap.IFC4):
    def test_assigning_a_container(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcBuilding")
        subelement = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        subelement2 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        rel = ifcopenshell.api.spatial.assign_container(
            self.file, products=[subelement, subelement2], relating_structure=element
        )
        assert ifcopenshell.util.element.get_container(subelement) == element
        assert ifcopenshell.util.element.get_container(subelement2) == element
        assert rel.is_a("IfcRelContainedInSpatialStructure")

    def test_doing_nothing_if_the_container_is_already_assigned(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcBuilding")
        subelement = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        ifcopenshell.api.spatial.assign_container(self.file, products=[subelement], relating_structure=element)
        total_elements = len([e for e in self.file])
        ifcopenshell.api.spatial.assign_container(self.file, products=[subelement], relating_structure=element)
        assert len([e for e in self.file]) == total_elements

    def test_that_old_containment_relationships_are_updated_if_they_still_contain_elements(self):
        element1 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcBuilding")
        element2 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcBuilding")
        subelement1 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        subelement2 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        ifcopenshell.api.spatial.assign_container(self.file, products=[subelement1], relating_structure=element1)
        ifcopenshell.api.spatial.assign_container(self.file, products=[subelement2], relating_structure=element1)
        rel = subelement1.ContainedInStructure[0]
        assert len(rel.RelatedElements) == 2
        ifcopenshell.api.spatial.assign_container(self.file, products=[subelement1], relating_structure=element2)
        assert len(rel.RelatedElements) == 1

    def test_that_old_containment_relationships_are_purged_if_no_more_elements_are_contained(self):
        element1 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcBuilding")
        element2 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcBuilding")
        subelement1 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        ifcopenshell.api.spatial.assign_container(self.file, products=[subelement1], relating_structure=element1)
        rel_id = subelement1.ContainedInStructure[0].id()
        ifcopenshell.api.spatial.assign_container(self.file, products=[subelement1], relating_structure=element2)
        with pytest.raises(RuntimeError):
            self.file.by_id(rel_id)

    def test_assigning_a_container_does_not_shift_object_placements(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        ifcopenshell.api.unit.assign_unit(self.file)
        element1 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcBuilding")
        element2 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcBuilding")
        subelement = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        ifcopenshell.api.spatial.assign_container(self.file, products=[subelement], relating_structure=element1)
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
        ifcopenshell.api.spatial.assign_container(self.file, products=[subelement], relating_structure=element2)
        assert subelement.ObjectPlacement.PlacementRelTo.PlacesObject[0] == element2
        assert numpy.array_equal(ifcopenshell.util.placement.get_local_placement(subelement.ObjectPlacement), matrix1)

    def test_not_updating_placement_if_placement_is_not_relative(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        ifcopenshell.api.unit.assign_unit(self.file)
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcBuilding")
        subelement = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        placement = self.file.createIfcGridPlacement()
        subelement.ObjectPlacement = placement
        ifcopenshell.api.spatial.assign_container(self.file, products=[subelement], relating_structure=element)
        assert subelement.ObjectPlacement == placement

    def test_removing_aggregation_if_it_exists(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        ifcopenshell.api.unit.assign_unit(self.file)
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcBuilding")
        aggregate = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcElementAssembly")
        subelement = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        ifcopenshell.api.aggregate.assign_object(self.file, products=[subelement], relating_object=aggregate)
        ifcopenshell.api.spatial.assign_container(self.file, products=[subelement], relating_structure=element)
        assert not ifcopenshell.util.element.get_aggregate(subelement)


class TestAssignContainerIFC2X3(test.bootstrap.IFC2X3, TestAssignContainer):
    pass
