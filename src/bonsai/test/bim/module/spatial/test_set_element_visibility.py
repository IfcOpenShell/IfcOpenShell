# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026
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
#
# This file was generated with the assistance of an AI coding tool.

"""Covers issue #6664 (Status filter and Isolate/Show/Hide must compose, not clobber
each other) together with the perf regression that same fix introduced: isolating a
small container used to walk every `IfcProduct` in the file to decide what to hide.

The call-count assertion below is a stand-in for a timing test (timing is flaky): it
pins the exact set of objects `tool.Blender.set_object_manual_visibility` is allowed to
touch, so a regression back to a whole-file Python loop fails deterministically instead
of only showing up as a slowdown on large files."""

import bpy
import ifcopenshell
import ifcopenshell.api.pset
import ifcopenshell.api.spatial
import pytest

import bonsai.tool as tool
from test.bim.bootstrap import NewFile

pytestmark = pytest.mark.spatial


def _make_wall(ifc, location, status=None):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    obj = bpy.context.active_object
    wall = ifc.create_entity("IfcWall")
    tool.Ifc.link(wall, obj)
    if status is not None:
        pset = ifcopenshell.api.pset.add_pset(ifc, product=wall, name="Pset_WallCommon")
        ifcopenshell.api.pset.edit_pset(ifc, pset=pset, properties={"Status": status})
    return wall, obj


def _register_container(props, container):
    item = props.containers.add()
    item.ifc_class = container.is_a()
    item["name"] = container.Name or "Unnamed"
    item.ifc_definition_id = container.id()
    return item


class TestSetElementVisibilityIsolate(NewFile):
    def test_isolate_composes_with_status_filter_and_stays_bounded(self, monkeypatch):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)

        storey_a = ifc.create_entity("IfcBuildingStorey", Name="Storey A")
        storey_b = ifc.create_entity("IfcBuildingStorey", Name="Storey B")

        existing_wall, existing_obj = _make_wall(ifc, (0, 0, 0), status="EXISTING")
        demolish_wall, demolish_obj = _make_wall(ifc, (2, 0, 0), status="DEMOLISH")
        new_wall, new_obj = _make_wall(ifc, (4, 0, 0), status="NEW")
        ifcopenshell.api.spatial.assign_container(
            ifc, products=[existing_wall, demolish_wall, new_wall], relating_structure=storey_a
        )

        # Unrelated elements in a different storey; must never be visited individually.
        other_walls = []
        other_objs = []
        for i in range(5):
            wall, obj = _make_wall(ifc, (10 + i, 0, 0), status="EXISTING")
            other_walls.append(wall)
            other_objs.append(obj)
        ifcopenshell.api.spatial.assign_container(ifc, products=other_walls, relating_structure=storey_b)

        props = tool.Spatial.get_spatial_props()
        _register_container(props, storey_a)
        _register_container(props, storey_b)
        props.active_container_index = 0
        props.should_include_children = True

        for obj in (existing_obj, demolish_obj, new_obj, *other_objs):
            obj.hide_set(False)

        # Apply a Status filter that hides DEMOLISH elements everywhere in the file.
        tool.Sequence.set_visibility_by_status({"EXISTING", "NEW"})
        assert demolish_obj.hide_get() is True
        assert existing_obj.hide_get() is False

        calls = []
        original = tool.Blender.set_object_manual_visibility

        def _counting(obj, is_hidden):
            calls.append(obj)
            return original(obj, is_hidden)

        monkeypatch.setattr(tool.Blender, "set_object_manual_visibility", _counting)

        result = bpy.ops.bim.set_element_visibility(mode="ISOLATE", should_filter=False)
        assert result == {"FINISHED"}

        # Correctness (#6664): isolating storey_a must not clobber the Status filter.
        assert existing_obj.hide_get() is False
        assert new_obj.hide_get() is False
        assert demolish_obj.hide_get() is True

        # Everything outside the isolated storey is hidden.
        for obj in other_objs:
            assert obj.hide_get() is True

        # Perf regression guard: a whole-file scan would call this 8 times instead of 3.
        assert len(calls) == 3, f"expected exactly the 3 isolated-storey objects, got {len(calls)}: {calls}"
        assert set(calls) == {existing_obj, demolish_obj, new_obj}

    def test_show_and_hide_only_touch_the_filtered_elements(self, monkeypatch):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)

        storey = ifc.create_entity("IfcBuildingStorey", Name="Storey A")
        target_wall, target_obj = _make_wall(ifc, (0, 0, 0))
        other_walls = []
        other_objs = []
        for i in range(4):
            wall, obj = _make_wall(ifc, (10 + i, 0, 0))
            other_walls.append(wall)
            other_objs.append(obj)
        ifcopenshell.api.spatial.assign_container(ifc, products=[target_wall], relating_structure=storey)

        props = tool.Spatial.get_spatial_props()
        _register_container(props, storey)
        props.active_container_index = 0
        props.should_include_children = True

        for obj in (target_obj, *other_objs):
            obj.hide_set(False)

        calls = []
        original = tool.Blender.set_object_manual_visibility

        def _counting(obj, is_hidden):
            calls.append(obj)
            return original(obj, is_hidden)

        monkeypatch.setattr(tool.Blender, "set_object_manual_visibility", _counting)

        result = bpy.ops.bim.set_element_visibility(mode="HIDE", should_filter=False)

        assert result == {"FINISHED"}
        assert target_obj.hide_get() is True
        for obj in other_objs:
            assert obj.hide_get() is False
        assert calls == [target_obj]
