# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
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

import bpy
import ifcopenshell
import test.bim.bootstrap
from blenderbim.tool import Ifc as subject


class TestSet(test.bim.bootstrap.NewFile):
    def test_setting_an_ifc_data(self):
        ifc = ifcopenshell.file()
        subject().set(ifc)
        assert subject().get() == ifc


class TestGet(test.bim.bootstrap.NewFile):
    def test_getting_an_ifc_dataset_from_a_ifc_spf_filepath(self):
        assert subject().get() is None
        bpy.context.scene.BIMProperties.ifc_file = "test/files/basic.ifc"
        result = subject().get()
        assert isinstance(result, ifcopenshell.file)

    def test_getting_the_active_ifc_dataset_regardless_of_ifc_path(self):
        bpy.context.scene.BIMProperties.ifc_file = "test/files/basic.ifc"
        ifc = ifcopenshell.file()
        subject().set(ifc)
        assert subject().get() == ifc


class TestRun(test.bim.bootstrap.NewFile):
    def test_running_a_command_on_the_active_ifc_dataset(self):
        ifc = ifcopenshell.file()
        subject().set(ifc)
        wall = subject().run("root.create_entity", ifc_class="IfcWall")
        assert subject().get().by_type("IfcWall")[0] == wall


class TestGetSchema(test.bim.bootstrap.NewFile):
    def test_getting_the_schema_version_identifier(self):
        ifc = ifcopenshell.file(schema="IFC4")
        subject().set(ifc)
        assert subject().get_schema() == "IFC4"
