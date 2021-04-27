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
        self.props = context.scene.BIMCostProperties

        if not Data.is_loaded:
            Data.load(IfcStore.get_file())

        row = self.layout.row()
        row.operator("bim.add_cost_schedule", icon="ADD")

        for cost_schedule_id, cost_schedule in Data.cost_schedules.items():
            self.draw_cost_schedule_ui(cost_schedule_id, cost_schedule)

    def draw_cost_schedule_ui(self, cost_schedule_id, cost_schedule):
        row = self.layout.row(align=True)
        row.label(text=cost_schedule["Name"] or "Unnamed", icon="LINENUMBERS_ON")

        if self.props.active_cost_schedule_id and self.props.active_cost_schedule_id == cost_schedule_id:
            if self.props.is_editing == "COST_SCHEDULE":
                row.operator("bim.edit_cost_schedule", text="", icon="CHECKMARK")
            elif self.props.is_editing == "COST_ITEMS":
                row.operator("bim.add_summary_cost_item", text="", icon="ADD").cost_schedule = cost_schedule_id
            row.operator("bim.disable_editing_cost_schedule", text="", icon="CANCEL")
        elif self.props.active_cost_schedule_id:
            row.operator("bim.remove_cost_schedule", text="", icon="X").cost_schedule = cost_schedule_id
        else:
            row.operator("bim.enable_editing_cost_items", text="", icon="OUTLINER").cost_schedule = cost_schedule_id
            row.operator(
                "bim.enable_editing_cost_schedule", text="", icon="GREASEPENCIL"
            ).cost_schedule = cost_schedule_id
            row.operator("bim.remove_cost_schedule", text="", icon="X").cost_schedule = cost_schedule_id

        if self.props.active_cost_schedule_id == cost_schedule_id:
            if self.props.is_editing == "COST_SCHEDULE":
                self.draw_editable_cost_schedule_ui()
            elif self.props.is_editing == "COST_ITEMS":
                self.draw_editable_cost_item_ui(cost_schedule_id)

    def draw_editable_cost_schedule_ui(self):
        for attribute in self.props.cost_schedule_attributes:
            row = self.layout.row(align=True)
            if attribute.data_type == "string":
                row.prop(attribute, "string_value", text=attribute.name)
            elif attribute.data_type == "enum":
                row.prop(attribute, "enum_value", text=attribute.name)
            if attribute.is_optional:
                row.prop(attribute, "is_null", icon="RADIOBUT_OFF" if attribute.is_null else "RADIOBUT_ON", text="")

    def draw_editable_cost_item_ui(self, cost_schedule_id):
        self.layout.template_list(
            "BIM_UL_cost_items",
            "",
            self.props,
            "cost_items",
            self.props,
            "active_cost_item_index",
        )
        if self.props.active_cost_item_id:
            if self.props.cost_item_editing_type == "ATTRIBUTES":
                self.draw_editable_cost_item_attributes_ui()
            elif self.props.cost_item_editing_type == "QUANTITIES":
                self.draw_editable_cost_item_quantities_ui()
            elif self.props.cost_item_editing_type == "VALUES":
                self.draw_editable_cost_item_values_ui()

    def draw_editable_cost_item_attributes_ui(self):
        for attribute in self.props.cost_item_attributes:
            row = self.layout.row(align=True)
            if attribute.data_type == "string":
                row.prop(attribute, "string_value", text=attribute.name)
            elif attribute.data_type == "boolean":
                row.prop(attribute, "bool_value", text=attribute.name)
            elif attribute.data_type == "integer":
                row.prop(attribute, "int_value", text=attribute.name)
            elif attribute.data_type == "enum":
                row.prop(attribute, "enum_value", text=attribute.name)
            if attribute.is_optional:
                row.prop(attribute, "is_null", icon="RADIOBUT_OFF" if attribute.is_null else "RADIOBUT_ON", text="")

    def draw_editable_cost_item_quantities_ui(self):
        row = self.layout.row(align=True)
        row.prop(self.props, "quantity_types", text="")
        if self.props.quantity_types == "QTO":
            row.prop(self.props, "qto_name", text="")
            row.prop(self.props, "prop_name", text="")
        op = row.operator("bim.add_cost_item_quantity", text="", icon="ADD")
        op.cost_item = self.props.active_cost_item_id
        op.ifc_class = self.props.quantity_types

        for quantity_id in Data.cost_items[self.props.active_cost_item_id]["CostQuantities"]:
            quantity = Data.physical_quantities[quantity_id]
            value = quantity[[k for k in quantity.keys() if "Value" in k][0]]
            row = self.layout.row(align=True)
            row.label(text=quantity["Name"])
            row.label(text=str(value))
            if self.props.active_cost_item_quantity_id and self.props.active_cost_item_quantity_id == quantity_id:
                op = row.operator("bim.edit_cost_item_quantity", text="", icon="CHECKMARK")
                op.physical_quantity = quantity_id
                row.operator("bim.disable_editing_cost_item_quantity", text="", icon="CANCEL")
            elif self.props.active_cost_item_quantity_id:
                op = row.operator("bim.remove_cost_item_quantity", text="", icon="X")
                op.cost_item = self.props.active_cost_item_id
                op.physical_quantity = quantity_id
            else:
                op = row.operator("bim.enable_editing_cost_item_quantity", text="", icon="GREASEPENCIL")
                op.physical_quantity = quantity_id
                op = row.operator("bim.remove_cost_item_quantity", text="", icon="X")
                op.cost_item = self.props.active_cost_item_id
                op.physical_quantity = quantity_id

            if self.props.active_cost_item_quantity_id and self.props.active_cost_item_quantity_id == quantity_id:
                box = self.layout.box()
                self.draw_editable_cost_item_quantity_ui(box)

    def draw_editable_cost_item_quantity_ui(self, layout):
        for attribute in self.props.quantity_attributes:
            row = layout.row(align=True)
            if attribute.data_type == "string":
                row.prop(attribute, "string_value", text=attribute.name)
            elif attribute.data_type == "boolean":
                row.prop(attribute, "bool_value", text=attribute.name)
            elif attribute.data_type == "integer":
                row.prop(attribute, "int_value", text=attribute.name)
            elif attribute.data_type == "float":
                row.prop(attribute, "float_value", text=attribute.name)
            elif attribute.data_type == "enum":
                row.prop(attribute, "enum_value", text=attribute.name)
            if attribute.is_optional:
                row.prop(attribute, "is_null", icon="RADIOBUT_OFF" if attribute.is_null else "RADIOBUT_ON", text="")

    def draw_editable_cost_item_values_ui(self):
        row = self.layout.row(align=True)
        row.prop(self.props, "cost_types", text="")
        if self.props.cost_types == "CATEGORY":
            row.prop(self.props, "cost_category", text="")
        op = row.operator("bim.add_cost_item_value", text="", icon="ADD")
        op.cost_item = self.props.active_cost_item_id
        op.cost_type = self.props.cost_types
        if self.props.cost_types == "CATEGORY":
            op.cost_category = self.props.cost_category

        for cost_value_id in Data.cost_items[self.props.active_cost_item_id]["CostValues"]:
            cost_value = Data.cost_values[cost_value_id]
            row = self.layout.row(align=True)
            row.label(text=str(cost_value["Category"]))
            row.label(text=str(cost_value["AppliedValue"]))
            if self.props.active_cost_item_value_id and self.props.active_cost_item_value_id == cost_value_id:
                op = row.operator("bim.edit_cost_item_value", text="", icon="CHECKMARK")
                op.cost_value = cost_value_id
                row.operator("bim.disable_editing_cost_item_value", text="", icon="CANCEL")
            elif self.props.active_cost_item_value_id:
                op = row.operator("bim.remove_cost_item_value", text="", icon="X")
                op.cost_value = cost_value_id
            else:
                op = row.operator("bim.enable_editing_cost_item_value", text="", icon="GREASEPENCIL")
                op.cost_value = cost_value_id
                op = row.operator("bim.remove_cost_item_value", text="", icon="X")
                op.cost_value = cost_value_id

            if self.props.active_cost_item_value_id and self.props.active_cost_item_value_id == cost_value_id:
                box = self.layout.box()
                self.draw_editable_cost_item_value_ui(box)

    def draw_editable_cost_item_value_ui(self, layout):
        for attribute in self.props.cost_value_attributes:
            row = layout.row(align=True)
            if attribute.data_type == "string":
                row.prop(attribute, "string_value", text=attribute.name)
            elif attribute.data_type == "boolean":
                row.prop(attribute, "bool_value", text=attribute.name)
            elif attribute.data_type == "integer":
                row.prop(attribute, "int_value", text=attribute.name)
            elif attribute.data_type == "float":
                row.prop(attribute, "float_value", text=attribute.name)
            elif attribute.data_type == "enum":
                row.prop(attribute, "enum_value", text=attribute.name)
            if attribute.is_optional:
                row.prop(attribute, "is_null", icon="RADIOBUT_OFF" if attribute.is_null else "RADIOBUT_ON", text="")


