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
import ifcopenshell.util.classification
import ifcopenshell.util.constraint
import ifcopenshell.util.element
import ifcopenshell.util.system
from datetime import datetime
from typing import Union


def deprecation_check(test):
    def new_test(self):
        assert datetime.now().date() < datetime(2024, 8, 1).date(), "API arguments are completely deprecated"
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

    @deprecation_check
    def test_assigning_a_nesting(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcSanitaryTerminal")
        subelement = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcValve")
        rel = ifcopenshell.api.run("nest.assign_object", self.file, related_object=subelement, relating_object=element)
        assert ifcopenshell.util.element.get_nest(subelement) == element
        assert rel.is_a("IfcRelNests")

    @deprecation_check
    def test_unassigning_an_nesting(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcTask")
        subelement1 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcTask")
        ifcopenshell.api.run("nest.assign_object", self.file, related_objects=[subelement1], relating_object=element)
        ifcopenshell.api.run("nest.unassign_object", self.file, related_object=subelement1)
        assert ifcopenshell.util.element.get_nest(subelement1) is None

    @deprecation_check
    def test_assigning_a_type(self):
        element1 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        element_type = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWallType")
        rel = ifcopenshell.api.run("type.assign_type", self.file, related_object=element1, relating_type=element_type)
        assert ifcopenshell.util.element.get_type(element1) == element_type
        assert rel.is_a("IfcRelDefinesByType")

    @deprecation_check
    def test_unassigning_a_type(self):
        element_type = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWallType")
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        ifcopenshell.api.run("type.assign_type", self.file, related_objects=[element], relating_type=element_type)
        ifcopenshell.api.run("type.unassign_type", self.file, related_object=element)
        assert ifcopenshell.util.element.get_type(element) is None

    @deprecation_check
    def test_assign_system(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcPump")
        system = ifcopenshell.api.run("system.add_system", self.file)

        # assign group for multiple elements
        ifcopenshell.api.run("system.assign_system", self.file, product=element, system=system)
        assert len(rels := self.file.by_type("IfcRelAssignsToGroup")) == 1
        rel = rels[0]
        assert rel.RelatingGroup == system
        assert rel.RelatedObjects == (element,)

    @deprecation_check
    def test_unassign_system(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcFlowSegment")
        element2 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcFlowSegment")
        system = ifcopenshell.api.run("system.add_system", self.file)
        ifcopenshell.api.run("system.assign_system", self.file, products=[element, element2], system=system)
        ifcopenshell.api.run("system.unassign_system", self.file, product=element, system=system)
        assert ifcopenshell.util.system.get_system_elements(system) == [element2]

        ifcopenshell.api.run("system.unassign_system", self.file, product=element2, system=system)
        assert ifcopenshell.util.system.get_system_elements(system) == []

    @deprecation_check
    def test_assign_element_single_material(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        material = ifcopenshell.api.run("material.add_material", self.file, name="CON01")
        ifcopenshell.api.run(
            "material.assign_material", self.file, product=element, type="IfcMaterial", material=material
        )
        assert len(self.file.by_type("IfcRelAssociatesMaterial")) == 1
        assert element.HasAssociations[0].RelatingMaterial == material

    @deprecation_check
    def test_unassign_single_material(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        material = ifcopenshell.api.run("material.add_material", self.file, name="CON01")
        ifcopenshell.api.run(
            "material.assign_material", self.file, products=[element], type="IfcMaterial", material=material
        )
        ifcopenshell.api.run("material.unassign_material", self.file, product=element)
        assert len(self.file.by_type("IfcRelAssociatesMaterial")) == 0
        assert len(self.file.by_type("IfcWall")) == 1
        assert len(self.file.by_type("IfcMaterial")) == 1

    @deprecation_check
    def test_adding_a_reference(self):
        ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcProject")
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        result = ifcopenshell.api.run("classification.add_classification", self.file, classification="Name")
        ifcopenshell.api.run(
            "classification.add_reference",
            self.file,
            product=element,
            identification="X",
            name="Foobar",
            classification=result,
        )
        references = list(ifcopenshell.util.classification.get_references(element))
        assert len(references) == 1
        assert references[0].Identification == "X"
        assert references[0].Name == "Foobar"
        assert references[0].ReferencedSource == self.file.by_type("IfcClassification")[0]

        element2 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        ifcopenshell.api.run(
            "classification.add_reference",
            self.file,
            product=element2,
            identification="X",
            name="Foobar",
            classification=result,
        )
        assert list(ifcopenshell.util.classification.get_references(element2))[0].Identification == "X"
        assert list(ifcopenshell.util.classification.get_references(element2))[0].Name == "Foobar"
        assert list(ifcopenshell.util.classification.get_references(element2))[0] == references[0]

    @deprecation_check
    def test_removing_a_reference(self):
        ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcProject")
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        result = ifcopenshell.api.run("classification.add_classification", self.file, classification="Name")
        reference = ifcopenshell.api.run(
            "classification.add_reference",
            self.file,
            products=[element],
            identification="X",
            name="Foobar",
            classification=result,
        )
        ifcopenshell.api.run("classification.remove_reference", self.file, product=element, reference=reference)
        assert len(ifcopenshell.util.classification.get_references(element)) == 0
        assert len(self.file.by_type("IfcClassificationReference")) == 0

    @deprecation_check
    def test_assigning_a_reference(self):
        reference = self.file.createIfcLibraryReference()
        product = self.file.createIfcWall()
        product2 = self.file.createIfcWall()
        ifcopenshell.api.run("library.assign_reference", self.file, product=product, reference=reference)
        assert reference.LibraryRefForObjects[0].RelatedObjects == (product,)
        ifcopenshell.api.run("library.assign_reference", self.file, product=product2, reference=reference)
        assert set(reference.LibraryRefForObjects[0].RelatedObjects) == set((product, product2))

    @deprecation_check
    def test_unassigning_a_reference(self):
        reference = self.file.createIfcLibraryReference()
        product = self.file.createIfcWall()
        ifcopenshell.api.run("library.assign_reference", self.file, products=[product], reference=reference)
        ifcopenshell.api.run("library.unassign_reference", self.file, product=product, reference=reference)
        assert len(self.file.by_type("IfcRelAssociatesLibrary")) == 0

    @deprecation_check
    def test_assigning_a_document(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        reference = ifcopenshell.api.run("document.add_reference", self.file, information=None)
        ifcopenshell.api.run("document.assign_document", self.file, product=element, document=reference)
        assert element.HasAssociations[0].RelatingDocument == reference

    @deprecation_check
    def test_unassigning_a_document(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        reference = ifcopenshell.api.run("document.add_reference", self.file, information=None)
        ifcopenshell.api.run("document.assign_document", self.file, products=[element], document=reference)
        ifcopenshell.api.run("document.unassign_document", self.file, product=element, document=reference)
        assert not element.HasAssociations
        assert not len(self.file.by_type("IfcRelAssociatesDocument"))

    @deprecation_check
    def test_referencing_a_structure(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcBuilding")
        subelement = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        rel = ifcopenshell.api.run(
            "spatial.reference_structure", self.file, product=subelement, relating_structure=element
        )
        assert ifcopenshell.util.element.get_referenced_structures(subelement) == [element]
        assert rel.is_a("IfcRelReferencedInSpatialStructure")

    @deprecation_check
    def test_removing_a_structure(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcBuilding")
        subelement = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        ifcopenshell.api.run(
            "spatial.reference_structure", self.file, products=[subelement], relating_structure=element
        )
        ifcopenshell.api.run("spatial.dereference_structure", self.file, product=subelement, relating_structure=element)
        assert ifcopenshell.util.element.get_referenced_structures(subelement) == []

    @deprecation_check
    def test_assign_a_constraint(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        constraint = ifcopenshell.api.run("constraint.add_objective", self.file)
        ifcopenshell.api.run("constraint.assign_constraint", self.file, product=element, constraint=constraint)
        assert ifcopenshell.util.constraint.get_constrained_elements(constraint) == {element}

    @deprecation_check
    def test_unassigning_a_constraint(self):
        constraint = ifcopenshell.api.run("constraint.add_objective", self.file)
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        ifcopenshell.api.run("constraint.assign_constraint", self.file, product=element, constraint=constraint)
        ifcopenshell.api.run("constraint.unassign_constraint", self.file, product=element, constraint=constraint)
        assert ifcopenshell.util.constraint.get_constrained_elements(element) == set()
        assert len(self.file.by_type("IfcRelAssociatesConstraint")) == 0

    @deprecation_check
    def test_assign_a_declaration(self):
        def get_declared_definitions(project: ifcopenshell.entity_instance) -> set[ifcopenshell.entity_instance]:
            definitions = set()
            for declares in project.Declares:
                definitions.update(declares.RelatedDefinitions)
            return definitions

        element_type = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWallType")
        library = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcProjectLibrary")
        ifcopenshell.api.run(
            "project.assign_declaration",
            self.file,
            definition=element_type,
            relating_context=library,
        )
        assert get_declared_definitions(library) == {element_type}
        assert len(self.file.by_type("IfcRelDeclares")) == 1

    @deprecation_check
    def test_unassigning_a_definition(self):
        def get_context(definition: ifcopenshell.entity_instance) -> Union[ifcopenshell.entity_instance, None]:
            rel = next(iter(definition.HasContext), None)
            if rel is not None:
                return rel.RelatingContext

        library = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcProjectLibrary")
        element_type = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWallType")
        ifcopenshell.api.run(
            "project.assign_declaration", self.file, definitions=[element_type], relating_context=library
        )
        ifcopenshell.api.run(
            "project.unassign_declaration",
            self.file,
            definition=element_type,
            relating_context=library,
        )
        assert get_context(element_type) == None
        assert len(self.file.by_type("IfcRelDeclares")) == 0

    @deprecation_check
    def test_add_group(self):
        group = ifcopenshell.api.run("group.add_group", self.file, Name="Name", Description="Description")
        assert group.Name == "Name"
        assert group.Description == "Description"

    @deprecation_check
    def test_add_layer(self):
        layer = ifcopenshell.api.run("layer.add_layer", self.file, Name="Name")
        assert layer.Name == "Name"
