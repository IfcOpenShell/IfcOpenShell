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

import bmesh
import bpy

import bonsai.tool as tool
from test.bim.bootstrap import NewIfc


def add_wall():
    bpy.ops.mesh.primitive_cube_add()
    obj = bpy.context.active_object
    root_props = tool.Root.get_root_props()
    root_props.ifc_product = "IfcElement"
    root_props.ifc_class = "IfcWall"
    bpy.ops.bim.assign_class()
    return obj


def add_extruded_wall():
    obj = add_wall()
    bpy.ops.bim.update_representation(ifc_representation_class="IfcExtrudedAreaSolid/IfcRectangleProfileDef")
    return obj


def body(obj):
    return tool.Ifc.get_entity(obj).Representation.Representations[0]


def enter_plain_edit_mode(obj):
    # Plain Blender edit mode, not Bonsai's item mode (bim.override_mode_set_edit).
    tool.Blender.select_and_activate_single_object(bpy.context, obj)
    bpy.ops.object.mode_set(mode="EDIT")
    return bmesh.from_edit_mesh(obj.data)


def raise_top_face(obj, bm, offset=0.5):
    for vert in bm.verts:
        if vert.co.z > 0:
            vert.co.z += offset
    bmesh.update_edit_mesh(obj.data)


def tab_out():
    return bpy.ops.bim.override_mode_set_object("INVOKE_DEFAULT")


def max_z(obj):
    return max(v.co.z for v in obj.data.vertices)


class TestOverrideModeSetObjectDirectEdit(NewIfc):
    def test_moving_vertices_of_a_tessellated_element_saves_the_representation(self):
        obj = add_wall()
        old_body = body(obj)
        assert old_body.RepresentationType == "Tessellation"
        bm = enter_plain_edit_mode(obj)
        raise_top_face(obj, bm)
        tab_out()
        assert obj.mode == "OBJECT"
        new_body = body(obj)
        assert new_body != old_body
        assert new_body.RepresentationType == "Tessellation"
        z_values = [c[2] for item in new_body.Items for c in item.Coordinates.CoordList]
        assert max(z_values) > 1.4

    def test_tabbing_out_without_changes_keeps_the_representation(self):
        obj = add_wall()
        old_body = body(obj)
        enter_plain_edit_mode(obj)
        tab_out()
        assert obj.mode == "OBJECT"
        assert body(obj) == old_body

    def test_assigning_a_material_to_faces_saves_the_representation(self):
        obj = add_wall()
        for name in ("First", "Second"):
            obj.data.materials.append(bpy.data.materials.new(name))
        old_body = body(obj)
        bm = enter_plain_edit_mode(obj)
        bm.faces.ensure_lookup_table()
        bm.faces[0].material_index = 1
        bmesh.update_edit_mesh(obj.data)
        tab_out()
        new_body = body(obj)
        assert new_body != old_body
        styles = {tool.Ifc.get_entity(slot.material) for slot in obj.material_slots}
        assert None not in styles
        assert len(styles) == 2

    def test_editing_a_parametric_element_reverts_the_mesh(self):
        obj = add_extruded_wall()
        old_body = body(obj)
        assert old_body.RepresentationType == "SweptSolid"
        original_max_z = max_z(obj)
        bm = enter_plain_edit_mode(obj)
        raise_top_face(obj, bm)
        tab_out()
        assert obj.mode == "OBJECT"
        assert body(obj) == old_body
        assert abs(max_z(obj) - original_max_z) < 1e-6
