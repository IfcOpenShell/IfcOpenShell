from bpy.types import Panel
from blenderbim.bim.module.pset.data import Data
from blenderbim.bim.ifc import IfcStore


def draw_psetqto_ui(context, pset_id, pset, props, layout, obj_type):
    box = layout.box()
    row = box.row(align=True)
    icon = "TRIA_DOWN" if pset["is_expanded"] else "TRIA_RIGHT"
    row.operator("bim.toggle_pset_expansion", icon=icon, text="", emboss=False).pset_id = pset_id
    if not props.active_pset_id:
        row.label(text=pset["Name"], icon="COPY_ID")
        op = row.operator("bim.enable_pset_editing", icon="GREASEPENCIL", text="")
        op.pset_id = pset_id
        op.obj = context.active_object.name if obj_type == "Object" else context.active_object.active_material.name
        op.obj_type = obj_type
        op = row.operator("bim.remove_pset", icon="X", text="")
        op.pset_id = pset_id
        op.obj = context.active_object.name if obj_type == "Object" else context.active_object.active_material.name
        op.obj_type = obj_type
    elif props.active_pset_id != pset_id:
        row.label(text=pset["Name"], icon="COPY_ID")
        op = row.operator("bim.remove_pset", icon="X", text="")
        op.pset_id = pset_id
        op.obj = context.active_object.name if obj_type == "Object" else context.active_object.active_material.name
        op.obj_type = obj_type
    elif props.active_pset_id == pset_id:
        row.prop(props, "active_pset_name", icon="COPY_ID", text="")
        op = row.operator("bim.edit_pset", icon="CHECKMARK", text="")
        op.obj = context.active_object.name if obj_type == "Object" else context.active_object.active_material.name
        op.obj_type = obj_type
        op = row.operator("bim.disable_pset_editing", icon="X", text="")
        op.obj = context.active_object.name if obj_type == "Object" else context.active_object.active_material.name
        op.obj_type = obj_type
    if pset["is_expanded"]:
        if props.active_pset_id == pset_id:
            for prop in pset["Properties"]:
                draw_psetqto_editable_ui(box, props, prop)
        else:
            has_props_displayed = False
            for prop in pset["Properties"]:
                if prop["value"] is None or prop["value"] == "":
                    continue
                has_props_displayed = True
                row = box.row(align=True)
                row.scale_y = 0.8
                row.label(text=prop["Name"])
                row.label(text=str(prop["value"]))
            if not has_props_displayed:
                row = box.row()
                row.scale_y = 0.8
                row.label(text="No Properties Set")


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
        op = row.operator("bim.add_pset", icon="ADD", text="")
        op.obj = context.active_object.name
        op.obj_type = "Object"

        for pset_id in Data.products[oprops.ifc_definition_id]["psets"]:
            pset = Data.psets[pset_id]
            draw_psetqto_ui(context, pset_id, pset, props, self.layout, "Object")

        # TODO reimplement. See #1222.
        # if props.relating_type and props.relating_type.PsetProperties.psets:
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
            draw_psetqto_ui(context, qto_id, qto, props, self.layout, "Object")


class BIM_PT_material_psets(Panel):
    bl_label = "IFC Material Property Sets"
    bl_idname = "BIM_PT_material_psets"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "material"

    @classmethod
    def poll(cls, context):
        if not context.active_object:
            return False
        props = context.active_object.active_material.BIMObjectProperties
        if not props.ifc_definition_id:
            return False
        if IfcStore.get_file().schema == "IFC2X3":
            return False # We don't support material psets in IFC2X3 because they suck
        if props.ifc_definition_id not in Data.products:
            Data.load(props.ifc_definition_id)
        if not Data.products[props.ifc_definition_id]:
            return False
        return True

    def draw(self, context):
        oprops = context.active_object.active_material.BIMObjectProperties
        props = context.active_object.active_material.PsetProperties
        if not oprops.ifc_definition_id:
            return
        if oprops.ifc_definition_id not in Data.products:
            Data.load(oprops.ifc_definition_id)
        row = self.layout.row(align=True)
        row.prop(props, "material_pset_name", text="")
        op = row.operator("bim.add_pset", icon="ADD", text="")
        op.obj = context.active_object.active_material.name
        op.obj_type = "Material"

        for pset_id in Data.products[oprops.ifc_definition_id]["psets"]:
            pset = Data.psets[pset_id]
            draw_psetqto_ui(context, pset_id, pset, props, self.layout, "Material")
