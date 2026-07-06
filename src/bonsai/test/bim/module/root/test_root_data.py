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
        # Baseline: a valid ifc_product resolves to a real schema declaration, so
        # load() completes and the class list is populated.
        tool.Root.get_root_props().ifc_product = "IfcElement"

        IfcClassData.is_loaded = False
        IfcClassData.load()

        assert IfcClassData.is_loaded is True
        assert IfcClassData.data["ifc_products"]
        assert IfcClassData.data["ifc_classes"]

    def test_load_survives_a_stale_enum_index(self):
        # Regression for the per-redraw freeze / KeyError 'ifc_products'. ifc_product and
        # ifc_class are dynamic EnumProperties; a reloaded file can carry a stored index
        # that matches no current item (Blender warns "matches no enum"). Assigning the
        # raw ID-property int bypasses enum validation and reproduces that stale state.
        #
        # Reading such an enum during load() runs its items= callback, which re-enters
        # load() unless is_loaded is already set, resetting cls.data mid-build; and
        # declaration_by_name() on the unresolved value raises. load() must survive both:
        # complete, keep the fully-built dict, and cache (is_loaded True). See #6398.
        props = tool.Root.get_root_props()
        props["ifc_product"] = 9999
        props["ifc_class"] = 9999

        IfcClassData.is_loaded = False
        IfcClassData.load()  # must not raise, KeyError, or leave is_loaded False

        assert IfcClassData.is_loaded is True
        assert "ifc_products" in IfcClassData.data
        assert IfcClassData.data["ifc_classes"] == []
        assert IfcClassData.data["ifc_predefined_types"] == []
