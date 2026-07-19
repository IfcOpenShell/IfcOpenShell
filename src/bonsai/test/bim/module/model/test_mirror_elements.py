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

"""Pins the contract that ``bim.mirror_elements`` re-syncs a mirrored wall's
filled opening to the wall's new (mirrored) placement.

``MirrorElements`` duplicates the selection, then repositions each
duplicate's ``matrix_world`` directly — the duplicated ``IfcOpeningElement``
has no selectable Blender object of its own, so without an explicit resync
its placement is left behind at the pre-mirror location while the host wall
and door move on (issue #3302)."""

from unittest.mock import patch

import bpy
import pytest

import bonsai.tool as tool
from test.bim.bootstrap import NewFile

pytestmark = pytest.mark.model


def _build_walled_door():
    """A single LAYER2 wall, extended out, with a door voided into its span."""
    bpy.ops.bim.create_project()
    bpy.ops.bim.select_library_file(filepath="./bonsai/bim/data/libraries/IFC4 Demo Library.ifc", append_all=True)

    ifc = tool.Ifc.get()
    wall_type = next(e for e in ifc.by_type("IfcWallType") if e.Name == "WAL100")
    door_type = next(e for e in ifc.by_type("IfcDoorType") if e.Name == "DT01")

    props = bpy.context.scene.BIMModelProperties
    props.ifc_class = "IfcWallType"
    props.relating_type_id = str(wall_type.id())
    bpy.context.scene.cursor.location = (0, 0, 0)
    bpy.ops.bim.add_occurrence()
    wall_obj = bpy.data.objects["IfcWall/Wall"]

    bpy.ops.object.select_all(action="DESELECT")
    wall_obj.select_set(True)
    bpy.context.view_layer.objects.active = wall_obj
    bpy.context.scene.cursor.location = (6, 0, 0)
    bpy.ops.bim.hotkey(hotkey="S_E")

    bpy.ops.object.select_all(action="DESELECT")
    wall_obj.select_set(True)
    bpy.context.view_layer.objects.active = wall_obj
    props.ifc_class = "IfcDoorType"
    props.relating_type_id = str(door_type.id())
    bpy.context.scene.cursor.location = (3, 0, 0)
    bpy.ops.bim.add_occurrence()
    door_obj = bpy.data.objects["IfcDoor/Door"]

    return wall_obj, door_obj


class TestMirrorElementsResyncsOpenings(NewFile):
    def test_mirrored_opening_follows_the_mirrored_host_wall(self):
        wall_obj, door_obj = _build_walled_door()

        mirror_empty = bpy.data.objects.new("MirrorAxis", None)
        bpy.context.collection.objects.link(mirror_empty)
        mirror_empty.location = (12, 0, 0)
        bpy.context.view_layer.update()

        bpy.ops.object.select_all(action="DESELECT")
        wall_obj.select_set(True)
        door_obj.select_set(True)
        mirror_empty.select_set(True)
        bpy.context.view_layer.objects.active = mirror_empty

        assert bpy.ops.bim.mirror_elements() == {"FINISHED"}
        bpy.context.view_layer.update()

        new_wall_obj = next(o for o in bpy.data.objects if o.name.startswith("IfcWall/") and o != wall_obj)
        new_door_obj = next(o for o in bpy.data.objects if o.name.startswith("IfcDoor/") and o != door_obj)

        new_door_el = tool.Ifc.get_entity(new_door_obj)
        assert new_door_el.FillsVoids, "mirrored door must still fill an opening"
        opening = new_door_el.FillsVoids[0].RelatingOpeningElement

        import ifcopenshell.util.placement

        opening_x = ifcopenshell.util.placement.get_local_placement(opening.ObjectPlacement)[0][3]
        door_x = new_door_obj.matrix_world.translation.x
        wall_min_x = min(v[0] for v in new_wall_obj.bound_box)
        wall_max_x = max(v[0] for v in new_wall_obj.bound_box)
        wall_min_x = new_wall_obj.matrix_world.translation.x + wall_min_x
        wall_max_x = new_wall_obj.matrix_world.translation.x + wall_max_x

        assert opening_x == pytest.approx(
            door_x, abs=0.01
        ), "the mirrored opening must sit where the mirrored door now is, not at the door's pre-mirror position"
        assert wall_min_x <= opening_x <= wall_max_x, "the mirrored opening must land inside its new host wall's span"

    def test_recalculate_walls_is_skipped_when_no_wall_is_mirrored(self):
        bpy.ops.bim.create_project()
        bpy.ops.mesh.primitive_cube_add()
        obj = bpy.context.active_object
        obj.name = "Furniture"
        rprops = tool.Root.get_root_props()
        rprops.ifc_product = "IfcElement"
        bpy.ops.bim.assign_class(ifc_class="IfcFurniture")

        mirror_empty = bpy.data.objects.new("MirrorAxis", None)
        bpy.context.collection.objects.link(mirror_empty)
        mirror_empty.location = (5, 0, 0)
        bpy.context.view_layer.update()

        bpy.ops.object.select_all(action="DESELECT")
        obj.select_set(True)
        mirror_empty.select_set(True)
        bpy.context.view_layer.objects.active = mirror_empty

        with patch.object(tool.Model, "recalculate_walls") as recalculate_walls:
            assert bpy.ops.bim.mirror_elements() == {"FINISHED"}

        recalculate_walls.assert_not_called()
