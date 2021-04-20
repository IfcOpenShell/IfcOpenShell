import bpy
import json
import ifcopenshell.api
from datetime import datetime
from dateutil import parser
from blenderbim.bim.ifc import IfcStore
from ifcopenshell.api.sequence.data import Data


class LoadWorkPlans(bpy.types.Operator):
    bl_idname = "bim.load_work_plans"
    bl_label = "Load Work Plans"

    def execute(self, context):
        props = context.scene.BIMWorkPlanProperties
        while len(props.work_plans) > 0:
            props.work_plans.remove(0)
        for ifc_definition_id, work_plan in Data.work_plans.items():
            new = props.work_plans.add()
            new.ifc_definition_id = ifc_definition_id
            new.name = work_plan["Name"] or "Unnamed"
        props.is_editing = True
        bpy.ops.bim.disable_editing_work_plan()
        return {"FINISHED"}


class DisableWorkPlanEditingUI(bpy.types.Operator):
    bl_idname = "bim.disable_work_plan_editing_ui"
    bl_label = "Disable WorkPlan Editing UI"

    def execute(self, context):
        context.scene.BIMWorkPlanProperties.is_editing = False
        return {"FINISHED"}


class AddWorkPlan(bpy.types.Operator):
    bl_idname = "bim.add_work_plan"
    bl_label = "Add Work Plan"

    def execute(self, context):
        ifcopenshell.api.run("sequence.add_work_plan", IfcStore.get_file())
        Data.load(IfcStore.get_file())
        bpy.ops.bim.load_work_plans()
        return {"FINISHED"}


class EditWorkPlan(bpy.types.Operator):
    bl_idname = "bim.edit_work_plan"
    bl_label = "Edit Work Plan"

    def execute(self, context):
        props = context.scene.BIMWorkPlanProperties
        attributes = {}
        for attribute in props.work_plan_attributes:
            if attribute.is_null:
                attributes[attribute.name] = None
            else:
                if attribute.data_type == "string":
                    attributes[attribute.name] = attribute.string_value
                elif attribute.data_type == "enum":
                    attributes[attribute.name] = attribute.enum_value
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "sequence.edit_work_plan",
            self.file,
            **{"work_plan": self.file.by_id(props.active_work_plan_id), "attributes": attributes}
        )
        Data.load(IfcStore.get_file())
        bpy.ops.bim.load_work_plans()
        return {"FINISHED"}


class RemoveWorkPlan(bpy.types.Operator):
    bl_idname = "bim.remove_work_plan"
    bl_label = "Remove Work Plan"
    work_plan: bpy.props.IntProperty()

    def execute(self, context):
        self.file = IfcStore.get_file()
        ifcopenshell.api.run("sequence.remove_work_plan", self.file, **{"work_plan": self.file.by_id(self.work_plan)})
        Data.load(IfcStore.get_file())
        bpy.ops.bim.load_work_plans()
        return {"FINISHED"}


class EnableEditingWorkPlan(bpy.types.Operator):
    bl_idname = "bim.enable_editing_work_plan"
    bl_label = "Enable Editing Work Plan"
    work_plan: bpy.props.IntProperty()

    def execute(self, context):
        props = context.scene.BIMWorkPlanProperties
        while len(props.work_plan_attributes) > 0:
            props.work_plan_attributes.remove(0)

        data = Data.work_plans[self.work_plan]

        for attribute in IfcStore.get_schema().declaration_by_name("IfcWorkPlan").all_attributes():
            data_type = ifcopenshell.util.attribute.get_primitive_type(attribute)
            if data_type == "entity":
                continue
            new = props.work_plan_attributes.add()
            new.name = attribute.name()
            new.is_null = data[attribute.name()] is None
            new.is_optional = attribute.optional()
            new.data_type = data_type
            if attribute.name() in ["CreationDate", "StartTime", "FinishTime"]:
                new.string_value = "" if new.is_null else data[attribute.name()].isoformat()
            elif data_type == "string":
                new.string_value = "" if new.is_null else data[attribute.name()]
            elif data_type == "enum":
                new.enum_items = json.dumps(ifcopenshell.util.attribute.get_enum_items(attribute))
                if data[attribute.name()]:
                    new.enum_value = data[attribute.name()]
        props.active_work_plan_id = self.work_plan
        return {"FINISHED"}


