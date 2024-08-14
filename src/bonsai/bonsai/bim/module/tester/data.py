# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2023 Dion Moult <dion@thinkmoult.com>
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


def refresh():
    TesterData.is_loaded = False


class TesterData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.data = {"has_report": cls.has_report(), "specification": cls.specification()}
        cls.is_loaded = True

    @classmethod
    def has_report(cls):
        return tool.Tester.report

    @classmethod
    def specification(cls):
        if not tool.Tester.report:
            return {}
        props = bpy.context.scene.IfcTesterProperties
        return tool.Tester.report[props.active_specification_index]
