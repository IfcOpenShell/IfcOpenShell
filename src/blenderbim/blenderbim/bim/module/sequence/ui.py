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
        if not Data.is_loaded:
            Data.load(IfcStore.get_file())
        self.props = context.scene.BIMWorkScheduleProperties
        row = self.layout.row(align=True)
        row.label(text="{} Work Schedules Found".format(len(Data.work_schedules)), icon="TEXT")
        if self.props.is_editing:
            row.operator("bim.add_work_schedule", text="", icon="ADD")
            row.operator("bim.disable_work_schedule_editing_ui", text="", icon="CHECKMARK")
        else:
            row.operator("bim.load_work_schedules", text="", icon="GREASEPENCIL")

        if self.props.is_editing:
            self.layout.template_list(
                "BIM_UL_work_schedules",
                "",
                self.props,
                "work_schedules",
                self.props,
                "active_work_schedule_index",
            )

        if self.props.active_work_schedule_id:
            self.draw_editable_ui(context)

    def draw_editable_ui(self, context):
        for attribute in self.props.work_schedule_attributes:
            row = self.layout.row(align=True)
            if attribute.data_type == "string":
                row.prop(attribute, "string_value", text=attribute.name)
            elif attribute.data_type == "enum":
                row.prop(attribute, "enum_value", text=attribute.name)
            if attribute.is_optional:
                row.prop(attribute, "is_null", icon="RADIOBUT_OFF" if attribute.is_null else "RADIOBUT_ON", text="")


class BIM_UL_work_schedules(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if item:
            row = layout.row(align=True)
            row.label(text=item.name)
            if context.scene.BIMWorkScheduleProperties.active_work_schedule_id == item.ifc_definition_id:
                row.operator("bim.edit_work_schedule", text="", icon="CHECKMARK")
                row.operator("bim.disable_editing_work_schedule", text="", icon="X")
            elif context.scene.BIMWorkScheduleProperties.active_work_schedule_id:
                row.operator("bim.remove_work_schedule", text="", icon="X").work_schedule = item.ifc_definition_id
            else:
                op = row.operator("bim.enable_editing_work_schedule", text="", icon="GREASEPENCIL")
                op.work_schedule = item.ifc_definition_id
                row.operator("bim.remove_work_schedule", text="", icon="X").work_schedule = item.ifc_definition_id


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


class BIM_PT_tasks(Panel):
    bl_label = "IFC Tasks"
    bl_idname = "BIM_PT_tasks"
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
        self.props = context.scene.BIMTaskProperties

        row = self.layout.row(align=True)
        row.label(text="{} Tasks Found".format(len(Data.tasks)), icon="ACTION")
        if self.props.is_editing:
            row.operator("bim.disable_task_editing_ui", text="", icon="CHECKMARK")
        else:
            row.operator("bim.load_tasks", text="", icon="GREASEPENCIL")

        if self.props.is_editing:
            self.layout.template_list(
                "BIM_UL_tasks",
                "",
                self.props,
                "tasks",
                self.props,
                "active_task_index",
            )

        if self.props.active_task_index:
            self.draw_editable_ui(context)

    def draw_editable_ui(self, context):
        pass


class BIM_UL_tasks(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if item:
            row = layout.row(align=True)
            if item.identification:
                layout.label(text=item.identification)
            layout.label(text=item.name)
