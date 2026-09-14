# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2026 Dion Moult <dion@thinkmoult.com>
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

import ifcopenshell.api.root
import ifcopenshell.api.structural
import test.bootstrap


class TestRemoveStructuralConnectionCondition(test.bootstrap.IFC4):
    def test_removing_a_connection_condition_also_purges_the_boundary_condition(self):
        member = ifcopenshell.api.root.create_entity(
            self.file, ifc_class="IfcStructuralCurveMember", predefined_type="RIGID_JOINED_MEMBER"
        )
        connection = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcStructuralPointConnection")
        rel = ifcopenshell.api.structural.add_structural_member_connection(
            self.file, relating_structural_member=member, related_structural_connection=connection
        )
        ifcopenshell.api.structural.add_structural_boundary_condition(self.file, connection=rel)
        assert len(self.file.by_type("IfcBoundaryCondition")) == 1

        ifcopenshell.api.structural.remove_structural_connection_condition(self.file, relation=rel)

        assert len(self.file.by_type("IfcRelConnectsStructuralMember")) == 0
        # The boundary condition was assigned to the relation (not the bare
        # connection), so it must be purged along with the relation instead
        # of being left as an orphan with no inverses.
        assert len(self.file.by_type("IfcBoundaryCondition")) == 0


class TestRemoveStructuralConnectionConditionIFC2X3(test.bootstrap.IFC2X3, TestRemoveStructuralConnectionCondition):
    pass
