import numpy
import pytest
import test.bootstrap
import ifcopenshell.api


class TestEditStructuralAnalysisModel(test.bootstrap.IFC4):
    def test_editing_a_structural_analysis_model(self):
        subject = ifcopenshell.api.run("structural.add_structural_analysis_model", self.file)
        subject = ifcopenshell.api.run(
            "structural.edit_structural_analysis_model",
            self.file,
            structural_analysis_model=subject,
            attributes={"Name": "My edited model", "Description": "Description of my model"},
        )
        models = self.file.by_type("IfcStructuralAnalysisModel")
        assert subject == models[0]
        assert subject.is_a("IfcStructuralAnalysisModel")
