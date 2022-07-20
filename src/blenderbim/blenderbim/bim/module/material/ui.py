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
from ifcopenshell.api.profile.data import Data as ProfileData
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
        if not Data.is_loaded:
            Data.load(IfcStore.get_file())
        if self.oprops.ifc_definition_id not in Data.products:
            Data.load(IfcStore.get_file(), self.oprops.ifc_definition_id)
        if not ProfileData.is_loaded:
            ProfileData.load(self.file)
        self.product_data = Data.products[self.oprops.ifc_definition_id]

        if not ObjectMaterialData.data["materials"]:
            row = self.layout.row(align=True)
            row.label(text="No Materials Available")
            row.operator("bim.add_material", icon="ADD", text="").obj = ""
            return

        if ObjectMaterialData.data["type_material"]:
            row = self.layout.row(align=True)
            row.label(text="Inherited Material: " + ObjectMaterialData.data["type_material"], icon="FILE_PARENT")

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
            else:
                self.material_set_id = 0
            return self.draw_material_ui()

        row = self.layout.row(align=True)
        prop_with_search(row, self.props, "material_type", text="")
        if self.props.material_type == "IfcMaterial" or self.props.material_type == "IfcMaterialList":
            prop_with_search(row, self.props, "material", text="")
        row.operator("bim.assign_material", icon="ADD", text="")

    def draw_material_ui(self):
        row = self.layout.row(align=True)
        row.label(text=self.product_data["type"])

        if self.props.is_editing:
            op = row.operator("bim.edit_assigned_material", icon="CHECKMARK", text="")
            op.material_set = self.material_set_id
            if "Usage" in self.product_data["type"]:
                op.material_set_usage = self.product_data["id"]
            row.operator("bim.disable_editing_assigned_material", icon="CANCEL", text="")
        else:
            if self.product_data["type"] == "IfcMaterial":
                row.operator("bim.copy_material", icon="COPYDOWN", text="")
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
        prop_with_search(self.layout, self.props, "material", text="")

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
        blenderbim.bim.helper.draw_attributes(self.props.material_set_usage_attributes, self.layout)

        for attribute in self.props.material_set_attributes:
            row = self.layout.row(align=True)
            row.prop(attribute, "string_value", text=attribute.name)
            row.prop(attribute, "is_null", icon="RADIOBUT_OFF" if attribute.is_null else "RADIOBUT_ON", text="")
        row = self.layout.row(align=True)
        prop_with_search(row, self.props, "material", text="")

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
        row.operator("bim.disable_editing_material_set_item", icon="CANCEL", text="")

        draw_attributes(self.props.material_set_item_attributes, self.layout)

        if self.set_item_name == "profile":
            self.draw_assign_profile_ui(box, item)
            self.draw_editable_profile_ui(box, item)

    def draw_assign_profile_ui(self, layout, item):
        row = layout.row(align=True)
        row.prop(self.props, "profile_classes", text="")
        if self.props.profile_classes == "IfcParameterizedProfileDef":
            row.prop(self.props, "parameterized_profile_classes", text="")
            op = row.operator(
                "bim.assign_parameterized_profile", icon="GREASEPENCIL" if item["Profile"] else "ADD", text=""
            )
            op.ifc_class = self.props.parameterized_profile_classes
            op.material_profile = item["id"]
        else:
            # TODO: support non parametric profiles by showing a list of named profiles to select from, or an
            # eyedropper to pick profile geometry from the scene
            row.operator("bim.disable_editing_material_set_item", icon="CANCEL", text="")

    def draw_editable_profile_ui(self, layout, item):
        draw_attributes(self.props.material_set_item_profile_attributes, self.layout)

    def draw_read_only_set_item_ui(self, set_item_id, index, is_first=False, is_last=False):
        if self.product_data["type"] == "IfcMaterialList":
            item = Data.materials[set_item_id]
            row = self.layout.row(align=True)
            row.label(text="IfcMaterial", icon="ALIGN_CENTER")
            row.label(text=item["Name"], icon="MATERIAL")
        else:
            item = self.set_data[set_item_id]
            row = self.layout.row(align=True)
            item_name = item.get("Name", "Unnamed") or "Unnamed"
            thickness = item.get("LayerThickness")
            if thickness:
                item_name += f" ({thickness})"
            row.label(text=item_name, icon="ALIGN_CENTER")
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
        if hasattr(op, f"{self.set_item_name}_index"):
            setattr(op, f"{self.set_item_name}_index", index)

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

        if self.product_data["type"] == "IfcMaterialProfileSetUsage":
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
            if self.material_set_usage["CardinalPoint"]:
                row = self.layout.row(align=True)
                row.label(text="CardinalPoint")
                row.label(text=cardinal_point_map[self.material_set_usage["CardinalPoint"]])
            if self.material_set_usage["ReferenceExtent"]:
                row = self.layout.row(align=True)
                row.label(text="ReferenceExtent")
                row.label(text=str(self.material_set_usage["ReferenceExtent"]))

        total_thickness = 0
        for item_id in self.set_items:
            if self.product_data["type"] == "IfcMaterialList":
                row = self.layout.row(align=True)
                row.label(text="IfcMaterial", icon="ALIGN_CENTER")
                row.label(text=Data.materials[item_id]["Name"], icon="MATERIAL")
            else:
                item = self.set_data[item_id]
                row = self.layout.row(align=True)
                item_name = item.get("Name", "Unnamed") or "Unnamed"
                thickness = item.get("LayerThickness")
                if thickness:
                    item_name += f" ({thickness:.3f})"
                    total_thickness += thickness
                row.label(text=item_name, icon="ALIGN_CENTER")
                row.label(text=Data.materials[item["Material"]]["Name"], icon="MATERIAL")

        if total_thickness:
            row = self.layout.row(align=True)
            row.label(text=f"Total Thickness: {total_thickness:.3f}")


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
