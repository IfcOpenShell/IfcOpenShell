import numpy
import pytest
import test.bootstrap
import ifcopenshell.api
import ifcopenshell.util.placement


class TestEditObjectPlacement(test.bootstrap.IFC4):
    def test_attemping_to_edit_the_placement_of_an_invalid_element(self):
        project = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcProject")
        result = ifcopenshell.api.run("geometry.edit_object_placement", self.file, product=project)
        assert result is None

    def test_setting_an_object_placement(self):
        ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcProject")
        ifcopenshell.api.run("unit.assign_unit", self.file)
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        matrix = numpy.array(
            (
                (1.0, 0.0, 0.0, 1.0),
                (0.0, 1.0, 0.0, 2.0),
                (0.0, 0.0, 1.0, 3.0),
                (0.0, 0.0, 0.0, 1.0),
            )
        )
        ifcopenshell.api.run(
            "geometry.edit_object_placement", self.file, product=element, matrix=matrix.copy(), is_si=False
        )
        assert numpy.array_equal(ifcopenshell.util.placement.get_local_placement(element.ObjectPlacement), matrix)

    def test_setting_an_object_placement_using_si_units(self):
        ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcProject")
        ifcopenshell.api.run("unit.assign_unit", self.file)
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
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
        ifcopenshell.api.run("geometry.edit_object_placement", self.file, product=element, matrix=matrix, is_si=True)
        assert numpy.array_equal(
            ifcopenshell.util.placement.get_local_placement(element.ObjectPlacement), matrix_millimeters
        )

    def test_changing_an_object_placement(self):
        ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcProject")
        ifcopenshell.api.run("unit.assign_unit", self.file)
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
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
        ifcopenshell.api.run(
            "geometry.edit_object_placement", self.file, product=element, matrix=matrix1.copy(), is_si=False
        )
        created_element_ids = [e.id() for e in self.file.traverse(element.ObjectPlacement)]
        ifcopenshell.api.run(
            "geometry.edit_object_placement", self.file, product=element, matrix=matrix2.copy(), is_si=False
        )
        assert numpy.array_equal(ifcopenshell.util.placement.get_local_placement(element.ObjectPlacement), matrix2)
        for element_id in created_element_ids:
            with pytest.raises(RuntimeError):
                self.file.by_id(element_id)

    def test_changing_placements_relative_to_a_spatial_container(self):
        ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcProject")
        ifcopenshell.api.run("unit.assign_unit", self.file)
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcBuilding")
        subelement = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
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
        ifcopenshell.api.run("spatial.assign_container", self.file, product=subelement, relating_structure=element)
        ifcopenshell.api.run(
            "geometry.edit_object_placement", self.file, product=element, matrix=matrix.copy(), is_si=False
        )
        ifcopenshell.api.run(
            "geometry.edit_object_placement", self.file, product=subelement, matrix=submatrix.copy(), is_si=False
        )
        assert numpy.array_equal(ifcopenshell.util.placement.get_local_placement(element.ObjectPlacement), matrix)
        assert numpy.array_equal(ifcopenshell.util.placement.get_local_placement(subelement.ObjectPlacement), submatrix)
        assert subelement.ObjectPlacement.PlacementRelTo == element.ObjectPlacement

    def test_changing_placements_relative_to_an_aggregate(self):
        ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcProject")
        ifcopenshell.api.run("unit.assign_unit", self.file)
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcElementAssembly")
        subelement = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcBeam")
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
        ifcopenshell.api.run("aggregate.assign_object", self.file, product=subelement, relating_object=element)
        ifcopenshell.api.run(
            "geometry.edit_object_placement", self.file, product=element, matrix=matrix.copy(), is_si=False
        )
        ifcopenshell.api.run(
            "geometry.edit_object_placement", self.file, product=subelement, matrix=submatrix.copy(), is_si=False
        )
        assert numpy.array_equal(ifcopenshell.util.placement.get_local_placement(element.ObjectPlacement), matrix)
        assert numpy.array_equal(ifcopenshell.util.placement.get_local_placement(subelement.ObjectPlacement), submatrix)
        assert subelement.ObjectPlacement.PlacementRelTo == element.ObjectPlacement

    def test_changing_placements_relative_to_a_voided_element(self):
        ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcProject")
        ifcopenshell.api.run("unit.assign_unit", self.file)
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        subelement = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcOpeningElement")
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
        ifcopenshell.api.run("void.add_opening", self.file, opening=subelement, element=element)
        ifcopenshell.api.run(
            "geometry.edit_object_placement", self.file, product=element, matrix=matrix.copy(), is_si=False
        )
        ifcopenshell.api.run(
            "geometry.edit_object_placement", self.file, product=subelement, matrix=submatrix.copy(), is_si=False
        )
        assert numpy.array_equal(ifcopenshell.util.placement.get_local_placement(element.ObjectPlacement), matrix)
        assert numpy.array_equal(ifcopenshell.util.placement.get_local_placement(subelement.ObjectPlacement), submatrix)
        assert subelement.ObjectPlacement.PlacementRelTo == element.ObjectPlacement

    def test_changing_placements_relative_to_an_opening(self):
        ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcProject")
        ifcopenshell.api.run("unit.assign_unit", self.file)
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcOpeningElement")
        subelement = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcDoor")
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
        ifcopenshell.api.run("void.add_filling", self.file, element=subelement, opening=element)
        ifcopenshell.api.run(
            "geometry.edit_object_placement", self.file, product=element, matrix=matrix.copy(), is_si=False
        )
        ifcopenshell.api.run(
            "geometry.edit_object_placement", self.file, product=subelement, matrix=submatrix.copy(), is_si=False
        )
        assert numpy.array_equal(ifcopenshell.util.placement.get_local_placement(element.ObjectPlacement), matrix)
        assert numpy.array_equal(ifcopenshell.util.placement.get_local_placement(subelement.ObjectPlacement), submatrix)
        assert subelement.ObjectPlacement.PlacementRelTo == element.ObjectPlacement

    def test_changing_placements_relative_to_a_projected_element(self):
        ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcProject")
        ifcopenshell.api.run("unit.assign_unit", self.file)
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        subelement = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcProjectionElement")
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
            }
        )
        ifcopenshell.api.run(
            "geometry.edit_object_placement", self.file, product=element, matrix=matrix.copy(), is_si=False
        )
        ifcopenshell.api.run(
            "geometry.edit_object_placement", self.file, product=subelement, matrix=submatrix.copy(), is_si=False
        )
        assert numpy.array_equal(ifcopenshell.util.placement.get_local_placement(element.ObjectPlacement), matrix)
        assert numpy.array_equal(ifcopenshell.util.placement.get_local_placement(subelement.ObjectPlacement), submatrix)
        assert subelement.ObjectPlacement.PlacementRelTo == element.ObjectPlacement

    def test_changing_placements_without_affecting_children(self):
        ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcProject")
        ifcopenshell.api.run("unit.assign_unit", self.file)
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcBuilding")
        subelement = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
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
        ifcopenshell.api.run("spatial.assign_container", self.file, product=subelement, relating_structure=element)
        ifcopenshell.api.run(
            "geometry.edit_object_placement", self.file, product=element, matrix=matrix.copy(), is_si=False
        )
        ifcopenshell.api.run(
            "geometry.edit_object_placement", self.file, product=subelement, matrix=submatrix.copy(), is_si=False
        )
        ifcopenshell.api.run(
            "geometry.edit_object_placement", self.file, product=element, matrix=submatrix.copy(), is_si=False
        )
        assert numpy.array_equal(ifcopenshell.util.placement.get_local_placement(element.ObjectPlacement), submatrix)
        assert numpy.array_equal(ifcopenshell.util.placement.get_local_placement(subelement.ObjectPlacement), submatrix)
        assert subelement.ObjectPlacement.PlacementRelTo == element.ObjectPlacement

    def test_changing_placements_with_affecting_children(self):
        ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcProject")
        ifcopenshell.api.run("unit.assign_unit", self.file)
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcBuilding")
        subelement = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
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
        ifcopenshell.api.run("spatial.assign_container", self.file, product=subelement, relating_structure=element)
        ifcopenshell.api.run(
            "geometry.edit_object_placement", self.file, product=element, matrix=matrix.copy(), is_si=False
        )
        ifcopenshell.api.run(
            "geometry.edit_object_placement", self.file, product=subelement, matrix=submatrix.copy(), is_si=False
        )
        ifcopenshell.api.run(
            "geometry.edit_object_placement",
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
