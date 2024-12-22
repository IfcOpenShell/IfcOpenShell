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

import numpy as np
import ifcopenshell
import ifcopenshell.api.geometry
import ifcopenshell.api.profile
import ifcopenshell.api.root
import ifcopenshell.geom
import ifcopenshell.geom
import ifcopenshell.util.unit
import test.bootstrap
from ifcopenshell.util.shape_builder import ShapeBuilder


class TestSettings(test.bootstrap.IFC4):
    def test_convert_back_units(self):
        settings = ifcopenshell.geom.settings()
        settings.set("convert-back-units", True)

        ifc_file = ifcopenshell.file()
        builder = ShapeBuilder(ifc_file)

        ifcopenshell.api.root.create_entity(ifc_file, "IfcProject")
        unit = ifcopenshell.api.run("unit.add_si_unit", ifc_file, unit_type="LENGTHUNIT", prefix="MILLI")
        ifcopenshell.api.run("unit.assign_unit", ifc_file, units=[unit])
        model = ifcopenshell.api.run("context.add_context", ifc_file, context_type="Model")

        # Placement.
        element = ifcopenshell.api.root.create_entity(ifc_file, "IfcWall")
        matrix = np.eye(4)
        matrix[0, 3] = 10
        placement = ifcopenshell.api.geometry.edit_object_placement(ifc_file, element, matrix)
        transform = ifcopenshell.geom.create_shape(settings, placement)
        assert transform.matrix == (1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 10000.0, 0.0, 0.0, 1.0)

        # Profile.
        profile = ifcopenshell.api.profile.add_parameterized_profile(ifc_file, "IfcRectangleProfileDef")
        ifcopenshell.api.profile.edit_profile(ifc_file, profile, {"XDim": 100, "YDim": 100})
        shape = ifcopenshell.geom.create_shape(settings, profile)
        assert shape.verts == (-50.0, -50.0, 0.0, 50.0, -50.0, 0.0, 50.0, 50.0, 0.0, -50.0, 50.0, 0.0)

        # Representation item.
        extrusion = builder.extrude(profile, 1000)
        shape = ifcopenshell.geom.create_shape(settings, extrusion)
        # fmt: off
        extrusion_verts = (
            -50.0, -50.0, 0.0, -50.0, -50.0, 1000.0, 50.0, -50.0, 1000.0, 50.0, -50.0, 0.0,
            50.0, 50.0, 1000.0, 50.0, 50.0, 0.0, -50.0, 50.0, 1000.0, -50.0, 50.0, 0.0
        )
        # fmt: on
        assert shape.verts == extrusion_verts

        # Representation.
        representation = builder.get_representation(model, [extrusion])
        shape = ifcopenshell.geom.create_shape(settings, representation)
        assert shape.verts == extrusion_verts

        # Element.
        ifcopenshell.api.geometry.assign_representation(ifc_file, element, representation)
        shape = ifcopenshell.geom.create_shape(settings, element)
        assert shape.geometry.verts == extrusion_verts

        # Element with disabled conversion.
        settings.set("convert-back-units", False)
        shape = ifcopenshell.geom.create_shape(settings, element)
        si_conversion = ifcopenshell.util.unit.calculate_unit_scale(ifc_file)
        converted_verts = np.array(extrusion_verts) * si_conversion
        assert np.allclose(shape.geometry.verts, converted_verts)
