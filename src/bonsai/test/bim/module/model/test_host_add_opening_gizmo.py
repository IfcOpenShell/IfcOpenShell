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

"""Poll + positioning tests for ``GizmoHostAddOpening``.

The gizmo dispatches on element type: walls keep the existing axis-projection
math, while LAYER3 hosts (slabs, roofs) use a world-Z face bias derived from
the void object's elevation. Each branch is exercised independently with
mocks so the per-type contract is pinned without launching a full Blender
modelling session."""

import contextlib
from types import SimpleNamespace
from unittest.mock import patch

import bpy
import pytest
from mathutils import Matrix, Vector

import bonsai.tool as tool
from test.bim.bootstrap import NewFile
from test.bim.module.model.conftest import make_context

pytestmark = pytest.mark.model


# ---------------------------------------------------------------------------
# poll() — entry gate per host type and per co-selection shape
# ---------------------------------------------------------------------------


_IFC_CLASS_BY_KIND = {
    "wall": "IfcWall",
    "slab": "IfcSlab",
    "roof": "IfcRoof",
    "plain": "IfcDiscreteAccessory",
    "door": "IfcDoor",
    "window": "IfcWindow",
    "opening": "IfcOpeningElement",
    "covering": "IfcCovering",
}


class _FakeIfcEntity:
    """Minimal stand-in for an ``ifcopenshell.entity_instance`` in poll tests.

    Mirrors ``ifcopenshell.entity_instance.is_a``'s two call shapes:
    ``is_a("Foo")`` returns True when the entity's class is ``Foo``, and
    ``is_a()`` returns the class name as a string. ``HasOpenings`` is
    optional so the poll's ``hasattr`` guard branch is reachable."""

    def __init__(self, ifc_class: str, has_openings: bool = True):
        self._ifc_class = ifc_class
        if has_openings:
            self.HasOpenings = ()

    def is_a(self, type_name: str | None = None):
        if type_name is None:
            return self._ifc_class
        return self._ifc_class == type_name


def _build_poll_callbacks(selected, active_kind, other_kind):
    """Build the ``(get_entity, is_path_connectable_wall)`` side-effect
    callables that simulate one poll() invocation. ``active_kind`` /
    ``other_kind`` accept ``"wall"``, ``"slab"``, ``"roof"``, ``"plain"``
    (non-host IFC element), ``"mesh"`` (no IFC entity), or ``None``
    (object outside the selection set).

    Wall recognition goes through ``tool.Parametric.is_path_connectable_wall``
    so fillet-corner walls (which have no LAYER2 usage) also surface the
    add-opening icon; slab/roof use ``is_a`` on the fake entity so the
    broadened class-based predicate is exercised."""
    sentinels = {kind: _FakeIfcEntity(_IFC_CLASS_BY_KIND[kind]) for kind in _IFC_CLASS_BY_KIND}
    # The "plain" sentinel lacks HasOpenings so the hasattr guard branch
    # is reachable from the corresponding poll test.
    sentinels["plain"] = _FakeIfcEntity(_IFC_CLASS_BY_KIND["plain"], has_openings=False)

    def entity_for(kind):
        if kind in (None, "mesh"):
            return None
        return sentinels[kind]

    entity_map = {}
    if len(selected) >= 1:
        entity_map[id(selected[0])] = entity_for(active_kind)
    if len(selected) >= 2:
        entity_map[id(selected[1])] = entity_for(other_kind)

    def get_entity(obj):
        return entity_map.get(id(obj))

    def is_path_connectable_wall(element):
        return element is sentinels["wall"]

    return get_entity, is_path_connectable_wall


def _run_poll(
    patched_tool, prefs_on=True, n_selected=2, active_in_selected=True, active_kind="wall", other_kind="mesh"
):
    from bonsai.bim.module.model.host_add_opening_gizmo import GizmoHostAddOpening

    selected = [object() for _ in range(n_selected)]
    active = selected[0] if (active_in_selected and selected) else object()
    get_entity, is_path_connectable_wall = _build_poll_callbacks(selected, active_kind, other_kind)

    with patched_tool(
        viewport_gizmos=prefs_on,
        selected=selected,
        entity=get_entity,
        modifier_predicates={"is_path_connectable_wall": is_path_connectable_wall},
    ):
        return GizmoHostAddOpening.poll(make_context(active=active, selected=selected))


