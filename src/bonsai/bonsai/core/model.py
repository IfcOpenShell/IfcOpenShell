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

import bonsai.core.tool as tool
from typing import Literal


def unjoin_walls(ifc: tool.Ifc, blender: tool.Blender, geometry: tool.Geometry, joiner, model: tool.Model) -> None:
    for obj in blender.get_selected_objects():
        if not (element := ifc.get_entity(obj)) or model.get_usage_type(element) != "LAYER2":
            continue
        geometry.clear_scale(obj)
        joiner.unjoin(obj)


def extend_walls(
    ifc: tool.Ifc, blender: tool.Blender, geometry: tool.Geometry, joiner, model: tool.Model, target
) -> None:
    for obj in blender.get_selected_objects():
        if not (element := ifc.get_entity(obj)) or model.get_usage_type(element) != "LAYER2":
            continue
        geometry.clear_scale(obj)
        joiner.join_E(obj, target)


def join_walls_LV(
    ifc: tool.Ifc,
    blender: tool.Blender,
    geometry: tool.Geometry,
    joiner,
    model: tool.Model,
    join_type: Literal["L", "V"] = "L",
) -> None:
    selected_objs = [
        o for o in blender.get_selected_objects() if (e := ifc.get_entity(o)) and model.get_usage_type(e) == "LAYER2"
    ]
    if len(selected_objs) != 2:
        raise RequireTwoWallsError("Two vertically layered elements must be selected to connect their paths together")

    if active_obj := blender.get_active_object():
        another_selected_object = next(o for o in selected_objs if o != active_obj)
    else:
        active_obj, another_selected_object = selected_objs

    for obj in selected_objs:
        geometry.clear_scale(obj)

    if join_type == "L":
        joiner.join_L(another_selected_object, active_obj)
    elif join_type == "V":
        joiner.join_V(another_selected_object, active_obj)


def join_walls_TZ(ifc: tool.Ifc, blender: tool.Blender, geometry: tool.Geometry, joiner, model: tool.Model) -> None:
    selected_objs = [
        o
        for o in blender.get_selected_objects()
        if (e := ifc.get_entity(o)) and model.get_usage_type(e) in ("LAYER2", "LAYER3")
    ]
    if len(selected_objs) < 2:
        raise RequireAtLeastTwoLayeredElements(
            "Two or more vertically or horizontally layered elements must be selected to connect their paths together"
        )

    for obj in selected_objs:
        geometry.clear_scale(obj)

    elements = [ifc.get_entity(o) for o in blender.get_selected_objects()]
    layer2_elements = []
    layer3_elements = []
    for element in elements:
        usage = model.get_usage_type(element)
        if usage == "LAYER2":
            layer2_elements.append(element)
        elif usage == "LAYER3":
            layer3_elements.append(element)
    if layer3_elements:
        target = ifc.get_object(layer3_elements[0])
        for element in layer2_elements:
            joiner.join_Z(ifc.get_object(element), target)
    else:
        if not (active_obj := blender.get_active_object()):
            active_obj = selected_objs[0]
        for obj in selected_objs:
            if obj == active_obj:
                continue
            joiner.join_T(obj, active_obj)


class RequireTwoWallsError(Exception):
    pass


class RequireAtLeastTwoLayeredElements(Exception):
    pass
