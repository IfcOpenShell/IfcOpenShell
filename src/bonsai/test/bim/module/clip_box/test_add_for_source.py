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

import bpy
import ifcopenshell
import ifcopenshell.api.spatial
import pytest

import bonsai.tool as tool
from test.bim.bootstrap import NewFile

pytestmark = pytest.mark.clip_box


def _make_ifc_cube(ifc, ifc_class, location=(0.0, 0.0, 0.0), size=2.0):
    bpy.ops.mesh.primitive_cube_add(size=size, location=location)
    obj = bpy.context.active_object
    entity = ifc.create_entity(ifc_class)
    tool.Ifc.link(entity, obj)
    return entity, obj


class TestAddClipBoxForSourceSpatial(NewFile):
    def test_spatial_creates_clip_box_sized_to_contained_walls(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        storey = ifc.create_entity("IfcBuildingStorey")
        wall_a, _ = _make_ifc_cube(ifc, "IfcWall", location=(0.0, 0.0, 0.0), size=2.0)
        wall_b, _ = _make_ifc_cube(ifc, "IfcWall", location=(4.0, 0.0, 0.0), size=2.0)
        ifcopenshell.api.spatial.assign_container(ifc, products=[wall_a, wall_b], relating_structure=storey)

        result = bpy.ops.bim.add_clip_box_for_source(source_kind="SPATIAL", source_id=str(storey.id()))

        assert result == {"FINISHED"}
        scene_props = tool.ClipBox.get_scene_props()
        assert len(scene_props.clip_boxes) == 1
        host = scene_props.clip_boxes[0].obj
        assert tool.ClipBox.get_object_props(host).is_clip_box is True
        translation, _, scale = host.matrix_world.decompose()
        assert translation.x == pytest.approx(2.0)
        assert scale.x == pytest.approx(3.0)


class TestAddClipBoxForSourceClass(NewFile):
    def test_class_creates_clip_box_for_all_walls(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        # Two walls + one window; the IfcWall pick should cover only the walls.
        _make_ifc_cube(ifc, "IfcWall", location=(0.0, 0.0, 0.0), size=2.0)
        _make_ifc_cube(ifc, "IfcWall", location=(4.0, 0.0, 0.0), size=2.0)
        _make_ifc_cube(ifc, "IfcWindow", location=(20.0, 0.0, 0.0), size=2.0)

        result = bpy.ops.bim.add_clip_box_for_source(source_kind="CLASS", source_id="IfcWall")

        assert result == {"FINISHED"}
        scene_props = tool.ClipBox.get_scene_props()
        host = scene_props.clip_boxes[0].obj
        translation, _, scale = host.matrix_world.decompose()
        # AABB of the two walls only (x in [-1, 5]); window at x=20 must not contribute.
        assert translation.x == pytest.approx(2.0)
        assert scale.x == pytest.approx(3.0)


class TestAddClipBoxForSourceEmpty(NewFile):
    def test_no_matching_elements_reports_error(self):
        # bpy.ops.* raises RuntimeError when an operator reports {"ERROR"},
        # so the assertion is on the raised message rather than the return code.
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        walltype = ifc.create_entity("IfcWallType")
        # No occurrences linked — TYPE source resolves to 0 elements.
        with pytest.raises(RuntimeError, match="No elements found"):
            bpy.ops.bim.add_clip_box_for_source(source_kind="TYPE", source_id=str(walltype.id()))
        scene_props = tool.ClipBox.get_scene_props()
        assert len(scene_props.clip_boxes) == 0

    def test_placeholder_source_id_reports_error(self):
        # With no IFC file loaded, data.py callbacks return the NO_OPTIONS_ID
        # sentinel. Submitting that sentinel as the picked source must ERROR.
        from bonsai.bim.module.clip_box import data as clip_data

        with pytest.raises(RuntimeError, match="No source selected"):
            bpy.ops.bim.add_clip_box_for_source(source_kind="SPATIAL", source_id=clip_data.NO_OPTIONS_ID)
        scene_props = tool.ClipBox.get_scene_props()
        assert len(scene_props.clip_boxes) == 0


class TestRemoveClipBoxOrphan(NewFile):
    def test_remove_orphan_entry_when_host_object_deleted(self):
        # The remove operator must work on an orphan entry — i.e. one whose
        # host empty was deleted out from under it via the outliner.
        bpy.ops.bim.add_clip_box()
        scene_props = tool.ClipBox.get_scene_props()
        assert len(scene_props.clip_boxes) == 1
        host = scene_props.clip_boxes[0].obj
        assert host is not None

        bpy.data.objects.remove(host, do_unlink=True)

        # Entry survives but its `obj` pointer is now None.
        assert len(scene_props.clip_boxes) == 1
        assert scene_props.clip_boxes[0].obj is None

        result = bpy.ops.bim.remove_clip_box(index=0)

        assert result == {"FINISHED"}
        assert len(scene_props.clip_boxes) == 0
