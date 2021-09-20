import test.bootstrap
import ifcopenshell.api


class TestCalculateTaskDuration(test.bootstrap.IFC4):
    def test_calculating_the_duration_based_on_a_labour_resource_with_work_hours(self):
        ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcProject")
        schedule = ifcopenshell.api.run("sequence.add_work_schedule", self.file)
        task = ifcopenshell.api.run("sequence.add_task", self.file, work_schedule=schedule)
        resource = ifcopenshell.api.run("resource.add_resource", self.file, ifc_class="IfcLaborResource")
        resource_time = ifcopenshell.api.run("resource.add_resource_time", self.file, resource=resource)
        resource_time.ScheduleWork = "PT48H"
        ifcopenshell.api.run("sequence.assign_process", self.file, relating_process=task, related_object=resource)
        ifcopenshell.api.run("sequence.calculate_task_duration", self.file, task=task)
        assert task.TaskTime.ScheduleDuration == "P6D"

    def test_calculating_the_duration_based_on_a_labour_resource_with_work_days(self):
        ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcProject")
        schedule = ifcopenshell.api.run("sequence.add_work_schedule", self.file)
        task = ifcopenshell.api.run("sequence.add_task", self.file, work_schedule=schedule)
        resource = ifcopenshell.api.run("resource.add_resource", self.file, ifc_class="IfcLaborResource")
        resource_time = ifcopenshell.api.run("resource.add_resource_time", self.file, resource=resource)
        resource_time.ScheduleWork = "P3.5D"
        ifcopenshell.api.run("sequence.assign_process", self.file, relating_process=task, related_object=resource)
        ifcopenshell.api.run("sequence.calculate_task_duration", self.file, task=task)
        assert task.TaskTime.ScheduleDuration == "P4D"

    def test_calculating_a_task_duration_without_a_work_schedule_defining_workday_duration(self):
        ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcProject")
        task = ifcopenshell.api.run("sequence.add_task", self.file)
        resource = ifcopenshell.api.run("resource.add_resource", self.file, ifc_class="IfcLaborResource")
        resource_time = ifcopenshell.api.run("resource.add_resource_time", self.file, resource=resource)
        resource_time.ScheduleWork = "P2D"
        ifcopenshell.api.run("sequence.assign_process", self.file, relating_process=task, related_object=resource)
        ifcopenshell.api.run("sequence.calculate_task_duration", self.file, task=task)
        assert task.TaskTime.ScheduleDuration == "P2D"

    def test_calculating_a_task_duration_with_a_custom_workday_duration(self):
        ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcProject")
        schedule = ifcopenshell.api.run("sequence.add_work_schedule", self.file)
        pset = ifcopenshell.api.run("pset.add_pset", self.file, product=schedule, name="Pset_WorkControlCommon")
        ifcopenshell.api.run("pset.edit_pset", self.file, pset=pset, properties={"WorkDayDuration": "PT2H"})
        task = ifcopenshell.api.run("sequence.add_task", self.file, work_schedule=schedule)
        resource = ifcopenshell.api.run("resource.add_resource", self.file, ifc_class="IfcLaborResource")
        resource_time = ifcopenshell.api.run("resource.add_resource_time", self.file, resource=resource)
        resource_time.ScheduleWork = "PT48H"
        ifcopenshell.api.run("sequence.assign_process", self.file, relating_process=task, related_object=resource)
        ifcopenshell.api.run("sequence.calculate_task_duration", self.file, task=task)
        assert task.TaskTime.ScheduleDuration == "P24D"

    def test_failing_to_calculate_if_no_schedule_work_usage(self):
        ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcProject")
        schedule = ifcopenshell.api.run("sequence.add_work_schedule", self.file)
        task = ifcopenshell.api.run("sequence.add_task", self.file, work_schedule=schedule)
        resource = ifcopenshell.api.run("resource.add_resource", self.file, ifc_class="IfcLaborResource")
        ifcopenshell.api.run("sequence.assign_process", self.file, relating_process=task, related_object=resource)
        ifcopenshell.api.run("sequence.calculate_task_duration", self.file, task=task)
        assert task.TaskTime is None

    def test_calculating_a_nested_task_duration_based_on_a_labour_resource_with_work_hours(self):
        ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcProject")
        schedule = ifcopenshell.api.run("sequence.add_work_schedule", self.file)
        task = ifcopenshell.api.run("sequence.add_task", self.file, work_schedule=schedule)
        subtask = ifcopenshell.api.run("sequence.add_task", self.file, parent_task=task)
        resource = ifcopenshell.api.run("resource.add_resource", self.file, ifc_class="IfcLaborResource")
        resource_time = ifcopenshell.api.run("resource.add_resource_time", self.file, resource=resource)
        resource_time.ScheduleWork = "PT48H"
        ifcopenshell.api.run("sequence.assign_process", self.file, relating_process=subtask, related_object=resource)
        ifcopenshell.api.run("sequence.calculate_task_duration", self.file, task=subtask)
        assert subtask.TaskTime.ScheduleDuration == "P6D"
