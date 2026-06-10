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

"""Unit coverage for the ``_RailingEditMixin`` lifecycle overrides.

The generic ``PathPreservingEditMixin`` lifecycle is tested in
``test_parametric_lifecycle.py``. This file pins the **railing-specific
overrides** that subclass it:

- ``_RailingEditMixin._finish_one`` short-circuit: when the draft equals
  the stored pset, ``_update_pset`` and ``_update_modifier_ifc_data`` are
  skipped so an Enable → Finish-without-changes cycle creates no new
  ``IfcShapeRepresentation``.
- ``_RailingEditMixin._cancel_one`` short-circuit: same logic guards the
  expensive ``bonsai.core.geometry.switch_representation`` call (which
  re-tessellates the swept-disk solid) when nothing actually changed.
- ``_RailingEditMixin._cancel_one`` WALL_MOUNTED_HANDRAIL branch: when
  changes WERE made, the cancel reloads the IFC body via
  ``switch_representation`` instead of running ``update_modifier_bmesh``
  (which would leave the low-poly cylinder-segment preview on screen).
"""

from unittest import mock

import pytest

from test.bim.conftest import _FakePropsBase
from test.bim.conftest import make_lifecycle_obj as _make_obj

pytestmark = pytest.mark.model


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


class _FakeRailingProps(_FakePropsBase):
    """Stand-in for ``BIMRailingProperties`` — adds ``railing_type`` on top of
    the shared parametric-edit contract. Starts in ``is_editing=True`` because
    the railing-specific overrides under test only fire on Finish / Cancel,
    not on Enable."""

    def __init__(self, railing_type: str = "WALL_MOUNTED_HANDRAIL", general: dict | None = None):
        super().__init__(general=general if general is not None else {"railing_type": railing_type, "height": 1.0})
        self.railing_type = railing_type
        self.is_editing = True


@pytest.fixture
def patched_railing():
    """Patch the railing module's external references for unit testing.

    ``_RailingEditMixin`` calls ``tool.Model.get_modeling_bbim_pset_data``,
    ``tool.Ifc.get_entity``, ``ifcopenshell.util.representation.get_representation``,
    and ``bonsai.core.geometry.switch_representation`` — each looked up
    through the railing module's own bindings, so we patch them there.

    Uses ``mock.patch.object`` with a direct module reference rather than
    the dotted-string form: ``mock.patch("bonsai.bim.module.model.railing.bonsai")``
    needs ``pkgutil.resolve_name`` to traverse ``bonsai → bim → module → …``,
    which fails at the ``bonsai.bim`` step until that subpackage has been
    imported elsewhere. The direct-object form sidesteps the resolution.

    Returns a dict for tests to seed return values and assert call sites.
    """
    from bonsai.bim.module.model import railing

    with (
        mock.patch.object(railing, "tool") as mock_tool,
        mock.patch.object(railing, "ifcopenshell") as mock_ifc,
        mock.patch.object(railing, "bonsai") as mock_bonsai,
    ):
        # _resolve will be overridden on the test subclass below so the
        # parametric_lifecycle.tool patch isn't needed.
        mock_tool.Ifc.get_entity.return_value = mock.Mock(name="entity")
        yield {"tool": mock_tool, "ifcopenshell": mock_ifc, "bonsai": mock_bonsai}


