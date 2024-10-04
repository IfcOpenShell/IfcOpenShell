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

import os
import bpy
import json
import ifcopenshell
import bonsai.core.tool
import bonsai.tool as tool
from contextlib import contextmanager
from mathutils import Vector
from ifcclash import ifcclash


class Clash(bonsai.core.tool.Clash):

    @classmethod
    def export_clash_sets(cls) -> list[ifcclash.ClashSet]:
        clash_sets = []
        for clash_set in bpy.context.scene.BIMClashProperties.clash_sets:
            a = []
            b = []
            for ab in ["a", "b"]:
                for data in getattr(clash_set, ab):
                    clash_source = {"file": data.name}
                    query = tool.Search.export_filter_query(data.filter_groups)
                    if query and data.mode != "a":
                        clash_source["selector"] = query
                        clash_source["mode"] = data.mode
                    if ab == "a":
                        a.append(clash_source)
                    elif ab == "b":
                        b.append(clash_source)
            clash_set_data = {"name": clash_set.name, "mode": clash_set.mode, "a": a, "b": b}
            if clash_set.mode == "intersection":
                clash_set_data["tolerance"] = clash_set.tolerance
                clash_set_data["check_all"] = clash_set.check_all
            elif clash_set.mode == "collision":
                clash_set_data["allow_touching"] = clash_set.allow_touching
            elif clash_set.mode == "clearance":
                clash_set_data["clearance"] = clash_set.clearance
                clash_set_data["check_all"] = clash_set.check_all
            clash_sets.append(clash_set_data)
        return clash_sets

    @classmethod
    def get_clash(cls, clash_set, a_global_id, b_global_id):
        clashes = clash_set.get("clashes", None)
        if not clashes:
            return
        return clashes.get(f"{a_global_id}-{b_global_id}", None)

    @classmethod
    def get_clash_set(cls, name):
        for clash_set in ClashStore.clash_sets:
            if clash_set["name"] == name:
                return clash_set

    @classmethod
    def get_clash_sets(cls):
        return ClashStore.clash_sets

    @classmethod
    def import_active_clashes(cls):
        clash_set = bpy.context.scene.BIMClashProperties.active_clash_set
        if not clash_set:
            return
        clash_set.clashes.clear()
        result = tool.Clash.get_clash_set(clash_set.name)
        for clash in sorted(result.get("clashes", {}).values(), key=lambda x: x["distance"]):
            blender_clash = clash_set.clashes.add()
            blender_clash.a_global_id = clash["a_global_id"]
            blender_clash.b_global_id = clash["b_global_id"]
            blender_clash.a_name = "{}/{}".format(clash["a_ifc_class"], clash["a_name"])
            blender_clash.b_name = "{}/{}".format(clash["b_ifc_class"], clash["b_name"])
            blender_clash.status = False if not "status" in clash.keys() else clash["status"]

    @classmethod
    def load_clash_sets(cls, fn):
        with open(fn) as f:
            ClashStore.clash_sets = json.load(f)

    @classmethod
    def look_at(cls, target, location):
        camera_location = location
        area = next(area for area in bpy.context.screen.areas if area.type == "VIEW_3D")
        region = next(region for region in area.regions if region.type == "WINDOW")
        space = next(space for space in area.spaces if space.type == "VIEW_3D")
        override = {"area": area, "region": region, "space_data": space}
        space.region_3d.view_location = target
        space.region_3d.view_rotation = Vector((camera_location - target)).to_track_quat("Z", "Y")
        space.region_3d.view_distance = (camera_location - target).length
        space.shading.show_xray = True


class ClashStore:
    clash_sets = None
    path = None

    @staticmethod
    def purge():
        ClashStore.clash_sets = None
        ClashStore.path = None