class DisableEditingWorkPlan(bpy.types.Operator):
    bl_idname = "bim.disable_editing_work_plan"
    bl_label = "Disable Editing Work Plan"

    def execute(self, context):
        context.scene.BIMWorkPlanProperties.active_work_plan_id = 0
        return {"FINISHED"}


class AddWorkSchedule(bpy.types.Operator):
    bl_idname = "bim.add_work_schedule"
    bl_label = "Add Work Schedule"

    def execute(self, context):
        ifcopenshell.api.run("sequence.add_work_schedule", IfcStore.get_file())
        Data.load(IfcStore.get_file())
        return {"FINISHED"}


class EditWorkSchedule(bpy.types.Operator):
    bl_idname = "bim.edit_work_schedule"
    bl_label = "Edit Work Schedule"

    def execute(self, context):
        props = context.scene.BIMWorkScheduleProperties
        attributes = {}
        for attribute in props.work_schedule_attributes:
            if attribute.is_null:
                attributes[attribute.name] = None
            else:
                if attribute.data_type == "string":
                    attributes[attribute.name] = attribute.string_value
                elif attribute.data_type == "enum":
                    attributes[attribute.name] = attribute.enum_value
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "sequence.edit_work_schedule",
            self.file,
            **{"work_schedule": self.file.by_id(props.active_work_schedule_id), "attributes": attributes}
        )
        Data.load(IfcStore.get_file())
        bpy.ops.bim.disable_editing_work_schedule()
        return {"FINISHED"}


class RemoveWorkSchedule(bpy.types.Operator):
    bl_idname = "bim.remove_work_schedule"
    bl_label = "Remove Work Schedule"
    work_schedule: bpy.props.IntProperty()

    def execute(self, context):
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "sequence.remove_work_schedule", self.file, work_schedule=self.file.by_id(self.work_schedule)
        )
        Data.load(self.file)
        return {"FINISHED"}


class EnableEditingWorkSchedule(bpy.types.Operator):
    bl_idname = "bim.enable_editing_work_schedule"
    bl_label = "Enable Editing Work Schedule"
    work_schedule: bpy.props.IntProperty()

    def execute(self, context):
        self.props = context.scene.BIMWorkScheduleProperties
        self.props.active_work_schedule_id = self.work_schedule
        while len(self.props.work_schedule_attributes) > 0:
            self.props.work_schedule_attributes.remove(0)
        self.enable_editing_work_schedule()
        self.props.is_editing = "WORK_SCHEDULE"
        return {"FINISHED"}

    def enable_editing_work_schedule(self):
        data = Data.work_schedules[self.work_schedule]

        for attribute in IfcStore.get_schema().declaration_by_name("IfcWorkSchedule").all_attributes():
            data_type = ifcopenshell.util.attribute.get_primitive_type(attribute)
            if data_type == "entity":
                continue
            new = self.props.work_schedule_attributes.add()
            new.name = attribute.name()
            new.is_null = data[attribute.name()] is None
            new.is_optional = attribute.optional()
            new.data_type = data_type
            if attribute.name() in ["CreationDate", "StartTime", "FinishTime"]:
                new.string_value = "" if new.is_null else data[attribute.name()].isoformat()
            elif data_type == "string":
                new.string_value = "" if new.is_null else data[attribute.name()]
            elif data_type == "enum":
                new.enum_items = json.dumps(ifcopenshell.util.attribute.get_enum_items(attribute))
                if data[attribute.name()]:
                    new.enum_value = data[attribute.name()]


