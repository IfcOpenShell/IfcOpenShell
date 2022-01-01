import numpy
import pytest
import test.bootstrap
import ifcopenshell.api

class TestAddStructuralAnalysisModel(test.bootstrap.IFC4):
    def test_adding_a_structural_analysis_model(self):
        subject = ifcopenshell.api.run("structural.add_structural_analysis_model", self.file)
        models = self.file.by_type("IfcStructuralAnalysisModel")
        assert subject == models[0]
        assert subject.is_a("IfcStructuralAnalysisModel")
