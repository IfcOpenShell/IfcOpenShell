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
import ifcopenshell.util.element


def refresh():
    AggregateData.is_loaded = False


class AggregateData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.data = {
            "has_aggregate": cls.has_aggregate(),
            "label": cls.get_label(),
            "relating_object_id": cls.get_relating_object_id(),
        }
        cls.is_loaded = True

    @classmethod
    def has_aggregate(cls):
        return ifcopenshell.util.element.get_aggregate(tool.Ifc.get_entity(bpy.context.active_object))

    @classmethod
    def get_label(cls):
        aggregate = ifcopenshell.util.element.get_aggregate(tool.Ifc.get_entity(bpy.context.active_object))
        if aggregate:
            return f"{aggregate.is_a()}/{aggregate.Name or ''}"

    @classmethod
    def get_relating_object_id(cls):
        aggregate = ifcopenshell.util.element.get_aggregate(tool.Ifc.get_entity(bpy.context.active_object))
        if aggregate:
            return aggregate.id()