class EnableEditingTasks(bpy.types.Operator):
    bl_idname = "bim.enable_editing_tasks"
    bl_label = "Enable Editing Tasks"
    work_schedule: bpy.props.IntProperty()

    def execute(self, context):
        self.props = context.scene.BIMWorkScheduleProperties
        self.props.active_work_schedule_id = self.work_schedule
        while len(self.props.tasks) > 0:
            self.props.tasks.remove(0)

        self.contracted_tasks = json.loads(self.props.contracted_tasks)
        for related_object_id in Data.work_schedules[self.work_schedule]["RelatedObjects"]:
            self.create_new_task_li(related_object_id, 0)
        self.props.is_editing = "TASKS"
        return {"FINISHED"}

    def create_new_task_li(self, related_object_id, level_index):
        task = Data.tasks[related_object_id]
        new = self.props.tasks.add()
        new.ifc_definition_id = related_object_id
        new.name = task["Name"] or "Unnamed"
        new.identification = task["Identification"] or "X"
        if task["TaskTime"]:
            task_time = Data.task_times[task["TaskTime"]]
            new.start = self.canonicalise_time(task_time["ScheduleStart"])
            new.finish = self.canonicalise_time(task_time["ScheduleFinish"])
            # TODO: duration
            new.duration = "-"
        else:
            new.start = "-"
            new.finish = "-"
            new.duration = "-"
        new.is_expanded = related_object_id not in self.contracted_tasks
        new.level_index = level_index
        if task["RelatedObjects"]:
            new.has_children = True
            if new.is_expanded:
                for related_object_id in task["RelatedObjects"]:
                    self.create_new_task_li(related_object_id, level_index + 1)

    def canonicalise_time(self, time):
        if not time:
            return "-"
        return time.strftime("%d/%m/%y")


class DisableEditingWorkSchedule(bpy.types.Operator):
    bl_idname = "bim.disable_editing_work_schedule"
    bl_label = "Disable Editing Work Schedule"

    def execute(self, context):
        context.scene.BIMWorkScheduleProperties.active_work_schedule_id = 0
        return {"FINISHED"}


class LoadWorkCalendars(bpy.types.Operator):
    bl_idname = "bim.load_work_calendars"
    bl_label = "Load Work Calendars"

    def execute(self, context):
        props = context.scene.BIMWorkCalendarProperties
        while len(props.work_calendars) > 0:
            props.work_calendars.remove(0)
        for ifc_definition_id, work_calendar in Data.work_calendars.items():
            new = props.work_calendars.add()
            new.ifc_definition_id = ifc_definition_id
            new.name = work_calendar["Name"] or "Unnamed"
        props.is_editing = True
        bpy.ops.bim.disable_editing_work_calendar()
        return {"FINISHED"}


class DisableWorkCalendarEditingUI(bpy.types.Operator):
    bl_idname = "bim.disable_work_calendar_editing_ui"
    bl_label = "Disable WorkCalendar Editing UI"

    def execute(self, context):
        context.scene.BIMWorkCalendarProperties.is_editing = False
        return {"FINISHED"}


class AddWorkCalendar(bpy.types.Operator):
    bl_idname = "bim.add_work_calendar"
    bl_label = "Add Work Calendar"

    def execute(self, context):
        ifcopenshell.api.run("sequence.add_work_calendar", IfcStore.get_file())
        Data.load(IfcStore.get_file())
        bpy.ops.bim.load_work_calendars()
        return {"FINISHED"}


