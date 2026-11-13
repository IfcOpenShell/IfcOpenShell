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

import bonsai.tool as tool
from test.bim.bootstrap import NewFile


class TestLinkIfc(NewFile):
    def test_linking_the_same_file_and_query_twice_adds_one_row(self, tmp_path):
        path = tmp_path / "linked.ifc"
        path.write_text("ISO-10303-21;")
        props = tool.Project.get_project_props()
        link = props.links.add()
        link.filepath = link.name = tool.Ifc.get_uri(path, use_relative_path=False)
        link.query = "IfcElement"

        bpy.ops.bim.link_ifc(filepath=str(path), directory=str(tmp_path), query="IfcElement")

        assert len(props.links) == 1
