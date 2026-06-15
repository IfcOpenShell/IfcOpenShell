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

"""Pins the contract that ``DumbWallJoiner.merge`` re-hosts openings from
the discarded wall to the survivor before the cascade delete tears down
``element2.HasOpenings`` and any filling that references them.

``edit_object_placement`` preserves the opening's world position when the
two walls have different placements — a ``PlacementRelTo`` swap alone
would shift the opening as the relative offset changes."""

from unittest.mock import MagicMock, Mock, patch

import numpy as np
import pytest

pytestmark = pytest.mark.wall


def _opening_rel(opening_id: int, placement_matrix: np.ndarray):
    """Build a stub ``IfcRelVoidsElement`` carrying an opening with a known
    placement. ``RelatingBuildingElement`` is settable so the test can
    observe the re-host."""
    opening = Mock(name=f"opening_{opening_id}")
    opening.id.return_value = opening_id
    opening.ObjectPlacement = Mock(name=f"opening_placement_{opening_id}")
    rel = Mock(name=f"voids_rel_{opening_id}")
    rel.RelatedOpeningElement = opening
    rel.RelatingBuildingElement = None
    return rel, opening, placement_matrix


def _merge_inputs(*, has_openings):
    """Stage the minimum wall1 + wall2 + element1 + element2 surface that
    ``DumbWallJoiner.merge`` reads. The reference lines and placements are
    rigged so the collinearity guard passes and execution reaches the
    opening-migration loop."""
    wall1 = Mock(name="wall1")
    wall2 = Mock(name="wall2")
    element1 = Mock(name="element1")
    element2 = Mock(name="element2")
    element1.ObjectPlacement = Mock(name="elem1_placement")
    element2.ObjectPlacement = Mock(name="elem2_placement")
    element1.ConnectedTo = []
    element1.ConnectedFrom = []
    element2.ConnectedTo = []
    element2.ConnectedFrom = []
    element2.HasOpenings = list(has_openings)
    return wall1, wall2, element1, element2


def _run_merge(wall1, wall2, element1, element2, opening_matrices, captured_edit_calls):
    """Invoke ``DumbWallJoiner().merge`` against the staged inputs with
    every heavy IFC / Blender side effect patched out. ``opening_matrices``
    maps an opening id to its captured world matrix; ``captured_edit_calls``
    is appended to whenever ``edit_object_placement`` fires."""
    from bonsai.bim.module.model.wall import DumbWallJoiner

    def fake_get_local_placement(placement):
        for rel in element2.HasOpenings:
            if rel.RelatedOpeningElement.ObjectPlacement is placement:
                return opening_matrices[rel.RelatedOpeningElement.id()]
        return np.eye(4)

    def fake_get_entity(obj):
        return {wall1: element1, wall2: element2}[obj]

    def fake_edit_object_placement(ifc_file, *, product, matrix, is_si, should_transform_children):
        captured_edit_calls.append(
            {
                "product": product,
                "matrix": matrix,
                "is_si": is_si,
                "should_transform_children": should_transform_children,
            }
        )

    p1 = np.array([0.0, 0.0])
    p2 = np.array([5.0, 0.0])
    p3 = np.array([5.0, 0.0])
    p4 = np.array([10.0, 0.0])

    with (
        patch("bonsai.bim.module.model.wall.tool.Ifc.is_moved", return_value=False),
        patch("bonsai.bim.module.model.wall.tool.Ifc.get_entity", side_effect=fake_get_entity),
        patch("bonsai.bim.module.model.wall.tool.Ifc.get", return_value=MagicMock(name="ifc_file")),
        patch(
            "bonsai.bim.module.model.wall.ifcopenshell.util.representation.get_reference_line",
            side_effect=lambda elem: (p1, p2) if elem is element1 else (p3, p4),
        ),
        patch(
            "bonsai.bim.module.model.wall.ifcopenshell.util.placement.get_local_placement",
            side_effect=fake_get_local_placement,
        ),
        patch(
            "bonsai.bim.module.model.wall.ifcopenshell.api.geometry.edit_object_placement",
            side_effect=fake_edit_object_placement,
        ),
        patch("bonsai.bim.module.model.wall.tool.Model.recreate_wall"),
        patch("bonsai.bim.module.model.wall.tool.Geometry.delete_ifc_object") as delete_ifc_object,
        patch("bonsai.bim.module.model.wall.DumbWallJoiner.set_axis"),
    ):
        DumbWallJoiner().merge(wall1, wall2)
        return delete_ifc_object


def test_merge_rehosts_each_opening_to_survivor():
    """Every void rel on the discarded wall is rebound to the survivor so
    the cascade delete doesn't take them down with element2."""
    matrix_a = np.eye(4)
    matrix_a[0, 3] = 1.0
    matrix_b = np.eye(4)
    matrix_b[0, 3] = 3.0
    rel_a, opening_a, _ = _opening_rel(opening_id=101, placement_matrix=matrix_a)
    rel_b, opening_b, _ = _opening_rel(opening_id=102, placement_matrix=matrix_b)
    wall1, wall2, element1, element2 = _merge_inputs(has_openings=[rel_a, rel_b])

    _run_merge(
        wall1,
        wall2,
        element1,
        element2,
        opening_matrices={101: matrix_a, 102: matrix_b},
        captured_edit_calls=[],
    )

    assert rel_a.RelatingBuildingElement is element1
    assert rel_b.RelatingBuildingElement is element1