class EditWorkCalendar(bpy.types.Operator):
    bl_idname = "bim.edit_work_calendar"
    bl_label = "Edit Work Calendar"

    def execute(self, context):
        props = context.scene.BIMWorkCalendarProperties
        attributes = {}
        for attribute in props.work_calendar_attributes:
            if attribute.is_null:
                attributes[attribute.name] = None
            else:
                if attribute.data_type == "string":
                    attributes[attribute.name] = attribute.string_value
                elif attribute.data_type == "enum":
                    attributes[attribute.name] = attribute.enum_value
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "sequence.edit_work_calendar",
            self.file,
            **{"work_calendar": self.file.by_id(props.active_work_calendar_id), "attributes": attributes}
        )
        Data.load(IfcStore.get_file())
        bpy.ops.bim.load_work_calendars()
        return {"FINISHED"}


class RemoveWorkCalendar(bpy.types.Operator):
    bl_idname = "bim.remove_work_calendar"
    bl_label = "Remove Work Plan"
    work_calendar: bpy.props.IntProperty()

    def execute(self, context):
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "sequence.remove_work_calendar", self.file, **{"work_calendar": self.file.by_id(self.work_calendar)}
        )
        Data.load(self.file)
        bpy.ops.bim.load_work_calendars()
        return {"FINISHED"}


class EnableEditingWorkCalendar(bpy.types.Operator):
    bl_idname = "bim.enable_editing_work_calendar"
    bl_label = "Enable Editing Work Plan"
    work_calendar: bpy.props.IntProperty()

    def execute(self, context):
        props = context.scene.BIMWorkCalendarProperties
        while len(props.work_calendar_attributes) > 0:
            props.work_calendar_attributes.remove(0)

        data = Data.work_calendars[self.work_calendar]

        for attribute in IfcStore.get_schema().declaration_by_name("IfcWorkCalendar").all_attributes():
            data_type = ifcopenshell.util.attribute.get_primitive_type(attribute)
            if data_type == "entity":
                continue
            new = props.work_calendar_attributes.add()
            new.name = attribute.name()
            new.is_null = data[attribute.name()] is None
            new.is_optional = attribute.optional()
            new.data_type = data_type
            if data_type == "string":
                new.string_value = "" if new.is_null else data[attribute.name()]
            elif data_type == "enum":
                new.enum_items = json.dumps(ifcopenshell.util.attribute.get_enum_items(attribute))
                if data[attribute.name()]:
                    new.enum_value = data[attribute.name()]
        props.active_work_calendar_id = self.work_calendar
        return {"FINISHED"}


class DisableEditingWorkCalendar(bpy.types.Operator):
    bl_idname = "bim.disable_editing_work_calendar"
    bl_label = "Disable Editing Work Calendar"

    def execute(self, context):
        context.scene.BIMWorkCalendarProperties.active_work_calendar_id = 0
        return {"FINISHED"}


class LoadTasks(bpy.types.Operator):
    bl_idname = "bim.load_tasks"
    bl_label = "Load Tasks"
    work_schedule: bpy.props.IntProperty()

    def execute(self, context):
        props = context.scene.BIMWorkScheduleProperties
        while len(props.tasks) > 0:
            props.tasks.remove(0)
        for ifc_definition_id in Data.work_schedules[self.work_schedule]["RelatedObjects"]:
            task = Data.tasks[ifc_definition_id]
            new = props.tasks.add()
            new.ifc_definition_id = ifc_definition_id
            new.name = task["Name"] or "Unnamed"
            new.identification = task["Identification"]
        return {"FINISHED"}


class DisableTaskEditingUI(bpy.types.Operator):
    bl_idname = "bim.disable_task_editing_ui"
    bl_label = "Disable Task Editing UI"

    def execute(self, context):
        context.scene.BIMTaskProperties.is_editing = False
        return {"FINISHED"}


class AddTask(bpy.types.Operator):
    bl_idname = "bim.add_task"
    bl_label = "Add Task"
    task: bpy.props.IntProperty()

    def execute(self, context):
        props = context.scene.BIMWorkScheduleProperties
        self.file = IfcStore.get_file()
        ifcopenshell.api.run("sequence.add_task", self.file, **{"parent_task": self.file.by_id(self.task)})
        Data.load(self.file)
        bpy.ops.bim.enable_editing_tasks(work_schedule=props.active_work_schedule_id)
        return {"FINISHED"}


