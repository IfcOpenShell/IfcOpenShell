from bpy.types import Panel, UIList
from blenderbim.bim.ifc import IfcStore
from blenderbim.bim.module.structural.data import Data


class BIM_PT_structural_connections(Panel):
    bl_label = "IFC Structural Connections"
    bl_idname = "BIM_PT_structural_connections"
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
        if not IfcStore.get_file().by_id(props.ifc_definition_id).is_a("IfcStructuralConnection"):
            return False
        return True

    def draw(self, context):
        self.oprops = context.active_object.BIMObjectProperties
        self.props = context.active_object.BIMStructuralProperties
        if self.oprops.ifc_definition_id not in Data.connections:
            Data.load(self.oprops.ifc_definition_id)

        self.data = Data.connections[self.oprops.ifc_definition_id]

        row = self.layout.row(align=True)
        if self.data and self.props.is_editing_connection:
            row.label(text=self.data["type"], icon="CON_TRACKTO")
            row.operator("bim.edit_structural_boundary_condition", text="", icon="CHECKMARK")
            row.operator("bim.disable_editing_structural_boundary_condition", text="", icon="X")
        elif self.data and not self.props.is_editing_connection:
            row.label(text=self.data["type"], icon="CON_TRACKTO")
            row.operator("bim.enable_editing_structural_boundary_condition", text="", icon="GREASEPENCIL")
            row.operator("bim.remove_structural_boundary_condition", text="", icon="X")
        else:
            row.label(text="No Connection Found", icon="CON_TRACKTO")
            row.operator("bim.add_structural_boundary_condition", text="", icon="ADD")

        if self.props.is_editing_connection:
            self.draw_editable_ui(context)
        else:
            self.draw_read_only_ui(context)

    def draw_editable_ui(self, context):
        for attribute in self.props.connection_attributes:
            if attribute.data_type == "string":
                row = self.layout.row()
                row.prop(attribute, "string_value", text=attribute["name"])
            else:
                row = self.layout.row(align=True)
                row.prop(attribute, "enum_value", text=attribute["name"])
                if attribute.enum_value == "IfcBoolean":
                    row.prop(attribute, "bool_value", text="")
                else:
                    row.prop(attribute, "float_value", text="")
            if attribute.is_optional:
                row.prop(attribute, "is_null", icon="RADIOBUT_OFF" if attribute.is_null else "RADIOBUT_ON", text="")

    def draw_read_only_ui(self, context):
        for key, value in self.data.items():
            if key == "id" or key == "type" or value == None:
                continue
            row = self.layout.row(align=True)
            row.label(text=key)
            if isinstance(value, bool):
                row.label(text="", icon="CHECKBOX_HLT" if value else "CHECKBOX_DEHLT")
            else:
                row.label(text=str(value))


class BIM_PT_structural(Panel):
    bl_label = "IFC Structural Analysis Models"
    bl_idname = "BIM_PT_structural"
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
        self.props = context.scene.BIMStructuralProperties

        row = self.layout.row(align=True)
        row.label(
            text="{} Structural Analysis Models Found".format(len(Data.structural_analysis_models)), icon="MOD_SIMPLIFY"
        )
        if self.props.is_editing:
            row.operator("bim.add_structural_analysis_model", text="", icon="ADD")
            row.operator("bim.disable_structural_analysis_model_editing_ui", text="", icon="CHECKMARK")
        else:
            row.operator("bim.load_structural_analysis_models", text="", icon="GREASEPENCIL")

        if self.props.is_editing:
            self.layout.template_list(
                "BIM_UL_structural_analysis_models",
                "",
                self.props,
                "structural_analysis_models",
                self.props,
                "active_structural_analysis_model_index",
            )

        if self.props.active_structural_analysis_model_id:
            self.draw_editable_ui(context)

    def draw_editable_ui(self, context):
        for attribute in self.props.structural_analysis_model_attributes:
            row = self.layout.row(align=True)
            if attribute.data_type == "string":
                row.prop(attribute, "string_value", text=attribute.name)
            elif attribute.data_type == "enum":
                row.prop(attribute, "enum_value", text=attribute.name)
            if attribute.is_optional:
                row.prop(attribute, "is_null", icon="RADIOBUT_OFF" if attribute.is_null else "RADIOBUT_ON", text="")


class BIM_UL_structural_analysis_models(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if item:
            row = layout.row(align=True)
            row.label(text=item.name)

            if context.active_object:
                oprops = context.active_object.BIMObjectProperties
                if (
                    oprops.ifc_definition_id in Data.products
                    and item.ifc_definition_id in Data.products[oprops.ifc_definition_id]
                ):
                    op = row.operator(
                        "bim.unassign_structural_analysis_model", text="", icon="KEYFRAME_HLT", emboss=False
                    )
                    op.structural_analysis_model = item.ifc_definition_id
                else:
                    op = row.operator("bim.assign_structural_analysis_model", text="", icon="KEYFRAME", emboss=False)
                    op.structural_analysis_model = item.ifc_definition_id

            if context.scene.BIMStructuralProperties.active_structural_analysis_model_id == item.ifc_definition_id:
                row.operator("bim.edit_structural_analysis_model", text="", icon="CHECKMARK")
                row.operator("bim.disable_editing_structural_analysis_model", text="", icon="X")
            elif context.scene.BIMStructuralProperties.active_structural_analysis_model_id:
                op = row.operator("bim.remove_structural_analysis_model", text="", icon="X")
                op.structural_analysis_model = item.ifc_definition_id
            else:
                op = row.operator("bim.enable_editing_structural_analysis_model", text="", icon="GREASEPENCIL")
                op.structural_analysis_model = item.ifc_definition_id
                op = row.operator("bim.remove_structural_analysis_model", text="", icon="X")
                op.structural_analysis_model = item.ifc_definition_id
