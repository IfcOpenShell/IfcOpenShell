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

from types import SimpleNamespace
from unittest import mock

import pytest

pytestmark = pytest.mark.covering


def draw_with_thumbnails(type_thumbnails):
    from bonsai.bim.module.covering.workspace import CoveringToolUI
    from bonsai.bim.module.model.data import AuthoringData

    box = mock.MagicMock()
    CoveringToolUI.layout = mock.MagicMock()
    CoveringToolUI.layout.box.return_value = box
    CoveringToolUI.props = SimpleNamespace(ifc_class="IfcCoveringType")
    AuthoringData.data = {"ifc_classes": [("IfcCoveringType",) * 3], "relating_type_data": {"id": 5}}
    AuthoringData.type_thumbnails = type_thumbnails
    with mock.patch.object(CoveringToolUI, "draw_type_selection_interface"):
        CoveringToolUI.draw_basic_bim_tool_interface()
    return box


def test_a_loaded_thumbnail_replaces_the_load_thumbnails_button():
    box = draw_with_thumbnails({5: 42})
    box.template_icon.assert_called_once_with(icon_value=42, scale=5)
    box.operator.assert_not_called()


def test_the_load_thumbnails_button_shows_until_a_thumbnail_is_loaded():
    box = draw_with_thumbnails({})
    box.template_icon.assert_not_called()
    box.operator.assert_called_once()