class AddSummaryTask(bpy.types.Operator):
    bl_idname = "bim.add_summary_task"
    bl_label = "Add Task"
    work_schedule: bpy.props.IntProperty()

    def execute(self, context):
        props = context.scene.BIMWorkScheduleProperties
        self.file = IfcStore.get_file()
        ifcopenshell.api.run("sequence.add_task", self.file, **{"work_schedule": self.file.by_id(self.work_schedule)})
        Data.load(self.file)
        bpy.ops.bim.enable_editing_tasks(work_schedule=props.active_work_schedule_id)
        return {"FINISHED"}


class ExpandTask(bpy.types.Operator):
    bl_idname = "bim.expand_task"
    bl_label = "Expand Task"
    task: bpy.props.IntProperty()

    def execute(self, context):
        props = context.scene.BIMWorkScheduleProperties
        self.file = IfcStore.get_file()
        contracted_tasks = json.loads(props.contracted_tasks)
        contracted_tasks.remove(self.task)
        props.contracted_tasks = json.dumps(contracted_tasks)
        Data.load(self.file)
        bpy.ops.bim.enable_editing_tasks(work_schedule=props.active_work_schedule_id)
        return {"FINISHED"}


class ContractTask(bpy.types.Operator):
    bl_idname = "bim.contract_task"
    bl_label = "Contract Task"
    task: bpy.props.IntProperty()

    def execute(self, context):
        props = context.scene.BIMWorkScheduleProperties
        self.file = IfcStore.get_file()
        contracted_tasks = json.loads(props.contracted_tasks)
        contracted_tasks.append(self.task)
        props.contracted_tasks = json.dumps(contracted_tasks)
        Data.load(self.file)
        bpy.ops.bim.enable_editing_tasks(work_schedule=props.active_work_schedule_id)
        return {"FINISHED"}


class RemoveTask(bpy.types.Operator):
    bl_idname = "bim.remove_task"
    bl_label = "Remove Task"
    task: bpy.props.IntProperty()

    def execute(self, context):
        props = context.scene.BIMWorkScheduleProperties
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "sequence.remove_task",
            self.file,
            task=IfcStore.get_file().by_id(self.task),
        )
        Data.load(self.file)
        bpy.ops.bim.enable_editing_tasks(work_schedule=props.active_work_schedule_id)
        return {"FINISHED"}


class EnableEditingTaskTime(bpy.types.Operator):
    bl_idname = "bim.enable_editing_task_time"
    bl_label = "Enable Editing Task"
    task: bpy.props.IntProperty()

    def execute(self, context):
        props = context.scene.BIMWorkScheduleProperties
        self.file = IfcStore.get_file()

        task_time_id = Data.tasks[self.task]["TaskTime"] or self.add_task_time().id()

        while len(props.task_time_attributes) > 0:
            props.task_time_attributes.remove(0)

        data = Data.task_times[task_time_id]

        for attribute in IfcStore.get_schema().declaration_by_name("IfcTaskTime").all_attributes():
            data_type = ifcopenshell.util.attribute.get_primitive_type(attribute)
            if data_type == "entity":
                continue
            new = props.task_time_attributes.add()
            new.name = attribute.name()
            new.is_null = data[attribute.name()] is None
            new.is_optional = attribute.optional()
            new.data_type = data_type
            if data_type == "string":
                if isinstance(data[attribute.name()], datetime):
                    new.string_value = "" if new.is_null else data[attribute.name()].isoformat()
                else:
                    new.string_value = "" if new.is_null else data[attribute.name()]
            elif data_type == "boolean":
                new.bool_value = False if new.is_null else data[attribute.name()]
            elif data_type == "float":
                new.float_value = 0.0 if new.is_null else data[attribute.name()]
            elif data_type == "enum":
                new.enum_items = json.dumps(ifcopenshell.util.attribute.get_enum_items(attribute))
                if data[attribute.name()]:
                    new.enum_value = data[attribute.name()]
        props.active_task_time_id = task_time_id
        props.active_task_id = self.task
        return {"FINISHED"}

    def add_task_time(self):
        task_time = ifcopenshell.api.run("sequence.add_task_time", self.file, task=self.file.by_id(self.task))
        Data.load(IfcStore.get_file())
        return task_time


