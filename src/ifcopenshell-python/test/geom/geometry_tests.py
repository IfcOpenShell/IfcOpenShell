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
import test.bootstrap
from ifcopenshell.util.shape_builder import ShapeBuilder, V


class TestCreatingShapes(test.bootstrap.IFC4):
    def test_create_IfcCirle(self):
        builder = ShapeBuilder(self.file)
        item = builder.circle(radius=1.0)
        settings = ifcopenshell.geom.settings()
        shape = ifcopenshell.geom.create_shape(settings, item)
        assert shape.verts

    def test_create_IfcEllipse(self):
        builder = ShapeBuilder(self.file)
        item = self.file.create_entity(
            "IfcEllipse", Position=builder.create_axis2_placement_2d(), SemiAxis1=1.0, SemiAxis2=0.5
        )
        settings = ifcopenshell.geom.settings()
        shape = ifcopenshell.geom.create_shape(settings, item)
        assert shape.verts
