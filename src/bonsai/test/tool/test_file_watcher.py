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

from pathlib import Path
from unittest import mock

import bpy
import ifcopenshell
import ifcopenshell.api.root
import pytest

import bonsai.tool as tool
from test.bim.bootstrap import NewIfc


@pytest.fixture
def saved_project():
    tool.Project.save_test_project()
    yield Path(tool.Blender.get_bim_props().ifc_file)
    tool.FileWatcher.cancel_timer()
    tool.Blender.get_addon_preferences().watch_ifc_enabled = False


def modify_file_externally(path: Path, wall_name: str) -> None:
    ifc_file = ifcopenshell.open(str(path))
    ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcWall", name=wall_name)
    ifc_file.write(str(path))


class TestFileWatcher(NewIfc):
    def test_change_on_disk_is_acted_on_only_once_the_file_has_settled(self, saved_project):
        tool.Blender.get_addon_preferences().watch_ifc_enabled = True
        tool.FileWatcher.reset_timer()
        modify_file_externally(saved_project, "External")

        with mock.patch.object(tool.FileWatcher, "_handle_external_change") as handle_change:
            tool.FileWatcher._on_timer_expired()
            assert not handle_change.called
            tool.FileWatcher._on_timer_expired()
            assert handle_change.call_count == 1
            tool.FileWatcher._on_timer_expired()
            assert handle_change.call_count == 1


class TestReloadProject(NewIfc):
    def test_reload_shows_what_changed_on_disk_and_keeps_the_rest_of_the_scene(self, saved_project):
        bpy.context.scene.collection.objects.link(bpy.data.objects.new("Reference", None))
        modify_file_externally(saved_project, "External")
        assert "IfcWall/External" not in bpy.data.objects

        bpy.ops.bim.reload_project()

        assert "IfcWall/External" in bpy.data.objects
        assert "Reference" in bpy.data.objects
