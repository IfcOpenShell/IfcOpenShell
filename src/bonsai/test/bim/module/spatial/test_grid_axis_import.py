# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026
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
#
# This file was generated with the assistance of an AI coding tool.

import bpy
import ifcopenshell.api.context
import ifcopenshell.api.geometry
import ifcopenshell.api.project
import ifcopenshell.api.root
import ifcopenshell.api.unit
import numpy as np
import pytest

import bonsai.tool as tool
from test.bim.bootstrap import NewFile

pytestmark = pytest.mark.spatial


def _write_two_grids_sharing_two_axes(path):
    ifc = ifcopenshell.api.project.create_file(version="IFC4")
    ifcopenshell.api.root.create_entity(ifc, "IfcProject", name="Project")
    ifcopenshell.api.unit.assign_unit(ifc)
    plan = ifcopenshell.api.context.add_context(ifc, context_type="Plan")
    ifcopenshell.api.context.add_context(
        ifc, context_type="Plan", context_identifier="Annotation", target_view="PLAN_VIEW", parent=plan
    )
    ifcopenshell.api.context.add_context(ifc, context_type="Model")

    def add_axis(tag, start, end):
        points = [ifc.create_entity("IfcCartesianPoint", start), ifc.create_entity("IfcCartesianPoint", end)]
        curve = ifc.create_entity("IfcPolyline", points)
        return ifc.create_entity("IfcGridAxis", AxisTag=tag, AxisCurve=curve, SameSense=True)

    u_axis = add_axis("A", (0.0, 0.0), (0.0, 10.0))
    v_axis = add_axis("1", (0.0, 0.0), (10.0, 0.0))
    for i, elevation in enumerate((0.0, 3.0)):
        grid = ifcopenshell.api.root.create_entity(ifc, "IfcGrid", name=f"Grid {i}")
        grid.UAxes = [u_axis]
        grid.VAxes = [v_axis]
        matrix = np.eye(4)
        matrix[2, 3] = elevation
        ifcopenshell.api.geometry.edit_object_placement(ifc, grid, matrix)
    ifc.write(str(path))


def _axis_objects():
    return [o for o in bpy.data.objects if o.name.startswith("IfcGridAxis/")]


class TestImportGridsSharingAxes(NewFile):
    def test_one_object_per_shared_axis(self, tmp_path):
        path = tmp_path / "shared_axes.ifc"
        _write_two_grids_sharing_two_axes(path)
        bpy.ops.bim.load_project(filepath=str(path))

        ifc = tool.Ifc.get()
        assert len(ifc.by_type("IfcGrid")) == 2
        assert len(ifc.by_type("IfcGridAxis")) == 2
        axis_objects = _axis_objects()
        assert len(axis_objects) == 2
        assert all(tool.Ifc.get_entity(o) for o in axis_objects)
        assert all(o.users_collection for o in axis_objects)
        assert {tool.Ifc.get_entity(o).id() for o in axis_objects} == {a.id() for a in ifc.by_type("IfcGridAxis")}

    def test_shared_axis_sits_at_the_first_grid_placement(self, tmp_path):
        path = tmp_path / "shared_axes.ifc"
        _write_two_grids_sharing_two_axes(path)
        bpy.ops.bim.load_project(filepath=str(path))

        assert [round(o.matrix_world.translation.z, 3) for o in _axis_objects()] == [0.0, 0.0]
