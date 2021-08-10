from bpy.types import Panel
from ifcopenshell.api.pset.data import Data
from blenderbim.bim.ifc import IfcStore


def draw_psetqto_ui(context, pset_id, pset, props, layout, obj_type):
    box = layout.box()
    row = box.row(align=True)
    if "is_expanded" not in pset:
        pset["is_expanded"] = True
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
        op = row.operator("bim.disable_pset_editing", icon="CANCEL", text="")
        op.obj = context.active_object.name if obj_type == "Object" else context.active_object.active_material.name
        op.obj_type = obj_type
    if pset["is_expanded"]:
        if props.active_pset_id == pset_id:
            for prop in props.properties:
                draw_psetqto_editable_ui(box, props, prop)
        else:
            has_props_displayed = False
            for prop_id in pset["Properties"]:
                prop = Data.properties[prop_id]
                if context.preferences.addons["blenderbim"].preferences.should_hide_empty_props and (
                    prop["NominalValue"] is None or prop["NominalValue"] == ""
                ):
                    continue
                has_props_displayed = True
                row = box.row(align=True)
                row.scale_y = 0.8
                row.label(text=prop["Name"])
                row.label(text=str(prop["NominalValue"]))
            if not has_props_displayed:
                row = box.row()
                row.scale_y = 0.8
                row.label(text="No Properties Set")


def draw_psetqto_editable_ui(box, props, prop):
    row = box.row(align=True)
    if prop.data_type == "string":
        row.prop(prop, "string_value", text=prop.name)
    elif prop.data_type == "integer":
        row.prop(prop, "int_value", text=prop.name)
    elif prop.data_type == "float":
        row.prop(prop, "float_value", text=prop.name)
    elif prop.data_type == "boolean":
        row.prop(prop, "bool_value", text=prop.name)
    elif prop.data_type == "enum":
        row.prop(prop, "enum_value", text=prop.name)
    row.prop(prop, "is_null", icon="RADIOBUT_OFF" if prop.is_null else "RADIOBUT_ON", text="")
    if (
        "length" in prop.name.lower()
        or "width" in prop.name.lower()
        or "height" in prop.name.lower()
        or "depth" in prop.name.lower()
        or "perimeter" in prop.name.lower()
    ):
        op = row.operator("bim.guess_quantity", icon="IPO_EASE_IN_OUT", text="")
        op.prop = prop.name
    elif "area" in prop.name.lower():
        op = row.operator("bim.guess_quantity", icon="MESH_CIRCLE", text="")
        op.prop = prop.name
    elif "volume" in prop.name.lower():
        op = row.operator("bim.guess_quantity", icon="SPHERE", text="")
        op.prop = prop.name


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
        if not IfcStore.get_element(props.ifc_definition_id):
            return False
        if props.ifc_definition_id not in Data.products:
            Data.load(IfcStore.get_file(), props.ifc_definition_id)
        if not Data.products[props.ifc_definition_id]:
            return False
        return True

    def draw(self, context):
        oprops = context.active_object.BIMObjectProperties
        props = context.active_object.PsetProperties
        if not oprops.ifc_definition_id:
            return
        if oprops.ifc_definition_id not in Data.products:
            Data.load(IfcStore.get_file(), oprops.ifc_definition_id)
        row = self.layout.row(align=True)
        row.prop(props, "pset_name", text="")
        op = row.operator("bim.add_pset", icon="ADD", text="")
        op.obj = context.active_object.name
        op.obj_type = "Object"

        psets = [(pset_id, Data.psets[pset_id]) for pset_id in Data.products[oprops.ifc_definition_id]["psets"]]
        for pset_id, pset in sorted(psets, key = lambda v: v[1]["Name"]):
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
        if not IfcStore.get_element(props.ifc_definition_id):
            return False
        if props.ifc_definition_id not in Data.products:
            Data.load(IfcStore.get_file(), props.ifc_definition_id)
        if not Data.products[props.ifc_definition_id]:
            return False
        return True

    def draw(self, context):
        oprops = context.active_object.BIMObjectProperties
        props = context.active_object.PsetProperties
        if not oprops.ifc_definition_id:
            return
        if oprops.ifc_definition_id not in Data.products:
            Data.load(IfcStore.get_file(), oprops.ifc_definition_id)
        row = self.layout.row(align=True)
        row.prop(props, "qto_name", text="")
        row.operator("bim.add_qto", icon="ADD", text="")

        qtos = [(qto_id, Data.qtos[qto_id]) for qto_id in Data.products[oprops.ifc_definition_id]["qtos"]]
        for qto_id, qto in sorted(qtos, key = lambda v: v[1]["Name"]):
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
        if not context.active_object.active_material:
            return False
        props = context.active_object.active_material.BIMObjectProperties
        if not props.ifc_definition_id:
            return False
        if IfcStore.get_file().schema == "IFC2X3":
            return False  # We don't support material psets in IFC2X3 because they suck
        if props.ifc_definition_id not in Data.products:
            Data.load(IfcStore.get_file(), props.ifc_definition_id)
        if not Data.products[props.ifc_definition_id]:
            return False
        return True

    def draw(self, context):
        oprops = context.active_object.active_material.BIMObjectProperties
        props = context.active_object.active_material.PsetProperties
        if not oprops.ifc_definition_id:
            return
        if oprops.ifc_definition_id not in Data.products:
            Data.load(IfcStore.get_file(), oprops.ifc_definition_id)
        row = self.layout.row(align=True)
        row.prop(props, "material_pset_name", text="")
        op = row.operator("bim.add_pset", icon="ADD", text="")
        op.obj = context.active_object.active_material.name
        op.obj_type = "Material"

        psets = [(pset_id, Data.psets[pset_id]) for pset_id in Data.products[oprops.ifc_definition_id]["psets"]]
        for pset_id, pset in sorted(psets, key = lambda v: v[1]["Name"]):
            draw_psetqto_ui(context, pset_id, pset, props, self.layout, "Material")
