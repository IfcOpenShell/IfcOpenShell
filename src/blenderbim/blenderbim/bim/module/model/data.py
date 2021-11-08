# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of BlenderBIM Add-on.
#
# BlenderBIM Add-on is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BlenderBIM Add-on is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with BlenderBIM Add-on.  If not, see <http://www.gnu.org/licenses/>.

import bpy
import blenderbim.tool as tool


def refresh():
    AuthoringData.is_loaded = False
    WorkspaceData.is_loaded = False


class AuthoringData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.data = {
            "ifc_classes": cls.ifc_classes(),
            "relating_types": cls.relating_types(),
        }
        cls.is_loaded = True

    @classmethod
    def ifc_classes(cls):
        results = []
        classes = set([e.is_a() for e in tool.Ifc.get().by_type("IfcElementType")])
        results.extend([(c, c, "") for c in sorted(classes)])
        return results

    @classmethod
    def relating_types(cls):
        results = []
        ifc_class = bpy.context.scene.BIMModelProperties.ifc_class
        if ifc_class:
            elements = [(str(e.id()), e.Name, "") for e in tool.Ifc.get().by_type(ifc_class)]
            results.extend(sorted(elements, key=lambda s: s[1]))
            return results
        return []


class WorkspaceData(AuthoringData):
    pass
