# This file was generated with the assistance of an AI coding tool.
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

import bpy
import pytest

import bonsai.tool as tool
from test.bim.bootstrap import NewFile


class TestLoadLink(NewFile):
    def test_an_unwritable_cache_folder_is_reported(self, tmp_path):
        folder = tmp_path / "readonly"
        folder.mkdir()
        path = folder / "linked.ifc"
        path.write_text("ISO-10303-21;")
        folder.chmod(0o555)
        link = tool.Project.get_project_props().links.add()
        link.filepath = link.name = str(path)

        try:
            with pytest.raises(RuntimeError, match="not writable"):
                bpy.ops.bim.load_link(link_index=0)
        finally:
            folder.chmod(0o755)
