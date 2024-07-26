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
import ifcopenshell.api.root
import ifcopenshell.api.type
import ifcopenshell.api.material
import ifcopenshell.api.geometry
import ifcopenshell.util.element
import ifcopenshell.util.representation
import pytest


class TestAssignType(test.bootstrap.IFC4):
    def test_assigning_a_type(self):
        element1 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        element2 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        element_type = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWallType")
        rel = ifcopenshell.api.type.assign_type(
            self.file, related_objects=[element1, element2], relating_type=element_type
        )
        assert ifcopenshell.util.element.get_type(element1) == element_type
        assert ifcopenshell.util.element.get_type(element2) == element_type
        assert rel.is_a("IfcRelDefinesByType")

    def test_doing_nothing_if_type_is_already_assigned(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        element_type = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWallType")
        ifcopenshell.api.type.assign_type(self.file, related_objects=[element], relating_type=element_type)
        total_elements = len([e for e in self.file])
        ifcopenshell.api.type.assign_type(self.file, related_objects=[element], relating_type=element_type)
        assert len([e for e in self.file]) == total_elements

    def test_that_old_typing_relationships_are_updated_if_they_still_have_elements(self):
        element_type1 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWallType")
        element_type2 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWallType")
        element1 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        element2 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        ifcopenshell.api.type.assign_type(self.file, related_objects=[element1, element2], relating_type=element_type1)
        rel = element1.IsDefinedBy[0] if self.file.schema == "IFC2X3" else element1.IsTypedBy[0]
        assert len(rel.RelatedObjects) == 2
        ifcopenshell.api.type.assign_type(self.file, related_objects=[element1], relating_type=element_type2)
        assert len(rel.RelatedObjects) == 1

    def test_that_old_typing_relationships_are_purged_if_no_more_elements_are_nested(self):
        element_type1 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWallType")
        element_type2 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWallType")
        element1 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        ifcopenshell.api.type.assign_type(self.file, related_objects=[element1], relating_type=element_type1)
        rel_id = (element1.IsDefinedBy[0] if self.file.schema == "IFC2X3" else element1.IsTypedBy[0]).id()
        ifcopenshell.api.type.assign_type(self.file, related_objects=[element1], relating_type=element_type2)
        with pytest.raises(RuntimeError):
            self.file.by_id(rel_id)

    def test_map_representation_disabled(self):
        element_type = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWallType")
        context = self.file.createIfcGeometricRepresentationContext()
        rep = self.file.createIfcShapeRepresentation(ContextOfItems=context)
        ifcopenshell.api.geometry.assign_representation(self.file, product=element_type, representation=rep)
        ifcopenshell.api.material.assign_material(self.file, products=[element_type], type="IfcMaterialLayerSet")

        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        ifcopenshell.api.type.assign_type(
            self.file,
            related_objects=[element],
            relating_type=element_type,
            should_map_representations=False,
        )

        # no representation mapping and no material usage
        assert ifcopenshell.util.representation.get_representation(element, context=context) == None
        assert ifcopenshell.util.element.get_material(element, should_inherit=False) == None

    def test_map_representation(self):
        element_type = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWallType")
        context = self.file.createIfcGeometricRepresentationContext()
        rep = self.file.createIfcShapeRepresentation(ContextOfItems=context)
        ifcopenshell.api.geometry.assign_representation(self.file, product=element_type, representation=rep)
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        ifcopenshell.api.type.assign_type(self.file, related_objects=[element], relating_type=element_type)
        mapped_rep = ifcopenshell.util.representation.get_representation(element, context=context)
        assert mapped_rep.RepresentationType == "MappedRepresentation"
        assert mapped_rep.Items[0].MappingSource.MappedRepresentation == rep

    def test_do_not_map_representation_if_type_was_assigned_previously(self):
        element_type = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWallType")
        context = self.file.createIfcGeometricRepresentationContext()
        rep = self.file.createIfcShapeRepresentation(ContextOfItems=context)
        ifcopenshell.api.geometry.assign_representation(self.file, product=element_type, representation=rep)
        element1 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        ifcopenshell.api.type.assign_type(self.file, related_objects=[element1], relating_type=element_type)
        assert (mapped_rep := ifcopenshell.util.representation.get_representation(element1, context=context))
        mapped_rep_id = mapped_rep.id()

        element2 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        ifcopenshell.api.type.assign_type(self.file, related_objects=[element1, element2], relating_type=element_type)
        assert (mapped_rep := ifcopenshell.util.representation.get_representation(element1, context=context))
        assert mapped_rep.id() == mapped_rep_id

    def test_map_material_usages(self):
        material_types = ("IfcMaterialLayerSet",)
        if self.file.schema != "IFC2X3":
            material_types += ("IfcMaterialProfileSet",)
        for material_type in material_types:
            element_type = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWallType")
            ifcopenshell.api.material.assign_material(self.file, products=[element_type], type=material_type)
            element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
            ifcopenshell.api.type.assign_type(self.file, related_objects=[element], relating_type=element_type)
            material = ifcopenshell.util.element.get_material(element)
            assert material
            assert material.is_a(f"{material_type}Usage")

    def test_do_not_reassign_material_if_it_was_assigned_previously(self):
        element1 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        element_type = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWallType")
        ifcopenshell.api.material.assign_material(self.file, products=[element_type], type="IfcMaterialLayerSet")
        ifcopenshell.api.type.assign_type(self.file, related_objects=[element1], relating_type=element_type)
        assert (material := ifcopenshell.util.element.get_material(element1))
        material_id = material.id()

        # use 2 elements to trigger material assignment code block
        element2 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        ifcopenshell.api.type.assign_type(self.file, related_objects=[element1, element2], relating_type=element_type)
        assert (material := ifcopenshell.util.element.get_material(element1))
        assert material.id() == material_id


class TestAssignTypeIFC2X3(test.bootstrap.IFC2X3, TestAssignType):
    pass
