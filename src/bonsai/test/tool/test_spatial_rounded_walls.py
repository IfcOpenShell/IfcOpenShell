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

# This file was generated with the assistance of an AI coding tool.

import math

import bpy
import mathutils
import shapely

import bonsai.tool as tool
from bonsai.tool.spatial import Spatial as subject
from test.bim.bootstrap import NewFile

LIBRARY = "./bonsai/bim/data/libraries/IFC4 Demo Library.ifc"
ROOM_SIZE = 10.0
FILLET_RADIUS = 3.0


class TestGetUnionShapeFromSelectedObjects(NewFile):
    def add_room_with_rounded_corner(self) -> None:
        bpy.ops.bim.create_project()
        bpy.ops.bim.select_library_file(filepath=LIBRARY, append_all=True)
        ifc = tool.Ifc.get()
        props = bpy.context.scene.BIMModelProperties
        props.ifc_class = "IfcWallType"
        wall_type = next(e for e in ifc.by_type("IfcWallType") if e.Name == "WAL100")
        props.relating_type_id = str(wall_type.id())
        corners = [(0, 0, 0), (ROOM_SIZE, 0, 0), (ROOM_SIZE, ROOM_SIZE, 0), (0, ROOM_SIZE, 0)]
        walls = []
        for i, corner in enumerate(corners):
            bpy.context.scene.cursor.location = corner
            bpy.ops.bim.add_occurrence()
            obj = bpy.context.active_object
            props.length = ROOM_SIZE
            bpy.ops.bim.change_layer_length(length=ROOM_SIZE)
            obj.matrix_world = mathutils.Matrix.Translation(corner) @ mathutils.Matrix.Rotation(i * math.pi / 2, 4, "Z")
            bpy.context.view_layer.update()
            tool.Model.recalculate_walls([obj])
            walls.append(obj)
        bpy.ops.bim.create_wall_fillet(
            wall_a_id=tool.Ifc.get_entity(walls[3]).id(),
            wall_b_id=tool.Ifc.get_entity(walls[0]).id(),
            radius=FILLET_RADIUS,
        )
        for obj in bpy.data.objects:
            element = tool.Ifc.get_entity(obj)
            obj.select_set(bool(element and element.is_a("IfcWall")))

    def test_the_room_interior_follows_a_rounded_wall_corner(self):
        self.add_room_with_rounded_corner()

        union = subject.get_union_shape_from_selected_objects()

        assert len(union.interiors) == 1
        interior = shapely.Polygon(union.interiors[0])
        assert interior.contains(shapely.Point(ROOM_SIZE / 2, ROOM_SIZE / 2))
        assert interior.contains(shapely.Point(1.2, 1.2))
        assert not interior.contains(shapely.Point(0.3, 0.3))

    def test_a_full_height_opening_does_not_open_the_room(self):
        self.add_room_with_rounded_corner()
        bpy.ops.mesh.primitive_cube_add(size=1, location=(6, 0.05, 1.5))
        opening = bpy.context.active_object
        opening.scale = (1, 1, 4)
        wall = bpy.data.objects["IfcWall/Wall"]
        for obj in bpy.data.objects:
            obj.select_set(obj in (opening, wall))
        bpy.ops.bim.add_opening()
        assert tool.Ifc.get_entity(wall).HasOpenings
        for obj in bpy.data.objects:
            element = tool.Ifc.get_entity(obj)
            obj.select_set(bool(element and element.is_a("IfcWall")))

        union = subject.get_union_shape_from_selected_objects()

        assert len(union.interiors) == 1