def test_merge_preserves_opening_world_placement():
    """``edit_object_placement`` re-applies the opening's pre-merge world
    matrix so the void doesn't drift when the two walls have different
    placements — the regression a ``PlacementRelTo`` swap alone would
    fail."""
    matrix = np.eye(4)
    matrix[:3, 3] = (2.5, 0.0, 0.0)
    rel, opening, _ = _opening_rel(opening_id=42, placement_matrix=matrix)
    wall1, wall2, element1, element2 = _merge_inputs(has_openings=[rel])
    captured: list[dict] = []

    _run_merge(
        wall1,
        wall2,
        element1,
        element2,
        opening_matrices={42: matrix},
        captured_edit_calls=captured,
    )

    edit_calls_for_opening = [call for call in captured if call["product"] is opening]
    assert len(edit_calls_for_opening) == 1
    np.testing.assert_allclose(edit_calls_for_opening[0]["matrix"], matrix, atol=1e-9)
    assert edit_calls_for_opening[0]["should_transform_children"] is False


def test_merge_rehosts_before_delete():
    """Order matters: ``delete_ifc_object`` cascades through
    ``element2.HasOpenings`` and would destroy the void if it ran before
    the re-host. Assert the survivor was rebound before delete fires."""
    matrix = np.eye(4)
    rel, opening, _ = _opening_rel(opening_id=7, placement_matrix=matrix)
    wall1, wall2, element1, element2 = _merge_inputs(has_openings=[rel])

    delete_ifc_object = _run_merge(
        wall1,
        wall2,
        element1,
        element2,
        opening_matrices={7: matrix},
        captured_edit_calls=[],
    )

    assert rel.RelatingBuildingElement is element1
    delete_ifc_object.assert_called_once_with(wall2)


def test_merge_skips_non_path_connection_rels():
    """``ConnectedTo`` / ``ConnectedFrom`` carry both
    ``IfcRelConnectsPathElements`` (wall-wall joins) AND
    ``IfcRelConnectsElements`` (slab underside clips). Only the path rels
    expose ``RelatingConnectionType`` / ``RelatedConnectionType``;
    accessing those attributes on an element rel raises ``AttributeError``.
    The migration loop must filter on the rel class so a wall with a slab
    clip can still be merged."""
    from bonsai.bim.module.model.wall import DumbWallJoiner

    wall1, wall2, element1, element2 = _merge_inputs(has_openings=[])

    path_rel = Mock(name="path_rel")
    path_rel.is_a = lambda c: c == "IfcRelConnectsPathElements"
    path_rel.RelatingElement = Mock(name="rel_relating")
    path_rel.RelatedElement = Mock(name="rel_related")
    path_rel.RelatingConnectionType = "ATSTART"
    path_rel.RelatedConnectionType = "ATEND"

    slab_rel = Mock(name="slab_rel")
    slab_rel.is_a = lambda c: c == "IfcRelConnectsElements"
    slab_rel.Description = "TOP"
    # ``RelatedConnectionType`` is what the merge loop reads from
    # ``ConnectedFrom``; the real ``IfcRelConnectsElements`` schema has
    # no such attribute, so wire the stub to raise like ifcopenshell does.
    type(slab_rel).RelatedConnectionType = property(
        lambda self: (_ for _ in ()).throw(AttributeError("RelatedConnectionType"))
    )
    type(slab_rel).RelatingConnectionType = property(
        lambda self: (_ for _ in ()).throw(AttributeError("RelatingConnectionType"))
    )
    element2.ConnectedFrom = [slab_rel, path_rel]

    captured_disconnects = []
    captured_connects = []

    def fake_disconnect_path(*args, **kwargs):
        captured_disconnects.append(kwargs)

    def fake_connect_path(*args, **kwargs):
        captured_connects.append(kwargs)

    p1 = np.array([0.0, 0.0])
    p2 = np.array([5.0, 0.0])
    p3 = np.array([5.0, 0.0])
    p4 = np.array([10.0, 0.0])

    def fake_get_entity(obj):
        return {wall1: element1, wall2: element2}[obj]

    with (
        patch("bonsai.bim.module.model.wall.tool.Ifc.is_moved", return_value=False),
        patch("bonsai.bim.module.model.wall.tool.Ifc.get_entity", side_effect=fake_get_entity),
        patch("bonsai.bim.module.model.wall.tool.Ifc.get", return_value=MagicMock(name="ifc_file")),
        patch(
            "bonsai.bim.module.model.wall.ifcopenshell.util.representation.get_reference_line",
            side_effect=lambda elem: (p1, p2) if elem is element1 else (p3, p4),
        ),
        patch(
            "bonsai.bim.module.model.wall.ifcopenshell.util.placement.get_local_placement",
            return_value=np.eye(4),
        ),
        patch(
            "bonsai.bim.module.model.wall.ifcopenshell.api.geometry.disconnect_path",
            side_effect=fake_disconnect_path,
        ),
        patch(
            "bonsai.bim.module.model.wall.ifcopenshell.api.geometry.connect_path",
            side_effect=fake_connect_path,
        ),
        patch("bonsai.bim.module.model.wall.tool.Model.recreate_wall"),
        patch("bonsai.bim.module.model.wall.tool.Geometry.delete_ifc_object"),
        patch("bonsai.bim.module.model.wall.DumbWallJoiner.set_axis"),
    ):
        # The bug pre-fix: the slab rel's ``RelatedConnectionType`` access
        # raised AttributeError and crashed merge. With the filter, this
        # call must complete cleanly.
        DumbWallJoiner().merge(wall1, wall2)

    assert len(captured_disconnects) == 1
    assert len(captured_connects) == 1
    assert captured_disconnects[0]["connection_type"] == "ATEND"
