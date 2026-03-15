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

from typing import TYPE_CHECKING

import bpy
from bpy.types import Panel, UIList

import bonsai.tool as tool

if TYPE_CHECKING:
    from bonsai.bim.module.document.prop import (
        BIMDocumentProperties,
        Document,
        DocumentObject,
    )

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
        return tool.Ifc.get()

    def draw(self, context):
        if not DocumentData.is_loaded:
            DocumentData.load()

        self.props = tool.Document.get_document_props()

        row = self.layout.row(align=True)
        row.label(text="{} Documents found".format(DocumentData.data["total_documents"]), icon="FILE")

        if self.props.is_editing:
            row.operator("bim.disable_document_editing_ui", text="", icon="CANCEL")
        else:
            row.operator("bim.load_project_documents", text="", icon="IMPORT")

        if not self.props.is_editing:
            return

        row = self.layout.row(align=True)
        row.alignment = "RIGHT"

        if self.props.active_document_id > 0:
            row.operator("bim.edit_document", text="", icon="CHECKMARK")
            row.operator("bim.disable_editing_document", text="", icon="CANCEL")
        else:
            if not self.props.active_document or self.props.active_document.document_type in ["INFORMATION", "PROJECT"]:
                row.operator("bim.add_information", text="", icon="ADD")

            if self.props.active_document and (
                self.props.active_document.document_type == "INFORMATION"
                and self.props.active_document.document_type != "PROJECT"
            ):
                row.operator("bim.add_document_reference", text="", icon="FILE_HIDDEN")

            active_document = self.props.active_document
            if active_document:
                ifc_definition_id = active_document.ifc_definition_id

                if active_document.document_type != "PROJECT":
                    row.operator("bim.select_document_objects", text="", icon="RESTRICT_SELECT_OFF").document = (
                        ifc_definition_id
                    )
                    row.operator("bim.assign_document", text="", icon="BRUSH_DATA").document = ifc_definition_id
                    row.operator("bim.enable_editing_document", text="", icon="GREASEPENCIL").document = (
                        ifc_definition_id
                    )
                    row.operator("bim.remove_document", text="", icon="X").document = ifc_definition_id
        self.layout.template_list("BIM_UL_documents", "", self.props, "documents", self.props, "active_document_index")

        if self.props.active_document_id > 0:
            active_document = self.props.active_document
            draw_attributes(self.props.document_attributes, self.layout)

        if self.props.is_editing and self.props.active_document:
            document = self.props.active_document
            box = self.layout.box()
            row = box.row(align=True)
            row.label(text="Assigned Objects", icon="OUTLINER_OB_EMPTY")
            box.template_list(
                "BIM_UL_document_objects",
                "",
                self.props,
                "document_objects",
                self.props,
                "active_document_object_index",
            )


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
        if not (obj := context.active_object):
            return False
        if not (ifc_id := tool.Blender.get_ifc_definition_id(obj)):
            return False
        if not tool.Ifc.get_object_by_identifier(ifc_id):
            return False
        return True

    def draw(self, context):
        obj = context.active_object
        if not ObjectDocumentData.is_loaded:
            ObjectDocumentData.load()

        self.oprops = tool.Blender.get_object_bim_props(obj)
        self.props = tool.Document.get_document_props()
        self.file = tool.Ifc.get()

        doc_count = len(ObjectDocumentData.data["documents"])

        row = self.layout.row(align=True)
        row.label(text="{} Documents Assigned".format(doc_count), icon="FILE")

        if self.props.is_object_editing:
            row.operator("bim.disable_object_document_editing_ui", text="", icon="CANCEL")
        else:
            row.operator("bim.load_object_documents", text="", icon="IMPORT")

        if not self.props.is_object_editing and doc_count == 0:
            row = self.layout.row()
            row.label(text="No documents assigned", icon="INFO")
            return

        if self.props.is_object_editing:
            self.draw_add_ui()
            box = self.layout.box()
            row = box.row(align=True)
            row.label(text="Assigned Documents", icon="OUTLINER_OB_EMPTY")

            if doc_count > 0:
                col = box.column(align=True)
                for document in ObjectDocumentData.data["documents"]:
                    row = col.row(align=True)

                    # Create a split layout to separate left and right sides
                    split = row.split(factor=0.7)  # Adjust factor as needed (0.7 = 70% left, 30% right)

                    # Left side - Document identification and name
                    left_side = split.row(align=True)
                    left_side.alignment = "LEFT"
                    left_side.label(text=document["identification"] or "*", icon="FILE")
                    left_side.label(text=document["name"] or "Unnamed")

                    # Right side - Action buttons
                    right_side = split.row(align=True)
                    right_side.alignment = "RIGHT"  # Align buttons to the right

                    if document["location"]:
                        if document["location"].lower().endswith(".ifc"):
                            right_side.operator("bim.open_ifc_document", icon="HIDE_OFF", text="").uri = document[
                                "location"
                            ]
                        right_side.operator("bim.open_uri", icon="URL", text="").uri = document["location"]

                    right_side.operator("bim.unassign_document", text="", icon="X").document = document["id"]

    def draw_add_ui(self):
        if self.props.is_object_editing:
            row = self.layout.row(align=True)
            row.alignment = "RIGHT"

            if self.props.active_document:
                document = self.props.active_document

                assigned_doc_ids = []
                for doc in ObjectDocumentData.data["documents"]:
                    assigned_doc_ids.append(doc["id"])

                if (
                    document.document_type == "INFORMATION"
                    and document.document_type != "PROJECT"
                    and document.ifc_definition_id not in assigned_doc_ids
                ):
                    doc_op = row.operator("bim.assign_document", text="", icon="BRUSH_DATA")
                    doc_op.document = document.ifc_definition_id
                elif document.ifc_definition_id in assigned_doc_ids:
                    row.label(text="", icon="CHECKMARK")
            self.layout.template_list(
                "BIM_UL_documents", "", self.props, "documents", self.props, "active_document_index"
            )


