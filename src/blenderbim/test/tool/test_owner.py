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
import blenderbim.core.tool
import blenderbim.tool as tool
from blenderbim.tool.owner import Owner as subject


class TestImplementsTool(test.bim.bootstrap.NewFile):
    def test_run(self):
        assert isinstance(subject(), blenderbim.core.tool.Owner)


class TestSetUser(test.bim.bootstrap.NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        user = ifc.createIfcPersonAndOrganization()
        subject.set_user(user)
        assert bpy.context.scene.BIMOwnerProperties.active_user_id == user.id()


class TestGetUser(test.bim.bootstrap.NewFile):
    def test_run(self):
        assert subject.get_user() is None
        TestSetUser().test_run()
        user = tool.Ifc.get().by_type("IfcPersonAndOrganization")[0]
        assert subject.get_user() == user


class TestClearUser(test.bim.bootstrap.NewFile):
    def test_run(self):
        TestSetUser().test_run()
        subject.clear_user()
        assert bpy.context.scene.BIMOwnerProperties.active_user_id == 0
