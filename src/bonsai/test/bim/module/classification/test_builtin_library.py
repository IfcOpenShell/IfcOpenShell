# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
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

# This file was generated with the assistance of an AI coding tool.

import bpy

from bonsai.bim.ifc import IfcStore
from bonsai.bim.module.classification.data import ClassificationsData
from test.bim.bootstrap import NewFile


class TestBuiltinClassificationLibrary(NewFile):
    def test_picking_a_bundled_library_loads_it(self):
        bpy.ops.bim.create_project()
        IfcStore.classification_file = None
        ClassificationsData.load()
        props = bpy.context.scene.BIMClassificationProperties
        assert IfcStore.classification_file is None
        props.builtin_classification_library = "Brick.ifc"
        assert IfcStore.classification_file is not None
        assert IfcStore.classification_file.by_type("IfcClassification")
