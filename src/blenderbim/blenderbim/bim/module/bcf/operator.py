import os
import bpy
import bcf
import bcf.bcfxml
import bcf.v2.data
import numpy as np
import ifcopenshell
import ifcopenshell.util.unit
from . import bcfstore
from blenderbim.bim.ifc import IfcStore
from math import radians, degrees, atan, tan, cos, sin
from mathutils import Vector, Matrix, Euler, geometry

class NewBcfProject(bpy.types.Operator):
    bl_idname = "bim.new_bcf_project"
    bl_label = "New BCF Project"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        context.scene.BCFProperties.is_loaded = False
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        bcfxml.new_project()
        bpy.ops.bim.load_bcf_project()
        context.scene.BCFProperties.is_loaded = True
        return {"FINISHED"}


class LoadBcfProject(bpy.types.Operator):
    bl_idname = "bim.load_bcf_project"
    bl_label = "Load BCF Project"
    bl_options = {"REGISTER", "UNDO"}
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    filter_glob: bpy.props.StringProperty(default="*.bcf;*.bcfzip", options={"HIDDEN"})

    def execute(self, context):
        context.scene.BCFProperties.is_loaded = False
        if self.filepath:
            bcfstore.BcfStore.bcfxml = bcf.bcfxml.load(self.filepath)
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        bcfxml.get_project()
        context.scene.BCFProperties.name = bcfxml.project.name
        bpy.ops.bim.load_bcf_topics()
        context.scene.BCFProperties.is_loaded = True
        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}


class LoadBcfTopics(bpy.types.Operator):
    bl_idname = "bim.load_bcf_topics"
    bl_label = "Load BCF Topics"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        bcfxml.get_topics()
        while len(context.scene.BCFProperties.topics) > 0:
            context.scene.BCFProperties.topics.remove(0)
        index = 0
        for topic_guid in bcfxml.topics.keys():
            new = context.scene.BCFProperties.topics.add()
            bpy.ops.bim.load_bcf_topic(topic_guid = topic_guid, topic_index = index)
            index += 1
        return {"FINISHED"}


class LoadBcfTopic(bpy.types.Operator):
    bl_idname = "bim.load_bcf_topic"
    bl_label = "Load BCF Topics"
    bl_options = {"REGISTER", "UNDO"}
    topic_guid: bpy.props.StringProperty()
    topic_index: bpy.props.IntProperty()

    def execute(self, context):
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        topic = bcfxml.get_topic(self.topic_guid)
        new = context.scene.BCFProperties.topics[self.topic_index]
        data_map = {
            "name": topic.guid,
            "title": topic.title,
            "type": topic.topic_type,
            "status": topic.topic_status,
            "priority": topic.priority,
            "stage": topic.stage,
            "creation_date": topic.creation_date,
            "creation_author": topic.creation_author,
            "modified_date": topic.modified_date,
            "modified_author": topic.modified_author,
            "assigned_to": topic.assigned_to,
            "due_date": topic.due_date,
            "description": topic.description
        }
        for key, value in data_map.items():
            if value is not None:
                setattr(new, key, str(value))
        while len(new.reference_links) > 0:
            new.reference_links.remove(0)
        for reference_link in topic.reference_links:
            new2 = new.reference_links.add()
            new2.name = reference_link
        while len(new.labels) > 0:
            new.labels.remove(0)
        for label in topic.labels:
            new2 = new.labels.add()
            new2.name = label
        if topic.bim_snippet:
            data_map = {
                "type": topic.bim_snippet.snippet_type,
                "is_external": topic.bim_snippet.is_external,
                "reference": topic.bim_snippet.reference,
                "schema": topic.bim_snippet.reference_schema
            }
            for key, value in data_map.items():
                if value is not None:
                    setattr(new.bim_snippet, key, value)
        while len(new.document_references) > 0:
            new.document_references.remove(0)
        for doc in topic.document_references:
            new2 = new.document_references.add()
            data_map = {
                "reference": doc.referenced_document,
                "description": doc.description,
                "guid": doc.guid,
                "is_external": doc.is_external
            }
            for key, value in data_map.items():
                if value is not None:
                    setattr(new2, key, value)
        while len(new.related_topics) > 0:
            new.related_topics.remove(0)
        for related_topic in topic.related_topics:
            new2 = new.related_topics.add()
            new2.name = related_topic.guid
        bpy.ops.bim.load_bcf_comments(topic_guid = topic.guid)
        return {"FINISHED"}


