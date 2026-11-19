# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026 Dion Moult <dion@thinkmoult.com>
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

from types import SimpleNamespace
from unittest.mock import patch

import pytest

import bonsai.tool as tool
from test.bim.bootstrap import NewFile

pytestmark = pytest.mark.geometry


class TestRecordObjectMaterials(NewFile):
    def test_skips_when_object_has_no_data(self):
        empty_obj = SimpleNamespace(data=None)

        with (
            patch.object(tool.Geometry, "get_mesh_props") as mock_get_mesh_props,
            patch.object(tool.Geometry, "get_material_checksum") as mock_checksum,
        ):
            tool.Geometry.record_object_materials(empty_obj)

        mock_get_mesh_props.assert_not_called()
        mock_checksum.assert_not_called()
