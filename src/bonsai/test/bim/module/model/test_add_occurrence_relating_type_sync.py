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

"""Regression test for AddOccurrence._execute's relating_type_id guard.

``AuthoringData.data["relating_type_id"]`` is a list of 3-tuples
``(id, name, description)``, built by ``AuthoringData.relating_type_id()``.
The guard in ``AddOccurrence._execute`` used to test
``str(self.relating_type_id) in AuthoringData.data["relating_type_id"]``,
which compares a string against a list of tuples and can never be True.
The branch was dead: calling ``bim.add_occurrence`` with an explicit
``relating_type_id`` from a Python invocation (``from_invoke=True``) never
synced that id into ``props.relating_type_id``, leaving the UI state stale
even though the occurrence itself was still added with the right type.

This test drives ``_execute`` for real and stops it right after the guard
runs (by making the next IFC lookup raise a sentinel exception), so it
proves the sync actually happened rather than merely that nothing raised.
"""

from unittest import mock

import pytest

pytestmark = pytest.mark.model


@pytest.fixture(autouse=True)
def _require_real_bpy():
    import types as _types

    import bpy

    if not isinstance(bpy, _types.ModuleType) or hasattr(bpy, "_mock_name"):
        pytest.skip("requires real Blender (bpy is mocked or absent)")


class _StopAfterGuard(Exception):
    """Raised from the first IFC lookup after the guard, to cut _execute
    short and let the test inspect props without running object creation."""


def _run_add_occurrence(relating_type_id: str, from_invoke: bool, relating_type_id_data: list):
    """Drive ``AddOccurrence._execute`` against fakes/mocks up to and
    including the relating_type_id guard, then stop it deliberately.
    Returns the fake props so the test can assert on
    ``props.relating_type_id``."""
    import bonsai.bim.module.model.product as product

    props = mock.Mock()
    props.relating_type_id = "1"  # stale value, distinct from any id under test

    ifc_file = mock.Mock()
    ifc_file.by_id.side_effect = _StopAfterGuard

    op = mock.Mock()
    op.relating_type_id = relating_type_id
    op.from_invoke = from_invoke

    context = mock.Mock()
    context.selected_objects = []

    with (
        mock.patch.object(product.tool.Ifc, "get", return_value=ifc_file),
        mock.patch.object(product.tool.Model, "get_model_props", return_value=props),
        mock.patch.object(product.AuthoringData, "data", {"relating_type_id": relating_type_id_data}),
    ):
        with pytest.raises(_StopAfterGuard):
            product.AddOccurrence._execute(op, context)

    return props


def test_from_invoke_with_valid_id_syncs_props():
    """The common case the guard exists for: adding e.g. an IfcRoofType
    while a Slab Tool operator invoked it, where the clicked id IS present
    in the current relating_type_id enum. props must end up in sync."""
    props = _run_add_occurrence(
        relating_type_id="64",
        from_invoke=True,
        relating_type_id_data=[("64", "IfcWallType", "")],
    )

    assert props.relating_type_id == "64"


def test_from_invoke_with_id_absent_from_enum_leaves_props_untouched():
    """The clicked id genuinely isn't offered here (e.g. an IfcRoofType id
    while adding via a Slab Tool): props must stay as they were."""
    props = _run_add_occurrence(
        relating_type_id="999",
        from_invoke=True,
        relating_type_id_data=[("64", "IfcWallType", "")],
    )

    assert props.relating_type_id == "1"


def test_not_from_invoke_leaves_props_untouched():
    """The guard is explicitly gated on from_invoke; a non-invoke call must
    not sync props even when the id is valid."""
    props = _run_add_occurrence(
        relating_type_id="64",
        from_invoke=False,
        relating_type_id_data=[("64", "IfcWallType", "")],
    )

    assert props.relating_type_id == "1"
