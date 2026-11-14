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

from unittest.mock import MagicMock

import bonsai.tool as tool
from bonsai.bim.module.project.data import LinksData
from bonsai.bim.module.project.ui import BIM_PT_links
from test.bim.bootstrap import NewFile


class TestLinksPanel(NewFile):
    def test_explore_tool_results_are_headed_as_queried_element(self, monkeypatch):
        tool.Project.get_project_props().links.add()
        data = {"attributes": {"Name": "Wall"}, "properties": [], "type_properties": []}
        monkeypatch.setattr(LinksData, "linked_data", data)
        monkeypatch.setattr(LinksData, "enable_culling", False)
        panel = MagicMock()
        panel.layout = MagicMock()
        BIM_PT_links.draw(panel, None)
        labels = [call.kwargs.get("text") for call in panel.layout.row.return_value.label.call_args_list]
        assert "Queried Element" in labels
