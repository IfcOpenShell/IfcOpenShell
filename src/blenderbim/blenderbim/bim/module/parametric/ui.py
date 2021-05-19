from bpy.types import Panel
from blenderbim.bim.ifc import IfcStore
from ifcopenshell.api.type.data import Data


class BIM_PT_parametric(Panel):
    bl_label = "IFC Parametric Engines"
    bl_idname = "BIM_PT_parametric"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"

    @classmethod
    def poll(cls, context):
        return IfcStore.get_file()

    def draw(self, context):
        #props = context.active_object.BIMTypeProperties
        row = self.layout.row(align=True)
        #row.prop(props, "relating_type_class", text="")
        row.operator("bim.activate_parametric_engine", icon="PLUGIN")
