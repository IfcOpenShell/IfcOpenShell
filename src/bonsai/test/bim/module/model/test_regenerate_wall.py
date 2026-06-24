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

"""Pins the branching contract of ``tool.Model.regenerate_wall``.

The body rebuild always runs (extrusion + openings); the slab re-clip only
runs when an ``IfcRelConnectsElements(TOP)`` rel survives. A wall without
either feature still completes without crashing."""

from unittest.mock import Mock, patch

import pytest

import bonsai.tool as tool

pytestmark = pytest.mark.model


def test_regenerate_wall_rebuilds_body_and_reclips_when_connected():
    """Wall with a TOP connection: body rebuilt first, then re-clipped."""
    element = Mock()
    obj = Mock()

    with patch("bonsai.tool.model.tool.Ifc.get_entity", return_value=element), patch.object(
        tool.Model, "recreate_wall"
    ) as recreate, patch.object(tool.Model, "has_underside_connection", return_value=True), patch(
        "bonsai.tool.model.bonsai.core.model.regenerate_wall_to_underside"
    ) as regen:
        tool.Model.regenerate_wall(obj)

    recreate.assert_called_once_with(element, obj)
    regen.assert_called_once()
    args, _ = regen.call_args
    assert args[3] == [obj]


def test_regenerate_wall_skips_reclip_when_no_top_rel():
    """Wall without a TOP connection: body rebuilt; re-clip skipped."""
    element = Mock()
    obj = Mock()

    with patch("bonsai.tool.model.tool.Ifc.get_entity", return_value=element), patch.object(
        tool.Model, "recreate_wall"
    ) as recreate, patch.object(tool.Model, "has_underside_connection", return_value=False), patch(
        "bonsai.tool.model.bonsai.core.model.regenerate_wall_to_underside"
    ) as regen:
        tool.Model.regenerate_wall(obj)

    recreate.assert_called_once_with(element, obj)
    regen.assert_not_called()


def test_regenerate_wall_noops_when_obj_has_no_ifc_entity():
    """Non-IFC objects (e.g. a freshly created Blender mesh before
    `tool.Ifc.run("root.create_entity")` runs) return None from get_entity;
    the helper must return without touching the body or any rels."""
    obj = Mock()

    with patch("bonsai.tool.model.tool.Ifc.get_entity", return_value=None), patch.object(
        tool.Model, "recreate_wall"
    ) as recreate, patch.object(tool.Model, "has_underside_connection") as has_top, patch(
        "bonsai.tool.model.bonsai.core.model.regenerate_wall_to_underside"
    ) as regen:
        tool.Model.regenerate_wall(obj)

    recreate.assert_not_called()
    has_top.assert_not_called()
    regen.assert_not_called()


def test_recreate_wall_noops_when_wall_has_no_layer_set():
    """``recreate_wall`` must short-circuit when
    ``regenerate_wall_representation`` returns ``None``. That API only knows
    how to rebuild ``IfcMaterialLayerSet`` walls; for walls without one it
    returns ``None``, and feeding ``None`` to ``switch_representation``
    crashes deep inside ``resolve_representation`` on ``.Items``."""
    element = Mock()
    obj = Mock()

    with patch("bonsai.tool.model.tool.Parametric.is_fillet_corner_wall", return_value=False), patch(
        "bonsai.tool.model.tool.Ifc.get", return_value=Mock()
    ), patch("bonsai.tool.model.ifcopenshell.api.geometry.regenerate_wall_representation", return_value=None), patch(
        "bonsai.tool.model.bonsai.core.geometry.switch_representation"
    ) as switch, patch.object(
        tool.Geometry, "record_object_materials"
    ) as record:
        tool.Model.recreate_wall(element, obj)

    switch.assert_not_called()
    record.assert_not_called()
