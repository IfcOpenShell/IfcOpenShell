# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of BlenderBIM Add-on.
#
# BlenderBIM Add-on is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BlenderBIM Add-on is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with BlenderBIM Add-on.  If not, see <http://www.gnu.org/licenses/>.

import bpy
import json
import ifcopenshell.api
import ifcopenshell.util.element
import ifcopenshell.util.attribute
import ifcopenshell.util.representation
import blenderbim.bim.helper
import blenderbim.tool as tool
import blenderbim.core.material as core
import blenderbim.bim.module.model.profile as model_profile
from blenderbim.bim.module.material.prop import purge as material_prop_purge
from blenderbim.bim.ifc import IfcStore
from ifcopenshell.api.material.data import Data


class LoadMaterials(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.load_materials"
    bl_label = "Load Materials"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.load_materials(tool.Material, context.scene.BIMMaterialProperties.material_type)


class DisableEditingMaterials(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.disable_editing_materials"
    bl_label = "Disable Editing Materials"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.disable_editing_materials(tool.Material)


class SelectByMaterial(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.select_by_material"
    bl_label = "Select By Material"
    bl_options = {"REGISTER", "UNDO"}
    material: bpy.props.IntProperty()

    def _execute(self, context):
        core.select_by_material(tool.Material, material=tool.Ifc.get().by_id(self.material))


class AssignParameterizedProfile(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.assign_parameterized_profile"
    bl_label = "Assign Parameterized Profile"
    bl_options = {"REGISTER", "UNDO"}
    ifc_class: bpy.props.StringProperty()
    material_profile: bpy.props.IntProperty()
    obj: bpy.props.StringProperty()

    def _execute(self, context):
        obj = bpy.data.objects.get(self.obj) if self.obj else context.active_object
        self.file = IfcStore.get_file()
        profile = ifcopenshell.api.run(
            "profile.add_parameterized_profile",
            self.file,
            **{"ifc_class": self.ifc_class},
        )
        ifcopenshell.api.run(
            "material.assign_profile",
            self.file,
            **{"material_profile": self.file.by_id(self.material_profile), "profile": profile},
        )
        Data.load_profiles()
        bpy.ops.bim.enable_editing_material_set_item(obj=obj.name, material_set_item=self.material_profile)


class AddMaterial(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_material"
    bl_label = "Add Material"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()

    def _execute(self, context):
        obj = bpy.data.materials.get(self.obj) if self.obj else None
        core.add_material(tool.Ifc, tool.Material, tool.Style, obj=obj)
        Data.load(IfcStore.get_file())
        material_prop_purge()


class AddMaterialSet(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_material_set"
    bl_label = "Add Material Set"
    bl_options = {"REGISTER", "UNDO"}
    set_type: bpy.props.StringProperty()

    def _execute(self, context):
        core.add_material_set(tool.Ifc, tool.Material, set_type=self.set_type)
        Data.load(IfcStore.get_file())
        material_prop_purge()


class RemoveMaterial(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_material"
    bl_label = "Remove Material"
    bl_options = {"REGISTER", "UNDO"}
    material: bpy.props.IntProperty()

    def _execute(self, context):
        core.remove_material(tool.Ifc, tool.Material, tool.Style, material=tool.Ifc.get().by_id(self.material))
        Data.load(IfcStore.get_file())


class RemoveMaterialSet(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_material_set"
    bl_label = "Remove Material Set"
    bl_options = {"REGISTER", "UNDO"}
    material: bpy.props.IntProperty()

    def _execute(self, context):
        core.remove_material_set(tool.Ifc, tool.Material, material=tool.Ifc.get().by_id(self.material))
        Data.load(IfcStore.get_file())


class UnlinkMaterial(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.unlink_material"
    bl_label = "Unlink Material"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.unlink_material(tool.Ifc, obj=context.active_object.active_material)


class AssignMaterial(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.assign_material"
    bl_label = "Assign Material"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()
    material_type: bpy.props.StringProperty()

    def _execute(self, context):
        obj = bpy.data.objects.get(self.obj) if self.obj else context.active_object
        material_type = self.material_type or obj.BIMObjectMaterialProperties.material_type
        self.file = IfcStore.get_file()
        element = self.file.by_id(obj.BIMObjectProperties.ifc_definition_id)
        ifcopenshell.api.run(
            "material.assign_material",
            self.file,
            **{
                "product": element,
                "type": material_type,
                "material": self.file.by_id(int(obj.BIMObjectMaterialProperties.material)),
            },
        )
        Data.load(IfcStore.get_file())
        Data.load(IfcStore.get_file(), obj.BIMObjectProperties.ifc_definition_id)


class UnassignMaterial(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.unassign_material"
    bl_label = "Unassign Material"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()

    def _execute(self, context):
        obj = bpy.data.objects.get(self.obj) if self.obj else context.active_object
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "material.unassign_material",
            self.file,
            **{"product": self.file.by_id(obj.BIMObjectProperties.ifc_definition_id)},
        )
        Data.purge()


class AddConstituent(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_constituent"
    bl_label = "Add Constituent"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()
    constituent_set: bpy.props.IntProperty()

    def _execute(self, context):
        obj = bpy.data.objects.get(self.obj) if self.obj else context.active_object
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


class RemoveConstituent(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_constituent"
    bl_label = "Remove Constituent"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()
    constituent: bpy.props.IntProperty()

    def _execute(self, context):
        obj = bpy.data.objects.get(self.obj) if self.obj else context.active_object
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "material.remove_constituent", self.file, **{"constituent": self.file.by_id(self.constituent)}
        )
        Data.load_constituents()


class AddProfile(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_profile"
    bl_label = "Add Profile"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()
    profile_set: bpy.props.IntProperty()

    def _execute(self, context):
        obj = bpy.data.objects.get(self.obj) if self.obj else context.active_object
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "material.add_profile",
            self.file,
            profile_set=self.file.by_id(self.profile_set),
            material=self.file.by_id(int(obj.BIMObjectMaterialProperties.material)),
            profile=self.file.by_id(int(context.scene.BIMMaterialProperties.profiles)),
        )
        Data.load_profiles()


class RemoveProfile(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_profile"
    bl_label = "Remove Profile"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()
    profile: bpy.props.IntProperty()

    def _execute(self, context):
        obj = bpy.data.objects.get(self.obj) if self.obj else context.active_object
        self.file = IfcStore.get_file()
        ifcopenshell.api.run("material.remove_profile", self.file, **{"profile": self.file.by_id(self.profile)})
        Data.load_profiles()


class AddLayer(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_layer"
    bl_label = "Add Layer"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()
    layer_set: bpy.props.IntProperty()

    def _execute(self, context):
        obj = bpy.data.objects.get(self.obj) if self.obj else context.active_object
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


class ReorderMaterialSetItem(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.reorder_material_set_item"
    bl_label = "Reorder Material Set Item"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()
    old_index: bpy.props.IntProperty()
    new_index: bpy.props.IntProperty()
    material_set: bpy.props.IntProperty()

    def _execute(self, context):
        obj = bpy.data.objects.get(self.obj) if self.obj else context.active_object
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


class RemoveLayer(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_layer"
    bl_label = "Remove Layer"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()
    layer: bpy.props.IntProperty()

    def _execute(self, context):
        obj = bpy.data.objects.get(self.obj) if self.obj else context.active_object
        self.file = IfcStore.get_file()
        ifcopenshell.api.run("material.remove_layer", self.file, **{"layer": self.file.by_id(self.layer)})
        Data.load_layers()


class AddListItem(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_list_item"
    bl_label = "Add List Item"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()
    list_item_set: bpy.props.IntProperty()

    def _execute(self, context):
        obj = bpy.data.objects.get(self.obj) if self.obj else context.active_object
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


class RemoveListItem(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_list_item"
    bl_label = "Remove List Item"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()
    list_item_set: bpy.props.IntProperty()
    list_item: bpy.props.IntProperty()
    list_item_index: bpy.props.IntProperty()

    def _execute(self, context):
        obj = bpy.data.objects.get(self.obj) if self.obj else context.active_object
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "material.remove_list_item",
            self.file,
            **{
                "material_list": self.file.by_id(self.list_item_set),
                "material_index": self.list_item_index,
            },
        )
        Data.load_lists()


class EnableEditingAssignedMaterial(bpy.types.Operator):
    bl_idname = "bim.enable_editing_assigned_material"
    bl_label = "Enable Editing Assigned Material"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()

    def execute(self, context):
        obj = bpy.data.objects.get(self.obj) if self.obj else context.active_object
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
            material_set_usage = Data.layer_set_usages[product_data["id"]]
            material_set_data = Data.layer_sets[material_set_usage["ForLayerSet"]]
            material_set_class = "IfcMaterialLayerSet"
        elif product_data["type"] == "IfcMaterialProfileSet":
            material_set_data = Data.profile_sets[product_data["id"]]
        elif product_data["type"] == "IfcMaterialProfileSetUsage":
            material_set_usage = Data.profile_set_usages[product_data["id"]]
            material_set_data = Data.profile_sets[material_set_usage["ForProfileSet"]]
            material_set_class = "IfcMaterialProfileSet"
        elif product_data["type"] == "IfcMaterialList":
            material_set_data = Data.lists[product_data["id"]]
        else:
            material_set_data = {}

        props.material_set_usage_attributes.clear()

        if "Usage" in product_data["type"]:
            blenderbim.bim.helper.import_attributes(
                product_data["type"], props.material_set_usage_attributes, material_set_usage, self.import_attributes
            )

        props.material_set_attributes.clear()

        blenderbim.bim.helper.import_attributes(material_set_class, props.material_set_attributes, material_set_data)
        return {"FINISHED"}

    def import_attributes(self, name, prop, data):
        if name == "CardinalPoint":
            # TODO: complain to buildingSMART
            cardinal_point_map = {
                1: "bottom left",
                2: "bottom centre",
                3: "bottom right",
                4: "mid-depth left",
                5: "mid-depth centre",
                6: "mid-depth right",
                7: "top left",
                8: "top centre",
                9: "top right",
                10: "geometric centroid",
                11: "bottom in line with the geometric centroid",
                12: "left in line with the geometric centroid",
                13: "right in line with the geometric centroid",
                14: "top in line with the geometric centroid",
                15: "shear centre",
                16: "bottom in line with the shear centre",
                17: "left in line with the shear centre",
                18: "right in line with the shear centre",
                19: "top in line with the shear centre",
            }
            prop.data_type = "enum"
            prop.enum_items = json.dumps(cardinal_point_map)
            if data[name]:
                prop.enum_value = str(data[name])
            return True


class DisableEditingAssignedMaterial(bpy.types.Operator):
    bl_idname = "bim.disable_editing_assigned_material"
    bl_label = "Disable Editing Assigned Material"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()

    def execute(self, context):
        bpy.ops.bim.disable_editing_material_set_item()
        obj = bpy.data.objects.get(self.obj) if self.obj else context.active_object
        props = obj.BIMObjectMaterialProperties
        props.is_editing = False
        return {"FINISHED"}


class EditAssignedMaterial(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.edit_assigned_material"
    bl_label = "Edit Assigned Material"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()
    material_set: bpy.props.IntProperty()
    material_set_usage: bpy.props.IntProperty()

    def _execute(self, context):
        self.file = IfcStore.get_file()
        obj = bpy.data.objects.get(self.obj) if self.obj else context.active_object
        props = obj.BIMObjectMaterialProperties
        product_data = Data.products[obj.BIMObjectProperties.ifc_definition_id]

        if props.active_material_set_item_id != 0:  # We were editing a material layer set item
            bpy.ops.bim.edit_material_set_item(material_set_item=props.active_material_set_item_id)

        if product_data["type"] == "IfcMaterial":
            bpy.ops.bim.unassign_material(obj=obj.name)
            bpy.ops.bim.assign_material(obj=obj.name, material_type="IfcMaterial")
            Data.load(IfcStore.get_file(), obj.BIMObjectProperties.ifc_definition_id)
            bpy.ops.bim.disable_editing_assigned_material(obj=obj.name)
            return {"FINISHED"}

        material_set = self.file.by_id(self.material_set)
        attributes = blenderbim.bim.helper.export_attributes(props.material_set_attributes)
        ifcopenshell.api.run(
            "material.edit_assigned_material",
            self.file,
            **{"element": material_set, "attributes": attributes},
        )
        Data.load(IfcStore.get_file(), obj.BIMObjectProperties.ifc_definition_id)

        if self.material_set_usage:
            material_set_usage = self.file.by_id(self.material_set_usage)
            attributes = blenderbim.bim.helper.export_attributes(props.material_set_usage_attributes)
            if material_set_usage.is_a("IfcMaterialLayerSetUsage"):
                ifcopenshell.api.run(
                    "material.edit_layer_usage",
                    self.file,
                    **{"usage": material_set_usage, "attributes": attributes},
                )
                Data.load_layer_usages()
            elif material_set_usage.is_a("IfcMaterialProfileSetUsage"):
                if attributes.get("CardinalPoint", None):
                    attributes["CardinalPoint"] = int(attributes["CardinalPoint"])
                ifcopenshell.api.run(
                    "material.edit_profile_usage",
                    self.file,
                    **{"usage": material_set_usage, "attributes": attributes},
                )
                Data.load_profile_usages()

        if material_set.is_a("IfcMaterialConstituentSet"):
            Data.load_constituents()
        elif material_set.is_a("IfcMaterialLayerSet"):
            Data.load_layers()
        elif material_set.is_a("IfcMaterialProfileSet"):
            Data.load_profiles()
        bpy.ops.bim.disable_editing_assigned_material(obj=obj.name)


class EnableEditingMaterialSetItemProfile(bpy.types.Operator):
    bl_idname = "bim.enable_editing_material_set_item_profile"
    bl_label = "Enable Editing Material Set Item"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()
    material_set_item: bpy.props.IntProperty()

    def execute(self, context):
        obj = bpy.data.objects.get(self.obj) if self.obj else context.active_object
        self.props = obj.BIMObjectMaterialProperties
        self.props.material_set_item_profile_attributes.clear()
        profile = tool.Ifc.get().by_id(self.material_set_item).Profile
        blenderbim.bim.helper.import_attributes2(profile, self.props.material_set_item_profile_attributes)
        return {"FINISHED"}


class DisableEditingMaterialSetItemProfile(bpy.types.Operator):
    bl_idname = "bim.disable_editing_material_set_item_profile"
    bl_label = "Disable Editing Material Set Item"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()

    def execute(self, context):
        obj = bpy.data.objects.get(self.obj) if self.obj else context.active_object
        self.props = obj.BIMObjectMaterialProperties
        self.props.material_set_item_profile_attributes.clear()
        return {"FINISHED"}


class EditMaterialSetItemProfile(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.edit_material_set_item_profile"
    bl_label = "Edit Material Set Item Profile"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()
    material_set_item: bpy.props.IntProperty()

    def _execute(self, context):
        obj = bpy.data.objects.get(self.obj) if self.obj else context.active_object
        self.props = obj.BIMObjectMaterialProperties
        attributes = blenderbim.bim.helper.export_attributes(self.props.material_set_item_profile_attributes)
        profile = tool.Ifc.get().by_id(self.material_set_item).Profile
        ifcopenshell.api.run("profile.edit_profile", tool.Ifc.get(), profile=profile, attributes=attributes)
        self.props.material_set_item_profile_attributes.clear()
        model_profile.DumbProfileRegenerator().regenerate_from_profile_def(profile)


class EnableEditingMaterialSetItem(bpy.types.Operator):
    bl_idname = "bim.enable_editing_material_set_item"
    bl_label = "Enable Editing Material Set Item"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()
    material_set_item: bpy.props.IntProperty()

    def execute(self, context):
        self.file = IfcStore.get_file()
        obj = bpy.data.objects.get(self.obj) if self.obj else context.active_object
        self.mprops = context.scene.BIMMaterialProperties
        self.props = obj.BIMObjectMaterialProperties
        self.props.active_material_set_item_id = self.material_set_item
        product_data = Data.products[obj.BIMObjectProperties.ifc_definition_id]
        material_set_item = self.file.by_id(self.material_set_item)

        if product_data["type"] == "IfcMaterialConstituentSet":
            material_set_item_data = Data.constituents[self.material_set_item]
        elif product_data["type"] == "IfcMaterialLayerSet" or product_data["type"] == "IfcMaterialLayerSetUsage":
            material_set_item_data = Data.layers[self.material_set_item]
        elif product_data["type"] == "IfcMaterialProfileSet" or product_data["type"] == "IfcMaterialProfileSetUsage":
            material_set_item_data = Data.profiles[self.material_set_item]
        else:
            material_set_item_data = {}

        self.props.material_set_item_material = str(material_set_item_data["Material"])

        self.load_set_item_attributes(material_set_item, material_set_item_data)
        if material_set_item.is_a("IfcMaterialProfile"):
            if material_set_item.Profile:
                self.mprops.profiles = str(material_set_item.Profile.id())

        return {"FINISHED"}

    def load_set_item_attributes(self, material_set_item, material_set_item_data):
        self.props.material_set_item_attributes.clear()

        for attribute in IfcStore.get_schema().declaration_by_name(material_set_item.is_a()).all_attributes():
            data_type = ifcopenshell.util.attribute.get_primitive_type(attribute)
            if data_type == "entity":
                continue
            if attribute.name() in material_set_item_data:
                new = self.props.material_set_item_attributes.add()
                new.ifc_class = material_set_item.is_a()
                new.name = attribute.name()
                new.is_null = material_set_item_data[attribute.name()] is None
                new.data_type = data_type
                if data_type == "string":
                    new.string_value = "" if new.is_null else str(material_set_item_data[attribute.name()])
                elif data_type == "float":
                    new.float_value = 0.0 if new.is_null else float(material_set_item_data[attribute.name()])
                elif data_type == "integer":
                    new.int_value = 0 if new.is_null else int(material_set_item_data[attribute.name()])
                elif data_type == "boolean":
                    new.bool_value = False if new.is_null else bool(material_set_item_data[attribute.name()])
                blenderbim.bim.helper.add_attribute_description(new, material_set_item_data)
                blenderbim.bim.helper.add_attribute_min_max(new)


class DisableEditingMaterialSetItem(bpy.types.Operator):
    bl_idname = "bim.disable_editing_material_set_item"
    bl_label = "Disable Editing Material Set Item"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()

    def execute(self, context):
        obj = bpy.data.objects.get(self.obj) if self.obj else context.active_object
        props = obj.BIMObjectMaterialProperties
        props.active_material_set_item_id = 0
        return {"FINISHED"}


class EditMaterialSetItem(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.edit_material_set_item"
    bl_label = "Edit Material Set Item"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()
    material_set_item: bpy.props.IntProperty()

    def _execute(self, context):
        obj = bpy.data.objects.get(self.obj) if self.obj else context.active_object
        self.file = IfcStore.get_file()
        props = obj.BIMObjectMaterialProperties
        mprops = context.scene.BIMMaterialProperties
        product_data = Data.products[obj.BIMObjectProperties.ifc_definition_id]

        attributes = blenderbim.bim.helper.export_attributes(props.material_set_item_attributes)

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
        elif product_data["type"] == "IfcMaterialProfileSet" or product_data["type"] == "IfcMaterialProfileSetUsage":
            profile_def = None
            if mprops.profiles:
                profile_def = tool.Ifc.get().by_id(int(mprops.profiles))

            ifcopenshell.api.run(
                "material.edit_profile",
                self.file,
                profile=self.file.by_id(self.material_set_item),
                attributes=attributes,
                profile_def=profile_def,
                material=self.file.by_id(int(obj.BIMObjectMaterialProperties.material_set_item_material)),
            )
            Data.load_profiles()
        else:
            pass

        bpy.ops.bim.disable_editing_material_set_item(obj=obj.name)


class CopyMaterial(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.copy_material"
    bl_label = "Copy Material"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        self.file = IfcStore.get_file()
        material = ifcopenshell.util.element.get_material(
            self.file.by_id(context.active_object.BIMObjectProperties.ifc_definition_id)
        )
        for obj in context.selected_objects:
            if obj == context.active_object:
                continue
            if not obj.BIMObjectProperties.ifc_definition_id:
                continue
            ifcopenshell.api.run(
                "material.copy_material",
                self.file,
                **{
                    "material": material,
                    "element": self.file.by_id(obj.BIMObjectProperties.ifc_definition_id),
                },
            )
            Data.load(self.file, obj.BIMObjectProperties.ifc_definition_id)
            self.set_default_material(obj, material)

    def set_default_material(self, obj, material):
        object_material_ids = [
            om.BIMObjectProperties.ifc_definition_id
            for om in obj.data.materials
            if om is not None and om.BIMObjectProperties.ifc_definition_id
        ]

        if material.id() in object_material_ids:
            return
        obj.data.materials.append(IfcStore.get_element(material.id()))


class ExpandMaterialCategory(bpy.types.Operator):
    bl_idname = "bim.expand_material_category"
    bl_label = "Expand Material Category"
    bl_options = {"REGISTER", "UNDO"}
    category: bpy.props.StringProperty()

    def execute(self, context):
        props = context.scene.BIMMaterialProperties
        for category in [c for c in props.materials if c.is_category and c.name == self.category]:
            category.is_expanded = True
        core.load_materials(tool.Material, props.material_type)
        return {"FINISHED"}


class ContractMaterialCategory(bpy.types.Operator):
    bl_idname = "bim.contract_material_category"
    bl_label = "Contract Material Category"
    bl_options = {"REGISTER", "UNDO"}
    category: bpy.props.StringProperty()

    def execute(self, context):
        props = context.scene.BIMMaterialProperties
        for category in [c for c in props.materials if c.is_category and c.name == self.category]:
            category.is_expanded = False
        core.load_materials(tool.Material, props.material_type)
        return {"FINISHED"}
