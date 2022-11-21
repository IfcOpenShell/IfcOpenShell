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

try:
    import ifcpatch
except:
    print("IfcPatch not available")


class Patch(blenderbim.core.tool.Patch):
    @classmethod
    def run_migrate_patch(cls, infile, outfile, schema):
        log = os.path.join(bpy.context.scene.BIMProperties.data_dir, "process.log")
        output = ifcpatch.execute({"input": ifcopenshell.open(infile), "recipe": "Migrate", "arguments": [schema]})
        ifcpatch.write(output, outfile)