@pytest.mark.parametrize("host_kind", ["wall", "slab", "roof"])
def test_poll_accepts_each_host_with_a_plain_mesh_void(host_kind, patched_tool):
    assert _run_poll(patched_tool, active_kind=host_kind, other_kind="mesh") is True


def test_poll_rejects_when_gizmo_toggle_off(patched_tool):
    assert _run_poll(patched_tool, prefs_on=False) is False


def test_poll_rejects_when_selection_count_is_not_two(patched_tool):
    assert _run_poll(patched_tool, n_selected=1) is False
    assert _run_poll(patched_tool, n_selected=3) is False


def test_poll_rejects_when_active_is_not_in_selection(patched_tool):
    assert _run_poll(patched_tool, active_in_selected=False) is False


def test_poll_rejects_when_active_has_no_ifc_entity(patched_tool):
    assert _run_poll(patched_tool, active_kind="mesh") is False


def test_poll_rejects_when_active_is_not_a_host(patched_tool):
    # "plain" sentinel is recognised as an IFC entity but is none of wall/slab/roof.
    assert _run_poll(patched_tool, active_kind="plain") is False


@pytest.mark.parametrize(
    "active_kind,other_kind",
    [
        ("wall", "wall"),  # wall-join gizmo owns this
        ("slab", "slab"),  # future slab-edit gizmo
        ("roof", "roof"),
        ("wall", "slab"),  # extend-vertically gizmo overlaps with this
        ("slab", "wall"),
        ("roof", "wall"),
    ],
)
def test_poll_rejects_host_host_pairs(active_kind, other_kind, patched_tool):
    """Host + host pairings must be suppressed so the icon never stacks with
    the wall-join / extend-vertical / future slab-edit gizmos."""
    assert _run_poll(patched_tool, active_kind=active_kind, other_kind=other_kind) is False


@pytest.mark.parametrize("filling_kind", ["door", "window", "opening", "mesh"])
def test_poll_accepts_host_with_supported_filling(filling_kind, patched_tool):
    """The apply-opening gizmo must activate when the secondary selection
    is a class the operator can dispatch on: ``IfcDoor`` / ``IfcWindow``
    (filled openings), ``IfcOpeningElement`` (existing opening reassigned
    to a new host), or a raw Blender mesh (converted to an opening)."""
    assert _run_poll(patched_tool, active_kind="wall", other_kind=filling_kind) is True


@pytest.mark.parametrize("non_filling_kind", ["covering", "plain"])
def test_poll_rejects_host_with_non_filling(non_filling_kind, patched_tool):
    """An IFC entity whose class the apply-opening operator can't dispatch
    on must keep the gizmo hidden — clicking it would otherwise dispatch
    the operator on a class whose geometry the opening generator can't
    derive, causing a deep traceback in the geometry kernel."""
    assert _run_poll(patched_tool, active_kind="wall", other_kind=non_filling_kind) is False


@pytest.mark.parametrize("filling_kind", ["door", "window", "opening", "mesh"])
def test_poll_accepts_filling_active_with_host_other(filling_kind, patched_tool):
    """The poll must be selection-order independent: the icon should appear
    whether the user clicked the host first or the filling first. The
    operator handles either order, so the gizmo should match."""
    assert _run_poll(patched_tool, active_kind=filling_kind, other_kind="wall") is True


@pytest.mark.parametrize("non_filling_kind", ["covering", "plain"])
def test_poll_rejects_non_filling_active_with_host_other(non_filling_kind, patched_tool):
    """The selection-order independence must not loosen the filling
    predicate — covering + wall stays rejected regardless of which is
    active."""
    assert _run_poll(patched_tool, active_kind=non_filling_kind, other_kind="wall") is False


