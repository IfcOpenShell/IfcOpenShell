# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
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
import json
import bonsai.tool as tool


def refresh():
    DiffData.is_loaded = False


class DiffData:
    data = {}
    is_loaded = False
    diff_json_file = None
    diff = None

    @classmethod
    def load(cls):
        cls.data["diff_json"] = cls.diff_json()
        cls.data["total_added"] = cls.total_added()
        cls.data["total_deleted"] = cls.total_deleted()
        cls.data["total_changed"] = cls.total_changed()
        cls.data["changes"] = cls.changes()
        cls.data["saved_searches"] = cls.saved_searches()
        cls.is_loaded = True

    @classmethod
    def diff_json(cls):
        props = bpy.context.scene.DiffProperties
        if not props.diff_json_file:
            cls.diff = None
            return
        if props.diff_json_file != cls.diff_json_file:
            cls.diff_json_file = props.diff_json_file
            with open(props.diff_json_file, "r") as file:
                cls.diff = json.load(file)
        return cls.diff

    @classmethod
    def total_added(cls):
        diff = cls.diff_json()
        if diff:
            return len(diff["added"])

    @classmethod
    def total_deleted(cls):
        diff = cls.diff_json()
        if diff:
            return len(diff["deleted"])

    @classmethod
    def total_changed(cls):
        diff = cls.diff_json()
        if diff:
            return len(diff["changed"].keys())

    @classmethod
    def changes(cls):
        diff = cls.diff_json()
        if not diff:
            return {}
        element = tool.Ifc.get_entity(bpy.context.active_object)
        if not element or not hasattr(element, "GlobalId"):
            return {}
        changes = {k.upper().replace("_", " "): str(v) for k, v in diff["changed"].get(element.GlobalId, {}).items()}
        if element.GlobalId in diff["added"]:
            changes["Added"] = True
        elif element.GlobalId in diff["deleted"]:
            changes["Deleted"] = True
        return changes

    @classmethod
    def saved_searches(cls):
        if not tool.Ifc.get():
            return []
        groups = tool.Ifc.get().by_type("IfcGroup")
        results = []
        for group in groups:
            try:
                data = json.loads(group.Description)
                if isinstance(data, dict) and data.get("type", None) == "BBIM_Search" and data.get("query", None):
                    results.append(group)
            except:
                pass
        return [(str(g.id()), g.Name or "Unnamed", "") for g in sorted(results, key=lambda x: x.Name or "Unnamed")]
