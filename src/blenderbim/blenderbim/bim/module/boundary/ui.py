import bpy
import blenderbim.bim.helper
from bpy.types import Panel, UIList
from blenderbim.bim.ifc import IfcStore
from ifcopenshell.api.boundary.data import Data


class BIM_PT_boundary(Panel):
    bl_label = "IFC Space Boundaries"
    bl_idname = "BIM_PT_boundary"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        if not context.active_object:
            return False
        props = context.active_object.BIMObjectProperties
        if not props.ifc_definition_id:
            return False
        if IfcStore.get_file().by_id(props.ifc_definition_id).is_a() not in ["IfcSpace", "IfcExternalSpatialElement"]:
            return False
        return True

    def draw(self, context):
        self.oprops = context.active_object.BIMObjectProperties
        if not Data.is_loaded:
            Data.load(IfcStore.get_file())
        for boundary_id in Data.spaces.get(self.oprops.ifc_definition_id, []):
            boundary = Data.boundaries[boundary_id]
            row = self.layout.row()
            row.label(text=f"{boundary_id}", icon="GHOST_ENABLED")
