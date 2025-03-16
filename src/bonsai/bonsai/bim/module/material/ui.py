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

from __future__ import annotations
import bonsai.bim.helper
import bonsai.tool as tool
import bpy
from bpy.types import Panel, UIList
from bonsai.bim.helper import draw_attributes
from bonsai.bim.helper import prop_with_search
from bonsai.bim.module.material.data import MaterialsData, ObjectMaterialData
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bonsai.bim.module.material.prop import Material, BIMMaterialProperties


class BIM_PT_materials(Panel):
    bl_label = "Materials"
    bl_idname = "BIM_PT_materials"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_tab_materials"
    bl_options = {"HIDE_HEADER"}

    @classmethod
    def poll(cls, context):
        return tool.Ifc.get()

    def draw(self, context):
        if not MaterialsData.is_loaded:
            MaterialsData.load()

        self.props = tool.Material.get_material_props()
        material = tool.Material.get_active_material_item()
        material_id = material.ifc_definition_id if material else None

        row = self.layout.row(align=True)
        if self.props.is_editing:
            row.label(text=f"{MaterialsData.data['total_materials']} {self.props.material_type}s", icon="NODE_MATERIAL")
            row.operator("bim.disable_editing_materials", text="", icon="CANCEL")
        else:
            row.label(text=f"{MaterialsData.data['total_materials']} Materials", icon="NODE_MATERIAL")
            prop_with_search(row, self.props, "material_type", text="")
            row.operator("bim.load_materials", text="", icon="IMPORT")
            return

        row = self.layout.row(align=True)
        row.alignment = "RIGHT"

        if self.props.material_type == "IfcMaterial":
            row.operator("bim.add_material", text="", icon="ADD")
            if material_id:
                op = row.operator("bim.duplicate_material", text="", icon="DUPLICATE")
                op.material = material_id
                op = row.operator("bim.select_by_material", text="", icon="RESTRICT_SELECT_OFF")
                op.material = material_id
                op = row.operator("bim.assign_material_to_selected", text="", icon="BRUSH_DATA")
                op.material = material_id
                op = row.operator("bim.enable_editing_material", text="", icon="GREASEPENCIL")
                op.material = material_id
                op = row.operator("bim.enable_editing_material_style", text="", icon="SHADING_RENDERED")
                op.material = material_id
                row.operator("bim.remove_material", text="", icon="X").material = material_id

            self.draw_editing_ui()
        else:
            row.operator("bim.add_material_set", text="", icon="ADD").set_type = self.props.material_type
            if material_id:
                op = row.operator("bim.select_by_material", text="", icon="RESTRICT_SELECT_OFF")
                op.material = material_id
                op = row.operator("bim.assign_material_to_selected", text="", icon="BRUSH_DATA")
                op.material = material_id
                row.operator("bim.remove_material_set", text="", icon="X").material = material_id

        self.layout.template_list("BIM_UL_materials", "", self.props, "materials", self.props, "active_material_index")

        if material_id:
            for style in MaterialsData.data["material_styles_data"][material_id]:
                row = self.layout.row(align=True)
                row.label(text="", icon="SHADING_RENDERED")
                row.label(text=style["context_type"])
                row.label(text=style["context_identifier"])
                row.label(text=style["target_view"])
                row.label(text=style["name"])
                op = row.operator("bim.styles_ui_select", icon="ZOOM_SELECTED", text="")
                op.style_id = style["id"]
                op = row.operator("bim.unassign_material_style", text="", icon="X")
                op.style = style["id"]
                op.context = style["context_id"]

    def draw_editing_ui(self):
        if not self.props.active_material_id:
            return
        ifc_definition_id = self.props.active_material_id
        if self.props.editing_material_type == "ATTRIBUTES":
            bonsai.bim.helper.draw_attributes(self.props.material_attributes, self.layout)
            row = self.layout.row(align=True)
            row.operator("bim.edit_material", text="Save Material", icon="CHECKMARK").material = ifc_definition_id
            row.operator("bim.disable_editing_material", text="", icon="CANCEL")
        elif self.props.editing_material_type == "STYLE":
            row = self.layout.row(align=True)
            row.prop(self.props, "contexts", text="")
            prop_with_search(row, self.props, "styles", text="")
            row = self.layout.row(align=True)
            row.operator("bim.edit_material_style", text="Assign Style", icon="CHECKMARK")
            row.operator("bim.disable_editing_material", text="", icon="CANCEL")


