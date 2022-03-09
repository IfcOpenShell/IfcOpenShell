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

from bpy.types import Panel, UIList
from blenderbim.bim.ifc import IfcStore
from blenderbim.bim.helper import draw_attributes
from blenderbim.bim.module.document.data import DocumentData, ObjectDocumentData


class BIM_PT_documents(Panel):
    bl_label = "IFC Documents"
    bl_idname = "BIM_PT_documents"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_collaboration"

    @classmethod
    def poll(cls, context):
        return IfcStore.get_file()

    def draw(self, context):
        if not DocumentData.is_loaded:
            DocumentData.load()

        self.props = context.scene.BIMDocumentProperties

        if not self.props.is_editing or self.props.is_editing == "information":
            row = self.layout.row(align=True)
            row.label(text="{} Documents Found".format(DocumentData.data["total_information"]), icon="FILE")
            if self.props.is_editing == "information":
                row.operator("bim.add_information", text="", icon="ADD")
                row.operator("bim.disable_document_editing_ui", text="", icon="CANCEL")
            else:
                row.operator("bim.load_information", text="", icon="IMPORT")

        if not self.props.is_editing or self.props.is_editing == "reference":
            row = self.layout.row(align=True)
            row.label(text="{} References Found".format(DocumentData.data["total_references"]), icon="FILE_HIDDEN")
            if self.props.is_editing == "reference":
                row.operator("bim.add_document_reference", text="", icon="ADD")
                row.operator("bim.disable_document_editing_ui", text="", icon="CANCEL")
            else:
                row.operator("bim.load_document_references", text="", icon="IMPORT")

        if self.props.is_editing:
            self.layout.template_list(
                "BIM_UL_documents", "", self.props, "documents", self.props, "active_document_index"
            )

        if self.props.active_document_id:
            self.draw_editable_ui(context)

    def draw_editable_ui(self, context):
        draw_attributes(self.props.document_attributes, self.layout)


class BIM_PT_object_documents(Panel):
    bl_label = "IFC Documents"
    bl_idname = "BIM_PT_object_documents"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    bl_parent_id = "BIM_PT_misc_object"

    @classmethod
    def poll(cls, context):
        if not context.active_object:
            return False
        if not IfcStore.get_element(context.active_object.BIMObjectProperties.ifc_definition_id):
            return False
        return bool(context.active_object.BIMObjectProperties.ifc_definition_id)

    def draw(self, context):
        if not ObjectDocumentData.is_loaded:
            ObjectDocumentData.load()

        obj = context.active_object
        self.oprops = obj.BIMObjectProperties
        self.sprops = context.scene.BIMDocumentProperties
        self.props = obj.BIMObjectDocumentProperties
        self.file = IfcStore.get_file()

        self.draw_add_ui()

        if not ObjectDocumentData.data["documents"]:
            row = self.layout.row(align=True)
            row.label(text="No Documents", icon="FILE")

        for document in ObjectDocumentData.data["documents"]:
            row = self.layout.row(align=True)
            row.label(text=document["identification"] or "*", icon="FILE")
            row.label(text=document["name"] or "Unnamed")
            row.operator("bim.unassign_document", text="", icon="X").document = document["id"]

    def draw_add_ui(self):
        if self.props.is_adding:
            row = self.layout.row(align=True)
            icon = "FILE" if self.props.is_adding == "IfcDocumentInformation" else "FILE_HIDDEN"
            row.label(text="Adding {}".format(self.props.is_adding), icon=icon)
            row.operator("bim.disable_assigning_document", text="", icon="CANCEL")
            self.layout.template_list(
                "BIM_UL_object_documents",
                "",
                self.sprops,
                "documents",
                self.sprops,
                "active_document_index",
            )
        else:
            row = self.layout.row(align=True)
            row.prop(self.props, "available_document_types", text="")
            row.operator("bim.enable_assigning_document", text="", icon="ADD")


class BIM_UL_documents(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if item:
            row = layout.row(align=True)
            row.label(text=item.identification)
            row.label(text=item.name)
            if context.scene.BIMDocumentProperties.active_document_id == item.ifc_definition_id:
                if context.scene.BIMDocumentProperties.is_editing == "information":
                    row.operator("bim.edit_information", text="", icon="CHECKMARK")
                elif context.scene.BIMDocumentProperties.is_editing == "reference":
                    row.operator("bim.edit_document_reference", text="", icon="CHECKMARK")
                row.operator("bim.disable_editing_document", text="", icon="CANCEL")
            elif context.scene.BIMDocumentProperties.active_document_id:
                row.operator("bim.remove_document", text="", icon="X").document = item.ifc_definition_id
            else:
                op = row.operator("bim.enable_editing_document", text="", icon="GREASEPENCIL")
                op.document = item.ifc_definition_id
                row.operator("bim.remove_document", text="", icon="X").document = item.ifc_definition_id


class BIM_UL_object_documents(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if item:
            row = layout.row(align=True)
            row.label(text=item.identification)
            row.label(text=item.name)
            row.operator("bim.assign_document", text="", icon="ADD").document = item.ifc_definition_id