class LoadBcfComments(bpy.types.Operator):
    bl_idname = "bim.load_bcf_comments"
    bl_label = "Load BCF Comments"
    bl_options = {"REGISTER", "UNDO"}
    topic_guid: bpy.props.StringProperty()

    def execute(self, context):
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        bcfxml.get_comments(self.topic_guid)
        blender_topic = context.scene.BCFProperties.topics.get(self.topic_guid)
        while len(blender_topic.comments) > 0:
            blender_topic.comments.remove(0)
        for comment in bcfxml.topics[self.topic_guid].comments.values():
            new = blender_topic.comments.add()
            data_map = {
                "name": comment.guid,
                "comment": comment.comment,
                "viewpoint": comment.viewpoint.guid if comment.viewpoint else None,
                "date": comment.date,
                "author": comment.author,
                "modified_date": comment.modified_date,
                "modified_author": comment.modified_author,
            }
            for key, value in data_map.items():
                if value is not None:
                    setattr(new, key, str(value))
        return {"FINISHED"}


class EditBcfProjectName(bpy.types.Operator):
    bl_idname = "bim.edit_bcf_project_name"
    bl_label = "Edit BCF Project Name"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        bcfxml.project.name = context.scene.BCFProperties.name
        bcfxml.edit_project()
        return {"FINISHED"}


class EditBcfAuthor(bpy.types.Operator):
    bl_idname = "bim.edit_bcf_author"
    bl_label = "Edit BCF Author"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        bcfxml.author = context.scene.BCFProperties.author
        return {"FINISHED"}


class EditBcfTopicName(bpy.types.Operator):
    bl_idname = "bim.edit_bcf_topic_name"
    bl_label = "Edit BCF Topic Name"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = context.scene.BCFProperties
        blender_topic = props.topics[props.active_topic_index]
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        topic = bcfxml.topics[blender_topic.name]
        topic.title = blender_topic.title
        bcfxml.edit_topic(topic)
        return {"FINISHED"}


class EditBcfTopic(bpy.types.Operator):
    bl_idname = "bim.edit_bcf_topic"
    bl_label = "Edit BCF Topic"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = context.scene.BCFProperties
        blender_topic = props.topics[props.active_topic_index]
        bcfxml = bcfstore.BcfStore.get_bcfxml()

        topic = bcfxml.topics[blender_topic.name]
        topic.title = blender_topic.title or None
        topic.priority = blender_topic.priority or None
        topic.due_date = blender_topic.due_date or None
        topic.assigned_to = blender_topic.assigned_to or None
        topic.stage = blender_topic.stage or None
        topic.description = blender_topic.description or None
        topic.topic_status = blender_topic.status or None
        topic.topic_type = blender_topic.type or None

        bcfxml.edit_topic(topic)
        props.active_topic_index = props.active_topic_index # Refreshes the BCF Topic
        return {"FINISHED"}


class SaveBcfProject(bpy.types.Operator):
    bl_idname = "bim.save_bcf_project"
    bl_label = "Save BCF Project"
    bl_options = {"REGISTER", "UNDO"}
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        bcfxml.save_project(self.filepath)
        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}


class AddBcfTopic(bpy.types.Operator):
    bl_idname = "bim.add_bcf_topic"
    bl_label = "Add BCF Topic"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        bcfxml.add_topic()
        new = context.scene.BCFProperties.topics.add()
        new.name = "New Topic"
        bpy.ops.bim.load_bcf_topics()
        return {"FINISHED"}


class AddBcfBimSnippet(bpy.types.Operator):
    bl_idname = "bim.add_bcf_bim_snippet"
    bl_label = "Add BCF BIM Snippet"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        props = context.scene.BCFProperties
        blender_topic = props.topics[props.active_topic_index]
        topic = bcfxml.topics[blender_topic.name]
        bim_snippet = bcf.v2.data.BimSnippet()
        bim_snippet.reference = blender_topic.bim_snippet_reference
        bim_snippet.reference_schema = blender_topic.bim_snippet_schema
        bim_snippet.snippet_type = blender_topic.bim_snippet_type
        bcfxml.add_bim_snippet(topic, bim_snippet)
        bpy.ops.bim.load_bcf_topic(topic_guid = topic.guid, topic_index = props.active_topic_index)
        return {"FINISHED"}


