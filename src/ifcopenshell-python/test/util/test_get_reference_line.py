# This file was generated with the assistance of an AI coding tool.

import numpy as np

import ifcopenshell.api.context
import ifcopenshell.api.root
import ifcopenshell.util.representation as subject
import test.bootstrap


class TestGetReferenceLine(test.bootstrap.IFC4):
    def add_wall_with_profile(self, profile):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        wall = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        model = ifcopenshell.api.context.add_context(self.file, context_type="Model")
        body = ifcopenshell.api.context.add_context(
            self.file, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=model
        )
        extrusion = self.file.createIfcExtrudedAreaSolid(
            profile,
            self.file.createIfcAxis2Placement3D(self.file.createIfcCartesianPoint((0.0, 0.0, 0.0))),
            self.file.createIfcDirection((0.0, 0.0, 1.0)),
            3.0,
        )
        wall.Representation = self.file.createIfcProductDefinitionShape(
            Representations=[self.file.createIfcShapeRepresentation(body, "Body", "SweptSolid", [extrusion])]
        )
        return wall

    def test_recovering_the_length_from_a_rectangle_profile(self):
        position = self.file.createIfcAxis2Placement2D(self.file.createIfcCartesianPoint((2.5, 0.0)))
        profile = self.file.createIfcRectangleProfileDef("AREA", None, position, 5.0, 0.2)
        wall = self.add_wall_with_profile(profile)
        start, end = subject.get_reference_line(wall)
        assert np.allclose(start, (0.0, 0.0))
        assert np.allclose(end, (5.0, 0.0))

    def test_recovering_the_length_from_a_rectangle_profile_without_a_position(self):
        profile = self.file.createIfcRectangleProfileDef("AREA", None, None, 4.0, 0.2)
        wall = self.add_wall_with_profile(profile)
        start, end = subject.get_reference_line(wall)
        assert np.allclose(start, (-2.0, 0.0))
        assert np.allclose(end, (2.0, 0.0))
