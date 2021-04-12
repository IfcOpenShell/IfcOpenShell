import bpy
import json
import ifcopenshell.api
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


class LoadWorkSchedules(bpy.types.Operator):
    bl_idname = "bim.load_work_schedules"
    bl_label = "Load Work Schedules"

    def execute(self, context):
        props = context.scene.BIMWorkScheduleProperties
        while len(props.work_schedules) > 0:
            props.work_schedules.remove(0)
        for ifc_definition_id, work_schedule in Data.work_schedules.items():
            new = props.work_schedules.add()
            new.ifc_definition_id = ifc_definition_id
            new.name = work_schedule["Name"] or "Unnamed"
        props.is_editing = True
        bpy.ops.bim.disable_editing_work_schedule()
        return {"FINISHED"}


class DisableWorkScheduleEditingUI(bpy.types.Operator):
    bl_idname = "bim.disable_work_schedule_editing_ui"
    bl_label = "Disable WorkSchedule Editing UI"

    def execute(self, context):
        context.scene.BIMWorkScheduleProperties.is_editing = False
        return {"FINISHED"}


class AddWorkSchedule(bpy.types.Operator):
    bl_idname = "bim.add_work_schedule"
    bl_label = "Add Work Schedule"

    def execute(self, context):
        ifcopenshell.api.run("sequence.add_work_schedule", IfcStore.get_file())
        Data.load(IfcStore.get_file())
        bpy.ops.bim.load_work_schedules()
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
        bpy.ops.bim.load_work_schedules()
        return {"FINISHED"}


class RemoveWorkSchedule(bpy.types.Operator):
    bl_idname = "bim.remove_work_schedule"
    bl_label = "Remove Work Schedule"
    work_schedule: bpy.props.IntProperty()

    def execute(self, context):
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "sequence.remove_work_schedule", self.file, **{"work_schedule": self.file.by_id(self.work_schedule)}
        )
        Data.load(self.file)
        bpy.ops.bim.load_work_schedules()
        return {"FINISHED"}


class EnableEditingWorkSchedule(bpy.types.Operator):
    bl_idname = "bim.enable_editing_work_schedule"
    bl_label = "Enable Editing Work Schedule"
    work_schedule: bpy.props.IntProperty()

    def execute(self, context):
        props = context.scene.BIMWorkScheduleProperties
        while len(props.work_schedule_attributes) > 0:
            props.work_schedule_attributes.remove(0)

        data = Data.work_schedules[self.work_schedule]

        for attribute in IfcStore.get_schema().declaration_by_name("IfcWorkSchedule").all_attributes():
            data_type = ifcopenshell.util.attribute.get_primitive_type(attribute)
            if data_type == "entity":
                continue
            new = props.work_schedule_attributes.add()
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
        props.active_work_schedule_id = self.work_schedule
        return {"FINISHED"}


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

    def execute(self, context):
        props = context.scene.BIMTaskProperties
        while len(props.tasks) > 0:
            props.tasks.remove(0)
        for ifc_definition_id, task in Data.tasks.items():
            new = props.tasks.add()
            new.ifc_definition_id = ifc_definition_id
            new.name = task["Name"]
            new.identification = task["Identification"]
        props.is_editing = True
        return {"FINISHED"}


class DisableTaskEditingUI(bpy.types.Operator):
    bl_idname = "bim.disable_task_editing_ui"
    bl_label = "Disable Task Editing UI"

    def execute(self, context):
        context.scene.BIMTaskProperties.is_editing = False
        return {"FINISHED"}
