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
import ifcopenshell.util.element


def refresh():
    NestData.is_loaded = False


class NestData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.data = {
            "has_relating_object": cls.has_relating_object(),
            "relating_object_label": cls.get_relating_object_label(),
            "has_related_objects": cls.has_related_objects(),
            "total_components": cls.total_components(),
        }
        cls.is_loaded = True

    @classmethod
    def get_relating_object(cls):
        return ifcopenshell.util.element.get_nest(tool.Ifc.get_entity(bpy.context.active_object))

    @classmethod
    def has_relating_object(cls) -> bool:
        return cls.get_relating_object() is not None

    @classmethod
    def get_relating_object_label(cls) -> str:
        nest = cls.get_relating_object()
        if nest:
            return f"{nest.is_a()}/{nest.Name or ''}"

    @classmethod
    def get_related_objects(cls):
        return ifcopenshell.util.element.get_components(tool.Ifc.get_entity(bpy.context.active_object))

    @classmethod
    def total_components(cls):
        components = cls.get_related_objects()
        return len(components) if components else 0

    @classmethod
    def has_related_objects(cls) -> bool:
        return bool(cls.get_related_objects())
