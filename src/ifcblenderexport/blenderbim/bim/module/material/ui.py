from bpy.types import Panel
from blenderbim.bim.module.material.data import Data
from blenderbim.bim.ifc import IfcStore


class BIM_PT_material(Panel):
    bl_label = "IFC Material"
    bl_idname = "BIM_PT_material"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "material"

    def draw(self, context):
        row = self.layout.row()
        if bool(context.active_object.active_material.BIMObjectProperties.ifc_definition_id):
            row.operator("bim.remove_material", icon="X", text="Remove IFC Material")
        else:
            row.operator("bim.add_material", icon="ADD", text="Create IFC Material")


class BIM_PT_object_material(Panel):
    bl_label = "IFC Object Material"
    bl_idname = "BIM_PT_object_material"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        props = context.active_object.BIMObjectProperties
        if not props.ifc_definition_id:
            return False
        if not hasattr(IfcStore.get_file().by_id(props.ifc_definition_id), "HasAssociations"):
            return False
        return True

    def draw(self, context):
        self.file = IfcStore.get_file()
        self.oprops = context.active_object.BIMObjectProperties
        self.props = context.active_object.BIMObjectMaterialProperties
        if not Data.is_loaded:
            Data.load()
        if self.oprops.ifc_definition_id not in Data.products:
            Data.load(self.oprops.ifc_definition_id)
        self.product_data = Data.products[self.oprops.ifc_definition_id]

        if not Data.materials:
            row = self.layout.row()
            row.label(text="No Materials Available")
            return

        if self.product_data:
            if self.product_data["type"] == "IfcMaterialConstituentSet":
                self.material_set_data = Data.constituent_sets[self.product_data["id"]]
                self.set_items = self.material_set_data["MaterialConstituents"]
                self.set_data = Data.constituents
                self.set_item_name = "constituent"
            elif self.product_data["type"] == "IfcMaterialLayerSet":
                self.material_set_data = Data.layer_sets[self.product_data["id"]]
                self.set_items = self.material_set_data["MaterialLayers"]
                self.set_data = Data.layers
                self.set_item_name = "layer"
            elif self.product_data["type"] == "IfcMaterialProfileSet":
                self.material_set_data = Data.profile_sets[self.product_data["id"]]
                self.set_items = self.material_set_data["MaterialProfiles"]
                self.set_data = Data.profiles
                self.set_item_name = "profile"
            elif self.product_data["type"] == "IfcMaterialList":
                self.material_set_data = Data.lists[self.product_data["id"]]
                self.set_items = self.material_set_data["Materials"]
                self.set_item_name = "list_item"
            return self.draw_material_ui()

        row = self.layout.row(align=True)
        row.prop(self.props, "material_type", text="")
        if self.props.material_type == "IfcMaterial" or self.props.material_type == "IfcMaterialList":
            row.prop(self.props, "material", text="")
        row.operator("bim.assign_material", icon="ADD", text="")

    def draw_material_ui(self):
        row = self.layout.row(align=True)
        row.label(text=self.product_data["type"])

        if self.props.is_editing:
            row.operator("bim.edit_assigned_material", icon="CHECKMARK", text="")
            row.operator("bim.disable_editing_assigned_material", icon="X", text="")
        else:
            row.operator("bim.enable_editing_assigned_material", icon="GREASEPENCIL", text="")
            row.operator("bim.unassign_material", icon="X", text="")

        if self.product_data["type"] == "IfcMaterial":
            self.draw_single_ui()
        else:
            self.draw_set_ui()

    def draw_single_ui(self):
        if self.props.is_editing:
            return self.draw_editable_single_ui()
        return self.draw_read_only_single_ui()

    def draw_editable_single_ui(self):
        row = self.layout.row(align=True)
        row.prop(self.props, "material", text="")

    def draw_read_only_single_ui(self):
        material = Data.materials[self.product_data["id"]]
        row = self.layout.row(align=True)
        row.label(text="Name")
        row.label(text=material["Name"])

    def draw_set_ui(self):
        if self.props.is_editing:
            return self.draw_editable_set_ui()
        self.draw_read_only_set_ui()

    def draw_editable_set_ui(self):
        for attribute in self.props.material_set_attributes:
            row = self.layout.row(align=True)
            row.prop(attribute, "string_value", text=attribute.name)
            row.prop(attribute, "is_null", icon="RADIOBUT_OFF" if attribute.is_null else "RADIOBUT_ON", text="")
        row = self.layout.row(align=True)
        row.prop(self.props, "material", text="")

        op = row.operator(f"bim.add_{self.set_item_name}", icon="ADD", text="")
        setattr(op, f"{self.set_item_name}_set", self.product_data["id"])

        total_items = len(self.set_items)
        for index, set_item_id in enumerate(self.set_items):
            if self.props.active_material_set_item_id == set_item_id:
                self.draw_editable_set_item_ui(set_item_id)
            else:
                self.draw_read_only_set_item_ui(set_item_id, is_first=index == 0, is_last=index == total_items - 1)

    def draw_editable_set_item_ui(self, set_item_id):
        item = self.set_data[set_item_id]
        material = Data.materials[item["Material"]]

        box = self.layout.box()
        row = box.row(align=True)
        row.prop(self.props, "material_set_item_material", icon="MATERIAL")
        op = row.operator("bim.edit_material_set_item", icon="CHECKMARK", text="")
        op.material_set_item = set_item_id
        row.operator("bim.disable_editing_material_set_item", icon="X", text="")

        for attribute in self.props.material_set_item_attributes:
            row = box.row(align=True)
            if attribute.data_type == "string":
                row.prop(attribute, "string_value", text=attribute.name)
            elif attribute.data_type == "integer":
                row.prop(attribute, "int_value", text=attribute.name)
            elif attribute.data_type == "float":
                row.prop(attribute, "float_value", text=attribute.name)
            elif attribute.data_type == "boolean":
                row.prop(attribute, "bool_value", text=attribute.name)
            row.prop(attribute, "is_null", icon="RADIOBUT_OFF" if attribute.is_null else "RADIOBUT_ON", text="")

    def draw_read_only_set_item_ui(self, set_item_id, is_first=False, is_last=False):
        if self.product_data["type"] == "IfcMaterialList":
            item = Data.materials[set_item_id]
            row = self.layout.row(align=True)
            row.label(text="IfcMaterial", icon="ALIGN_CENTER")
            row.label(text=item["Name"], icon="MATERIAL")
        else:
            item = self.set_data[set_item_id]
            row = self.layout.row(align=True)
            row.label(text=item.get("Name", "Unnamed"), icon="ALIGN_CENTER")
            row.label(text=Data.materials[item["Material"]]["Name"], icon="MATERIAL")

        if not is_first:
            row.operator("bim.edit_attributes", icon="TRIA_UP", text="")
        if not is_last:
            row.operator("bim.edit_attributes", icon="TRIA_DOWN", text="")
        if not self.props.active_material_set_item_id and self.product_data["type"] != "IfcMaterialList":
            op = row.operator("bim.enable_editing_material_set_item", icon="GREASEPENCIL", text="")
            op.material_set_item = set_item_id
        op = row.operator(f"bim.remove_{self.set_item_name}", icon="X", text="")
        if self.product_data["type"] == "IfcMaterialList":
            setattr(op, "list_item_set", self.product_data["id"])
        setattr(op, self.set_item_name, item["id"])

    def draw_read_only_set_ui(self):
        name_attr = "LayerSetName" if self.product_data["type"] == "IfcMaterialLayerSet" else "Name"
        row = self.layout.row(align=True)
        row.label(text=name_attr)
        row.label(text=self.material_set_data.get(name_attr, "Unnamed"))
        if hasattr(self.material_set_data, "Description") and self.material_set_data["Description"]:
            row = self.layout.row(align=True)
            row.label(text="Description")
            row.label(text=str(self.material_set_data["Description"]))

        for item_id in self.set_items:
            if self.product_data["type"] == "IfcMaterialList":
                row = self.layout.row(align=True)
                row.label(text="IfcMaterial", icon="ALIGN_CENTER")
                row.label(text=Data.materials[item_id]["Name"], icon="MATERIAL")
            else:
                item = self.set_data[item_id]
                row = self.layout.row(align=True)
                row.label(text=item.get("Name", "Unnamed"), icon="ALIGN_CENTER")
                row.label(text=Data.materials[item["Material"]]["Name"], icon="MATERIAL")
