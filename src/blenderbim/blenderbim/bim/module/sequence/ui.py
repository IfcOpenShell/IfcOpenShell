from bpy.types import Panel, UIList
from blenderbim.bim.ifc import IfcStore
from ifcopenshell.api.sequence.data import Data


class BIM_PT_work_plans(Panel):
    bl_label = "IFC Work Plans"
    bl_idname = "BIM_PT_work_plans"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"

    @classmethod
    def poll(cls, context):
        return IfcStore.get_file()

    def draw(self, context):
        if not Data.is_loaded:
            Data.load(IfcStore.get_file())
        self.props = context.scene.BIMWorkPlanProperties

        row = self.layout.row()
        row.operator("bim.add_work_plan", icon="ADD")

        for work_plan_id, work_plan in Data.work_plans.items():
            self.draw_work_plan_ui(work_plan_id, work_plan)

    def draw_work_plan_ui(self, work_plan_id, work_plan):
        row = self.layout.row(align=True)
        row.label(text=work_plan["Name"] or "Unnamed", icon="TEXT")

        if self.props.active_work_plan_id == work_plan_id:
            row.operator("bim.edit_work_plan", text="", icon="CHECKMARK")
            row.operator("bim.disable_editing_work_plan", text="", icon="CANCEL")
        elif self.props.active_work_plan_id:
            row.operator("bim.remove_work_plan", text="", icon="X").work_plan = work_plan_id
        else:
            op = row.operator("bim.enable_editing_work_plan_schedules", text="", icon="LINENUMBERS_ON")
            op.work_plan = work_plan_id
            op = row.operator("bim.enable_editing_work_plan", text="", icon="GREASEPENCIL")
            op.work_plan = work_plan_id
            row.operator("bim.remove_work_plan", text="", icon="X").work_plan = work_plan_id

        if self.props.active_work_plan_id == work_plan_id:
            if self.props.is_editing == "ATTRIBUTES":
                self.draw_editable_ui()
            elif self.props.is_editing == "SCHEDULES":
                self.draw_work_schedule_ui()

    def draw_editable_ui(self):
        for attribute in self.props.work_plan_attributes:
            row = self.layout.row(align=True)
            if attribute.data_type == "string":
                row.prop(attribute, "string_value", text=attribute.name)
            elif attribute.data_type == "enum":
                row.prop(attribute, "enum_value", text=attribute.name)
            if attribute.is_optional:
                row.prop(attribute, "is_null", icon="RADIOBUT_OFF" if attribute.is_null else "RADIOBUT_ON", text="")

    def draw_work_schedule_ui(self):
        row = self.layout.row(align=True)
        row.prop(self.props, "work_schedules", text="")
        op = row.operator("bim.assign_work_schedule", text="", icon="ADD")
        op.work_plan = self.props.active_work_plan_id
        op.work_schedule = int(self.props.work_schedules)

        for work_schedule_id in Data.work_plans[self.props.active_work_plan_id]["IsDecomposedBy"]:
            work_schedule = Data.work_schedules[work_schedule_id]
            row = self.layout.row(align=True)
            row.label(text=work_schedule["Name"] or "Unnamed", icon="LINENUMBERS_ON")
            op = row.operator("bim.unassign_work_schedule", text="", icon="X")
            op.work_plan = self.props.active_work_plan_id
            op.work_schedule = int(self.props.work_schedules)


