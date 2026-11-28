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

import bpy
import pytest

pytestmark = pytest.mark.misc


class TestSectionCutawayPanels:
    @pytest.mark.parametrize("panel_name", ["BIM_PT_section_plane", "BIM_PT_section_with_cappings"])
    def test_panel_is_shown_inside_the_drawings_tab(self, panel_name):
        panel = getattr(bpy.types, panel_name)
        drawings_tab = bpy.types.BIM_PT_tab_drawings

        assert panel.bl_parent_id == "BIM_PT_tab_drawings"
        assert panel.bl_context == drawings_tab.bl_context
