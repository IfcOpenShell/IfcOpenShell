import numpy
import pytest
import test.bootstrap
import ifcopenshell.api


class TestRemoveStructuralAnalysisModel(test.bootstrap.IFC4):
    def test_removing_a_structural_analysis_model(self):
        subject = ifcopenshell.api.run("structural.add_structural_analysis_model", self.file)
        ifcopenshell.api.run(
            "structural.remove_structural_analysis_model",
            self.file,
            structural_analysis_model=subject,
        )
        models = self.file.by_type("IfcStructuralAnalysisModel")
        assert len(models) == 0
