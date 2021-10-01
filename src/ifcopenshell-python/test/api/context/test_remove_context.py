import test.bootstrap
import ifcopenshell.api


class TestRemoveContext(test.bootstrap.IFC4):
    def test_removing_a_context(self):
        context = self.file.createIfcGeometricRepresentationContext()
        ifcopenshell.api.run("context.remove_context", self.file, context=context)
        assert len(self.file.by_type("IfcGeometricRepresentationContext")) == 0

    def test_removing_a_context_with_subcontexts(self):
        context = self.file.createIfcGeometricRepresentationContext()
        subcontext = self.file.createIfcGeometricRepresentationSubcontext()
        subcontext.ParentContext = context
        ifcopenshell.api.run("context.remove_context", self.file, context=context)
        assert len(self.file.by_type("IfcGeometricRepresentationContext")) == 0

    def test_removing_a_subcontext_and_reassigning_references_to_its_parent(self):
        context = self.file.createIfcGeometricRepresentationContext()
        subcontext = self.file.createIfcGeometricRepresentationSubcontext()
        subcontext.ParentContext = context
        representation = self.file.createIfcRepresentation(ContextOfItems=subcontext)
        projected_crs = self.file.createIfcProjectedCRS()
        map_conversion = self.file.createIfcMapConversion(SourceCRS=subcontext, TargetCRS=projected_crs)
        ifcopenshell.api.run("context.remove_context", self.file, context=subcontext)
        assert len(self.file.by_type("IfcGeometricRepresentationSubcontext")) == 0
        assert representation in self.file.get_inverse(context)
        assert len(self.file.by_type("IfcMapConversion")) == 0
        assert len(self.file.by_type("IfcProjectedCRS")) == 0

    def test_removing_a_context_with_references(self):
        context = self.file.createIfcGeometricRepresentationContext()
        representation = self.file.createIfcRepresentation(ContextOfItems=context)
        ifcopenshell.api.run("context.remove_context", self.file, context=context)
        assert len([e for e in self.file]) == 0
