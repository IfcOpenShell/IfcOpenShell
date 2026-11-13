# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026
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

import subprocess

import bpy
import pytest

import bonsai.tool as tool
from test.bim.bootstrap import NewIfc

pytestmark = pytest.mark.misc

INSPECT_SCRIPT = """
import bpy
for obj in bpy.data.objects:
    if obj.type == "EMPTY":
        collection = obj.instance_collection
        print("RESULT", obj.name, collection.name if collection else None)
"""


class TestSaveBlendMetadataFile(NewIfc):
    def test_collection_linked_by_the_user_survives_the_metadata_save(self, tmp_path):
        library_path = tmp_path / "library.blend"
        source = bpy.data.collections.new("Blue Cube")
        bpy.data.libraries.write(str(library_path), {source}, fake_user=True)
        bpy.data.collections.remove(source)

        with bpy.data.libraries.load(str(library_path), link=True) as (data_from, data_to):
            data_to.collections = ["Blue Cube"]
        empty = bpy.data.objects.new("Blue Cube", None)
        empty.instance_type = "COLLECTION"
        empty.instance_collection = data_to.collections[0]
        bpy.context.scene.collection.objects.link(empty)

        ifc_path = tmp_path / "model.ifc"
        tool.Ifc.get().write(str(ifc_path))
        tool.Blender.get_bim_props().ifc_file = str(ifc_path)
        suffix = tool.Blender.get_addon_preferences().metadata_blend_file_suffix
        metadata_path = tmp_path / f"model{suffix}"

        bpy.ops.bim.save_blend_metadata_file()

        assert metadata_path.is_file()
        result = subprocess.run(
            [bpy.app.binary_path, str(metadata_path), "--background", "--python-expr", INSPECT_SCRIPT],
            capture_output=True,
            text=True,
        )
        assert "RESULT Blue Cube Blue Cube" in result.stdout
