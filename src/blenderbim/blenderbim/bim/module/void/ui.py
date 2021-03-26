import bpy
from bpy.types import Panel
from ifcopenshell.api.void.data import Data
from blenderbim.bim.ifc import IfcStore


class BIM_PT_voids(Panel):
    bl_label = "IFC Voids"
    bl_idname = "BIM_PT_voids"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        return IfcStore.get_file()

    def draw(self, context):
        props = context.active_object.BIMObjectProperties
        if props.ifc_definition_id not in Data.products:
            Data.load(IfcStore.get_file(), props.ifc_definition_id)

        row = self.layout.row(align=True)
        if len(context.selected_objects) == 2:
            op = row.operator("bim.add_opening", icon="ADD", text="Add Opening")
            for obj in context.selected_objects:
                if "IfcOpeningElement" in obj.name or not obj.BIMObjectProperties.ifc_definition_id:
                    op.opening = obj.name
                else:
                    op.obj = obj.name

            opening_id = None
            obj_name = None
            for obj in context.selected_objects:
                if obj.BIMObjectProperties.ifc_definition_id in Data.openings:
                    opening_id = obj.BIMObjectProperties.ifc_definition_id
                elif obj.BIMObjectProperties.ifc_definition_id in Data.fillings:
                    opening_id = Data.fillings[obj.BIMObjectProperties.ifc_definition_id]["FillsVoid"]
                else:
                    obj_name = obj.name
            if opening_id and obj_name:
                op = row.operator("bim.remove_opening", icon="X", text="Remove Opening")
                op.opening_id = opening_id
                op.obj = obj_name
        else:
            row.label(text="Select an opening and an element to modify", icon="HELP")

        opening_ids = Data.products[props.ifc_definition_id]
        if not opening_ids:
            row = self.layout.row(align=True)
            row.label(text="No Openings", icon="SELECT_SUBTRACT")
        for opening_id in opening_ids:
            opening = Data.openings[opening_id]
            if opening["HasFillings"]:
                for filling_id in opening["HasFillings"]:
                    filling = Data.fillings[filling_id]
                    row = self.layout.row(align=True)
                    row.label(text=opening["Name"], icon="SELECT_SUBTRACT")
                    row.label(text=filling["Name"], icon="SELECT_INTERSECT")
            else:
                row = self.layout.row(align=True)
                row.label(text=opening["Name"], icon="SELECT_SUBTRACT")
            op = row.operator("bim.remove_opening", icon="X", text="")
            op.opening_id = opening_id

        if props.ifc_definition_id not in Data.fillings:
            row = self.layout.row(align=True)
            row.prop(context.scene.VoidProperties, "desired_opening", text="", icon="SELECT_INTERSECT")
            row.operator("bim.add_filling", icon="ADD", text="")
        else:
            opening = Data.openings[Data.fillings[props.ifc_definition_id]["FillsVoid"]]
            row = self.layout.row(align=True)
            row.label(text=opening["Name"], icon="SELECT_INTERSECT")
            row.operator("bim.remove_filling", icon="X", text="")
