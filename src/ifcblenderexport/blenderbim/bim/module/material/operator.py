import bpy
import blenderbim.bim.module.material.add_material as add_material
import blenderbim.bim.module.material.remove_material as remove_material
import blenderbim.bim.module.material.assign_material as assign_material
import blenderbim.bim.module.material.unassign_material as unassign_material
import blenderbim.bim.module.material.add_constituent as add_constituent
import blenderbim.bim.module.material.remove_constituent as remove_constituent
import blenderbim.bim.module.material.add_layer as add_layer
import blenderbim.bim.module.material.edit_layer as edit_layer
import blenderbim.bim.module.material.remove_layer as remove_layer
import blenderbim.bim.module.material.reorder_layer as reorder_layer
import blenderbim.bim.module.material.add_list_item as add_list_item
import blenderbim.bim.module.material.remove_list_item as remove_list_item
import blenderbim.bim.module.material.edit_assigned_material as edit_assigned_material
from blenderbim.bim.ifc import IfcStore
from blenderbim.bim.module.material.data import Data


class AddMaterial(bpy.types.Operator):
    bl_idname = "bim.add_material"
    bl_label = "Add Material"
    obj: bpy.props.StringProperty()

    def execute(self, context):
        obj = bpy.data.materials.get(self.obj) if self.obj else bpy.context.active_object.active_material
        self.file = IfcStore.get_file()
        result = add_material.Usecase(self.file, {"Name": obj.name}).execute()
        obj.BIMObjectProperties.ifc_definition_id = result.id()
        Data.load()
        return {"FINISHED"}


class RemoveMaterial(bpy.types.Operator):
    bl_idname = "bim.remove_material"
    bl_label = "Remove Material"
    obj: bpy.props.StringProperty()

    def execute(self, context):
        obj = bpy.data.materials.get(self.obj) if self.obj else bpy.context.active_object.active_material
        self.file = IfcStore.get_file()
        result = remove_material.Usecase(
            self.file, {"material": self.file.by_id(obj.BIMObjectProperties.ifc_definition_id)}
        ).execute()
        obj.BIMObjectProperties.ifc_definition_id = 0
        Data.load()
        return {"FINISHED"}


class AssignMaterial(bpy.types.Operator):
    bl_idname = "bim.assign_material"
    bl_label = "Assign Material"
    obj: bpy.props.StringProperty()
    material_type: bpy.props.StringProperty()

    def execute(self, context):
        obj = bpy.data.objects.get(self.obj) if self.obj else bpy.context.active_object
        material_type = self.material_type or obj.BIMObjectMaterialProperties.material_type
        self.file = IfcStore.get_file()
        assign_material.Usecase(
            self.file,
            {
                "product": self.file.by_id(obj.BIMObjectProperties.ifc_definition_id),
                "type": material_type,
                "material": self.file.by_id(int(obj.BIMObjectMaterialProperties.material)),
            },
        ).execute()
        Data.load()
        Data.load(obj.BIMObjectProperties.ifc_definition_id)
        return {"FINISHED"}


class UnassignMaterial(bpy.types.Operator):
    bl_idname = "bim.unassign_material"
    bl_label = "Unassign Material"
    obj: bpy.props.StringProperty()

    def execute(self, context):
        obj = bpy.data.objects.get(self.obj) if self.obj else bpy.context.active_object
        self.file = IfcStore.get_file()
        unassign_material.Usecase(
            self.file, {"product": self.file.by_id(obj.BIMObjectProperties.ifc_definition_id)}
        ).execute()
        Data.load(obj.BIMObjectProperties.ifc_definition_id)
        return {"FINISHED"}


class AddConstituent(bpy.types.Operator):
    bl_idname = "bim.add_constituent"
    bl_label = "Add Constituent"
    obj: bpy.props.StringProperty()
    constituent_set: bpy.props.IntProperty()

    def execute(self, context):
        obj = bpy.data.objects.get(self.obj) if self.obj else bpy.context.active_object
        self.file = IfcStore.get_file()
        add_constituent.Usecase(
            self.file,
            {
                "constituent_set": self.file.by_id(self.constituent_set),
                "material": self.file.by_id(int(obj.BIMObjectMaterialProperties.material)),
            },
        ).execute()
        Data.load_constituents()
        return {"FINISHED"}