class AddBcfRelatedTopic(bpy.types.Operator):
    bl_idname = "bim.add_bcf_related_topic"
    bl_label = "Add BCF Related Topic"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        props = context.scene.BCFProperties
        blender_topic = props.topics[props.active_topic_index]
        related_topic = None
        for topic in bcfxml.topics.values():
            if topic.title == blender_topic.related_topic:
                related_topic = bcf.v2.data.RelatedTopic()
                related_topic.guid = topic.guid
                break
        if not related_topic:
            return {"FINISHED"}
        topic = bcfxml.topics[blender_topic.name]
        topic.related_topics.append(related_topic)
        bcfxml.edit_topic(topic)
        bpy.ops.bim.load_bcf_topic(topic_guid = topic.guid, topic_index = props.active_topic_index)
        return {"FINISHED"}


class AddBcfHeaderFile(bpy.types.Operator):
    bl_idname = "bim.add_bcf_header_file"
    bl_label = "Add BCF Header File"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        props = context.scene.BCFProperties
        blender_topic = props.topics[props.active_topic_index]
        topic = bcfxml.topics[blender_topic.name]
        header_file = bcf.v2.data.HeaderFile()
        header_file.reference = blender_topic.file_reference
        if not os.path.exists(header_file.reference):
            header_file.filename = header_file.reference
        if len(blender_topic.file_ifc_project) == 22:
            header_file.ifc_project = blender_topic.file_ifc_project
        if len(blender_topic.file_ifc_spatial_structure_element) == 22:
            header_file.ifc_spatial_structure_element = blender_topic.file_ifc_spatial_structure_element
        bcfxml.add_file(topic, header_file)
        props.active_topic_index = props.active_topic_index # refreshes the BCF Topic
        return {"FINISHED"}


class ViewBcfTopic(bpy.types.Operator):
    bl_idname = "bim.view_bcf_topic"
    bl_label = "Get BCF Topic"
    bl_options = {"REGISTER", "UNDO"}
    topic_guid: bpy.props.StringProperty()

    def execute(self, context):
        for index, topic in enumerate(context.scene.BCFProperties.topics):
            if topic.guid.lower() == self.topic_guid.lower():
                context.scene.BCFProperties.active_topic_index = index
        return {"FINISHED"}


class AddBcfViewpoint(bpy.types.Operator):
    bl_idname = "bim.add_bcf_viewpoint"
    bl_label = "Add BCF Viewpoint"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        if not context.scene.camera:
            return {"FINISHED"}
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        props = context.scene.BCFProperties
        blender_topic = props.topics[props.active_topic_index]
        topic = bcfxml.topics[blender_topic.name]
        viewpoint = bcf.v2.data.Viewpoint()

        if context.scene.camera.data.type == "ORTHO":
            camera = bcf.v2.data.OrthogonalCamera()
            camera.view_to_world_scale = context.scene.camera.data.ortho_scale
            viewpoint.orthogonal_camera = camera
        elif context.scene.camera.data.type == "PERSP":
            camera = bcf.v2.data.PerspectiveCamera()
            camera.field_of_view = degrees(context.scene.camera.data.angle)
            viewpoint.perspective_camera = camera
        camera.camera_view_point.x = context.scene.camera.location.x
        camera.camera_view_point.y = context.scene.camera.location.y
        camera.camera_view_point.z = context.scene.camera.location.z
        direction = context.scene.camera.matrix_world.to_quaternion() @ Vector((0.0, 0.0, -1.0))
        camera.camera_direction.x = direction.x
        camera.camera_direction.y = direction.y
        camera.camera_direction.z = direction.z
        up = context.scene.camera.matrix_world.to_quaternion() @ Vector((0.0, 1.0, 0.0))
        camera.camera_up_vector.x = up.x
        camera.camera_up_vector.y = up.y
        camera.camera_up_vector.z = up.z

        old_file_format = context.scene.render.image_settings.file_format
        context.scene.render.image_settings.file_format = "PNG"
        old_filepath = context.scene.render.filepath
        context.scene.render.filepath = os.path.join(context.scene.BIMProperties.data_dir, "snapshot.png")
        bpy.ops.render.opengl(write_still=True)
        viewpoint.snapshot = context.scene.render.filepath

        bcfxml.add_viewpoint(topic, viewpoint)
        context.scene.render.filepath = old_filepath
        context.scene.render.image_settings.file_format = old_file_format
        props.active_topic_index = props.active_topic_index # refreshes the BCF Topic
        return {"FINISHED"}


