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

import bonsai.core.drawing as subject
from test.core.bootstrap import drawing  # ruff: ignore[unused-import]


class TestAddElementClass:
    def test_run(self, drawing):
        drawing.add_element_class("element", "dashed").should_be_called()
        subject.add_element_class(drawing, element="element", name="dashed")


class TestRemoveElementClass:
    def test_run(self, drawing):
        drawing.remove_element_class("element", "dashed").should_be_called()
        subject.remove_element_class(drawing, element="element", name="dashed")
