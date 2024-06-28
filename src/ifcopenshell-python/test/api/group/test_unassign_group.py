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
import ifcopenshell.api.root
import ifcopenshell.api.group


class TestAssignGroup(test.bootstrap.IFC4):
    def test_group_unassignment(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        element2 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        element3 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        group = ifcopenshell.api.group.add_group(self.file)
        ifcopenshell.api.group.assign_group(self.file, products=[element, element2, element3], group=group)
        ifcopenshell.api.group.unassign_group(self.file, products=[element2, element3], group=group)

        assert len(rels := self.file.by_type("IfcRelAssignsToGroup")) == 1
        rel = rels[0]
        assert rel.RelatingGroup == group
        assert rel.RelatedObjects == (element,)

    def test_remove_relationship_unassigning_last_element(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        element2 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        group = ifcopenshell.api.group.add_group(self.file)
        ifcopenshell.api.group.assign_group(self.file, products=[element, element2], group=group)
        ifcopenshell.api.group.unassign_group(self.file, products=[element, element2], group=group)
        assert len(self.file.by_type("IfcRelAssignsToGroup")) == 0


class TestAssignGroupIFC2X3(test.bootstrap.IFC2X3, TestAssignGroup):
    pass
