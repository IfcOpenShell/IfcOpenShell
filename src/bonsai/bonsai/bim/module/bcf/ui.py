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

import os
import bpy
import bonsai.tool as tool
from . import bcfstore
from bpy.types import Panel


class BIM_PT_bcf(Panel):
    bl_label = "BCF Project"
    bl_idname = "BIM_PT_bcf"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_tab_collaboration"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        scene = context.scene
        props = scene.BCFProperties

        if not bcfstore.BcfStore.get_bcfxml():
            row = layout.row(align=True)
            row.operator("bim.new_bcf_project", text="New Project")
            row.operator("bim.load_bcf_project", text="Load Project")
            layout.prop(props, "bcf_version")
            return

        row = layout.row(align=True)
        op = row.operator("bim.save_bcf_project", icon="FILE_TICK", text="Save Current Project")
        op.save_current_bcf = True
        row.operator("bim.save_bcf_project", icon="EXPORT", text="Save Project As...")
        row.operator("bim.unload_bcf_project", text="", icon="CANCEL")

        row = layout.row()
        row.prop(props, "bcf_version", emboss=False)
        row.enabled = False

        row = layout.row()
        row.prop(props, "name")

        row = layout.row()
        row.prop(props, "author")

        props = context.scene.BCFProperties
        row = layout.row()
        row.template_list("BIM_UL_topics", "", props, "topics", props, "active_topic_index")
        col = row.column(align=True)
        col.operator("bim.add_bcf_topic", icon="ADD", text="")
        col.operator("bim.remove_bcf_topic", icon="REMOVE", text="")
        if props.active_topic_index < len(props.topics):
            topic = props.active_topic
            is_editable = topic.is_editable
            col.prop(topic, "is_editable", icon="CHECKMARK" if topic.is_editable else "GREASEPENCIL", icon_only=True)

            topic = props.active_topic
            row = layout.row()
            row.enabled = is_editable
            row.prop(topic, "description", text="")

            row = layout.row()
            row.prop(topic, "viewpoints")
            row.operator("bim.activate_bcf_viewpoint", icon="SCENE", text="")
            row.operator("bim.add_bcf_viewpoint", icon="ADD", text="")
            row.operator("bim.remove_bcf_viewpoint", icon="X", text="")

            col = layout.column(align=True)
            topic_props = ("type", "status", "priority", "stage", "assigned_to", "due_date")
            bl_rna_props = topic.bl_rna.properties

            def draw_prop(prop_name: str) -> None:
                row = col.row(align=True)
                row.label(text=f"{bl_rna_props[prop_name].name}")
                row.label(text=getattr(topic, prop_name))

            for prop in topic_props:
                if getattr(topic, prop) or is_editable:
                    # Can't just use emboss because search= on props is changing
                    # how they look and adds "ui.button_string_clear" button
                    # which allows clearing out the string and we don't want to.
                    if is_editable:
                        col.prop(topic, prop, emboss=is_editable)
                    else:
                        draw_prop(prop)

            col = layout.column(align=True)
            if topic.modified_date:
                draw_prop("modified_date")
                draw_prop("modified_author")
            else:
                draw_prop("creation_date")
                draw_prop("creation_author")


