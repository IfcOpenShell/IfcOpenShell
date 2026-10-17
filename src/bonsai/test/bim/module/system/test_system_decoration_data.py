# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026 Dion Moult <dion@thinkmoult.com>
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
import ifcopenshell.api.system

import bonsai.tool as tool
from bonsai.bim.module.system.data import SystemData, SystemDecorationData, refresh
from test.bim.bootstrap import NewFile


class TestDecorationSource(NewFile):
    def add_wall(self, ifc_class="IfcWall"):
        bpy.ops.mesh.primitive_cube_add()
        obj = bpy.context.active_object
        wall = tool.Ifc.get().create_entity(ifc_class)
        tool.Ifc.link(wall, obj)
        return wall

    def add_system(self, products, ifc_class="IfcBuildingSystem", name="Structure"):
        system = ifcopenshell.api.system.add_system(tool.Ifc.get(), ifc_class=ifc_class)
        system.Name = name
        ifcopenshell.api.system.assign_system(tool.Ifc.get(), products=products, system=system)
        return system

    def test_active_object_systems_come_first(self):
        bpy.ops.bim.create_project()
        wall = self.add_wall()
        system = self.add_system([wall])
        refresh()
        assert SystemDecorationData.decoration_source() == ("OBJECT_SYSTEMS", [system])
        SystemData.load()
        assert SystemData.data["decoration"]["systems"] == [
            {"id": system.id(), "name": "Structure", "ifc_class": "IfcBuildingSystem"}
        ]

    def test_falling_back_to_the_active_system(self):
        bpy.ops.bim.create_project()
        other_wall = self.add_wall()
        system = self.add_system([other_wall])
        self.add_wall()
        tool.System.set_active_system(system)
        refresh()
        assert SystemDecorationData.decoration_source() == ("ACTIVE_SYSTEM", [system])

    def test_falling_back_to_connected_elements(self):
        bpy.ops.bim.create_project()
        self.add_wall()
        refresh()
        assert SystemDecorationData.decoration_source() == ("NONE", [])

    def test_clearing_the_active_system(self):
        bpy.ops.bim.create_project()
        other_wall = self.add_wall()
        system = self.add_system([other_wall])
        self.add_wall()
        tool.System.set_active_system(system)
        bpy.ops.bim.clear_active_system()
        assert tool.System.get_active_system() is None
        assert SystemDecorationData.decoration_source() == ("NONE", [])

    def test_counting_only_elements_the_decorations_can_draw(self):
        bpy.ops.bim.create_project()
        wall = self.add_wall()
        self.add_system([wall])
        refresh()
        SystemData.load()
        assert SystemData.data["decoration"]["total_system_drawable"] == 0

        duct = self.add_wall(ifc_class="IfcDuctSegment")
        self.add_system([duct], ifc_class="IfcDistributionSystem", name="HVAC")
        refresh()
        SystemData.load()
        assert SystemData.data["decoration"]["source"] == "OBJECT_SYSTEMS"
        assert SystemData.data["decoration"]["total_system_drawable"] == 1

    def test_rebuilding_decorations_after_unassigning(self):
        bpy.ops.bim.create_project()
        duct = self.add_wall(ifc_class="IfcDuctSegment")
        system = self.add_system([duct], ifc_class="IfcDistributionSystem", name="HVAC")
        refresh()
        before = tool.System.get_decoration_data()
        assert tool.System.get_decoration_data() is before
        ifcopenshell.api.system.unassign_system(tool.Ifc.get(), products=[duct], system=system)
        refresh()
        assert tool.System.get_decoration_data() is not before
        assert SystemDecorationData.decoration_source() == ("NONE", [])

    def test_unassigning_removes_the_system_but_keeps_the_run(self):
        bpy.ops.bim.create_project()
        duct = self.add_wall(ifc_class="IfcDuctSegment")
        system = self.add_system([duct], ifc_class="IfcDistributionSystem", name="HVAC")
        refresh()
        SystemDecorationData.load()
        assert SystemDecorationData.data["system_elements"] == {duct}
        assert SystemDecorationData.data["run_elements"] == {duct}

        ifcopenshell.api.system.unassign_system(tool.Ifc.get(), products=[duct], system=system)
        refresh()
        SystemDecorationData.load()
        assert SystemDecorationData.data["system_elements"] == set()
        assert SystemDecorationData.data["run_elements"] == {duct}
        SystemData.load()
        assert SystemData.data["decoration"]["total_system_drawable"] == 0
        assert SystemData.data["decoration"]["total_run_drawable"] == 1

    def test_forgetting_the_active_system_once_another_object_is_active(self):
        bpy.ops.bim.create_project()
        other_wall = self.add_wall()
        system = self.add_system([other_wall])
        self.add_wall()
        tool.System.set_active_system(system)
        refresh()
        assert SystemDecorationData.decoration_source() == ("ACTIVE_SYSTEM", [system])

        self.add_wall()  # Another wall in no system becomes the active object.
        refresh()
        assert SystemDecorationData.decoration_source() == ("NONE", [])