def test_poll_rejects_active_host_without_has_openings(patched_tool):
    # Real-world equivalent: an IFC class that the active schema strips
    # ``HasOpenings`` from (e.g., a non-element subtype). The active sentinel
    # is set up as a connectable wall but with no HasOpenings attribute.
    from bonsai.bim.module.model.host_add_opening_gizmo import GizmoHostAddOpening

    selected = [object(), object()]
    active = selected[0]
    host_sentinel = object()  # No HasOpenings attribute
    other_sentinel = None

    with patched_tool(
        viewport_gizmos=True,
        selected=selected,
        entity=lambda o: host_sentinel if o is selected[0] else other_sentinel,
        modifier_predicates={"is_path_connectable_wall": lambda e: e is host_sentinel},
    ):
        assert GizmoHostAddOpening.poll(make_context(active=active, selected=selected)) is False


# ---------------------------------------------------------------------------
# position_gizmos() — branch dispatch and per-branch anchor math
# ---------------------------------------------------------------------------


def _run_position_wall_branch(patched_tool, *, other_translation=(0.5, 0.0, 0.0), top_down=True):
    """Drive the wall branch with stub IFC reads, returning the icon's
    matrix_basis translation."""
    from bonsai.bim.module.drawing import gizmos as gizmo_module
    from bonsai.bim.module.model import host_add_opening_gizmo as host_mod
    from bonsai.bim.module.model.host_add_opening_gizmo import GizmoHostAddOpening

    geom = {"anchor_x": 0.0, "length": 2.0, "height": 3.0, "offset": 0.0, "thickness": 0.2}
    wall_element = object()
    active = SimpleNamespace(matrix_world=Matrix.Identity(4))
    other = SimpleNamespace(matrix_world=Matrix.Translation(Vector(other_translation)))
    selected = [active, other]
    context = SimpleNamespace(active_object=active)
    icon = SimpleNamespace(matrix_basis=None, hide=True)
    self_stub = SimpleNamespace(add_opening_icon=icon)

    with contextlib.ExitStack() as stack:
        stack.enter_context(
            patched_tool(
                selected_list=selected,
                entity=wall_element,
                modifier_predicates={"is_path_connectable_wall": True},
                view_top_down=top_down,
                screen_up=Vector((0.0, 1.0, 0.0)),
            )
        )
        stack.enter_context(patch.object(host_mod, "_get_wall_geom_cached", return_value=geom))
        stack.enter_context(patch.object(host_mod, "_wall_camera_facing_icon_y", return_value=0.0))
        stack.enter_context(patch.object(gizmo_module, "get_billboard_rotation", return_value=Matrix.Identity(4)))
        stack.enter_context(
            patch.object(
                gizmo_module, "billboarded_at", side_effect=lambda pos, rot, scale=0.5: Matrix.Translation(pos)
            )
        )
        GizmoHostAddOpening.position_gizmos(self_stub, context)
    return icon.matrix_basis.translation


def test_wall_branch_drops_height_lift_in_top_down_view(patched_tool):
    """In plan view the wall-top Z lift must collapse to zero and the icon
    must instead offset along screen-up — otherwise the icon stacks on top
    of the wall outline and the user can't see it."""
    from bonsai.bim.module.drawing.gizmos import BaseParametricGizmoGroup

    pos = _run_position_wall_branch(patched_tool, top_down=True)
    assert pos.z == pytest.approx(0.0)
    assert pos.y == pytest.approx(BaseParametricGizmoGroup.SCREEN_STACK_OFFSET)


