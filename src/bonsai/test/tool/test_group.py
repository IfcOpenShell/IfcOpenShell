# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026 Dion Moult <dion@thinkmoult.com>
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

import json

import bpy
import ifcopenshell.api.group
import ifcopenshell.api.system
import pytest

import bonsai.tool as tool
from bonsai.tool.group import Group as subject
from test.bim.bootstrap import NewFile


def add_group(name="Group", description=None, object_type=None):
    group = ifcopenshell.api.group.add_group(tool.Ifc.get(), name=name, description=description)
    group.ObjectType = object_type
    return group


class TestGetDescriptionType(NewFile):
    def test_run(self):
        bpy.ops.bim.create_project()
        group = add_group(description=json.dumps({"type": "BBIM_Search", "query": "IfcWall"}))
        assert subject.get_description_type(group) == "BBIM_Search"

    @pytest.mark.parametrize("description", [None, "", "Not JSON", "[1, 2]", '{"no_type": 1}'])
    def test_groups_without_a_bonsai_type(self, description):
        bpy.ops.bim.create_project()
        assert subject.get_description_type(add_group(description=description)) is None


class TestIsInternal(NewFile):
    @pytest.mark.parametrize("object_type", ["DRAWING", "DRAWINGS", "SEARCH"])
    def test_internal_object_types(self, object_type):
        bpy.ops.bim.create_project()
        assert subject.is_internal(add_group(object_type=object_type))

    @pytest.mark.parametrize("data_type", ["BBIM_Search", "BBIM_AnimationColorScheme"])
    def test_internal_description_types(self, data_type):
        bpy.ops.bim.create_project()
        assert subject.is_internal(add_group(description=json.dumps({"type": data_type})))

    def test_linked_aggregate_group(self):
        bpy.ops.bim.create_project()
        assert subject.is_internal(add_group(name="BBIM_Linked_Aggregate"))

    def test_user_groups(self):
        bpy.ops.bim.create_project()
        assert not subject.is_internal(add_group(name="Furniture", description="Loose furniture"))
        assert not subject.is_internal(add_group(name="Phase 1", object_type="PHASE"))

    def test_systems_are_never_internal(self):
        bpy.ops.bim.create_project()
        system = ifcopenshell.api.system.add_system(tool.Ifc.get())
        system.ObjectType = "SEARCH"
        assert not subject.is_internal(system)


class TestGetUserGroups(NewFile):
    def test_run(self):
        bpy.ops.bim.create_project()
        user_group = add_group(name="Furniture")
        internal_group = add_group(name="Plan", object_type="DRAWING")
        ifcopenshell.api.system.add_system(tool.Ifc.get())
        assert subject.get_user_groups() == [user_group]
        assert set(subject.get_user_groups(include_internal=True)) == {user_group, internal_group}


class TestImportGroups(NewFile):
    def test_hiding_internal_groups(self):
        bpy.ops.bim.create_project()
        add_group(name="Furniture")
        parent = add_group(name="DRAWINGS", object_type="DRAWINGS")
        drawing = add_group(name="Plan", object_type="DRAWING")
        ifcopenshell.api.group.assign_group(tool.Ifc.get(), products=[drawing], group=parent)
        subject.import_groups("IfcGroup")
        assert [g.name for g in subject.get_group_props().groups] == ["Furniture"]

    def test_showing_internal_groups_when_toggled(self):
        bpy.ops.bim.create_project()
        add_group(name="Furniture")
        add_group(name="DRAWINGS", object_type="DRAWINGS")
        subject.get_group_props().should_show_internal = True
        subject.import_groups("IfcGroup")
        assert [g.name for g in subject.get_group_props().groups] == ["DRAWINGS", "Furniture"]

    def test_loading_collapsed_nested_groups_while_filtering(self):
        bpy.ops.bim.create_project()
        parent = add_group(name="Phase 1")
        child = add_group(name="Kitchen")
        ifcopenshell.api.group.assign_group(tool.Ifc.get(), products=[child], group=parent)
        subject.import_groups("IfcGroup")
        assert [g.name for g in subject.get_group_props().groups] == ["Phase 1"]
        subject.get_group_props().group_filter = "kitchen"
        subject.import_groups("IfcGroup")
        assert [g.name for g in subject.get_group_props().groups] == ["Phase 1", "Kitchen"]
