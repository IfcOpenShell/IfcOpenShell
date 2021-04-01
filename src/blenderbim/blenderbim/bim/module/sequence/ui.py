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

        row = self.layout.row()
        row.operator("bim.add_work_plan", icon="ADD")

        for work_plan_id, work_plan in Data.work_plans.items():
            row = self.layout.row(align=True)
            row.label(text=work_plan["Name"] or "Unnamed", icon="TEXT")
            row.operator("bim.add_work_plan", text="", icon="GREASEPENCIL")
            row.operator("bim.remove_work_plan", text="", icon="X").work_plan = work_plan_id


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
