from bpy.types import Panel, UIList
from blenderbim.bim.ifc import IfcStore
from ifcopenshell.api.spatial.data import Data


class BIM_PT_spatial(Panel):
    bl_label = "IFC Spatial Container"
    bl_idname = "BIM_PT_spatial"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        if not context.active_object:
            return False
        oprops = context.active_object.BIMObjectProperties
        if not oprops.ifc_definition_id:
            return False
        if oprops.ifc_definition_id not in Data.products:
            Data.load(IfcStore.get_file(), oprops.ifc_definition_id)
        if not Data.products[oprops.ifc_definition_id]:
            return False
        return True

    def draw(self, context):
        oprops = context.active_object.BIMObjectProperties
        sprops = context.scene.BIMSpatialProperties
        props = context.active_object.BIMObjectSpatialProperties
        if not oprops.ifc_definition_id:
            return
        if oprops.ifc_definition_id not in Data.products:
            Data.load(IfcStore.get_file(), oprops.ifc_definition_id)

        if props.is_editing:
            row = self.layout.row(align=True)
            if sprops.active_decomposes_parent_id:
                op = row.operator("bim.change_spatial_level", text="", icon="FRAME_PREV")
                op.parent_id = sprops.active_decomposes_parent_id
            row.operator("bim.assign_container", icon="CHECKMARK")
            row.operator("bim.disable_editing_container", icon="X", text="")

            self.layout.template_list(
                "BIM_UL_spatial_elements", "", sprops, "spatial_elements", sprops, "active_spatial_element_index"
            )
        else:
            row = self.layout.row(align=True)
            name = "{}/{}".format(
                Data.products[oprops.ifc_definition_id]["type"], Data.products[oprops.ifc_definition_id]["Name"]
            )
            if name == "None/None":
                name = "This object is not spatially contained"
            row.label(text=name)
            row.operator("bim.enable_editing_container", icon="GREASEPENCIL", text="")
            row.operator("bim.remove_container", icon="X", text="")


class BIM_UL_spatial_elements(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if item:
            if item.has_decomposition:
                op = layout.operator("bim.change_spatial_level", text="", icon="DISCLOSURE_TRI_RIGHT", emboss=False)
                op.parent_id = item.ifc_definition_id
            layout.label(text=item.name)
            layout.label(text=item.long_name)