class RemoveBcfViewpoint(bpy.types.Operator):
    bl_idname = "bim.remove_bcf_viewpoint"
    bl_label = "Remove BCF Viewpoint"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        props = context.scene.BCFProperties
        blender_topic = props.topics[props.active_topic_index]
        viewpoint_guid = blender_topic.viewpoints
        topic = bcfxml.topics[blender_topic.name]
        bcfxml.delete_viewpoint(viewpoint_guid, topic)
        props.active_topic_index = props.active_topic_index # Refreshes the BCF Topic
        return {"FINISHED"}


class RemoveBcfFile(bpy.types.Operator):
    bl_idname = "bim.remove_bcf_file"
    bl_label = "Remove BCF File"
    bl_options = {"REGISTER", "UNDO"}
    index: bpy.props.IntProperty()

    def execute(self, context):
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        props = context.scene.BCFProperties
        blender_topic = props.topics[props.active_topic_index]
        topic = bcfxml.topics[blender_topic.name]
        bcfxml.delete_file(topic, self.index)
        props.active_topic_index = props.active_topic_index # Refreshes the BCF Topic
        return {"FINISHED"}


class AddBcfReferenceLink(bpy.types.Operator):
    bl_idname = "bim.add_bcf_reference_link"
    bl_label = "Add BCF Reference Link"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        props = context.scene.BCFProperties
        blender_topic = props.topics[props.active_topic_index]
        topic = bcfxml.topics[blender_topic.name]
        if not blender_topic.reference_link:
            return {"FINISHED"}
        topic.reference_links.append(blender_topic.reference_link)
        bcfxml.edit_topic(topic)
        bpy.ops.bim.load_bcf_topic(topic_guid = topic.guid, topic_index = props.active_topic_index)
        blender_topic.reference_link = ""
        return {"FINISHED"}


class AddBcfDocumentReference(bpy.types.Operator):
    bl_idname = "bim.add_bcf_document_reference"
    bl_label = "Add BCF Document Reference"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        props = context.scene.BCFProperties
        blender_topic = props.topics[props.active_topic_index]
        topic = bcfxml.topics[blender_topic.name]
        if not blender_topic.document_reference:
            return {"FINISHED"}
        document_reference = bcf.v2.data.DocumentReference()
        document_reference.referenced_document = blender_topic.document_reference
        document_reference.description = blender_topic.document_reference_description or None
        bcfxml.add_document_reference(topic, document_reference)
        bpy.ops.bim.load_bcf_topic(topic_guid = topic.guid, topic_index = props.active_topic_index)
        blender_topic.document_reference = ""
        blender_topic.document_reference_description = ""
        return {"FINISHED"}


class AddBcfLabel(bpy.types.Operator):
    bl_idname = "bim.add_bcf_label"
    bl_label = "Add BCF Label"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        props = context.scene.BCFProperties
        blender_topic = props.topics[props.active_topic_index]
        topic = bcfxml.topics[blender_topic.name]
        if not blender_topic.label:
            return {"FINISHED"}
        new = blender_topic.labels.add()
        new.name = blender_topic.label
        topic.labels.append(blender_topic.label)
        bcfxml.edit_topic(topic)
        blender_topic.label = ""
        return {"FINISHED"}


class EditBcfReferenceLinks(bpy.types.Operator):
    bl_idname = "bim.edit_bcf_reference_links"
    bl_label = "Edit BCF Reference Link"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        props = context.scene.BCFProperties
        blender_topic = props.topics[props.active_topic_index]
        topic = bcfxml.topics[blender_topic.name]
        for index, reference_link in enumerate(topic.reference_links):
            if reference_link == blender_topic.reference_links[index].name:
                continue
            topic.reference_links[index] = blender_topic.reference_links[index].name
        bcfxml.edit_topic(topic)
        return {"FINISHED"}


class EditBcfLabels(bpy.types.Operator):
    bl_idname = "bim.edit_bcf_labels"
    bl_label = "Edit BCF Labels"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        props = context.scene.BCFProperties
        blender_topic = props.topics[props.active_topic_index]
        topic = bcfxml.topics[blender_topic.name]
        for index, label in enumerate(blender_topic.labels):
            if label.name == topic.labels[index]:
                continue
            topic.labels[index] = blender_topic.labels[index].name
        bcfxml.edit_topic(topic)
        return {"FINISHED"}