class BIM_PT_work_schedules(Panel):
    bl_label = "IFC Work Schedules"
    bl_idname = "BIM_PT_work_schedules"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"

    @classmethod
    def poll(cls, context):
        return IfcStore.get_file()

    def draw(self, context):
        self.props = context.scene.BIMWorkScheduleProperties
        self.tprops = context.scene.BIMTaskTreeProperties

        if not Data.is_loaded:
            Data.load(IfcStore.get_file())

        row = self.layout.row()
        row.operator("bim.add_work_schedule", icon="ADD")

        for work_schedule_id, work_schedule in Data.work_schedules.items():
            self.draw_work_schedule_ui(work_schedule_id, work_schedule)

    def draw_work_schedule_ui(self, work_schedule_id, work_schedule):
        row = self.layout.row(align=True)
        row.label(text=work_schedule["Name"] or "Unnamed", icon="LINENUMBERS_ON")

        if self.props.active_work_schedule_id and self.props.active_work_schedule_id == work_schedule_id:
            if self.props.is_editing == "WORK_SCHEDULE":
                row.operator("bim.edit_work_schedule", text="", icon="CHECKMARK")
            elif self.props.is_editing == "TASKS":
                row.prop(self.props, "should_show_times", text="", icon="TIME")
                row.operator("bim.generate_gantt_chart", text="", icon="NLA").work_schedule = work_schedule_id
                row.operator("bim.add_summary_task", text="", icon="ADD").work_schedule = work_schedule_id
            row.operator("bim.disable_editing_work_schedule", text="", icon="CANCEL")
        elif self.props.active_work_schedule_id:
            row.operator("bim.remove_work_schedule", text="", icon="X").work_schedule = work_schedule_id
        else:
            row.operator("bim.enable_editing_tasks", text="", icon="ACTION").work_schedule = work_schedule_id
            row.operator(
                "bim.enable_editing_work_schedule", text="", icon="GREASEPENCIL"
            ).work_schedule = work_schedule_id
            row.operator("bim.remove_work_schedule", text="", icon="X").work_schedule = work_schedule_id

        if self.props.active_work_schedule_id == work_schedule_id:
            if self.props.is_editing == "WORK_SCHEDULE":
                self.draw_editable_work_schedule_ui()
            elif self.props.is_editing == "TASKS":
                self.draw_editable_task_ui(work_schedule_id)

    def draw_editable_work_schedule_ui(self):
        for attribute in self.props.work_schedule_attributes:
            row = self.layout.row(align=True)
            if attribute.data_type == "string":
                row.prop(attribute, "string_value", text=attribute.name)
            elif attribute.data_type == "enum":
                row.prop(attribute, "enum_value", text=attribute.name)
            if attribute.is_optional:
                row.prop(attribute, "is_null", icon="RADIOBUT_OFF" if attribute.is_null else "RADIOBUT_ON", text="")

    def draw_editable_task_ui(self, work_schedule_id):
        self.layout.template_list(
            "BIM_UL_tasks",
            "",
            self.tprops,
            "tasks",
            self.props,
            "active_task_index",
        )
        if self.props.active_task_id:
            self.draw_editable_task_attributes_ui()
        if self.props.active_task_time_id:
            self.draw_editable_task_time_attributes_ui()

    def draw_editable_task_attributes_ui(self):
        for attribute in self.props.task_attributes:
            row = self.layout.row(align=True)
            if attribute.data_type == "string":
                row.prop(attribute, "string_value", text=attribute.name)
            elif attribute.data_type == "boolean":
                row.prop(attribute, "bool_value", text=attribute.name)
            elif attribute.data_type == "integer":
                row.prop(attribute, "int_value", text=attribute.name)
            elif attribute.data_type == "enum":
                row.prop(attribute, "enum_value", text=attribute.name)
            if attribute.is_optional:
                row.prop(attribute, "is_null", icon="RADIOBUT_OFF" if attribute.is_null else "RADIOBUT_ON", text="")

    def draw_editable_task_time_attributes_ui(self):
        for attribute in self.props.task_time_attributes:
            row = self.layout.row(align=True)
            if attribute.data_type == "string":
                row.prop(attribute, "string_value", text=attribute.name)
            elif attribute.data_type == "boolean":
                row.prop(attribute, "bool_value", text=attribute.name)
            elif attribute.data_type == "integer":
                row.prop(attribute, "int_value", text=attribute.name)
            elif attribute.data_type == "float":
                row.prop(attribute, "float_value", text=attribute.name)
            elif attribute.data_type == "enum":
                row.prop(attribute, "enum_value", text=attribute.name)
            if attribute.is_optional:
                row.prop(attribute, "is_null", icon="RADIOBUT_OFF" if attribute.is_null else "RADIOBUT_ON", text="")


