import os
import bpy
from . import bcfstore
from bpy.types import Panel

class BIM_PT_bcf(Panel):
    bl_label = "BIM Collaboration Format (BCF)"
    bl_idname = "BIM_PT_bcf"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        scene = context.scene
        props = bpy.context.scene.BCFProperties

        row = layout.row(align=True)
        row.operator("bim.new_bcf_project", text="New Project")
        row.operator("bim.load_bcf_project", text="Load Project")

        if not props.is_loaded:
            return

        row.operator("bim.save_bcf_project", text="Save Project")

        row = layout.row()
        row.prop(props, "name")

        row = layout.row()
        row.prop(props, "author")

        props = bpy.context.scene.BCFProperties
        row = layout.row()
        row.template_list("BIM_UL_topics", "", props, "topics", props, "active_topic_index")
        col = row.column(align=True)
        col.operator("bim.add_bcf_topic", icon="ADD", text="")
        if props.active_topic_index < len(props.topics):
            topic = props.topics[props.active_topic_index]
            col.prop(topic, "is_editable", icon="CHECKMARK" if topic.is_editable else "GREASEPENCIL", icon_only=True)

        if props.active_topic_index < len(props.topics):
            topic = props.topics[props.active_topic_index]
            row = layout.row()
            row.enabled = topic.is_editable
            row.prop(topic, "description", text="")

            row = layout.row()
            row.prop(topic, "viewpoints")
            row.operator("bim.activate_bcf_viewpoint", icon="SCENE", text="")
            row.operator("bim.add_bcf_viewpoint", icon="ADD", text="")
            row.operator("bim.remove_bcf_viewpoint", icon="X", text="")

            col = layout.column(align=True)
            if topic.type:
                col.prop(topic, "type", emboss=topic.is_editable)
            if topic.status:
                col.prop(topic, "status", emboss=topic.is_editable)
            if topic.priority:
                col.prop(topic, "priority", emboss=topic.is_editable)
            if topic.stage:
                col.prop(topic, "stage", emboss=topic.is_editable)
            if topic.assigned_to:
                col.prop(topic, "assigned_to", emboss=topic.is_editable)
            if topic.due_date:
                col.prop(topic, "due_date", emboss=topic.is_editable)

            col = layout.column(align=True)
            if topic.modified_date:
                col.prop(topic, "modified_date", emboss=False)
                col.prop(topic, "modified_author", emboss=False)
            else:
                col.prop(topic, "creation_date", emboss=False)
                col.prop(topic, "creation_author", emboss=False)


