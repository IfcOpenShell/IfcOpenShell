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
from unittest.mock import Mock, patch

from bonsai.bim.module.model.mep import FitFlowSegments
from bonsai.bim.module.model.workspace import Hotkey


def test_a_nested_fitting_error_is_reported_instead_of_raised():
    fake_self = SimpleNamespace(report=Mock())

    result = FitFlowSegments._call_fitting_op(fake_self, Mock(side_effect=RuntimeError("Error: Profile not supported")))

    assert result is False
    fake_self.report.assert_called_once_with({"ERROR"}, "Profile not supported")


def test_the_fit_hotkey_reports_a_fitting_error_instead_of_raising():
    fake_self = SimpleNamespace(report=Mock(), active_class="IfcPipeSegment")

    with patch("bonsai.bim.module.model.workspace.bpy") as bpy:
        bpy.context.selected_objects = [Mock()]
        bpy.ops.bim.fit_flow_segments.side_effect = RuntimeError("Error: Profile not supported")
        Hotkey.hotkey_S_Y(fake_self)

    fake_self.report.assert_called_once_with({"ERROR"}, "Profile not supported")
