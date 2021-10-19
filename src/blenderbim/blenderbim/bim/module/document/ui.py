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
from ifcopenshell.api.document.data import Data


class BIM_PT_documents(Panel):
    bl_label = "IFC Documents"
    bl_idname = "BIM_PT_documents"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"

    @classmethod
    def poll(cls, context):
        view_setting = context.preferences.addons["blenderbim"].preferences.module_visibility
        if not IfcStore.get_file():
            return False
        return view_setting.document

    def draw(self, context):
        if not Data.is_loaded:
            Data.load(IfcStore.get_file())

        self.props = context.scene.BIMDocumentProperties

        if not self.props.is_editing or self.props.is_editing == "information":
            row = self.layout.row(align=True)
            row.label(text="{} Documents Found".format(len(Data.information)), icon="FILE")
            if self.props.is_editing == "information":
                row.operator("bim.add_information", text="", icon="ADD")
                row.operator("bim.disable_document_editing_ui", text="", icon="CANCEL")
            else:
                row.operator("bim.load_information", text="", icon="IMPORT")

        if not self.props.is_editing or self.props.is_editing == "reference":
            row = self.layout.row(align=True)
            row.label(text="{} References Found".format(len(Data.references)), icon="FILE_HIDDEN")
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

    @classmethod
    def poll(cls, context):
        view_setting = context.preferences.addons["blenderbim"].preferences.module_visibility
        if not context.active_object:
            return False
        if not IfcStore.get_element(context.active_object.BIMObjectProperties.ifc_definition_id):
            return False
        if not bool(context.active_object.BIMObjectProperties.ifc_definition_id):
            return False
        return view_setting.document


    def draw(self, context):
        obj = context.active_object
        self.oprops = obj.BIMObjectProperties
        self.sprops = context.scene.BIMDocumentProperties
        self.props = obj.BIMObjectDocumentProperties
        self.file = IfcStore.get_file()
        if not Data.is_loaded:
            Data.load(IfcStore.get_file())
        if self.oprops.ifc_definition_id not in Data.products:
            Data.load(IfcStore.get_file(), self.oprops.ifc_definition_id)

        self.draw_add_ui()

        document_ids = Data.products[self.oprops.ifc_definition_id]

        if not document_ids:
            row = self.layout.row(align=True)
            row.label(text="No Documents", icon="FILE")

        for document_id in document_ids:
            try:
                document = Data.information[document_id]
                document_type = "IfcDocumentInformation"
                icon = "FILE"
            except:
                document = Data.references[document_id]
                document_type = "IfcDocumentReference"
                icon = "FILE_HIDDEN"
            row = self.layout.row(align=True)
            if self.file.schema == "IFC2X3":
                if document_type == "IfcDocumentInformation":
                    row.label(text=document.get("DocumentId") or "*", icon=icon)
                elif document_type == "IfcDocumentReference":
                    row.label(text=document.get("ItemReference") or "*", icon=icon)
            else:
                row.label(text=document.get("Identification") or "*", icon=icon)
            row.label(text=document.get("Name") or "Unnamed")
            row.operator("bim.unassign_document", text="", icon="X").document = document_id

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