class BIM_UL_tasks(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if item:
            props = context.scene.BIMWorkScheduleProperties
            row = layout.row(align=True)
            for i in range(0, item.level_index):
                row.label(text="", icon="BLANK1")
            if item.has_children:
                if item.is_expanded:
                    row.operator(
                        "bim.contract_task", text="", emboss=False, icon="DISCLOSURE_TRI_DOWN"
                    ).task = item.ifc_definition_id
                else:
                    row.operator(
                        "bim.expand_task", text="", emboss=False, icon="DISCLOSURE_TRI_RIGHT"
                    ).task = item.ifc_definition_id
            else:
                row.label(text="", icon="DOT")
            row.prop(item, "identification", emboss=False, text="")
            row.prop(item, "name", emboss=False, text="")

            if props.should_show_times:
                row.prop(item, "start", emboss=False, text="")
                row.prop(item, "finish", emboss=False, text="")
                row.prop(item, "duration", emboss=False, text="")

            if context.active_object:
                oprops = context.active_object.BIMObjectProperties
                row = layout.row(align=True)
                if oprops.ifc_definition_id in Data.tasks[item.ifc_definition_id]["RelatingProducts"]:
                    op = row.operator("bim.unassign_product", text="", icon="KEYFRAME_HLT", emboss=False)
                    op.task = item.ifc_definition_id
                else:
                    op = row.operator("bim.assign_product", text="", icon="KEYFRAME", emboss=False)
                    op.task = item.ifc_definition_id

            if props.active_task_id == item.ifc_definition_id:
                if props.active_task_time_id:
                    row.operator("bim.edit_task_time", text="", icon="CHECKMARK")
                else:
                    row.operator("bim.edit_task", text="", icon="CHECKMARK")
                row.operator("bim.disable_editing_task", text="", icon="CANCEL")
            elif props.active_task_id:
                if item.is_predecessor:
                    row.operator(
                        "bim.unassign_predecessor", text="", icon="BACK", emboss=False
                    ).task = item.ifc_definition_id
                else:
                    row.operator(
                        "bim.assign_predecessor", text="", icon="TRACKING_BACKWARDS", emboss=False
                    ).task = item.ifc_definition_id

                if item.is_successor:
                    row.operator(
                        "bim.unassign_successor", text="", icon="FORWARD", emboss=False
                    ).task = item.ifc_definition_id
                else:
                    row.operator(
                        "bim.assign_successor", text="", icon="TRACKING_FORWARDS", emboss=False
                    ).task = item.ifc_definition_id

                row.operator("bim.add_task", text="", icon="ADD").task = item.ifc_definition_id
                row.operator("bim.remove_task", text="", icon="X").task = item.ifc_definition_id
            else:
                row.operator("bim.enable_editing_task_time", text="", icon="TIME").task = item.ifc_definition_id
                row.operator("bim.enable_editing_task", text="", icon="GREASEPENCIL").task = item.ifc_definition_id
                row.operator("bim.add_task", text="", icon="ADD").task = item.ifc_definition_id
                row.operator("bim.remove_task", text="", icon="X").task = item.ifc_definition_id


class BIM_PT_work_calendars(Panel):
    bl_label = "IFC Work Calendars"
    bl_idname = "BIM_PT_work_calendars"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"

    @classmethod
    def poll(cls, context):
        return IfcStore.get_file()

    def draw(self, context):
        if not Data.is_loaded:
            Data.load(IfcStore.get_file())
        self.props = context.scene.BIMWorkCalendarProperties

        row = self.layout.row()
        row.operator("bim.add_work_calendar", icon="ADD")

        for work_calendar_id, work_calendar in Data.work_calendars.items():
            self.draw_work_calendar_ui(work_calendar_id, work_calendar)

    def draw_work_calendar_ui(self, work_calendar_id, work_calendar):
        row = self.layout.row(align=True)
        row.label(text=work_calendar["Name"] or "Unnamed", icon="VIEW_ORTHO")
        if self.props.active_work_calendar_id == work_calendar_id:
            row.operator("bim.edit_work_calendar", text="", icon="CHECKMARK")
            row.operator("bim.disable_editing_work_calendar", text="", icon="CANCEL")
        elif self.props.active_work_calendar_id:
            row.operator("bim.remove_work_calendar", text="", icon="X").work_calendar = work_calendar_id
        else:
            op = row.operator("bim.enable_editing_work_calendar_times", text="", icon="MESH_GRID")
            op.work_calendar = work_calendar_id
            op = row.operator("bim.enable_editing_work_calendar", text="", icon="GREASEPENCIL")
            op.work_calendar = work_calendar_id
            row.operator("bim.remove_work_calendar", text="", icon="X").work_calendar = work_calendar_id

        if self.props.active_work_calendar_id == work_calendar_id:
            if self.props.is_editing == "ATTRIBUTES":
                self.draw_editable_ui()
            elif self.props.is_editing == "WORKTIMES":
                self.draw_work_times_ui(work_calendar_id, work_calendar)

    def draw_work_times_ui(self, work_calendar_id, work_calendar):
        row = self.layout.row(align=True)
        op = row.operator("bim.add_work_time", text="Add Work Time", icon="ADD")
        op.work_calendar = work_calendar_id
        op.time_type = "WorkingTimes"
        op = row.operator("bim.add_work_time", text="Add Exception Time", icon="ADD")
        op.work_calendar = work_calendar_id
        op.time_type = "ExceptionTimes"

        for work_time_id in work_calendar["WorkingTimes"]:
            self.draw_work_time_ui(Data.work_times[work_time_id], time_type="WorkingTimes")

        for work_time_id in work_calendar["ExceptionTimes"]:
            self.draw_work_time_ui(Data.work_times[work_time_id], time_type="ExceptionTimes")

    def draw_work_time_ui(self, work_time, time_type):
        row = self.layout.row(align=True)
        row.label(
            text=work_time["Name"] or "Unnamed", icon="MESH_GRID" if time_type == "WorkingTimes" else "LIGHTPROBE_GRID"
        )
        if work_time["Start"] or work_time["Finish"]:
            row.label(text="{} - {}".format(work_time["Start"] or "*", work_time["Finish"] or "*"))
        if self.props.active_work_time_id == work_time["id"]:
            row.operator("bim.edit_work_time", text="", icon="CHECKMARK")
            row.operator("bim.disable_editing_work_time", text="", icon="CANCEL")
        elif self.props.active_work_time_id:
            op = row.operator("bim.remove_work_time", text="", icon="X")
            op.work_time = work_time["id"]
        else:
            op = row.operator("bim.enable_editing_work_time", text="", icon="GREASEPENCIL")
            op.work_time = work_time["id"]
            op = row.operator("bim.remove_work_time", text="", icon="X")
            op.work_time = work_time["id"]

        if self.props.active_work_time_id == work_time["id"]:
            self.draw_editable_work_time_ui(work_time)

    def draw_editable_work_time_ui(self, work_time):
        for attribute in self.props.work_time_attributes:
            row = self.layout.row(align=True)
            if attribute.data_type == "string":
                row.prop(attribute, "string_value", text=attribute.name)
            elif attribute.data_type == "enum":
                row.prop(attribute, "enum_value", text=attribute.name)
            if attribute.is_optional:
                row.prop(attribute, "is_null", icon="RADIOBUT_OFF" if attribute.is_null else "RADIOBUT_ON", text="")

        if work_time["RecurrencePattern"]:
            self.draw_editable_recurrence_pattern_ui(Data.recurrence_patterns[work_time["RecurrencePattern"]])
        else:
            row = self.layout.row(align=True)
            row.prop(self.props, "recurrence_types", icon="RECOVER_LAST", text="")
            op = row.operator("bim.assign_recurrence_pattern", icon="ADD", text="")
            op.work_time = work_time["id"]
            op.recurrence_type = self.props.recurrence_types

    def draw_editable_recurrence_pattern_ui(self, recurrence_pattern):
        box = self.layout.box()
        row = box.row(align=True)
        row.label(text=recurrence_pattern["RecurrenceType"], icon="RECOVER_LAST")
        op = row.operator("bim.unassign_recurrence_pattern", text="", icon="X")
        op.recurrence_pattern = recurrence_pattern["id"]

        row = box.row(align=True)
        row.prop(self.props, "start_time", text="")
        row.prop(self.props, "end_time", text="")
        op = row.operator("bim.add_time_period", text="", icon="ADD")
        op.recurrence_pattern = recurrence_pattern["id"]

        for time_period_id in recurrence_pattern["TimePeriods"]:
            time_period = Data.time_periods[time_period_id]
            row = box.row(align=True)
            row.label(text="{} - {}".format(time_period["StartTime"], time_period["EndTime"]), icon="TIME")
            op = row.operator("bim.remove_time_period", text="", icon="X")
            op.time_period = time_period_id

        applicable_data = {
            "DAILY": ["Interval", "Occurrences"],
            "WEEKLY": ["WeekdayComponent", "Interval", "Occurrences"],
            "MONTHLY_BY_DAY_OF_MONTH": ["DayComponent", "Interval", "Occurrences"],
            "MONTHLY_BY_POSITION": ["WeekdayComponent", "Position", "Interval", "Occurrences"],
            "BY_DAY_COUNT": ["Interval", "Occurrences"],
            "BY_WEEKDAY_COUNT": ["WeekdayComponent", "Interval", "Occurrences"],
            "YEARLY_BY_DAY_OF_MONTH": ["DayComponent", "MonthComponent", "Interval", "Occurrences"],
            "YEARLY_BY_POSITION": ["WeekdayComponent", "MonthComponent", "Position", "Interval", "Occurrences"],
        }

        if "Position" in applicable_data[recurrence_pattern["RecurrenceType"]]:
            row = box.row()
            row.prop(self.props, "position")

        if "DayComponent" in applicable_data[recurrence_pattern["RecurrenceType"]]:
            for i, component in enumerate(self.props.day_components):
                if i % 7 == 0:
                    row = box.row(align=True)
                row.prop(component, "is_specified", text=component.name)

        if "WeekdayComponent" in applicable_data[recurrence_pattern["RecurrenceType"]]:
            row = box.row(align=True)
            for component in self.props.weekday_components:
                row.prop(component, "is_specified", text=component.name)

        if "MonthComponent" in applicable_data[recurrence_pattern["RecurrenceType"]]:
            for i, component in enumerate(self.props.month_components):
                if i % 4 == 0:
                    row = box.row(align=True)
                row.prop(component, "is_specified", text=component.name)

        row = box.row()
        row.prop(self.props, "interval")
        row = box.row()
        row.prop(self.props, "occurrences")

    def draw_editable_ui(self):
        for attribute in self.props.work_calendar_attributes:
            row = self.layout.row(align=True)
            if attribute.data_type == "string":
                row.prop(attribute, "string_value", text=attribute.name)
            elif attribute.data_type == "enum":
                row.prop(attribute, "enum_value", text=attribute.name)
            if attribute.is_optional:
                row.prop(attribute, "is_null", icon="RADIOBUT_OFF" if attribute.is_null else "RADIOBUT_ON", text="")
