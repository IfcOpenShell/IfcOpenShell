# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2026 IfcOpenShell contributors
#
# This file is part of IfcOpenShell.
#
# IfcOpenShell is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.


import pytest

import ifcopenshell.api.root
import ifcopenshell.api.sequence
import ifcopenshell.util.sequence
import test.bootstrap


class TestCreateBaseline(test.bootstrap.IFC4):
    def create_planned_schedule(self, name="Design & Build"):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        return ifcopenshell.api.sequence.add_work_schedule(self.file, name=name, predefined_type="PLANNED")

    def test_returns_the_created_baseline_schedule(self):
        planned = self.create_planned_schedule()
        root_task = ifcopenshell.api.sequence.add_task(self.file, work_schedule=planned, name="Design")

        baseline = ifcopenshell.api.sequence.create_baseline(self.file, work_schedule=planned, name="Baseline 1")

        assert baseline.is_a("IfcWorkSchedule")
        assert baseline.Name == "Baseline 1"
        assert baseline.PredefinedType == "BASELINE"
        baseline_roots = ifcopenshell.util.sequence.get_root_tasks(baseline)
        assert [task.Name for task in baseline_roots] == [root_task.Name]
        assert baseline_roots != [root_task]

    def test_falls_back_to_the_planned_schedule_name(self):
        planned = self.create_planned_schedule()

        baseline = ifcopenshell.api.sequence.create_baseline(self.file, work_schedule=planned)

        assert baseline.Name == "Design & Build"

    def test_leaves_the_name_null_when_both_names_are_omitted(self):
        planned = self.create_planned_schedule()
        planned.Name = None

        baseline = ifcopenshell.api.sequence.create_baseline(self.file, work_schedule=planned)

        assert baseline.Name is None

    def test_rejects_a_non_planned_schedule(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        actual = ifcopenshell.api.sequence.add_work_schedule(self.file, predefined_type="ACTUAL")

        with pytest.raises(ValueError):
            ifcopenshell.api.sequence.create_baseline(self.file, work_schedule=actual)

    def test_baselines_a_schedule_without_tasks(self):
        planned = self.create_planned_schedule()

        baseline = ifcopenshell.api.sequence.create_baseline(self.file, work_schedule=planned, name="Baseline 1")

        assert ifcopenshell.util.sequence.get_root_tasks(baseline) == []

    def test_baselines_every_root_task(self):
        planned = self.create_planned_schedule()
        ifcopenshell.api.sequence.add_task(self.file, work_schedule=planned, name="Design")
        ifcopenshell.api.sequence.add_task(self.file, work_schedule=planned, name="Construction")

        baseline = ifcopenshell.api.sequence.create_baseline(self.file, work_schedule=planned, name="Baseline 1")

        baseline_roots = ifcopenshell.util.sequence.get_root_tasks(baseline)
        assert sorted(task.Name for task in baseline_roots) == ["Construction", "Design"]

    def test_baselines_nested_tasks(self):
        planned = self.create_planned_schedule()
        root_task = ifcopenshell.api.sequence.add_task(self.file, work_schedule=planned, name="Construction")
        ifcopenshell.api.sequence.add_task(self.file, parent_task=root_task, name="Foundations")
        ifcopenshell.api.sequence.add_task(self.file, parent_task=root_task, name="Superstructure")

        baseline = ifcopenshell.api.sequence.create_baseline(self.file, work_schedule=planned, name="Baseline 1")

        baseline_root = ifcopenshell.util.sequence.get_root_tasks(baseline)[0]
        nested = ifcopenshell.util.sequence.get_nested_tasks(baseline_root)
        assert sorted(task.Name for task in nested) == ["Foundations", "Superstructure"]
        assert len(self.file.by_type("IfcTask")) == 6

    def test_baselines_task_attributes_and_times(self):
        planned = self.create_planned_schedule()
        task = ifcopenshell.api.sequence.add_task(
            self.file, work_schedule=planned, name="Foundations", identification="A1", description="Pour concrete"
        )
        ifcopenshell.api.sequence.add_task_time(self.file, task=task)
        ifcopenshell.api.sequence.edit_task_time(
            self.file, task_time=task.TaskTime, attributes={"ScheduleDuration": "P5D"}
        )

        baseline = ifcopenshell.api.sequence.create_baseline(self.file, work_schedule=planned, name="Baseline 1")

        baseline_task = ifcopenshell.util.sequence.get_root_tasks(baseline)[0]
        assert baseline_task.Identification == "A1"
        assert baseline_task.Description == "Pour concrete"
        assert baseline_task.TaskTime != task.TaskTime
        assert baseline_task.TaskTime.ScheduleDuration == "P5D"

    def test_baselines_sequence_relationships_between_tasks(self):
        planned = self.create_planned_schedule()
        root_task = ifcopenshell.api.sequence.add_task(self.file, work_schedule=planned, name="Construction")
        predecessor = ifcopenshell.api.sequence.add_task(self.file, parent_task=root_task, name="Foundations")
        successor = ifcopenshell.api.sequence.add_task(self.file, parent_task=root_task, name="Superstructure")
        ifcopenshell.api.sequence.assign_sequence(self.file, relating_process=predecessor, related_process=successor)

        baseline = ifcopenshell.api.sequence.create_baseline(self.file, work_schedule=planned, name="Baseline 1")

        baseline_root = ifcopenshell.util.sequence.get_root_tasks(baseline)[0]
        nested = {task.Name: task for task in ifcopenshell.util.sequence.get_nested_tasks(baseline_root)}
        rels = nested["Foundations"].IsPredecessorTo
        assert len(rels) == 1
        assert rels[0].RelatedProcess == nested["Superstructure"]

    def test_references_the_planned_schedule_and_tasks(self):
        planned = self.create_planned_schedule()
        root_task = ifcopenshell.api.sequence.add_task(self.file, work_schedule=planned, name="Construction")
        subtask = ifcopenshell.api.sequence.add_task(self.file, parent_task=root_task, name="Foundations")

        baseline = ifcopenshell.api.sequence.create_baseline(self.file, work_schedule=planned, name="Baseline 1")

        baseline_root = ifcopenshell.util.sequence.get_root_tasks(baseline)[0]
        baseline_subtask = ifcopenshell.util.sequence.get_nested_tasks(baseline_root)[0]
        references = {
            rel.RelatingObject: list(rel.RelatedObjects) for rel in self.file.by_type("IfcRelDefinesByObject")
        }
        assert references[planned] == [baseline]
        assert references[root_task] == [baseline_root]
        assert references[subtask] == [baseline_subtask]

    def test_reuses_the_existing_reference_for_further_baselines(self):
        planned = self.create_planned_schedule()

        first = ifcopenshell.api.sequence.create_baseline(self.file, work_schedule=planned, name="Baseline 1")
        second = ifcopenshell.api.sequence.create_baseline(self.file, work_schedule=planned, name="Baseline 2")

        assert len(planned.Declares) == 1
        assert list(planned.Declares[0].RelatedObjects) == [first, second]