class BIM_PT_bcf_metadata(Panel):
    bl_label = "BCF Metadata"
    bl_idname = "BIM_PT_bcf_metadata"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_bcf"

    def draw(self, context):
        # TODO: in bcf v3 documents can be added to the bcf
        # without adding them to specific topic.
        # Currently we just handle it the same way as in v2
        # documents are accessed and managed from topics.
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        scene = context.scene
        props = scene.BCFProperties

        bcfxml = bcfstore.BcfStore.get_bcfxml()
        if not bcfxml or props.active_topic_index >= len(props.topics):
            layout.label(text="No BCF project is loaded")
            return
        bcf_verison = bcfxml.version.version_id or ""
        bcf_v3 = bcf_verison.startswith("3")

        topic = props.active_topic
        bcf_topic = bcfxml.topics[topic.name]

        layout.label(text="Header Files:")

        if bcf_topic.header:
            for index, f in enumerate(tool.Bcf.get_topic_header_files(bcf_topic)):
                box = self.layout.box()
                row = box.row(align=True)
                row.label(text=f.filename, icon="FILE_BLANK")
                if f.is_external:
                    row.operator("bim.open_uri", icon="URL", text="").uri = f.reference
                else:
                    op = row.operator("bim.load_bcf_header_ifc_file", icon="FILE_REFRESH", text="")
                    op.index = index
                    op = row.operator("bim.extract_bcf_file", icon="FILE_FOLDER", text="")
                    op.index = index
                    op.entity_type = "HEADER_FILE"
                row.operator("bim.remove_bcf_file", icon="X", text="").index = index

                row = box.row()
                row.label(text="Date")
                row.label(text=str(f.date))

                if f.ifc_project:
                    row = box.row()
                    row.label(text="IFC Project")
                    row.label(text=f.ifc_project)

                if f.ifc_spatial_structure_element:
                    row = box.row()
                    row.label(text="IFC Spatial Structure Element")
                    row.label(text=f.ifc_spatial_structure_element)

        row = layout.row(align=True)
        row.prop(props, "file_reference")
        row.operator("bim.select_bcf_header_file", icon="FILE_FOLDER", text="")
        row = layout.row()
        row.prop(props, "file_ifc_project")
        row = layout.row()
        row.prop(props, "file_ifc_spatial_structure_element")

        row = layout.row()
        row.operator("bim.add_bcf_header_file")

        layout.label(text="Reference Links:")
        for index, link in enumerate(topic.reference_links):
            row = layout.row(align=True)
            row.prop(link, "name", text="")
            row.operator("bim.open_uri", icon="URL", text="").uri = link.name
            row.operator("bim.remove_bcf_reference_link", icon="X", text="").index = index
        row = layout.row()
        row.prop(props, "reference_link", text="New Reference Link:")
        row = layout.row()
        row.operator("bim.add_bcf_reference_link")

        layout.label(text="Labels:")
        for index, label in enumerate(topic.labels):
            row = layout.row(align=True)
            row.prop(label, "name", text="")
            row.operator("bim.remove_bcf_label", icon="X", text="").index = index
        row = layout.row()
        row.prop(props, "label")
        row = layout.row()
        row.operator("bim.add_bcf_label")

        layout.label(text="BIM Snippet:")
        if topic.bim_snippet.reference:
            row = layout.row(align=True)
            row.prop(topic.bim_snippet, "type", emboss=False)
            if topic.bim_snippet.schema:
                row.operator("bim.open_uri", icon="URL", text="").uri = topic.bim_snippet.schema

            row = layout.row(align=True)
            row.prop(topic.bim_snippet, "reference", emboss=False)
            if topic.bim_snippet.is_external:
                row.operator("bim.open_uri", icon="URL", text="").uri = topic.bim_snippet.reference
            else:
                op = row.operator("bim.extract_bcf_file", icon="FILE_FOLDER", text="")
                op.entity_type = "BIM_SNIPPET"
            row.operator("bim.remove_bcf_bim_snippet", icon="X", text="")
        else:
            row = layout.row(align=True)
            row.prop(props, "bim_snippet_reference")
            row.operator("bim.select_bcf_bim_snippet_reference", icon="FILE_FOLDER", text="")
            row = layout.row()
            row.prop(props, "bim_snippet_type")
            row = layout.row()
            row.prop(props, "bim_snippet_schema")
            row = layout.row()
            row.operator("bim.add_bcf_bim_snippet")

        layout.label(text="Document References:")
        for index, doc in enumerate(topic.document_references):
            box = self.layout.box()
            row = box.row(align=True)
            row.prop(doc, "reference", emboss=False)
            if doc.is_external:
                row.operator("bim.open_uri", icon="URL", text="").uri = doc.reference
            else:
                op = row.operator("bim.extract_bcf_file", icon="FILE_FOLDER", text="")
                op.entity_type = "DOCUMENT_REFERENCE"
                op.index = index

            row.operator("bim.remove_bcf_document_reference", icon="X", text="").index = index
            row = box.row(align=True)
            row.prop(doc, "description", emboss=False)
        row = layout.row(align=True)
        row.prop(props, "document_reference")
        row.operator("bim.select_bcf_document_reference", icon="FILE_FOLDER", text="")
        row = layout.row()
        row.prop(
            props, "document_reference_description", text="Reference Description" if bcf_v3 else "Document Description"
        )
        if bcf_v3:
            row = layout.row()
            row.prop(props, "document_description")
        row = layout.row()
        row.operator("bim.add_bcf_document_reference")

        layout.label(text="Related Topics:")
        for index, related_topic in enumerate(topic.related_topics):
            try:
                row = layout.row(align=True)
                op = row.operator(
                    "bim.view_bcf_topic", text=f"Select {bcfxml.topics[related_topic.name.lower()].topic.title}"
                )
                op.topic_guid = related_topic.name
                row.operator("bim.remove_bcf_related_topic", icon="X", text="").index = index
            except KeyError:
                pass

        if len(props.topics) == len(topic.related_topics) + 1:
            layout.label(text="No topics to add as related.")
        else:
            row = layout.row()
            row.prop(props, "related_topic")
            row = layout.row()
            row.operator("bim.add_bcf_related_topic")


class BIM_PT_bcf_comments(Panel):
    bl_label = "BCF Comments"
    bl_idname = "BIM_PT_bcf_comments"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_bcf"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        scene = context.scene
        props = scene.BCFProperties

        if props.active_topic_index >= len(props.topics):
            layout.label(text="No BCF project is loaded")
            return

        row = layout.row()
        row.prop(props, "comment_text_width")

        topic = props.active_topic
        for comment in topic.comments:
            box = self.layout.box()

            author_text = "{} ({})".format(comment.author, comment.date)
            if comment.modified_author:
                author_text = "*{} ({})".format(comment.modified_author, comment.modified_date)
            row = box.row(align=True)
            row.label(text=author_text, icon="WORDWRAP_ON")
            if comment.viewpoint:
                op = row.operator("bim.activate_bcf_viewpoint", icon="SCENE", text="")
                op.viewpoint_guid = comment.viewpoint
            row.prop(
                comment, "is_editable", icon="CHECKMARK" if comment.is_editable else "GREASEPENCIL", icon_only=True
            )
            row.operator("bim.remove_bcf_comment", icon="X", text="").comment_guid = comment.name

            if comment.is_editable:
                row = box.row()
                row.prop(comment, "comment", text="")
            else:
                col = box.column(align=True)
                col.scale_y = 0.8
                words = comment.comment.split()
                while words:
                    total_line_chars = 0
                    line_words = []
                    while words and total_line_chars < props.comment_text_width:
                        word = words.pop(0)
                        line_words.append(word)
                        total_line_chars += len(word) + 1  # 1 is for the space
                    col.label(text=" ".join(line_words))

        row = layout.row()
        row.prop(props, "comment")
        row = layout.row()
        row.prop(props, "has_related_viewpoint")
        row = layout.row()
        row.operator("bim.add_bcf_comment")
