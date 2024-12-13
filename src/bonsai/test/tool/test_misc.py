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
import math
import numpy
import ifcopenshell
import test.bim.bootstrap
import bonsai.core.tool
import bonsai.tool as tool
from bonsai.tool.misc import Misc as subject
from bonsai.bim.ifc import IfcStore


class TestImplementsTool(test.bim.bootstrap.NewFile):
    def test_run(self):
        assert isinstance(subject(), bonsai.core.tool.Misc)


class TestGetObjectStorey(test.bim.bootstrap.NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        obj = bpy.data.objects.new("Object", None)
        wall = ifc.createIfcWall()
        tool.Ifc.link(wall, obj)
        storey = ifc.createIfcBuildingStorey()
        ifcopenshell.api.run("spatial.assign_container", ifc, products=[wall], relating_structure=storey)
        assert subject.get_object_storey(obj) == storey

    def test_only_returning_a_building_storey(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        obj = bpy.data.objects.new("Object", None)
        wall = ifc.createIfcWall()
        tool.Ifc.link(wall, obj)
        building = ifc.createIfcBuilding()
        ifcopenshell.api.run("spatial.assign_container", ifc, products=[wall], relating_structure=building)
        assert subject.get_object_storey(obj) is None

    def test_returning_nothing_if_uncontained(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        obj = bpy.data.objects.new("Object", None)
        wall = ifc.createIfcWall()
        tool.Ifc.link(wall, obj)
        assert subject.get_object_storey(obj) is None


class TestGetStoreyElevation(test.bim.bootstrap.NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        ifc.createIfcProject()
        unit = ifcopenshell.api.run("unit.add_si_unit", ifc, prefix="MILLI")
        ifcopenshell.api.run("unit.assign_unit", ifc, units=[unit])
        storey = ifc.createIfcBuildingStorey()
        storey.Elevation = 3000
        tool.Ifc.set(ifc)
        assert subject.get_storey_elevation_in_si(storey) == 3.0


class TestGetStoreyHeight(test.bim.bootstrap.NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        ifc.createIfcProject()
        unit = ifcopenshell.api.run("unit.add_si_unit", ifc, prefix="MILLI")
        ifcopenshell.api.run("unit.assign_unit", ifc, units=[unit])
        tool.Ifc.set(ifc)
        building = ifc.createIfcBuilding()
        storey = ifc.createIfcBuildingStorey()
        storey.Elevation = 3000
        storey2 = ifc.createIfcBuildingStorey()
        storey2.Elevation = 5000
        ifcopenshell.api.run("aggregate.assign_object", ifc, products=[storey], relating_object=building)
        ifcopenshell.api.run("aggregate.assign_object", ifc, products=[storey2], relating_object=building)
        assert subject.get_storey_height_in_si(storey, 1) == 2.0

    def test_getting_a_double_storey_height(self):
        ifc = ifcopenshell.file()
        ifc.createIfcProject()
        unit = ifcopenshell.api.run("unit.add_si_unit", ifc, prefix="MILLI")
        ifcopenshell.api.run("unit.assign_unit", ifc, units=[unit])
        tool.Ifc.set(ifc)
        building = ifc.createIfcBuilding()
        storey = ifc.createIfcBuildingStorey()
        storey.Elevation = 3000
        storey2 = ifc.createIfcBuildingStorey()
        storey2.Elevation = 5000
        storey3 = ifc.createIfcBuildingStorey()
        storey3.Elevation = 9000
        ifcopenshell.api.run("aggregate.assign_object", ifc, products=[storey], relating_object=building)
        ifcopenshell.api.run("aggregate.assign_object", ifc, products=[storey2], relating_object=building)
        ifcopenshell.api.run("aggregate.assign_object", ifc, products=[storey3], relating_object=building)
        assert subject.get_storey_height_in_si(storey, 2) == 6.0

    def test_only_considering_storeys_in_the_same_building(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        building = ifc.createIfcBuilding()
        storey = ifc.createIfcBuildingStorey()
        storey.Elevation = 3000
        storey2 = ifc.createIfcBuildingStorey()
        storey2.Elevation = 5000
        ifcopenshell.api.run("aggregate.assign_object", ifc, products=[storey], relating_object=building)
        assert subject.get_storey_height_in_si(storey, 1) is None

    def test_returning_none_if_the_storey_height_is_undefined(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        building = ifc.createIfcBuilding()
        storey = ifc.createIfcBuildingStorey()
        ifcopenshell.api.run("aggregate.assign_object", ifc, products=[storey], relating_object=building)
        assert subject.get_storey_height_in_si(storey, 1) is None


class TestSetObjectOriginToBottom(test.bim.bootstrap.NewFile):
    def test_run(self):
        bpy.ops.mesh.primitive_cube_add()
        obj = bpy.data.objects.get("Cube")
        subject.set_object_origin_to_bottom(obj)
        assert list(obj.matrix_world.translation) == [0.0, 0.0, -1.0]

    def test_moving_the_origin_of_a_rotated_object(self):
        bpy.ops.mesh.primitive_cube_add()
        obj = bpy.data.objects.get("Cube")
        obj.rotation_euler[1] = math.pi / 2
        bpy.context.view_layer.update()
        subject.set_object_origin_to_bottom(obj)
        assert list(obj.matrix_world.translation) == [0.0, 0.0, -1.0]


class TestMoveObjectToElevation(test.bim.bootstrap.NewFile):
    def test_run(self):
        bpy.ops.mesh.primitive_cube_add()
        obj = bpy.data.objects.get("Cube")
        subject.move_object_to_elevation(obj, 3)
        assert list(obj.matrix_world.translation) == [0.0, 0.0, 3.0]


class TestRunRootCopyClass(test.bim.bootstrap.NewFile):
    def test_nothing(self):
        pass


class TestScaleObjectToHeight(test.bim.bootstrap.NewFile):
    def test_run(self):
        bpy.ops.mesh.primitive_cube_add()
        obj = bpy.data.objects.get("Cube")
        subject.set_object_origin_to_bottom(obj)
        subject.scale_object_to_height(obj, 3)
        assert obj.dimensions[2] == 3.0
        assert list(obj.scale) == [1.0, 1.0, 1.0]


class TestSplitObjectsWithCutter(test.bim.bootstrap.NewFile):
    def test_run(self):
        bpy.ops.mesh.primitive_cube_add()
        bpy.ops.mesh.primitive_plane_add(size=4)
        obj = bpy.data.objects.get("Cube")
        cutter = bpy.data.objects.get("Plane")
        assert obj.dimensions[2] == 2
        new_objs = subject.split_objects_with_cutter([obj], cutter)
        assert new_objs[0].name == "Cube.001"
        assert obj.dimensions[2] == 1
        assert new_objs[0].dimensions[2] == 1
