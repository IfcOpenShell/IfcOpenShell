from bpy.types import Panel
from blenderbim.bim.module.attribute.data import Data


def draw_ui(context, layout, obj_type):
    obj = context.active_object if obj_type == "Object" else context.active_object.active_material
    oprops = obj.BIMObjectProperties
    props = obj.BIMAttributeProperties
    if oprops.ifc_definition_id not in Data.products:
        Data.load(oprops.ifc_definition_id)

    if props.is_editing_attributes:
        row = layout.row(align=True)
        op = row.operator("bim.edit_attributes", icon="CHECKMARK", text="Save Attributes")
        op.obj_type = obj_type
        op.obj = obj.name
        op = row.operator("bim.disable_editing_attributes", icon="X", text="")
        op.obj_type = obj_type
        op.obj = obj.name

        for attribute in Data.products[oprops.ifc_definition_id]:
            if attribute["type"] == "entity":
                continue
            row = layout.row(align=True)
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
                row.prop(
                    blender_attribute,
                    "is_null",
                    icon="RADIOBUT_OFF" if blender_attribute.is_null else "RADIOBUT_ON",
                    text="",
                )
            # TODO: reimplement, see #1222
            # op = row.operator("bim.copy_attribute_to_selection", icon="COPYDOWN", text="")
            # op.attribute_name = attribute.name
            # op.attribute_value = attribute.string_value
    else:
        row = layout.row()
        op = row.operator("bim.enable_editing_attributes", icon="GREASEPENCIL", text="Edit")
        op.obj_type = obj_type
        op.obj = obj.name
        for attribute in Data.products[oprops.ifc_definition_id]:
            if attribute["value"] is None or attribute["type"] == "entity":
                continue
            row = layout.row(align=True)
            row.label(text=attribute["name"])
            row.label(text=str(attribute["value"]))

    # TODO: reimplement, see #1222
    # if "IfcSite/" in context.active_object.name or "IfcBuilding/" in context.active_object.name:
    #    self.draw_addresses_ui()


class BIM_PT_object_attributes(Panel):
    bl_label = "IFC Attributes"
    bl_idname = "BIM_PT_object_attributes"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        return bool(context.active_object.BIMObjectProperties.ifc_definition_id)

    def draw(self, context):
        draw_ui(context, self.layout, "Object")


class BIM_PT_material_attributes(Panel):
    bl_label = "IFC Attributes"
    bl_idname = "BIM_PT_material_attributes"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "material"

    @classmethod
    def poll(cls, context):
        try:
            return bool(context.active_object.active_material.BIMObjectProperties.ifc_definition_id)
        except:
            return False

    def draw(self, context):
        draw_ui(context, self.layout, "Material")
