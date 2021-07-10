from bpy.types import Panel, UIList, Mesh
from blenderbim.bim.ifc import IfcStore
from ifcopenshell.api.layer.data import Data


class BIM_PT_layers(Panel):
    bl_label = "IFC Presentation Layers"
    bl_idname = "BIM_PT_layers"
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

        self.props = context.scene.BIMLayerProperties

        row = self.layout.row(align=True)
        row.label(text="{} Layers Found".format(len(Data.layers.keys())))
        if self.props.is_editing:
            row.operator("bim.add_presentation_layer", text="", icon="ADD")
            row.operator("bim.disable_layer_editing_ui", text="", icon="X")
        else:
            row.operator("bim.load_layers", text="", icon="GREASEPENCIL")

        if self.props.is_editing:
            self.layout.template_list(
                "BIM_UL_layers",
                "",
                self.props,
                "layers",
                self.props,
                "active_layer_index",
            )

        if self.props.active_layer_id:
            self.draw_editable_ui(context)

    def draw_editable_ui(self, context):
        for attribute in self.props.layer_attributes:
            row = self.layout.row(align=True)
            row.prop(attribute, "string_value", text=attribute.name)
            if attribute.is_optional:
                row.prop(attribute, "is_null", icon="RADIOBUT_OFF" if attribute.is_null else "RADIOBUT_ON", text="")


class BIM_UL_layers(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if item:
            row = layout.row(align=True)
            row.label(text=item.name)

            if context.active_object and isinstance(context.active_object.data, Mesh):
                mprops = context.active_object.data.BIMMeshProperties
                if (
                    mprops.ifc_definition_id in Data.items
                    and item.ifc_definition_id in Data.items[mprops.ifc_definition_id]
                ):
                    op = row.operator("bim.unassign_presentation_layer", text="", icon="KEYFRAME_HLT", emboss=False)
                    op.layer = item.ifc_definition_id
                else:
                    op = row.operator("bim.assign_presentation_layer", text="", icon="KEYFRAME", emboss=False)
                    op.layer = item.ifc_definition_id

            row.operator("bim.disable_editing_layer", text="", icon="HIDE_OFF", emboss=False)
            row.operator("bim.disable_editing_layer", text="", icon="FREEZE", emboss=False)

            if context.scene.BIMLayerProperties.active_layer_id == item.ifc_definition_id:
                row.operator("bim.edit_presentation_layer", text="", icon="CHECKMARK")
                row.operator("bim.disable_editing_layer", text="", icon="X")
            elif context.scene.BIMLayerProperties.active_layer_id:
                row.operator("bim.remove_presentation_layer", text="", icon="X").layer = item.ifc_definition_id
            else:
                op = row.operator("bim.enable_editing_layer", text="", icon="GREASEPENCIL")
                op.layer = item.ifc_definition_id
                row.operator("bim.remove_presentation_layer", text="", icon="X").layer = item.ifc_definition_id