class RemoveConstituent(bpy.types.Operator):
    bl_idname = "bim.remove_constituent"
    bl_label = "Remove Constituent"
    obj: bpy.props.StringProperty()
    constituent: bpy.props.IntProperty()

    def execute(self, context):
        obj = bpy.data.objects.get(self.obj) if self.obj else bpy.context.active_object
        self.file = IfcStore.get_file()
        remove_constituent.Usecase(self.file, {"constituent": self.file.by_id(self.constituent)}).execute()
        Data.load_constituents()
        return {"FINISHED"}


class AddLayer(bpy.types.Operator):
    bl_idname = "bim.add_layer"
    bl_label = "Add Layer"
    obj: bpy.props.StringProperty()
    layer_set: bpy.props.IntProperty()

    def execute(self, context):
        obj = bpy.data.objects.get(self.obj) if self.obj else bpy.context.active_object
        self.file = IfcStore.get_file()
        add_layer.Usecase(
            self.file,
            {
                "layer_set": self.file.by_id(self.layer_set),
                "material": self.file.by_id(int(obj.BIMObjectMaterialProperties.material)),
            },
        ).execute()
        Data.load_layers()
        return {"FINISHED"}


class ReorderLayer(bpy.types.Operator):
    bl_idname = "bim.reorder_layer"
    bl_label = "Reorder Layer"
    obj: bpy.props.StringProperty()
    old_index: bpy.props.IntProperty()
    new_index: bpy.props.IntProperty()
    layer_set: bpy.props.IntProperty()

    def execute(self, context):
        obj = bpy.data.objects.get(self.obj) if self.obj else bpy.context.active_object
        self.file = IfcStore.get_file()
        reorder_layer.Usecase(
            self.file,
            {
                "layer_set": self.file.by_id(self.layer_set),
                "old_index": self.old_index,
                "new_index": self.new_index,
            },
        ).execute()
        Data.load_layers()
        return {"FINISHED"}


class RemoveLayer(bpy.types.Operator):
    bl_idname = "bim.remove_layer"
    bl_label = "Remove Layer"
    obj: bpy.props.StringProperty()
    layer: bpy.props.IntProperty()

    def execute(self, context):
        obj = bpy.data.objects.get(self.obj) if self.obj else bpy.context.active_object
        self.file = IfcStore.get_file()
        remove_layer.Usecase(self.file, {"layer": self.file.by_id(self.layer)}).execute()
        Data.load_layers()
        return {"FINISHED"}


class AddListItem(bpy.types.Operator):
    bl_idname = "bim.add_list_item"
    bl_label = "Add List Item"
    obj: bpy.props.StringProperty()
    list_item_set: bpy.props.IntProperty()

    def execute(self, context):
        obj = bpy.data.objects.get(self.obj) if self.obj else bpy.context.active_object
        self.file = IfcStore.get_file()
        add_list_item.Usecase(
            self.file,
            {
                "material_list": self.file.by_id(self.list_item_set),
                "material": self.file.by_id(int(obj.BIMObjectMaterialProperties.material)),
            },
        ).execute()
        Data.load_lists()
        return {"FINISHED"}


class RemoveListItem(bpy.types.Operator):
    bl_idname = "bim.remove_list_item"
    bl_label = "Remove List Item"
    obj: bpy.props.StringProperty()
    list_item_set: bpy.props.IntProperty()
    list_item: bpy.props.IntProperty()

    def execute(self, context):
        obj = bpy.data.objects.get(self.obj) if self.obj else bpy.context.active_object
        self.file = IfcStore.get_file()
        remove_list_item.Usecase(
            self.file,
            {
                "material_list": self.file.by_id(self.list_item_set),
                "material": self.file.by_id(self.list_item),
            },
        ).execute()
        Data.load_lists()
        return {"FINISHED"}