class BIM_UL_cost_items(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if item:
            props = context.scene.BIMCostProperties
            cost_item = Data.cost_items[item.ifc_definition_id]
            row = layout.row(align=True)
            for i in range(0, item.level_index):
                row.label(text="", icon="BLANK1")
            if item.has_children:
                if item.is_expanded:
                    row.operator(
                        "bim.contract_cost_item", text="", emboss=False, icon="DISCLOSURE_TRI_DOWN"
                    ).cost_item = item.ifc_definition_id
                else:
                    row.operator(
                        "bim.expand_cost_item", text="", emboss=False, icon="DISCLOSURE_TRI_RIGHT"
                    ).cost_item = item.ifc_definition_id
            else:
                row.label(text="", icon="DOT")
            row.prop(item, "name", emboss=False, text="")

            row.label(text="M3")
            op = row.operator("bim.enable_editing_cost_item_quantities", text="", icon="PROPERTIES")
            op.cost_item = item.ifc_definition_id
            row.label(text=str(cost_item["TotalCostQuantity"]))

            op = row.operator("bim.enable_editing_cost_item_values", text="", icon="DISC")
            op.cost_item = item.ifc_definition_id
            row.label(text=str(cost_item["TotalAppliedValue"]))
            row.label(text=str(cost_item["TotalCostValue"]), icon="CON_TRANSLIKE")

            if context.active_object:
                oprops = context.active_object.BIMObjectProperties
                row = layout.row(align=True)
                if oprops.ifc_definition_id in cost_item["Controls"]:
                    op = row.operator("bim.unassign_control", text="", icon="KEYFRAME_HLT", emboss=False)
                    op.cost_item = item.ifc_definition_id
                else:
                    op = row.operator("bim.assign_control", text="", icon="KEYFRAME", emboss=False)
                    op.cost_item = item.ifc_definition_id

            if props.active_cost_item_id == item.ifc_definition_id:
                row.operator("bim.edit_cost_item", text="", icon="CHECKMARK")
                row.operator("bim.disable_editing_cost_item", text="", icon="CANCEL")
            elif props.active_cost_item_id:
                row.operator("bim.add_cost_item", text="", icon="ADD").cost_item = item.ifc_definition_id
                row.operator("bim.remove_cost_item", text="", icon="X").cost_item = item.ifc_definition_id
            else:
                row.operator(
                    "bim.enable_editing_cost_item", text="", icon="GREASEPENCIL"
                ).cost_item = item.ifc_definition_id
                row.operator("bim.add_cost_item", text="", icon="ADD").cost_item = item.ifc_definition_id
                row.operator("bim.remove_cost_item", text="", icon="X").cost_item = item.ifc_definition_id
