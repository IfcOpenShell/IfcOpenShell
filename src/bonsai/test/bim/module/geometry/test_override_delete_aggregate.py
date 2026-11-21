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

"""``bim.override_object_delete`` must not keep ``entity_instance`` handles to
aggregates across the deletion loop. When the aggregate is selected together
with its parts, the loop removes it, and a handle kept from before the loop
points at freed memory."""

from unittest import mock

import pytest

pytestmark = pytest.mark.geometry


@pytest.fixture(autouse=True)
def _require_real_bpy():
    import types as _types

    import bpy

    if not isinstance(bpy, _types.ModuleType) or hasattr(bpy, "_mock_name"):
        pytest.skip("requires real Blender (bpy is mocked or absent)")


def _add_object(name, ifc_class):
    import bpy

    bpy.ops.mesh.primitive_cube_add()
    obj = bpy.context.active_object
    obj.name = name
    bpy.ops.bim.assign_class(ifc_class=ifc_class)
    return obj


def test_deleting_an_aggregate_with_its_parts_never_touches_the_removed_aggregate():
    import bpy
    import ifcopenshell.api.aggregate
    import ifcopenshell.util.element

    import bonsai.tool as tool

    bpy.ops.wm.read_homefile(app_template="")
    bpy.ops.bim.create_project()
    stair = _add_object("Stair", "IfcStair")
    flight = _add_object("Flight", "IfcStairFlight")
    slab = _add_object("Landing", "IfcSlab")
    ifc_file = tool.Ifc.get()
    aggregate = tool.Ifc.get_entity(stair)
    parts = [tool.Ifc.get_entity(flight), tool.Ifc.get_entity(slab)]
    ifcopenshell.api.aggregate.assign_object(ifc_file, products=parts, relating_object=aggregate)
    aggregate_id = aggregate.id()

    bpy.ops.object.select_all(action="DESELECT")
    for obj in (stair, flight, slab):
        obj.select_set(True)

    with mock.patch.object(ifcopenshell.util.element, "get_parts", wraps=ifcopenshell.util.element.get_parts) as spy:
        assert bpy.ops.bim.override_object_delete(is_batch=False) == {"FINISHED"}

    assert tool.Ifc.get_entity_by_id(aggregate_id) is None
    assert not ifc_file.by_type("IfcStair")
    assert aggregate_id not in [call.args[0].id() for call in spy.call_args_list]
