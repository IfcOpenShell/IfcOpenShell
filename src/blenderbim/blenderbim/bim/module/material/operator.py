import bpy
import json
import ifcopenshell.api
import ifcopenshell.util.attribute
from blenderbim.bim.module.material.prop import purge as material_prop_purge
from blenderbim.bim.ifc import IfcStore
from ifcopenshell.api.material.data import Data
from ifcopenshell.api.profile.data import Data as ProfileData


class AssignParameterizedProfile(bpy.types.Operator):
    bl_idname = "bim.assign_parameterized_profile"
    bl_label = "Assign Parameterized Profile"
    ifc_class: bpy.props.StringProperty()
    material_profile: bpy.props.IntProperty()
    obj: bpy.props.StringProperty()

    def execute(self, context):
        obj = bpy.data.objects.get(self.obj) if self.obj else bpy.context.active_object
        self.file = IfcStore.get_file()
        profile = ifcopenshell.api.run(
            "profile.add_parameterized_profile",
            self.file,
            **{"ifc_class": self.ifc_class},
        )
        ifcopenshell.api.run(
            "material.assign_profile",
            self.file,
            **{"material_profile": self.file.by_id(self.material_profile), "profile": profile}
        )
        Data.load_profiles()
        ProfileData.load(self.file)
        bpy.ops.bim.enable_editing_material_set_item(obj=obj.name, material_set_item=self.material_profile)
        return {"FINISHED"}


class AddMaterial(bpy.types.Operator):
    bl_idname = "bim.add_material"
    bl_label = "Add Material"
    obj: bpy.props.StringProperty()

    def execute(self, context):
        obj = bpy.data.materials.get(self.obj) if self.obj else bpy.context.active_object.active_material
        self.file = IfcStore.get_file()
        result = ifcopenshell.api.run("material.add_material", self.file, **{"Name": obj.name})
        obj.BIMObjectProperties.ifc_definition_id = result.id()
        Data.load(IfcStore.get_file())
        material_prop_purge()
        return {"FINISHED"}


class RemoveMaterial(bpy.types.Operator):
    bl_idname = "bim.remove_material"
    bl_label = "Remove Material"
    obj: bpy.props.StringProperty()

    def execute(self, context):
        obj = bpy.data.materials.get(self.obj) if self.obj else bpy.context.active_object.active_material
        self.file = IfcStore.get_file()
        result = ifcopenshell.api.run(
            "material.remove_material",
            self.file,
            **{"material": self.file.by_id(obj.BIMObjectProperties.ifc_definition_id)},
        )
        obj.BIMObjectProperties.ifc_definition_id = 0
        Data.load(IfcStore.get_file())
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
        ifcopenshell.api.run(
            "material.assign_material",
            self.file,
            **{
                "product": self.file.by_id(obj.BIMObjectProperties.ifc_definition_id),
                "type": material_type,
                "material": self.file.by_id(int(obj.BIMObjectMaterialProperties.material)),
            },
        )
        Data.load(IfcStore.get_file())
        Data.load(IfcStore.get_file(), obj.BIMObjectProperties.ifc_definition_id)
        return {"FINISHED"}


class UnassignMaterial(bpy.types.Operator):
    bl_idname = "bim.unassign_material"
    bl_label = "Unassign Material"
    obj: bpy.props.StringProperty()

    def execute(self, context):
        obj = bpy.data.objects.get(self.obj) if self.obj else bpy.context.active_object
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "material.unassign_material",
            self.file,
            **{"product": self.file.by_id(obj.BIMObjectProperties.ifc_definition_id)},
        )
        Data.load(IfcStore.get_file(), obj.BIMObjectProperties.ifc_definition_id)
        return {"FINISHED"}


class AddConstituent(bpy.types.Operator):
    bl_idname = "bim.add_constituent"
    bl_label = "Add Constituent"
    obj: bpy.props.StringProperty()
    constituent_set: bpy.props.IntProperty()

    def execute(self, context):
        obj = bpy.data.objects.get(self.obj) if self.obj else bpy.context.active_object
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "material.add_constituent",
            self.file,
            **{
                "constituent_set": self.file.by_id(self.constituent_set),
                "material": self.file.by_id(int(obj.BIMObjectMaterialProperties.material)),
            },
        )
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
        ifcopenshell.api.run(
            "material.remove_constituent", self.file, **{"constituent": self.file.by_id(self.constituent)}
        )
        Data.load_constituents()
        return {"FINISHED"}


