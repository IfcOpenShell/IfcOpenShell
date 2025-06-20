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
import bonsai.tool as tool
from bpy.types import Panel, UIList
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
        split = row.split(factor=0.55)

        left_row = split.row(align=True)
        left_row.label(text="{} Informations".format(DocumentData.data["total_document_informations"]), icon="FILE")
        left_row.label(text="{} References".format(DocumentData.data["total_document_references"]), icon="FILE_HIDDEN")

        right_row = split.row(align=True)
        right_row.label(
            text="{} Objects Referenced".format(DocumentData.data["total_referenced_objects"]), icon="OBJECT_DATA"
        )
        if self.props.is_editing:
            right_row.operator("bim.disable_document_editing_ui", text="", icon="CANCEL")
        else:
            right_row.operator("bim.load_project_documents", text="", icon="IMPORT")

        if not self.props.is_editing:
            return

        row = self.layout.row(align=True)
        row.alignment = "RIGHT"

        if self.props.is_document_editing:
            row.operator("bim.edit_document", text="", icon="CHECKMARK")
            row.operator("bim.disable_editing_document", text="", icon="CANCEL")
        else:
            if not self.props.documents or not self.props.active_document_index < len(self.props.documents) or \
            (self.props.active_document_index < len(self.props.documents) and 
                self.props.documents[self.props.active_document_index].is_information):
                row.operator("bim.add_information", text="", icon="ADD")

            if self.props.documents and self.props.active_document_index < len(self.props.documents):
                active_doc = self.props.documents[self.props.active_document_index]
                if active_doc.is_information and active_doc.ifc_definition_id != -1:
                    row.operator("bim.add_document_reference", text="", icon="FILE_HIDDEN")

            active_document = self.props.active_document
            if active_document:
                ifc_definition_id = active_document.ifc_definition_id
                row.operator("bim.select_document_objects", text="", icon="RESTRICT_SELECT_OFF").document = (
                    ifc_definition_id
                )
                
                row.operator("bim.assign_document", text="", icon="BRUSH_DATA").document = ifc_definition_id
                row.operator("bim.enable_editing_document", text="", icon="GREASEPENCIL").document = ifc_definition_id
                row.operator("bim.remove_document", text="", icon="X").document = ifc_definition_id
        self.layout.template_list("BIM_UL_documents", "", self.props, "documents", self.props, "active_document_index")

        if self.props.is_document_editing:
            active_document = self.props.active_document
            if active_document.is_information:
                draw_attributes(self.props.document_attributes, self.layout)
            else:
                draw_attributes(self.props.document_attributes, self.layout, filter_attributes=["Name"])

        if (
            self.props.is_editing
            and self.props.documents
            and self.props.active_document_index < len(self.props.documents)
        ):
            document = self.props.documents[self.props.active_document_index]
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
        if not ObjectDocumentData.is_loaded:
            ObjectDocumentData.load()

        obj = context.active_object
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
            if doc_count > 0:
                box = self.layout.box()
                row = box.row(align=True)
                row.label(text="Assigned Documents", icon="OUTLINER_OB_EMPTY")

                box.template_list(
                    "BIM_UL_assigned_documents",
                    "",
                    self.props,
                    "assigned_documents",
                    self.props,
                    "active_assigned_document_index",
                )

    def draw_add_ui(self):
        if self.props.is_object_editing:
            row = self.layout.row(align=True)
            row.alignment = "RIGHT"

            if self.props.documents and self.props.active_document_index < len(self.props.documents):
                document = self.props.documents[self.props.active_document_index]

                assigned_doc_ids = []
                for doc in ObjectDocumentData.data["documents"]:
                    assigned_doc_ids.append(doc["id"])

                # Only show assign button if the document is information (not reference) and not already assigned
                if (document.is_information and 
                    document.ifc_definition_id not in assigned_doc_ids):
                    doc_op = row.operator("bim.assign_document", text="", icon="BRUSH_DATA")
                    doc_op.document = document.ifc_definition_id  # Pass the current document's ID
                elif document.ifc_definition_id in assigned_doc_ids:
                    row.label(text="", icon="CHECKMARK")

            self.layout.template_list(
                "BIM_UL_documents", "", self.props, "documents", self.props, "active_document_index"
            )


