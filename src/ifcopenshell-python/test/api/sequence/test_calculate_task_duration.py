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