class DisableEditingTaskTime(bpy.types.Operator):
    bl_idname = "bim.disable_editing_task_time"
    bl_label = "Disable Editing Task Time"

    def execute(self, context):
        context.scene.BIMWorkScheduleProperties.active_task_time_id = 0
        bpy.ops.bim.disable_editing_task()
        return {"FINISHED"}


class EditTaskTime(bpy.types.Operator):
    bl_idname = "bim.edit_task_time"
    bl_label = "Edit Task Time"

    def execute(self, context):
        props = context.scene.BIMWorkScheduleProperties
        attributes = {}
        for attribute in props.task_time_attributes:
            if attribute.is_null:
                attributes[attribute.name] = None
            else:
                if attribute.data_type == "string":
                    attributes[attribute.name] = attribute.string_value
                elif attribute.data_type == "boolean":
                    attributes[attribute.name] = attribute.bool_value
                elif attribute.data_type == "float":
                    attributes[attribute.name] = attribute.float_value
                elif attribute.data_type == "enum":
                    attributes[attribute.name] = attribute.enum_value

        attributes = self.convert_strings_to_date_times(attributes)

        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "sequence.edit_task_time",
            self.file,
            **{"task_time": self.file.by_id(props.active_task_time_id), "attributes": attributes}
        )
        Data.load(IfcStore.get_file())
        bpy.ops.bim.disable_editing_task_time()
        bpy.ops.bim.enable_editing_tasks(work_schedule=props.active_work_schedule_id)
        return {"FINISHED"}

    def convert_strings_to_date_times(self, attributes):
        for key, value in attributes.items():
            if not value:
                continue
            if "Start" in key or "Finish" in key or key == "StatusTime":
                try:
                    attributes[key] = parser.isoparse(value)
                except:
                    try:
                        attributes[key] = parser.parse(value, dayfirst=True, fuzzy=True)
                    except:
                        attributes[key] = None
        return attributes


class EnableEditingTask(bpy.types.Operator):
    bl_idname = "bim.enable_editing_task"
    bl_label = "Enable Editing Task"
    task: bpy.props.IntProperty()

    def execute(self, context):
        props = context.scene.BIMWorkScheduleProperties
        while len(props.task_attributes) > 0:
            props.task_attributes.remove(0)

        data = Data.tasks[self.task]

        for attribute in IfcStore.get_schema().declaration_by_name("IfcTask").all_attributes():
            data_type = ifcopenshell.util.attribute.get_primitive_type(attribute)
            if data_type == "entity":
                continue
            new = props.task_attributes.add()
            new.name = attribute.name()
            new.is_null = data[attribute.name()] is None
            new.is_optional = attribute.optional()
            new.data_type = data_type
            if data_type == "string":
                new.string_value = "" if new.is_null else data[attribute.name()]
            elif data_type == "boolean":
                new.bool_value = False if new.is_null else data[attribute.name()]
            elif data_type == "integer":
                new.int_value = 0 if new.is_null else data[attribute.name()]
            elif data_type == "enum":
                new.enum_items = json.dumps(ifcopenshell.util.attribute.get_enum_items(attribute))
                if data[attribute.name()]:
                    new.enum_value = data[attribute.name()]
        props.active_task_id = self.task
        props.should_show_times = True
        return {"FINISHED"}


