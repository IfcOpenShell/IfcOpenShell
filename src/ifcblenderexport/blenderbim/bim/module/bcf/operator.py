import os
import bpy
import bcf
from . import bcfstore
from blenderbim.bim.ifc import IfcStore
from math import radians, degrees, atan, tan, cos, sin
from mathutils import Vector, Matrix, Euler, geometry

class NewBcfProject(bpy.types.Operator):
    bl_idname = "bim.new_bcf_project"
    bl_label = "New BCF Project"

    def execute(self, context):
        bpy.context.scene.BCFProperties.is_loaded = False
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        bcfxml.new_project()
        bpy.ops.bim.load_bcf_project()
        bpy.context.scene.BCFProperties.is_loaded = True
        return {"FINISHED"}


class LoadBcfProject(bpy.types.Operator):
    bl_idname = "bim.load_bcf_project"
    bl_label = "Load BCF Project"
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        bpy.context.scene.BCFProperties.is_loaded = False
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        if self.filepath:
            bcfxml.get_project(self.filepath)
        bpy.context.scene.BCFProperties.name = bcfxml.project.name
        bpy.ops.bim.load_bcf_topics()
        bpy.context.scene.BCFProperties.is_loaded = True
        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}


class LoadBcfTopics(bpy.types.Operator):
    bl_idname = "bim.load_bcf_topics"
    bl_label = "Load BCF Topics"

    def execute(self, context):
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        bcfxml.get_topics()
        while len(bpy.context.scene.BCFProperties.topics) > 0:
            bpy.context.scene.BCFProperties.topics.remove(0)
        index = 0
        for topic_guid in bcfxml.topics.keys():
            new = bpy.context.scene.BCFProperties.topics.add()
            bpy.ops.bim.load_bcf_topic(topic_guid = topic_guid, topic_index = index)
            index += 1
        return {"FINISHED"}


class LoadBcfTopic(bpy.types.Operator):
    bl_idname = "bim.load_bcf_topic"
    bl_label = "Load BCF Topics"
    topic_guid: bpy.props.StringProperty()
    topic_index: bpy.props.IntProperty()

    def execute(self, context):
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        topic = bcfxml.get_topic(self.topic_guid)
        new = bpy.context.scene.BCFProperties.topics[self.topic_index]
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
    topic_guid: bpy.props.StringProperty()

    def execute(self, context):
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        bcfxml.get_comments(self.topic_guid)
        blender_topic = bpy.context.scene.BCFProperties.topics.get(self.topic_guid)
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

    def execute(self, context):
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        bcfxml.project.name = bpy.context.scene.BCFProperties.name
        bcfxml.edit_project()
        return {"FINISHED"}


class EditBcfAuthor(bpy.types.Operator):
    bl_idname = "bim.edit_bcf_author"
    bl_label = "Edit BCF Author"

    def execute(self, context):
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        bcfxml.author = bpy.context.scene.BCFProperties.author
        return {"FINISHED"}


class EditBcfTopicName(bpy.types.Operator):
    bl_idname = "bim.edit_bcf_topic_name"
    bl_label = "Edit BCF Topic Name"

    def execute(self, context):
        props = bpy.context.scene.BCFProperties
        blender_topic = props.topics[props.active_topic_index]
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        topic = bcfxml.topics[blender_topic.name]
        topic.title = blender_topic.title
        bcfxml.edit_topic(topic)
        return {"FINISHED"}


class EditBcfTopic(bpy.types.Operator):
    bl_idname = "bim.edit_bcf_topic"
    bl_label = "Edit BCF Topic"

    def execute(self, context):
        props = bpy.context.scene.BCFProperties
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

    def execute(self, context):
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        bcfxml.add_topic()
        new = bpy.context.scene.BCFProperties.topics.add()
        new.name = "New Topic"
        bpy.ops.bim.load_bcf_topics()
        return {"FINISHED"}


