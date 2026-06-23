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

"""Dispatch tests for ``core.connection.disconnect_rel``.

The dispatch is the single source of truth for per-kind cleanup shared by the
explicit ``bim.disconnect_elements`` operator and the implicit cascade in
``tool.Geometry.delete_ifc_object``. Each kind has one test that pins which
helpers must be called; the AST forward-compat guard in
``test_connection_forward_compat.py`` then asserts the dispatch table covers
every kind ``Connection.find_rels`` can emit.

Uses ``unittest.mock`` directly (rather than the Prophecy fixtures) because
the dispatch passes IFC rel entities with attribute access (``rel.RelatingElement``)
that Prophecy's JSON call recorder can't serialize.
"""

from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest

import bonsai.core.connection as subject


def _rel(relating="slab", related="wall"):
    return SimpleNamespace(RelatingElement=relating, RelatedElement=related)


def _ifc_with_objects(mapping):
    ifc = Mock()
    ifc.get_object.side_effect = lambda e: mapping.get(e)
    ifc.run = Mock()
    return ifc


class TestDisconnectRelPath:
    def test_removes_connection_and_recreates_both_walls(self):
        ifc = _ifc_with_objects({"elem_a": "obj_a", "elem_b": "obj_b"})
        geometry = Mock()
        model = Mock()
        connection = Mock()

        with patch("bonsai.core.connection.bonsai.core.geometry.remove_connection") as remove:
            subject.disconnect_rel(
                ifc,
                geometry,
                model,
                connection,
                subject="rel",
                kind="path",
                elem="elem_a",
                partner="elem_b",
            )

        remove.assert_called_once_with(geometry, connection="rel")
        model.recreate_wall.assert_any_call("elem_a", "obj_a")
        model.recreate_wall.assert_any_call("elem_b", "obj_b")
        assert model.recreate_wall.call_count == 2

    def test_skip_elem_recreate_suppresses_elem_side(self):
        """Cascade case: elem is being deleted — don't recreate it."""
        ifc = _ifc_with_objects({"elem": "elem_obj", "partner": "partner_obj"})
        geometry = Mock()
        model = Mock()
        connection = Mock()

        with patch("bonsai.core.connection.bonsai.core.geometry.remove_connection"):
            subject.disconnect_rel(
                ifc,
                geometry,
                model,
                connection,
                subject="rel",
                kind="path",
                elem="elem",
                partner="partner",
                skip_elem_recreate=True,
            )

        model.recreate_wall.assert_called_once_with("partner", "partner_obj")

    def test_skip_partner_recreate_suppresses_partner_side(self):
        ifc = _ifc_with_objects({"elem": "elem_obj", "partner": "partner_obj"})
        geometry = Mock()
        model = Mock()
        connection = Mock()

        with patch("bonsai.core.connection.bonsai.core.geometry.remove_connection"):
            subject.disconnect_rel(
                ifc,
                geometry,
                model,
                connection,
                subject="rel",
                kind="path",
                elem="elem",
                partner="partner",
                skip_partner_recreate=True,
            )

        model.recreate_wall.assert_called_once_with("elem", "elem_obj")

    def test_both_skips_means_only_remove_rel(self):
        ifc = _ifc_with_objects({})
        geometry = Mock()
        model = Mock()
        connection = Mock()

        with patch("bonsai.core.connection.bonsai.core.geometry.remove_connection") as remove:
            subject.disconnect_rel(
                ifc,
                geometry,
                model,
                connection,
                subject="rel",
                kind="path",
                elem="elem",
                partner="partner",
                skip_elem_recreate=True,
                skip_partner_recreate=True,
            )

        remove.assert_called_once()
        model.recreate_wall.assert_not_called()