class DisableEditingTask(bpy.types.Operator):
    bl_idname = "bim.disable_editing_task"
    bl_label = "Disable Editing Task"

    def execute(self, context):
        context.scene.BIMWorkScheduleProperties.active_task_id = 0
        return {"FINISHED"}


class EditTask(bpy.types.Operator):
    bl_idname = "bim.edit_task"
    bl_label = "Edit Task"

    def execute(self, context):
        props = context.scene.BIMWorkScheduleProperties
        attributes = {}
        for attribute in props.task_attributes:
            if attribute.is_null:
                attributes[attribute.name] = None
            else:
                if attribute.data_type == "string":
                    attributes[attribute.name] = attribute.string_value
                elif attribute.data_type == "boolean":
                    attributes[attribute.name] = attribute.bool_value
                elif attribute.data_type == "integer":
                    attributes[attribute.name] = attribute.int_value
                elif attribute.data_type == "enum":
                    attributes[attribute.name] = attribute.enum_value
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "sequence.edit_task",
            self.file,
            **{"task": self.file.by_id(props.active_task_id), "attributes": attributes}
        )
        Data.load(IfcStore.get_file())
        bpy.ops.bim.disable_editing_task()
        bpy.ops.bim.enable_editing_tasks(work_schedule=props.active_work_schedule_id)
        return {"FINISHED"}


class AssignPredecessor(bpy.types.Operator):
    bl_idname = "bim.assign_predecessor"
    bl_label = "Assign Predecessor"
    task: bpy.props.IntProperty()

    def execute(self, context):
        props = context.scene.BIMWorkScheduleProperties
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "sequence.assign_sequence",
            self.file,
            relating_process=IfcStore.get_file().by_id(self.task),
            related_process=IfcStore.get_file().by_id(props.active_task_id),
        )
        Data.load(self.file)
        return {"FINISHED"}


class AssignSuccessor(bpy.types.Operator):
    bl_idname = "bim.assign_successor"
    bl_label = "Assign Successor"
    task: bpy.props.IntProperty()

    def execute(self, context):
        props = context.scene.BIMWorkScheduleProperties
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "sequence.assign_sequence",
            self.file,
            relating_process=IfcStore.get_file().by_id(props.active_task_id),
            related_process=IfcStore.get_file().by_id(self.task),
        )
        Data.load(self.file)
        return {"FINISHED"}


class UnassignPredecessor(bpy.types.Operator):
    bl_idname = "bim.unassign_predecessor"
    bl_label = "Unassign Predecessor"
    task: bpy.props.IntProperty()

    def execute(self, context):
        props = context.scene.BIMWorkScheduleProperties
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "sequence.unassign_sequence",
            self.file,
            relating_process=IfcStore.get_file().by_id(self.task),
            related_process=IfcStore.get_file().by_id(props.active_task_id),
        )
        Data.load(self.file)
        return {"FINISHED"}


class UnassignSuccessor(bpy.types.Operator):
    bl_idname = "bim.unassign_successor"
    bl_label = "Unassign Successor"
    task: bpy.props.IntProperty()

    def execute(self, context):
        props = context.scene.BIMWorkScheduleProperties
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "sequence.unassign_sequence",
            self.file,
            relating_process=self.file.by_id(props.active_task_id),
            related_process=self.file.by_id(self.task),
        )
        Data.load(self.file)
        return {"FINISHED"}


class AssignProduct(bpy.types.Operator):
    bl_idname = "bim.assign_product"
    bl_label = "Assign Product"
    task: bpy.props.IntProperty()

    def execute(self, context):
        obj = bpy.context.active_object.BIMObjectProperties.ifc_definition_id
        props = context.scene.BIMWorkScheduleProperties
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "sequence.assign_product",
            self.file,
            relating_product = self.file.by_id(obj),
            related_process = self.file.by_id(self.task),
        )
        props.has_assignment = True
        Data.load(self.file)
        return {"FINISHED"}
