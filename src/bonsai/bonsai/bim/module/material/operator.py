# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of Bonsai.
#
# Bonsai is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Bonsai is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Bonsai.  If not, see <http://www.gnu.org/licenses/>.

import bpy
import json
import ifcopenshell.api
import ifcopenshell.util.element
import ifcopenshell.util.attribute
import ifcopenshell.util.representation
import ifcopenshell.util.unit
import bonsai.bim.helper
import bonsai.tool as tool
import bonsai.core.style
import bonsai.core.material as core
import bonsai.bim.module.model.profile as model_profile
from bonsai.bim.ifc import IfcStore
from typing import Any, Union


class LoadMaterials(bpy.types.Operator):
    bl_idname = "bim.load_materials"
    bl_label = "Load Materials"
    bl_description = "Display list of named materials"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        core.load_materials(tool.Material, context.scene.BIMMaterialProperties.material_type)
        return {"FINISHED"}


class DisableEditingMaterials(bpy.types.Operator):
    bl_idname = "bim.disable_editing_materials"
    bl_label = "Disable Editing Materials"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        core.disable_editing_materials(tool.Material)
        return {"FINISHED"}


class SelectByMaterial(bpy.types.Operator):
    bl_idname = "bim.select_by_material"
    bl_label = "Select By Material"
    bl_description = "Select objects using the provided material"
    bl_options = {"REGISTER", "UNDO"}
    material: bpy.props.IntProperty()

    def execute(self, context):
        material=tool.Ifc.get().by_id(self.material)
        core.select_by_material(tool.Material, tool.Spatial, material=material)
        
        # copy selection query to clipboard
        material_name = material.Name
        result = f'material="{material_name}"'  
        bpy.context.window_manager.clipboard = result
        self.report({"INFO"}, f"({result}) was copied to the clipboard.")
        
        return {"FINISHED"}


class EnableEditingMaterial(bpy.types.Operator):
    bl_idname = "bim.enable_editing_material"
    bl_label = "Enable Editing Material"
    bl_options = {"REGISTER", "UNDO"}
    material: bpy.props.IntProperty()

    def execute(self, context):
        core.enable_editing_material(tool.Material, material=tool.Ifc.get().by_id(self.material))
        return {"FINISHED"}


