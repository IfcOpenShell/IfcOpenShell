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

"""TypeData.relating_type_classes() feeds an EnumProperty ``items`` callback
(type/prop.py get_relating_type_class -> BIMTypeProperties.relating_type_class,
drawn at type/ui.py:78), which Blender requires to always return a list.

The "no active object" branch used to fall off the end of the function and
implicitly return None. The sibling branch two lines below ("no ifc entity
on the object") already returned [] correctly.

BIM_PT_type.poll() gates the panel with tool.Blender.get_active_object(),
which falls back to view_layer.objects.active when bpy.context.active_object
is unavailable (its own docstring: "stripped operator contexts"; added in
25651a1507e). relating_type_classes() read the narrower bpy.context.active_object
directly, so poll() can pass in exactly the context shape where
relating_type_classes() still saw no active object.
"""

import bpy
import pytest

import bonsai.tool as tool
from bonsai.bim.module.type.data import TypeData
from bonsai.bim.module.type.ui import BIM_PT_type
from test.bim.bootstrap import NewFile

pytestmark = pytest.mark.type


class TestRelatingTypeClassesNoneActiveObject(NewFile):
    def test_no_active_object_at_all_returns_empty_list(self):
        assert bpy.context.active_object is None
        TypeData.is_loaded = False
        result = TypeData.relating_type_classes()
        assert result == []

    def test_stripped_context_active_object_returns_empty_list_not_none(self):
        """Reproduces the gap: poll() passes via the view_layer fallback while
        bpy.context.active_object is unavailable to relating_type_classes()."""
        bpy.ops.bim.create_project()
        bpy.ops.mesh.primitive_cube_add(size=1)
        obj = bpy.context.active_object
        bpy.ops.bim.assign_class(obj=obj.name, ifc_class="IfcWall", predefined_type="STANDARD", userdefined_type="")
        tool.Blender.set_active_object(obj)
        assert tool.Ifc.get_entity(obj) is not None

        with bpy.context.temp_override(active_object=None):
            assert bpy.context.active_object is None
            assert bpy.context.view_layer.objects.active is obj
            assert tool.Blender.get_active_object() is obj
            assert BIM_PT_type.poll(bpy.context) is True

            TypeData.is_loaded = False
            result = TypeData.relating_type_classes()
            assert result == []
            assert result is not None