def _run_position_layer3_branch(
    patched_tool, *, host_world_z_range=(0.0, 0.2), other_z=1.0, other_xy=(0.7, 0.4), is_path_connectable_wall=False
):
    """Drive the LAYER3 (slab/roof) branch and return the icon translation.

    ``host_world_z_range`` sets the world-Z extents of the host's bounding box
    (the gizmo picks top vs bottom by comparing the void's Z to the box
    midpoint). ``is_path_connectable_wall`` keeps a single helper for both
    branches by flipping the dispatch predicate."""
    from bonsai.bim.module.drawing import gizmos as gizmo_module
    from bonsai.bim.module.model.host_add_opening_gizmo import GizmoHostAddOpening

    z_min, z_max = host_world_z_range
    # bound_box returns 8 corners in local space; we only need their world-Z
    # range to drive the branch, so fix XY at zero and vary Z.
    local_corners = [(0.0, 0.0, z_min), (0.0, 0.0, z_max)] * 4
    host_obj = SimpleNamespace(matrix_world=Matrix.Identity(4), bound_box=local_corners)
    other = SimpleNamespace(matrix_world=Matrix.Translation(Vector((other_xy[0], other_xy[1], other_z))))
    selected = [host_obj, other]
    context = SimpleNamespace(active_object=host_obj)
    icon = SimpleNamespace(matrix_basis=None, hide=True)
    self_stub = SimpleNamespace(add_opening_icon=icon)

    # Host identification in the gizmo branches on the entity's class, so
    # the sentinel must respond to ``is_a``. The non-host selection has no
    # IFC entity (mesh-like) and is accepted as a filling.
    host_element = _FakeIfcEntity("IfcSlab")
    entity_map = {id(host_obj): host_element, id(other): None}
    with contextlib.ExitStack() as stack:
        stack.enter_context(
            patched_tool(
                selected_list=selected,
                entity=lambda o: entity_map.get(id(o)),
                modifier_predicates={"is_path_connectable_wall": is_path_connectable_wall},
            )
        )
        stack.enter_context(patch.object(gizmo_module, "get_billboard_rotation", return_value=Matrix.Identity(4)))
        stack.enter_context(
            patch.object(
                gizmo_module, "billboarded_at", side_effect=lambda pos, rot, scale=0.5: Matrix.Translation(pos)
            )
        )
        GizmoHostAddOpening.position_gizmos(self_stub, context)
    return icon.matrix_basis.translation


@pytest.mark.parametrize("other_z", [1.0, 0.1, -1.0])
def test_layer3_branch_always_parks_above_top_face(patched_tool, other_z):
    """Icon parks above the host's top face regardless of the void's Z —
    predictable height every time. Void's XY is preserved so clicking the
    icon dispatches the operator at the intended XY position."""
    from bonsai.bim.module.drawing.gizmos import BaseParametricGizmoGroup

    pos = _run_position_layer3_branch(patched_tool, host_world_z_range=(0.0, 0.2), other_z=other_z, other_xy=(0.7, 0.4))
    assert pos.x == pytest.approx(0.7)
    assert pos.y == pytest.approx(0.4)
    assert pos.z == pytest.approx(0.2 + BaseParametricGizmoGroup.ICON_Z_OFFSET)


def test_position_gizmos_identifies_host_by_class_when_selected_second(patched_tool):
    """Host role in ``position_gizmos`` is resolved by IFC class, not by
    active-object position — so a slab clicked SECOND (filling first,
    host active or not) still anchors the icon correctly on the slab.
    This pins the selection-order independence of the positioner (the
    poll's independence is covered separately by the poll parametrize)."""
    from bonsai.bim.module.drawing import gizmos as gizmo_module
    from bonsai.bim.module.model.host_add_opening_gizmo import GizmoHostAddOpening

    other = SimpleNamespace(matrix_world=Matrix.Translation(Vector((0.7, 0.4, 1.0))))
    host_obj = SimpleNamespace(matrix_world=Matrix.Identity(4), bound_box=[(0.0, 0.0, 0.0), (0.0, 0.0, 0.2)] * 4)
    # Host at index 1; the filling (no IFC entity) sits at index 0 as active.
    selected = [other, host_obj]
    context = SimpleNamespace(active_object=other)
    icon = SimpleNamespace(matrix_basis=None, hide=True)
    self_stub = SimpleNamespace(add_opening_icon=icon)

    entity_map = {id(host_obj): _FakeIfcEntity("IfcSlab"), id(other): None}
    with contextlib.ExitStack() as stack:
        stack.enter_context(
            patched_tool(
                selected_list=selected,
                entity=lambda o: entity_map.get(id(o)),
                modifier_predicates={"is_path_connectable_wall": False},
            )
        )
        stack.enter_context(patch.object(gizmo_module, "get_billboard_rotation", return_value=Matrix.Identity(4)))
        stack.enter_context(
            patch.object(
                gizmo_module, "billboarded_at", side_effect=lambda pos, rot, scale=0.5: Matrix.Translation(pos)
            )
        )
        GizmoHostAddOpening.position_gizmos(self_stub, context)

    # Icon anchors on the host's top face (slab bound_box top-Z = 0.2) at
    # the void's XY — same result as when the host was at index 0.
    from bonsai.bim.module.drawing.gizmos import BaseParametricGizmoGroup

    pos = icon.matrix_basis.translation
    assert pos.x == pytest.approx(0.7)
    assert pos.y == pytest.approx(0.4)
    assert pos.z == pytest.approx(0.2 + BaseParametricGizmoGroup.ICON_Z_OFFSET)