class BIM_UL_documents(UIList):
    def draw_item(
        self,
        context,
        layout: bpy.types.UILayout,
        data: BIMDocumentProperties,
        item: Document,
        icon,
        active_data,
        active_propname,
    ) -> None:
        if item:
            row = layout.row(align=True)
            indent_depth = 0

            if item.document_type != "PROJECT":
                if item.tree_depth > 1:
                    indent_depth = item.tree_depth - 1

            for i in range(indent_depth):
                row.label(text="", icon="BLANK1")

            if item.document_type == "PROJECT":
                row.label(text="", icon="OUTLINER_COLLECTION")
                row.label(text=item.name)
                return

            if item.document_type == "INFORMATION" and item.has_children:
                op = row.operator(
                    "bim.toggle_document", icon="TRIA_DOWN" if item.is_expanded else "TRIA_RIGHT", text="", emboss=False
                )
                op.document = item.ifc_definition_id
                op.option = "Collapse" if item.is_expanded else "Expand"
            elif item.document_type == "INFORMATION":
                row.label(text="", icon="BLANK1")

            if item.document_type == "INFORMATION":
                row.label(text="", icon="FILE")
                text = " - ".join([x for x in [item.location, item.description, item.name] if x])
            else:
                row.label(text="", icon="FILE_HIDDEN")
                text = " - ".join([x for x in [item.location, item.description] if x])
            split1 = row.split(factor=0.1)
            split1.prop(item, "identification", text="", emboss=False)
            split2 = split1.split(factor=0.8)
            split2.label(text=text)

            if item.location:
                uri = ObjectDocumentData.convert_to_file_uri(item.location)
                if item.location.lower().endswith(".ifc"):
                    row.operator("bim.open_ifc_document", icon="HIDE_OFF", text="").uri = uri
                row.operator("bim.open_uri", icon="URL", text="").uri = uri


class BIM_UL_document_objects(UIList):
    def draw_item(
        self,
        context,
        layout: bpy.types.UILayout,
        data: BIMDocumentProperties,
        item: DocumentObject,
        icon,
        active_data,
        active_propname,
    ) -> None:
        if item:
            row = layout.row(align=True)
            row.prop(item, "name", text="", emboss=False, icon="OBJECT_DATA")
            row.operator("bim.select_object", text="", icon="RESTRICT_SELECT_OFF").obj_name = item.name

            if document := data.active_document:
                op = row.operator("bim.unassign_document", text="", icon="X")
                op.document = document.ifc_definition_id
                op.obj = item.name