class AddProfile(bpy.types.Operator):
    bl_idname = "bim.add_profile"
    bl_label = "Add Profile"
    obj: bpy.props.StringProperty()
    profile_set: bpy.props.IntProperty()

    def execute(self, context):
        obj = bpy.data.objects.get(self.obj) if self.obj else bpy.context.active_object
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "material.add_profile",
            self.file,
            **{
                "profile_set": self.file.by_id(self.profile_set),
                "material": self.file.by_id(int(obj.BIMObjectMaterialProperties.material)),
            },
        )
        Data.load_profiles()
        return {"FINISHED"}


class RemoveProfile(bpy.types.Operator):
    bl_idname = "bim.remove_profile"
    bl_label = "Remove Profile"
    obj: bpy.props.StringProperty()
    profile: bpy.props.IntProperty()

    def execute(self, context):
        obj = bpy.data.objects.get(self.obj) if self.obj else bpy.context.active_object
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "material.remove_profile", self.file, **{"profile": self.file.by_id(self.profile)}
        )
        Data.load_profiles()
        return {"FINISHED"}


class AddLayer(bpy.types.Operator):
    bl_idname = "bim.add_layer"
    bl_label = "Add Layer"
    obj: bpy.props.StringProperty()
    layer_set: bpy.props.IntProperty()

    def execute(self, context):
        obj = bpy.data.objects.get(self.obj) if self.obj else bpy.context.active_object
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "material.add_layer",
            self.file,
            **{
                "layer_set": self.file.by_id(self.layer_set),
                "material": self.file.by_id(int(obj.BIMObjectMaterialProperties.material)),
            },
        )
        Data.load_layers()
        return {"FINISHED"}


class ReorderMaterialSetItem(bpy.types.Operator):
    bl_idname = "bim.reorder_material_set_item"
    bl_label = "Reorder Material Set Item"
    obj: bpy.props.StringProperty()
    old_index: bpy.props.IntProperty()
    new_index: bpy.props.IntProperty()
    material_set: bpy.props.IntProperty()

    def execute(self, context):
        obj = bpy.data.objects.get(self.obj) if self.obj else bpy.context.active_object
        self.file = IfcStore.get_file()
        material_set = self.file.by_id(self.material_set)
        ifcopenshell.api.run(
            "material.reorder_set_item",
            self.file,
            **{
                "material_set": material_set,
                "old_index": self.old_index,
                "new_index": self.new_index,
            },
        )
        if material_set.is_a("IfcMaterialConstituentSet"):
            Data.load_constituents()
        elif material_set.is_a("IfcMaterialLayerSet"):
            Data.load_layers()
        elif material_set.is_a("IfcMaterialProfileSet"):
            Data.load_profiles()
        elif material_set.is_a("IfcMaterialList"):
            Data.load_lists()
        return {"FINISHED"}


