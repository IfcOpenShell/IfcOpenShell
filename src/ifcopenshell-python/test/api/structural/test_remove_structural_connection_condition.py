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

import ifcopenshell.api.root
import ifcopenshell.api.structural
import test.bootstrap


class TestRemoveStructuralConnectionCondition(test.bootstrap.IFC4):
    def make_support_with_a_released_member(self):
        member = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcStructuralCurveMember")
        connection = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcStructuralPointConnection")
        support = ifcopenshell.api.structural.add_structural_boundary_condition(
            self.file, name="Support", connection=connection
        )
        relation = ifcopenshell.api.structural.add_structural_member_connection(
            self.file, relating_structural_member=member, related_structural_connection=connection
        )
        release = ifcopenshell.api.structural.add_structural_boundary_condition(
            self.file, name="Release", connection=relation
        )
        return connection, support, relation, release

    def test_removing_a_relation_without_a_condition(self):
        member = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcStructuralCurveMember")
        connection = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcStructuralPointConnection")
        relation = ifcopenshell.api.structural.add_structural_member_connection(
            self.file, relating_structural_member=member, related_structural_connection=connection
        )
        ifcopenshell.api.structural.remove_structural_connection_condition(self.file, relation=relation)
        assert not self.file.by_type("IfcRelConnectsStructuralMember")
        assert self.file.by_type("IfcStructuralPointConnection") == (connection,)

    def test_keeping_the_condition_of_the_connection(self):
        # The relation's AppliedCondition is a release of the member; the connection's is the support
        connection, support, relation, release = self.make_support_with_a_released_member()
        ifcopenshell.api.structural.remove_structural_connection_condition(self.file, relation=relation)
        assert connection.AppliedCondition == support

    def test_removing_the_release_of_the_relation(self):
        connection, support, relation, release = self.make_support_with_a_released_member()
        ifcopenshell.api.structural.remove_structural_connection_condition(self.file, relation=relation)
        assert not self.file.by_type("IfcRelConnectsStructuralMember")
        assert [c.Name for c in self.file.by_type("IfcBoundaryNodeCondition")] == ["Support"]

    def test_keeping_a_release_used_by_another_relation(self):
        connection, support, relation, release = self.make_support_with_a_released_member()
        other_member = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcStructuralCurveMember")
        other = ifcopenshell.api.structural.add_structural_member_connection(
            self.file, relating_structural_member=other_member, related_structural_connection=connection
        )
        other.AppliedCondition = release
        ifcopenshell.api.structural.remove_structural_connection_condition(self.file, relation=relation)
        assert other.AppliedCondition == release
        assert connection.AppliedCondition == support


class TestRemoveStructuralConnectionConditionIFC2X3(test.bootstrap.IFC2X3, TestRemoveStructuralConnectionCondition):
    pass
