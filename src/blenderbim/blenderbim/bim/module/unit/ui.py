import blenderbim.bim.helper
from bpy.types import Panel, UIList
from blenderbim.bim.ifc import IfcStore
from ifcopenshell.api.unit.data import Data


class BIM_PT_units(Panel):
    bl_label = "IFC Units"
    bl_idname = "BIM_PT_units"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"

    @classmethod
    def poll(cls, context):
        file = IfcStore.get_file()
        return file

    def draw(self, context):
        self.file = IfcStore.get_file()
        if not Data.is_loaded:
            Data.load(self.file)
        self.props = context.scene.BIMUnitProperties

        row = self.layout.row(align=True)
        row.label(text="{} Units Found".format(len(Data.unit_assignment)), icon="SNAP_GRID")
        if self.props.is_editing:
            row.operator("bim.add_group", text="", icon="ADD")
            row.operator("bim.disable_group_editing_ui", text="", icon="CANCEL")
        else:
            row.operator("bim.load_units", text="", icon="GREASEPENCIL")

        if self.props.is_editing:
            self.layout.template_list(
                "BIM_UL_units",
                "",
                self.props,
                "units",
                self.props,
                "active_unit_index",
            )


class BIM_UL_units(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        props = context.scene.BIMUnitProperties
        if item:
            row = layout.row(align=True)
            row.label(text=item.unit_type or "No Type", icon=item.icon)
            row.label(text=item.name or "Unnamed")
