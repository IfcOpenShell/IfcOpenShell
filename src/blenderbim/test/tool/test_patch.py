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

import os
import bpy
import ifcopenshell
import blenderbim.core.tool
import blenderbim.tool as tool
from test.bim.bootstrap import NewFile
from blenderbim.tool.patch import Patch as subject


class TestImplementsTool(NewFile):
    def test_run(self):
        assert isinstance(subject(), blenderbim.core.tool.Patch)


class TestRunMigratePatch(NewFile):
    def test_run(self):
        cwd = os.path.dirname(os.path.realpath(__file__))
        infile = os.path.join(cwd, "..", "files", "ifc2x3.ifc")
        outfile = os.path.join(cwd, "..", "files", "temp", "ifc2x3-migrated.ifc")
        subject.run_migrate_patch(infile, outfile, "IFC4")
        ifc = ifcopenshell.open(outfile)
        assert ifc.schema == "IFC4"
