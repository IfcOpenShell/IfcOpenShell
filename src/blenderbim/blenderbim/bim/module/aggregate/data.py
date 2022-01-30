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
            "has_relating_object": cls.has_relating_object(),
            "relating_object_label": cls.get_relating_object_label(),
            "relating_object_id": cls.get_relating_object_id(),
            "ifc_class": cls.ifc_class(),
        }
        cls.is_loaded = True

    @classmethod
    def get_relating_object(cls):
        return ifcopenshell.util.element.get_relating_object(tool.Ifc.get_entity(bpy.context.active_object))

    @classmethod
    def has_relating_object(cls) -> bool:
        return cls.get_relating_object() is not None

    @classmethod
    def get_relating_object_label(cls) -> str:
        aggregate = cls.get_relating_object()
        if aggregate:
            return f"{aggregate.is_a()}/{aggregate.Name or ''}"

    @classmethod
    def get_relating_object_id(cls) -> int:
        aggregate = cls.get_relating_object()
        if aggregate:
            return aggregate.id()

    @classmethod
    def ifc_class(cls):
        element = tool.Ifc.get_entity(bpy.context.active_object)
        if element:
            return element.is_a()