# ---------------------------------------------------------------------------
# is_supported_host() — predicate totality
# ---------------------------------------------------------------------------


def test_is_supported_host_returns_false_for_none():
    """Total predicate: ``None`` short-circuits to False without raising."""
    from bonsai.bim.module.model.host_add_opening_gizmo import is_supported_host

    assert is_supported_host(None) is False


def test_is_supported_host_accepts_bare_ifc_slab():
    """The slab branch is class-based — any ``IfcSlab`` qualifies, even
    without LAYER3 parametric usage. The positioner reads ``obj.bound_box``,
    which works for both parametric and imported geometry."""
    from bonsai.bim.module.model.host_add_opening_gizmo import is_supported_host

    assert is_supported_host(_FakeIfcEntity("IfcSlab")) is True


def test_is_supported_host_accepts_bare_ifc_roof():
    """The roof branch is class-based, not pset-based — a bare ``IfcRoof``
    imported from another IFC tool qualifies even without the Bonsai
    BBIM_Roof parametric marker that ``tool.Parametric.is_roof``
    would require."""
    from bonsai.bim.module.model.host_add_opening_gizmo import is_supported_host

    assert is_supported_host(_FakeIfcEntity("IfcRoof")) is True


def test_is_supported_host_rejects_non_host_ifc_class():
    """Non-host IFC classes are filtered — covers ``IfcCovering`` (which has
    HasOpenings but is not a wall/slab/roof) and prevents the gizmo from
    surfacing on arbitrary building elements."""
    from bonsai.bim.module.model.host_add_opening_gizmo import is_supported_host

    assert is_supported_host(_FakeIfcEntity("IfcCovering")) is False
    assert is_supported_host(_FakeIfcEntity("IfcDiscreteAccessory")) is False


# ---------------------------------------------------------------------------
# End-to-end smoke: gizmo's target operator handles host + mesh-void selection
# ---------------------------------------------------------------------------
#
# The gizmo binds ``bim.add_opening`` via ``setup_icon_gizmo`` — clicking the
# icon dispatches that operator with the current selection set. The operator
# has its own target/opening detection that swaps based on which selected
# object carries an IFC entity. This smoke test pins that handoff: with a
# host as the active object and a non-IFC mesh as the "void", the operator
# creates an ``IfcOpeningElement`` linked to the host via the standard
# ``HasOpenings`` inverse.


class TestAddOpeningIntegrationOnSlab(NewFile):
    def test_creates_opening_when_slab_is_active_with_mesh_void(self):
        tool.Project.get_project_props().template_file = "IFC4 Demo Template.ifc"
        bpy.ops.bim.create_project()
        ifc_file = tool.Ifc.get()
        slab_type = ifc_file.by_type("IfcSlabType")[0]
        bpy.ops.bim.add_occurrence(relating_type_id=slab_type.id())
        slab = ifc_file.by_type("IfcSlab")[0]
        slab_obj = tool.Ifc.get_object(slab)
        assert isinstance(slab_obj, bpy.types.Object)
        assert len(slab.HasOpenings) == 0

        void_obj = bpy.data.objects.new("VoidMesh", bpy.data.meshes.new("VoidMesh"))
        bpy.context.scene.collection.objects.link(void_obj)
        void_obj.matrix_world = void_obj.matrix_world.copy()
        void_obj.matrix_world.translation = (
            slab_obj.matrix_world.translation.x,
            slab_obj.matrix_world.translation.y,
            slab_obj.matrix_world.translation.z + 1.0,
        )

        tool.Blender.set_objects_selection(bpy.context, slab_obj, (slab_obj, void_obj))
        bpy.ops.bim.add_opening()

        assert len(slab.HasOpenings) == 1
        opening = slab.HasOpenings[0].RelatedOpeningElement
        assert opening.is_a("IfcOpeningElement")


