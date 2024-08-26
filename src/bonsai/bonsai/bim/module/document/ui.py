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

from bpy.types import Panel, UIList
from bonsai.bim.ifc import IfcStore
from bonsai.bim.helper import draw_attributes
from bonsai.bim.module.document.data import DocumentData, ObjectDocumentData


class BIM_PT_documents(Panel):
    bl_label = "Documents"
    bl_idname = "BIM_PT_documents"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_tab_project_setup"

    @classmethod
    def poll(cls, context):
        return IfcStore.get_file()

    def draw(self, context):
        if not DocumentData.is_loaded:
            DocumentData.load()

        self.props = context.scene.BIMDocumentProperties

        row = self.layout.row(align=True)
        row.label(text="{} Documents Found".format(DocumentData.data["total_information"]), icon="FILE")
        if self.props.is_editing:
            row.operator("bim.disable_document_editing_ui", text="", icon="CANCEL")
        else:
            row.operator("bim.load_project_documents", text="", icon="IMPORT")

        if not self.props.is_editing:
            return

        row = self.layout.row(align=True)
        if self.props.breadcrumbs:
            row.operator("bim.load_parent_document", text="", icon="FRAME_PREV")
            row.label(text=DocumentData.data["parent_document"])
        else:
            row.alignment = "RIGHT"
        row.operator("bim.add_information", text="", icon="ADD")
        if self.props.breadcrumbs:
            row.operator("bim.add_document_reference", text="", icon="FILE_HIDDEN")

        if self.props.active_document_id:
            row.operator("bim.edit_document", text="", icon="CHECKMARK")
            row.operator("bim.disable_editing_document", text="", icon="CANCEL")
        elif self.props.documents and self.props.active_document_index < len(self.props.documents):
            ifc_definition_id = self.props.documents[self.props.active_document_index].ifc_definition_id
            row.operator("bim.select_document_objects", text="", icon="RESTRICT_SELECT_OFF").document = (
                ifc_definition_id
            )
            row.operator("bim.enable_editing_document", text="", icon="GREASEPENCIL").document = ifc_definition_id
            row.operator("bim.remove_document", text="", icon="X").document = ifc_definition_id

        self.layout.template_list("BIM_UL_documents", "", self.props, "documents", self.props, "active_document_index")

        if self.props.active_document_id:
            draw_attributes(self.props.document_attributes, self.layout)


class BIM_PT_object_documents(Panel):
    bl_label = "Documents"
    bl_idname = "BIM_PT_object_documents"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    bl_order = 1
    bl_parent_id = "BIM_PT_tab_misc"

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
        self.props = context.scene.BIMDocumentProperties
        self.file = IfcStore.get_file()

        self.draw_add_ui()

        if not ObjectDocumentData.data["documents"]:
            row = self.layout.row(align=True)
            row.label(text="No Documents", icon="FILE")

        for document in ObjectDocumentData.data["documents"]:
            row = self.layout.row(align=True)
            row.label(text=document["identification"] or "*", icon="FILE")
            row.label(text=document["name"] or "Unnamed")
            if document["location"]:
                row.operator("bim.open_uri", icon="URL", text="").uri = document["location"]
            row.operator("bim.unassign_document", text="", icon="X").document = document["id"]

    def draw_add_ui(self):
        if not self.props.is_editing:
            row = self.layout.row(align=True)
            row.operator("bim.load_project_documents", text="Assign Document References", icon="ADD")
            return

        row = self.layout.row(align=True)
        if self.props.breadcrumbs:
            row.operator("bim.load_parent_document", text="", icon="FRAME_PREV")
            row.label(text=DocumentData.data["parent_document"])
        else:
            row.alignment = "RIGHT"

        if self.props.documents and self.props.active_document_index < len(self.props.documents):
            document = self.props.documents[self.props.active_document_index]
            if not document.is_information:
                row.operator("bim.assign_document", text="", icon="ADD").document = document.ifc_definition_id
        row.operator("bim.disable_document_editing_ui", text="", icon="CANCEL")

        self.layout.template_list("BIM_UL_documents", "", self.props, "documents", self.props, "active_document_index")


class BIM_UL_documents(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if item:
            row = layout.row(align=True)

            if item.is_information:
                op = row.operator("bim.load_document", text="", emboss=False, icon="DISCLOSURE_TRI_RIGHT")
                op.document = item.ifc_definition_id
                row.label(text="", icon="FILE")
            else:
                row.label(text="", icon="BLANK1")
                row.label(text="", icon="FILE_HIDDEN")

            split1 = row.split(factor=0.1)
            split1.label(text=item.identification)
            split2 = split1.split(factor=0.9)
            split2.label(text=item.name)
