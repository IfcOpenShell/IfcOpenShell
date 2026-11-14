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
import ifcopenshell

import bonsai.tool as tool
from test.bim.bootstrap import NewFile


class TestExportImportFilters(NewFile):
    def test_search_filter_round_trip(self, tmp_path):
        tool.Ifc.set(ifcopenshell.file())
        filter_groups = tool.Search.get_search_props().filter_groups
        tool.Search.import_filter_query('IfcWall, location="G1" + IfcSlab', filter_groups)
        expected = tool.Search.export_filter_query(filter_groups)
        filepath = str(tmp_path / "filter.json")

        bpy.ops.bim.export_search_filter(filepath=filepath)
        filter_groups.clear()
        bpy.ops.bim.import_search_filter(filepath=filepath)

        assert tool.Search.export_filter_query(filter_groups) == expected

    def test_colourscheme_round_trip(self, tmp_path):
        tool.Ifc.set(ifcopenshell.file())
        props = tool.Search.get_search_props()
        props.colourscheme_query = "IfcWall"
        new = props.colourscheme.add()
        new.name = "Wall"
        new.total = 3
        new.colour = (1.0, 0.0, 0.0)
        filepath = str(tmp_path / "colours.json")

        bpy.ops.bim.export_colourscheme(filepath=filepath)
        props.colourscheme_query = ""
        props.colourscheme.clear()
        bpy.ops.bim.import_colourscheme(filepath=filepath)

        assert props.colourscheme_query == "IfcWall"
        assert [(cs.name, cs.total, tuple(cs.colour[0:3])) for cs in props.colourscheme] == [
            ("Wall", 3, (1.0, 0.0, 0.0))
        ]
