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

import bpy
import ifcopenshell.api.drawing
import ifcopenshell.guid

import bonsai.tool as tool
from test.bim.bootstrap import NewFile


def select_only(obj):
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


class TestRefreshLinkedAggregate(NewFile):
    def test_annotation_with_several_products_ends_up_with_the_refreshed_one(self):
        bpy.ops.bim.load_project(filepath=str(Path.cwd() / "test" / "files" / "linked-aggregates.ifc"))
        original_obj = bpy.data.objects["IfcWall/Wall_01"]
        select_only(original_obj)
        bpy.ops.bim.object_duplicate_move_linked_aggregate()
        ifc = tool.Ifc.get()
        annotation = ifc.createIfcAnnotation(GlobalId=ifcopenshell.guid.new(), Name="Tag")
        products = [tool.Ifc.get_entity(original_obj)]
        products += [ifc.createIfcWall(GlobalId=ifcopenshell.guid.new(), Name=f"Other {i}") for i in (1, 2)]
        for product in products:
            ifcopenshell.api.drawing.assign_product(ifc, relating_product=product, related_object=annotation)
        select_only(bpy.data.objects["IfcWall/Wall_01.001"])
        bpy.ops.bim.refresh_linked_aggregate()
        assert [r.RelatingProduct.Name for r in annotation.HasAssignments] == ["Wall_01"]
