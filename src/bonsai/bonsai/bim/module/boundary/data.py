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
    SpaceBoundariesData.is_loaded = False


class SpaceBoundariesData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.data = {"boundaries": cls.boundaries()}
        cls.is_loaded = True

    @classmethod
    def boundaries(cls):
        results = []
        element = tool.Ifc.get_entity(bpy.context.active_object)
        for rel in element.BoundedBy or []:
            description = f"{rel.id()} > {rel.RelatedBuildingElement.is_a()}/{rel.RelatedBuildingElement.Name}"
            results.append({"id": rel.id(), "description": description})
        return results
