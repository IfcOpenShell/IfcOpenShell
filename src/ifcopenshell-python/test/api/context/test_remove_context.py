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

import ifcopenshell.api.context
import ifcopenshell.api.geometry
import ifcopenshell.api.root
import test.bootstrap


class TestRemoveContext(test.bootstrap.IFC4):
    def test_removing_a_context(self):
        context = self.file.createIfcGeometricRepresentationContext()
        ifcopenshell.api.context.remove_context(self.file, context=context)
        assert len(self.file.by_type("IfcGeometricRepresentationContext")) == 0

    def test_removing_a_context_with_subcontexts(self):
        context = self.file.createIfcGeometricRepresentationContext()
        subcontext = self.file.createIfcGeometricRepresentationSubcontext()
        subcontext.ParentContext = context
        ifcopenshell.api.context.remove_context(self.file, context=context)
        assert len(self.file.by_type("IfcGeometricRepresentationContext")) == 0

    def test_removing_a_subcontext_and_reassigning_references_to_its_parent(self):
        context = self.file.createIfcGeometricRepresentationContext()
        subcontext = self.file.createIfcGeometricRepresentationSubcontext()
        subcontext.ParentContext = context
        representation = self.file.createIfcRepresentation(ContextOfItems=subcontext)
        if self.file.schema != "IFC2X3":
            projected_crs = self.file.createIfcProjectedCRS()
            map_conversion = self.file.createIfcMapConversion(SourceCRS=subcontext, TargetCRS=projected_crs)
        ifcopenshell.api.context.remove_context(self.file, context=subcontext)
        assert len(self.file.by_type("IfcGeometricRepresentationSubcontext")) == 0
        assert representation in self.file.get_inverse(context)
        if self.file.schema != "IFC2X3":
            assert len(self.file.by_type("IfcMapConversion")) == 0
            assert len(self.file.by_type("IfcProjectedCRS")) == 0

    def test_removing_a_context_with_assigned_representations(self):
        context = self.file.createIfcGeometricRepresentationContext()
        element = ifcopenshell.api.root.create_entity(self.file)
        rep = self.file.createIfcRepresentation(ContextOfItems=context)
        ifcopenshell.api.geometry.assign_representation(self.file, product=element, representation=rep)
        ifcopenshell.api.context.remove_context(self.file, context=context)
        if self.file.schema == "IFC2X3":
            assert len([e for e in self.file]) == 6
        else:
            assert len([e for e in self.file]) == 1

    def test_removing_a_context_used_by_two_products_sharing_one_shape(self):
        # two products referencing the exact same IfcProductDefinitionShape
        # (eg. Revit-authored files, #9207) must not crash and must not
        # leak an orphaned representation once both are detached
        context = self.file.createIfcGeometricRepresentationContext()
        rep = self.file.createIfcRepresentation(ContextOfItems=context)
        shape = self.file.createIfcProductDefinitionShape(Representations=[rep])
        element_a = ifcopenshell.api.root.create_entity(self.file)
        element_b = ifcopenshell.api.root.create_entity(self.file)
        element_a.Representation = shape
        element_b.Representation = shape

        ifcopenshell.api.context.remove_context(self.file, context=context)

        assert element_a.Representation is None
        assert element_b.Representation is None
        assert len(self.file.by_type("IfcProductDefinitionShape")) == 0
        assert len(self.file.by_type("IfcRepresentation")) == 0


class TestRemoveContextIFC2X3(test.bootstrap.IFC2X3, TestRemoveContext):
    pass