class BIM_PT_object_material(Panel):
    bl_label = "Object Material"
    bl_idname = "BIM_PT_object_material"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_tab_object_materials"
    bl_options = {"HIDE_HEADER"}

    @classmethod
    def poll(cls, context):
        if not tool.Blender.is_tab(context, "GEOMETRY"):
            return False
        if not (obj := context.active_object):
            return False
        ifc_id = tool.Blender.get_ifc_definition_id(obj)
        if not ifc_id:
            return False
        if not tool.Ifc.get_object_by_identifier(ifc_id):
            return False
        if not hasattr(tool.Ifc.get().by_id(ifc_id), "HasAssociations"):
            return False
        return True

    def draw(self, context):
        if not ObjectMaterialData.is_loaded:
            ObjectMaterialData.load()

        obj = context.active_object
        assert obj
        self.file = tool.Ifc.get()
        self.oprops = tool.Blender.get_object_bim_props(obj)
        self.props = tool.Material.get_object_material_props(obj)
        self.mprops = tool.Material.get_material_props()

        if not ObjectMaterialData.data["materials"]:
            row = self.layout.row(align=True)
            row.label(text="No Materials Available")
            row.operator("bim.add_material", icon="ADD", text="")
            return

        if ObjectMaterialData.data["type_material"]:
            row = self.layout.row(align=True)
            if ObjectMaterialData.data["is_type_material_overridden"]:
                row.label(
                    text=f"Inherited Material Is Occurrence Overridden",
                    icon="CON_CHILDOF",
                )
            else:
                row.label(text="Inherited Material: " + ObjectMaterialData.data["type_material"], icon="CON_CHILDOF")

        if ObjectMaterialData.data["material_class"]:
            return self.draw_material_ui()

        row = self.layout.row(align=True)
        prop_with_search(row, self.props, "material_type", text="")
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
            op = row.operator("bim.material_ui_select", icon="ZOOM_SELECTED", text="")
            op.material_id = ObjectMaterialData.data["material_id"]
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
        material_id = ObjectMaterialData.data["material_id"]
        layout = self.layout
        box = layout.box()
        row = box.row()
        row.label(text="Name")
        op = row.operator(
            "bim.select_by_material", text=ObjectMaterialData.data["material_name"], icon="NONE", emboss=False
        )
        op.material = material_id

    def draw_set_ui(self):
        if self.props.is_editing:
            return self.draw_editable_set_ui()
        self.draw_read_only_set_ui()

    def draw_editable_set_ui(self):
        bonsai.bim.helper.draw_attributes(self.props.material_set_attributes, self.layout)
        bonsai.bim.helper.draw_attributes(self.props.material_set_usage_attributes, self.layout)

        if ObjectMaterialData.data["set_item_name"] == "profile" and not self.mprops.profiles:
            row = self.layout.row(align=True)
            row.label(text="No Profiles Available")
            row.operator("bim.add_profile_def", icon="ADD", text="")
        else:
            layout = self.layout
            layout.separator()
            layout.separator()
            row = self.layout.row(align=True)
            if ObjectMaterialData.data["set_item_name"] == "profile":
                prop_with_search(row, self.mprops, "profiles", icon="ITALIC", text="")
            prop_with_search(row, self.props, "material", icon="MATERIAL", text="")
            op = row.operator(f"bim.add_{ObjectMaterialData.data['set_item_name']}", icon="ADD", text="")
            setattr(op, f"{ObjectMaterialData.data['set_item_name']}_set", ObjectMaterialData.data["set"]["id"])

        total_items = len(ObjectMaterialData.data["set_items"])

        layout = self.layout
        box = layout.box()
        active_object = bpy.context.active_object
        self.layerset_bounds(box, active_object, location="Top_Exterior")

        for set_item in ObjectMaterialData.data["set_items"]:
            if (
                len(self.props.material_set_item_profile_attributes)
                and self.props.active_material_set_item_id == set_item["id"]
            ):
                self.draw_editable_set_item_profile_ui(box, set_item)
            elif self.props.active_material_set_item_id == set_item["id"]:
                self.draw_editable_set_item_ui(box, set_item)
            else:
                self.draw_read_only_set_item_ui(box, set_item)

        self.layerset_bounds(box, active_object, location="Bottom_Interior")

    def draw_editable_set_item_profile_ui(self, box, set_item):
        # box = self.layout.box()
        row = box.row(align=True)
        op = row.operator("bim.edit_material_set_item_profile", icon="CHECKMARK", text="Save Changes")
        op.material_set_item = set_item["id"]
        row.operator("bim.disable_editing_material_set_item_profile", icon="CANCEL", text="")
        draw_attributes(self.props.material_set_item_profile_attributes, box)

    def draw_editable_set_item_ui(self, box, set_item):
        row = box.row(align=True)
        op = row.operator("bim.edit_material_set_item", icon="CHECKMARK", text="Save Changes")
        op.material_set_item = set_item["id"]
        row.operator("bim.disable_editing_material_set_item", icon="CANCEL", text="")

        draw_attributes(self.props.material_set_item_attributes, box)

        row = box.row()
        prop_with_search(row, self.props, "material_set_item_material", icon="MATERIAL", text="Material")

        if ObjectMaterialData.data["set_item_name"] == "profile":
            row = box.row()
            prop_with_search(row, self.mprops, "profiles", icon="ITALIC", text="Profile")

    def draw_read_only_set_item_ui(self, box, set_item):
        if ObjectMaterialData.data["material_class"] == "IfcMaterialList":
            row = box.row(align=True)
            row.label(text="IfcMaterial", icon="LAYER_ACTIVE")
            row.label(text=set_item["name"], icon="MATERIAL")
        else:
            row = box.row(align=True)
            row.label(text=set_item["name"], icon=set_item["icon"])
            row.label(text=set_item["material"], icon="MATERIAL")

        if set_item["index_up"] is not None:
            op = row.operator("bim.reorder_material_set_item", icon="TRIA_UP", text="")
            op.old_index = set_item["index"]
            op.new_index = set_item["index_up"]
            setattr(op, "material_set", ObjectMaterialData.data["set"]["id"])
        if set_item["index_down"] is not None:
            op = row.operator("bim.reorder_material_set_item", icon="TRIA_DOWN", text="")
            op.old_index = set_item["index"]
            op.new_index = set_item["index_down"]
            setattr(op, "material_set", ObjectMaterialData.data["set"]["id"])
        if (
            not self.props.active_material_set_item_id
            and ObjectMaterialData.data["material_class"] != "IfcMaterialList"
        ):
            if "Profile" in ObjectMaterialData.data["material_class"]:
                op = row.operator("bim.profiles_ui_select", icon="ZOOM_SELECTED", text="")
                op.profile_id = set_item["profile_id"]
                op = row.operator("bim.enable_editing_material_set_item_profile", icon="ITALIC", text="")
                op.material_set_item = set_item["id"]
            op = row.operator("bim.enable_editing_material_set_item", icon="GREASEPENCIL", text="")
            op.material_set_item = set_item["id"]
        if ObjectMaterialData.data["set_item_name"] == "layer":
            row.operator("bim.duplicate_layer", icon="DUPLICATE", text="").layer = set_item["id"]
        op = row.operator(f"bim.remove_{ObjectMaterialData.data['set_item_name']}", icon="X", text="")
        if ObjectMaterialData.data["material_class"] == "IfcMaterialList":
            setattr(op, "list_item_set", ObjectMaterialData.data["set"]["id"])
        setattr(op, ObjectMaterialData.data["set_item_name"], set_item["id"])
        if hasattr(op, f"{ObjectMaterialData.data['set_item_name']}_index"):
            setattr(op, f"{ObjectMaterialData.data['set_item_name']}_index", set_item["index"])

    def draw_read_only_set_ui(self):
        if ObjectMaterialData.data["material_class"] != "IfcMaterialList":
            row = self.layout.row(align=True)
            set_name = ObjectMaterialData.data["set"]["name"]
            row.label(text="Name")
            row.label(text=set_name)

        if value := ObjectMaterialData.data["set"]["description"]:
            row = self.layout.row(align=True)
            row.label(text="Description")
            row.label(text=value)

        if ObjectMaterialData.data["material_class"] == "IfcMaterialProfileSetUsage":
            if value := ObjectMaterialData.data["set_usage"].get("cardinal_point"):
                row = self.layout.row(align=True)
                row.label(text="Cardinal Point")
                row.label(text=value)

        if ObjectMaterialData.data["total_thickness"]:
            row = self.layout.row(align=True)
            row.label(text="Total Thickness*")
            row.label(text=ObjectMaterialData.data["total_thickness"])

        box = self.layout.box()
        active_object = bpy.context.active_object
        self.layerset_bounds(box, active_object, location="Top_Interior")

        for set_item in ObjectMaterialData.data["set_items"]:
            material_name = set_item["material"]
            material_id = set_item["material_id"]
            if ObjectMaterialData.data["material_class"] == "IfcMaterialList":
                row = box.row()
                row.label(text="IfcMaterial", icon="LAYER_ACTIVE")
                op = row.operator("bim.select_by_material", text=material_name, emboss=False)
                op.material = material_id
            else:
                row = box.row()
                row.label(text=set_item["name"], icon=set_item["icon"])
                op = row.operator("bim.select_by_material", text=material_name, emboss=False)
                op.material = material_id

        self.layerset_bounds(box, active_object, location="Bottom_Exterior")

    def layerset_bounds(self, layout, obj, location="Top_Interior"):
        set_usage = ObjectMaterialData.data.get("set_usage", {})
        layer_set_direction = set_usage.get("layer_set_direction")
        if layer_set_direction:
            row = layout.row()
            row.alignment = "CENTER"
            row.enabled = False
            if location == "Top_Interior":
                if layer_set_direction == "AXIS3":
                    row.label(text="Top")
                else:
                    row.label(text="Interior")
            elif location == "Bottom_Exterior":
                if layer_set_direction == "AXIS3":
                    row.label(text="Bottom")
                else:
                    row.label(text="Exterior")


class BIM_UL_materials(UIList):
    def draw_item(
        self,
        context,
        layout: bpy.types.UILayout,
        data: BIMMaterialProperties,
        item: Material,
        icon,
        active_data,
        active_propname,
    ) -> None:
        material_type = data.material_type

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
                ifc_file = tool.Ifc.get()
                if ifc_file.schema == "IFC2X3":
                    row.label(text=item.name)
                else:
                    row.prop(item, "name", text="", emboss=False)
            else:
                row.label(text="", icon="BLANK1")
                if item.ifc_definition_id == data.active_material_id:
                    row.label(text="", icon="GREASEPENCIL")
                if material_type == "IfcMaterialList":
                    row.label(text=item.name, icon="MATERIAL")
                else:
                    row.prop(item, "name", text="", icon="MATERIAL", emboss=False)

                row2 = row.row()
                row2.alignment = "RIGHT"
                if item.has_style:
                    row2.label(text="", icon="SHADING_RENDERED")
                row2.label(text=str(item.total_elements))
