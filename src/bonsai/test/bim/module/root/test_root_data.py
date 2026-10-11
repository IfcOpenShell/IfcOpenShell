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

import pytest

import bonsai.tool as tool
from bonsai.bim.module.root.data import IfcClassData
from test.bim.bootstrap import NewIfc

pytestmark = pytest.mark.root


class TestIfcClassDataLoad(NewIfc):
    def test_load_populates_classes_for_a_valid_product(self):
        tool.Root.get_root_props().ifc_product = "IfcElement"

        IfcClassData.is_loaded = False
        IfcClassData.load()

        assert IfcClassData.is_loaded is True
        assert IfcClassData.data["ifc_products"]
        assert IfcClassData.data["ifc_classes"]

    def test_load_survives_a_stale_enum_index(self):
        props = tool.Root.get_root_props()
        props["ifc_product"] = 9999
        props["ifc_class"] = 9999

        IfcClassData.is_loaded = False
        IfcClassData.load()

        assert IfcClassData.is_loaded is True
        assert "ifc_products" in IfcClassData.data
        assert IfcClassData.data["ifc_classes"] == []
        assert IfcClassData.data["ifc_predefined_types"] == []