class RemoveLayer(bpy.types.Operator):
    bl_idname = "bim.remove_layer"
    bl_label = "Remove Layer"
    obj: bpy.props.StringProperty()
    layer: bpy.props.IntProperty()

    def execute(self, context):
        obj = bpy.data.objects.get(self.obj) if self.obj else bpy.context.active_object
        self.file = IfcStore.get_file()
        ifcopenshell.api.run("material.remove_layer", self.file, **{"layer": self.file.by_id(self.layer)})
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
        ifcopenshell.api.run(
            "material.add_list_item",
            self.file,
            **{
                "material_list": self.file.by_id(self.list_item_set),
                "material": self.file.by_id(int(obj.BIMObjectMaterialProperties.material)),
            },
        )
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
        ifcopenshell.api.run(
            "material.remove_list_item",
            self.file,
            **{
                "material_list": self.file.by_id(self.list_item_set),
                "material": self.file.by_id(self.list_item),
            },
        )
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
            Data.load(IfcStore.get_file(), obj.BIMObjectProperties.ifc_definition_id)
            bpy.ops.bim.disable_editing_assigned_material(obj=obj.name)
            return {"FINISHED"}

        attributes = {}
        for attribute in props.material_set_attributes:
            attributes[attribute.name] = None if attribute.is_null else attribute.string_value
        ifcopenshell.api.run(
            "material.edit_assigned_material",
            self.file,
            **{
                "element": material_set,
                "attributes": attributes,
            },
        )
        Data.load(IfcStore.get_file(), obj.BIMObjectProperties.ifc_definition_id)
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
        self.props = obj.BIMObjectMaterialProperties
        self.props.active_material_set_item_id = self.material_set_item
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

        self.props.material_set_item_material = str(material_set_item_data["Material"])

        self.load_set_item_attributes(material_set_item, material_set_item_data)
        if material_set_item.is_a("IfcMaterialProfile"):
            self.load_profile_attributes(material_set_item, material_set_item_data)

        return {"FINISHED"}

    def load_set_item_attributes(self, material_set_item, material_set_item_data):
        while len(self.props.material_set_item_attributes) > 0:
            self.props.material_set_item_attributes.remove(0)

        for attribute in IfcStore.get_schema().declaration_by_name(material_set_item.is_a()).all_attributes():
            data_type = ifcopenshell.util.attribute.get_primitive_type(attribute)
            if data_type == "entity":
                continue
            if attribute.name() in material_set_item_data:
                new = self.props.material_set_item_attributes.add()
                new.name = attribute.name()
                new.is_null = material_set_item_data[attribute.name()] is None
                new.data_type = data_type
                if data_type == "string":
                    new.string_value = "" if new.is_null else material_set_item_data[attribute.name()]
                elif data_type == "float":
                    new.float_value = 0.0 if new.is_null else material_set_item_data[attribute.name()]
                elif data_type == "integer":
                    new.int_value = 0 if new.is_null else material_set_item_data[attribute.name()]
                elif data_type == "boolean":
                    new.bool_value = False if new.is_null else material_set_item_data[attribute.name()]

    def load_profile_attributes(self, material_set_item, material_set_item_data):
        while len(self.props.material_set_item_profile_attributes) > 0:
            self.props.material_set_item_profile_attributes.remove(0)

        if not material_set_item_data["Profile"]:
            return

        profile = self.file.by_id(material_set_item_data["Profile"])
        profile_data = ProfileData.profiles[material_set_item_data["Profile"]]

        for attribute in IfcStore.get_schema().declaration_by_name(profile.is_a()).all_attributes():
            data_type = ifcopenshell.util.attribute.get_primitive_type(attribute)
            if data_type == "entity":
                continue
            if attribute.name() in profile_data:
                new = self.props.material_set_item_profile_attributes.add()
                new.name = attribute.name()
                new.is_null = profile_data[attribute.name()] is None
                new.is_optional = attribute.optional()
                new.data_type = data_type
                if data_type == "string":
                    new.string_value = "" if new.is_null else profile_data[attribute.name()]
                elif data_type == "float":
                    new.float_value = 0.0 if new.is_null else profile_data[attribute.name()]
                elif data_type == "integer":
                    new.int_value = 0 if new.is_null else profile_data[attribute.name()]
                elif data_type == "boolean":
                    new.bool_value = False if new.is_null else profile_data[attribute.name()]
                elif data_type == "enum":
                    new.enum_items = json.dumps(ifcopenshell.util.attribute.get_enum_items(attribute))
                    if profile_data[attribute.name()]:
                        new.enum_value = profile_data[attribute.name()]

                # Force null to be false if the attribute is mandatory because when we first assign a profile, all of
                # its fields are null (which is illegal).
                # TODO: find a better solution.
                if not new.is_optional:
                    new.is_null = False


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
            ifcopenshell.api.run(
                "material.edit_constituent",
                self.file,
                **{
                    "constituent": self.file.by_id(self.material_set_item),
                    "attributes": attributes,
                    "material": self.file.by_id(int(obj.BIMObjectMaterialProperties.material_set_item_material)),
                },
            )
            Data.load_constituents()
        elif product_data["type"] == "IfcMaterialLayerSet" or product_data["type"] == "IfcMaterialLayerSetUsage":
            ifcopenshell.api.run(
                "material.edit_layer",
                self.file,
                **{
                    "layer": self.file.by_id(self.material_set_item),
                    "attributes": attributes,
                    "material": self.file.by_id(int(obj.BIMObjectMaterialProperties.material_set_item_material)),
                },
            )
            Data.load_layers()
        elif product_data["type"] == "IfcMaterialProfileSet":
            profile_attributes = {}
            for attribute in props.material_set_item_profile_attributes:
                if attribute.data_type == "string":
                    value = attribute.string_value
                elif attribute.data_type == "float":
                    value = attribute.float_value
                elif attribute.data_type == "integer":
                    value = attribute.int_value
                elif attribute.data_type == "boolean":
                    value = attribute.bool_value
                elif attribute.data_type == "enum":
                    value = attribute.enum_value
                profile_attributes[attribute.name] = None if attribute.is_null else value
            ifcopenshell.api.run(
                "material.edit_profile",
                self.file,
                **{
                    "profile": self.file.by_id(self.material_set_item),
                    "attributes": attributes,
                    "profile_attributes": profile_attributes,
                    "material": self.file.by_id(int(obj.BIMObjectMaterialProperties.material_set_item_material)),
                },
            )
            Data.load_profiles()
            ProfileData.load(self.file)
        else:
            pass

        bpy.ops.bim.disable_editing_material_set_item(obj=obj.name)
        return {"FINISHED"}