class EnableEditingAssignedMaterial(bpy.types.Operator):
    bl_idname = "bim.enable_editing_assigned_material"
    bl_label = "Enable Editing Assigned Material"
    obj: bpy.props.StringProperty()

    def execute(self, context):
        obj = bpy.data.objects.get(self.obj) if self.obj else bpy.context.active_object
        props = obj.BIMObjectMaterialProperties
        props.is_editing = True
        product_data = Data.products[obj.BIMObjectProperties.ifc_definition_id]

        if product_data["type"] == "IfcMaterial":
            props.material = str(product_data["id"])
            return {"FINISHED"}

        material_set_class = product_data["type"]
        if product_data["type"] == "IfcMaterialConstituentSet":
            material_set_data = Data.constituent_sets[product_data["id"]]
        elif product_data["type"] == "IfcMaterialLayerSet":
            material_set_data = Data.layer_sets[product_data["id"]]
        elif product_data["type"] == "IfcMaterialLayerSetUsage":
            layer_set_usage = Data.layer_set_usages[product_data["id"]]
            material_set_data = Data.layer_sets[layer_set_usage["ForLayerSet"]]
            material_set_class = "IfcMaterialLayerSet"
        elif product_data["type"] == "IfcMaterialProfileSet":
            material_set_data = Data.profile_sets[product_data["id"]]
        elif product_data["type"] == "IfcMaterialList":
            material_set_data = Data.lists[product_data["id"]]
        else:
            material_set_data = {}

        while len(props.material_set_attributes) > 0:
            props.material_set_attributes.remove(0)

        for attribute in IfcStore.get_schema().declaration_by_name(material_set_class).all_attributes():
            if "<string>" not in str(attribute.type_of_attribute):
                continue
            if attribute.name() in material_set_data:
                new = props.material_set_attributes.add()
                new.name = attribute.name()
                new.is_null = material_set_data[attribute.name()] is None
                new.string_value = "" if new.is_null else material_set_data[attribute.name()]
        return {"FINISHED"}


class DisableEditingAssignedMaterial(bpy.types.Operator):
    bl_idname = "bim.disable_editing_assigned_material"
    bl_label = "Disable Editing Assigned Material"
    obj: bpy.props.StringProperty()

    def execute(self, context):
        obj = bpy.data.objects.get(self.obj) if self.obj else bpy.context.active_object
        props = obj.BIMObjectMaterialProperties
        props.is_editing = False
        return {"FINISHED"}


class EditAssignedMaterial(bpy.types.Operator):
    bl_idname = "bim.edit_assigned_material"
    bl_label = "Edit Assigned Material"
    obj: bpy.props.StringProperty()
    material_set: bpy.props.IntProperty()

    def execute(self, context):
        self.file = IfcStore.get_file()
        obj = bpy.data.objects.get(self.obj) if self.obj else bpy.context.active_object
        props = obj.BIMObjectMaterialProperties
        product_data = Data.products[obj.BIMObjectProperties.ifc_definition_id]
        material_set = self.file.by_id(self.material_set)

        if product_data["type"] == "IfcMaterial":
            bpy.ops.bim.unassign_material(obj=obj.name)
            bpy.ops.bim.assign_material(obj=obj.name, material_type="IfcMaterial")
            Data.load(obj.BIMObjectProperties.ifc_definition_id)
            bpy.ops.bim.disable_editing_assigned_material(obj=obj.name)
            return {"FINISHED"}

        attributes = {}
        for attribute in props.material_set_attributes:
            attributes[attribute.name] = None if attribute.is_null else attribute.string_value
        edit_assigned_material.Usecase(
            self.file,
            {
                "element": material_set,
                "attributes": attributes,
            },
        ).execute()
        Data.load(obj.BIMObjectProperties.ifc_definition_id)
        if material_set.is_a("IfcMaterialConstituentSet"):
            Data.load_constituents()
        elif material_set.is_a("IfcMaterialLayerSet"):
            Data.load_layers()
        elif material_set.is_a("IfcMaterialProfileSet"):
            Data.load_profiles()
        bpy.ops.bim.disable_editing_assigned_material(obj=obj.name)
        return {"FINISHED"}


