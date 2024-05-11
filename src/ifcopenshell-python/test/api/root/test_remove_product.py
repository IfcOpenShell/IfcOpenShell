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
import ifcopenshell.guid


class TestRemoveProduct(test.bootstrap.IFC4):
    def test_removing_an_element_by_itself(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        ifcopenshell.api.run("root.remove_product", self.file, product=element)
        assert len(self.file.by_type("IfcWall")) == 0

    def test_removing_an_element_local_placement(self):
        # just removing the product with the placement
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        placement = ifcopenshell.api.run("geometry.edit_object_placement", self.file, product=element)
        ifcopenshell.api.run("root.remove_product", self.file, product=element)
        assert len(self.file.by_type("IfcObjectPlacement")) == 0

        # removing the product that shares the placement with other product
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        placement = ifcopenshell.api.run("geometry.edit_object_placement", self.file, product=element)
        element1 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        element1.ObjectPlacement = placement
        ifcopenshell.api.run("root.remove_product", self.file, product=element)
        assert len(self.file.by_type("IfcObjectPlacement")) == 1
        ifcopenshell.api.run("root.remove_product", self.file, product=element1)
        assert len(self.file.by_type("IfcObjectPlacement")) == 0

        # removing the product that's placement used as a reference point for another placement
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        placement = ifcopenshell.api.run("geometry.edit_object_placement", self.file, product=element)
        element1 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        placement1 = ifcopenshell.api.run("geometry.edit_object_placement", self.file, product=element1)
        placement.PlacementRelTo = placement1
        ifcopenshell.api.run("root.remove_product", self.file, product=element)
        assert len(self.file.by_type("IfcObjectPlacement")) == 1
        ifcopenshell.api.run("root.remove_product", self.file, product=element1)
        assert len(self.file.by_type("IfcObjectPlacement")) == 0

    def test_removing_element_type_psets(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWallType")
        pset = ifcopenshell.api.run("pset.add_pset", self.file, product=element, name="Foo_Bar")
        ifcopenshell.api.run("pset.edit_pset", self.file, pset=pset, properties={"Foo": "Bar"})

        element2 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWallType")
        element2.HasPropertySets = (pset,)

        # make sure it won't remove the pset if it's connected elsewhere
        ifcopenshell.api.run("root.remove_product", self.file, product=element2)
        assert len(self.file.by_type("IfcPropertySet")) == 1
        assert len(self.file.by_type("IfcPropertySingleValue")) == 1

        # if it's the product is the only inverse for pset, it should remove the pset
        ifcopenshell.api.run("root.remove_product", self.file, product=element)
        assert len(self.file.by_type("IfcPropertySet")) == 0
        assert len(self.file.by_type("IfcPropertySingleValue")) == 0

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
        ifcopenshell.api.run("type.assign_type", self.file, related_objects=[element], relating_type=element_type)
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

    def test_removing_all_nesting_relationships_of_a_whole(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        subelement = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcBeam")
        ifcopenshell.api.run("nest.assign_object", self.file, related_objects=[subelement], relating_object=element)
        total_entities = len(list(self.file))
        ifcopenshell.api.run("root.remove_product", self.file, product=element)
        assert len(list(self.file)) == total_entities - 2
        assert len(self.file.by_type("IfcRelNests")) == 0
        assert len(self.file.by_type("IfcWall")) == 0
        assert len(self.file.by_type("IfcBeam")) == 1

    def test_removing_all_nesting_relationships_of_a_part(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        subelement = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcBeam")
        ifcopenshell.api.run("nest.assign_object", self.file, related_objects=[subelement], relating_object=element)
        total_entities = len(list(self.file))
        ifcopenshell.api.run("root.remove_product", self.file, product=subelement)
        assert len(list(self.file)) == total_entities - 2
        assert len(self.file.by_type("IfcRelNests")) == 0
        assert len(self.file.by_type("IfcWall")) == 1
        assert len(self.file.by_type("IfcBeam")) == 0

    def test_removing_all_aggregate_relationships_of_a_whole(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcElementAssembly")
        subelement = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcBeam")
        ifcopenshell.api.run("aggregate.assign_object", self.file, products=[subelement], relating_object=element)
        total_entities = len(list(self.file))
        ifcopenshell.api.run("root.remove_product", self.file, product=element)
        assert len(list(self.file)) == total_entities - 2
        assert len(self.file.by_type("IfcRelAggregates")) == 0
        assert len(self.file.by_type("IfcElementAssembly")) == 0
        assert len(self.file.by_type("IfcBeam")) == 1

    def test_removing_all_aggregate_relationships_of_a_part(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcElementAssembly")
        subelement = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcBeam")
        ifcopenshell.api.run("aggregate.assign_object", self.file, products=[subelement], relating_object=element)
        total_entities = len(list(self.file))
        ifcopenshell.api.run("root.remove_product", self.file, product=subelement)
        assert len(list(self.file)) == total_entities - 2
        assert len(self.file.by_type("IfcRelAggregates")) == 0
        assert len(self.file.by_type("IfcElementAssembly")) == 1
        assert len(self.file.by_type("IfcBeam")) == 0

    def test_removing_all_containment_relationships_of_a_container(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcSpace")
        subelement = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        ifcopenshell.api.run("spatial.assign_container", self.file, products=[subelement], relating_structure=element)
        total_entities = len(list(self.file))
        ifcopenshell.api.run("root.remove_product", self.file, product=element)
        assert len(list(self.file)) == total_entities - 2
        assert len(self.file.by_type("IfcRelContainedInSpatialStructure")) == 0
        assert len(self.file.by_type("IfcSpace")) == 0
        assert len(self.file.by_type("IfcWall")) == 1

    def test_removing_all_containment_relationships_of_an_element(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcSpace")
        subelement = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        ifcopenshell.api.run("spatial.assign_container", self.file, products=[subelement], relating_structure=element)
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

    def test_removing_connection_relationships_of_an_element(self):
        element1 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        element2 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcSlab")
        ifcopenshell.api.run(
            "geometry.connect_element",
            self.file,
            related_element=element1,
            relating_element=element2,
        )
        total_entities = len(list(self.file))
        ifcopenshell.api.run("root.remove_product", self.file, product=element1)
        assert len(list(self.file)) == total_entities - 2
        assert len(self.file.by_type("IfcRelConnectsElements")) == 0
        assert len(self.file.by_type("IfcSlab")) == 1
        assert len(self.file.by_type("IfcWall")) == 0

    def test_removing_connection_relationships_of_an_element_with_additional_realizing_element(self):
        wall = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        slab1 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcSlab")
        slab2 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcSlab")
        self.file.createIfcRelConnectsWithRealizingElements(
            ifcopenshell.guid.new(),
            OwnerHistory=ifcopenshell.api.run("owner.create_owner_history", self.file),
            RelatingElement=wall,
            RelatedElement=slab1,
            RealizingElements=(wall, slab1, slab2),
        )
        total_entities = len(list(self.file))
        ifcopenshell.api.run("root.remove_product", self.file, product=wall)
        assert len(list(self.file)) == total_entities - 2
        assert len(self.file.by_type("IfcRelConnectsElements")) == 0
        assert len(self.file.by_type("IfcSlab")) == 2
        assert len(self.file.by_type("IfcWall")) == 0

    def test_removing_connection_relationships_of_an_element_element_is_realizing_element(self):
        wall = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        slab1 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcSlab")
        slab2 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcSlab")
        self.file.createIfcRelConnectsWithRealizingElements(
            ifcopenshell.guid.new(),
            OwnerHistory=ifcopenshell.api.run("owner.create_owner_history", self.file),
            RelatingElement=wall,
            RelatedElement=slab1,
            RealizingElements=(wall, slab1, slab2),
        )
        total_entities = len(list(self.file))
        ifcopenshell.api.run("root.remove_product", self.file, product=slab2)
        assert len(list(self.file)) == total_entities - 1
        assert len(self.file.by_type("IfcRelConnectsElements")) == 1
        assert len(self.file.by_type("IfcSlab")) == 1
        assert len(self.file.by_type("IfcWall")) == 1

    def test_removing_connection_relationships_of_an_element_element_is_only_realizing_element(self):
        wall = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        slab1 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcSlab")
        slab2 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcSlab")
        self.file.createIfcRelConnectsWithRealizingElements(
            ifcopenshell.guid.new(),
            OwnerHistory=ifcopenshell.api.run("owner.create_owner_history", self.file),
            RelatingElement=wall,
            RelatedElement=slab1,
            RealizingElements=(slab2,),
        )
        total_entities = len(list(self.file))
        ifcopenshell.api.run("root.remove_product", self.file, product=slab2)
        assert len(list(self.file)) == total_entities - 2
        assert len(self.file.by_type("IfcRelConnectsElements")) == 0
        assert len(self.file.by_type("IfcSlab")) == 1
        assert len(self.file.by_type("IfcWall")) == 1

    def test_removing_ports_connection_relationship(self):
        port1 = ifcopenshell.api.run("system.add_port", self.file)
        element1 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcFlowSegment")
        ifcopenshell.api.run("system.assign_port", self.file, element=element1, port=port1)

        port2 = ifcopenshell.api.run("system.add_port", self.file)
        element2 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcFlowSegment")
        ifcopenshell.api.run("system.assign_port", self.file, element=element2, port=port2)

        ifcopenshell.api.run("system.connect_port", self.file, port1=port1, port2=port2, direction="SOURCE")
        connection = self.file.by_type("IfcRelConnectsPorts")[0]

        # making sure removing realizing element won't remove the entire connection since it's optional
        element3 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcFlowSegment")
        connection.RealizingElement = element3
        ifcopenshell.api.run("root.remove_product", self.file, product=element3)
        assert len(self.file.by_type("IfcRelConnectsPorts")) == 1

        ifcopenshell.api.run("root.remove_product", self.file, product=element1)
        assert len(self.file.by_type("IfcRelConnectsPorts")) == 0
        assert len(self.file.by_type("IfcFlowSegment")) == 1
        assert len(self.file.by_type("IfcDistributionPort")) == 1

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
        ifcopenshell.api.run("material.assign_material", self.file, products=[element], material=material)
        ifcopenshell.api.run("root.remove_product", self.file, product=element)
        assert not self.file.by_type("IfcRelAssociatesMaterial")
        assert self.file.by_type("IfcMaterial")

    def test_removing_all_type_relationships_of_an_element(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        element_type = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWallType")
        ifcopenshell.api.run("type.assign_type", self.file, related_objects=[element], relating_type=element_type)
        ifcopenshell.api.run("root.remove_product", self.file, product=element)
        assert not self.file.by_type("IfcRelDefinesByType")
        assert self.file.by_type("IfcWallType")

    def test_removing_all_type_relationships_of_an_element_type(self):
        element1 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        element2 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        element_type = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWallType")
        ifcopenshell.api.run("type.assign_type", self.file, related_objects=[element1], relating_type=element_type)
        ifcopenshell.api.run("type.assign_type", self.file, related_objects=[element2], relating_type=element_type)
        ifcopenshell.api.run("root.remove_product", self.file, product=element_type)
        assert not self.file.by_type("IfcRelDefinesByType")
        assert self.file.by_type("IfcWall")

    def test_removing_all_space_boundaries_of_an_element(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        boundary = self.file.createIfcRelSpaceBoundary(
            GlobalId=ifcopenshell.guid.new(), RelatedBuildingElement=element
        )
        ifcopenshell.api.run("root.remove_product", self.file, product=element)
        assert not self.file.by_type("IfcRelSpaceBoundary")

    def test_removing_orphaned_group_relationships(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        group = ifcopenshell.api.run("group.add_group", self.file, Name="Unit 1A")
        ifcopenshell.api.run("group.assign_group", self.file, products=[element], group=group)
        ifcopenshell.api.run("root.remove_product", self.file, product=element)
        assert not self.file.by_type("IfcRelAssignsToGroup")

    def test_removing_product_assignments(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        annotation = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcAnnotation")
        ifcopenshell.api.run("drawing.assign_product", self.file, relating_product=element, related_object=annotation)
        ifcopenshell.api.run("root.remove_product", self.file, product=element)
        assert not self.file.by_type("IfcRelAssignsToProduct")

    def test_removing_flow_control_elements(self):
        flow_element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcFlowSegment")
        flow_control = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcDistributionControlElement")
        flow_control1 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcDistributionControlElement")

        ifcopenshell.api.run(
            "system.assign_flow_control",
            self.file,
            related_flow_control=flow_control,
            relating_flow_element=flow_element,
        )
        ifcopenshell.api.run(
            "system.assign_flow_control",
            self.file,
            related_flow_control=flow_control1,
            relating_flow_element=flow_element,
        )
        ifcopenshell.api.run("root.remove_product", self.file, product=flow_control)
        assert len(self.file.by_type("IfcRelFlowControlElements")) == 1
        ifcopenshell.api.run("root.remove_product", self.file, product=flow_control1)
        assert not self.file.by_type("IfcRelFlowControlElements")

    def test_removing_flow_element_with_flow_controls(self):
        flow_element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcFlowSegment")
        flow_control = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcDistributionControlElement")
        flow_control1 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcDistributionControlElement")

        ifcopenshell.api.run(
            "system.assign_flow_control",
            self.file,
            related_flow_control=flow_control,
            relating_flow_element=flow_element,
        )
        ifcopenshell.api.run(
            "system.assign_flow_control",
            self.file,
            related_flow_control=flow_control1,
            relating_flow_element=flow_element,
        )
        ifcopenshell.api.run("root.remove_product", self.file, product=flow_element)
        assert not self.file.by_type("IfcRelFlowControlElements")


class TestRemoveProductIFC2X3(TestRemoveProduct, test.bootstrap.IFC2X3):
    pass