class EditMaterial(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.edit_material"
    bl_label = "Edit Material"
    bl_options = {"REGISTER", "UNDO"}
    material: bpy.props.IntProperty()

    def _execute(self, context):
        core.edit_material(tool.Ifc, tool.Material, material=tool.Ifc.get().by_id(self.material))


class DisableEditingMaterial(bpy.types.Operator):
    bl_idname = "bim.disable_editing_material"
    bl_label = "Disable Editing Material"
    bl_options = {"REGISTER", "UNDO"}
    material: bpy.props.IntProperty()

    def execute(self, context):
        core.disable_editing_material(tool.Material)
        return {"FINISHED"}


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
        bpy.ops.bim.enable_editing_material_set_item(obj=obj.name, material_set_item=self.material_profile)


class AddMaterial(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_material"
    bl_label = "Add Material"
    bl_description = "Create a new IfcMaterial"
    bl_options = {"REGISTER", "UNDO"}
    name: bpy.props.StringProperty(default="Default")
    category: bpy.props.StringProperty(default="")
    description: bpy.props.StringProperty(default="")

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        row = self.layout
        row.prop(self, "name", text="Name")
        row = self.layout
        row.prop(self, "description", text="Description")
        row = self.layout
        row.prop(self, "category", text="Category")

    def _execute(self, context):
        core.add_material(tool.Ifc, tool.Material, name=self.name, category=self.category, description=self.description)


class DuplicateMaterial(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.duplicate_material"
    bl_label = "Diplicate Material"
    bl_options = {"REGISTER", "UNDO"}
    material: bpy.props.IntProperty(name="Material ID")

    def _execute(self, context):
        material = tool.Ifc.get().by_id(self.material)
        tool.Material.duplicate_material(material)
        bpy.ops.bim.load_materials()


class AddMaterialSet(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_material_set"
    bl_label = "Add Material Set"
    bl_description = "Create a new material set, will use a default material/profile as a placeholder"
    bl_options = {"REGISTER", "UNDO"}
    set_type: bpy.props.StringProperty()

    def _execute(self, context):
        core.add_material_set(tool.Ifc, tool.Material, set_type=self.set_type)


class RemoveMaterial(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_material"
    bl_label = "Remove Material"
    bl_options = {"REGISTER", "UNDO"}
    material: bpy.props.IntProperty()

    def _execute(self, context):
        res = core.remove_material(tool.Ifc, tool.Material, material=tool.Ifc.get().by_id(self.material))
        if not res:
            self.report({"ERROR"}, "Material is used in material sets and cannot be removed.")
            return {"CANCELLED"}


class RemoveMaterialSet(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_material_set"
    bl_label = "Remove Material Set"
    bl_options = {"REGISTER", "UNDO"}
    material: bpy.props.IntProperty()

    def _execute(self, context):
        core.remove_material_set(tool.Ifc, tool.Material, material=tool.Ifc.get().by_id(self.material))


class AssignMaterialToSelected(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.assign_material_to_selected"
    bl_label = "Assign Material To Selected"
    bl_description = "Assign currently selected material in Materials UI to the selected objects"
    bl_options = {"REGISTER", "UNDO"}
    material: bpy.props.IntProperty(name="Material IFC ID")

    @classmethod
    def poll(cls, context):
        if not context.selected_objects:
            cls.poll_message_set("No objects selected")
            return False
        return True

    def _execute(self, context):
        material = tool.Ifc.get().by_id(self.material)
        objects = tool.Blender.get_selected_objects()
        core.assign_material(
            tool.Ifc,
            tool.Material,
            material_type=tool.Material.get_active_material_type(),
            objects=objects,
            material=material,
        )


class AssignMaterial(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.assign_material"
    bl_label = "Assign Material"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()
    material_type: bpy.props.StringProperty()

    @classmethod
    def description(cls, context, properties):
        if not (material_type := properties.material_type):
            if not (obj := context.active_object):
                return ""
            material_type = obj.BIMObjectMaterialProperties.material_type

        description = "Assign current IfcMaterial to the selected objects"
        if material_type != "IfcMaterial":
            description += f" as part of a new {material_type}"
        return description

    def _execute(self, context):
        objects = [bpy.data.objects.get(self.obj)] if self.obj else tool.Blender.get_selected_objects()
        core.assign_material(tool.Ifc, tool.Material, material_type=self.material_type, objects=objects)


class UnassignMaterial(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.unassign_material"
    bl_label = "Unassign Material"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()

    def _execute(self, context):
        objects = [bpy.data.objects.get(self.obj)] if self.obj else tool.Blender.get_selected_objects()
        core.unassign_material(tool.Ifc, tool.Material, objects=objects)


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


class RemoveConstituent(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_constituent"
    bl_label = "Remove Constituent"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()
    constituent: bpy.props.IntProperty()

    def _execute(self, context):
        constituent = tool.Ifc.get().by_id(self.constituent)
        for material_set in constituent.ToMaterialConstituentSet:
            if len(material_set.MaterialConstituents) == 1:
                self.report({"ERROR"}, "At least one constituent must exist")
                return {"CANCELLED"}
        ifcopenshell.api.run("material.remove_constituent", tool.Ifc.get(), constituent=constituent)


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


class RemoveProfile(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_profile"
    bl_label = "Remove Profile"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()
    profile: bpy.props.IntProperty()

    def _execute(self, context):
        profile = tool.Ifc.get().by_id(self.profile)
        for material_set in profile.ToMaterialProfileSet:
            if len(material_set.MaterialProfiles) == 1:
                self.report({"ERROR"}, "At least one profile must exist")
                return {"CANCELLED"}
        ifcopenshell.api.run("material.remove_profile", tool.Ifc.get(), profile=profile)


class AddLayer(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_layer"
    bl_label = "Add Layer"
    bl_description = "The List is Ordered From Origin Point"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()
    layer_set: bpy.props.IntProperty()

    def _execute(self, context):
        obj = bpy.data.objects.get(self.obj) if self.obj else context.active_object
        self.file = IfcStore.get_file()
        layer = ifcopenshell.api.run(
            "material.add_layer",
            self.file,
            **{
                "layer_set": self.file.by_id(self.layer_set),
                "material": self.file.by_id(int(obj.BIMObjectMaterialProperties.material)),
            },
        )

        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        thickness = 0.1  # Arbitrary metric thickness for now
        layer.LayerThickness = thickness / unit_scale


class ReorderMaterialSetItem(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.reorder_material_set_item"
    bl_label = "Reorder Material Set Item"
    bl_description = "The List is Ordered From Origin Point"
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


class RemoveLayer(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_layer"
    bl_label = "Remove Layer"
    bl_options = {"REGISTER", "UNDO"}
    layer: bpy.props.IntProperty()

    def _execute(self, context):
        layer = tool.Ifc.get().by_id(self.layer)
        for material_set in layer.ToMaterialLayerSet:
            if len(material_set.MaterialLayers) == 1:
                self.report({"ERROR"}, "At least one layer must exist")
                return {"CANCELLED"}
        ifcopenshell.api.run("material.remove_layer", tool.Ifc.get(), layer=layer)


class DuplicateLayer(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.duplicate_layer"
    bl_label = "Duplicate Layer"
    bl_options = {"REGISTER", "UNDO"}
    layer: bpy.props.IntProperty()

    def _execute(self, context):
        layer = tool.Ifc.get().by_id(self.layer)
        new_layer = ifcopenshell.util.element.copy(tool.Ifc.get(), layer)
        for material_set in layer.ToMaterialLayerSet:
            layers = list(material_set.MaterialLayers)
            layers.insert(layers.index(layer), new_layer)
            material_set.MaterialLayers = layers


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
            material_list=self.file.by_id(self.list_item_set),
            material=self.file.by_id(int(obj.BIMObjectMaterialProperties.material)),
        )


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


class EnableEditingAssignedMaterial(bpy.types.Operator):
    bl_idname = "bim.enable_editing_assigned_material"
    bl_label = "Enable Editing Assigned Material"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()

    def execute(self, context):
        obj = bpy.data.objects.get(self.obj) if self.obj else context.active_object
        props = obj.BIMObjectMaterialProperties
        props.is_editing = True
        element = tool.Ifc.get_entity(obj)
        material = ifcopenshell.util.element.get_material(element)

        if material.is_a("IfcMaterial"):
            props.material = str(material.id())
            return {"FINISHED"}

        props.material_set_usage_attributes.clear()
        props.material_set_attributes.clear()

        if "Usage" in material.is_a():
            bonsai.bim.helper.import_attributes2(
                material, props.material_set_usage_attributes, callback=self.import_attributes
            )
            bonsai.bim.helper.import_attributes2(material[0], props.material_set_attributes)
        else:
            bonsai.bim.helper.import_attributes2(material, props.material_set_attributes)
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
        active_obj = bpy.data.objects.get(self.obj) if self.obj else context.active_object
        props = active_obj.BIMObjectMaterialProperties
        element = tool.Ifc.get_entity(active_obj)
        material = ifcopenshell.util.element.get_material(element)

        objects = tool.Blender.get_selected_objects()

        if props.active_material_set_item_id != 0:  # We were editing a material layer set item
            bpy.ops.bim.edit_material_set_item(material_set_item=props.active_material_set_item_id)

        if material.is_a("IfcMaterial"):
            for obj in objects:
                bpy.ops.bim.unassign_material(obj=obj.name)
                bpy.ops.bim.assign_material(obj=obj.name, material_type="IfcMaterial")
            bpy.ops.bim.disable_editing_assigned_material(obj=active_obj.name)
            return {"FINISHED"}

        material_set = self.file.by_id(self.material_set)
        attributes = bonsai.bim.helper.export_attributes(props.material_set_attributes)
        ifcopenshell.api.run(
            "material.edit_assigned_material",
            self.file,
            **{"element": material_set, "attributes": attributes},
        )

        if self.material_set_usage:
            material_set_usage = self.file.by_id(self.material_set_usage)
            attributes = bonsai.bim.helper.export_attributes(props.material_set_usage_attributes)
            if material_set_usage.is_a("IfcMaterialLayerSetUsage"):
                ifcopenshell.api.run(
                    "material.edit_layer_usage",
                    self.file,
                    **{"usage": material_set_usage, "attributes": attributes},
                )
            elif material_set_usage.is_a("IfcMaterialProfileSetUsage"):
                if attributes.get("CardinalPoint", None):
                    attributes["CardinalPoint"] = int(attributes["CardinalPoint"])
                ifcopenshell.api.run(
                    "material.edit_profile_usage",
                    self.file,
                    **{"usage": material_set_usage, "attributes": attributes},
                )

        bpy.ops.bim.disable_editing_assigned_material(obj=active_obj.name)


class EnableEditingMaterialSetItemProfile(bpy.types.Operator):
    bl_idname = "bim.enable_editing_material_set_item_profile"
    bl_label = "Enable Editing Material Set Item Profile"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()
    material_set_item: bpy.props.IntProperty()

    def execute(self, context):
        obj = bpy.data.objects.get(self.obj) if self.obj else context.active_object
        self.props = obj.BIMObjectMaterialProperties
        self.props.active_material_set_item_id = self.material_set_item
        self.props.material_set_item_profile_attributes.clear()
        profile = tool.Ifc.get().by_id(self.material_set_item).Profile
        bonsai.bim.helper.import_attributes2(profile, self.props.material_set_item_profile_attributes)
        return {"FINISHED"}


class DisableEditingMaterialSetItemProfile(bpy.types.Operator):
    bl_idname = "bim.disable_editing_material_set_item_profile"
    bl_label = "Disable Editing Material Set Item Profile"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()

    def execute(self, context):
        obj = bpy.data.objects.get(self.obj) if self.obj else context.active_object
        self.props = obj.BIMObjectMaterialProperties
        self.props.active_material_set_item_id = 0
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
        attributes = bonsai.bim.helper.export_attributes(self.props.material_set_item_profile_attributes)
        profile = tool.Ifc.get().by_id(self.material_set_item).Profile
        ifcopenshell.api.run("profile.edit_profile", tool.Ifc.get(), profile=profile, attributes=attributes)
        self.props.active_material_set_item_id = 0
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

        element = tool.Ifc.get_entity(obj)
        material = ifcopenshell.util.element.get_material(element, should_skip_usage=True)
        material_set_item = self.file.by_id(self.material_set_item)

        self.props.material_set_item_material = str(material_set_item.Material.id())

        self.props.material_set_item_attributes.clear()
        bonsai.bim.helper.import_attributes2(material_set_item, self.props.material_set_item_attributes)

        if material_set_item.is_a("IfcMaterialProfile"):
            if material_set_item.Profile and material_set_item.Profile.ProfileName:
                self.mprops.profiles = str(material_set_item.Profile.id())

        return {"FINISHED"}


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
        element = tool.Ifc.get_entity(obj)
        material = ifcopenshell.util.element.get_material(element, should_skip_usage=True)

        attributes = bonsai.bim.helper.export_attributes(props.material_set_item_attributes)

        if material.is_a("IfcMaterialConstituentSet"):
            ifcopenshell.api.run(
                "material.edit_constituent",
                self.file,
                **{
                    "constituent": self.file.by_id(self.material_set_item),
                    "attributes": attributes,
                    "material": self.file.by_id(int(obj.BIMObjectMaterialProperties.material_set_item_material)),
                },
            )
        elif material.is_a("IfcMaterialLayerSet"):
            ifcopenshell.api.run(
                "material.edit_layer",
                self.file,
                **{
                    "layer": self.file.by_id(self.material_set_item),
                    "attributes": attributes,
                    "material": self.file.by_id(int(obj.BIMObjectMaterialProperties.material_set_item_material)),
                },
            )
        elif material.is_a("IfcMaterialProfileSet"):
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
        else:
            pass

        bpy.ops.bim.disable_editing_material_set_item(obj=obj.name)


class ExpandMaterialCategory(bpy.types.Operator):
    bl_idname = "bim.expand_material_category"
    bl_label = "Expand Material Category"
    bl_description = "SHIFT+CLICK to expand all material categories"
    bl_options = {"REGISTER", "UNDO"}
    category: bpy.props.StringProperty()
    expand_all: bpy.props.BoolProperty(name="Expand All", default=False, options={"SKIP_SAVE"})

    def invoke(self, context, event):
        # Expanding all categories on shift+click.
        # Make sure to use SKIP_SAVE on property, otherwise it might get stuck.
        if event.type == "LEFTMOUSE" and event.shift:
            self.expand_all = True
        return self.execute(context)

    def execute(self, context):
        props = context.scene.BIMMaterialProperties
        for index, category in (
            (i, c)
            for i, c in enumerate(props.materials)
            if c.is_category and (self.expand_all or c.name == self.category)
        ):
            category.is_expanded = True
            if category.name == self.category:
                props.active_material_index = index
        core.load_materials(tool.Material, props.material_type)
        return {"FINISHED"}


class ContractMaterialCategory(bpy.types.Operator):
    bl_idname = "bim.contract_material_category"
    bl_label = "Contract Material Category"
    bl_description = "SHIFT+CLICK to contract all material categories"
    bl_options = {"REGISTER", "UNDO"}
    category: bpy.props.StringProperty()
    contract_all: bpy.props.BoolProperty(name="Contract All", default=False, options={"SKIP_SAVE"})

    def invoke(self, context, event):
        # Contracting all categories on shift+click.
        # Make sure to use SKIP_SAVE on property, otherwise it might get stuck.
        if event.type == "LEFTMOUSE" and event.shift:
            self.contract_all = True
        return self.execute(context)

    def execute(self, context):
        props = context.scene.BIMMaterialProperties
        for index, category in (
            (i, c)
            for i, c in enumerate(props.materials)
            if c.is_category and (self.contract_all or c.name == self.category)
        ):
            category.is_expanded = False
            if category.name == self.category:
                props.active_material_index = index
        core.load_materials(tool.Material, props.material_type)
        return {"FINISHED"}


class EnableEditingMaterialStyle(bpy.types.Operator):
    bl_idname = "bim.enable_editing_material_style"
    bl_label = "Enable Editing Material Style"
    bl_options = {"REGISTER", "UNDO"}
    material: bpy.props.IntProperty()

    def execute(self, context):
        props = bpy.context.scene.BIMMaterialProperties
        props.active_material_id = self.material
        props.editing_material_type = "STYLE"

        # set already applied style and context if possible
        if not 0 <= props.active_material_index < len(props.materials):
            return {"FINISHED"}

        ifc_file = tool.Ifc.get()
        material = ifc_file.by_id(props.materials[props.active_material_index].ifc_definition_id)
        if not material.HasRepresentation:
            # MODEL_VIEW is probably the one that's used with the styles most frequently.
            context = ifcopenshell.util.representation.get_context(ifc_file, "Model", "Body", "MODEL_VIEW")
            if context:
                props.contexts = str(context.id())
            return {"FINISHED"}

        rep = material.HasRepresentation[0].Representations[0]  # IfcStyledRepresentation
        props.contexts = str(rep.ContextOfItems.id())
        style = rep.Items[0].Styles[0]
        if style.Name:  # props.styles only has named styles
            props.styles = str(rep.Items[0].Styles[0].id())
        return {"FINISHED"}


class EditMaterialStyle(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.edit_material_style"
    bl_label = "Edit Material Style"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        props = bpy.context.scene.BIMMaterialProperties
        ifc_file = tool.Ifc.get()
        material = ifc_file.by_id(props.active_material_id)
        style = ifc_file.by_id(int(props.styles))
        context = ifc_file.by_id(int(props.contexts))
        ifcopenshell.api.run("style.assign_material_style", ifc_file, material=material, style=style, context=context)
        tool.Material.disable_editing_material()
        core.load_materials(tool.Material, props.material_type)
        # NOTE: Update all elements that has this material and
        # not just the ones that are using it in IfcMaterialConstituent,
        # to handle cases where Style is connected to geometry implicitly:
        # e.g. RepItem->IfcElement->IfcMaterial->Style
        # instead of RepItem->ShapeAspect->Constituent->Style.
        tool.Material.update_elements_using_material(material)


class UnassignMaterialStyle(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.unassign_material_style"
    bl_label = "Unassign Material Style"
    bl_options = {"REGISTER", "UNDO"}
    style: bpy.props.IntProperty()
    context: bpy.props.IntProperty()

    def _execute(self, context):
        props = bpy.context.scene.BIMMaterialProperties
        material = tool.Ifc.get().by_id(props.materials[props.active_material_index].ifc_definition_id)
        style = tool.Ifc.get().by_id(self.style)
        context = tool.Ifc.get().by_id(self.context)
        ifcopenshell.api.run(
            "style.unassign_material_style", tool.Ifc.get(), material=material, style=style, context=context
        )
        core.load_materials(tool.Material, props.material_type)
        tool.Material.update_elements_using_material(material)


class SelectMaterialInMaterialsUI(bpy.types.Operator):
    bl_idname = "bim.material_ui_select"
    bl_label = "Select Material In Materials UI"
    bl_options = {"REGISTER", "UNDO"}
    material_id: bpy.props.IntProperty()

    def execute(self, context):
        props = bpy.context.scene.BIMMaterialProperties
        ifc_file = tool.Ifc.get()
        material = ifc_file.by_id(self.material_id)
        core.load_materials(tool.Material, material.is_a())

        def get_material_item() -> Union[tuple[int, bpy.types.PropertyGroup], None]:
            return next(
                ((i, m) for i, m in enumerate(props.materials) if m.ifc_definition_id == self.material_id), None
            )

        material_item = get_material_item()

        # Material category is contracted, won't occur for non-IfcMaterials.
        if material_item is None:
            material_category = tool.Material.get_material_category(material)
            bpy.ops.bim.expand_material_category(category=material_category)
            material_item = get_material_item()
            assert material_item

        item_index, _ = material_item
        props.active_material_index = item_index

        self.report(
            {"INFO"},
            f"Material '{tool.Material.get_material_name(material) or 'Unnamed'}' is selected in Materials UI.",
        )
        return {"FINISHED"}
