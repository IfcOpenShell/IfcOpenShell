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
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Bonsai.  If not, see <http://www.gnu.org/licenses/>.
#
# This file was generated with the assistance of an AI coding tool.

"""Contract test for BIM_OT_assign_type's per-object class-compatibility
partition.

When the user multi-selects mixed classes (e.g. a wall + a door), the panel
picker filters the class dropdown by the active object's class only.
Historically the operator then fanned out across the whole selection without
re-checking each occurrence, producing schema-corrupt IFC files (IfcDoor
typed by IfcWallType). The partition added in this change must:

1. Assign the type only to compatible occurrences.
2. Surface skipped classes through ``self.report({'WARNING'}, ...)``.
3. ``return {'CANCELLED'}`` and emit an ERROR when nothing in the selection
   is compatible — no mutation must reach ``core.assign_type``.
"""

from unittest import mock

import pytest

pytestmark = pytest.mark.type


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

    previous = IfcStore.file
    IfcStore.file = ifcopenshell.file(schema="IFC4")
    try:
        yield IfcStore.file
    finally:
        IfcStore.file = previous


def _make_object(name, element):
    """Build a real bpy.types.Object linked to an IFC entity via
    tool.Ifc.link, so tool.Ifc.get_entity(obj) resolves correctly."""
    import bpy

    import bonsai.tool as tool

    obj = bpy.data.objects.new(name, None)
    tool.Ifc.link(element, obj)
    return obj


def _execute_assign(op, context):
    """Drive ``AssignType._execute`` directly. Bypasses the framework's
    transaction wrapping so a unit test can observe the partition without
    setting up the full Blender harness."""
    return op._execute(context)


@pytest.fixture
def neutralised_side_effects():
    """Patch the helpers ``AssignType._execute`` calls outside the partition
    logic (addon prefs, drawing context lookup, drawing target-view branch),
    so the test asserts only the partition / report / return-code contract."""
    with mock.patch("bonsai.bim.module.type.operator.tool.Blender.get_addon_preferences") as prefs:
        prefs.return_value = mock.Mock(occurrence_name_style="OCCURRENCE")
        yield


def _build_context_with_no_active_drawing():
    """Return a Mock ``context`` whose ``scene.DocProperties.active_drawing_id``
    is 0, skipping the drawing-target-view block in ``_execute``."""
    context = mock.Mock()
    context.scene.DocProperties.active_drawing_id = 0
    return context


def _fake_operator_with_report():
    """Build a Mock that satisfies the attribute reads ``AssignType._execute``
    makes on ``self`` (``relating_type``, ``related_object``, ``report``)."""
    op = mock.MagicMock()
    op.relating_type = 0
    op.related_object = ""
    op.report = mock.Mock()
    return op


def test_mixed_selection_assigns_only_compatible_objects(fresh_ifc, neutralised_side_effects):
    """Wall + door selected, IfcWallType picked: wall gets typed, door is
    skipped with a WARNING, and the operator returns success.

    ``core.assign_type`` is mocked: it would otherwise run the
    representation-switch and material plumbing on stub Blender objects.
    The contract under test is the partition / report logic, not the
    downstream representation pipeline."""
    import ifcopenshell.api.root

    from bonsai.bim.module.type.operator import AssignType

    wall_elem = ifcopenshell.api.root.create_entity(fresh_ifc, ifc_class="IfcWall")
    door_elem = ifcopenshell.api.root.create_entity(fresh_ifc, ifc_class="IfcDoor")
    wall_type = ifcopenshell.api.root.create_entity(fresh_ifc, ifc_class="IfcWallType")

    wall_obj = _make_object("Wall", wall_elem)
    door_obj = _make_object("Door", door_elem)

    op = _fake_operator_with_report()
    op.relating_type = wall_type.id()

    with mock.patch(
        "bonsai.bim.module.type.operator.tool.Blender.get_selected_objects", return_value=[wall_obj, door_obj]
    ), mock.patch("bonsai.bim.module.type.operator.core.assign_type") as mock_assign:
        result = AssignType._execute(op, _build_context_with_no_active_drawing())

    assert result != {"CANCELLED"}, "operator must succeed when at least one object is compatible"
    typed_elements = {call.kwargs["element"] for call in mock_assign.call_args_list}
    assert typed_elements == {
        wall_elem
    }, f"only the compatible wall element should reach core.assign_type, got {typed_elements}"

    warning_calls = [c for c in op.report.call_args_list if c.args[0] == {"WARNING"}]
    assert warning_calls, "skipped occurrence class must surface as a WARNING"
    assert any("IfcDoor" in c.args[1] for c in warning_calls)


def test_all_incompatible_selection_returns_cancelled_without_mutation(fresh_ifc, neutralised_side_effects):
    """Door alone selected, IfcWallType picked: nothing to assign. Operator
    must return CANCELLED, emit an ERROR, and never call core.assign_type."""
    import ifcopenshell.api.root
    import ifcopenshell.util.element

    from bonsai.bim.module.type.operator import AssignType

    door_elem = ifcopenshell.api.root.create_entity(fresh_ifc, ifc_class="IfcDoor")
    wall_type = ifcopenshell.api.root.create_entity(fresh_ifc, ifc_class="IfcWallType")
    door_obj = _make_object("Door", door_elem)

    op = _fake_operator_with_report()
    op.relating_type = wall_type.id()

    with mock.patch(
        "bonsai.bim.module.type.operator.tool.Blender.get_selected_objects", return_value=[door_obj]
    ), mock.patch("bonsai.bim.module.type.operator.core.assign_type") as mock_assign:
        result = AssignType._execute(op, _build_context_with_no_active_drawing())

    assert result == {"CANCELLED"}
    assert mock_assign.call_count == 0
    error_calls = [c for c in op.report.call_args_list if c.args[0] == {"ERROR"}]
    assert error_calls, "all-incompatible selection must surface as an ERROR"
    assert ifcopenshell.util.element.get_type(door_elem) is None
