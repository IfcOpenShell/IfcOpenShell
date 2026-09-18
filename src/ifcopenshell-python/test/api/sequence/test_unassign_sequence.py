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
class TestUnassignSequence(test.bootstrap.IFC4):
    def _pair(self):
        return (
            ifcopenshell.api.sequence.add_task(self.file),
            ifcopenshell.api.sequence.add_task(self.file),
        )

    def test_unassigning_a_sequence(self):
        predecessor, successor = self._pair()
        ifcopenshell.api.sequence.assign_sequence(self.file, relating_process=predecessor, related_process=successor)
        ifcopenshell.api.sequence.unassign_sequence(self.file, relating_process=predecessor, related_process=successor)
        assert len(self.file.by_type("IfcRelSequence")) == 0

    def test_doing_nothing_if_the_tasks_are_not_sequenced(self):
        predecessor, successor = self._pair()
        ifcopenshell.api.sequence.unassign_sequence(self.file, relating_process=predecessor, related_process=successor)
        assert len(self.file.by_type("IfcRelSequence")) == 0

    def test_unassigning_every_sequence_between_the_pair_by_default(self):
        predecessor, successor = self._pair()
        for sequence_type in ("START_START", "FINISH_FINISH"):
            ifcopenshell.api.sequence.assign_sequence(
                self.file,
                relating_process=predecessor,
                related_process=successor,
                sequence_type=sequence_type,
            )
        ifcopenshell.api.sequence.unassign_sequence(self.file, relating_process=predecessor, related_process=successor)
        assert len(self.file.by_type("IfcRelSequence")) == 0

    def test_unassigning_only_the_named_type(self):
        predecessor, successor = self._pair()
        for sequence_type in ("START_START", "FINISH_FINISH"):
            ifcopenshell.api.sequence.assign_sequence(
                self.file,
                relating_process=predecessor,
                related_process=successor,
                sequence_type=sequence_type,
            )
        ifcopenshell.api.sequence.unassign_sequence(
            self.file,
            relating_process=predecessor,
            related_process=successor,
            sequence_type="START_START",
        )
        rels = self.file.by_type("IfcRelSequence")
        assert len(rels) == 1
        assert rels[0].SequenceType == "FINISH_FINISH"

    def test_not_unassigning_a_type_that_is_not_there(self):
        predecessor, successor = self._pair()
        ifcopenshell.api.sequence.assign_sequence(
            self.file,
            relating_process=predecessor,
            related_process=successor,
            sequence_type="START_START",
        )
        ifcopenshell.api.sequence.unassign_sequence(
            self.file,
            relating_process=predecessor,
            related_process=successor,
            sequence_type="FINISH_FINISH",
        )
        assert len(self.file.by_type("IfcRelSequence")) == 1

    def test_leaving_the_other_direction_alone(self):
        task1, task2 = self._pair()
        ifcopenshell.api.sequence.assign_sequence(self.file, relating_process=task1, related_process=task2)
        ifcopenshell.api.sequence.assign_sequence(self.file, relating_process=task2, related_process=task1)
        ifcopenshell.api.sequence.unassign_sequence(self.file, relating_process=task1, related_process=task2)
        rels = self.file.by_type("IfcRelSequence")
        assert len(rels) == 1
        assert rels[0].RelatingProcess == task2
