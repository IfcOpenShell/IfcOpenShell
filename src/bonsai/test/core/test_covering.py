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

"""Coverage for ``core.covering.add_instance_wall_coverings_from_walls``.

This is the single operator that survived collapsing the wall-covering pair
(``bim.add_instance_wall_covering_from_cursor`` and
``bim.add_instance_wall_coverings_from_walls``) into one, per review feedback
on PR #8699: the "from cursor" variant only ever ran off the active object
inside a wall-restricted poll, so it never covered anything this variant
doesn't already do when a single wall is selected.

Uses ``unittest.mock`` directly (matching ``test_connection.py``) rather than
the ``Prophecy`` fixtures, since the dispatch loop checks
``element.is_a("IfcWall")`` on whatever ``ifc.get_entity`` returns, which is
easier to express with plain mocks than with Prophecy's JSON call recorder.
"""

from unittest.mock import Mock

import pytest

import bonsai.core.covering as subject


def _wall(name="wall"):
    element = Mock(name=f"{name}_element")
    element.is_a.side_effect = lambda c: c == "IfcWall"
    return element


def _non_wall(name="slab"):
    element = Mock(name=f"{name}_element")
    element.is_a.side_effect = lambda c: c == "IfcSlab"
    return element


class TestAddInstanceWallCoveringsFromWallsGuards:
    def test_raises_no_default_container_when_none_set(self):
        ifc, root, covering, spatial = Mock(), Mock(), Mock(), Mock()
        root.get_default_container.return_value = None

        with pytest.raises(subject.NoDefaultContainer):
            subject.add_instance_wall_coverings_from_walls(ifc, root, covering, spatial)

        covering.get_relating_type_layer_thickness.assert_not_called()
        spatial.get_selected_objects.assert_not_called()

    def test_raises_no_layer_set_thickness_when_relating_type_has_none(self):
        ifc, root, covering, spatial = Mock(), Mock(), Mock(), Mock()
        root.get_default_container.return_value = "container"
        covering.get_relating_type_layer_thickness.return_value = 0.0

        with pytest.raises(subject.NoLayerSetThickness):
            subject.add_instance_wall_coverings_from_walls(ifc, root, covering, spatial)

        spatial.get_selected_objects.assert_not_called()


class TestAddInstanceWallCoveringsFromWallsSelection:
    def test_creates_a_covering_for_each_selected_wall_and_skips_the_rest(self):
        """A multi-object selection with two walls and one non-wall element
        must produce exactly two coverings, one per wall — the non-wall
        object is silently skipped, not errored on."""
        ifc, root, covering, spatial = Mock(), Mock(), Mock(), Mock()
        root.get_default_container.return_value = "container"
        covering.get_relating_type_layer_thickness.return_value = 0.1

        wall_obj_1, wall_obj_2, slab_obj = Mock(name="wall_obj_1"), Mock(name="wall_obj_2"), Mock(name="slab_obj")
        wall_element_1, wall_element_2, slab_element = _wall("wall1"), _wall("wall2"), _non_wall()
        spatial.get_selected_objects.return_value = [wall_obj_1, slab_obj, wall_obj_2]
        ifc.get_entity.side_effect = lambda obj: {
            wall_obj_1: wall_element_1,
            wall_obj_2: wall_element_2,
            slab_obj: slab_element,
        }[obj]

        subject.add_instance_wall_coverings_from_walls(ifc, root, covering, spatial, facing_cursor=True)

        assert covering.create_wall_covering.call_count == 2
        covering.create_wall_covering.assert_any_call(wall_obj_1, facing_cursor=True)
        covering.create_wall_covering.assert_any_call(wall_obj_2, facing_cursor=True)

    def test_passes_facing_cursor_false_through_for_the_opposite_side(self):
        ifc, root, covering, spatial = Mock(), Mock(), Mock(), Mock()
        root.get_default_container.return_value = "container"
        covering.get_relating_type_layer_thickness.return_value = 0.1

        wall_obj = Mock(name="wall_obj")
        spatial.get_selected_objects.return_value = [wall_obj]
        ifc.get_entity.return_value = _wall()

        subject.add_instance_wall_coverings_from_walls(ifc, root, covering, spatial, facing_cursor=False)

        covering.create_wall_covering.assert_called_once_with(wall_obj, facing_cursor=False)

    def test_no_wall_in_selection_creates_nothing_and_does_not_raise(self):
        """The operator's poll already requires a wall active object, but the
        core dispatch loop itself must stay defensive: a selection with no
        ``IfcWall`` element (e.g. only the non-wall part of a multi-select
        survives to this point) must be a no-op, not a crash."""
        ifc, root, covering, spatial = Mock(), Mock(), Mock(), Mock()
        root.get_default_container.return_value = "container"
        covering.get_relating_type_layer_thickness.return_value = 0.1

        slab_obj = Mock(name="slab_obj")
        spatial.get_selected_objects.return_value = [slab_obj]
        ifc.get_entity.return_value = _non_wall()

        subject.add_instance_wall_coverings_from_walls(ifc, root, covering, spatial)

        covering.create_wall_covering.assert_not_called()

    def test_selected_object_with_no_ifc_entity_is_skipped(self):
        """Non-IFC Blender objects (e.g. a stray mesh) can be selected
        alongside a wall; ``ifc.get_entity`` returns ``None`` for those and
        the loop must not call ``.is_a`` on ``None``."""
        ifc, root, covering, spatial = Mock(), Mock(), Mock(), Mock()
        root.get_default_container.return_value = "container"
        covering.get_relating_type_layer_thickness.return_value = 0.1

        stray_obj = Mock(name="stray_obj")
        spatial.get_selected_objects.return_value = [stray_obj]
        ifc.get_entity.return_value = None

        subject.add_instance_wall_coverings_from_walls(ifc, root, covering, spatial)

        covering.create_wall_covering.assert_not_called()
