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

"""Contract tests for ``ReassignClass._execute``'s occurrence handling.

Reassigning the class of one occurrence that shares its type with siblings
must not redirect to the type (which would cascade the new class onto every
sibling, issue #2831). The type redirect is only valid when the user selected
every occurrence of that type, in which case reassigning the type once is
the sensible batch behavior."""

from unittest import mock

import pytest

pytestmark = pytest.mark.root


@pytest.fixture(autouse=True)
def _require_real_bpy():
    import types as _types

    import bpy

    if not isinstance(bpy, _types.ModuleType) or hasattr(bpy, "_mock_name"):
        pytest.skip("requires real Blender (bpy is mocked or absent)")


@pytest.fixture
def fresh_ifc():
    import ifcopenshell

    from bonsai.bim.ifc import IfcStore

    previous_file = IfcStore.file
    previous_schema = IfcStore.schema
    IfcStore.file = ifcopenshell.file(schema="IFC4")
    IfcStore.schema = None
    try:
        yield IfcStore.file
    finally:
        IfcStore.file = previous_file
        IfcStore.schema = previous_schema


def _make_object(name, element):
    """Build a real bpy.types.Object linked to an IFC entity via
    tool.Ifc.link, so tool.Ifc.get_entity(obj) resolves correctly."""
    import bpy

    import bonsai.tool as tool

    obj = bpy.data.objects.new(name, None)
    tool.Ifc.link(element, obj)
    return obj


def _make_root_props(ifc_product, ifc_class):
    return mock.Mock(
        ifc_product=ifc_product,
        ifc_class=ifc_class,
        ifc_predefined_type="",
        ifc_userdefined_type="",
    )


def _fake_operator():
    """Satisfy the attribute reads ``ReassignClass._execute`` makes on
    ``self`` (``obj``, ``file``, ``report``)."""
    op = mock.MagicMock()
    op.obj = ""
    op.report = mock.Mock()
    return op


def _run_reassign(selected_objects, ifc_class="IfcSlab"):
    from bonsai.bim.module.root.operator import ReassignClass

    op = _fake_operator()
    with mock.patch(
        "bonsai.bim.module.root.operator.tool.Blender.get_selected_objects", return_value=selected_objects
    ), mock.patch(
        "bonsai.bim.module.root.operator.tool.Root.get_root_props",
        return_value=_make_root_props("IfcElement", ifc_class),
    ), mock.patch(
        "bonsai.bim.module.root.operator.tool.Root.set_object_name"
    ), mock.patch(
        "bonsai.bim.module.root.operator.tool.Collector.assign"
    ):
        return ReassignClass._execute(op, mock.Mock())


def _typed_walls(ifc_file, count=3):
    import ifcopenshell.api.root
    import ifcopenshell.api.type

    wall_type = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcWallType")
    walls = [
        ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcWall", name=f"Wall{i + 1}") for i in range(count)
    ]
    ifcopenshell.api.type.assign_type(ifc_file, related_objects=walls, relating_type=wall_type)
    return wall_type, walls


def test_reassigning_one_occurrence_among_siblings_leaves_type_and_siblings_untouched(fresh_ifc):
    import ifcopenshell.util.element

    wall_type, walls = _typed_walls(fresh_ifc)
    objs = [_make_object(f"IfcWall/Wall{i + 1}", wall) for i, wall in enumerate(walls)]
    wall1_id = walls[0].id()

    result = _run_reassign([objs[0]])

    assert result == {"FINISHED"}
    slab = fresh_ifc.by_id(wall1_id)
    assert slab.is_a("IfcSlab")
    # reassigned occurrence is detached from the now-mismatched type
    assert ifcopenshell.util.element.get_type(slab) is None
    # shared type and sibling occurrences are untouched
    assert wall_type.is_a("IfcWallType")
    assert set(ifcopenshell.util.element.get_types(wall_type)) == {walls[1], walls[2]}
    assert walls[1].is_a("IfcWall") and walls[2].is_a("IfcWall")
    assert len(fresh_ifc.by_type("IfcSlabType")) == 0


def test_reassigning_all_occurrences_of_a_type_reassigns_the_type_once(fresh_ifc):
    import ifcopenshell.util.element

    wall_type, walls = _typed_walls(fresh_ifc)
    objs = [_make_object(f"IfcWall/Wall{i + 1}", wall) for i, wall in enumerate(walls)]
    wall_type_id = wall_type.id()

    result = _run_reassign(objs)

    assert result == {"FINISHED"}
    slab_type = fresh_ifc.by_id(wall_type_id)
    assert slab_type.is_a("IfcSlabType")
    occurrences = ifcopenshell.util.element.get_types(slab_type)
    assert len(occurrences) == 3
    assert all(o.is_a("IfcSlab") for o in occurrences)
    assert len(fresh_ifc.by_type("IfcWall")) == 0
    assert len(fresh_ifc.by_type("IfcWallType")) == 0