def _railing_test_subclass(props):
    """Build a ``_RailingEditMixin`` subclass that bypasses ``_resolve``.

    The base ``_resolve`` reads ``tool.Ifc.get_entity`` from
    ``parametric_lifecycle.tool`` (a separate import from the railing
    module's ``tool``). Overriding it here keeps the test patches local
    to the railing module and the hook closures local to the test."""
    from bonsai.bim.module.model.railing import _RailingEditMixin

    test_element = mock.Mock(name="ifc_element")

    class _TestRailingMixin(_RailingEditMixin):
        pset_updates: mock.MagicMock = mock.MagicMock(name="_update_pset")
        ifc_data_updates: mock.MagicMock = mock.MagicMock(name="_update_modifier_ifc_data")
        bmesh_updates: mock.MagicMock = mock.MagicMock(name="_update_modifier_bmesh")

        @classmethod
        def _resolve(cls, obj):
            return test_element, props

        @classmethod
        def _update_pset(cls, element, data):
            cls.pset_updates(element, data)

        @classmethod
        def _update_modifier_ifc_data(cls, obj, context):
            cls.ifc_data_updates(obj, context)

        @classmethod
        def _update_modifier_bmesh(cls, obj, context):
            cls.bmesh_updates(obj, context)

        # The base _post_load_data JSON-serialises path_data; bypass that
        # here so the round-trip stays a plain dict and tests can compare
        # by reference / equality without re-parsing.
        @classmethod
        def _post_load_data(cls, data):
            return dict(data)

    return _TestRailingMixin, test_element


# ---------------------------------------------------------------------------
# _RailingEditMixin._finish_one
# ---------------------------------------------------------------------------


def test_finish_one_short_circuits_when_draft_matches_stored(patched_railing):
    """Enable → Finish without any property edit must NOT write to IFC.

    Without this, every "open Edit, click Validate immediately" cycle
    would create a fresh ``IfcShapeRepresentation``, pollute the file's
    representation list, and burn an undo entry — the user-visible
    regression that motivated the short-circuit.
    """
    stored = {"railing_type": "WALL_MOUNTED_HANDRAIL", "height": 1.0}
    props = _FakeRailingProps(general=dict(stored))
    obj = _make_obj(props)
    patched_railing["tool"].Model.get_modeling_bbim_pset_data.return_value = {
        "data_dict": {**stored, "path_data": {"verts": [], "edges": []}},
    }

    cls, _element = _railing_test_subclass(props)
    cls._finish_one(obj, mock.Mock(name="context"))

    assert props.is_editing is False, "is_editing must still flip even on no-op"
    cls.pset_updates.assert_not_called()
    cls.ifc_data_updates.assert_not_called()


def test_finish_one_writes_when_draft_differs(patched_railing):
    """The complement of the short-circuit: a real property change must
    flow through to ``_update_pset`` + ``_update_modifier_ifc_data``."""
    stored = {"railing_type": "WALL_MOUNTED_HANDRAIL", "height": 1.0}
    # Draft height differs: simulating a user edit.
    props = _FakeRailingProps(general={"railing_type": "WALL_MOUNTED_HANDRAIL", "height": 1.5})
    obj = _make_obj(props)
    patched_railing["tool"].Model.get_modeling_bbim_pset_data.return_value = {
        "data_dict": {**stored, "path_data": {"verts": [], "edges": []}},
    }

    cls, element = _railing_test_subclass(props)
    cls._finish_one(obj, mock.Mock(name="context"))

    assert props.is_editing is False
    cls.pset_updates.assert_called_once()
    # The pset must receive the DRAFT data, not the stored data — that's the
    # whole point of Finish committing the user's edits.
    written = cls.pset_updates.call_args[0][1]
    assert written["height"] == 1.5
    cls.ifc_data_updates.assert_called_once_with(obj, mock.ANY)


# ---------------------------------------------------------------------------
# _RailingEditMixin._cancel_one
# ---------------------------------------------------------------------------


