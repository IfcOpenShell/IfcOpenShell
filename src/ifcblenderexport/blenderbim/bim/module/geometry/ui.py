import bpy
from bpy.types import Panel
from blenderbim.bim.module.geometry.data import Data
from blenderbim.bim.ifc import IfcStore


class BIM_PT_representations(Panel):
    bl_label = "IFC Representations"
    bl_idname = "BIM_PT_representations"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        return IfcStore.get_file()

    def draw(self, context):
        layout = self.layout
        props = context.active_object.BIMObjectProperties

        if props.ifc_definition_id not in Data.products:
            Data.load(props.ifc_definition_id)

        representations = Data.products[props.ifc_definition_id]
        if not representations:
            layout.label(text="No representations found")

        row = layout.row(align=True)
        row.prop(bpy.context.scene.BIMProperties, "contexts", text="")
        row.operator("bim.add_representation", icon="ADD", text="")

        for ifc_definition_id in representations:
            representation = Data.representations[ifc_definition_id]
            row = self.layout.row(align=True)
            row.label(text=representation["ContextOfItems"]["ContextType"])
            row.label(text=representation["ContextOfItems"]["ContextIdentifier"])
            row.label(text=representation["ContextOfItems"]["TargetView"])
            row.label(text=representation["RepresentationType"])
            row.operator("bim.switch_representation", icon="OUTLINER_DATA_MESH", text="").ifc_definition_id = ifc_definition_id
            row.operator("bim.remove_representation", icon="X", text="").ifc_definition_id = ifc_definition_id


class BIM_PT_mesh(Panel):
    bl_label = "IFC Representation"
    bl_idname = "BIM_PT_mesh"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"

    @classmethod
    def poll(cls, context):
        return (
            context.active_object is not None
            and context.active_object.type == "MESH"
            and hasattr(context.active_object.data, "BIMMeshProperties")
        )

    def draw(self, context):
        if not context.active_object.data:
            return
        layout = self.layout
        props = context.active_object.data.BIMMeshProperties

        row = layout.row()
        row.operator("bim.get_representation_ifc_parameters")
        row = layout.row()
        row.operator("bim.update_mesh_representation")
        for index, ifc_parameter in enumerate(props.ifc_parameters):
            row = layout.row(align=True)
            row.prop(ifc_parameter, "name", text="")
            row.prop(ifc_parameter, "value", text="")
            row.operator("bim.update_parametric_representation", icon="FILE_REFRESH", text="").index = index


def BIM_PT_transform(self, context):
    if context.active_object and context.active_object.BIMObjectProperties.ifc_definition_id:
        row = self.layout.row()
        row.operator("bim.edit_object_placement")
