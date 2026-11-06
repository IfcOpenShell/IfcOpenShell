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

"""Regression test for #10026:
AttributeError when recreating profiles on elements without ConnectedTo / ConnectedFrom (such as IfcStructuralCurveMember in IFC4).
"""

from unittest.mock import MagicMock
import pytest

from bonsai.bim.module.model.profile import DumbProfileJoiner

pytestmark = pytest.mark.model


def test_recreate_profile_without_connected_to_attribute():
    """Verify DumbProfileJoiner.recreate_profile gracefully handles elements without
    ConnectedTo or ConnectedFrom attributes (e.g. IFC4 IfcStructuralCurveMember)."""
    joiner = DumbProfileJoiner()

    # Mock element without ConnectedTo or ConnectedFrom (attribute access raises AttributeError)
    class MockElementWithoutConnectedTo:
        def __getattr__(self, name):
            if name in ("ConnectedTo", "ConnectedFrom"):
                raise AttributeError(f"Mock element has no attribute '{name}'")
            return MagicMock()

    element = MockElementWithoutConnectedTo()
    mock_obj = MagicMock()

    # Mock material retrieval to return None to exit early after connection processing
    import ifcopenshell.util.element
    orig_get_material = ifcopenshell.util.element.get_material
    try:
        ifcopenshell.util.element.get_material = MagicMock(return_value=None)
        # Should not raise AttributeError when inspecting connections
        axis = [MagicMock(), MagicMock()]
        joiner.recreate_profile(element, mock_obj, axis=axis, body=axis)
    finally:
        ifcopenshell.util.element.get_material = orig_get_material
