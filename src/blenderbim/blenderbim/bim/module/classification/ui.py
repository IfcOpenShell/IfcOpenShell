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
import blenderbim.tool as tool
import blenderbim.bim.module.classification.prop as classification_prop
from bpy.types import Panel, UIList
from blenderbim.bim.ifc import IfcStore
from blenderbim.bim.module.classification.data import (
    ClassificationsData,
    ClassificationReferencesData,
    MaterialClassificationsData,
    CostClassificationsData,
)


class BIM_PT_classifications(Panel):
    bl_label = "IFC Classifications"
    bl_idname = "BIM_PT_classifications"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_project_setup"

    @classmethod
    def poll(cls, context):
        return tool.Ifc.get()

    def draw(self, context):
        if not ClassificationsData.is_loaded:
            ClassificationsData.load()

        self.props = context.scene.BIMClassificationProperties

        if ClassificationsData.data["has_classification_file"]:
            row = self.layout.row(align=True)
            row.prop(self.props, "available_classifications", text="")
            row.operator("bim.load_classification_library", text="", icon="IMPORT")
            row.operator("bim.add_classification", text="", icon="ADD")
        else:
            row = self.layout.row(align=True)
            row.label(text="No Active Classification Library")
            row.operator("bim.load_classification_library", text="", icon="IMPORT")

        for classification in ClassificationsData.data["classifications"]:
            if self.props.active_classification_id == classification["id"]:
                self.draw_editable_ui()
            else:
                self.draw_ui(classification)

    def draw_editable_ui(self):
        row = self.layout.row(align=True)
        row.operator("bim.edit_classification", text="Save changes", icon="CHECKMARK")
        row.operator("bim.disable_editing_classification", text="", icon="CANCEL")
        blenderbim.bim.helper.draw_attributes(self.props.classification_attributes, self.layout)

    def draw_ui(self, classification):
        row = self.layout.row(align=True)
        row.label(text=classification["Name"], icon="ASSET_MANAGER")
        if not self.props.active_classification_id:
            op = row.operator("bim.enable_editing_classification", text="", icon="GREASEPENCIL")
            op.classification = classification["id"]
        row.operator("bim.remove_classification", text="", icon="X").classification = classification["id"]


class ReferenceUI:
    def draw_ui(self, context):
        obj = context.active_object
        self.oprops = obj.BIMObjectProperties
        self.sprops = context.scene.BIMClassificationProperties
        self.props = obj.BIMClassificationReferenceProperties
        self.file = IfcStore.get_file()

        self.draw_add_ui(context)

        if not self.data.data["references"]:
            row = self.layout.row(align=True)
            row.label(text="No References")

        for reference in self.data.data["references"]:
            if self.props.active_reference_id == reference["id"]:
                self.draw_editable_ui()
            else:
                self.draw_reference_ui(reference)

    def draw_add_ui(self, context):
        if not self.data.data["is_available_classification_added"]:
            return
        row = self.layout.row(align=True)
        row.prop(self.sprops, "available_classifications", text="")
        if not self.sprops.available_library_references:
            op = row.operator("bim.change_classification_level", text="", icon="IMPORT")
            op.parent_id = int(self.sprops.available_classifications)
            return
        if self.sprops.active_library_referenced_source:
            op = row.operator("bim.change_classification_level", text="", icon="FRAME_PREV")
            op.parent_id = self.sprops.active_library_referenced_source
        if self.sprops.active_library_reference_index < len(self.sprops.available_library_references):
            op = row.operator("bim.add_classification_reference", text="", icon="ADD")
            op.obj = self.obj
            op.obj_type = self.obj_type
            op.reference = self.sprops.available_library_references[
                self.sprops.active_library_reference_index
            ].ifc_definition_id
        row.operator("bim.disable_editing_classification_references", text="", icon="CANCEL")
        self.layout.template_list(
            "BIM_UL_classifications",
            "",
            self.sprops,
            "available_library_references",
            self.sprops,
            "active_library_reference_index",
        )

    def draw_editable_ui(self):
        row = self.layout.row(align=True)
        row.operator("bim.edit_classification_reference", text="Save changes", icon="CHECKMARK")
        row.operator("bim.disable_editing_classification_reference", text="", icon="CANCEL")
        blenderbim.bim.helper.draw_attributes(self.props.reference_attributes, self.layout)

    def draw_reference_ui(self, reference):
        row = self.layout.row(align=True)
        if self.file.schema == "IFC2X3":
            name = reference["ItemReference"] or "No Identification"
        else:
            name = reference["Identification"] or "No Identification"
        row.label(text=name, icon="ASSET_MANAGER")
        row.label(text=reference["Name"] or "")
        if not self.props.active_reference_id:
            op = row.operator("bim.enable_editing_classification_reference", text="", icon="GREASEPENCIL")
            op.reference = reference["id"]
        op = row.operator("bim.remove_classification_reference", text="", icon="X")
        op.reference = reference["id"]
        op.obj = self.obj
        op.obj_type = self.obj_type


class BIM_PT_classification_references(Panel, ReferenceUI):
    bl_label = "IFC Classification References"
    bl_idname = "BIM_PT_classification_references"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    bl_parent_id = "BIM_PT_object_metadata"

    @classmethod
    def poll(cls, context):
        if not context.active_object:
            return False
        return bool(tool.Ifc.get_entity(context.active_object))

    def draw(self, context):
        if not ClassificationReferencesData.is_loaded:
            ClassificationReferencesData.load()
        self.data = ClassificationReferencesData
        self.obj = context.active_object.name
        self.obj_type = "Object"
        self.draw_ui(context)


class BIM_PT_material_classifications(Panel, ReferenceUI):
    bl_label = "IFC Material Classifications"
    bl_idname = "BIM_PT_material_classifications"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "material"

    @classmethod
    def poll(cls, context):
        if not tool.Ifc.get():
            return False
        try:
            return bool(context.active_object.active_material.BIMObjectProperties.ifc_definition_id)
        except:
            return False

    def draw(self, context):
        if not MaterialClassificationsData.is_loaded:
            MaterialClassificationsData.load()
        self.data = MaterialClassificationsData
        self.obj = context.active_object.active_material.name
        self.obj_type = "Material"
        self.draw_ui(context)


class BIM_PT_cost_classifications(Panel, ReferenceUI):
    bl_label = "IFC Cost Classifications"
    bl_idname = "BIM_PT_cost_classifications"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_cost_schedules"

    @classmethod
    def poll(cls, context):
        if not tool.Ifc.get():
            return False
        return bool(context.scene.BIMCostProperties.cost_items)

    def draw(self, context):
        if not CostClassificationsData.is_loaded:
            CostClassificationsData.load()
        self.data = CostClassificationsData
        self.obj = ""
        self.obj_type = "Cost"
        self.draw_ui(context)


class BIM_UL_classifications(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if item:
            if item.has_references:
                op = layout.operator("bim.change_classification_level", text="", icon="DISCLOSURE_TRI_RIGHT")
                op.parent_id = item.ifc_definition_id
            layout.label(text=item.identification)
            layout.label(text=item.name)
