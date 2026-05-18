# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
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


import ifcopenshell.api.cost

import bonsai.core.tool
import bonsai.tool as tool
import test.bim.bootstrap
from bonsai.tool.cost import Cost as subject
from test.bim.bootstrap import NewFile


class TestImplementsTool(NewFile):
    def test_run(self):
        assert isinstance(subject(), bonsai.core.tool.Cost)


class TestDisableEditingCostItemParent(NewFile):
    def test_avoid_recursion_error(newfile, monkeypatch):
        class DummyProps:
            def __init__(self):
                self.change_cost_item_parent = None
                self.active_cost_item_id = 5

        props = DummyProps()
        monkeypatch.setattr("bonsai.tool.Cost.get_cost_props", lambda: props)
        subject.disable_editing_cost_item_parent()
        assert props.active_cost_item_id == 0
        assert props.change_cost_item_parent is not False
