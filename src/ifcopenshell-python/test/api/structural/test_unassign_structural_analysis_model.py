import numpy
import pytest
import test.bootstrap
import ifcopenshell.api

class TestUnassignStructuralAnalysisModel(test.bootstrap.IFC4):
    def test_unassigning_a_structural_analysis_model(self):
        subject = ifcopenshell.api.run("structural.add_structural_analysis_model", self.file)
        product = ifcopenshell.api.run(
            "root.create_entity",
            self.file,
            ifc_class="IfcStructuralMember",
            predefined_type=None,
            name=None
        )
        rel = ifcopenshell.api.run(
            "structural.assign_structural_analysis_model",
            self.file,
            product=product,
            structural_analysis_model=subject,
        )
        ifcopenshell.api.run(
            "structural.unassign_structural_analysis_model",
            self.file,
            product=product,
            structural_analysis_model=subject,
        )
        models = self.file.by_type("IfcStructuralAnalysisModel")
        rels = self.file.by_type("IfcRelAssignsToGroup")
        assert len(models[0].IsGroupedBy) == 0
        assert len(rels) == 0
