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
import ifcopenshell
import bonsai.tool as tool
from typing import Any


def refresh():
    LayersData.is_loaded = False


class LayersData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.data = {
            "active_layers": cls.active_layers(),
            "layers": cls.layers(),
        }
        # After .layers().
        cls.data["total_layers"] = cls.total_layers()
        # After .layers() and .active_layers().
        cls.data["layers_enum"] = cls.layers_enum()
        cls.data["layers_enum_no_active"] = cls.layers_enum(skip_active=True)

        cls.is_loaded = True

    @classmethod
    def total_layers(cls) -> int:
        return len(cls.data["layers"])

    @classmethod
    def layers(cls) -> dict[int, dict[str, Any]]:
        results = dict()
        KEEP_ATTRS = set(("id", "Name", "Description"))
        for layer in tool.Ifc.get().by_type("IfcPresentationLayerAssignment"):
            results[layer.id()] = {k: v for k, v in layer.get_info().items() if k in KEEP_ATTRS}
        return results

    @classmethod
    def layers_enum(cls, skip_active: bool = False) -> list[tuple[str, str, str]]:
        active_layers = cls.data["active_layers"]
        return list(
            (str(data["id"]), data["Name"], data["Description"] or "")
            for data in cls.data["layers"].values()
            if not skip_active or (data["id"] not in active_layers)
        )

    @classmethod
    def active_layers(cls) -> dict[int, str]:
        results = {}
        if not (obj := bpy.context.active_object) or not (shape := tool.Geometry.get_active_representation(obj)):
            return results

        attr_name = None
        if shape.is_a("IfcShapeModel"):
            attr_name = "LayerAssignments"
        elif shape.is_a("IfcRepresentationItem"):
            attr_name = "LayerAssignment"
        if attr_name is None:
            return results
        return {layer.id(): layer.Name or "Unnamed" for layer in getattr(shape, attr_name)}
