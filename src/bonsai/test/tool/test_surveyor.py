# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of Bonsai.
#
# Bonsai is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Bonsai is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Bonsai.  If not, see <http://www.gnu.org/licenses/>.

import bpy
import ifcopenshell
import ifcopenshell.api.root
import ifcopenshell.api.unit
import ifcopenshell.util.geolocation
import numpy as np
from mathutils import Matrix

import bonsai.core.tool
import bonsai.tool as tool
import test.bim.bootstrap
from bonsai.tool import Surveyor as subject


class TestImplementsTool(test.bim.bootstrap.NewFile):
    def test_run(self):
        assert isinstance(subject(), bonsai.core.tool.Surveyor)


class TestGetGlobalMatrix(test.bim.bootstrap.NewFile):
    def test_getting_an_absolute_matrix_if_no_blender_offset(self):
        props = tool.Georeference.get_georeference_props()
        props.has_blender_offset = False
        obj = bpy.data.objects.new("Object", None)
        assert (subject.get_absolute_matrix(obj) == np.array(obj.matrix_world)).all()

    def test_applying_an_object_placement_blender_offset(self):
        ifc = ifcopenshell.file()
        ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcProject")
        unit = ifcopenshell.api.unit.add_si_unit(ifc, unit_type="LENGTHUNIT", prefix="MILLI")
        ifcopenshell.api.unit.assign_unit(ifc, units=[unit])
        tool.Ifc.set(ifc)
        props = tool.Georeference.get_georeference_props()
        props.has_blender_offset = True
        props.blender_offset_x = "1000"
        props.blender_offset_y = "2000"
        props.blender_offset_z = "3000"
        props.blender_x_axis_abscissa = "0"
        props.blender_x_axis_ordinate = "1"
        obj = bpy.data.objects.new("Object", None)
        props = tool.Blender.get_object_bim_props(obj)
        props.blender_offset_type = "OBJECT_PLACEMENT"
        matrix = ifcopenshell.util.geolocation.local2global(np.array(obj.matrix_world), 1.0, 2.0, 3.0, 0.0, 1.0)
        assert (subject.get_absolute_matrix(obj) == matrix).all()

    def test_undoing_a_cartesian_point_offset_along_the_objects_axes(self):
        ifc = ifcopenshell.file()
        ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcProject")
        unit = ifcopenshell.api.unit.add_si_unit(ifc, unit_type="LENGTHUNIT")
        ifcopenshell.api.unit.assign_unit(ifc, units=[unit])
        tool.Ifc.set(ifc)
        props = tool.Georeference.get_georeference_props()
        props.has_blender_offset = True
        # A mesh stored relative to (1000, 2000, 30) sits at the placement translated by that
        # offset along the object's own axes, here rotated 90 degrees about Z.
        obj = bpy.data.objects.new("Object", None)
        obj.matrix_world = Matrix.Rotation(np.pi / 2, 4, "Z") @ Matrix.Translation((1000.0, 2000.0, 30.0))
        oprops = tool.Blender.get_object_bim_props(obj)
        oprops.blender_offset_type = "CARTESIAN_POINT"
        oprops.cartesian_point_offset = "1000,2000,30"
        # Blender holds the matrix in float32, so the fold is only precise to that.
        assert np.allclose(subject.get_absolute_matrix(obj), np.array(Matrix.Rotation(np.pi / 2, 4, "Z")), atol=1e-3)
