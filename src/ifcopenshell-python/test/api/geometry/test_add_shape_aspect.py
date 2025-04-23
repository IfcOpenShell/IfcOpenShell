# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2025 Dion Moult <dion@thinkmoult.com>
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
import ifcopenshell.api.context
import ifcopenshell.api.geometry
import ifcopenshell.util.shape_builder


class TestAddShapeAspect(test.bootstrap.IFC4):
    def test_adding_a_shape_aspect(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        model = ifcopenshell.api.context.add_context(self.file, context_type="Model")
        body = ifcopenshell.api.context.add_context(
            self.file, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=model
        )
        builder = ifcopenshell.util.shape_builder.ShapeBuilder(self.file)
        item = builder.sphere()
        rep = builder.get_representation(body, [item])
        element = ifcopenshell.api.root.create_entity(self.file)
        ifcopenshell.api.geometry.assign_representation(self.file, product=element, representation=rep)

        aspect = ifcopenshell.api.geometry.add_shape_aspect(
            self.file, name="Foo", items=[item], representation=rep, part_of_product=element.Representation
        )
        assert aspect.is_a("IfcShapeAspect")
        assert aspect.PartOfProductDefinitionShape == element.Representation
        assert aspect.Name == "Foo"
        assert len(aspect.ShapeRepresentations) == 1
        aspect_rep = aspect.ShapeRepresentations[0]
        assert aspect_rep != rep
        assert aspect_rep.ContextOfItems == rep.ContextOfItems
        assert aspect_rep.RepresentationIdentifier == rep.RepresentationIdentifier
        assert aspect_rep.RepresentationType == rep.RepresentationType
        assert aspect_rep.Items == (item,)

    def test_adding_a_type_shape_aspect(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        model = ifcopenshell.api.context.add_context(self.file, context_type="Model")
        body = ifcopenshell.api.context.add_context(
            self.file, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=model
        )
        builder = ifcopenshell.util.shape_builder.ShapeBuilder(self.file)
        item = builder.sphere()
        rep = builder.get_representation(body, [item])
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWallType")
        ifcopenshell.api.geometry.assign_representation(self.file, product=element, representation=rep)

        aspect = ifcopenshell.api.geometry.add_shape_aspect(
            self.file, name="Foo", items=[item], representation=rep, part_of_product=element.RepresentationMaps[0]
        )
        assert aspect.is_a("IfcShapeAspect")
        assert aspect.PartOfProductDefinitionShape == element.RepresentationMaps[0]
        assert aspect.Name == "Foo"
        assert len(aspect.ShapeRepresentations) == 1
        aspect_rep = aspect.ShapeRepresentations[0]
        assert aspect_rep != rep
        assert aspect_rep.ContextOfItems == rep.ContextOfItems
        assert aspect_rep.RepresentationIdentifier == rep.RepresentationIdentifier
        assert aspect_rep.RepresentationType == rep.RepresentationType
        assert aspect_rep.Items == (item,)

    def test_reusing_an_existing_aspect(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        model = ifcopenshell.api.context.add_context(self.file, context_type="Model")
        body = ifcopenshell.api.context.add_context(
            self.file, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=model
        )
        builder = ifcopenshell.util.shape_builder.ShapeBuilder(self.file)
        item = builder.sphere()
        item2 = builder.sphere()
        rep = builder.get_representation(body, [item, item2])
        element = ifcopenshell.api.root.create_entity(self.file)
        ifcopenshell.api.geometry.assign_representation(self.file, product=element, representation=rep)

        aspect = ifcopenshell.api.geometry.add_shape_aspect(
            self.file, name="Foo", items=[item], representation=rep, part_of_product=element.Representation
        )
        aspect2 = ifcopenshell.api.geometry.add_shape_aspect(
            self.file, name="Foo", items=[item2], representation=rep, part_of_product=element.Representation
        )
        assert aspect == aspect2
        assert len(aspect.ShapeRepresentations) == 1
        assert set(aspect.ShapeRepresentations[0].Items) == {item, item2}

    def test_removing_from_previous_aspects(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        model = ifcopenshell.api.context.add_context(self.file, context_type="Model")
        body = ifcopenshell.api.context.add_context(
            self.file, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=model
        )
        builder = ifcopenshell.util.shape_builder.ShapeBuilder(self.file)
        item = builder.sphere()
        item2 = builder.sphere()
        rep = builder.get_representation(body, [item, item2])
        element = ifcopenshell.api.root.create_entity(self.file)
        ifcopenshell.api.geometry.assign_representation(self.file, product=element, representation=rep)

        aspect = ifcopenshell.api.geometry.add_shape_aspect(
            self.file, name="Foo", items=[item, item2], representation=rep, part_of_product=element.Representation
        )
        aspect2 = ifcopenshell.api.geometry.add_shape_aspect(
            self.file, name="Bar", items=[item2], representation=rep, part_of_product=element.Representation
        )
        assert aspect != aspect2
        assert aspect.Name == "Foo"
        assert aspect.ShapeRepresentations[0].Items == (item,)
        assert aspect2.Name == "Bar"
        assert aspect2.ShapeRepresentations[0].Items == (item2,)

    def test_take_context_into_account(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        model = ifcopenshell.api.context.add_context(self.file, context_type="Model")
        body = ifcopenshell.api.context.add_context(
            self.file, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=model
        )
        box = ifcopenshell.api.context.add_context(
            self.file, context_type="Model", context_identifier="Box", target_view="MODEL_VIEW", parent=model
        )
        builder = ifcopenshell.util.shape_builder.ShapeBuilder(self.file)
        item = builder.sphere()
        item2 = builder.sphere()
        rep = builder.get_representation(body, [item, item2])
        rep2 = builder.get_representation(box, [item, item2])
        element = ifcopenshell.api.root.create_entity(self.file)
        ifcopenshell.api.geometry.assign_representation(self.file, product=element, representation=rep)
        ifcopenshell.api.geometry.assign_representation(self.file, product=element, representation=rep2)

        aspect = ifcopenshell.api.geometry.add_shape_aspect(
            self.file, name="Foo", items=[item, item2], representation=rep, part_of_product=element.Representation
        )
        aspect2 = ifcopenshell.api.geometry.add_shape_aspect(
            self.file, name="Foo", items=[item2], representation=rep2, part_of_product=element.Representation
        )
        assert aspect == aspect2
        assert aspect.Name == "Foo"
        assert len(aspect.ShapeRepresentations) == 2
        assert aspect.ShapeRepresentations[0].ContextOfItems == rep.ContextOfItems
        assert aspect.ShapeRepresentations[1].ContextOfItems == rep2.ContextOfItems
        assert set(aspect.ShapeRepresentations[0].Items) == {item, item2}
        assert aspect.ShapeRepresentations[1].Items == (item2,)


class TestAddShapeAspectIFC2X3(test.bootstrap.IFC2X3, TestAddShapeAspect):
    def test_adding_a_type_shape_aspect(self):
        pass  # Not allowed
