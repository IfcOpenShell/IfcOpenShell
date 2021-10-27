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

import blenderbim.bim.module.classification.prop as classification_prop
from bpy.types import Panel, UIList
from blenderbim.bim.ifc import IfcStore
from blenderbim.bim.module.classification.data import ClassificationData
#from ifcopenshell.api.classification.data import Data


class BIM_PT_classifications(Panel):
    bl_label = "IFC Classifications"
    bl_idname = "BIM_PT_classifications"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"

    @classmethod
    def poll(cls, context):
        return IfcStore.get_file()  #Is it better tool.Ifc.get() ??

    def draw(self, context):
        if not ClassificationData.is_loaded:
            ClassificationData.load()

        self.props = context.scene.BIMClassificationProperties

        if ClassificationData.library_file:
            row = self.layout.row(align=True)
            row.prop(self.props, "available_classifications", text="")
            row.operator("bim.load_classification_library", text="", icon="IMPORT")
            row.operator("bim.add_classification", text="", icon="ADD")
        else:
            row = self.layout.row(align=True)
            row.label(text="No Active Classification Library")
            row.operator("bim.load_classification_library", text="", icon="IMPORT")

        for classification_id, classification in ClassificationData.data["classifications"].items():
            if self.props.active_classification_id == classification_id:
                self.draw_editable_ui(classification)
            else:
                self.draw_ui(classification_id, classification)

    def draw_editable_ui(self, classification):
        row = self.layout.row(align=True)
        row.prop(self.props.classification_attributes.get("Name"), "string_value", text="", icon="ASSET_MANAGER")
        row.operator("bim.edit_classification", text="", icon="CHECKMARK")
        row.operator("bim.disable_editing_classification", text="", icon="CANCEL")

        for attribute in self.props.classification_attributes:
            if attribute.name == "Name":
                continue
            row = self.layout.row(align=True)
            row.prop(attribute, "string_value", text=attribute.name)
            if attribute.is_optional:
                row.prop(attribute, "is_null", icon="RADIOBUT_OFF" if attribute.is_null else "RADIOBUT_ON", text="")

    def draw_ui(self, classification_id, classification):
        row = self.layout.row(align=True)
        row.label(text=classification["Name"], icon="ASSET_MANAGER")
        if not self.props.active_classification_id:
            op = row.operator("bim.enable_editing_classification", text="", icon="GREASEPENCIL")
            op.classification = classification_id
        row.operator("bim.remove_classification", text="", icon="X").classification = classification_id


class BIM_PT_classification_references(Panel):
    bl_label = "IFC Classification References"
    bl_idname = "BIM_PT_classification_references"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        if not context.active_object:
            return False
        if not IfcStore.get_element(context.active_object.BIMObjectProperties.ifc_definition_id):
            return False
        return bool(context.active_object.BIMObjectProperties.ifc_definition_id)

    def draw(self, context):
        obj = context.active_object
        self.oprops = obj.BIMObjectProperties
        self.sprops = context.scene.BIMClassificationProperties
        self.props = obj.BIMClassificationReferenceProperties
        self.file = IfcStore.get_file()
        if not ClassificationData.is_loaded:
            ClassificationData.load()
        if self.oprops.ifc_definition_id not in ClassificationData.products:
            ClassificationData.load(self.oprops.ifc_definition_id)

        self.draw_add_ui(context)

        reference_ids = ClassificationData.products[self.oprops.ifc_definition_id]
        if not reference_ids:
            row = self.layout.row(align=True)
            row.label(text="No References")

        for reference_id in reference_ids:
            reference = ClassificationData.data["references"][reference_id]
            if self.props.active_reference_id == reference_id:
                self.draw_editable_ui(reference)
            else:
                self.draw_ui(reference_id, reference)

    def draw_add_ui(self, context):
        if not classification_prop.getClassifications(self.sprops, context):
            return

        name = ClassificationData.library_classifications[int(self.sprops.available_classifications)]
        if name in [c["Name"] for c in ClassificationData.data["classifications"].values()]:
            row = self.layout.row(align=True)
            row.prop(self.sprops, "available_classifications", text="")
            if self.sprops.active_library_referenced_source:
                op = row.operator("bim.change_classification_level", text="", icon="FRAME_PREV")
                op.parent_id = self.sprops.active_library_referenced_source
            op = row.operator("bim.add_classification_reference", text="", icon="ADD")
            op.reference = self.sprops.available_library_references[
                self.sprops.active_library_reference_index
            ].ifc_definition_id
            self.layout.template_list(
                "BIM_UL_classifications",
                "",
                self.sprops,
                "available_library_references",
                self.sprops,
                "active_library_reference_index",
            )

    def draw_editable_ui(self, reference):
        row = self.layout.row(align=True)
        row.prop(self.props.reference_attributes.get("Name"), "string_value", text="", icon="ASSET_MANAGER")
        row.operator("bim.edit_classification_reference", text="", icon="CHECKMARK")
        row.operator("bim.disable_editing_classification_reference", text="", icon="CANCEL")

        for attribute in self.props.reference_attributes:
            if attribute.name == "Name":
                continue
            row = self.layout.row(align=True)
            row.prop(attribute, "string_value", text=attribute.name)
            if attribute.is_optional:
                row.prop(attribute, "is_null", icon="RADIOBUT_OFF" if attribute.is_null else "RADIOBUT_ON", text="")

    def draw_ui(self, reference_id, reference):
        row = self.layout.row(align=True)
        if self.file.schema == "IFC2X3":
            name = reference["ItemReference"] or "No Identification"
        else:
            name = reference["Identification"] or "No Identification"
        row.label(text=name, icon="ASSET_MANAGER")
        row.label(text=reference["Name"] or "")
        if not self.props.active_reference_id:
            op = row.operator("bim.enable_editing_classification_reference", text="", icon="GREASEPENCIL")
            op.reference = reference_id
        row.operator("bim.remove_classification_reference", text="", icon="X").reference = reference_id


class BIM_UL_classifications(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if item:
            if item.has_references:
                op = layout.operator("bim.change_classification_level", text="", icon="DISCLOSURE_TRI_RIGHT")
                op.parent_id = item.ifc_definition_id
            layout.label(text=item.identification)
            layout.label(text=item.name)
