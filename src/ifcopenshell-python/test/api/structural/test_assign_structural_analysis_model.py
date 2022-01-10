import numpy
import pytest
import test.bootstrap
import ifcopenshell.api


class TestAssignStructuralAnalysisModel(test.bootstrap.IFC4):
    def test_assigning_a_structural_analysis_model(self):
        subject = ifcopenshell.api.run("structural.add_structural_analysis_model", self.file)
        product = ifcopenshell.api.run(
            "root.create_entity", self.file, ifc_class="IfcStructuralMember", predefined_type=None, name=None
        )
        rel = ifcopenshell.api.run(
            "structural.assign_structural_analysis_model",
            self.file,
            product=product,
            structural_analysis_model=subject,
        )
        assert rel.is_a("IfcRelAssignsToGroup")
        assert rel.RelatingGroup == subject
        assert product in rel.RelatedObjects
