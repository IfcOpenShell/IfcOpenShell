# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of IfcOpenShell.
#
# IfcOpenShell is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcOpenShell is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcOpenShell.  If not, see <http://www.gnu.org/licenses/>.

"""Run this test from src/ifcopenshell-python folder: pytest --durations=0 ifcopenshell/util/test_pset.py"""
from ifcopenshell.util import pset
from ifcopenshell import util


class TestPsetQto:
    @classmethod
    def setup_class(cls):
        cls.pset_qto = util.pset.PsetQto("IFC4")

    def test_get_applicables(self):
        for i in range(1000):
            assert len(self.pset_qto.get_applicable("IfcMaterial")) == 14

    def test_get_applicables_names(self):
        for i in range(1000):
            assert len(self.pset_qto.get_applicable_names("IfcMaterial")) == 14
