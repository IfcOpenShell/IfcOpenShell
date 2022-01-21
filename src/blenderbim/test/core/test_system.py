# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
#
# This file is part of BlenderBIM Add-on.
#
# BlenderBIM Add-on is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BlenderBIM Add-on is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with BlenderBIM Add-on.  If not, see <http://www.gnu.org/licenses/>.


import blenderbim.core.system as subject
from test.core.bootstrap import ifc, system


class TestLoadSystems:
    def test_run(self, system):
        system.import_systems().should_be_called()
        system.enable_system_editing_ui().should_be_called()
        system.disable_editing_system().should_be_called()
        subject.load_systems(system)


class TestDisableSystemEditingUI:
    def test_run(self, system):
        system.disable_editing_system().should_be_called()
        system.disable_system_editing_ui().should_be_called()
        subject.disable_system_editing_ui(system)


class TestAddSystem:
    def test_run(self, ifc, system):
        ifc.run("system.add_system", ifc_class="ifc_class").should_be_called()
        system.import_systems().should_be_called()
        subject.add_system(ifc, system, ifc_class="ifc_class")


class TestEditSystem:
    def test_run(self, ifc, system):
        system.export_system_attributes().should_be_called().will_return("attributes")
        ifc.run("system.edit_system", system="system", attributes="attributes").should_be_called()
        system.disable_editing_system().should_be_called()
        system.import_systems().should_be_called()
        subject.edit_system(ifc, system, system="system")


class TestRemoveSystem:
    def test_run(self, ifc, system):
        ifc.run("system.remove_system", system="system").should_be_called()
        system.import_systems().should_be_called()
        subject.remove_system(ifc, system, system="system")


class TestEnableEditingSystem:
    def test_run(self, system):
        system.import_system_attributes("system").should_be_called()
        system.set_active_system("system").should_be_called()
        subject.enable_editing_system(system, system="system")


class TestDisableEditingSystem:
    def test_run(self, system):
        system.disable_editing_system().should_be_called()
        subject.disable_editing_system(system)


class TestAssignSystem:
    def test_run(self, ifc):
        ifc.run("system.assign_system", product="product", system="system").should_be_called()
        subject.assign_system(ifc, system="system", product="product")


class TestUnassignSystem:
    def test_run(self, ifc):
        ifc.run("system.unassign_system", product="product", system="system").should_be_called()
        subject.unassign_system(ifc, system="system", product="product")


class TestSelectSystemProducts:
    def test_run(self, system):
        system.select_system_products("system").should_be_called()
        subject.select_system_products(system, system="system")
