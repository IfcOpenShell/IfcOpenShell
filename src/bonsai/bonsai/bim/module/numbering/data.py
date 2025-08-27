# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
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

import bonsai.tool as tool


def refresh():
    NumberingData.is_loaded = False


class NumberingData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.is_loaded = True
        cls.data["poll"] = cls.poll()
        if cls.data["poll"]:
            cls.data.update({"has_project": cls.has_project(), "project": cls.project()})

    @classmethod
    def poll(cls):
        return cls.has_project()

    @classmethod
    def has_project(cls):
        return bool(tool.Ifc.get())

    @classmethod
    def project(cls):
        ifc = tool.Ifc.get()
        if ifc:
            return ifc.by_type("IfcProject")[0] or None