def test_cancel_one_short_circuits_when_draft_matches_stored(patched_railing):
    """Cancel-without-changes is asymmetrically expensive without this guard:
    ``switch_representation`` re-tessellates the IfcSweptDiskSolid and is
    visibly slow on a long handrail. When nothing changed, the mesh on
    screen is still the committed IFC representation (the preview only
    builds on a property change) — skip the reload entirely.
    """
    stored = {"railing_type": "WALL_MOUNTED_HANDRAIL", "height": 1.0}
    props = _FakeRailingProps(general=dict(stored))
    obj = _make_obj(props)
    patched_railing["tool"].Model.get_modeling_bbim_pset_data.return_value = {
        "data_dict": {**stored, "path_data": {"verts": [], "edges": []}},
    }

    cls, _element = _railing_test_subclass(props)
    cls._cancel_one(obj, mock.Mock(name="context"))

    assert props.is_editing is False
    patched_railing["bonsai"].core.geometry.switch_representation.assert_not_called()
    cls.bmesh_updates.assert_not_called()


def test_cancel_one_wall_mounted_handrail_switches_representation(patched_railing):
    """Cancel after a real edit on a WALL_MOUNTED_HANDRAIL must reload the
    committed Body representation (high-poly, IFC-derived) rather than
    re-running the low-poly bmesh preview — that preview is a viewport-only
    approximation and would persist visibly after Cancel without this.
    """
    stored = {"railing_type": "WALL_MOUNTED_HANDRAIL", "height": 1.0}
    # Differs → not a no-op → cancel must take the real branch.
    props = _FakeRailingProps(
        railing_type="WALL_MOUNTED_HANDRAIL",
        general={"railing_type": "WALL_MOUNTED_HANDRAIL", "height": 1.5},
    )
    obj = _make_obj(props)
    patched_railing["tool"].Model.get_modeling_bbim_pset_data.return_value = {
        "data_dict": {**stored, "path_data": {"verts": [], "edges": []}},
    }
    body_repr = mock.Mock(name="body_representation")
    patched_railing["ifcopenshell"].util.representation.get_representation.return_value = body_repr

    cls, _element = _railing_test_subclass(props)
    cls._cancel_one(obj, mock.Mock(name="context"))

    assert props.is_editing is False
    # Must call switch_representation with the Body representation; must NOT
    # call _update_modifier_bmesh (that's the FRAMELESS branch).
    patched_railing["bonsai"].core.geometry.switch_representation.assert_called_once()
    kwargs = patched_railing["bonsai"].core.geometry.switch_representation.call_args.kwargs
    assert kwargs["obj"] is obj
    assert kwargs["representation"] is body_repr
    cls.bmesh_updates.assert_not_called()


def test_cancel_one_frameless_panel_runs_bmesh_preview(patched_railing):
    """FRAMELESS_PANEL's bmesh IS the canonical mesh — there's no IFC
    swept-disk solid to reload. Cancel must run the bmesh rebuild instead
    of switch_representation, which would no-op or worse."""
    stored = {"railing_type": "FRAMELESS_PANEL", "height": 1.0, "thickness": 0.05}
    props = _FakeRailingProps(
        railing_type="FRAMELESS_PANEL",
        general={"railing_type": "FRAMELESS_PANEL", "height": 1.0, "thickness": 0.08},
    )
    obj = _make_obj(props)
    patched_railing["tool"].Model.get_modeling_bbim_pset_data.return_value = {
        "data_dict": {**stored, "path_data": {"verts": [], "edges": []}},
    }

    cls, _element = _railing_test_subclass(props)
    cls._cancel_one(obj, mock.Mock(name="context"))

    assert props.is_editing is False
    cls.bmesh_updates.assert_called_once_with(obj, mock.ANY)
    patched_railing["bonsai"].core.geometry.switch_representation.assert_not_called()


# ---------------------------------------------------------------------------
# _get_railing_path_anchor: tests removed.
#
# The schematic-redesign branch replaced ``GizmoRailingEdition`` with
# ``GizmoRailingSchematic``, which anchors via the schematic frame rather
# than the polyline's first vertex. ``_get_railing_path_anchor`` was the
# helper for the old anchor strategy and has been deleted along with the
# old gizmo group. If schematic-mode gains a similar path-derived helper,
# new tests should land here.
# ---------------------------------------------------------------------------
