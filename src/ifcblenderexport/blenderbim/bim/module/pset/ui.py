from bpy.types import Panel
from blenderbim.bim.module.pset.data import Data

def draw_psetqto_ui(pset_id, pset, props, layout):
    box = layout.box()
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
                draw_psetqto_editable_ui(box, props, prop)
        else:
            for prop in pset["Properties"]:
                if prop["value"] is None or prop["value"] == "":
                    continue
                row = box.row(align=True)
                row.scale_y = 0.8
                row.label(text=prop["Name"])
                row.label(text=str(prop["value"]))

def draw_psetqto_editable_ui(box, props, prop):
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
    if (
        "length" in prop["Name"].lower()
        or "width" in prop["Name"].lower()
        or "height" in prop["Name"].lower()
        or "depth" in prop["Name"].lower()
        or "perimeter" in prop["Name"].lower()
    ):
        op = row.operator("bim.guess_quantity", icon="IPO_EASE_IN_OUT", text="")
        op.prop = prop["Name"]
    elif "area" in prop["Name"].lower():
        op = row.operator("bim.guess_quantity", icon="MESH_CIRCLE", text="")
        op.prop = prop["Name"]
    elif "volume" in prop["Name"].lower():
        op = row.operator("bim.guess_quantity", icon="SPHERE", text="")
        op.prop = prop["Name"]

class BIM_PT_object_psets(Panel):
    bl_label = "IFC Object Property Sets"
    bl_idname = "BIM_PT_object_psets"
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
        if props.ifc_definition_id not in Data.products:
            Data.load(props.ifc_definition_id)
        if not Data.products[props.ifc_definition_id]:
            return False
        return True

    def draw(self, context):
        oprops = context.active_object.BIMObjectProperties
        props = context.active_object.PsetProperties
        if not oprops.ifc_definition_id:
            return
        if oprops.ifc_definition_id not in Data.products:
            Data.load(oprops.ifc_definition_id)
        row = self.layout.row(align=True)
        row.prop(props, "pset_name", text="")
        row.operator("bim.add_pset", icon="ADD", text="")

        for pset_id in Data.products[oprops.ifc_definition_id]["psets"]:
            pset = Data.psets[pset_id]
            draw_psetqto_ui(pset_id, pset, props, self.layout)

        # TODO reimplement. See #1222.
        #if props.relating_type and props.relating_type.PsetProperties.psets:
        #    self.layout.label(text="Inherited Psets:")
        #    self.draw_psets_ui(props.relating_type.PsetProperties, enabled=False)


class BIM_PT_object_qtos(Panel):
    bl_label = "IFC Object Quantity Sets"
    bl_idname = "BIM_PT_object_qtos"
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
        if props.ifc_definition_id not in Data.products:
            Data.load(props.ifc_definition_id)
        if not Data.products[props.ifc_definition_id]:
            return False
        return True

    def draw(self, context):
        oprops = context.active_object.BIMObjectProperties
        props = context.active_object.PsetProperties
        if not oprops.ifc_definition_id:
            return
        if oprops.ifc_definition_id not in Data.products:
            Data.load(oprops.ifc_definition_id)
        row = self.layout.row(align=True)
        row.prop(props, "qto_name", text="")
        row.operator("bim.add_qto", icon="ADD", text="")

        for qto_id in Data.products[oprops.ifc_definition_id]["qtos"]:
            qto = Data.qtos[qto_id]
            draw_psetqto_ui(qto_id, qto, props, self.layout)
