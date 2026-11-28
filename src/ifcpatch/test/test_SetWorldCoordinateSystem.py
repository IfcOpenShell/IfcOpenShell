# This file was generated with the assistance of an AI coding tool.

import ifcopenshell.api.context
import ifcopenshell.api.root
import pytest

import ifcpatch
import test.bootstrap


class TestSetWorldCoordinateSystem(test.bootstrap.IFC4):
    def test_plan_context_gets_a_2d_placement(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        ifcopenshell.api.context.add_context(self.file, context_type="Plan")
        ifcpatch.execute({"file": self.file, "recipe": "SetWorldCoordinateSystem", "arguments": [1, 2, 3, 0, 0, 90]})
        wcs = self.file.by_type("IfcGeometricRepresentationContext")[0].WorldCoordinateSystem
        assert wcs.is_a("IfcAxis2Placement2D")
        assert wcs.Location.Coordinates == pytest.approx((1.0, 2.0))
        assert wcs.RefDirection.DirectionRatios == pytest.approx((0.0, 1.0))
