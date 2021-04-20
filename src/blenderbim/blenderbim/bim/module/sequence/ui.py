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
        row = self.layout.row(align=True)
        row.label(text="{} Work Plans Found".format(len(Data.work_plans)), icon="TEXT")
        if self.props.is_editing:
            row.operator("bim.add_work_plan", text="", icon="ADD")
            row.operator("bim.disable_work_plan_editing_ui", text="", icon="CHECKMARK")
        else:
            row.operator("bim.load_work_plans", text="", icon="GREASEPENCIL")

        if self.props.is_editing:
            self.layout.template_list(
                "BIM_UL_work_plans",
                "",
                self.props,
                "work_plans",
                self.props,
                "active_work_plan_index",
            )

        if self.props.active_work_plan_id:
            self.draw_editable_ui(context)

    def draw_editable_ui(self, context):
        for attribute in self.props.work_plan_attributes:
            row = self.layout.row(align=True)
            if attribute.data_type == "string":
                row.prop(attribute, "string_value", text=attribute.name)
            elif attribute.data_type == "enum":
                row.prop(attribute, "enum_value", text=attribute.name)
            if attribute.is_optional:
                row.prop(attribute, "is_null", icon="RADIOBUT_OFF" if attribute.is_null else "RADIOBUT_ON", text="")


class BIM_UL_work_plans(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if item:
            row = layout.row(align=True)
            row.label(text=item.name)
            if context.scene.BIMWorkPlanProperties.active_work_plan_id == item.ifc_definition_id:
                row.operator("bim.edit_work_plan", text="", icon="CHECKMARK")
                row.operator("bim.disable_editing_work_plan", text="", icon="X")
            elif context.scene.BIMWorkPlanProperties.active_work_plan_id:
                row.operator("bim.remove_work_plan", text="", icon="X").work_plan = item.ifc_definition_id
            else:
                op = row.operator("bim.enable_editing_work_plan", text="", icon="GREASEPENCIL")
                op.work_plan = item.ifc_definition_id
                row.operator("bim.remove_work_plan", text="", icon="X").work_plan = item.ifc_definition_id


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

        if not Data.is_loaded:
            Data.load(IfcStore.get_file())

        row = self.layout.row()
        row.operator("bim.add_work_schedule", icon="ADD")

        for work_schedule_id, work_schedule in Data.work_schedules.items():
            self.draw_work_schedule_ui(work_schedule_id, work_schedule)

    def draw_work_schedule_ui(self, work_schedule_id, work_schedule):
        row = self.layout.row(align=True)
        row.label(text=work_schedule["Name"] or "Unnamed", icon="TEXT")

        if self.props.active_work_schedule_id and self.props.active_work_schedule_id == work_schedule_id:
            if self.props.is_editing == "WORK_SCHEDULE":
                row.operator("bim.edit_work_schedule", text="", icon="CHECKMARK")
            elif self.props.is_editing == "TASKS":
                row.prop(self.props, "should_show_times", text="", icon="TIME")
                row.operator("bim.add_summary_task", text="", icon="ADD").work_schedule = work_schedule_id
            row.operator("bim.disable_editing_work_schedule", text="", icon="CANCEL")
        elif self.props.active_work_schedule_id:
            row.operator("bim.remove_work_schedule", text="", icon="X").work_schedule = work_schedule_id
        else:
            row.operator("bim.enable_editing_tasks", text="", icon="ACTION").work_schedule = work_schedule_id
            op = row.operator("bim.enable_editing_work_schedule", text="", icon="GREASEPENCIL")
            op.work_schedule = work_schedule_id
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
            self.props,
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
        row = self.layout.row(align=True)
        row.label(text="{} Work Calendar Found".format(len(Data.work_calendars)), icon="TEXT")
        if self.props.is_editing:
            row.operator("bim.add_work_calendar", text="", icon="ADD")
            row.operator("bim.disable_work_calendar_editing_ui", text="", icon="CHECKMARK")
        else:
            row.operator("bim.load_work_calendars", text="", icon="GREASEPENCIL")

        if self.props.is_editing:
            self.layout.template_list(
                "BIM_UL_work_calendars",
                "",
                self.props,
                "work_calendars",
                self.props,
                "active_work_calendar_index",
            )

        if self.props.active_work_calendar_id:
            self.draw_editable_ui(context)

    def draw_editable_ui(self, context):
        for attribute in self.props.work_calendar_attributes:
            row = self.layout.row(align=True)
            if attribute.data_type == "string":
                row.prop(attribute, "string_value", text=attribute.name)
            elif attribute.data_type == "enum":
                row.prop(attribute, "enum_value", text=attribute.name)
            if attribute.is_optional:
                row.prop(attribute, "is_null", icon="RADIOBUT_OFF" if attribute.is_null else "RADIOBUT_ON", text="")


class BIM_UL_work_calendars(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if item:
            row = layout.row(align=True)
            row.label(text=item.name)
            if context.scene.BIMWorkCalendarProperties.active_work_calendar_id == item.ifc_definition_id:
                row.operator("bim.edit_work_calendar", text="", icon="CHECKMARK")
                row.operator("bim.disable_editing_work_calendar", text="", icon="X")
            elif context.scene.BIMWorkCalendarProperties.active_work_calendar_id:
                row.operator("bim.remove_work_calendar", text="", icon="X").work_calendar = item.ifc_definition_id
            else:
                op = row.operator("bim.enable_editing_work_calendar", text="", icon="GREASEPENCIL")
                op.work_calendar = item.ifc_definition_id
                row.operator("bim.remove_work_calendar", text="", icon="X").work_calendar = item.ifc_definition_id


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

            if props.active_task_id == item.ifc_definition_id:
                if props.active_task_time_id:
                    row.operator("bim.edit_task_time", text="", icon="CHECKMARK")
                else:
                    row.operator("bim.edit_task", text="", icon="CHECKMARK")
                row.operator("bim.disable_editing_task", text="", icon="CANCEL")
            elif props.active_task_id:
                if props.active_task_id in Data.tasks[item.ifc_definition_id]["IsPredecessorTo"]:
                    row.operator(
                        "bim.unassign_predecessor", text="", icon="BACK", emboss=False
                    ).task = item.ifc_definition_id
                else:
                    row.operator(
                        "bim.assign_predecessor", text="", icon="TRACKING_BACKWARDS", emboss=False
                    ).task = item.ifc_definition_id

                if props.active_task_id in Data.tasks[item.ifc_definition_id]["IsSuccessorFrom"]:
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
