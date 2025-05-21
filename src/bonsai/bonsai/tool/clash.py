# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2024 Dion Moult <dion@thinkmoult.com>
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
import os
import bpy
import json
import ifcopenshell
import bonsai.core.tool
import bonsai.tool as tool
from contextlib import contextmanager
from mathutils import Vector
from ifcclash import ifcclash
from ifcclash.ifcclash import ClashSource
from typing import TYPE_CHECKING, Union, Literal, get_args

if TYPE_CHECKING:
    from bonsai.bim.module.clash.prop import BIMClashProperties


class Clash(bonsai.core.tool.Clash):

    @classmethod
    def get_clash_props(cls) -> BIMClashProperties:
        return bpy.context.scene.BIMClashProperties

    ClashSourceGroup = Literal["a", "b"]
    CLASH_SOURCE_GROUP_LITERALS = ("a", "b")

    @classmethod
    def export_clash_sets(cls) -> list[ifcclash.ClashSet]:
        clash_sets: list[ifcclash.ClashSet] = []
        props = cls.get_clash_props()
        for clash_set in props.clash_sets:
            a: list[ClashSource] = []
            b: list[ClashSource] = []
            for ab, ab_data in clash_set.get_clash_sources().items():
                for data in ab_data:
                    clash_source: ClashSource = {"file": data.name}
                    query = tool.Search.export_filter_query(data.filter_groups)
                    if query and data.mode != "a":
                        clash_source["selector"] = query
                        clash_source["mode"] = data.mode
                    if ab == "a":
                        a.append(clash_source)
                    elif ab == "b":
                        b.append(clash_source)
            clash_set_data = ifcclash.ClashSet(name=clash_set.name, mode=clash_set.mode, a=a, b=b)
            if clash_set.mode == "intersection":
                clash_set_data["tolerance"] = clash_set.tolerance
                clash_set_data["check_all"] = clash_set.check_all
            elif clash_set.mode == "collision":
                clash_set_data["allow_touching"] = clash_set.allow_touching
            elif clash_set.mode == "clearance":
                clash_set_data["clearance"] = clash_set.clearance
                clash_set_data["check_all"] = clash_set.check_all
            clash_sets.append(ifcclash.ClashSet(**clash_set_data))
        return clash_sets

    @classmethod
    def get_clash(
        cls, clash_set: ifcclash.ClashSet, a_global_id: str, b_global_id: str
    ) -> Union[ifcclash.ClashResult, None]:
        clashes = clash_set.get("clashes", None)
        if not clashes:
            return
        return clashes.get(f"{a_global_id}-{b_global_id}", None)

    @classmethod
    def get_clash_set(cls, name: str) -> Union[ifcclash.ClashSet, None]:
        for clash_set in ClashStore.clash_sets:
            if clash_set["name"] == name:
                return clash_set

    @classmethod
    def get_clash_sets(cls) -> list[ifcclash.ClashSet]:
        return ClashStore.clash_sets

    @classmethod
    def import_active_clashes(cls) -> None:
        props = cls.get_clash_props()
        clash_set = props.active_clash_set
        if not clash_set:
            return
        clash_set.clashes.clear()
        result = tool.Clash.get_clash_set(clash_set.name)
        assert result is not None
        if "clashes" not in result:
            return
        for clash in sorted(result["clashes"].values(), key=lambda x: x["distance"]):
            blender_clash = clash_set.clashes.add()
            blender_clash.a_global_id = clash["a_global_id"]
            blender_clash.b_global_id = clash["b_global_id"]
            blender_clash.a_name = "{}/{}".format(clash["a_ifc_class"], clash["a_name"])
            blender_clash.b_name = "{}/{}".format(clash["b_ifc_class"], clash["b_name"])
            blender_clash.status = False if not "status" in clash else clash["status"]

    @classmethod
    def load_clash_sets(cls, fn: str) -> None:
        """
        :param fn: .json filepath to load clash results from.
        """
        with open(fn) as f:
            ClashStore.clash_sets = json.load(f)

    @classmethod
    def look_at(cls, target: Vector, location: Vector) -> None:
        camera_location = location
        area = tool.Blender.get_view3d_area()
        region = next(region for region in area.regions if region.type == "WINDOW")
        space = next(space for space in area.spaces if space.type == "VIEW_3D")
        override = {"area": area, "region": region, "space_data": space}
        assert isinstance(space, bpy.types.SpaceView3D)
        assert space.region_3d
        space.region_3d.view_location = target
        space.region_3d.view_rotation = Vector((camera_location - target)).to_track_quat("Z", "Y")
        space.region_3d.view_distance = (camera_location - target).length
        space.shading.show_xray = True


class ClashStore:
    clash_sets: list[ifcclash.ClashSet] = []

    @staticmethod
    def purge():
        ClashStore.clash_sets = []