class RemoveBcfReferenceLink(bpy.types.Operator):
    bl_idname = "bim.remove_bcf_reference_link"
    bl_label = "Remove BCF Reference Link"
    bl_options = {"REGISTER", "UNDO"}
    index: bpy.props.IntProperty()

    def execute(self, context):
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        props = context.scene.BCFProperties
        blender_topic = props.topics[props.active_topic_index]
        topic = bcfxml.topics[blender_topic.name]
        del topic.reference_links[self.index]
        bcfxml.edit_topic(topic)
        blender_topic.reference_links.remove(self.index)
        return {"FINISHED"}


class RemoveBcfLabel(bpy.types.Operator):
    bl_idname = "bim.remove_bcf_label"
    bl_label = "Remove BCF Label"
    bl_options = {"REGISTER", "UNDO"}
    index: bpy.props.IntProperty()

    def execute(self, context):
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        props = context.scene.BCFProperties
        blender_topic = props.topics[props.active_topic_index]
        topic = bcfxml.topics[blender_topic.name]
        del topic.labels[self.index]
        bcfxml.edit_topic(topic)
        blender_topic.labels.remove(self.index)
        return {"FINISHED"}


class RemoveBcfBimSnippet(bpy.types.Operator):
    bl_idname = "bim.remove_bcf_bim_snippet"
    bl_label = "Remove BCF BIM Snippet"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        props = context.scene.BCFProperties
        blender_topic = props.topics[props.active_topic_index]
        topic = bcfxml.topics[blender_topic.name]
        bcfxml.delete_bim_snippet(topic)
        blender_topic.bim_snippet.schema = ""
        blender_topic.bim_snippet.reference = ""
        blender_topic.bim_snippet.type = ""
        return {"FINISHED"}


class RemoveBcfDocumentReference(bpy.types.Operator):
    bl_idname = "bim.remove_bcf_document_reference"
    bl_label = "Remove BCF Document Reference"
    bl_options = {"REGISTER", "UNDO"}
    index: bpy.props.IntProperty()

    def execute(self, context):
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        props = context.scene.BCFProperties
        blender_topic = props.topics[props.active_topic_index]
        topic = bcfxml.topics[blender_topic.name]
        bcfxml.delete_document_reference(topic, self.index)
        bpy.ops.bim.load_bcf_topic(topic_guid = topic.guid, topic_index = props.active_topic_index)
        return {"FINISHED"}


class RemoveBcfRelatedTopic(bpy.types.Operator):
    bl_idname = "bim.remove_bcf_related_topic"
    bl_label = "Remove BCF Related Topic"
    bl_options = {"REGISTER", "UNDO"}
    index: bpy.props.IntProperty()

    def execute(self, context):
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        props = context.scene.BCFProperties
        blender_topic = props.topics[props.active_topic_index]
        topic = bcfxml.topics[blender_topic.name]
        del topic.related_topics[self.index]
        bcfxml.edit_topic(topic)
        bpy.ops.bim.load_bcf_topic(topic_guid = topic.guid, topic_index = props.active_topic_index)
        return {"FINISHED"}


class RemoveBcfComment(bpy.types.Operator):
    bl_idname = "bim.remove_bcf_comment"
    bl_label = "Remove BCF Comment"
    bl_options = {"REGISTER", "UNDO"}
    comment_guid: bpy.props.StringProperty()

    def execute(self, context):
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        props = context.scene.BCFProperties
        blender_topic = props.topics[props.active_topic_index]
        topic = bcfxml.topics[blender_topic.name]
        bcfxml.delete_comment(self.comment_guid, topic)
        bpy.ops.bim.load_bcf_comments(topic_guid = topic.guid)
        return {"FINISHED"}


class EditBcfComment(bpy.types.Operator):
    bl_idname = "bim.edit_bcf_comment"
    bl_label = "Edit BCF Comment"
    bl_options = {"REGISTER", "UNDO"}
    comment_guid: bpy.props.StringProperty()

    def execute(self, context):
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        props = context.scene.BCFProperties
        blender_topic = props.topics[props.active_topic_index]
        blender_comment = blender_topic.comments.get(self.comment_guid)
        topic = bcfxml.topics[blender_topic.name]
        comment = topic.comments[self.comment_guid]
        comment.comment = blender_comment.comment
        bcfxml.edit_comment(comment, topic)
        bpy.ops.bim.load_bcf_comments(topic_guid = topic.guid)
        return {"FINISHED"}


