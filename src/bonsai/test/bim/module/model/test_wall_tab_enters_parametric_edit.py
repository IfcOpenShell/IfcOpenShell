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

"""Pins TAB-key dispatch on a LAYER2 wall through ``Modifier.try_applying_edit_mode``.

Three behavioural legs of the TAB toggle:

* Fresh LAYER2 wall → enters parametric edit via ``bim.enable_editing_wall``.
* LAYER2 wall already in parametric edit → finishes (toggle close).
* Wall without ``IfcMaterialLayerSetUsage`` → dispatch returns False so the
  caller routes the TAB to item mode."""

import bpy
import ifcopenshell.api.material
import ifcopenshell.util.element
import pytest

import bonsai.tool as tool
from test.bim.bootstrap import NewFile

pytestmark = pytest.mark.model


def _add_layer2_wall_occurrence():
    """Create a single LAYER2 wall occurrence from the IFC4 Demo Template.

    Returns the (element, obj) pair, with the object selected and active so
    ``try_applying_edit_mode`` reads the same context the TAB-key operator
    chain would feed it."""
    tool.Project.get_project_props().template_file = "IFC4 Demo Template.ifc"
    bpy.ops.bim.create_project()
    ifc_file = tool.Ifc.get()
    wall_type = next(t for t in ifc_file.by_type("IfcWallType") if tool.Model.get_usage_type(t) == "LAYER2")
    bpy.ops.bim.add_occurrence(relating_type_id=wall_type.id())
    wall = ifc_file.by_type("IfcWall")[0]
    obj = tool.Ifc.get_object(wall)
    assert isinstance(obj, bpy.types.Object)
    tool.Blender.set_objects_selection(bpy.context, obj, (obj,))
    return wall, obj


class TestTabOnLayer2WallEntersParametricEdit(NewFile):
    def test_dispatch_enables_wall_edit(self):
        wall, obj = _add_layer2_wall_occurrence()
        assert tool.Parametric.is_wall(wall) is True
        assert obj.BIMWallProperties.is_editing is False

        result = tool.Blender.Modifier.try_applying_edit_mode(obj, wall)

        assert result is True
        assert obj.BIMWallProperties.is_editing is True


class TestTabOnLayer2WallAlreadyEditingFinishes(NewFile):
    def test_dispatch_finishes_wall_edit(self):
        wall, obj = _add_layer2_wall_occurrence()
        bpy.ops.bim.enable_editing_wall()
        assert obj.BIMWallProperties.is_editing is True

        result = tool.Blender.Modifier.try_applying_edit_mode(obj, wall)

        assert result is True
        assert obj.BIMWallProperties.is_editing is False


class TestTabOnNonLayer2WallReturnsFalse(NewFile):
    def test_dispatch_falls_through_for_wall_without_layer_set_usage(self):
        """A wall without ``IfcMaterialLayerSetUsage`` is not a parametric-edit
        target; the dispatch returns False so the caller routes the TAB to
        item mode."""
        wall, obj = _add_layer2_wall_occurrence()
        ifc_file = tool.Ifc.get()
        wall_type = ifcopenshell.util.element.get_type(wall)
        ifcopenshell.api.material.unassign_material(ifc_file, products=[wall, wall_type])
        assert tool.Parametric.is_wall(wall) is False
        assert obj.BIMWallProperties.is_editing is False

        result = tool.Blender.Modifier.try_applying_edit_mode(obj, wall)

        assert result is False
        assert obj.BIMWallProperties.is_editing is False
