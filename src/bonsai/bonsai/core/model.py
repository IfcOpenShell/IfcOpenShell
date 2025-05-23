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

from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Literal, Iterable

if TYPE_CHECKING:
    import bpy
    import ifcopenshell
    import bonsai.tool as tool

    from mathutils import Vector
    from bonsai.bim.module.model.wall import DumbWallJoiner, DumbWallAligner

    AlignType = Literal["CENTER", "EXTERIOR", "INTERIOR"]
    OffsetType = Literal["CENTER", "EXTERIOR", "INTERIOR"]


def unjoin_walls(
    ifc: tool.Ifc, blender: tool.Blender, geometry: tool.Geometry, joiner: DumbWallJoiner, model: tool.Model
) -> None:
    """Unjoin selected walls."""
    for obj in blender.get_selected_objects():
        if not (element := ifc.get_entity(obj)) or model.get_usage_type(element) != "LAYER2":
            continue
        geometry.clear_scale(obj)
        if ifc.is_moved(obj):
            geometry.run_edit_object_placement(obj=obj)
        joiner.unjoin(obj)


def extend_walls(
    ifc: tool.Ifc,
    blender: tool.Blender,
    geometry: tool.Geometry,
    joiner: DumbWallJoiner,
    model: tool.Model,
    target: Vector,
    connection: Optional[str]=None,
) -> None:
    """Extend selected walls to the target."""
    for obj in blender.get_selected_objects():
        if not (element := ifc.get_entity(obj)) or model.get_usage_type(element) != "LAYER2":
            continue
        geometry.clear_scale(obj)
        joiner.extend(obj, target, connection)


def join_walls_LV(
    ifc: tool.Ifc,
    blender: tool.Blender,
    geometry: tool.Geometry,
    joiner: DumbWallJoiner,
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

    joiner.connect(another_selected_object, active_obj)


def offset_walls(ifc: tool.Ifc, blender: tool.Blender, model: tool.Model, offset_type: OffsetType):
    objs = [
        obj
        for obj in blender.get_selected_objects()
        if (element := ifc.get_entity(obj)) and model.get_usage_type(element) == "LAYER2"
    ]
    for obj in objs:
        model.offset_wall(obj, offset_type)
    model.recalculate_walls(objs)


def align_walls(
    ifc: tool.Ifc, blender: tool.Blender, model: tool.Model, aligner: DumbWallAligner, align_type: AlignType
):
    reference_obj = blender.get_active_object(is_selected=True)
    if not (e := ifc.get_entity(reference_obj) or not model.get_usage_type(e) == "LAYER2"):
        reference_obj = None
    objs = [
        o
        for o in blender.get_selected_objects()
        if o != reference_obj and (e := ifc.get_entity(o)) and model.get_usage_type(e) == "LAYER2"
    ]
    if not reference_obj or not objs:
        raise RequireAtLeastTwoLayeredElements(
            "At least two vertically layered elements must be selected to match alignments."
        )
    aligner.set_reference_wall(reference_obj)
    for obj in objs:
        if align_type == "CENTER":
            aligner.align_centerline(obj)
        elif align_type == "EXTERIOR":
            aligner.align_first_layer(obj)
        elif align_type == "INTERIOR":
            aligner.align_last_layer(obj)


def align_objects(blender: tool.Blender, model: tool.Model, align_type: Literal["CENTER", "POSITIVE", "NEGATIVE"]):
    reference_obj = blender.get_active_object(is_selected=True)
    objs = [o for o in blender.get_selected_objects() if o != reference_obj]
    if not reference_obj or not objs:
        raise RequireAtLeastTwoElements("At least two objects must be selected to match alignments.")
    model.align_objects(reference_obj, objs, align_type)


def extend_wall_to_slab(
    ifc: tool.Ifc,
    geometry: tool.Geometry,
    model: tool.Model,
    slab_obj: bpy.types.Object,
    wall_objs: list[bpy.types.Object],
) -> None:
    if not (clip := model.get_slab_clipping_bmesh(slab_obj)):
        return  # Nothing to clip?
    slab = ifc.get_entity(slab_obj)
    for obj in wall_objs:
        if ifc.is_moved(obj):
            geometry.run_edit_object_placement(obj=obj)
        wall = ifc.get_entity(obj)
        model.clip_wall_to_slab(wall, clip)
        model.connect_wall_to_slab(wall, slab)
    model.reload_body_representation(wall_objs)


def join_walls_TZ(
    ifc: tool.Ifc, blender: tool.Blender, geometry: tool.Geometry, joiner: DumbWallJoiner, model: tool.Model
) -> None:
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


class RequireAtLeastTwoElements(Exception):
    pass


class RequireLayeredElement(Exception):
    pass
