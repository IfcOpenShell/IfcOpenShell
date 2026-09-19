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

import os

import ifcopenshell
import ifcopenshell.api.aggregate
import ifcopenshell.api.context
import ifcopenshell.api.feature
import ifcopenshell.api.geometry
import ifcopenshell.api.georeference
import ifcopenshell.api.material
import ifcopenshell.api.pset
import ifcopenshell.api.root
import ifcopenshell.api.spatial
import ifcopenshell.api.system
import ifcopenshell.api.type
import ifcopenshell.guid
import ifcopenshell.util.element
import ifcopenshell.validate
import numpy
import pytest

import ifcpatch
import test.bootstrap


class TestExtractElements(test.bootstrap.IFC4):
    def test_basic(self):
        project = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        wall = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        output = ifcpatch.execute({"file": self.file, "recipe": "ExtractElements", "arguments": ["IfcWall"]})

        assert output.by_type("IfcProject")[0].GlobalId == project.GlobalId
        assert output.by_type("IfcWall")[0].GlobalId == wall.GlobalId

    def test_shared_relationship_members_are_preserved(self):
        # Regression test: a relationship shared by many extracted elements
        # (e.g. one IfcRelAssociatesMaterial linking every product) must keep all
        # of its members. The deferred member-list assignment used to avoid the
        # O(n^2) cost of re-assigning a growing list per element must not drop any.
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        ifcopenshell.api.context.add_context(self.file, context_type="Model")
        material = ifcopenshell.api.material.add_material(self.file, name="Steel")
        walls = [ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall") for _ in range(3)]
        ifcopenshell.api.material.assign_material(self.file, products=walls, material=material)

        output = ifcpatch.execute({"file": self.file, "recipe": "ExtractElements", "arguments": ["IfcWall"]})

        rels = output.by_type("IfcRelAssociatesMaterial")
        assert len(rels) == 1
        assert {w.GlobalId for w in rels[0].RelatedObjects} == {w.GlobalId for w in walls}

    def test_relationship_members_outside_the_query_are_preserved(self):
        # Regression test: spatial containers, decomposition parents and element
        # types are appended alongside the queried elements, so deferred
        # relationship member lists must be resolved against everything present in
        # the output, not only the query matches. Otherwise their property sets and
        # material associations are dropped and relationships are left with an
        # empty member list, which violates the IFC [1:?] cardinality.
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        ifcopenshell.api.context.add_context(self.file, context_type="Model")

        site = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcSite")
        building = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcBuilding")
        storeys = [ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcBuildingStorey") for _ in range(2)]
        ifcopenshell.api.aggregate.assign_object(self.file, products=[building], relating_object=site)
        ifcopenshell.api.aggregate.assign_object(self.file, products=storeys, relating_object=building)

        wall_type = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWallType")
        walls = [ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall") for _ in range(4)]
        for i, wall in enumerate(walls):
            ifcopenshell.api.spatial.assign_container(
                self.file, products=[wall], relating_structure=storeys[i % len(storeys)]
            )
        ifcopenshell.api.type.assign_type(self.file, related_objects=walls, relating_type=wall_type)

        containers = [site, building] + storeys
        for element in containers + walls:
            pset = ifcopenshell.api.pset.add_pset(self.file, product=element, name="Pset_Test")
            ifcopenshell.api.pset.edit_pset(self.file, pset=pset, properties={"Foo": "Bar"})

        material = ifcopenshell.api.material.add_material(self.file, name="Steel")
        ifcopenshell.api.material.assign_material(self.file, products=walls + [wall_type], material=material)

        output = ifcpatch.execute({"file": self.file, "recipe": "ExtractElements", "arguments": ["IfcWall"]})

        for element in containers + walls:
            new_element = output.by_guid(element.GlobalId)
            psets = ifcopenshell.util.element.get_psets(new_element)
            assert psets.get("Pset_Test", {}).get("Foo") == "Bar", element.is_a()

        rels = output.by_type("IfcRelAssociatesMaterial")
        assert len(rels) == 1
        assert {o.GlobalId for o in rels[0].RelatedObjects} == {e.GlobalId for e in walls + [wall_type]}

        for rel in output.by_type("IfcRelationship"):
            for attribute in rel:
                assert attribute != (), f"{rel.is_a()} has an empty member list"

    def test_overrides_properties_members_are_preserved(self):
        # Regression test: IfcRelOverridesProperties.OverridingProperties holds
        # IfcProperty members, which unlike most relationship members have no
        # GlobalId. The deferred member-list assignment used to resolve members
        # by GlobalId, so every member of this one relationship silently
        # resolved to nothing and the list was written empty, violating the
        # IFC [1:?] cardinality.
        if self.file.schema != "IFC2X3":
            pytest.skip("IfcRelOverridesProperties only exists in IFC2X3")
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        wall = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        pset = ifcopenshell.api.pset.add_pset(self.file, product=wall, name="Pset_Test")
        ifcopenshell.api.pset.edit_pset(self.file, pset=pset, properties={"Foo": "Bar"})
        override = self.file.createIfcPropertySingleValue("Foo", None, self.file.createIfcText("Baz"), None)
        owner_history = self.file.by_type("IfcOwnerHistory")[0]
        self.file.createIfcRelOverridesProperties(
            ifcopenshell.guid.new(), owner_history, None, None, [wall], pset, [override]
        )

        output = ifcpatch.execute({"file": self.file, "recipe": "ExtractElements", "arguments": ["IfcWall"]})

        rels = output.by_type("IfcRelOverridesProperties")
        assert len(rels) == 1
        assert len(rels[0].OverridingProperties) == 1
        assert rels[0].OverridingProperties[0].Name == "Foo"
        assert rels[0].OverridingProperties[0].NominalValue.wrappedValue == "Baz"

    def test_representation_shared_with_a_type_map_is_not_duplicated(self):
        # Regression test: exporters do emit an IfcShapeRepresentation that is at
        # once a product's own representation and a type's
        # IfcRepresentationMap.MappedRepresentation. Extraction must reproduce the
        # source as it stands, one entity in both roles. Appending the element type
        # through the name uniqueness code path the caller had opted out of used to
        # copy the representation instead, silently rewriting the model.
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        context = ifcopenshell.api.context.add_context(self.file, context_type="Model")
        wall_type = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWallType")
        wall = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        ifcopenshell.api.type.assign_type(
            self.file, related_objects=[wall], relating_type=wall_type, should_map_representations=False
        )

        points = [self.file.createIfcCartesianPoint(p) for p in ((0.0, 0.0), (1.0, 0.0))]
        representation = self.file.createIfcShapeRepresentation(
            context, "Body", "Curve2D", [self.file.createIfcPolyline(points)]
        )
        wall.Representation = self.file.createIfcProductDefinitionShape(None, None, [representation])
        origin = self.file.createIfcAxis2Placement3D(self.file.createIfcCartesianPoint((0.0, 0.0, 0.0)))
        wall_type.RepresentationMaps = [self.file.createIfcRepresentationMap(origin, representation)]

        output = ifcpatch.execute({"file": self.file, "recipe": "ExtractElements", "arguments": ["IfcWall", False]})

        new_wall = output.by_type("IfcWall")[0]
        new_type = output.by_type("IfcWallType")[0]
        own = {r.id() for r in new_wall.Representation.Representations}
        mapped = {m.MappedRepresentation.id() for m in new_type.RepresentationMaps}
        assert own == mapped
        assert len(output.by_type("IfcShapeRepresentation")) == 1

    def test_shared_presentation_layer_keeps_every_element(self):
        # Regression test for #9008: an IfcPresentationLayerAssignment is shared by
        # every element drawn on it. append_asset created it on the first element
        # that reached it and returned on every later visit, so the output kept the
        # items of one element and every other element silently lost its layer.
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        context = ifcopenshell.api.context.add_context(self.file, context_type="Model")

        walls = []
        items = []
        for _ in range(4):
            wall = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
            points = [self.file.createIfcCartesianPoint(p) for p in ((0.0, 0.0), (1.0, 0.0))]
            item = self.file.createIfcPolyline(points)
            representation = self.file.createIfcShapeRepresentation(context, "Body", "Curve2D", [item])
            wall.Representation = self.file.createIfcProductDefinitionShape(None, None, [representation])
            walls.append(wall)
            items.append(item)
        layer = self.file.createIfcPresentationLayerAssignment("Layer", None, items, None)
        assert len(layer.AssignedItems) == len(walls)

        output = ifcpatch.execute({"file": self.file, "recipe": "ExtractElements", "arguments": ["IfcWall", False]})

        assert len(output.by_type("IfcWall")) == len(walls)
        layers = output.by_type("IfcPresentationLayerAssignment")
        assert len(layers) == 1
        assert layers[0].Name == "Layer"
        assigned = set(layers[0].AssignedItems)
        assert len(assigned) == len(walls)
        for wall in output.by_type("IfcWall"):
            wall_items = {i for r in wall.Representation.Representations for i in r.Items}
            assert wall_items & assigned, f"{wall.GlobalId} lost its presentation layer"

    def test_ifc2x3_mep_ports_and_abstract_distribution_type_are_preserved(self):
        if self.file.schema != "IFC2X3":
            pytest.skip("IfcRelConnectsPortToElement is an IFC2X3-only port relationship")
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        terminal = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcFlowTerminal")
        terminal_type = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcDistributionElementType")
        ifcopenshell.api.type.assign_type(self.file, related_objects=[terminal], relating_type=terminal_type)
        ports = [ifcopenshell.api.system.add_port(self.file, element=terminal) for _ in range(2)]

        output = ifcpatch.execute({"file": self.file, "recipe": "ExtractElements", "arguments": ["IfcFlowTerminal"]})

        new_terminal = output.by_type("IfcFlowTerminal")[0]
        assert ifcopenshell.util.element.get_type(new_terminal).is_a("IfcDistributionElementType")
        new_ports = output.by_type("IfcDistributionPort")
        assert len(new_ports) == len(ports)
        rels = output.by_type("IfcRelConnectsPortToElement")
        assert len(rels) == len(ports)
        assert {rel.RelatedElement for rel in rels} == {new_terminal}
        assert {rel.RelatingPort for rel in rels} == set(new_ports)

    def test_keep_spatial_structure(self):
        project = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")

        site = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcSite")
        building = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcBuilding")
        storey = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcBuildingStorey")
        wall = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        ifcopenshell.api.aggregate.assign_object(self.file, products=[building], relating_object=site)
        ifcopenshell.api.aggregate.assign_object(self.file, products=[storey], relating_object=building)
        ifcopenshell.api.spatial.assign_container(self.file, products=[wall], relating_structure=storey)

        output = ifcpatch.execute({"file": self.file, "recipe": "ExtractElements", "arguments": ["IfcWall"]})

        wall_new = output.by_type("IfcWall")[0]
        assert (storey_new := ifcopenshell.util.element.get_container(wall_new)).GlobalId == storey.GlobalId
        assert (building_new := ifcopenshell.util.element.get_aggregate(storey_new)).GlobalId == building.GlobalId
        assert (site_new := ifcopenshell.util.element.get_aggregate(building_new)).GlobalId == site.GlobalId

    def test_extract_without_leaving_orphan_placements(self):
        project = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        site = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcSite")
        storey = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcBuildingStorey")
        ifcopenshell.api.aggregate.assign_object(self.file, products=[site], relating_object=project)
        ifcopenshell.api.aggregate.assign_object(self.file, products=[storey], relating_object=site)
        ifcopenshell.api.geometry.edit_object_placement(self.file, product=site)
        ifcopenshell.api.geometry.edit_object_placement(self.file, product=storey)
        for index in range(2):
            wall = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
            ifcopenshell.api.spatial.assign_container(self.file, products=[wall], relating_structure=storey)
            matrix = numpy.eye(4)
            matrix[0][3] = index + 1.0
            ifcopenshell.api.geometry.edit_object_placement(self.file, product=wall, matrix=matrix)

        output = ifcpatch.execute({"file": self.file, "recipe": "ExtractElements", "arguments": ["IfcWall"]})

        assert len(output.by_type("IfcWall")) == 2
        assert not [placement for placement in output.by_type("IfcLocalPlacement") if not placement.PlacesObject]
        logger = ifcopenshell.validate.json_logger()
        ifcopenshell.validate.validate(output, logger)
        assert not [statement for statement in logger.statements if "PlacesObject" in str(statement)]

    def test_extract_without_orphan_placement_ancestors_of_excluded_products(self):
        project = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        storey = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcBuildingStorey")
        ifcopenshell.api.aggregate.assign_object(self.file, products=[storey], relating_object=project)
        ifcopenshell.api.geometry.edit_object_placement(self.file, product=storey)
        wall = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        opening = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcOpeningElement")
        door = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcDoor")
        ifcopenshell.api.spatial.assign_container(self.file, products=[wall, door], relating_structure=storey)
        ifcopenshell.api.feature.add_feature(self.file, feature=opening, element=wall)
        ifcopenshell.api.feature.add_filling(self.file, element=door, opening=opening)
        matrix = numpy.eye(4)
        matrix[0][3] = 1.0
        ifcopenshell.api.geometry.edit_object_placement(self.file, product=wall, matrix=matrix)
        ifcopenshell.api.geometry.edit_object_placement(self.file, product=opening, matrix=matrix.copy())
        ifcopenshell.api.geometry.edit_object_placement(self.file, product=door, matrix=matrix.copy())

        output = ifcpatch.execute({"file": self.file, "recipe": "ExtractElements", "arguments": ["IfcDoor"]})

        assert output.by_type("IfcDoor")
        assert not output.by_type("IfcWall")
        assert not [placement for placement in output.by_type("IfcLocalPlacement") if not placement.PlacesObject]
        logger = ifcopenshell.validate.json_logger()
        ifcopenshell.validate.validate(output, logger)
        assert not [statement for statement in logger.statements if "PlacesObject" in str(statement)]

    def test_keep_aggregate_in_spatial_structure(self):
        project = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")

        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcElementAssembly")
        container = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcBuildingStorey")
        subelement = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        ifcopenshell.api.spatial.assign_container(self.file, products=[element], relating_structure=container)
        ifcopenshell.api.aggregate.assign_object(self.file, products=[subelement], relating_object=element)

        output = ifcpatch.execute({"file": self.file, "recipe": "ExtractElements", "arguments": ["IfcWall"]})

        wall_new = output.by_type("IfcWall")[0]
        assembly = output.by_type("IfcElementAssembly")[0]

        assert ifcopenshell.util.element.get_aggregate(wall_new).GlobalId == element.GlobalId
        assert ifcopenshell.util.element.get_container(assembly).GlobalId == container.GlobalId

    def test_getting_the_psets_of_a_product_as_a_dictionary(self):
        ifc = ifcopenshell.open(os.path.join(os.path.dirname(__file__), "files", "basic.ifc"))
        output = ifcpatch.execute({"file": ifc, "recipe": "ExtractElements", "arguments": ["IfcWall"]})
        assert output.by_type("IfcWall")
        assert not output.by_type("IfcSlab")

    def test_preserving_georeferencing(self):
        # Regression test for #8199: ExtractElements must carry IfcMapConversion
        # and IfcProjectedCRS into the output. Without the fix these entities are
        # silently dropped because they reference the IfcGeometricRepresentationContext
        # via an inverse attribute and are therefore not reachable through the
        # IfcProject forward-attribute walk used by self.new.add().
        if self.file.schema == "IFC2X3":
            pytest.skip("IfcMapConversion does not exist in IFC2X3")
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        ifcopenshell.api.context.add_context(self.file, context_type="Model")
        ifcopenshell.api.georeference.add_georeferencing(self.file)
        ifcopenshell.api.georeference.edit_georeferencing(
            self.file,
            coordinate_operation={"Eastings": 100000.0, "Northings": 200000.0},
        )
        wall = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        matrix = numpy.eye(4)
        matrix[:3, 3] = [5.0, 10.0, 2.0]
        ifcopenshell.api.geometry.edit_object_placement(self.file, product=wall, matrix=matrix)

        output = ifcpatch.execute({"file": self.file, "recipe": "ExtractElements", "arguments": ["IfcWall"]})

        assert len(output.by_type("IfcMapConversion")) == 1
        assert len(output.by_type("IfcProjectedCRS")) == 1
        conversion = output.by_type("IfcMapConversion")[0]
        assert conversion.Eastings == 100000.0
        assert conversion.Northings == 200000.0
        # Placements must be copied verbatim: extraction must not bake map
        # coordinates (or any other georeferencing transform) into the local
        # placements of the extracted elements.
        wall_new = output.by_type("IfcWall")[0]
        assert wall_new.ObjectPlacement.RelativePlacement.Location.Coordinates == (5.0, 10.0, 2.0)

    def test_preserving_georeferencing_ifc2x3(self):
        # Regression test: IFC2X3 has no IfcMapConversion. Georeferencing is instead
        # stored as ePSet_MapConversion / ePSet_ProjectedCRS property sets on
        # IfcProject, reached only via the inverse IsDefinedBy relationship, so they
        # were dropped by the same forward-attribute-only IfcProject copy that
        # originally lost IfcMapConversion for #8199 (that fix only covered IFC4+).
        # Losing them is worse than silent data loss: append_asset() still globalises
        # each element's placement using the source's georeferencing and, finding
        # none on the target, leaves the globalised (Eastings/Northings-scale)
        # coordinates in place, corrupting every extracted element's placement.
        if self.file.schema != "IFC2X3":
            pytest.skip("ePSet_MapConversion is an IFC2X3-only convention")
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        ifcopenshell.api.georeference.add_georeferencing(self.file)
        ifcopenshell.api.georeference.edit_georeferencing(
            self.file,
            coordinate_operation={
                "Eastings": 500000.0,
                "Northings": 6000000.0,
                "XAxisAbscissa": 0.6,
                "XAxisOrdinate": 0.8,
            },
        )
        wall = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        matrix = numpy.eye(4)
        matrix[:3, 3] = [5.0, 10.0, 2.0]
        ifcopenshell.api.geometry.edit_object_placement(self.file, product=wall, matrix=matrix)

        # ePSet_MapConversion / ePSet_ProjectedCRS are added by add_georeferencing.
        # The other IFC2X3-legal georeferencing psets have no dedicated API and are
        # added directly, as a real-world producer that doesn't use IfcOpenShell
        # would. See https://github.com/buildingSMART/validate/issues/310#issuecomment-5076630963
        # for the complete list this recipe must preserve.
        other_names = ("ePSet_GeographicCRS", "ePSet_MapConversionScaled", "ePSet_RigidOperation")
        for name in other_names:
            pset = ifcopenshell.api.pset.add_pset(self.file, self.file.by_type("IfcProject")[0], name)
            ifcopenshell.api.pset.edit_pset(self.file, pset, properties={"Name": name})

        output = ifcpatch.execute({"file": self.file, "recipe": "ExtractElements", "arguments": ["IfcWall"]})

        project_new = output.by_type("IfcProject")[0]
        conversion = ifcopenshell.util.element.get_pset(project_new, "ePSet_MapConversion")
        assert conversion is not None
        assert conversion["Eastings"] == 500000.0
        assert conversion["Northings"] == 6000000.0
        for name in other_names:
            pset_new = ifcopenshell.util.element.get_pset(project_new, name)
            assert pset_new is not None, f"{name} was dropped"
            assert pset_new["Name"] == name
        # Placements must be copied verbatim: extraction must not bake map
        # coordinates (or any other georeferencing transform) into the local
        # placements of the extracted elements.
        wall_new = output.by_type("IfcWall")[0]
        coords = wall_new.ObjectPlacement.RelativePlacement.Location.Coordinates
        assert coords == pytest.approx((5.0, 10.0, 2.0))

    def test_preserving_georeferencing_ifc2x3_on_site(self):
        # Regression test: several real-world tools (see JoostGevaert's comment on
        # https://github.com/buildingSMART/validate/issues/310#issuecomment-4867354635)
        # attach the IFC2X3 georeferencing psets to IfcSite rather than IfcProject.
        # ExtractElements must preserve them from either location, without
        # duplicating the IfcRelDefinesByProperties relationship.
        if self.file.schema != "IFC2X3":
            pytest.skip("ePSet_MapConversion is an IFC2X3-only convention")
        project = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        site = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcSite")
        ifcopenshell.api.aggregate.assign_object(self.file, products=[site], relating_object=project)
        pset = ifcopenshell.api.pset.add_pset(self.file, site, "ePSet_MapConversion")
        ifcopenshell.api.pset.edit_pset(
            self.file, pset, properties={"Eastings": self.file.createIfcLengthMeasure(500000.0)}
        )
        wall = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        ifcopenshell.api.spatial.assign_container(self.file, products=[wall], relating_structure=site)

        output = ifcpatch.execute({"file": self.file, "recipe": "ExtractElements", "arguments": ["IfcWall"]})

        site_new = output.by_type("IfcSite")[0]
        conversion = ifcopenshell.util.element.get_pset(site_new, "ePSet_MapConversion")
        assert conversion is not None
        assert conversion["Eastings"] == 500000.0
        rels = [r for r in output.by_type("IfcRelDefinesByProperties") if site_new in r.RelatedObjects]
        assert len(rels) == 1, "georeferencing pset must not be linked twice"

    @pytest.mark.skipif(
        "IFC4X3" not in ifcopenshell.ifcopenshell_wrapper.schema_names(),
        reason=(
            "Need some non-standard schema available for this test."
            "IFC4X3 is typically available in the full build, but not in CI."
        ),
    )
    def test_extracting_non_standard_schema_version(self):
        self.file = ifcopenshell.file(schema_version=(4, 3, 0, 0))
        project = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        wall = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        output = ifcpatch.execute({"file": self.file, "recipe": "ExtractElements", "arguments": ["IfcWall"]})
        assert output.by_type("IfcProject")[0].GlobalId == project.GlobalId
        assert output.by_type("IfcWall")[0].GlobalId == wall.GlobalId


class TestExtractElementsIFC2X3(test.bootstrap.IFC2X3, TestExtractElements):
    pass
