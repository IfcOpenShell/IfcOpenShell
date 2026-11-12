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

"""Shared fixtures and factories for ``test/bim/module/model/`` gizmo and
decorator tests.

The boundary between Blender / IFC / Bonsai's ``tool.*`` layer is patched
identically across many model-test files (viewport-state, selection, IFC
entity lookup, modifier predicates, view-camera state). The ``patched_tool``
fixture below centralises that patch stack so each test names only the
boundary methods it cares about; everything else is left to production.

Factory helpers (``make_obj``, ``make_element``, ``make_context``,
``make_ifc_file``) replace near-identical local helpers that previously
lived in each file.

When to use these fixtures in a new test file:

- Adding a gizmo / decorator test that patches ``tool.Blender`` or
  ``tool.Ifc`` boundary methods? Request the ``patched_tool`` fixture
  as a test parameter and call it as a context-manager factory.
- Need a stub ``bpy.types.Object`` / ``ifcopenshell.entity_instance`` /
  ``poll()`` context / ``ifcopenshell.file``? Import the matching factory
  from this module rather than re-rolling locally.
- Need to reset module-level state (e.g. a decorator cache token) between
  tests? Define an ``@pytest.fixture(autouse=True)`` reset in the test
  file itself — these stay file-local because they target state specific
  to one decorator/module and globalising the reset would surprise
  unrelated tests.

Layout note: pure helpers (``make_*``) live alongside the fixture in this
file rather than a sibling ``test_utils.py``. pytest's documented role for
``conftest.py`` is fixtures, so this is a mild convention bend — kept here
because the helper count is small and the dependencies (``tool``, ``Mock``)
already need to be imported for the fixture itself. Split into a separate
module if the helper count grows past ~6 or any helper picks up its own
non-trivial dependencies."""

import contextlib
import types
from types import SimpleNamespace
from unittest.mock import MagicMock, Mock, patch

import bpy
import ifcopenshell
import pytest

from bonsai import tool


@pytest.fixture(autouse=True)
def _require_real_bpy():
    """Skip every test in this directory when ``bpy`` is mocked or absent.

    The model gizmo / decorator suite reaches into Blender's RNA layer
    (``bpy.types.Operator``, registered ``bl_idname`` lookups, ``Modifier``
    predicates) that ``Mock`` cannot impersonate, so a tool-lane run with a
    stubbed ``bpy`` would error rather than meaningfully exercise the
    contract. The autouse scope means new test files added under this
    directory inherit the gate without re-declaring it."""
    if not isinstance(bpy, types.ModuleType) or hasattr(bpy, "_mock_name"):
        pytest.skip("requires real Blender (bpy is mocked or absent)")


def make_obj(*, session_uid=None, selected=True, **attrs):
    """Mock a ``bpy.types.Object`` with attributes commonly read by gizmos.

    ``session_uid`` is set only when provided so tests that don't care about
    object identity (most poll() tests use ``object()`` sentinels) can use
    ``make_obj()`` without a spurious uid. ``selected`` wires ``select_get()``
    to return the given boolean. Extra attrs are set as plain attributes.

    A bare ``Mock()`` is required because ``Mock(spec=bpy.types.Object)``
    rejects ``select_get`` — Blender's C-registered methods aren't exposed
    to Python introspection."""
    obj = Mock()
    if session_uid is not None:
        obj.session_uid = session_uid
    obj.select_get.return_value = selected
    for name, value in attrs.items():
        setattr(obj, name, value)
    return obj


def make_element(step_id=None, *, ifc_class=None, **attrs):
    """Mock an ``ifcopenshell.entity_instance`` with the surfaces gizmos read.

    ``step_id`` populates ``element.id()``. ``ifc_class`` wires ``is_a(name)``
    to return True only when ``name == ifc_class``. Extra kwargs become plain
    attributes (e.g. ``HasOpenings=()``)."""
    element = Mock()
    if step_id is not None:
        element.id.return_value = step_id
    if ifc_class is not None:
        element.is_a.side_effect = lambda type_name: type_name == ifc_class
    for name, value in attrs.items():
        setattr(element, name, value)
    return element


def make_context(*, active=None, selected=(), scene=None):
    """``SimpleNamespace`` stub with the ``poll()`` reads tests exercise:
    ``active_object``, ``selected_objects``, and ``scene``. ``selected`` is
    materialised to a list so tests can iterate without re-walking a generator.
    ``scene`` defaults to an empty namespace so guards that walk
    ``context.scene.BIMPreviewProperties`` (via ``getattr(..., default=None)``)
    treat the preview as inactive — pass a custom namespace to activate."""
    return SimpleNamespace(
        active_object=active,
        selected_objects=list(selected),
        scene=scene if scene is not None else SimpleNamespace(),
    )


