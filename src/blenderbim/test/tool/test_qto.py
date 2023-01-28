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
from blenderbim.tool.qto import Qto as subject


class TestImplementsTool(test.bim.bootstrap.NewFile):
    def test_run(self):
        assert isinstance(subject(), blenderbim.core.tool.Qto)


class TestGetRadiusOfSelectedVertices(test.bim.bootstrap.NewFile):
    def test_run(self):
        bpy.ops.mesh.primitive_circle_add()
        assert round(subject.get_radius_of_selected_vertices(bpy.data.objects.get("Circle")), 3) == 1


class TestSetQtoResult(test.bim.bootstrap.NewFile):
    def test_run(self):
        subject.set_qto_result(123.4567)
        assert bpy.context.scene.BIMQtoProperties.qto_result == "123.457"
