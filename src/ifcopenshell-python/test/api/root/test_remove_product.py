# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
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


class TestRemoveProduct(test.bootstrap.IFC4):
    def test_removing_an_element_by_itself(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        ifcopenshell.api.run("root.remove_product", self.file, product=element)
        assert len(self.file.by_type("IfcWall")) == 0

    def test_removing_all_representations_of_an_element(self):
        ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcProject")
        ifcopenshell.api.run("unit.assign_unit", self.file)
        context = ifcopenshell.api.run("context.add_context", self.file, context_type="Model")
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        element.Representation = self.file.createIfcProductDefinitionShape(
            Representations=[
                self.file.createIfcShapeRepresentation(
                    ContextOfItems=context, Items=[self.file.createIfcExtrudedAreaSolid()]
                )
            ]
        )
        total_entities = len(list(self.file))
        ifcopenshell.api.run("root.remove_product", self.file, product=element)
        assert len(list(self.file)) == total_entities - 4
        assert len(self.file.by_type("IfcProductDefinitionShape")) == 0
        assert len(self.file.by_type("IfcShapeRepresentation")) == 0
        assert len(self.file.by_type("IfcExtrudedAreaSolid")) == 0
        assert len(self.file.by_type("IfcWall")) == 0

    def test_unassigning_but_not_removing_mapped_representations_of_an_element(self):
        ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcProject")
        ifcopenshell.api.run("unit.assign_unit", self.file)
        context = ifcopenshell.api.run("context.add_context", self.file, context_type="Model")
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        element_type = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWallType")
        ifcopenshell.api.run("type.assign_type", self.file, related_object=element, relating_type=element_type)
        rep_map = self.file.createIfcRepresentationMap(
            MappingOrigin=self.file.createIfcAxis2Placement3D(),
            MappedRepresentation=self.file.createIfcShapeRepresentation(
                ContextOfItems=context, Items=[self.file.createIfcExtrudedAreaSolid()]
            ),
        )
        element_type.RepresentationMaps = [rep_map]
        element.Representation = self.file.createIfcProductDefinitionShape(
            Representations=[
                self.file.createIfcShapeRepresentation(
                    ContextOfItems=context,
                    RepresentationType="MappedRepresentation",
                    Items=[
                        self.file.createIfcMappedItem(
                            MappingSource=rep_map, MappingTarget=self.file.createIfcCartesianTransformationOperator3D()
                        )
                    ],
                )
            ]
        )
        total_entities = len(list(self.file))
        assert len(self.file.by_type("IfcShapeRepresentation")) == 2
        ifcopenshell.api.run("root.remove_product", self.file, product=element)
        assert len(list(self.file)) == total_entities - 6
        assert len(self.file.by_type("IfcProductDefinitionShape")) == 0
        assert len(self.file.by_type("IfcShapeRepresentation")) == 1
        assert len(self.file.by_type("IfcMappedItem")) == 0
        assert len(self.file.by_type("IfcCartesianTransformationOperator3D")) == 0
        assert len(self.file.by_type("IfcWall")) == 0

    def test_removing_an_element_type_by_itself(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWallType")
        ifcopenshell.api.run("root.remove_product", self.file, product=element)
        assert len(self.file.by_type("IfcWallType")) == 0

    def test_removing_all_openings_of_an_element(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        opening = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcOpeningElement")
        ifcopenshell.api.run("void.add_opening", self.file, opening=opening, element=element)
        total_entities = len(list(self.file))
        ifcopenshell.api.run("root.remove_product", self.file, product=element)
        assert len(list(self.file)) == total_entities - 3
        assert len(self.file.by_type("IfcWall")) == 0
        assert len(self.file.by_type("IfcOpeningElement")) == 0
        assert len(self.file.by_type("IfcRelVoidsElement")) == 0

    def test_removing_axes_of_a_grid(self):
        grid = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcGrid")
        axis = ifcopenshell.api.run("grid.create_grid_axis", self.file, uvw_axes="UAxes", grid=grid)
        axis.AxisCurve = self.file.createIfcPolyline()
        axis = ifcopenshell.api.run("grid.create_grid_axis", self.file, uvw_axes="VAxes", grid=grid)
        axis.AxisCurve = self.file.createIfcPolyline()
        total_entities = len(list(self.file))
        ifcopenshell.api.run("root.remove_product", self.file, product=grid)
        assert len(list(self.file)) == 0

    def test_removing_all_void_relationships_of_an_opening(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        opening = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcOpeningElement")
        ifcopenshell.api.run("void.add_opening", self.file, opening=opening, element=element)
        total_entities = len(list(self.file))
        ifcopenshell.api.run("root.remove_product", self.file, product=opening)
        assert len(list(self.file)) == total_entities - 2
        assert len(self.file.by_type("IfcOpeningElement")) == 0
        assert len(self.file.by_type("IfcRelVoidsElement")) == 0

    def test_removing_all_fill_relationships_of_a_filling(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        opening = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcOpeningElement")
        filling = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcDoor")
        ifcopenshell.api.run("void.add_opening", self.file, opening=opening, element=element)
        ifcopenshell.api.run("void.add_filling", self.file, opening=opening, element=filling)
        total_entities = len(list(self.file))
        ifcopenshell.api.run("root.remove_product", self.file, product=filling)
        assert len(list(self.file)) == total_entities - 2
        assert len(self.file.by_type("IfcDoor")) == 0
        assert len(self.file.by_type("IfcRelFillsElement")) == 0

    def test_removing_all_distribution_ports(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcChiller")
        port = ifcopenshell.api.run("system.add_port", self.file, element=element)
        total_entities = len(list(self.file))
        ifcopenshell.api.run("root.remove_product", self.file, product=element)
        assert len(list(self.file)) == total_entities - 3
        assert len(self.file.by_type("IfcChiller")) == 0
        assert len(self.file.by_type("IfcRelNests")) == 0
        assert len(self.file.by_type("IfcDistributionPort")) == 0

    def test_removing_all_aggregate_relationships_of_a_whole(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcElementAssembly")
        subelement = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcBeam")
        ifcopenshell.api.run("aggregate.assign_object", self.file, product=subelement, relating_object=element)
        total_entities = len(list(self.file))
        ifcopenshell.api.run("root.remove_product", self.file, product=element)
        assert len(list(self.file)) == total_entities - 2
        assert len(self.file.by_type("IfcRelAggregates")) == 0
        assert len(self.file.by_type("IfcElementAssembly")) == 0
        assert len(self.file.by_type("IfcBeam")) == 1

    def test_removing_all_aggregate_relationships_of_a_part(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcElementAssembly")
        subelement = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcBeam")
        ifcopenshell.api.run("aggregate.assign_object", self.file, product=subelement, relating_object=element)
        total_entities = len(list(self.file))
        ifcopenshell.api.run("root.remove_product", self.file, product=subelement)
        assert len(list(self.file)) == total_entities - 2
        assert len(self.file.by_type("IfcRelAggregates")) == 0
        assert len(self.file.by_type("IfcElementAssembly")) == 1
        assert len(self.file.by_type("IfcBeam")) == 0

    def test_removing_all_containment_relationships_of_a_container(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcSpace")
        subelement = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        ifcopenshell.api.run("spatial.assign_container", self.file, product=subelement, relating_structure=element)
        total_entities = len(list(self.file))
        ifcopenshell.api.run("root.remove_product", self.file, product=element)
        assert len(list(self.file)) == total_entities - 2
        assert len(self.file.by_type("IfcRelContainedInSpatialStructure")) == 0
        assert len(self.file.by_type("IfcSpace")) == 0
        assert len(self.file.by_type("IfcWall")) == 1

    def test_removing_all_containment_relationships_of_an_element(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcSpace")
        subelement = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        ifcopenshell.api.run("spatial.assign_container", self.file, product=subelement, relating_structure=element)
        total_entities = len(list(self.file))
        ifcopenshell.api.run("root.remove_product", self.file, product=subelement)
        assert len(list(self.file)) == total_entities - 2
        assert len(self.file.by_type("IfcRelContainedInSpatialStructure")) == 0
        assert len(self.file.by_type("IfcSpace")) == 1
        assert len(self.file.by_type("IfcWall")) == 0

    def test_removing_path_connection_relationships_of_an_element(self):
        element1 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcBeam")
        element2 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcColumn")
        ifcopenshell.api.run("geometry.connect_path", self.file, relating_element=element1, related_element=element2)
        total_entities = len(list(self.file))
        ifcopenshell.api.run("root.remove_product", self.file, product=element1)
        assert len(list(self.file)) == total_entities - 2
        assert len(self.file.by_type("IfcRelConnectsPathElements")) == 0
        assert len(self.file.by_type("IfcColumn")) == 1
        assert len(self.file.by_type("IfcBeam")) == 0

    def test_removing_all_property_relationships_of_an_element(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        pset = ifcopenshell.api.run("pset.add_pset", self.file, product=element, name="Foo_Bar")
        ifcopenshell.api.run("pset.edit_pset", self.file, pset=pset, properties={"Foo": "Bar"})
        ifcopenshell.api.run("root.remove_product", self.file, product=element)
        assert not self.file.by_type("IfcRelDefinesByProperties")
        assert not self.file.by_type("IfcPropertySet")
        assert not self.file.by_type("IfcPropertySingleValue")

    def test_removing_all_material_relationships_of_an_element(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        material = ifcopenshell.api.run("material.add_material", self.file, name="Foo")
        ifcopenshell.api.run("material.assign_material", self.file, product=element, material=material)
        ifcopenshell.api.run("root.remove_product", self.file, product=element)
        assert not self.file.by_type("IfcRelAssociatesMaterial")
        assert self.file.by_type("IfcMaterial")

    def test_removing_all_type_relationships_of_an_element(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        element_type = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWallType")
        ifcopenshell.api.run("type.assign_type", self.file, related_object=element, relating_type=element_type)
        ifcopenshell.api.run("root.remove_product", self.file, product=element)
        assert not self.file.by_type("IfcRelDefinesByType")
        assert self.file.by_type("IfcWallType")

    def test_removing_all_type_relationships_of_an_element_type(self):
        element1 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        element2 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        element_type = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWallType")
        ifcopenshell.api.run("type.assign_type", self.file, related_object=element1, relating_type=element_type)
        ifcopenshell.api.run("type.assign_type", self.file, related_object=element2, relating_type=element_type)
        ifcopenshell.api.run("root.remove_product", self.file, product=element_type)
        assert not self.file.by_type("IfcRelDefinesByType")
        assert self.file.by_type("IfcWall")

    def test_removing_all_space_boundaries_of_an_element(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        boundary = self.file.createIfcRelSpaceBoundary2ndLevel(
            GlobalId=ifcopenshell.guid.new(), RelatedBuildingElement=element
        )
        ifcopenshell.api.run("root.remove_product", self.file, product=element)
        assert not self.file.by_type("IfcRelSpaceBoundary")
