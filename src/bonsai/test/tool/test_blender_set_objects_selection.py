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

import bpy

import bonsai.tool as tool
from test.bim.bootstrap import NewFile


class TestSetObjectsSelection(NewFile):
    def test_an_object_in_an_excluded_collection_is_ignored(self):
        collection = bpy.data.collections.new("Excluded")
        bpy.context.scene.collection.children.link(collection)
        obj = bpy.data.objects.new("Hidden", None)
        collection.objects.link(obj)
        visible = bpy.data.objects.new("Visible", None)
        bpy.context.scene.collection.objects.link(visible)
        bpy.context.view_layer.layer_collection.children["Excluded"].exclude = True

        tool.Blender.set_objects_selection(bpy.context, obj, [obj, visible])

        assert visible.select_get()
        assert bpy.context.view_layer.objects.active is None
