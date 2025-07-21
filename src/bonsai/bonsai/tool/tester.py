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

from __future__ import annotations

from typing import TYPE_CHECKING, Union

import bpy
import ifctester.ids
import ifctester.reporter

if TYPE_CHECKING:
    from bonsai.bim.module.tester.prop import IfcTesterProperties


class Tester:
    specs: Union[ifctester.ids.Ids, None] = None
    report: list[ifctester.reporter.ResultsSpecification] = []

    @classmethod
    def get_tester_props(cls) -> IfcTesterProperties:
        assert (scene := bpy.context.scene)
        return scene.IfcTesterProperties  # pyright: ignore[reportAttributeAccessIssue]
