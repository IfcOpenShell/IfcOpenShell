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

"""Unit coverage for the ``_RailingEditMixin`` overrides and the lifecycle
behaviour railing inherits from ``PathPreservingEditMixin``.

The parent short-circuit (skip the IFC commit / viewport rebuild when the
draft is identical to the stored pset) lives in
``PathPreservingEditMixin``; the tests below verify railing's subclass
honours that contract by inheritance, then pin the railing-specific
viewport-restore dispatch:

- Finish / Cancel no-op short-circuit: inherited from the parent — verified
  here because railing was the original consumer that motivated the
  optimisation.
- ``_RailingEditMixin._restore_viewport_after_cancel`` dispatch: WALL_MOUNTED_HANDRAIL
  reloads the high-poly Body representation via ``switch_representation``;
  FRAMELESS_PANEL rebuilds the bmesh preview via
  ``update_railing_modifier_bmesh``. This is the per-type branch that used
  to live in ``_cancel_one`` and now lives in the viewport-restore hook the
  parent's ``_cancel_one`` calls.
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

    ``_RailingEditMixin`` and the parent lifecycle reach for
    ``tool.Model.get_modeling_bbim_pset_data``, ``tool.Ifc.get_entity``,
    ``ifcopenshell.util.representation.get_representation``,
    ``bonsai.core.geometry.switch_representation``, and the module-level
    ``update_railing_modifier_bmesh`` — each looked up through the railing
    module's own bindings, so we patch them there.

    ``parametric_lifecycle.tool`` is patched separately so the parent's
    ``_resolve`` and ``_cancel_one`` can read ``tool.Model.get_modeling_bbim_pset_data``
    without falling through to the real Blender bindings.

    Uses ``mock.patch.object`` with a direct module reference rather than
    the dotted-string form: ``mock.patch("bonsai.bim.module.model.railing.bonsai")``
    needs ``pkgutil.resolve_name`` to traverse ``bonsai → bim → module → …``,
    which fails at the ``bonsai.bim`` step until that subpackage has been
    imported elsewhere. The direct-object form sidesteps the resolution.

    Returns a dict for tests to seed return values and assert call sites.
    """
    from bonsai.bim import parametric_lifecycle
    from bonsai.bim.module.model import railing

    with (
        mock.patch.object(railing, "tool") as mock_tool,
        mock.patch.object(railing, "ifcopenshell") as mock_ifc,
        mock.patch.object(railing, "bonsai") as mock_bonsai,
        mock.patch.object(railing, "update_railing_modifier_bmesh") as mock_update_bmesh,
        mock.patch.object(parametric_lifecycle, "tool") as mock_pl_tool,
    ):
        # _resolve will be overridden on the test subclass below so the
        # parametric_lifecycle.tool patch isn't needed for that path, but the
        # parent's _cancel_one / _finish_one still call
        # tool.Model.get_modeling_bbim_pset_data and would otherwise miss.
        mock_tool.Ifc.get_entity.return_value = mock.Mock(name="entity")
        yield {
            "tool": mock_tool,
            "ifcopenshell": mock_ifc,
            "bonsai": mock_bonsai,
            "update_bmesh": mock_update_bmesh,
            "pl_tool": mock_pl_tool,
        }


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
        bmesh_updates: mock.MagicMock = mock.MagicMock(name="_restore_viewport_after_cancel")

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
        def _restore_viewport_after_cancel(cls, obj, context):
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

    Behaviour now inherited from ``PathPreservingEditMixin``; railing keeps
    the coverage as the original consumer of the contract.
    """
    stored = {"railing_type": "WALL_MOUNTED_HANDRAIL", "height": 1.0}
    props = _FakeRailingProps(general=dict(stored))
    obj = _make_obj(props)
    patched_railing["pl_tool"].Model.get_modeling_bbim_pset_data.return_value = {
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
    patched_railing["pl_tool"].Model.get_modeling_bbim_pset_data.return_value = {
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

    Behaviour now inherited from ``PathPreservingEditMixin``; railing keeps
    the coverage as the original consumer of the contract.
    """
    stored = {"railing_type": "WALL_MOUNTED_HANDRAIL", "height": 1.0}
    props = _FakeRailingProps(general=dict(stored))
    obj = _make_obj(props)
    patched_railing["pl_tool"].Model.get_modeling_bbim_pset_data.return_value = {
        "data_dict": {**stored, "path_data": {"verts": [], "edges": []}},
    }

    cls, _element = _railing_test_subclass(props)
    cls._cancel_one(obj, mock.Mock(name="context"))

    assert props.is_editing is False
    patched_railing["bonsai"].core.geometry.switch_representation.assert_not_called()
    patched_railing["update_bmesh"].assert_not_called()
    cls.bmesh_updates.assert_not_called()


# ---------------------------------------------------------------------------
# _RailingEditMixin._restore_viewport_after_cancel — per-type viewport-restore dispatch
#
# The parent's _cancel_one calls cls._restore_viewport_after_cancel whenever
# the draft differs from the stored pset. Railing's override branches on
# railing_type so WALL_MOUNTED_HANDRAIL reloads the high-poly Body
# representation rather than rebuilding the low-poly cylinder-segment preview.
# ---------------------------------------------------------------------------


def test_restore_viewport_wall_mounted_handrail_switches_representation(patched_railing):
    """WALL_MOUNTED_HANDRAIL restore must call ``switch_representation`` with
    the Body representation — the preview is viewport-only (low-poly cylinder)
    and would persist visibly without the reload."""
    from bonsai.bim.module.model.railing import _RailingEditMixin

    props = _FakeRailingProps(railing_type="WALL_MOUNTED_HANDRAIL")
    obj = _make_obj(props)
    patched_railing["tool"].Model.get_railing_props.return_value = props
    body_repr = mock.Mock(name="body_representation")
    patched_railing["ifcopenshell"].util.representation.get_representation.return_value = body_repr

    _RailingEditMixin._restore_viewport_after_cancel(obj, mock.Mock(name="context"))

    patched_railing["bonsai"].core.geometry.switch_representation.assert_called_once()
    kwargs = patched_railing["bonsai"].core.geometry.switch_representation.call_args.kwargs
    assert kwargs["obj"] is obj
    assert kwargs["representation"] is body_repr
    # Must NOT fall through to the FRAMELESS bmesh-rebuild path.
    patched_railing["update_bmesh"].assert_not_called()


def test_restore_viewport_frameless_panel_calls_module_bmesh_rebuild(patched_railing):
    """FRAMELESS_PANEL's bmesh IS the canonical mesh — there's no IFC
    swept-disk solid to reload. The restore must delegate to the module-level
    ``update_railing_modifier_bmesh`` rebuilder rather than swap representations."""
    from bonsai.bim.module.model.railing import _RailingEditMixin

    props = _FakeRailingProps(railing_type="FRAMELESS_PANEL")
    obj = _make_obj(props)
    patched_railing["tool"].Model.get_railing_props.return_value = props
    ctx = mock.Mock(name="context")

    _RailingEditMixin._restore_viewport_after_cancel(obj, ctx)

    patched_railing["update_bmesh"].assert_called_once_with(ctx)
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
