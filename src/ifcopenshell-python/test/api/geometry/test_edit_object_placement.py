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
import ifcopenshell.api.feature
import ifcopenshell.api.root
import ifcopenshell.api.unit
import ifcopenshell.api.system
import ifcopenshell.api.spatial
import ifcopenshell.api.geometry
import ifcopenshell.api.aggregate
import ifcopenshell.guid
import ifcopenshell.util.placement


class TestEditObjectPlacement(test.bootstrap.IFC4):
    def test_attemping_to_edit_the_placement_of_an_invalid_element(self):
        project = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        result = ifcopenshell.api.geometry.edit_object_placement(self.file, product=project)
        assert result is None

    def test_setting_an_object_placement(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        ifcopenshell.api.unit.assign_unit(self.file)
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        matrix = numpy.array(
            (
                (1.0, 0.0, 0.0, 1.0),
                (0.0, 1.0, 0.0, 2.0),
                (0.0, 0.0, 1.0, 3.0),
                (0.0, 0.0, 0.0, 1.0),
            )
        )
        ifcopenshell.api.geometry.edit_object_placement(self.file, product=element, matrix=matrix.copy(), is_si=False)
        assert numpy.array_equal(ifcopenshell.util.placement.get_local_placement(element.ObjectPlacement), matrix)

    def test_setting_an_object_placement_using_si_units(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        ifcopenshell.api.unit.assign_unit(self.file)
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        matrix = numpy.array(
            (
                (1.0, 0.0, 0.0, 1.0),
                (0.0, 1.0, 0.0, 2.0),
                (0.0, 0.0, 1.0, 3.0),
                (0.0, 0.0, 0.0, 1.0),
            )
        )
        matrix_millimeters = numpy.array(
            (
                (1.0, 0.0, 0.0, 1000.0),
                (0.0, 1.0, 0.0, 2000.0),
                (0.0, 0.0, 1.0, 3000.0),
                (0.0, 0.0, 0.0, 1.0),
            )
        )
        ifcopenshell.api.geometry.edit_object_placement(self.file, product=element, matrix=matrix, is_si=True)
        assert numpy.array_equal(
            ifcopenshell.util.placement.get_local_placement(element.ObjectPlacement), matrix_millimeters
        )

    def test_changing_an_object_placement(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        ifcopenshell.api.unit.assign_unit(self.file)
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        matrix1 = numpy.array(
            (
                (1.0, 0.0, 0.0, 1.0),
                (0.0, 1.0, 0.0, 2.0),
                (0.0, 0.0, 1.0, 3.0),
                (0.0, 0.0, 0.0, 1.0),
            )
        )
        matrix2 = numpy.array(
            (
                (1.0, 0.0, 0.0, 4.0),
                (0.0, 1.0, 0.0, 5.0),
                (0.0, 0.0, 1.0, 6.0),
                (0.0, 0.0, 0.0, 1.0),
            )
        )
        ifcopenshell.api.geometry.edit_object_placement(self.file, product=element, matrix=matrix1.copy(), is_si=False)
        created_element_ids = [e.id() for e in self.file.traverse(element.ObjectPlacement)]
        ifcopenshell.api.geometry.edit_object_placement(self.file, product=element, matrix=matrix2.copy(), is_si=False)
        assert numpy.array_equal(ifcopenshell.util.placement.get_local_placement(element.ObjectPlacement), matrix2)
        for element_id in created_element_ids:
            with pytest.raises(RuntimeError):
                self.file.by_id(element_id)

    def test_changing_an_object_placement_used_by_other_products(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        ifcopenshell.api.unit.assign_unit(self.file)
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        element2 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        matrix1 = numpy.array(
            (
                (1.0, 0.0, 0.0, 1.0),
                (0.0, 1.0, 0.0, 2.0),
                (0.0, 0.0, 1.0, 3.0),
                (0.0, 0.0, 0.0, 1.0),
            )
        )
        matrix2 = numpy.array(
            (
                (1.0, 0.0, 0.0, 4.0),
                (0.0, 1.0, 0.0, 5.0),
                (0.0, 0.0, 1.0, 6.0),
                (0.0, 0.0, 0.0, 1.0),
            )
        )
        ifcopenshell.api.geometry.edit_object_placement(self.file, product=element, matrix=matrix1.copy(), is_si=False)
        element2.ObjectPlacement = element.ObjectPlacement
        ifcopenshell.api.geometry.edit_object_placement(self.file, product=element, matrix=matrix2.copy(), is_si=False)
        assert numpy.array_equal(ifcopenshell.util.placement.get_local_placement(element.ObjectPlacement), matrix2)
        assert element.ObjectPlacement != element2.ObjectPlacement

    def test_changing_an_object_placement_partially_used_by_other_products(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        ifcopenshell.api.unit.assign_unit(self.file)
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        element2 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        matrix1 = numpy.array(
            (
                (1.0, 0.0, 0.0, 1.0),
                (0.0, 1.0, 0.0, 2.0),
                (0.0, 0.0, 1.0, 3.0),
                (0.0, 0.0, 0.0, 1.0),
            )
        )
        matrix2 = numpy.array(
            (
                (1.0, 0.0, 0.0, 4.0),
                (0.0, 1.0, 0.0, 5.0),
                (0.0, 0.0, 1.0, 6.0),
                (0.0, 0.0, 0.0, 1.0),
            )
        )
        ifcopenshell.api.geometry.edit_object_placement(self.file, product=element, matrix=matrix1.copy(), is_si=False)
        element2.ObjectPlacement = self.file.createIfcLocalPlacement(
            RelativePlacement=element.ObjectPlacement.RelativePlacement
        )
        ifcopenshell.api.geometry.edit_object_placement(self.file, product=element, matrix=matrix2.copy(), is_si=False)
        assert numpy.array_equal(ifcopenshell.util.placement.get_local_placement(element.ObjectPlacement), matrix2)
        assert numpy.array_equal(ifcopenshell.util.placement.get_local_placement(element2.ObjectPlacement), matrix1)

    def test_changing_an_object_placement_shared_by_its_parent(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        ifcopenshell.api.unit.assign_unit(self.file)
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcBuilding")
        subelement = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        ifcopenshell.api.spatial.assign_container(self.file, products=[subelement], relating_structure=element)
        matrix1 = numpy.array(
            (
                (1.0, 0.0, 0.0, 1.0),
                (0.0, 1.0, 0.0, 2.0),
                (0.0, 0.0, 1.0, 3.0),
                (0.0, 0.0, 0.0, 1.0),
            )
        )
        matrix2 = numpy.array(
            (
                (1.0, 0.0, 0.0, 4.0),
                (0.0, 1.0, 0.0, 5.0),
                (0.0, 0.0, 1.0, 6.0),
                (0.0, 0.0, 0.0, 1.0),
            )
        )
        ifcopenshell.api.geometry.edit_object_placement(self.file, product=element, matrix=matrix1.copy(), is_si=False)
        subelement.ObjectPlacement = element.ObjectPlacement
        ifcopenshell.api.geometry.edit_object_placement(
            self.file, product=subelement, matrix=matrix2.copy(), is_si=False
        )
        assert subelement.ObjectPlacement.PlacementRelTo != subelement.ObjectPlacement
        assert numpy.array_equal(ifcopenshell.util.placement.get_local_placement(subelement.ObjectPlacement), matrix2)
        assert element.ObjectPlacement != subelement.ObjectPlacement

    def test_changing_placements_relative_to_a_spatial_container(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        ifcopenshell.api.unit.assign_unit(self.file)
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcBuilding")
        subelement = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        matrix = numpy.array(
            (
                (1.0, 0.0, 0.0, 1.0),
                (0.0, 1.0, 0.0, 1.0),
                (0.0, 0.0, 1.0, 1.0),
                (0.0, 0.0, 0.0, 1.0),
            )
        )
        submatrix = numpy.array(
            (
                (1.0, 0.0, 0.0, 1.0),
                (0.0, 1.0, 0.0, 2.0),
                (0.0, 0.0, 1.0, 3.0),
                (0.0, 0.0, 0.0, 1.0),
            )
        )
        ifcopenshell.api.spatial.assign_container(self.file, products=[subelement], relating_structure=element)
        ifcopenshell.api.geometry.edit_object_placement(self.file, product=element, matrix=matrix.copy(), is_si=False)
        ifcopenshell.api.geometry.edit_object_placement(
            self.file, product=subelement, matrix=submatrix.copy(), is_si=False
        )
        assert numpy.array_equal(ifcopenshell.util.placement.get_local_placement(element.ObjectPlacement), matrix)
        assert numpy.array_equal(ifcopenshell.util.placement.get_local_placement(subelement.ObjectPlacement), submatrix)
        assert subelement.ObjectPlacement.PlacementRelTo == element.ObjectPlacement

    def test_changing_placements_relative_to_an_aggregate(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        ifcopenshell.api.unit.assign_unit(self.file)
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcElementAssembly")
        subelement = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcBeam")
        matrix = numpy.array(
            (
                (1.0, 0.0, 0.0, 1.0),
                (0.0, 1.0, 0.0, 1.0),
                (0.0, 0.0, 1.0, 1.0),
                (0.0, 0.0, 0.0, 1.0),
            )
        )
        submatrix = numpy.array(
            (
                (1.0, 0.0, 0.0, 1.0),
                (0.0, 1.0, 0.0, 2.0),
                (0.0, 0.0, 1.0, 3.0),
                (0.0, 0.0, 0.0, 1.0),
            )
        )
        ifcopenshell.api.aggregate.assign_object(self.file, products=[subelement], relating_object=element)
        ifcopenshell.api.geometry.edit_object_placement(self.file, product=element, matrix=matrix.copy(), is_si=False)
        ifcopenshell.api.geometry.edit_object_placement(
            self.file, product=subelement, matrix=submatrix.copy(), is_si=False
        )
        assert numpy.array_equal(ifcopenshell.util.placement.get_local_placement(element.ObjectPlacement), matrix)
        assert numpy.array_equal(ifcopenshell.util.placement.get_local_placement(subelement.ObjectPlacement), submatrix)
        assert subelement.ObjectPlacement.PlacementRelTo == element.ObjectPlacement

    def test_changing_placements_relative_to_a_nest_parent(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        ifcopenshell.api.unit.assign_unit(self.file)
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcFlowSegment")
        subelement = ifcopenshell.api.system.add_port(self.file, element=element)
        matrix = numpy.array(
            (
                (1.0, 0.0, 0.0, 1.0),
                (0.0, 1.0, 0.0, 1.0),
                (0.0, 0.0, 1.0, 1.0),
                (0.0, 0.0, 0.0, 1.0),
            )
        )
        submatrix = numpy.array(
            (
                (1.0, 0.0, 0.0, 1.0),
                (0.0, 1.0, 0.0, 2.0),
                (0.0, 0.0, 1.0, 3.0),
                (0.0, 0.0, 0.0, 1.0),
            )
        )
        ifcopenshell.api.geometry.edit_object_placement(self.file, product=element, matrix=matrix.copy(), is_si=False)
        ifcopenshell.api.geometry.edit_object_placement(
            self.file, product=subelement, matrix=submatrix.copy(), is_si=False
        )
        assert numpy.array_equal(ifcopenshell.util.placement.get_local_placement(element.ObjectPlacement), matrix)
        assert numpy.array_equal(ifcopenshell.util.placement.get_local_placement(subelement.ObjectPlacement), submatrix)
        assert subelement.ObjectPlacement.PlacementRelTo == element.ObjectPlacement

    def test_changing_placements_relative_to_a_voided_element(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        ifcopenshell.api.unit.assign_unit(self.file)
        site = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcSite")
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        subelement = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcOpeningElement")
        ifcopenshell.api.spatial.assign_container(self.file, products=[element], relating_structure=site)
        matrix = numpy.array(
            (
                (1.0, 0.0, 0.0, 1.0),
                (0.0, 1.0, 0.0, 1.0),
                (0.0, 0.0, 1.0, 1.0),
                (0.0, 0.0, 0.0, 1.0),
            )
        )
        submatrix = numpy.array(
            (
                (1.0, 0.0, 0.0, 1.0),
                (0.0, 1.0, 0.0, 2.0),
                (0.0, 0.0, 1.0, 3.0),
                (0.0, 0.0, 0.0, 1.0),
            )
        )
        ifcopenshell.api.feature.add_feature(self.file, feature=subelement, element=element)
        ifcopenshell.api.geometry.edit_object_placement(self.file, product=element, matrix=matrix.copy(), is_si=False)
        ifcopenshell.api.geometry.edit_object_placement(
            self.file, product=subelement, matrix=submatrix.copy(), is_si=False
        )
        assert numpy.array_equal(ifcopenshell.util.placement.get_local_placement(element.ObjectPlacement), matrix)
        assert numpy.array_equal(ifcopenshell.util.placement.get_local_placement(subelement.ObjectPlacement), submatrix)
        assert subelement.ObjectPlacement.PlacementRelTo == element.ObjectPlacement

    def test_changing_placements_relative_to_an_opening(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        ifcopenshell.api.unit.assign_unit(self.file)
        site = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcSite")
        wall = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcOpeningElement")
        subelement = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcDoor")
        ifcopenshell.api.spatial.assign_container(self.file, products=[wall], relating_structure=site)
        ifcopenshell.api.spatial.assign_container(self.file, products=[subelement], relating_structure=site)
        matrix = numpy.array(
            (
                (1.0, 0.0, 0.0, 1.0),
                (0.0, 1.0, 0.0, 1.0),
                (0.0, 0.0, 1.0, 1.0),
                (0.0, 0.0, 0.0, 1.0),
            )
        )
        submatrix = numpy.array(
            (
                (1.0, 0.0, 0.0, 1.0),
                (0.0, 1.0, 0.0, 2.0),
                (0.0, 0.0, 1.0, 3.0),
                (0.0, 0.0, 0.0, 1.0),
            )
        )
        ifcopenshell.api.feature.add_feature(self.file, feature=element, element=wall)
        ifcopenshell.api.feature.add_filling(self.file, element=subelement, opening=element)
        ifcopenshell.api.geometry.edit_object_placement(self.file, product=site, matrix=numpy.eye(4), is_si=False)
        ifcopenshell.api.geometry.edit_object_placement(self.file, product=wall, matrix=numpy.eye(4), is_si=False)
        ifcopenshell.api.geometry.edit_object_placement(self.file, product=element, matrix=matrix.copy(), is_si=False)
        ifcopenshell.api.geometry.edit_object_placement(
            self.file, product=subelement, matrix=submatrix.copy(), is_si=False
        )
        assert numpy.array_equal(ifcopenshell.util.placement.get_local_placement(element.ObjectPlacement), matrix)
        assert numpy.array_equal(ifcopenshell.util.placement.get_local_placement(subelement.ObjectPlacement), submatrix)
        assert not site.ObjectPlacement.PlacementRelTo
        assert wall.ObjectPlacement.PlacementRelTo == site.ObjectPlacement
        assert element.ObjectPlacement.PlacementRelTo == wall.ObjectPlacement
        assert subelement.ObjectPlacement.PlacementRelTo == element.ObjectPlacement

    def test_changing_placements_relative_to_a_projected_element(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        ifcopenshell.api.unit.assign_unit(self.file)
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        subelement = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProjectionElement")
        matrix = numpy.array(
            (
                (1.0, 0.0, 0.0, 1.0),
                (0.0, 1.0, 0.0, 1.0),
                (0.0, 0.0, 1.0, 1.0),
                (0.0, 0.0, 0.0, 1.0),
            )
        )
        submatrix = numpy.array(
            (
                (1.0, 0.0, 0.0, 1.0),
                (0.0, 1.0, 0.0, 2.0),
                (0.0, 0.0, 1.0, 3.0),
                (0.0, 0.0, 0.0, 1.0),
            )
        )
        self.file.create_entity(
            "IfcRelProjectsElement",
            **{
                "GlobalId": ifcopenshell.guid.new(),
                "RelatingElement": element,
                "RelatedFeatureElement": subelement,
            },
        )
        ifcopenshell.api.geometry.edit_object_placement(self.file, product=element, matrix=matrix.copy(), is_si=False)
        ifcopenshell.api.geometry.edit_object_placement(
            self.file, product=subelement, matrix=submatrix.copy(), is_si=False
        )
        assert numpy.array_equal(ifcopenshell.util.placement.get_local_placement(element.ObjectPlacement), matrix)
        assert numpy.array_equal(ifcopenshell.util.placement.get_local_placement(subelement.ObjectPlacement), submatrix)
        assert subelement.ObjectPlacement.PlacementRelTo == element.ObjectPlacement

    def test_changing_placements_without_affecting_children(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        ifcopenshell.api.unit.assign_unit(self.file)
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcBuilding")
        subelement = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        matrix = numpy.array(
            (
                (1.0, 0.0, 0.0, 1.0),
                (0.0, 1.0, 0.0, 1.0),
                (0.0, 0.0, 1.0, 1.0),
                (0.0, 0.0, 0.0, 1.0),
            )
        )
        submatrix = numpy.array(
            (
                (1.0, 0.0, 0.0, 1.0),
                (0.0, 1.0, 0.0, 2.0),
                (0.0, 0.0, 1.0, 3.0),
                (0.0, 0.0, 0.0, 1.0),
            )
        )
        ifcopenshell.api.spatial.assign_container(self.file, products=[subelement], relating_structure=element)
        ifcopenshell.api.geometry.edit_object_placement(self.file, product=element, matrix=matrix.copy(), is_si=False)
        ifcopenshell.api.geometry.edit_object_placement(
            self.file, product=subelement, matrix=submatrix.copy(), is_si=False
        )
        ifcopenshell.api.geometry.edit_object_placement(
            self.file, product=element, matrix=submatrix.copy(), is_si=False
        )
        assert numpy.array_equal(ifcopenshell.util.placement.get_local_placement(element.ObjectPlacement), submatrix)
        assert numpy.array_equal(ifcopenshell.util.placement.get_local_placement(subelement.ObjectPlacement), submatrix)
        assert subelement.ObjectPlacement.PlacementRelTo == element.ObjectPlacement

    def test_changing_placements_with_affecting_children(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        ifcopenshell.api.unit.assign_unit(self.file)
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcBuilding")
        subelement = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        matrix = numpy.array(
            (
                (1.0, 0.0, 0.0, 1.0),
                (0.0, 1.0, 0.0, 1.0),
                (0.0, 0.0, 1.0, 1.0),
                (0.0, 0.0, 0.0, 1.0),
            )
        )
        submatrix = numpy.array(
            (
                (1.0, 0.0, 0.0, 1.0),
                (0.0, 1.0, 0.0, 2.0),
                (0.0, 0.0, 1.0, 3.0),
                (0.0, 0.0, 0.0, 1.0),
            )
        )
        shifted_submatrix = numpy.array(
            (
                (1.0, 0.0, 0.0, 1.0),
                (0.0, 1.0, 0.0, 3.0),
                (0.0, 0.0, 1.0, 5.0),
                (0.0, 0.0, 0.0, 1.0),
            )
        )
        ifcopenshell.api.spatial.assign_container(self.file, products=[subelement], relating_structure=element)
        ifcopenshell.api.geometry.edit_object_placement(self.file, product=element, matrix=matrix.copy(), is_si=False)
        ifcopenshell.api.geometry.edit_object_placement(
            self.file, product=subelement, matrix=submatrix.copy(), is_si=False
        )
        ifcopenshell.api.geometry.edit_object_placement(
            self.file,
            product=element,
            matrix=submatrix.copy(),
            is_si=False,
            should_transform_children=True,
        )
        assert numpy.array_equal(ifcopenshell.util.placement.get_local_placement(element.ObjectPlacement), submatrix)
        assert numpy.array_equal(
            ifcopenshell.util.placement.get_local_placement(subelement.ObjectPlacement), shifted_submatrix
        )
        assert subelement.ObjectPlacement.PlacementRelTo == element.ObjectPlacement

    def test_changing_placements_with_children_using_non_si_units(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        ifcopenshell.api.unit.assign_unit(self.file)
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcBuilding")
        subelement = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        matrix = numpy.array(
            (
                (1.0, 0.0, 0.0, 1000.0),
                (0.0, 1.0, 0.0, 1000.0),
                (0.0, 0.0, 1.0, 1000.0),
                (0.0, 0.0, 0.0, 1.0),
            )
        )
        matrix_si = numpy.array(
            (
                (1.0, 0.0, 0.0, 1.0),
                (0.0, 1.0, 0.0, 1.0),
                (0.0, 0.0, 1.0, 1.0),
                (0.0, 0.0, 0.0, 1.0),
            )
        )
        submatrix = numpy.array(
            (
                (1.0, 0.0, 0.0, 1000.0),
                (0.0, 1.0, 0.0, 2000.0),
                (0.0, 0.0, 1.0, 3000.0),
                (0.0, 0.0, 0.0, 1.0),
            )
        )
        ifcopenshell.api.spatial.assign_container(self.file, products=[subelement], relating_structure=element)
        ifcopenshell.api.geometry.edit_object_placement(self.file, product=element, matrix=matrix.copy(), is_si=False)
        ifcopenshell.api.geometry.edit_object_placement(
            self.file, product=subelement, matrix=submatrix.copy(), is_si=False
        )
        ifcopenshell.api.geometry.edit_object_placement(self.file, product=element, matrix=matrix_si.copy(), is_si=True)
        assert numpy.array_equal(ifcopenshell.util.placement.get_local_placement(element.ObjectPlacement), matrix)
        assert numpy.array_equal(ifcopenshell.util.placement.get_local_placement(subelement.ObjectPlacement), submatrix)
        assert subelement.ObjectPlacement.PlacementRelTo == element.ObjectPlacement

    def test_changing_placements_always_affecting_child_ports_as_a_special_case(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        ifcopenshell.api.unit.assign_unit(self.file)
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcFlowSegment")
        subelement = ifcopenshell.api.system.add_port(self.file, element=element)

        matrix = numpy.eye(4)
        matrix[:3, 3] = (1, 1, 1)

        submatrix = numpy.eye(4)
        submatrix[:3, 3] = (1, 2, 3)

        shifted_submatrix = numpy.eye(4)
        shifted_submatrix[:3, 3] = (1, 3, 5)

        previous_placement_id = ifcopenshell.api.geometry.edit_object_placement(
            self.file, product=element, matrix=matrix.copy(), is_si=False
        ).id()
        ifcopenshell.api.geometry.edit_object_placement(
            self.file, product=subelement, matrix=submatrix.copy(), is_si=False
        )
        ifcopenshell.api.geometry.edit_object_placement(
            self.file,
            product=element,
            matrix=submatrix.copy(),
            is_si=False,
            should_transform_children=False,
        )
        assert numpy.array_equal(ifcopenshell.util.placement.get_local_placement(element.ObjectPlacement), submatrix)
        assert numpy.array_equal(
            ifcopenshell.util.placement.get_local_placement(subelement.ObjectPlacement), shifted_submatrix
        )
        assert subelement.ObjectPlacement.PlacementRelTo == element.ObjectPlacement
        # old placement should be removed to avoid orphaned entities
        with pytest.raises(RuntimeError):
            self.file.by_id(previous_placement_id)

    def test_changing_placements_always_affecting_child_features_but_not_subchildren_as_a_special_case(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        ifcopenshell.api.unit.assign_unit(self.file)
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        subelement = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcOpeningElement")
        subsubelement = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcDoor")

        matrix = numpy.eye(4)
        matrix[:3, 3] = (1, 1, 1)

        submatrix = numpy.eye(4)
        submatrix[:3, 3] = (1, 2, 3)

        subsubmatrix = numpy.eye(4)
        subsubmatrix[:3, 3] = (7, 8, 9)

        shifted_submatrix = numpy.eye(4)
        shifted_submatrix[:3, 3] = (1, 3, 5)

        ifcopenshell.api.feature.add_feature(self.file, feature=subelement, element=element)
        ifcopenshell.api.feature.add_filling(self.file, opening=subelement, element=subsubelement)
        previous_placement_id = ifcopenshell.api.geometry.edit_object_placement(
            self.file, product=element, matrix=matrix.copy(), is_si=False
        ).id()
        ifcopenshell.api.geometry.edit_object_placement(
            self.file, product=subelement, matrix=submatrix.copy(), is_si=False
        )
        ifcopenshell.api.geometry.edit_object_placement(
            self.file, product=subsubelement, matrix=subsubmatrix.copy(), is_si=False
        )
        ifcopenshell.api.geometry.edit_object_placement(
            self.file,
            product=element,
            matrix=submatrix.copy(),
            is_si=False,
            should_transform_children=False,
        )
        assert numpy.array_equal(ifcopenshell.util.placement.get_local_placement(element.ObjectPlacement), submatrix)
        assert numpy.array_equal(
            ifcopenshell.util.placement.get_local_placement(subelement.ObjectPlacement), shifted_submatrix
        )
        assert numpy.array_equal(
            ifcopenshell.util.placement.get_local_placement(subsubelement.ObjectPlacement), subsubmatrix
        )
        assert subelement.ObjectPlacement.PlacementRelTo == element.ObjectPlacement
        assert subsubelement.ObjectPlacement.PlacementRelTo == subelement.ObjectPlacement
        # old placement should be removed to avoid orphaned entities
        with pytest.raises(RuntimeError):
            self.file.by_id(previous_placement_id)

    def test_changing_placements_without_affecting_children_doesnt_affect_subchildren(self):
        def np_matrix_translation(translation):
            (m := numpy.eye(4))[:3, 3] = translation
            return m

        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        ifcopenshell.api.unit.assign_unit(self.file)

        building = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcBuilding")
        storey = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcBuildingStorey")
        ifcopenshell.api.aggregate.assign_object(self.file, products=[storey], relating_object=building)
        wall = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        ifcopenshell.api.spatial.assign_container(self.file, products=[wall], relating_structure=storey)

        matrix = np_matrix_translation((1, 1, 1))
        submatrix = np_matrix_translation((1, 2, 3))
        building_placement_id = ifcopenshell.api.geometry.edit_object_placement(
            self.file, product=building, matrix=matrix.copy(), is_si=False
        ).id()
        storey_placement_id = ifcopenshell.api.geometry.edit_object_placement(
            self.file, product=storey, matrix=matrix.copy(), is_si=False
        ).id()
        wall_placement_id = ifcopenshell.api.geometry.edit_object_placement(
            self.file, product=wall, matrix=matrix.copy(), is_si=False
        ).id()
        ifcopenshell.api.geometry.edit_object_placement(
            self.file,
            product=building,
            matrix=submatrix.copy(),
            is_si=False,
        )
        # product and it's children have their placement rebuilt
        with pytest.raises(RuntimeError):
            self.file.by_id(building_placement_id)
        with pytest.raises(RuntimeError):
            self.file.by_id(storey_placement_id)
        # subchildren are unaffected, exception is not raised
        self.file.by_id(wall_placement_id)
        assert numpy.array_equal(ifcopenshell.util.placement.get_local_placement(wall.ObjectPlacement), matrix)


class TestEditObjectPlacementIFC2X3(test.bootstrap.IFC2X3, TestEditObjectPlacement):
    def test_changing_placements_relative_to_a_distribution_element(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        ifcopenshell.api.unit.assign_unit(self.file)
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcFlowSegment")
        subelement = ifcopenshell.api.system.add_port(self.file, element=element)
        matrix = numpy.array(
            (
                (1.0, 0.0, 0.0, 1.0),
                (0.0, 1.0, 0.0, 1.0),
                (0.0, 0.0, 1.0, 1.0),
                (0.0, 0.0, 0.0, 1.0),
            )
        )
        submatrix = numpy.array(
            (
                (1.0, 0.0, 0.0, 1.0),
                (0.0, 1.0, 0.0, 2.0),
                (0.0, 0.0, 1.0, 3.0),
                (0.0, 0.0, 0.0, 1.0),
            )
        )
        ifcopenshell.api.geometry.edit_object_placement(self.file, product=element, matrix=matrix.copy(), is_si=False)
        ifcopenshell.api.geometry.edit_object_placement(
            self.file, product=subelement, matrix=submatrix.copy(), is_si=False
        )
        assert numpy.array_equal(ifcopenshell.util.placement.get_local_placement(element.ObjectPlacement), matrix)
        assert numpy.array_equal(ifcopenshell.util.placement.get_local_placement(subelement.ObjectPlacement), submatrix)
        assert subelement.ObjectPlacement.PlacementRelTo == element.ObjectPlacement
