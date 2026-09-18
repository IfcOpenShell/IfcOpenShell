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


import webbrowser

import bpy
import pytest

import bonsai.bim.handler
import bonsai.tool as tool
from bonsai.bim.ifc import IfcStore

# Monkey-patch webbrowser opening since we want to test headlessly
webbrowser.open = lambda x: True
tool.Drawing.open_with_user_command = lambda x, y: True


class NewFile:
    @pytest.fixture(autouse=True)
    def setup(self):
        IfcStore.purge()
        bpy.ops.wm.read_homefile(app_template="")
        if bpy.data.objects:
            bpy.data.batch_remove(bpy.data.objects)
            bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)
        bonsai.bim.handler.load_post(None)


class NewIfc:
    @pytest.fixture(autouse=True)
    def setup(self):
        IfcStore.purge()
        bpy.ops.wm.read_homefile(app_template="")
        bpy.data.batch_remove(bpy.data.objects)
        bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)
        bonsai.bim.handler.load_post(None)
        bpy.ops.bim.create_project()


class NewIfc4X3:
    @pytest.fixture(autouse=True)
    def setup(self):
        IfcStore.purge()
        bpy.ops.wm.read_homefile(app_template="")
        bpy.data.batch_remove(bpy.data.objects)
        bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)
        bonsai.bim.handler.load_post(None)
        props = tool.Project.get_project_props()
        props.export_schema = "IFC4X3_ADD2"
        bpy.ops.bim.create_project()