class AddBcfBimSnippet(bpy.types.Operator):
    bl_idname = "bim.add_bcf_bim_snippet"
    bl_label = "Add BCF BIM Snippet"

    def execute(self, context):
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        props = bpy.context.scene.BCFProperties
        blender_topic = props.topics[props.active_topic_index]
        topic = bcfxml.topics[blender_topic.name]
        bim_snippet = bcf.data.BimSnippet()
        bim_snippet.reference = blender_topic.bim_snippet_reference
        bim_snippet.reference_schema = blender_topic.bim_snippet_schema
        bim_snippet.snippet_type = blender_topic.bim_snippet_type
        bcfxml.add_bim_snippet(topic, bim_snippet)
        bpy.ops.bim.load_bcf_topic(topic_guid = topic.guid, topic_index = props.active_topic_index)
        return {"FINISHED"}


class AddBcfRelatedTopic(bpy.types.Operator):
    bl_idname = "bim.add_bcf_related_topic"
    bl_label = "Add BCF Related Topic"

    def execute(self, context):
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        props = bpy.context.scene.BCFProperties
        blender_topic = props.topics[props.active_topic_index]
        related_topic = None
        for topic in bcfxml.topics.values():
            if topic.title == blender_topic.related_topic:
                related_topic = bcf.data.RelatedTopic()
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

    def execute(self, context):
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        props = bpy.context.scene.BCFProperties
        blender_topic = props.topics[props.active_topic_index]
        topic = bcfxml.topics[blender_topic.name]
        header_file = bcf.data.HeaderFile()
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
    topic_guid: bpy.props.StringProperty()

    def execute(self, context):
        for index, topic in enumerate(bpy.context.scene.BCFProperties.topics):
            if topic.guid.lower() == self.topic_guid.lower():
                bpy.context.scene.BCFProperties.active_topic_index = index
        return {"FINISHED"}


class AddBcfViewpoint(bpy.types.Operator):
    bl_idname = "bim.add_bcf_viewpoint"
    bl_label = "Add BCF Viewpoint"

    def execute(self, context):
        if not bpy.context.scene.camera:
            return {"FINISHED"}
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        props = bpy.context.scene.BCFProperties
        blender_topic = props.topics[props.active_topic_index]
        topic = bcfxml.topics[blender_topic.name]
        viewpoint = bcf.data.Viewpoint()

        if bpy.context.scene.camera.data.type == "ORTHO":
            camera = bcf.data.OrthogonalCamera()
            camera.view_to_world_scale = bpy.context.scene.camera.data.ortho_scale
            viewpoint.orthogonal_camera = camera
        elif bpy.context.scene.camera.data.type == "PERSP":
            camera = bcf.data.PerspectiveCamera()
            camera.field_of_view = degrees(bpy.context.scene.camera.data.angle)
            viewpoint.perspective_camera = camera
        camera.camera_view_point.x = bpy.context.scene.camera.location.x
        camera.camera_view_point.y = bpy.context.scene.camera.location.y
        camera.camera_view_point.z = bpy.context.scene.camera.location.z
        direction = bpy.context.scene.camera.matrix_world.to_quaternion() @ Vector((0.0, 0.0, -1.0))
        camera.camera_direction.x = direction.x
        camera.camera_direction.y = direction.y
        camera.camera_direction.z = direction.z
        up = bpy.context.scene.camera.matrix_world.to_quaternion() @ Vector((0.0, 1.0, 0.0))
        camera.camera_up_vector.x = up.x
        camera.camera_up_vector.y = up.y
        camera.camera_up_vector.z = up.z

        old_file_format = bpy.context.scene.render.image_settings.file_format
        bpy.context.scene.render.image_settings.file_format = "PNG"
        old_filepath = bpy.context.scene.render.filepath
        bpy.context.scene.render.filepath = os.path.join(bpy.context.scene.BIMProperties.data_dir, "snapshot.png")
        bpy.ops.render.opengl(write_still=True)
        viewpoint.snapshot = bpy.context.scene.render.filepath

        bcfxml.add_viewpoint(topic, viewpoint)
        bpy.context.scene.render.filepath = old_filepath
        bpy.context.scene.render.image_settings.file_format = old_file_format
        props.active_topic_index = props.active_topic_index # refreshes the BCF Topic
        return {"FINISHED"}


