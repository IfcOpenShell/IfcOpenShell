import test.bootstrap
import ifcopenshell.api


class TestEditContext(test.bootstrap.IFC4):
    def test_editing_a_context(self):
        context = self.file.createIfcGeometricRepresentationContext()
        ifcopenshell.api.run("context.edit_context", self.file, context=context, attributes={
            "ContextIdentifier": "ContextIdentifier",
            "ContextType": "ContextType",
            "CoordinateSpaceDimension": 1,
            "Precision": 1,
        })
        assert context.ContextIdentifier == "ContextIdentifier"
        assert context.ContextType == "ContextType"
        assert context.CoordinateSpaceDimension == 1
        assert context.Precision == 1

    def test_editing_a_subcontext(self):
        subcontext = self.file.createIfcGeometricRepresentationSubcontext()
        ifcopenshell.api.run("context.edit_context", self.file, context=subcontext, attributes={
            "ContextIdentifier": "ContextIdentifier",
            "ContextType": "ContextType",
            "TargetScale": 0.5,
            "TargetView": "MODEL_VIEW",
            "UserDefinedTargetView": "UserDefinedTargetView",
        })
        assert subcontext.ContextIdentifier == "ContextIdentifier"
        assert subcontext.ContextType == "ContextType"
        assert subcontext.TargetScale == 0.5
        assert subcontext.TargetView == "MODEL_VIEW"
        assert subcontext.UserDefinedTargetView == "UserDefinedTargetView"
