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
from test.bim.bootstrap import NewIfc


def make_curve_object(ifc_class):
    element = tool.Ifc.get().create_entity(ifc_class)
    obj = bpy.data.objects.new("Curve", bpy.data.curves.new("Curve", "CURVE"))
    bpy.context.scene.collection.objects.link(obj)
    tool.Ifc.link(element, obj)
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    return obj


class TestOverrideModeSetEditCurves(NewIfc):
    def test_curve_without_item_ids_does_not_enter_item_mode(self):
        obj = make_curve_object("IfcBuildingElementProxy")
        bpy.ops.bim.override_mode_set_edit("INVOKE_DEFAULT")
        assert tool.Geometry.get_geometry_props().representation_obj is None
        assert not obj.select_get()
