from bpy.types import Panel, UIList
from blenderbim.bim.ifc import IfcStore
from ifcopenshell.api.cost.data import Data


class BIM_PT_cost_schedules(Panel):
    bl_label = "IFC Cost Schedules"
    bl_idname = "BIM_PT_cost_schedules"
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
        row.operator("bim.add_cost_schedule", icon="ADD")

        for cost_schedule_id, cost_schedule in Data.cost_schedules.items():
            row = self.layout.row(align=True)
            row.label(text=cost_schedule["Name"] or "Unnamed", icon="LINENUMBERS_ON")
            row.operator("bim.add_cost_schedule", text="", icon="GREASEPENCIL")
            row.operator("bim.remove_cost_schedule", text="", icon="X").cost_schedule = cost_schedule_id