class RemoveBcfViewpoint(bpy.types.Operator):
    bl_idname = "bim.remove_bcf_viewpoint"
    bl_label = "Remove BCF Viewpoint"

    def execute(self, context):
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        props = bpy.context.scene.BCFProperties
        blender_topic = props.topics[props.active_topic_index]
        viewpoint_guid = blender_topic.viewpoints
        topic = bcfxml.topics[blender_topic.name]
        bcfxml.delete_viewpoint(viewpoint_guid, topic)
        props.active_topic_index = props.active_topic_index # Refreshes the BCF Topic
        return {"FINISHED"}


class RemoveBcfFile(bpy.types.Operator):
    bl_idname = "bim.remove_bcf_file"
    bl_label = "Remove BCF File"
    index: bpy.props.IntProperty()

    def execute(self, context):
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        props = bpy.context.scene.BCFProperties
        blender_topic = props.topics[props.active_topic_index]
        topic = bcfxml.topics[blender_topic.name]
        bcfxml.delete_file(topic, self.index)
        props.active_topic_index = props.active_topic_index # Refreshes the BCF Topic
        return {"FINISHED"}


class AddBcfReferenceLink(bpy.types.Operator):
    bl_idname = "bim.add_bcf_reference_link"
    bl_label = "Add BCF Reference Link"

    def execute(self, context):
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        props = bpy.context.scene.BCFProperties
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

    def execute(self, context):
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        props = bpy.context.scene.BCFProperties
        blender_topic = props.topics[props.active_topic_index]
        topic = bcfxml.topics[blender_topic.name]
        if not blender_topic.document_reference:
            return {"FINISHED"}
        document_reference = bcf.data.DocumentReference()
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

    def execute(self, context):
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        props = bpy.context.scene.BCFProperties
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

    def execute(self, context):
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        props = bpy.context.scene.BCFProperties
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

    def execute(self, context):
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        props = bpy.context.scene.BCFProperties
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
    index: bpy.props.IntProperty()

    def execute(self, context):
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        props = bpy.context.scene.BCFProperties
        blender_topic = props.topics[props.active_topic_index]
        topic = bcfxml.topics[blender_topic.name]
        del topic.reference_links[self.index]
        bcfxml.edit_topic(topic)
        blender_topic.reference_links.remove(self.index)
        return {"FINISHED"}


class RemoveBcfLabel(bpy.types.Operator):
    bl_idname = "bim.remove_bcf_label"
    bl_label = "Remove BCF Label"
    index: bpy.props.IntProperty()

    def execute(self, context):
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        props = bpy.context.scene.BCFProperties
        blender_topic = props.topics[props.active_topic_index]
        topic = bcfxml.topics[blender_topic.name]
        del topic.labels[self.index]
        bcfxml.edit_topic(topic)
        blender_topic.labels.remove(self.index)
        return {"FINISHED"}


class RemoveBcfBimSnippet(bpy.types.Operator):
    bl_idname = "bim.remove_bcf_bim_snippet"
    bl_label = "Remove BCF BIM Snippet"

    def execute(self, context):
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        props = bpy.context.scene.BCFProperties
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
    index: bpy.props.IntProperty()

    def execute(self, context):
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        props = bpy.context.scene.BCFProperties
        blender_topic = props.topics[props.active_topic_index]
        topic = bcfxml.topics[blender_topic.name]
        bcfxml.delete_document_reference(topic, self.index)
        bpy.ops.bim.load_bcf_topic(topic_guid = topic.guid, topic_index = props.active_topic_index)
        return {"FINISHED"}