class AddBcfComment(bpy.types.Operator):
    bl_idname = "bim.add_bcf_comment"
    bl_label = "Add BCF Comment"
    bl_options = {"REGISTER", "UNDO"}
    comment_guid: bpy.props.StringProperty()

    def execute(self, context):
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        props = context.scene.BCFProperties
        blender_topic = props.topics[props.active_topic_index]
        topic = bcfxml.topics[blender_topic.name]
        if not blender_topic.comment:
            return {"FINISHED"}
        comment = bcf.v2.data.Comment()
        comment.comment = blender_topic.comment
        if blender_topic.has_related_viewpoint and blender_topic.viewpoints:
            comment.viewpoint = bcf.v2.data.Viewpoint()
            comment.viewpoint.guid = blender_topic.viewpoints
        bcfxml.add_comment(topic, comment)
        bpy.ops.bim.load_bcf_comments(topic_guid = topic.guid)
        return {"FINISHED"}


class ActivateBcfViewpoint(bpy.types.Operator):
    bl_idname = "bim.activate_bcf_viewpoint"
    bl_label = "Activate BCF Viewpoint"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        self.file = IfcStore.get_file()
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        props = context.scene.BCFProperties
        blender_topic = props.topics[props.active_topic_index]
        topic = bcfxml.topics[blender_topic.name]
        if not topic.viewpoints:
            return {"FINISHED"}

        viewpoint_guid = blender_topic.viewpoints
        viewpoint = topic.viewpoints[viewpoint_guid]
        obj = bpy.data.objects.get("Viewpoint")
        if not obj:
            obj = bpy.data.objects.new("Viewpoint", bpy.data.cameras.new("Viewpoint"))
            context.scene.collection.objects.link(obj)
            context.scene.camera = obj

        cam_width = context.scene.render.resolution_x
        cam_height = context.scene.render.resolution_y
        cam_aspect = cam_width / cam_height

        if viewpoint.snapshot:
            obj.data.show_background_images = True
            while len(obj.data.background_images) > 0:
                obj.data.background_images.remove(obj.data.background_images[0])
            background = obj.data.background_images.new()
            background.image = bpy.data.images.load(
                os.path.join(bcfxml.filepath, topic.guid, viewpoint.snapshot)
            )
            src_width = background.image.size[0]
            src_height = background.image.size[1]
            src_aspect = src_width / src_height

            if src_aspect > cam_aspect:
                background.frame_method = "FIT"
            else:
                background.frame_method = "CROP"
            background.display_depth = "FRONT"
        area = next(area for area in context.screen.areas if area.type == "VIEW_3D")
        area.spaces[0].region_3d.view_perspective = "CAMERA"

        if self.file:
            self.set_viewpoint_components(viewpoint)

        gp = bpy.data.grease_pencils.get("BCF")
        if gp:
            bpy.data.grease_pencils.remove(gp)
        if viewpoint.lines:
            self.draw_lines(viewpoint, context)

        self.delete_clipping_planes(context)
        if viewpoint.clipping_planes:
            self.create_clipping_planes(viewpoint)

        self.delete_bitmaps(context)
        if viewpoint.bitmaps:
            self.create_bitmaps(bcfxml, viewpoint, topic)

        self.setup_camera(viewpoint, obj, cam_aspect)
        return {"FINISHED"}

    def setup_camera(self, viewpoint, obj, cam_aspect):
        if viewpoint.orthogonal_camera:
            camera = viewpoint.orthogonal_camera
            obj.data.type = "ORTHO"
            obj.data.ortho_scale = viewpoint.orthogonal_camera.view_to_world_scale
        elif viewpoint.perspective_camera:
            camera = viewpoint.perspective_camera
            obj.data.type = "PERSP"
            if cam_aspect >= 1:
                obj.data.angle = radians(camera.field_of_view)
            else:
                # https://blender.stackexchange.com/questions/23431/how-to-set-camera-horizontal-and-vertical-fov
                obj.data.angle = 2 * atan((0.5 * cam_height) / (0.5 * cam_width / tan(radians(camera.field_of_view) / 2)))

        z_axis = Vector((-camera.camera_direction.x, -camera.camera_direction.y, -camera.camera_direction.z)).normalized()
        y_axis = Vector((camera.camera_up_vector.x, camera.camera_up_vector.y, camera.camera_up_vector.z)).normalized()
        x_axis = y_axis.cross(z_axis).normalized()
        rotation = Matrix((x_axis, y_axis, z_axis))
        rotation.invert()
        matrix = np.matrix((
            [x_axis[0], y_axis[0], z_axis[0], camera.camera_view_point.x],
            [x_axis[1], y_axis[1], z_axis[1], camera.camera_view_point.y],
            [x_axis[2], y_axis[2], z_axis[2], camera.camera_view_point.z],
            [0, 0, 0, 1],
        ))
        props = bpy.context.scene.BIMGeoreferenceProperties
        if props.has_blender_offset:
            unit_scale = ifcopenshell.util.unit.calculate_unit_scale(self.file)
            matrix = ifcopenshell.util.geolocation.global2local(
                matrix,
                float(props.blender_eastings) * unit_scale,
                float(props.blender_northings) * unit_scale,
                float(props.blender_orthogonal_height) * unit_scale,
                float(props.blender_x_axis_abscissa),
                float(props.blender_x_axis_ordinate),
            )
        obj.matrix_world = Matrix(matrix.tolist())

    def set_viewpoint_components(self, viewpoint):
        if not viewpoint.components:
            return

        # Operators with context overrides are used because they are
        # significantly faster than looping through all objects

        exception_global_ids = [v.ifc_guid for v in viewpoint.components.visibility.exceptions]

        if viewpoint.components.visibility.default_visibility:
            old = bpy.context.area.type
            bpy.context.area.type = "VIEW_3D"
            bpy.ops.object.hide_view_clear()
            bpy.context.area.type = old
            for global_id in exception_global_ids:
                obj = IfcStore.get_element(global_id)
                if obj:
                    obj.hide_set(True)
        else:
            objs = []
            for global_id in exception_global_ids:
                obj = IfcStore.get_element(global_id)
                if obj:
                    objs.append(obj)
            if objs:
                old = bpy.context.area.type
                bpy.context.area.type = "VIEW_3D"
                context_override = {}
                context_override["object"] = context_override["active_object"] = objs[0]
                context_override["selected_objects"] = context_override["selected_editable_objects"] = objs
                bpy.ops.object.hide_view_set(context_override, unselected=True)
                bpy.context.area.type = old

        if viewpoint.components.view_setup_hints:
            if not viewpoint.components.view_setup_hints.spaces_visible:
                self.hide_spaces()
            if viewpoint.components.view_setup_hints.openings_visible is not None:
                self.set_openings_visibility(viewpoint.components.view_setup_hints.openings_visible)
        else:
            self.hide_spaces()
            self.set_openings_visibility(False)

        self.set_selection(viewpoint)
        self.set_colours(viewpoint)

    def hide_spaces(self):
        old = bpy.context.area.type
        bpy.context.area.type = "VIEW_3D"
        bpy.ops.object.select_pattern(pattern="IfcSpace/*")
        bpy.ops.object.hide_view_set({})
        bpy.context.area.type = old

    def set_openings_visibility(self, is_visible):
        for collection in self.get_opening_collections():
            collection.hide_viewport = not is_visible

    def set_selection(self, viewpoint):
        selected_global_ids = [s.ifc_guid for s in viewpoint.components.selection]
        bpy.ops.object.select_all(action="DESELECT")
        for global_id in selected_global_ids:
            obj = IfcStore.get_element(global_id)
            if obj:
                obj.select_set(True)

    def set_colours(self, viewpoint):
        global_id_colours = {}
        for coloring in viewpoint.components.coloring:
            for component in coloring.components:
                global_id_colours.setdefault(component.ifc_guid, coloring.color)
        for global_id, color in global_id_colours.items():
            obj = IfcStore.get_element(global_id)
            if obj:
                obj.color = self.hex_to_rgb(color)

    def get_opening_collections(self):
        collections = []
        for collection in bpy.context.view_layer.layer_collection.children:
            opening_collection = collection.children.get("IfcOpeningElements")
            if opening_collection:
                collections.append(opening_collection)
        return collections

    def draw_lines(self, viewpoint, context):
        gp = bpy.data.grease_pencils.new("BCF")
        scene = context.scene
        scene.grease_pencil = gp
        scene.frame_set(1)
        layer = gp.layers.new("BCF Annotation", set_active=True)
        layer.thickness = 3
        layer.color = (1, 0, 0)
        frame = layer.frames.new(1)
        stroke = frame.strokes.new()
        stroke.display_mode = "3DSPACE"
        stroke.points.add(len(viewpoint.lines) * 2)
        coords = []
        for l in viewpoint.lines:
            coords.extend([l.start_point.x, l.start_point.y, l.start_point.z, l.end_point.x, l.end_point.y, l.end_point.z])
        stroke.points.foreach_set("co", coords)

    def create_clipping_planes(self, viewpoint):
        n = 0
        for plane in viewpoint.clipping_planes:
            bpy.ops.bim.add_section_plane()
            if n == 0:
                obj = bpy.data.objects["Section"]
            else:
                obj = bpy.data.objects["Section.{:03d}".format(n)]
            obj.location = (plane.location.x, plane.location.y, plane.location.z)
            obj.rotation_mode = "QUATERNION"
            obj.rotation_quaternion = Vector((plane.direction.x, plane.direction.y, plane.direction.z)).to_track_quat(
                "Z", "Y"
            )
            n += 1

    def delete_clipping_planes(self, context):
        collection = bpy.data.collections.get("Sections")
        if not collection:
            return
        for section in collection.objects:
            context.view_layer.objects.active = section
            bpy.ops.bim.remove_section_plane()

    def delete_bitmaps(self, context):
        collection = bpy.data.collections.get("Bitmaps")
        if not collection:
            collection = bpy.data.collections.new("Bitmaps")
            context.scene.collection.children.link(collection)
        for bitmap in collection.objects:
            bpy.data.objects.remove(bitmap)

    def create_bitmaps(self, bcfxml, viewpoint, topic):
        collection = bpy.data.collections.get("Bitmaps")
        if not collection:
            collection = bpy.data.collections.new("Bitmaps")
        for bitmap in viewpoint.bitmaps:
            obj = bpy.data.objects.new("Bitmap", None)
            obj.empty_display_type = "IMAGE"
            image = bpy.data.images.load(os.path.join(bcfxml.filepath, topic.guid, bitmap.reference))
            src_width = image.size[0]
            src_height = image.size[1]
            if src_height > src_width:
                obj.empty_display_size = bitmap.height
            else:
                obj.empty_display_size = bitmap.height * (src_width / src_height)
            obj.data = image
            y = Vector((bitmap.up.x, bitmap.up.y, bitmap.up.z))
            z = Vector((bitmap.normal.x, bitmap.normal.y, bitmap.normal.z))
            x = y.cross(z)
            obj.matrix_world = Matrix(
                [[x[0], y[0], z[0], 0], [x[1], y[1], z[1], 0], [x[2], y[2], z[2], 0], [0, 0, 0, 1]]
            )
            obj.location = (bitmap.location.x, bitmap.location.y, bitmap.location.z)
            collection.objects.link(obj)

    def hex_to_rgb(self, value):
        value = value.lstrip("#")
        lv = len(value)
        t = tuple(int(value[i : i + lv // 3], 16) for i in range(0, lv, lv // 3))
        return [t[0] / 255.0, t[1] / 255.0, t[2] / 255.0, 1]

class OpenBcfReferenceLink(bpy.types.Operator):
    bl_idname = "bim.open_bcf_reference_link"
    bl_label = "Open BCF Reference Link"
    index: bpy.props.IntProperty()

    def execute(self, context):
        webbrowser.open(context.scene.BCFProperties.topic_links[self.index].name)
        return {"FINISHED"}


class SelectBcfHeaderFile(bpy.types.Operator):
    bl_idname = "bim.select_bcf_header_file"
    bl_label = "Select BCF Header File"
    bl_options = {"REGISTER", "UNDO"}
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        if self.filepath:
            props = context.scene.BCFProperties
            topic = props.topics[props.active_topic_index]
            topic.file_reference = self.filepath
        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}


class SelectBcfBimSnippetReference(bpy.types.Operator):
    bl_idname = "bim.select_bcf_bim_snippet_reference"
    bl_label = "Select BCF BIM Snippet Reference"
    bl_options = {"REGISTER", "UNDO"}
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        if self.filepath:
            props = context.scene.BCFProperties
            topic = props.topics[props.active_topic_index]
            topic.bim_snippet_reference = self.filepath
        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}


class SelectBcfDocumentReference(bpy.types.Operator):
    bl_idname = "bim.select_bcf_document_reference"
    bl_label = "Select BCF Document Reference"
    bl_options = {"REGISTER", "UNDO"}
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        if self.filepath:
            props = context.scene.BCFProperties
            topic = props.topics[props.active_topic_index]
            topic.document_reference = self.filepath
        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}
