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


class TestAppendAsset(test.bootstrap.IFC4):
    def test_do_not_append_twice(self):
        library = ifcopenshell.api.run("project.create_file")
        element = ifcopenshell.api.run("root.create_entity", library, ifc_class="IfcWallType")
        material = ifcopenshell.api.run("material.add_material", library, name="Material")
        schedule = ifcopenshell.api.run("cost.add_cost_schedule", library, name="Schedule")
        profile = library.createIfcIShapeProfileDef()

        ifcopenshell.api.run("project.append_asset", self.file, library=library, element=element)
        ifcopenshell.api.run("project.append_asset", self.file, library=library, element=element)
        ifcopenshell.api.run("project.append_asset", self.file, library=library, element=material)
        ifcopenshell.api.run("project.append_asset", self.file, library=library, element=material)
        ifcopenshell.api.run("project.append_asset", self.file, library=library, element=schedule)
        ifcopenshell.api.run("project.append_asset", self.file, library=library, element=schedule)
        ifcopenshell.api.run("project.append_asset", self.file, library=library, element=profile)
        ifcopenshell.api.run("project.append_asset", self.file, library=library, element=profile)
        assert len(self.file.by_type("IfcWallType")) == 1

    def test_append_a_type_product(self):
        library = ifcopenshell.api.run("project.create_file")
        element = ifcopenshell.api.run("root.create_entity", library, ifc_class="IfcWallType")
        ifcopenshell.api.run("project.append_asset", self.file, library=library, element=element)
        assert len(self.file.by_type("IfcWallType")) == 1

    def test_append_a_single_type_product_even_though_an_inverse_material_relationship_is_shared(self):
        library = ifcopenshell.api.run("project.create_file")
        element = ifcopenshell.api.run("root.create_entity", library, ifc_class="IfcWallType")
        element2 = ifcopenshell.api.run("root.create_entity", library, ifc_class="IfcWallType")
        material = ifcopenshell.api.run("material.add_material", library, name="Material")
        ifcopenshell.api.run("material.assign_material", library, product=element, material=material)
        ifcopenshell.api.run("material.assign_material", library, product=element2, material=material)
        ifcopenshell.api.run("project.append_asset", self.file, library=library, element=element)
        assert len(self.file.by_type("IfcWallType")) == 1

    def test_append_a_type_product_with_its_materials(self):
        library = ifcopenshell.api.run("project.create_file")
        element = ifcopenshell.api.run("root.create_entity", library, ifc_class="IfcWallType")
        material = ifcopenshell.api.run("material.add_material", library, name="Material")
        ifcopenshell.api.run("material.assign_material", library, product=element, material=material)
        ifcopenshell.api.run("project.append_asset", self.file, library=library, element=element)
        assert self.file.by_type("IfcWallType")[0].HasAssociations[0].RelatingMaterial.Name == "Material"

    def test_append_a_type_product_with_its_styles(self):
        library = ifcopenshell.api.run("project.create_file")
        element = ifcopenshell.api.run("root.create_entity", library, ifc_class="IfcWallType")
        item = library.createIfcBoundingBox()
        library.createIfcStyledItem(Item=item)
        mapped_rep = library.createIfcShapeRepresentation(Items=[item])
        element.RepresentationMaps = [library.createIfcRepresentationMap(MappedRepresentation=mapped_rep)]
        new = ifcopenshell.api.run("project.append_asset", self.file, library=library, element=element)
        assert len(new.RepresentationMaps[0].MappedRepresentation.Items[0].StyledByItem) == 1
        assert self.file.by_type("IfcStyledItem")[0].Item == self.file.by_type("IfcBoundingBox")[0]

    def test_append_a_material(self):
        library = ifcopenshell.api.run("project.create_file")
        material = ifcopenshell.api.run("material.add_material", library, name="Material")
        ifcopenshell.api.run("project.append_asset", self.file, library=library, element=material)
        assert len(self.file.by_type("IfcMaterial")) == 1

    def test_append_a_material_with_a_representation(self):
        ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcProject")

        library = ifcopenshell.api.run("project.create_file")
        ifcopenshell.api.run("root.create_entity", library, ifc_class="IfcProject")
        material = ifcopenshell.api.run("material.add_material", library, name="Material")
        style = ifcopenshell.api.run("style.add_style", library)
        context = ifcopenshell.api.run("context.add_context", library, context_type="Model")
        ifcopenshell.api.run("style.assign_material_style", library, material=material, style=style, context=context)
        ifcopenshell.api.run("project.append_asset", self.file, library=library, element=material)
        assert len(self.file.by_type("IfcMaterial")) == 1
        assert len(self.file.by_type("IfcGeometricRepresentationContext")) == 1
        context = self.file.by_type("IfcMaterial")[0].HasRepresentation[0].Representations[0].ContextOfItems
        assert context.ContextType == "Model"

    def test_append_a_material_with_a_representation_and_reuse_an_existing_context(self):
        ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcProject")
        file_context = ifcopenshell.api.run("context.add_context", self.file, context_type="Model")

        library = ifcopenshell.api.run("project.create_file")
        ifcopenshell.api.run("root.create_entity", library, ifc_class="IfcProject")
        material = ifcopenshell.api.run("material.add_material", library, name="Material")
        style = ifcopenshell.api.run("style.add_style", library)
        context = ifcopenshell.api.run("context.add_context", library, context_type="Model")
        ifcopenshell.api.run("style.assign_material_style", library, material=material, style=style, context=context)
        ifcopenshell.api.run("project.append_asset", self.file, library=library, element=material)
        assert len(self.file.by_type("IfcMaterial")) == 1
        assert len(self.file.by_type("IfcGeometricRepresentationContext")) == 1
        context = self.file.by_type("IfcMaterial")[0].HasRepresentation[0].Representations[0].ContextOfItems
        assert context == file_context
        assert context.WorldCoordinateSystem

    def test_append_a_material_with_a_representation_and_reuse_an_existing_subcontext(self):
        ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcProject")
        file_context = ifcopenshell.api.run("context.add_context", self.file, context_type="Model")
        file_subcontext = ifcopenshell.api.run("context.add_context", self.file, parent=file_context, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW")

        library = ifcopenshell.api.run("project.create_file")
        ifcopenshell.api.run("root.create_entity", library, ifc_class="IfcProject")
        material = ifcopenshell.api.run("material.add_material", library, name="Material")
        style = ifcopenshell.api.run("style.add_style", library)
        context = ifcopenshell.api.run("context.add_context", library, context_type="Model")
        subcontext = ifcopenshell.api.run("context.add_context", library, parent=context, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW")
        ifcopenshell.api.run("style.assign_material_style", library, material=material, style=style, context=subcontext)
        ifcopenshell.api.run("project.append_asset", self.file, library=library, element=material)
        assert len(self.file.by_type("IfcMaterial")) == 1
        assert len(self.file.by_type("IfcGeometricRepresentationContext", include_subtypes=False)) == 1
        assert len(self.file.by_type("IfcGeometricRepresentationSubContext", include_subtypes=False)) == 1
        subcontext = self.file.by_type("IfcMaterial")[0].HasRepresentation[0].Representations[0].ContextOfItems
        assert subcontext == file_subcontext
        assert subcontext.ParentContext.WorldCoordinateSystem

    def test_append_a_material_with_a_representation_and_reuse_an_existing_context_by_a_new_subcontext(self):
        ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcProject")
        file_context = ifcopenshell.api.run("context.add_context", self.file, context_type="Model")

        library = ifcopenshell.api.run("project.create_file")
        ifcopenshell.api.run("root.create_entity", library, ifc_class="IfcProject")
        material = ifcopenshell.api.run("material.add_material", library, name="Material")
        style = ifcopenshell.api.run("style.add_style", library)
        context = ifcopenshell.api.run("context.add_context", library, context_type="Model")
        subcontext = ifcopenshell.api.run("context.add_context", library, context_type="Model",
                context_identifier="Body", target_view="MODEL_VIEW", parent=context)
        ifcopenshell.api.run("style.assign_material_style", library, material=material, style=style, context=subcontext)
        ifcopenshell.api.run("project.append_asset", self.file, library=library, element=material)
        assert len(self.file.by_type("IfcMaterial")) == 1
        assert len(self.file.by_type("IfcGeometricRepresentationContext", include_subtypes=False)) == 1
        assert len(self.file.by_type("IfcGeometricRepresentationSubContext", include_subtypes=False)) == 1
        subcontext = self.file.by_type("IfcMaterial")[0].HasRepresentation[0].Representations[0].ContextOfItems
        assert subcontext.ContextType == "Model"
        assert subcontext.ContextIdentifier == "Body"
        assert subcontext.TargetView == "MODEL_VIEW"
        assert subcontext.ParentContext == file_context

    def test_append_a_cost_schedule(self):
        library = ifcopenshell.api.run("project.create_file")
        schedule = ifcopenshell.api.run("cost.add_cost_schedule", library, name="Schedule")
        item = ifcopenshell.api.run("cost.add_cost_item", library, cost_schedule=schedule)
        item2 = ifcopenshell.api.run("cost.add_cost_item", library, cost_item=item)
        ifcopenshell.api.run("project.append_asset", self.file, library=library, element=schedule)
        assert len(self.file.by_type("IfcCostSchedule")) == 1
        assert len(self.file.by_type("IfcCostItem")) == 2
        assert self.file.by_type("IfcCostSchedule")[0].Name == "Schedule"
        appended_item = self.file.by_type("IfcCostSchedule")[0].Controls[0].RelatedObjects[0]
        assert appended_item.is_a("IfcCostItem")
        assert appended_item.IsNestedBy[0].RelatedObjects[0].is_a("IfcCostItem")

    def test_append_a_profile_def(self):
        library = ifcopenshell.api.run("project.create_file")
        profile = library.createIfcIShapeProfileDef()
        ifcopenshell.api.run("project.append_asset", self.file, library=library, element=profile)
        assert len(self.file.by_type("IfcIShapeProfileDef")) == 1

    def test_append_a_profile_def_with_all_properties(self):
        library = ifcopenshell.api.run("project.create_file")
        profile = library.createIfcIShapeProfileDef()
        ifcopenshell.api.run("pset.add_pset", library, product=profile, name="Foo_Bar")
        ifcopenshell.api.run("project.append_asset", self.file, library=library, element=profile)
        assert len(self.file.by_type("IfcIShapeProfileDef")) == 1
        assert self.file.by_type("IfcIShapeProfileDef")[0].HasProperties[0].Name == "Foo_Bar"

    def test_append_a_product(self):
        library = ifcopenshell.api.run("project.create_file")
        element = ifcopenshell.api.run("root.create_entity", library, ifc_class="IfcWall")
        ifcopenshell.api.run("project.append_asset", self.file, library=library, element=element)
        assert len(self.file.by_type("IfcWall")) == 1

    def test_append_a_product_with_all_properties(self):
        library = ifcopenshell.api.run("project.create_file")
        element = ifcopenshell.api.run("root.create_entity", library, ifc_class="IfcWall")
        ifcopenshell.api.run("pset.add_pset", library, product=element, name="Foo_Bar")
        ifcopenshell.api.run("project.append_asset", self.file, library=library, element=element)
        assert ifcopenshell.util.element.get_psets(self.file.by_type("IfcWall")[0])["Foo_Bar"]

    def test_append_a_product_with_its_type(self):
        library = ifcopenshell.api.run("project.create_file")
        element = ifcopenshell.api.run("root.create_entity", library, ifc_class="IfcWall")
        element_type = ifcopenshell.api.run("root.create_entity", library, ifc_class="IfcWallType")
        ifcopenshell.api.run("type.assign_type", library, related_object=element, relating_type=element_type)
        ifcopenshell.api.run("project.append_asset", self.file, library=library, element=element)
        assert ifcopenshell.util.element.get_type(self.file.by_type("IfcWall")[0]).is_a("IfcWallType")

    def test_append_only_specified_occurrences_of_a_typed_product(self):
        library = ifcopenshell.api.run("project.create_file")
        element = ifcopenshell.api.run("root.create_entity", library, ifc_class="IfcWall")
        element2 = ifcopenshell.api.run("root.create_entity", library, ifc_class="IfcWall")
        element3 = ifcopenshell.api.run("root.create_entity", library, ifc_class="IfcWall")
        element_type = ifcopenshell.api.run("root.create_entity", library, ifc_class="IfcWallType")
        ifcopenshell.api.run("type.assign_type", library, related_object=element, relating_type=element_type)
        ifcopenshell.api.run("type.assign_type", library, related_object=element2, relating_type=element_type)
        ifcopenshell.api.run("type.assign_type", library, related_object=element3, relating_type=element_type)
        ifcopenshell.api.run("project.append_asset", self.file, library=library, element=element)
        ifcopenshell.api.run("project.append_asset", self.file, library=library, element=element2)
        assert len(ifcopenshell.util.element.get_types(self.file.by_type("IfcWallType")[0])) == 2
        assert len(self.file.by_type("IfcWall")) == 2

    def test_append_a_product_with_materials(self):
        library = ifcopenshell.api.run("project.create_file")
        element = ifcopenshell.api.run("root.create_entity", library, ifc_class="IfcWall")
        material = ifcopenshell.api.run("material.add_material", library, name="Material")
        ifcopenshell.api.run("material.assign_material", library, product=element, material=material)
        ifcopenshell.api.run("project.append_asset", self.file, library=library, element=element)
        assert ifcopenshell.util.element.get_material(self.file.by_type("IfcWall")[0]).Name == "Material"

    def test_append_a_product_with_its_styles(self):
        library = ifcopenshell.api.run("project.create_file")
        element = ifcopenshell.api.run("root.create_entity", library, ifc_class="IfcWall")
        item = library.createIfcBoundingBox()
        library.createIfcStyledItem(Item=item)
        representation = library.createIfcShapeRepresentation(Items=[item])
        element.Representation = library.createIfcProductDefinitionShape(Representations=[representation])
        ifcopenshell.api.run("project.append_asset", self.file, library=library, element=element)
        assert self.file.by_type("IfcStyledItem")[0].Item == self.file.by_type("IfcBoundingBox")[0]

    def test_append_a_product_with_openings(self):
        library = ifcopenshell.api.run("project.create_file")
        element = ifcopenshell.api.run("root.create_entity", library, ifc_class="IfcWall")
        opening = ifcopenshell.api.run("root.create_entity", library, ifc_class="IfcOpeningElement")
        ifcopenshell.api.run("void.add_opening", library, opening=opening, element=element)
        ifcopenshell.api.run("project.append_asset", self.file, library=library, element=element)
        assert self.file.by_type("IfcWall")[0].HasOpenings[0].RelatedOpeningElement.is_a("IfcOpeningElement")


class TestAppendAssetIFC2X3(test.bootstrap.IFC2X3):
    def test_append_a_product_with_its_type(self):
        library = ifcopenshell.api.run("project.create_file", version="IFC2X3")
        element = ifcopenshell.api.run("root.create_entity", library, ifc_class="IfcWall")
        element_type = ifcopenshell.api.run("root.create_entity", library, ifc_class="IfcWallType")
        ifcopenshell.api.run("type.assign_type", library, related_object=element, relating_type=element_type)
        ifcopenshell.api.run("project.append_asset", self.file, library=library, element=element)
        assert ifcopenshell.util.element.get_type(self.file.by_type("IfcWall")[0]).is_a("IfcWallType")

    def test_append_only_specified_occurrences_of_a_typed_product(self):
        library = ifcopenshell.api.run("project.create_file", version="IFC2X3")
        element = ifcopenshell.api.run("root.create_entity", library, ifc_class="IfcWall")
        element2 = ifcopenshell.api.run("root.create_entity", library, ifc_class="IfcWall")
        element3 = ifcopenshell.api.run("root.create_entity", library, ifc_class="IfcWall")
        element_type = ifcopenshell.api.run("root.create_entity", library, ifc_class="IfcWallType")
        ifcopenshell.api.run("type.assign_type", library, related_object=element, relating_type=element_type)
        ifcopenshell.api.run("type.assign_type", library, related_object=element2, relating_type=element_type)
        ifcopenshell.api.run("type.assign_type", library, related_object=element3, relating_type=element_type)
        ifcopenshell.api.run("project.append_asset", self.file, library=library, element=element)
        ifcopenshell.api.run("project.append_asset", self.file, library=library, element=element2)
        assert len(ifcopenshell.util.element.get_types(self.file.by_type("IfcWallType")[0])) == 2
        assert len(self.file.by_type("IfcWall")) == 2