class RemoveBcfRelatedTopic(bpy.types.Operator):
    bl_idname = "bim.remove_bcf_related_topic"
    bl_label = "Remove BCF Related Topic"
    index: bpy.props.IntProperty()

    def execute(self, context):
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        props = bpy.context.scene.BCFProperties
        blender_topic = props.topics[props.active_topic_index]
        topic = bcfxml.topics[blender_topic.name]
        del topic.related_topics[self.index]
        bcfxml.edit_topic(topic)
        bpy.ops.bim.load_bcf_topic(topic_guid = topic.guid, topic_index = props.active_topic_index)
        return {"FINISHED"}


class RemoveBcfComment(bpy.types.Operator):
    bl_idname = "bim.remove_bcf_comment"
    bl_label = "Remove BCF Comment"
    comment_guid: bpy.props.StringProperty()

    def execute(self, context):
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        props = bpy.context.scene.BCFProperties
        blender_topic = props.topics[props.active_topic_index]
        topic = bcfxml.topics[blender_topic.name]
        bcfxml.delete_comment(self.comment_guid, topic)
        bpy.ops.bim.load_bcf_comments(topic_guid = topic.guid)
        return {"FINISHED"}


class EditBcfComment(bpy.types.Operator):
    bl_idname = "bim.edit_bcf_comment"
    bl_label = "Edit BCF Comment"
    comment_guid: bpy.props.StringProperty()

    def execute(self, context):
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        props = bpy.context.scene.BCFProperties
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
    comment_guid: bpy.props.StringProperty()

    def execute(self, context):
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        props = bpy.context.scene.BCFProperties
        blender_topic = props.topics[props.active_topic_index]
        topic = bcfxml.topics[blender_topic.name]
        if not blender_topic.comment:
            return {"FINISHED"}
        comment = bcf.data.Comment()
        comment.comment = blender_topic.comment
        if blender_topic.has_related_viewpoint and blender_topic.viewpoints:
            comment.viewpoint = bcf.data.Viewpoint()
            comment.viewpoint.guid = blender_topic.viewpoints
        bcfxml.add_comment(topic, comment)
        bpy.ops.bim.load_bcf_comments(topic_guid = topic.guid)
        print(bcfxml.filepath)
        return {"FINISHED"}


