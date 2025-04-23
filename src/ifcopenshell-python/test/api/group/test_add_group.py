# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
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

import test.bootstrap
import ifcopenshell.api.group
import ifcopenshell.util.element


class TestAddGroup(test.bootstrap.IFC4):
    def test_add_group_no_arguments(self):
        group = ifcopenshell.api.group.add_group(self.file)
        assert group.Name == "Unnamed"
        assert group.Description == None

    def test_add_group(self):
        group = ifcopenshell.api.group.add_group(self.file, name="Name", description="Description")
        assert group.Name == "Name"
        assert group.Description == "Description"


class TestAddGroupIFC2X3(test.bootstrap.IFC2X3, TestAddGroup):
    pass
