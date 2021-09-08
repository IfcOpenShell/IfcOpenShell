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
import test.bim.bootstrap
from blenderbim.bim.ifc import IfcStore


class TestImportIFC(test.bim.bootstrap.NewFile):
    def test_manual_offset_of_object_placements(self):
        bpy.ops.import_ifc.bim(
            filepath="./test/files/manual-geolocation.ifc",
            should_offset_model=True,
            model_offset_coordinates="-268388.5, -5774506.0, -21.899999618530273",
        )
        assert IfcStore.id_map[63].location.length < 1
