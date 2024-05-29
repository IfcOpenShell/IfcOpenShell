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

from __future__ import annotations
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    import bpy
    import ifcopenshell
    import blenderbim.tool as tool
    from blenderbim.bim.module.pset.qto_calculator import QtoCalculator


def calculate_circle_radius(qto: tool.Qto, obj: bpy.types.Object) -> float:
    result = qto.get_radius_of_selected_vertices(obj)
    qto.set_qto_result(result)
    return result


def assign_objects_base_qto(ifc: tool.Ifc, qto: tool.Qto, selected_objects: list[bpy.types.Object]) -> None:
    for obj in selected_objects:
        assign_object_base_qto(ifc, qto, obj)


def assign_object_base_qto(ifc: tool.Ifc, qto: tool.Qto, obj: bpy.types.Object) -> None:
    product = ifc.get_entity(obj)
    if not product:
        return
    base_quantity_name = qto.get_applicable_base_quantity_name(product)
    if not base_quantity_name:
        return
    ifc.run(
        "pset.add_qto",
        product=product,
        name=base_quantity_name,
    )
