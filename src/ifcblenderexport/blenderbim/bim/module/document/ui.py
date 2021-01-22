from bpy.types import Panel, UIList
from blenderbim.bim.ifc import IfcStore
from blenderbim.bim.module.document.data import Data


class BIM_PT_documents(Panel):
    bl_label = "IFC Documents"
    bl_idname = "BIM_PT_documents"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"

    @classmethod
    def poll(cls, context):
        return IfcStore.get_file()

    def draw(self, context):
        if not Data.is_loaded:
            Data.load()

        self.props = context.scene.BIMDocumentProperties

        if not self.props.is_editing or self.props.is_editing == "information":
            row = self.layout.row(align=True)
            row.label(text="{} Documents Found".format(len(Data.information)))
            if self.props.is_editing == "information":
                row.operator("bim.disable_document_editing_ui", text="", icon="CHECKMARK")
                row.operator("bim.add_information", text="", icon="ADD")
            else:
                row.operator("bim.load_information", text="", icon="GREASEPENCIL")

        if not self.props.is_editing or self.props.is_editing == "reference":
            row = self.layout.row(align=True)
            row.label(text="{} References Found".format(len(Data.references)))
            if self.props.is_editing == "reference":
                row.operator("bim.disable_document_editing_ui", text="", icon="CHECKMARK")
                row.operator("bim.add_document_reference", text="", icon="ADD")
            else:
                row.operator("bim.load_document_references", text="", icon="GREASEPENCIL")

        if self.props.is_editing:
            self.layout.template_list(
                "BIM_UL_documents",
                "",
                self.props,
                "documents",
                self.props,
                "active_document_index",
            )

        if self.props.active_document_id:
            self.draw_editable_ui(context)
        return

    def draw_editable_ui(self, context):
        for attribute in self.props.document_attributes:
            row = self.layout.row(align=True)
            if attribute.data_type == "string":
                row.prop(attribute, "string_value", text=attribute.name)
            elif attribute.data_type == "enum":
                row.prop(attribute, "enum_value", text=attribute.name)
            if attribute.is_optional:
                row.prop(attribute, "is_null", icon="RADIOBUT_OFF" if attribute.is_null else "RADIOBUT_ON", text="")


class BIM_UL_documents(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if item:
            row = layout.row(align=True)
            row.label(text=item.identification)
            row.label(text=item.name)
            if context.scene.BIMDocumentProperties.active_document_id == item.ifc_definition_id:
                if context.scene.BIMDocumentProperties.is_editing == "information":
                    row.operator("bim.edit_information", text="", icon="CHECKMARK")
                elif context.scene.BIMDocumentProperties.is_editing == "reference":
                    row.operator("bim.edit_document_reference", text="", icon="CHECKMARK")
                row.operator("bim.disable_editing_document", text="", icon="X")
            elif context.scene.BIMDocumentProperties.active_document_id:
                row.operator("bim.remove_document", text="", icon="X").document = item.ifc_definition_id
            else:
                op = row.operator("bim.enable_editing_document", text="", icon="GREASEPENCIL")
                op.document = item.ifc_definition_id
                row.operator("bim.remove_document", text="", icon="X").document = item.ifc_definition_id
