"""Run this test from src/ifcopenshell-python folder: pytest --durations=0 ifcopenshell/util/test_pset.py"""
from ifcopenshell.util import pset
from ifcopenshell import util


class TestPsetQto:
    @classmethod
    def setup_class(cls):
        cls.pset_qto = util.pset.PsetQto("IFC4")

    def test_get_applicables(self):
        for i in range(1000):
            assert len(self.pset_qto.get_applicable("IfcMaterial")) == 14

    def test_get_applicables_names(self):
        for i in range(1000):
            assert len(self.pset_qto.get_applicable_names("IfcMaterial")) == 14