def make_ifc_file(elements_by_guid: dict | None = None) -> MagicMock:
    """Mock ``ifcopenshell.file`` with ``spec=`` so attribute typos surface as
    ``AttributeError`` instead of silently auto-creating a child mock.

    When ``elements_by_guid`` is given, ``by_guid`` is wired to look up the
    mapping and raise ``RuntimeError`` on a missing guid — same shape as the
    real ifcopenshell.file behaviour, so a test that depends on orphan handling
    sees an exception rather than a silent ``None``."""
    f = MagicMock(spec=ifcopenshell.file, name="ifc_file")
    if elements_by_guid is not None:

        def _by_guid(guid):
            try:
                return elements_by_guid[guid]
            except KeyError:
                raise RuntimeError(f"no entity with guid {guid}")

        f.by_guid.side_effect = _by_guid
    return f


@pytest.fixture
def patched_tool():
    """Context-manager factory for the ``tool.*`` boundary patches that nearly
    every gizmo / decorator test repeats. Use as::

        with patched_tool(viewport_gizmos=True, selected=[obj_a, obj_b],
                          modifier_predicates={"is_wall": True}):
            GizmoFoo.poll(context)

    Only the kwargs you pass are patched — anything left as ``None`` (or
    omitted) keeps production behaviour. Values can be:

    - ``viewport_gizmos`` / ``view_top_down`` / ``addon_prefs``: passed to
      ``return_value=`` of the corresponding patch.
    - ``selected``: wrapped in ``set(...)`` for ``get_selected_objects``
      (matches the production return type for ``poll()``-side reads).
    - ``selected_list``: as-is for ``get_selected_objects`` when order
      matters (some operators iterate it). Mutually exclusive with
      ``selected`` — if both are passed, ``selected`` wins and
      ``selected_list`` is ignored. Pass only one.
    - ``entity``: either a callable (used as ``side_effect``) or a single
      value (used as ``return_value``).
    - ``modifier_predicates``: dict ``{predicate_name: bool_or_callable}``.
      Callables are wired as ``side_effect``, bools as ``return_value``.
    - ``screen_up``: ``return_value`` for ``get_screen_up_world``.

    Patches close on context-manager exit via an ``ExitStack`` — no
    ``try/finally`` bookkeeping in the test body."""

    @contextlib.contextmanager
    def _factory(
        *,
        viewport_gizmos=None,
        addon_prefs=None,
        selected=None,
        selected_list=None,
        entity=None,
        modifier_predicates=None,
        view_top_down=None,
        screen_up=None,
    ):
        with contextlib.ExitStack() as stack:
            if viewport_gizmos is not None:
                stack.enter_context(
                    patch.object(tool.Blender, "are_viewport_gizmos_enabled", return_value=viewport_gizmos)
                )
            if addon_prefs is not None:
                stack.enter_context(patch.object(tool.Blender, "get_addon_preferences", return_value=addon_prefs))
            if selected is not None:
                stack.enter_context(patch.object(tool.Blender, "get_selected_objects", return_value=set(selected)))
            elif selected_list is not None:
                stack.enter_context(
                    patch.object(tool.Blender, "get_selected_objects", return_value=list(selected_list))
                )
            if entity is not None:
                if callable(entity):
                    stack.enter_context(patch.object(tool.Ifc, "get_entity", side_effect=entity))
                else:
                    stack.enter_context(patch.object(tool.Ifc, "get_entity", return_value=entity))
            if modifier_predicates:
                for name, value in modifier_predicates.items():
                    # Parametric feature-kind predicates live on tool.Parametric; the
                    # remaining cardinality / non-parametric predicates (is_array_child,
                    # is_slab, is_eligible_for_*) stay on tool.Blender.Modifier.
                    target = tool.Parametric if hasattr(tool.Parametric, name) else tool.Blender.Modifier
                    if callable(value):
                        stack.enter_context(patch.object(target, name, side_effect=value))
                    else:
                        stack.enter_context(patch.object(target, name, return_value=value))
            if view_top_down is not None:
                stack.enter_context(patch.object(tool.Blender, "is_view_top_down", return_value=view_top_down))
            if screen_up is not None:
                stack.enter_context(patch.object(tool.Blender, "get_screen_up_world", return_value=screen_up))
            yield

    return _factory
