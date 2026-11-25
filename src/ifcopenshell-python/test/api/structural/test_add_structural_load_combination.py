# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2026 Bruno Postle <bruno@postle.net>
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
# This file was generated with the assistance of an AI coding tool.

import ifcopenshell.api.structural
import test.bootstrap


class TestAddStructuralLoadCombination(test.bootstrap.IFC4):
    def test_adding_a_load_combination(self):
        subject = ifcopenshell.api.structural.add_structural_load_combination(self.file, name="ULS 1", purpose="ULS")
        assert subject.is_a() == "IfcStructuralLoadGroup"
        assert subject.PredefinedType == "LOAD_COMBINATION"
        assert subject.Name == "ULS 1"
        assert subject.Purpose == "ULS"
        assert subject.ActionType == "NOTDEFINED"
        assert subject.ActionSource == "NOTDEFINED"
        assert subject.Coefficient is None


class TestAddStructuralLoadCombinationIFC4X3(test.bootstrap.IFC4X3, TestAddStructuralLoadCombination):
    pass
