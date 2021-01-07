from bpy.types import Panel
from blenderbim.bim.module.attribute.data import Data


class BIM_PT_attributes(Panel):
    bl_label = "IFC Attributes"
    bl_idname = "BIM_PT_attributes"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        return bool(context.active_object.BIMObjectProperties.ifc_definition_id)

    def draw(self, context):
        props = context.active_object.BIMObjectProperties
        if not props.ifc_definition_id:
            return
        if props.ifc_definition_id not in Data.products:
            Data.load(props.ifc_definition_id)

        if props.is_editing_attributes:
            row = self.layout.row(align=True)
            row.operator("bim.edit_attributes", icon="CHECKMARK", text="Save Attributes")
            row.operator("bim.disable_editing_attributes", icon="X", text="")

            for attribute in Data.products[props.ifc_definition_id]:
                if attribute["type"] == "entity":
                    continue
                row = self.layout.row(align=True)
                blender_attribute = props.attributes.get(attribute["name"])
                if attribute["type"] == "string" or attribute["type"] == "list":
                    row.prop(blender_attribute, "string_value", text=attribute["name"])
                elif attribute["type"] == "integer":
                    row.prop(blender_attribute, "int_value", text=attribute["name"])
                elif attribute["type"] == "float":
                    row.prop(blender_attribute, "float_value", text=attribute["name"])
                elif attribute["type"] == "enum":
                    row.prop(blender_attribute, "enum_value", text=attribute["name"])

                if attribute["name"] == "GlobalId":
                    row.operator("bim.generate_global_id", icon="FILE_REFRESH", text="")
                if attribute["is_optional"]:
                    row.prop(blender_attribute, "is_null", icon="RADIOBUT_OFF" if blender_attribute.is_null else "RADIOBUT_ON", text="")
                # TODO: reimplement, see #1222
                #op = row.operator("bim.copy_attribute_to_selection", icon="COPYDOWN", text="")
                #op.attribute_name = attribute.name
                #op.attribute_value = attribute.string_value
        else:
            row = self.layout.row()
            row.operator("bim.enable_editing_attributes", icon="GREASEPENCIL", text="Edit")
            for attribute in Data.products[props.ifc_definition_id]:
                if attribute["value"] is None or attribute["type"] == "entity":
                    continue
                row = self.layout.row(align=True)
                row.label(text=attribute["name"])
                row.label(text=str(attribute["value"]))

        # TODO: reimplement, see #1222
        #if "IfcSite/" in context.active_object.name or "IfcBuilding/" in context.active_object.name:
        #    self.draw_addresses_ui()

    def draw_addresses_ui(self):
        self.layout.label(text="Address:")
        address = bpy.context.active_object.BIMObjectProperties.address
        row = self.layout.row()
        row.prop(address, "purpose")
        if address.purpose == "USERDEFINED":
            row = self.layout.row()
            row.prop(address, "user_defined_purpose")
        row = self.layout.row()
        row.prop(address, "description")

        row = self.layout.row()
        row.prop(address, "internal_location")
        row = self.layout.row()
        row.prop(address, "address_lines")
        row = self.layout.row()
        row.prop(address, "postal_box")
        row = self.layout.row()
        row.prop(address, "town")
        row = self.layout.row()
        row.prop(address, "region")
        row = self.layout.row()
        row.prop(address, "postal_code")
        row = self.layout.row()
        row.prop(address, "country")

