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


def get_popup_keys() -> dict[str, str]:
    keymap = bpy.context.window_manager.keyconfigs.addon.keymaps["Toolbar Popup"]
    return {item.properties.name: item.type for item in keymap.keymap_items if item.idname == "wm.tool_set_by_id"}


class TestToolbarPopupShortcuts:
    def test_create_element_and_annotation_tools_have_their_own_popup_keys(self):
        keys = get_popup_keys()

        assert keys["bim.bim_tool"] == "C"
        assert keys["bim.annotation_tool"] == "A"
