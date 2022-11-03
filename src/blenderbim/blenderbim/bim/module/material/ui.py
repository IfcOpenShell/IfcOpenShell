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

import blenderbim.bim.helper
from bpy.types import Panel, UIList
from ifcopenshell.api.material.data import Data
from blenderbim.bim.ifc import IfcStore
from blenderbim.bim.helper import draw_attributes
from blenderbim.bim.helper import prop_with_search
from blenderbim.bim.module.material.data import MaterialsData, ObjectMaterialData


class BIM_PT_materials(Panel):
    bl_label = "IFC Materials"
    bl_idname = "BIM_PT_materials"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_geometry"

    @classmethod
    def poll(cls, context):
        return IfcStore.get_file()

    def draw(self, context):
        if not MaterialsData.is_loaded:
            MaterialsData.load()

        self.props = context.scene.BIMMaterialProperties

        row = self.layout.row(align=True)
        row.label(text="{} Materials Found".format(MaterialsData.data["total_materials"]), icon="MATERIAL")
        if self.props.is_editing:
            row.operator("bim.disable_editing_materials", text="", icon="CANCEL")
        else:
            row = self.layout.row(align=True)
            prop_with_search(row, self.props, "material_type", text="")
            row.operator("bim.load_materials", text="", icon="IMPORT")
            return

        row = self.layout.row(align=True)
        row.alignment = "RIGHT"

        if self.props.material_type == "IfcMaterial":
            row.operator("bim.add_material", text="", icon="ADD")
            if self.props.materials and self.props.active_material_index < len(self.props.materials):
                material = self.props.materials[self.props.active_material_index]
                if material.ifc_definition_id:
                    op = row.operator("bim.select_by_material", text="", icon="RESTRICT_SELECT_OFF")
                    op.material = material.ifc_definition_id
                    row.operator("bim.remove_material", text="", icon="X").material = material.ifc_definition_id
        else:
            row.operator("bim.add_material_set", text="", icon="ADD").set_type = self.props.material_type
            if self.props.materials and self.props.active_material_index < len(self.props.materials):
                material = self.props.materials[self.props.active_material_index]
                if material.ifc_definition_id:
                    op = row.operator("bim.select_by_material", text="", icon="RESTRICT_SELECT_OFF")
                    op.material = material.ifc_definition_id
                    row.operator("bim.remove_material_set", text="", icon="X").material = material.ifc_definition_id

        self.layout.template_list("BIM_UL_materials", "", self.props, "materials", self.props, "active_material_index")


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
        row = self.layout.row(align=True)
        material_id = context.active_object.active_material.BIMObjectProperties.ifc_definition_id
        if bool(material_id):
            row.operator("bim.remove_material", icon="X", text="Remove IFC Material").material = material_id
            row.operator("bim.unlink_material", icon="UNLINKED", text="")
        else:
            op = row.operator("bim.add_material", icon="ADD", text="Create IFC Material")
            op.obj = context.active_object.active_material.name


