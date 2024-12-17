# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of IfcOpenShell.
#
# IfcOpenShell is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcOpenShell is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcOpenShell.  If not, see <http://www.gnu.org/licenses/>.

import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.util.shape
import test.bootstrap
import numpy as np
from ifcopenshell.util.shape_builder import ShapeBuilder, V


class TestCreatingShapesIfcCurve(test.bootstrap.IFC4):
    def test_create_IfcCirle(self):
        builder = ShapeBuilder(self.file)
        radius = 1.0
        item = builder.circle(radius=radius)
        settings = ifcopenshell.geom.settings()
        shape = ifcopenshell.geom.create_shape(settings, item)
        verts = ifcopenshell.util.shape.get_vertices(shape)
        assert len(verts) == 72
        distances = np.linalg.norm(verts, axis=1)
        assert np.allclose(distances, np.full(len(verts), radius))

    def test_create_IfcEllipse(self):
        builder = ShapeBuilder(self.file)
        item = self.file.create_entity(
            "IfcEllipse", Position=builder.create_axis2_placement_2d(), SemiAxis1=1.0, SemiAxis2=0.5
        )
        settings = ifcopenshell.geom.settings()
        shape = ifcopenshell.geom.create_shape(settings, item)
        assert shape.verts

    def test_create_IfcLine(self):
        item = self.file.create_entity(
            "IfcLine",
            Pnt=self.file.create_entity("IfcCartesianPoint", (0.0, 0.0)),
            Dir=self.file.create_entity(
                "IfcVector", Orientation=self.file.create_entity("IfcDirection", (1.0, 0.0)), Magnitude=1.0
            ),
        )
        settings = ifcopenshell.geom.settings()
        shape = ifcopenshell.geom.create_shape(settings, item)
        assert shape.verts

    def test_create_IfcBSplineCurve(self):
        points = [
            (6.4062, 19.4575766757, 13.352536093),
            (5.8477429418, 19.9080686796, 14.1328111323),
            (3.6139147091, 20.3256826827, 14.8561398035),
            (1.1790137971e-05, 20.2853841412, 14.7863406821),
            (1.1790137971e-05, 18.5102818197, 11.7117732726),
            (1.16078600148, 18.0665062393, 10.9431314203),
        ]
        item = self.file.create_entity(
            "IfcBSplineCurveWithKnots",
            Degree=3,
            ControlPointsList=[self.file.create_entity("IfcCartesianPoint", p) for p in points],
            KnotMultiplicities=(4, 1, 1, 4),
            Knots=(0.0, 1 / 3, 2 / 3, 1.0),
        )
        settings = ifcopenshell.geom.settings()
        shape = ifcopenshell.geom.create_shape(settings, item)
        assert shape.verts


class TestCreatingShapes(test.bootstrap.IFC4):
    def test_create_IfcSweptDiskSolid(self):
        builder = ShapeBuilder(self.file)
        curve = builder.polyline([V(0.0, 0.0), V(3.0, 0.0)])
        item = self.file.create_entity("IfcSweptDiskSolid", Directrix=curve, Radius=0.5, InnerRadius=0.4)
        settings = ifcopenshell.geom.settings()
        shape = ifcopenshell.geom.create_shape(settings, item)
        verts = ifcopenshell.util.shape.get_vertices(shape)

        unique_values = np.unique(verts[:, 0])
        assert unique_values.tolist() == [0.0, 3.0]

        modified_verts = verts.copy()
        modified_verts[:, 0] = 0
        distances = np.linalg.norm(modified_verts, axis=1)
        tolerance = 1e-5
        rounded_distances = np.round(distances / tolerance) * tolerance
        unique_values = np.unique(rounded_distances)
        assert unique_values.tolist() == [0.4, 0.5]