class ActivateBcfViewpoint(bpy.types.Operator):
    bl_idname = "bim.activate_bcf_viewpoint"
    bl_label = "Activate BCF Viewpoint"

    def execute(self, context):
        self.file = IfcStore.get_file()
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        props = bpy.context.scene.BCFProperties
        blender_topic = props.topics[props.active_topic_index]
        topic = bcfxml.topics[blender_topic.name]
        if not topic.viewpoints:
            return {"FINISHED"}

        viewpoint_guid = blender_topic.viewpoints
        viewpoint = topic.viewpoints[viewpoint_guid]
        obj = bpy.data.objects.get("Viewpoint")
        if not obj:
            obj = bpy.data.objects.new("Viewpoint", bpy.data.cameras.new("Viewpoint"))
            bpy.context.scene.collection.objects.link(obj)
            bpy.context.scene.camera = obj

        cam_width = bpy.context.scene.render.resolution_x
        cam_height = bpy.context.scene.render.resolution_y
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
        area = next(area for area in bpy.context.screen.areas if area.type == "VIEW_3D")
        area.spaces[0].region_3d.view_perspective = "CAMERA"

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

        self.set_viewpoint_components(viewpoint)

        gp = bpy.data.grease_pencils.get("BCF")
        if gp:
            bpy.data.grease_pencils.remove(gp)
        if viewpoint.lines:
            self.draw_lines(viewpoint)

        self.delete_clipping_planes()
        if viewpoint.clipping_planes:
            self.create_clipping_planes(viewpoint)

        self.delete_bitmaps()
        if viewpoint.bitmaps:
            self.create_bitmaps(bcfxml, viewpoint, topic)

        z_axis = Vector((-camera.camera_direction.x, -camera.camera_direction.y, -camera.camera_direction.z)).normalized()
        y_axis = Vector((camera.camera_up_vector.x, camera.camera_up_vector.y, camera.camera_up_vector.z)).normalized()
        x_axis = y_axis.cross(z_axis).normalized()
        rotation = Matrix((x_axis, y_axis, z_axis))
        rotation.invert()
        location = Vector((camera.camera_view_point.x, camera.camera_view_point.y, camera.camera_view_point.z))
        obj.matrix_world = rotation.to_4x4()
        obj.location = location
        return {"FINISHED"}

    def set_viewpoint_components(self, viewpoint):
        if not viewpoint.components:
            return
        selected_global_ids = [s.ifc_guid for s in viewpoint.components.selection]
        exception_global_ids = [v.ifc_guid for v in viewpoint.components.visibility.exceptions]
        global_id_colours = {}
        for coloring in viewpoint.components.coloring:
            for component in coloring.components:
                global_id_colours.setdefault(component.ifc_guid, coloring.color)

        for obj in bpy.data.objects:
            if not obj.BIMObjectProperties.ifc_definition_id:
                continue
            global_id = self.file.by_id(obj.BIMObjectProperties.ifc_definition_id).GlobalId
            is_visible = viewpoint.components.visibility.default_visibility
            if global_id in exception_global_ids:
                is_visible = not is_visible
            if not is_visible:
                obj.hide_set(True)
                continue
            if "IfcSpace" in obj.name:
                if viewpoint.components.view_setup_hints:
                    is_visible = viewpoint.components.view_setup_hints.spaces_visible
                else:
                    is_visible = False
            elif "IfcOpeningElement" in obj.name:
                if viewpoint.components.view_setup_hints:
                    is_visible = viewpoint.components.view_setup_hints.openings_visible
                else:
                    is_visible = False
            obj.hide_set(not is_visible)
            if not is_visible:
                continue
            obj.select_set(global_id in selected_global_ids)
            if global_id in global_id_colours:
                obj.color = self.hex_to_rgb(global_id_colours[global_id])

    def draw_lines(self, viewpoint):
        gp = bpy.data.grease_pencils.new("BCF")
        scene = bpy.context.scene
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

    def delete_clipping_planes(self):
        collection = bpy.data.collections.get("Sections")
        if not collection:
            return
        for section in collection.objects:
            bpy.context.view_layer.objects.active = section
            bpy.ops.bim.remove_section_plane()

    def delete_bitmaps(self):
        collection = bpy.data.collections.get("Bitmaps")
        if not collection:
            collection = bpy.data.collections.new("Bitmaps")
            bpy.context.scene.collection.children.link(collection)
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
        webbrowser.open(bpy.context.scene.BCFProperties.topic_links[self.index].name)
        return {"FINISHED"}


class SelectBcfHeaderFile(bpy.types.Operator):
    bl_idname = "bim.select_bcf_header_file"
    bl_label = "Select BCF Header File"
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        if self.filepath:
            props = bpy.context.scene.BCFProperties
            topic = props.topics[props.active_topic_index]
            topic.file_reference = self.filepath
        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}


class SelectBcfBimSnippetReference(bpy.types.Operator):
    bl_idname = "bim.select_bcf_bim_snippet_reference"
    bl_label = "Select BCF BIM Snippet Reference"
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        if self.filepath:
            props = bpy.context.scene.BCFProperties
            topic = props.topics[props.active_topic_index]
            topic.bim_snippet_reference = self.filepath
        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}


class SelectBcfDocumentReference(bpy.types.Operator):
    bl_idname = "bim.select_bcf_document_reference"
    bl_label = "Select BCF Document Reference"
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        if self.filepath:
            props = bpy.context.scene.BCFProperties
            topic = props.topics[props.active_topic_index]
            topic.document_reference = self.filepath
        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}