class BIM_PT_object_material(Panel):
    bl_label = "IFC Object Material"
    bl_idname = "BIM_PT_object_material"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    bl_parent_id = "BIM_PT_object_metadata"

    @classmethod
    def poll(cls, context):
        if not context.active_object:
            return False
        props = context.active_object.BIMObjectProperties
        if not props.ifc_definition_id:
            return False
        if not IfcStore.get_element(props.ifc_definition_id):
            return False
        if not hasattr(IfcStore.get_file().by_id(props.ifc_definition_id), "HasAssociations"):
            return False
        return True

    def draw(self, context):
        if not ObjectMaterialData.is_loaded:
            ObjectMaterialData.load()

        self.file = IfcStore.get_file()
        self.oprops = context.active_object.BIMObjectProperties
        self.props = context.active_object.BIMObjectMaterialProperties
        self.mprops = context.scene.BIMMaterialProperties
        if not Data.is_loaded:
            Data.load(IfcStore.get_file())
        if self.oprops.ifc_definition_id not in Data.products:
            Data.load(IfcStore.get_file(), self.oprops.ifc_definition_id)

        if not ObjectMaterialData.data["materials"]:
            row = self.layout.row(align=True)
            row.label(text="No Materials Available")
            row.operator("bim.add_material", icon="ADD", text="").obj = ""
            return

        if ObjectMaterialData.data["type_material"]:
            row = self.layout.row(align=True)
            row.label(text="Inherited Material: " + ObjectMaterialData.data["type_material"], icon="FILE_PARENT")

        if ObjectMaterialData.data["material_class"]:
            return self.draw_material_ui()

        row = self.layout.row(align=True)
        prop_with_search(row, self.props, "material_type", text="")
        if self.props.material_type == "IfcMaterial" or self.props.material_type == "IfcMaterialList":
            prop_with_search(row, self.props, "material", text="")
        row.operator("bim.assign_material", icon="ADD", text="")

    def draw_material_ui(self):
        row = self.layout.row(align=True)
        row.label(text=ObjectMaterialData.data["material_class"])

        if self.props.is_editing:
            op = row.operator("bim.edit_assigned_material", icon="CHECKMARK", text="")
            op.material_set = ObjectMaterialData.data["set"]["id"]
            if "Usage" in ObjectMaterialData.data["material_class"]:
                op.material_set_usage = ObjectMaterialData.data["material_id"]
            row.operator("bim.disable_editing_assigned_material", icon="CANCEL", text="")
        else:
            if ObjectMaterialData.data["material_class"] == "IfcMaterial":
                row.operator("bim.copy_material", icon="COPYDOWN", text="")
            row.operator("bim.enable_editing_assigned_material", icon="GREASEPENCIL", text="")
            row.operator("bim.unassign_material", icon="X", text="")

        if ObjectMaterialData.data["material_class"] == "IfcMaterial":
            self.draw_single_ui()
        else:
            self.draw_set_ui()

    def draw_single_ui(self):
        if self.props.is_editing:
            return self.draw_editable_single_ui()
        return self.draw_read_only_single_ui()

    def draw_editable_single_ui(self):
        prop_with_search(self.layout, self.props, "material", text="")

    def draw_read_only_single_ui(self):
        row = self.layout.row(align=True)
        row.label(text="Name")
        row.label(text=ObjectMaterialData.data["material_name"])

    def draw_set_ui(self):
        if self.props.is_editing:
            return self.draw_editable_set_ui()
        self.draw_read_only_set_ui()

    def draw_editable_set_ui(self):
        blenderbim.bim.helper.draw_attributes(self.props.material_set_attributes, self.layout)
        blenderbim.bim.helper.draw_attributes(self.props.material_set_usage_attributes, self.layout)

        if ObjectMaterialData.data["set_item_name"] == "profile" and not self.mprops.profiles:
            row = self.layout.row(align=True)
            row.label(text="No Profiles Available")
            row.operator("bim.add_profile_def", icon="ADD", text="")
        else:
            row = self.layout.row(align=True)
            if ObjectMaterialData.data["set_item_name"] == "profile":
                row.prop(self.mprops, "profiles", icon="ITALIC", text="")
            prop_with_search(row, self.props, "material", icon="MATERIAL", text="")
            op = row.operator(f"bim.add_{ObjectMaterialData.data['set_item_name']}", icon="ADD", text="")
            setattr(op, f"{ObjectMaterialData.data['set_item_name']}_set", ObjectMaterialData.data["set"]["id"])

        total_items = len(ObjectMaterialData.data["set_items"])
        for index, set_item in enumerate(ObjectMaterialData.data["set_items"]):
            if len(self.props.material_set_item_profile_attributes):
                self.draw_editable_set_item_profile_ui(set_item)
            elif self.props.active_material_set_item_id == set_item["id"]:
                self.draw_editable_set_item_ui(set_item)
            else:
                self.draw_read_only_set_item_ui(
                    set_item, index, is_first=index == 0, is_last=index == total_items - 1
                )

    def draw_editable_set_item_profile_ui(self, set_item):
        box = self.layout.box()
        row = box.row(align=True)
        op = row.operator("bim.edit_material_set_item_profile", icon="CHECKMARK", text="Save Changes")
        op.material_set_item = set_item["id"]
        row.operator("bim.disable_editing_material_set_item_profile", icon="CANCEL", text="")
        draw_attributes(self.props.material_set_item_profile_attributes, box)

    def draw_editable_set_item_ui(self, set_item):
        box = self.layout.box()
        row = box.row(align=True)
        op = row.operator("bim.edit_material_set_item", icon="CHECKMARK", text="Save Changes")
        op.material_set_item = set_item["id"]
        row.operator("bim.disable_editing_material_set_item", icon="CANCEL", text="")

        draw_attributes(self.props.material_set_item_attributes, box)

        row = box.row()
        row.prop(self.props, "material_set_item_material", icon="MATERIAL", text="Material")

        if ObjectMaterialData.data["set_item_name"] == "profile":
            row = box.row()
            row.prop(self.mprops, "profiles", icon="ITALIC", text="Profile")

    def draw_read_only_set_item_ui(self, set_item, index, is_first=False, is_last=False):
        if ObjectMaterialData.data["material_class"] == "IfcMaterialList":
            row = self.layout.row(align=True)
            row.label(text="IfcMaterial", icon="LAYER_ACTIVE")
            row.label(text=set_item["name"], icon="MATERIAL")
        else:
            row = self.layout.row(align=True)
            row.label(text=set_item["name"], icon=set_item["icon"])
            row.label(text=set_item["material"], icon="MATERIAL")

        if not is_first:
            op = row.operator(f"bim.reorder_material_set_item", icon="TRIA_UP", text="")
            op.old_index = index
            op.new_index = index - 1
            setattr(op, "material_set", ObjectMaterialData.data["set"]["id"])
        if not is_last:
            op = row.operator(f"bim.reorder_material_set_item", icon="TRIA_DOWN", text="")
            op.old_index = index
            op.new_index = index + 1
            setattr(op, "material_set", ObjectMaterialData.data["set"]["id"])
        if not self.props.active_material_set_item_id and ObjectMaterialData.data["material_class"] != "IfcMaterialList":
            if "Profile" in ObjectMaterialData.data["material_class"]:
                op = row.operator("bim.enable_editing_material_set_item_profile", icon="ITALIC", text="")
                op.material_set_item = set_item["id"]
            op = row.operator("bim.enable_editing_material_set_item", icon="GREASEPENCIL", text="")
            op.material_set_item = set_item["id"]
        op = row.operator(f"bim.remove_{ObjectMaterialData.data['set_item_name']}", icon="X", text="")
        if ObjectMaterialData.data["material_class"] == "IfcMaterialList":
            setattr(op, "list_item_set", ObjectMaterialData.data["set"]["id"])
        setattr(op, ObjectMaterialData.data["set_item_name"], set_item["id"])
        if hasattr(op, f"{ObjectMaterialData.data['set_item_name']}_index"):
            setattr(op, f"{ObjectMaterialData.data['set_item_name']}_index", index)

    def draw_read_only_set_ui(self):
        row = self.layout.row(align=True)
        row.label(text="Name")
        row.label(text=ObjectMaterialData.data["set"]["name"])
        if ObjectMaterialData.data["set"]["description"]:
            row = self.layout.row(align=True)
            row.label(text="Description")
            row.label(text=ObjectMaterialData.data["set"]["description"])

        if ObjectMaterialData.data["material_class"] == "IfcMaterialProfileSetUsage":
            if ObjectMaterialData.data["set_usage"].get("cardinal_point"):
                row = self.layout.row(align=True)
                row.label(text="CardinalPoint")
                row.label(text=ObjectMaterialData.data["set_usage"]["cardinal_point"])

        for set_item in ObjectMaterialData.data["set_items"]:
            if ObjectMaterialData.data["material_class"] == "IfcMaterialList":
                row = self.layout.row(align=True)
                row.label(text="IfcMaterial", icon="LAYER_ACTIVE")
                row.label(text=set_item["name"], icon="MATERIAL")
            else:
                row = self.layout.row(align=True)
                row.label(text=set_item["name"], icon=set_item["icon"])
                row.label(text=set_item["material"], icon="MATERIAL")

        if ObjectMaterialData.data["total_thickness"]:
            row = self.layout.row(align=True)
            row.label(text=f"Total Thickness: {ObjectMaterialData.data['total_thickness']:.3f}")


class BIM_UL_materials(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if item:
            row = layout.row(align=True)

            if item.is_category:
                if item.is_expanded:
                    row.operator(
                        "bim.contract_material_category", text="", emboss=False, icon="DISCLOSURE_TRI_DOWN"
                    ).category = item.name
                else:
                    row.operator(
                        "bim.expand_material_category", text="", emboss=False, icon="DISCLOSURE_TRI_RIGHT"
                    ).category = item.name
                row.label(text=item.name or "Uncategorised")
            else:
                row.label(text="", icon="BLANK1")
                row.label(text=item.name, icon="MATERIAL")

                row2 = row.row()
                row2.alignment = "RIGHT"
                row2.label(text=str(item.total_elements))