class TestAddOpeningPollOnForeignAuthoredSlab(NewFile):
    def test_poll_resolves_true_for_slab_without_layer3_usage(self):
        """An ``IfcSlab`` loaded from a non-Bonsai IFC carries no
        ``IfcMaterialLayerSetUsage``, so ``tool.Blender.Modifier.is_slab``
        rejects it — yet the gizmo's widened predicate accepts any
        ``IfcSlab`` because the positioner only reads the bound box.
        This pins the bare-class branch through the full ``poll`` path
        with real bpy + ifcopenshell state."""
        import ifcopenshell.api.material

        from bonsai.bim.module.model.host_add_opening_gizmo import (
            GizmoHostAddOpening,
            is_supported_host,
        )

        tool.Project.get_project_props().template_file = "IFC4 Demo Template.ifc"
        bpy.ops.bim.create_project()
        ifc_file = tool.Ifc.get()
        slab_type = ifc_file.by_type("IfcSlabType")[0]
        bpy.ops.bim.add_occurrence(relating_type_id=slab_type.id())
        slab = ifc_file.by_type("IfcSlab")[0]
        slab_obj = tool.Ifc.get_object(slab)
        assert isinstance(slab_obj, bpy.types.Object)

        # Strip every material association so the slab has no direct
        # LayerSetUsage and nothing to inherit from the type. The slab is
        # now a foreign-authored IFC class in everything but provenance.
        ifcopenshell.api.material.unassign_material(ifc_file, products=[slab, slab_type])
        assert tool.Blender.Modifier.is_slab(slab) is False
        assert is_supported_host(slab) is True

        void_obj = bpy.data.objects.new("VoidMesh", bpy.data.meshes.new("VoidMesh"))
        bpy.context.scene.collection.objects.link(void_obj)
        void_obj.matrix_world = void_obj.matrix_world.copy()
        void_obj.matrix_world.translation = (
            slab_obj.matrix_world.translation.x,
            slab_obj.matrix_world.translation.y,
            slab_obj.matrix_world.translation.z + 1.0,
        )

        tool.Blender.set_objects_selection(bpy.context, slab_obj, (slab_obj, void_obj))
        assert GizmoHostAddOpening.poll(bpy.context) is True


class TestAddOpeningPollOnForeignAuthoredRoof(NewFile):
    def test_poll_resolves_true_for_roof_without_bbim_pset(self):
        """A mesh-bodied ``IfcRoof`` promoted from a raw Blender mesh
        carries no ``BBIM_Roof`` pset, so ``tool.Parametric.is_roof``
        rejects it — yet the gizmo's widened predicate accepts any
        ``IfcRoof`` because the positioner only reads the bound box. This
        fixture mirrors how a foreign IFC roof loads (geometry + IFC
        identity, no parametric markers)."""
        from bonsai.bim.module.model.host_add_opening_gizmo import (
            GizmoHostAddOpening,
            is_supported_host,
        )

        tool.Project.get_project_props().template_file = "IFC4 Demo Template.ifc"
        bpy.ops.bim.create_project()

        bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))
        roof_obj = bpy.context.active_object
        assert roof_obj is not None
        tool.Root.get_root_props().ifc_product = "IfcElement"
        bpy.ops.bim.assign_class(ifc_class="IfcRoof")
        roof = tool.Ifc.get_entity(roof_obj)
        assert roof is not None and roof.is_a("IfcRoof")
        assert tool.Parametric.is_roof(roof) is False
        assert is_supported_host(roof) is True

        void_obj = bpy.data.objects.new("VoidMesh", bpy.data.meshes.new("VoidMesh"))
        bpy.context.scene.collection.objects.link(void_obj)
        void_obj.matrix_world = void_obj.matrix_world.copy()
        void_obj.matrix_world.translation = (
            roof_obj.matrix_world.translation.x,
            roof_obj.matrix_world.translation.y,
            roof_obj.matrix_world.translation.z + 1.0,
        )

        tool.Blender.set_objects_selection(bpy.context, roof_obj, (roof_obj, void_obj))
        assert GizmoHostAddOpening.poll(bpy.context) is True