class TestDisconnectRelElementTop:
    def test_disconnects_then_regenerates_wall(self):
        """Operator case (no skip flags): both sides survive, so the wall gets
        re-clipped against currently-connected slabs."""
        rel = _rel()
        ifc = _ifc_with_objects({"wall": "wall_obj"})
        geometry = Mock()
        model = Mock()
        connection = Mock()
        connection.orient_element_top.return_value = ("wall", "slab")

        with patch("bonsai.core.connection.regenerate_wall_to_underside") as regen:
            subject.disconnect_rel(
                ifc,
                geometry,
                model,
                connection,
                subject=rel,
                kind="element-top",
                elem="elem",
                partner="partner",
            )

        ifc.run.assert_called_once_with("geometry.disconnect_element", relating_element="slab", related_element="wall")
        regen.assert_called_once_with(ifc, geometry, model, ["wall_obj"])

    def test_slab_delete_cascade_still_regenerates_wall(self):
        """When slab is being deleted (elem=slab), wall survives and must
        re-clip against remaining connections — the cascade's main purpose."""
        rel = _rel()
        ifc = _ifc_with_objects({"wall": "wall_obj"})
        connection = Mock()
        connection.orient_element_top.return_value = ("wall", "slab")

        with patch("bonsai.core.connection.regenerate_wall_to_underside") as regen:
            subject.disconnect_rel(
                ifc,
                Mock(),
                Mock(),
                connection,
                subject=rel,
                kind="element-top",
                elem="slab",
                partner="wall",
                skip_elem_recreate=True,  # slab is being deleted
            )

        regen.assert_called_once()

    def test_wall_delete_cascade_skips_wall_regen(self):
        """When the wall itself is being deleted, regenerating its body moments
        before remove_product wipes it is wasted work — skip."""
        rel = _rel()
        ifc = _ifc_with_objects({"wall": "wall_obj"})
        connection = Mock()
        connection.orient_element_top.return_value = ("wall", "slab")

        with patch("bonsai.core.connection.regenerate_wall_to_underside") as regen:
            subject.disconnect_rel(
                ifc,
                Mock(),
                Mock(),
                connection,
                subject=rel,
                kind="element-top",
                elem="wall",
                partner="slab",
                skip_elem_recreate=True,  # wall is being deleted
            )

        regen.assert_not_called()
        ifc.run.assert_called_once()  # rel still removed

    def test_both_in_batch_skips_wall_regen(self):
        """Batch delete of both endpoints, processing slab first: partner (wall)
        also queued for deletion → skip wall regen."""
        rel = _rel()
        ifc = _ifc_with_objects({"wall": "wall_obj"})
        connection = Mock()
        connection.orient_element_top.return_value = ("wall", "slab")

        with patch("bonsai.core.connection.regenerate_wall_to_underside") as regen:
            subject.disconnect_rel(
                ifc,
                Mock(),
                Mock(),
                connection,
                subject=rel,
                kind="element-top",
                elem="slab",
                partner="wall",
                skip_elem_recreate=True,
                skip_partner_recreate=True,  # wall also in batch
            )

        regen.assert_not_called()


class TestDisconnectRelElement:
    def test_just_removes_the_rel(self):
        rel = _rel(relating="A", related="B")
        ifc = Mock()

        subject.disconnect_rel(
            ifc,
            Mock(),
            Mock(),
            Mock(),
            subject=rel,
            kind="element",
            elem="elem_a",
            partner="elem_b",
        )

        ifc.run.assert_called_once_with("geometry.disconnect_element", relating_element="A", related_element="B")


class TestDisconnectRelMEPPairFitting:
    """The ``mep-pair-fitting`` kind treats the rel slot as the fitting whose
    removal disconnects the pair — deletion routes through
    ``geometry.delete_ifc_object`` so the cascade-on-delete contract still
    owns port-rel cleanup."""

    def test_deletes_fitting_via_delete_ifc_object(self):
        fitting = Mock(name="fitting")
        fitting_obj = Mock(name="fitting_obj")
        ifc = _ifc_with_objects({fitting: fitting_obj})
        geometry = Mock()

        subject.disconnect_rel(
            ifc,
            geometry,
            Mock(),
            Mock(),
            subject=fitting,
            kind="mep-pair-fitting",
            elem="seg_a",
            partner="seg_b",
        )

        geometry.delete_ifc_object.assert_called_once_with(fitting_obj)

    def test_noops_when_fitting_has_no_blender_object(self):
        """Defensive: a fitting with no bound Blender object can't be
        deleted via ``delete_ifc_object``; the dispatch must not crash."""
        fitting = Mock(name="fitting")
        ifc = _ifc_with_objects({})
        geometry = Mock()

        subject.disconnect_rel(
            ifc,
            geometry,
            Mock(),
            Mock(),
            subject=fitting,
            kind="mep-pair-fitting",
            elem="seg_a",
            partner="seg_b",
        )

        geometry.delete_ifc_object.assert_not_called()

    def test_skip_elem_recreate_suppresses_delete_when_fitting_is_elem(self):
        """Cascade case: the fitting is itself the element being deleted
        — don't try to delete it twice."""
        fitting = Mock(name="fitting")
        ifc = _ifc_with_objects({fitting: Mock()})
        geometry = Mock()

        subject.disconnect_rel(
            ifc,
            geometry,
            Mock(),
            Mock(),
            subject=fitting,
            kind="mep-pair-fitting",
            elem=fitting,
            partner="other",
            skip_elem_recreate=True,
        )

        geometry.delete_ifc_object.assert_not_called()

    def test_skip_partner_recreate_suppresses_delete_when_fitting_is_partner(self):
        fitting = Mock(name="fitting")
        ifc = _ifc_with_objects({fitting: Mock()})
        geometry = Mock()

        subject.disconnect_rel(
            ifc,
            geometry,
            Mock(),
            Mock(),
            subject=fitting,
            kind="mep-pair-fitting",
            elem="seg_a",
            partner=fitting,
            skip_partner_recreate=True,
        )

        geometry.delete_ifc_object.assert_not_called()


class TestDisconnectRelUnknownKind:
    def test_raises_value_error(self):
        with pytest.raises(ValueError, match="Unknown kind"):
            subject.disconnect_rel(
                Mock(),
                Mock(),
                Mock(),
                Mock(),
                subject="rel",
                kind="bogus",
                elem="a",
                partner="b",
            )