class BIM_PT_bcf_metadata(Panel):
    bl_label = "BCF Metadata"
    bl_idname = "BIM_PT_bcf_metadata"
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
        props = bpy.context.scene.BCFProperties

        if props.active_topic_index >= len(props.topics):
            layout.label(text="No BCF project is loaded")
            return

        topic = props.topics[props.active_topic_index]
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        bcf_topic = bcfxml.topics[topic.name]

        layout.label(text="Header Files:")

        if bcf_topic.header:
            for index, f in enumerate(bcf_topic.header.files):
                box = self.layout.box()
                row = box.row(align=True)
                row.label(text=f.filename, icon="FILE_BLANK")
                if f.is_external:
                    row.operator("bim.open_uri", icon="URL", text="").uri = f.reference
                else:
                    op = row.operator("bim.open_uri", icon="FILE_FOLDER", text="")
                    op.uri = os.path.join(bcfxml.filepath, topic.name, f.reference)
                row.operator("bim.remove_bcf_file", icon="X", text="").index = index

                row = box.row()
                row.label(text="Date")
                row.label(text=f.date)

                if f.ifc_project:
                    row = box.row()
                    row.label(text="IFC Project")
                    row.label(text=f.ifc_project)

                if f.ifc_spatial_structure_element:
                    row = box.row()
                    row.label(text="IFC Spatial Structure Element")
                    row.label(text=f.ifc_spatial_structure_element)

        row = layout.row(align=True)
        row.prop(topic, "file_reference")
        row.operator("bim.select_bcf_header_file", icon="FILE_FOLDER", text="")
        row = layout.row()
        row.prop(topic, "file_ifc_project")
        row = layout.row()
        row.prop(topic, "file_ifc_spatial_structure_element")

        row = layout.row()
        row.operator("bim.add_bcf_header_file")

        layout.label(text="Reference Links:")
        for index, link in enumerate(topic.reference_links):
            row = layout.row(align=True)
            row.prop(link, "name")
            row.operator("bim.open_uri", icon="URL", text="").uri = link.name
            row.operator("bim.remove_bcf_reference_link", icon="X", text="").index = index
        row = layout.row()
        row.prop(topic, "reference_link")
        row = layout.row()
        row.operator("bim.add_bcf_reference_link")

        layout.label(text="Labels:")
        for index, label in enumerate(topic.labels):
            row = layout.row(align=True)
            row.prop(label, "name", text="")
            row.operator("bim.remove_bcf_label", icon="X", text="").index = index
        row = layout.row()
        row.prop(topic, "label")
        row = layout.row()
        row.operator("bim.add_bcf_label")

        layout.label(text="BIM Snippet:")
        if topic.bim_snippet.schema:
            row = layout.row(align=True)
            row.prop(topic.bim_snippet, "type", emboss=False)
            if topic.bim_snippet.schema:
                row.operator("bim.open_uri", icon="URL", text="").uri = topic.bim_snippet.schema

            row = layout.row(align=True)
            row.prop(topic.bim_snippet, "reference", emboss=False)
            if topic.bim_snippet.is_external:
                row.operator("bim.open_uri", icon="URL", text="").uri = topic.bim_snippet.reference
            else:
                op = row.operator("bim.open_uri", icon="FILE_FOLDER", text="")
                op.uri = os.path.join(bcfxml.filepath, topic.name, topic.bim_snippet.reference)
            row.operator("bim.remove_bcf_bim_snippet", icon="X", text="")
        else:
            row = layout.row(align=True)
            row.prop(topic, "bim_snippet_reference")
            row.operator("bim.select_bcf_bim_snippet_reference", icon="FILE_FOLDER", text="")
            row = layout.row()
            row.prop(topic, "bim_snippet_type")
            row = layout.row()
            row.prop(topic, "bim_snippet_schema")
            row = layout.row()
            row.operator("bim.add_bcf_bim_snippet")

        layout.label(text="Document References:")
        for index, doc in enumerate(topic.document_references):
            box = self.layout.box()
            row = box.row(align=True)
            row.prop(doc, "reference")
            if doc.is_external:
                row.operator("bim.open_uri", icon="URL", text="").uri = doc.reference
            else:
                op = row.operator("bim.open_uri", icon="FILE_FOLDER", text="")
                op.uri = os.path.join(bcfxml.filepath, topic.name, doc.reference)
            row.operator("bim.remove_bcf_document_reference", icon="X", text="").index = index
            row = box.row(align=True)
            row.prop(doc, "description")
        row = layout.row(align=True)
        row.prop(topic, "document_reference")
        row.operator("bim.select_bcf_document_reference", icon="FILE_FOLDER", text="")
        row = layout.row()
        row.prop(topic, "document_reference_description")
        row = layout.row()
        row.operator("bim.add_bcf_document_reference")

        layout.label(text="Related Topics:")
        for index, related_topic in enumerate(topic.related_topics):
            row = layout.row(align=True)
            row.operator("bim.view_bcf_topic", text=bcfxml.topics[related_topic.name.lower()].title).topic_guid = related_topic.name
            row.operator("bim.remove_bcf_related_topic", icon="X", text="").index = index
        row = layout.row()
        row.prop(topic, "related_topic")
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
        props = bpy.context.scene.BCFProperties

        if props.active_topic_index >= len(props.topics):
            layout.label(text="No BCF project is loaded")
            return

        row = layout.row()
        row.prop(props, "comment_text_width")

        topic = props.topics[props.active_topic_index]
        for comment in topic.comments:
            box = self.layout.box()

            author_text = "{} ({})".format(comment.author, comment.date)
            if comment.modified_author:
                author_text = "*{} ({})".format(comment.modified_author, comment.modified_date)
            row = box.row(align=True)
            row.label(text=author_text, icon="WORDWRAP_ON")
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
        row.prop(topic, "comment")
        row = layout.row()
        row.prop(topic, "has_related_viewpoint")
        row = layout.row()
        row.operator("bim.add_bcf_comment")
