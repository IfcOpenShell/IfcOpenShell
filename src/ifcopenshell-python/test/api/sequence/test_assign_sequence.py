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

import ifcopenshell.api.sequence
import test.bootstrap


# NOTE: sequence module features rely on entities introduced in IFC4
# therefore no IFC2X3 tests
class TestAssignSequence(test.bootstrap.IFC4):
    def test_assigning_a_sequence(self):
        predecessor = ifcopenshell.api.sequence.add_task(self.file)
        successor = ifcopenshell.api.sequence.add_task(self.file)
        rel = ifcopenshell.api.sequence.assign_sequence(
            self.file, relating_process=predecessor, related_process=successor
        )
        assert rel.is_a("IfcRelSequence")
        assert rel.RelatingProcess == predecessor
        assert rel.RelatedProcess == successor
        assert rel.SequenceType == "FINISH_START"

    def test_assigning_a_sequence_of_a_chosen_type(self):
        predecessor = ifcopenshell.api.sequence.add_task(self.file)
        successor = ifcopenshell.api.sequence.add_task(self.file)
        rel = ifcopenshell.api.sequence.assign_sequence(
            self.file,
            relating_process=predecessor,
            related_process=successor,
            sequence_type="START_START",
        )
        assert rel.SequenceType == "START_START"

    def test_not_assigning_the_same_sequence_twice(self):
        predecessor = ifcopenshell.api.sequence.add_task(self.file)
        successor = ifcopenshell.api.sequence.add_task(self.file)
        rel1 = ifcopenshell.api.sequence.assign_sequence(
            self.file, relating_process=predecessor, related_process=successor
        )
        rel2 = ifcopenshell.api.sequence.assign_sequence(
            self.file, relating_process=predecessor, related_process=successor
        )
        assert rel1 == rel2
        assert len(self.file.by_type("IfcRelSequence")) == 1

    def test_assigning_two_sequences_of_different_types_to_the_same_pair(self):
        # A "ladder": the follower may start once the leader has started, and
        # may not finish before the leader finishes. Both constraints are real
        # and neither implies the other, so both relationships must survive.
        predecessor = ifcopenshell.api.sequence.add_task(self.file)
        successor = ifcopenshell.api.sequence.add_task(self.file)
        start = ifcopenshell.api.sequence.assign_sequence(
            self.file,
            relating_process=predecessor,
            related_process=successor,
            sequence_type="START_START",
        )
        finish = ifcopenshell.api.sequence.assign_sequence(
            self.file,
            relating_process=predecessor,
            related_process=successor,
            sequence_type="FINISH_FINISH",
        )
        assert start != finish
        assert len(self.file.by_type("IfcRelSequence")) == 2
        assert {rel.SequenceType for rel in successor.IsSuccessorFrom} == {
            "START_START",
            "FINISH_FINISH",
        }

    def test_not_confusing_the_two_directions_of_a_pair(self):
        task1 = ifcopenshell.api.sequence.add_task(self.file)
        task2 = ifcopenshell.api.sequence.add_task(self.file)
        forwards = ifcopenshell.api.sequence.assign_sequence(
            self.file, relating_process=task1, related_process=task2
        )
        backwards = ifcopenshell.api.sequence.assign_sequence(
            self.file, relating_process=task2, related_process=task1
        )
        assert forwards != backwards
        assert len(self.file.by_type("IfcRelSequence")) == 2