class BIM_UL_documents(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if item:
            row = layout.row(align=True)
            indent_depth = 0

            if item.ifc_definition_id != -1:
                if item.tree_depth > 1:
                    indent_depth = item.tree_depth - 1
            for i in range(indent_depth):
                row.label(text="", icon="BLANK1")
            if item.ifc_definition_id == -1:
                row.label(text="", icon="OUTLINER_COLLECTION")
                row.label(text=item.name)
                return
            if item.is_information and item.has_children:
                op = row.operator(
                    "bim.toggle_document", icon="TRIA_DOWN" if item.is_expanded else "TRIA_RIGHT", text="", emboss=False
                )
                op.document = item.ifc_definition_id
                op.option = "Collapse" if item.is_expanded else "Expand"
            elif item.is_information:
                row.label(text="", icon="BLANK1")
            if item.is_information:
                row.label(text="", icon="FILE")
                text = " - ".join([x for x in [item.name, item.location] if x])
            else:
                row.label(text="", icon="FILE_HIDDEN")
                text = " - ".join([x for x in [item.description, item.location] if x])
            split1 = row.split(factor=0.1)
            split1.prop(item, "identification", text="", emboss=False)
            split2 = split1.split(factor=0.8)
            split2.label(text=text)

            if item.location:
                if item.location.lower().endswith(".ifc"):
                    row.operator("bim.open_ifc_document", icon="HIDE_OFF", text="").uri = item.location
                row.operator("bim.open_uri", icon="URL", text="").uri = item.location


class BIM_UL_document_objects(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if item:
            row = layout.row(align=True)
            row.prop(item, "name", text="", emboss=False, icon="OBJECT_DATA")
            row.operator("bim.select_object", text="", icon="RESTRICT_SELECT_OFF").obj_name = item.name

            props = tool.Document.get_document_props()
            if props.documents and props.active_document_index < len(props.documents):
                document = props.documents[props.active_document_index]

                op = row.operator("bim.unassign_document", text="", icon="X")
                op.document = document.ifc_definition_id
                op.obj = item.name


class BIM_UL_assigned_documents(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if item:
            row = layout.row(align=True)

            if item.is_information:
                row.label(text="", icon="FILE")
            else:
                row.label(text="", icon="FILE_HIDDEN")

            split1 = row.split(factor=0.2)
            split1.label(text=item.identification or "")

            split2 = split1.split(factor=1.0)
            if item.is_information:
                split2.label(text=item.name or "Unnamed")
            else:
                split2.label(text=item.description or "No Description")

            if item.location:
                if item.location.lower().endswith(".ifc"):
                    row.operator("bim.open_ifc_document", icon="HIDE_OFF", text="").uri = item.location
                row.operator("bim.open_uri", icon="URL", text="").uri = item.location
            op = row.operator("bim.unassign_document", text="", icon="X")
            op.document = item.ifc_definition_id


def add_object_documents_context_menu(self, context):
    if not context.active_object:
        return

    if not tool.Blender.get_ifc_definition_id(context.active_object):
        return

    self.layout.separator()
    self.layout.menu("BIM_MT_object_documents_context_menu", icon="FILE")


class BIM_MT_object_documents_context_menu(bpy.types.Menu):
    bl_idname = "BIM_MT_object_documents_context_menu"
    bl_label = "Documents"

    def draw(self, context):
        layout = self.layout

        if not context.selected_objects:
            layout.label(text="No documents", icon="INFO")
            return

        if len(context.selected_objects) > 1:
            layout.label(text="Select a single object to see its referenced documents", icon="INFO")
            return

        obj = context.active_object
        if not obj or not tool.Blender.get_ifc_definition_id(obj):
            layout.label(text="No documents", icon="INFO")
            return

        if not ObjectDocumentData.is_loaded:
            ObjectDocumentData.load()

        if not ObjectDocumentData.data["documents"]:
            layout.label(text="No Documents", icon="FILE")
        else:
            for document in ObjectDocumentData.data["documents"]:
                row = layout.row(align=True)

                with_ifc_icon = document["location"] and document["location"].lower().endswith(".ifc")
                with_url_icon = bool(document["location"])

                if with_ifc_icon:
                    row.operator("bim.open_ifc_document", icon="HIDE_OFF", text="").uri = document["location"]
                else:
                    row.label(text="", icon="BLANK1")

                if with_url_icon:
                    row.operator("bim.open_uri", icon="URL", text="").uri = document["location"]
                else:
                    row.label(text="", icon="BLANK1")

                doc_entity = None
                if "id" in document:
                    doc_entity = tool.Ifc.get().by_id(document["id"])

                if doc_entity and doc_entity.is_a("IfcDocumentReference"):
                    display_text = document.get("description") or ""
                else:
                    display_text = document.get("name") or ""

                row.label(text=f"{document['identification'] or ''}: {display_text}")
