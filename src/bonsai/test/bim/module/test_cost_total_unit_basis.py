# This file was generated with the assistance of an AI coding tool.

import ifcopenshell
import ifcopenshell.api.root
import pytest

import bonsai.tool as tool
from bonsai.bim.module.cost.data import CostSchedulesData
from test.bim.bootstrap import NewFile


class TestTotalCostUnitBasis(NewFile):
    def test_each_cost_value_uses_its_own_unit_basis(self):
        ifc = ifcopenshell.file(schema="IFC4")
        tool.Ifc.set(ifc)
        item = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcCostItem")
        metre = ifc.createIfcSIUnit(UnitType="LENGTHUNIT", Name="METRE")
        per_ten = ifc.createIfcCostValue(
            AppliedValue=ifc.createIfcMonetaryMeasure(100.0),
            UnitBasis=ifc.createIfcMeasureWithUnit(ifc.createIfcReal(10.0), metre),
        )
        per_unit = ifc.createIfcCostValue(AppliedValue=ifc.createIfcMonetaryMeasure(50.0))
        item.CostValues = [per_ten, per_unit]
        assert CostSchedulesData.cost_items()[item.id()]["TotalCost"] == pytest.approx(60.0)
