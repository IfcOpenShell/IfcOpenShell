from bpy.types import Panel
from blenderbim.bim.module.pset.data import Data


class BIM_PT_object_psets(Panel):
    bl_label = "IFC Object Property Sets"
    bl_idname = "BIM_PT_object_psets"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and hasattr(context.active_object, "BIMObjectProperties")

    def draw(self, context):
        props = context.active_object.BIMObjectProperties
        if not props.ifc_definition_id:
            return
        if props.ifc_definition_id not in Data.products:
            Data.load(props.ifc_definition_id)
        row = self.layout.row(align=True)
        row.prop(props, "pset_name", text="")
        row.operator("bim.add_pset", icon="ADD", text="")

        self.draw_psets_ui(props, Data.products[props.ifc_definition_id])

        # TODO reimplement. See #1222.
        #if props.relating_type and props.relating_type.BIMObjectProperties.psets:
        #    self.layout.label(text="Inherited Psets:")
        #    self.draw_psets_ui(props.relating_type.BIMObjectProperties, enabled=False)

    def draw_psets_ui(self, props, pset_ids):
        for pset_id in pset_ids:
            pset = Data.psets[pset_id]
            box = self.layout.box()
            row = box.row(align=True)
            icon = "TRIA_DOWN" if pset["is_expanded"] else "TRIA_RIGHT"
            row.operator("bim.toggle_pset_expansion", icon=icon, text="", emboss=False).pset_id = pset_id
            if not props.active_pset_id:
                row.label(text=pset["Name"], icon="COPY_ID")
                row.operator("bim.enable_pset_editing", icon="GREASEPENCIL", text="").pset_id = pset_id
                row.operator("bim.remove_pset", icon="X", text="").pset_id = pset_id
            elif props.active_pset_id != pset_id:
                row.label(text=pset["Name"], icon="COPY_ID")
                row.operator("bim.remove_pset", icon="X", text="").pset_id = pset_id
            elif props.active_pset_id == pset_id:
                row.prop(props, "active_pset_name", icon="COPY_ID", text="")
                row.operator("bim.edit_pset", icon="CHECKMARK", text="")
                row.operator("bim.disable_pset_editing", icon="X", text="")
            if pset["is_expanded"]:
                if props.active_pset_id == pset_id:
                    for prop in pset["Properties"]:
                        row = box.row(align=True)
                        blender_prop = props.properties.get(prop["Name"])
                        if prop["type"] == "string":
                            row.prop(blender_prop, "string_value", text=prop["Name"])
                        elif prop["type"] == "integer":
                            row.prop(blender_prop, "int_value", text=prop["Name"])
                        elif prop["type"] == "float":
                            row.prop(blender_prop, "float_value", text=prop["Name"])
                        elif prop["type"] == "boolean":
                            row.prop(blender_prop, "bool_value", text=prop["Name"])
                        elif prop["type"] == "enum":
                            row.prop(blender_prop, "enum_value", text=prop["Name"])
                        row.prop(blender_prop, "is_null", icon="RADIOBUT_OFF" if blender_prop.is_null else "RADIOBUT_ON", text="")
                else:
                    for prop in pset["Properties"]:
                        if prop["value"] is None or prop["value"] == "":
                            continue
                        row = box.row(align=True)
                        row.scale_y = 0.8
                        row.label(text=prop["Name"])
                        row.label(text=str(prop["value"]))