class EnableEditingMaterialSetItem(bpy.types.Operator):
    bl_idname = "bim.enable_editing_material_set_item"
    bl_label = "Enable Editing Material Set Item"
    obj: bpy.props.StringProperty()
    material_set_item: bpy.props.IntProperty()

    def execute(self, context):
        self.file = IfcStore.get_file()
        obj = bpy.data.objects.get(self.obj) if self.obj else bpy.context.active_object
        props = obj.BIMObjectMaterialProperties
        props.active_material_set_item_id = self.material_set_item
        product_data = Data.products[obj.BIMObjectProperties.ifc_definition_id]
        material_set_item = self.file.by_id(self.material_set_item)

        if product_data["type"] == "IfcMaterialConstituentSet":
            material_set_item_data = Data.constituents[self.material_set_item]
        elif product_data["type"] == "IfcMaterialLayerSet" or product_data["type"] == "IfcMaterialLayerSetUsage":
            material_set_item_data = Data.layers[self.material_set_item]
        elif product_data["type"] == "IfcMaterialProfileSet":
            material_set_item_data = Data.profiles[self.material_set_item]
        else:
            material_set_item_data = {}

        props.material_set_item_material = str(material_set_item_data["Material"])

        while len(props.material_set_item_attributes) > 0:
            props.material_set_item_attributes.remove(0)

        for attribute in IfcStore.get_schema().declaration_by_name(material_set_item.is_a()).all_attributes():
            data_type = str(attribute.type_of_attribute)
            if "<entity" in data_type:
                continue
            if attribute.name() in material_set_item_data:
                new = props.material_set_item_attributes.add()
                new.name = attribute.name()
                new.is_null = material_set_item_data[attribute.name()] is None
                if "<string>" in data_type:
                    new.string_value = "" if new.is_null else material_set_item_data[attribute.name()]
                    new.data_type = "string"
                elif "<real>" in data_type:
                    new.float_value = 0.0 if new.is_null else material_set_item_data[attribute.name()]
                    new.data_type = "float"
                elif "<integer>" in data_type:
                    new.int_value = 0 if new.is_null else material_set_item_data[attribute.name()]
                    new.data_type = "integer"
                elif "<boolean>" in data_type or "<logical>" in data_type:
                    new.bool_value = False if new.is_null else material_set_item_data[attribute.name()]
                    new.data_type = "boolean"
        return {"FINISHED"}


class DisableEditingMaterialSetItem(bpy.types.Operator):
    bl_idname = "bim.disable_editing_material_set_item"
    bl_label = "Disable Editing Material Set Item"
    obj: bpy.props.StringProperty()

    def execute(self, context):
        obj = bpy.data.objects.get(self.obj) if self.obj else bpy.context.active_object
        props = obj.BIMObjectMaterialProperties
        props.active_material_set_item_id = 0
        return {"FINISHED"}


class EditMaterialSetItem(bpy.types.Operator):
    bl_idname = "bim.edit_material_set_item"
    bl_label = "Edit Material Set Item"
    obj: bpy.props.StringProperty()
    material_set_item: bpy.props.IntProperty()

    def execute(self, context):
        obj = bpy.data.objects.get(self.obj) if self.obj else bpy.context.active_object
        self.file = IfcStore.get_file()
        props = obj.BIMObjectMaterialProperties
        product_data = Data.products[obj.BIMObjectProperties.ifc_definition_id]

        attributes = {}
        for attribute in props.material_set_item_attributes:
            if attribute.data_type == "string":
                value = attribute.string_value
            elif attribute.data_type == "float":
                value = attribute.float_value
            elif attribute.data_type == "integer":
                value = attribute.int_value
            elif attribute.data_type == "boolean":
                value = attribute.bool_value
            attributes[attribute.name] = None if attribute.is_null else value

        if product_data["type"] == "IfcMaterialConstituentSet":
            edit_constituent.Usecase(
                self.file,
                {
                    "constituent": self.file.by_id(self.material_set_item),
                    "attributes": attributes,
                    "material": self.file.by_id(int(obj.BIMObjectMaterialProperties.material_set_item_material)),
                },
            ).execute()
            Data.load_constituents()
        elif product_data["type"] == "IfcMaterialLayerSet" or product_data["type"] == "IfcMaterialLayerSetUsage":
            edit_layer.Usecase(
                self.file,
                {
                    "layer": self.file.by_id(self.material_set_item),
                    "attributes": attributes,
                    "material": self.file.by_id(int(obj.BIMObjectMaterialProperties.material_set_item_material)),
                },
            ).execute()
            Data.load_layers()
        elif product_data["type"] == "IfcMaterialProfileSet":
            edit_profile.Usecase(
                self.file,
                {
                    "profile": self.file.by_id(self.material_set_item),
                    "attributes": attributes,
                    "material": self.file.by_id(int(obj.BIMObjectMaterialProperties.material_set_item_material)),
                },
            ).execute()
            Data.load_profiles()
        else:
            pass

        bpy.ops.bim.disable_editing_material_set_item(obj=obj.name)
        return {"FINISHED"}
