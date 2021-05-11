from bpy.types import Panel
from ifcopenshell.api.material.data import Data
from ifcopenshell.api.profile.data import Data as ProfileData
from blenderbim.bim.ifc import IfcStore


class BIM_PT_material(Panel):
    bl_label = "IFC Material"
    bl_idname = "BIM_PT_material"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "material"

    @classmethod
    def poll(cls, context):
        return IfcStore.get_file() and context.active_object and context.active_object.active_material

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
            Data.load(IfcStore.get_file())
        if self.oprops.ifc_definition_id not in Data.products:
            Data.load(IfcStore.get_file(), self.oprops.ifc_definition_id)
        if not ProfileData.is_loaded:
            ProfileData.load(self.file)
        self.product_data = Data.products[self.oprops.ifc_definition_id]

        if not Data.materials:
            row = self.layout.row()
            row.label(text="No Materials Available")
            return

        if self.product_data:
            if self.product_data["type"] == "IfcMaterialConstituentSet":
                self.material_set_id = self.product_data["id"]
                self.material_set_data = Data.constituent_sets[self.material_set_id]
                self.set_items = self.material_set_data["MaterialConstituents"] or []
                self.set_data = Data.constituents
                self.set_item_name = "constituent"
            elif self.product_data["type"] == "IfcMaterialLayerSet":
                self.material_set_id = self.product_data["id"]
                self.material_set_data = Data.layer_sets[self.material_set_id]
                self.set_items = self.material_set_data["MaterialLayers"] or []
                self.set_data = Data.layers
                self.set_item_name = "layer"
            elif self.product_data["type"] == "IfcMaterialLayerSetUsage":
                self.material_set_usage = Data.layer_set_usages[self.product_data["id"]]
                self.material_set_id = self.material_set_usage["ForLayerSet"]
                self.material_set_data = Data.layer_sets[self.material_set_id]
                self.set_items = self.material_set_data["MaterialLayers"] or []
                self.set_data = Data.layers
                self.set_item_name = "layer"
            elif self.product_data["type"] == "IfcMaterialProfileSet":
                self.material_set_id = self.product_data["id"]
                self.material_set_data = Data.profile_sets[self.material_set_id]
                self.set_items = self.material_set_data["MaterialProfiles"] or []
                self.set_data = Data.profiles
                self.set_item_name = "profile"
            elif self.product_data["type"] == "IfcMaterialProfileSetUsage":
                self.material_set_usage = Data.profile_set_usages[self.product_data["id"]]
                self.material_set_id = self.material_set_usage["ForProfileSet"]
                self.material_set_data = Data.profile_sets[self.material_set_id]
                self.set_items = self.material_set_data["MaterialProfiles"] or []
                self.set_data = Data.profiles
                self.set_item_name = "profile"
            elif self.product_data["type"] == "IfcMaterialList":
                self.material_set_id = self.product_data["id"]
                self.material_set_data = Data.lists[self.material_set_id]
                self.set_items = self.material_set_data["Materials"] or []
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
            op = row.operator("bim.edit_assigned_material", icon="CHECKMARK", text="")
            op.material_set = self.material_set_id
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
        setattr(op, f"{self.set_item_name}_set", self.material_set_id)

        total_items = len(self.set_items)
        for index, set_item_id in enumerate(self.set_items):
            if self.props.active_material_set_item_id == set_item_id:
                self.draw_editable_set_item_ui(set_item_id)
            else:
                self.draw_read_only_set_item_ui(
                    set_item_id, index, is_first=index == 0, is_last=index == total_items - 1
                )

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

        if self.set_item_name == "profile":
            self.draw_assign_profile_ui(box, item)
            self.draw_editable_profile_ui(box, item)

    def draw_assign_profile_ui(self, layout, item):
        row = layout.row(align=True)
        row.prop(self.props, "profile_classes", text="")
        if self.props.profile_classes == "IfcParameterizedProfileDef":
            row.prop(self.props, "parameterized_profile_classes", text="")
            op = row.operator("bim.assign_parameterized_profile", icon="GREASEPENCIL" if item["Profile"] else "ADD", text="")
            op.ifc_class = self.props.parameterized_profile_classes
            op.material_profile = item["id"]
        else:
            # TODO: support non parametric profiles by showing a list of named profiles to select from, or an
            # eyedropper to pick profile geometry from the scene
            row.operator("bim.disable_editing_material_set_item", icon="X", text="")

    def draw_editable_profile_ui(self, layout, item):
        for attribute in self.props.material_set_item_profile_attributes:
            row = layout.row(align=True)
            if attribute.data_type == "string":
                row.prop(attribute, "string_value", text=attribute.name)
            elif attribute.data_type == "integer":
                row.prop(attribute, "int_value", text=attribute.name)
            elif attribute.data_type == "float":
                row.prop(attribute, "float_value", text=attribute.name)
            elif attribute.data_type == "boolean":
                row.prop(attribute, "bool_value", text=attribute.name)
            elif attribute.data_type == "enum":
                row.prop(attribute, "enum_value", text=attribute.name)
            if attribute.is_optional:
                row.prop(attribute, "is_null", icon="RADIOBUT_OFF" if attribute.is_null else "RADIOBUT_ON", text="")

    def draw_read_only_set_item_ui(self, set_item_id, index, is_first=False, is_last=False):
        if self.product_data["type"] == "IfcMaterialList":
            item = Data.materials[set_item_id]
            row = self.layout.row(align=True)
            row.label(text="IfcMaterial", icon="ALIGN_CENTER")
            row.label(text=item["Name"], icon="MATERIAL")
        else:
            item = self.set_data[set_item_id]
            row = self.layout.row(align=True)
            row.label(text=item.get("Name", "Unnamed") or "Unnamed", icon="ALIGN_CENTER")
            row.label(text=Data.materials[item["Material"]]["Name"], icon="MATERIAL")

        if not is_first:
            op = row.operator(f"bim.reorder_material_set_item", icon="TRIA_UP", text="")
            op.old_index = index
            op.new_index = index - 1
            setattr(op, "material_set", self.material_set_id)
        if not is_last:
            op = row.operator(f"bim.reorder_material_set_item", icon="TRIA_DOWN", text="")
            op.old_index = index
            op.new_index = index + 1
            setattr(op, "material_set", self.material_set_id)
        if not self.props.active_material_set_item_id and self.product_data["type"] != "IfcMaterialList":
            op = row.operator("bim.enable_editing_material_set_item", icon="GREASEPENCIL", text="")
            op.material_set_item = set_item_id
        op = row.operator(f"bim.remove_{self.set_item_name}", icon="X", text="")
        if self.product_data["type"] == "IfcMaterialList":
            setattr(op, "list_item_set", self.material_set_id)
        setattr(op, self.set_item_name, item["id"])

    def draw_read_only_set_ui(self):
        if (
            self.product_data["type"] == "IfcMaterialLayerSetUsage"
            or self.product_data["type"] == "IfcMaterialLayerSet"
        ):
            name_attr = "LayerSetName"
        else:
            name_attr = "Name"
        row = self.layout.row(align=True)
        row.label(text=name_attr)
        row.label(text=self.material_set_data.get(name_attr, "Unnamed") or "Unnamed")
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
                row.label(text=item.get("Name", "Unnamed") or "Unnamed", icon="ALIGN_CENTER")
                row.label(text=Data.materials[item["Material"]]["Name"], icon="MATERIAL")
