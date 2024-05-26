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

import os
import bpy
import bcf
import bcf.bcfxml
import bcf.v2.model
import uuid
import numpy as np
import tempfile
import webbrowser
import ifcopenshell
import ifcopenshell.util.unit
import blenderbim.bim.module.bcf.prop as bcf_prop
from . import bcfstore
from pathlib import Path
from blenderbim.bim.ifc import IfcStore
from math import radians, degrees, atan, tan, cos, sin
from mathutils import Vector, Matrix, Euler, geometry
from xsdata.models.datatype import XmlDateTime


class NewBcfProject(bpy.types.Operator):
    bl_idname = "bim.new_bcf_project"
    bl_label = "New BCF Project"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        bcfxml = bcf.v2.bcfxml.BcfXml.create_new("New Project")
        bcfstore.BcfStore.set(bcfxml, "")
        bpy.ops.bim.load_bcf_project()
        return {"FINISHED"}


class LoadBcfProject(bpy.types.Operator):
    bl_idname = "bim.load_bcf_project"
    bl_label = "Load BCF Project"
    bl_options = {"REGISTER", "UNDO"}
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    filter_glob: bpy.props.StringProperty(default="*.bcf;*.bcfzip", options={"HIDDEN"})

    def execute(self, context):
        if self.filepath:
            bcfstore.BcfStore.set_by_filepath(self.filepath)
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        context.scene.BCFProperties.name = bcfxml.project.name
        bpy.ops.bim.load_bcf_topics()
        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}


class UnloadBcfProject(bpy.types.Operator):
    bl_idname = "bim.unload_bcf_project"
    bl_label = "Unload BCF Project"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        bcfstore.BcfStore.unload_bcfxml()
        return {"FINISHED"}


class LoadBcfTopics(bpy.types.Operator):
    bl_idname = "bim.load_bcf_topics"
    bl_label = "Load BCF Topics"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        context.scene.BCFProperties.topics.clear()
        for index, topic_guid in enumerate(bcfxml.topics.keys()):
            new = context.scene.BCFProperties.topics.add()
            bpy.ops.bim.load_bcf_topic(topic_guid=topic_guid, topic_index=index)
        return {"FINISHED"}


class LoadBcfTopic(bpy.types.Operator):
    bl_idname = "bim.load_bcf_topic"
    bl_label = "Load BCF Topics"
    bl_options = {"REGISTER", "UNDO"}
    topic_guid: bpy.props.StringProperty()
    topic_index: bpy.props.IntProperty()

    def execute(self, context):
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        topic = bcfxml.topics[self.topic_guid]
        bcfxml.get_header(self.topic_guid)
        new = context.scene.BCFProperties.topics[self.topic_index]
        data_map = {
            "name": topic.guid,
            "title": topic.topic.title,
            "type": topic.topic.topic_type,
            "status": topic.topic.topic_status,
            "priority": topic.topic.priority,
            "stage": topic.topic.stage,
            "creation_date": topic.topic.creation_date,
            "creation_author": topic.topic.creation_author,
            "modified_date": topic.topic.modified_date,
            "modified_author": topic.topic.modified_author,
            "assigned_to": topic.topic.assigned_to,
            "due_date": topic.topic.due_date,
            "description": topic.topic.description,
        }
        for key, value in data_map.items():
            if value is not None:
                setattr(new, key, str(value))

        new.reference_links.clear()
        for reference_link in topic.topic.reference_link:
            new_reference_link = new.reference_links.add()
            new_reference_link.name = reference_link

        new.labels.clear()
        for label in topic.topic.labels:
            new_label = new.labels.add()
            new_label.name = label

        if topic.topic.bim_snippet:
            data_map = {
                "type": topic.topic.bim_snippet.snippet_type,
                "is_external": topic.topic.bim_snippet.is_external,
                "reference": topic.topic.bim_snippet.reference,
                "schema": topic.topic.bim_snippet.reference_schema,
            }
            for key, value in data_map.items():
                if value is not None:
                    setattr(new.bim_snippet, key, value)

        new.document_references.clear()
        for doc in topic.topic.document_reference:
            new_document_references = new.document_references.add()
            data_map = {
                "reference": doc.referenced_document,
                "description": doc.description,
                "guid": doc.guid,
                "is_external": doc.is_external,
            }
            for key, value in data_map.items():
                if value is not None:
                    setattr(new_document_references, key, value)

        new.related_topics.clear()
        for related_topic in topic.topic.related_topic:
            new_related_topic = new.related_topics.add()
            new_related_topic.name = related_topic.guid

        bpy.ops.bim.load_bcf_comments(topic_guid=topic.guid)
        return {"FINISHED"}


class LoadBcfComments(bpy.types.Operator):
    bl_idname = "bim.load_bcf_comments"
    bl_label = "Load BCF Comments"
    bl_options = {"REGISTER", "UNDO"}
    topic_guid: bpy.props.StringProperty()

    def execute(self, context):
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        blender_topic = context.scene.BCFProperties.topics.get(self.topic_guid)
        blender_topic.comments.clear()
        for comment in bcfxml.topics[self.topic_guid].comments:
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
        blender_topic = props.active_topic
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        topic = bcfxml.topics[blender_topic.name].topic
        topic.title = blender_topic.title
        return {"FINISHED"}


class EditBcfTopic(bpy.types.Operator):
    bl_idname = "bim.edit_bcf_topic"
    bl_label = "Edit BCF Topic"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = context.scene.BCFProperties
        blender_topic = props.active_topic
        bcfxml = bcfstore.BcfStore.get_bcfxml()

        topic = bcfxml.topics[blender_topic.name].topic
        topic.title = blender_topic.title or None
        topic.priority = blender_topic.priority or None
        topic.due_date = blender_topic.due_date or None
        topic.assigned_to = blender_topic.assigned_to or None
        topic.stage = blender_topic.stage or None
        topic.description = blender_topic.description or None
        topic.topic_status = blender_topic.status or None
        topic.topic_type = blender_topic.type or None

        props.refresh_topic(context)
        return {"FINISHED"}


class SaveBcfProject(bpy.types.Operator):
    bl_idname = "bim.save_bcf_project"
    bl_label = "Save BCF Project"
    bl_options = {"REGISTER", "UNDO"}
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    filter_glob: bpy.props.StringProperty(default="*.bcf;*.bcfzip", options={"HIDDEN"})

    def execute(self, context):
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        bcfxml.save(self.filepath)
        bcfstore.BcfStore.set(bcfxml, self.filepath)
        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}


class AddBcfTopic(bpy.types.Operator):
    bl_idname = "bim.add_bcf_topic"
    bl_label = "Add BCF Topic"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.scene.BCFProperties.author

    def execute(self, context):
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        bcfxml.add_topic("New Topic", "", context.scene.BCFProperties.author)
        bpy.ops.bim.load_bcf_topics()
        return {"FINISHED"}


class AddBcfBimSnippet(bpy.types.Operator):
    bl_idname = "bim.add_bcf_bim_snippet"
    bl_label = "Add BCF BIM Snippet"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return all(
            (
                getattr(context.scene.BCFProperties, attr, False)
                for attr in ("bim_snippet_reference", "bim_snippet_schema", "bim_snippet_type")
            )
        )

    def execute(self, context):
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        props = context.scene.BCFProperties
        blender_topic = props.active_topic
        topic = bcfxml.topics[blender_topic.name]
        is_external = "://" in props.bim_snippet_reference
        bim_snippet = bcf.v2.model.BimSnippet(
            reference=props.bim_snippet_reference if is_external else Path(props.bim_snippet_reference).name,
            reference_schema=props.bim_snippet_schema,
            snippet_type=props.bim_snippet_type,
            is_external=is_external,
        )
        topic.topic.bim_snippet = bim_snippet
        with open(props.bim_snippet_reference, "r") as f:
            topic.bim_snippet = f.read()
        bpy.ops.bim.load_bcf_topic(topic_guid=topic.guid, topic_index=props.active_topic_index)
        return {"FINISHED"}


class AddBcfRelatedTopic(bpy.types.Operator):
    bl_idname = "bim.add_bcf_related_topic"
    bl_label = "Add BCF Related Topic"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        props = context.scene.BCFProperties
        blender_topic = props.active_topic
        if not props.related_topic:
            return False
        if props.related_topic == blender_topic.title:
            # Prevent adding self as related topic
            return False
        related_topic_guid = None
        for topic in bcfxml.topics.values():
            if topic.topic.title == props.related_topic:
                related_topic_guid = topic.guid
                break
        if not related_topic_guid:
            return False
        if str(related_topic_guid) in [t.name for t in blender_topic.related_topics]:
            # Prevent adding the same related topic more than once
            return False
        return True

    def execute(self, context):
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        props = context.scene.BCFProperties
        blender_topic = props.active_topic
        topic = bcfxml.topics[blender_topic.name]
        topic.topic.related_topic.append(
            bcf.v2.model.TopicRelatedTopic(
                guid=next((t for t in bcfxml.topics.values() if t.topic.title == props.related_topic)).guid
            )
        )
        bpy.ops.bim.load_bcf_topic(topic_guid=topic.guid, topic_index=props.active_topic_index)
        props.related_topic = ""
        return {"FINISHED"}


class AddBcfHeaderFile(bpy.types.Operator):
    bl_idname = "bim.add_bcf_header_file"
    bl_label = "Add BCF Header File"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.scene.BCFProperties.file_reference

    def execute(self, context):
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        props = context.scene.BCFProperties
        blender_topic = props.active_topic
        topic = bcfxml.topics[blender_topic.name]

        is_external = "://" in props.file_reference
        filename = Path(props.file_reference).name if os.path.exists(props.file_reference) else None

        if filename:
            with open(props.file_reference, "r") as f:
                topic.reference_files[filename] = f.read()

        header_file = bcf.v2.model.HeaderFile(
            filename=filename,
            date=XmlDateTime.now(),
            reference=props.file_reference if is_external else Path(props.file_reference).name,
            ifc_project=props.file_ifc_project,
            ifc_spatial_structure_element=props.file_ifc_spatial_structure_element,
            is_external=is_external,
        )
        topic.header.file.append(header_file)

        props.refresh_topic(context)
        return {"FINISHED"}


class ViewBcfTopic(bpy.types.Operator):
    bl_idname = "bim.view_bcf_topic"
    bl_label = "Get BCF Topic"
    bl_options = {"REGISTER", "UNDO"}
    topic_guid: bpy.props.StringProperty()

    def execute(self, context):
        for index, topic in enumerate(context.scene.BCFProperties.topics):
            if topic.name.lower() == self.topic_guid.lower():
                context.scene.BCFProperties.active_topic_index = index
                break
        return {"FINISHED"}


class AddBcfViewpoint(bpy.types.Operator):
    bl_idname = "bim.add_bcf_viewpoint"
    bl_label = "Add BCF Viewpoint"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.scene.camera

    def execute(self, context):
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        blender_camera = context.scene.camera
        props = context.scene.BCFProperties
        blender_topic = props.active_topic
        topic = bcfxml.topics[blender_topic.name]

        direction = blender_camera.matrix_world.to_quaternion() @ Vector((0.0, 0.0, -1.0))
        up = blender_camera.matrix_world.to_quaternion() @ Vector((0.0, 1.0, 0.0))

        camera_view_point = bcf.v2.model.Point(
            x=blender_camera.location.x, y=blender_camera.location.y, z=blender_camera.location.z
        )
        camera_direction = bcf.v2.model.Direction(x=direction.x, y=direction.y, z=direction.z)
        camera_up_vector = bcf.v2.model.Direction(x=up.x, y=up.y, z=up.z)
        if blender_camera.data.type == "ORTHO":
            camera = bcf.v2.model.OrthogonalCamera(
                view_to_world_scale=blender_camera.data.ortho_scale,
                camera_view_point=camera_view_point,
                camera_direction=camera_direction,
                camera_up_vector=camera_up_vector,
            )
            visualization_info = bcf.v2.model.VisualizationInfo(orthogonal_camera=camera)
        elif blender_camera.data.type == "PERSP":
            camera = bcf.v2.model.PerspectiveCamera(
                field_of_view=degrees(blender_camera.data.angle),
                camera_view_point=camera_view_point,
                camera_direction=camera_direction,
                camera_up_vector=camera_up_vector,
            )
            visualization_info = bcf.v2.model.VisualizationInfo(guid=str(uuid.uuid4()), perspective_camera=camera)

        # TODO allow the user to enable or disable snapshotting
        snapshot = None

        blender_render = context.scene.render
        old_file_format = blender_render.image_settings.file_format
        blender_render.image_settings.file_format = "PNG"
        old_filepath = blender_render.filepath
        blender_render.filepath = os.path.join(context.scene.BIMProperties.data_dir, "snapshot.png")
        bpy.ops.render.opengl(write_still=True)
        with open(blender_render.filepath, "rb") as f:
            snapshot = f.read()
        # viewpoint.snapshot = blender_render.filepath

        # TODO we should handle selection and visibility state
        vizinfo = bcf.v2.visinfo.VisualizationInfoHandler(visualization_info=visualization_info, snapshot=snapshot)
        topic.viewpoints[vizinfo.guid + ".bcfv"] = vizinfo
        topic.markup.viewpoints.append(
            bcf.v2.model.ViewPoint(viewpoint=vizinfo.guid + ".bcfv", guid=vizinfo.guid, snapshot=vizinfo.guid + ".png")
        )

        blender_render.filepath = old_filepath
        blender_render.image_settings.file_format = old_file_format
        props.refresh_topic(context)
        return {"FINISHED"}


class RemoveBcfViewpoint(bpy.types.Operator):
    bl_idname = "bim.remove_bcf_viewpoint"
    bl_label = "Remove BCF Viewpoint"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return bcf_prop.getBcfViewpoints(None, context)

    def execute(self, context):
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        props = context.scene.BCFProperties
        blender_topic = props.active_topic
        topic = bcfxml.topics[blender_topic.name]
        for key, viewpoint in topic.viewpoints.items():
            if viewpoint.guid == blender_topic.viewpoints:
                break
        del topic.viewpoints[key]
        for i, viewpoint in enumerate(topic.markup.viewpoints):
            if viewpoint.guid == blender_topic.viewpoints:
                break
        del topic.markup.viewpoints[i]
        props.refresh_topic(context)
        return {"FINISHED"}


class RemoveBcfFile(bpy.types.Operator):
    bl_idname = "bim.remove_bcf_file"
    bl_label = "Remove BCF File"
    bl_options = {"REGISTER", "UNDO"}
    index: bpy.props.IntProperty()

    def execute(self, context):
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        props = context.scene.BCFProperties
        blender_topic = props.active_topic
        topic = bcfxml.topics[blender_topic.name]
        del topic.header.file[self.index]
        props.refresh_topic(context)
        return {"FINISHED"}


class RemoveBcfTopic(bpy.types.Operator):
    bl_idname = "bim.remove_bcf_topic"
    bl_label = "Remove BCF Topic"
    bl_options = {"REGISTER", "UNDO"}
    guid: bpy.props.StringProperty()

    @classmethod
    def poll(cls, context):
        return context.scene.BCFProperties.topics

    def execute(self, context):
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        props = context.scene.BCFProperties
        del bcfxml.topics[props.active_topic.name]
        bpy.ops.bim.load_bcf_topics()
        return {"FINISHED"}


class AddBcfReferenceLink(bpy.types.Operator):
    bl_idname = "bim.add_bcf_reference_link"
    bl_label = "Add BCF Reference Link"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.scene.BCFProperties.reference_link

    def execute(self, context):
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        props = context.scene.BCFProperties
        blender_topic = props.active_topic
        topic = bcfxml.topics[blender_topic.name]
        topic.topic.reference_link.append(props.reference_link)
        bpy.ops.bim.load_bcf_topic(topic_guid=topic.guid, topic_index=props.active_topic_index)
        props.reference_link = ""
        return {"FINISHED"}


class AddBcfDocumentReference(bpy.types.Operator):
    bl_idname = "bim.add_bcf_document_reference"
    bl_label = "Add BCF Document Reference"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.scene.BCFProperties.document_reference

    def execute(self, context):
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        props = context.scene.BCFProperties
        blender_topic = props.active_topic
        topic = bcfxml.topics[blender_topic.name]

        is_external = "://" in props.document_reference
        filename = Path(props.document_reference).name if os.path.exists(props.document_reference) else None

        if filename:
            with open(props.document_reference, "rb") as f:
                topic.document_references[filename] = f.read()

        document_reference = bcf.v2.model.TopicDocumentReference(
            referenced_document=props.document_reference if is_external else filename,
            description=props.document_reference_description or None,
            guid=str(uuid.uuid4()),
            is_external=is_external,
        )

        topic.topic.document_reference.append(document_reference)

        bpy.ops.bim.load_bcf_topic(topic_guid=topic.guid, topic_index=props.active_topic_index)
        props.document_reference = ""
        props.document_reference_description = ""
        return {"FINISHED"}


class AddBcfLabel(bpy.types.Operator):
    bl_idname = "bim.add_bcf_label"
    bl_label = "Add BCF Label"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.scene.BCFProperties.label

    def execute(self, context):
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        props = context.scene.BCFProperties
        blender_topic = props.active_topic
        topic = bcfxml.topics[blender_topic.name]
        new = blender_topic.labels.add()
        new.name = props.label
        topic.topic.labels.append(props.label)
        props.label = ""
        return {"FINISHED"}


class EditBcfReferenceLinks(bpy.types.Operator):
    bl_idname = "bim.edit_bcf_reference_links"
    bl_label = "Edit BCF Reference Link"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        props = context.scene.BCFProperties
        blender_topic = props.active_topic
        topic = bcfxml.topics[blender_topic.name]
        for index, reference_link in enumerate(topic.topic.reference_link):
            if reference_link == blender_topic.reference_links[index].name:
                continue
            topic.topic.reference_link[index] = blender_topic.reference_links[index].name
        return {"FINISHED"}


class EditBcfLabels(bpy.types.Operator):
    bl_idname = "bim.edit_bcf_labels"
    bl_label = "Edit BCF Labels"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        props = context.scene.BCFProperties
        blender_topic = props.active_topic
        topic = bcfxml.topics[blender_topic.name]
        for index, label in enumerate(blender_topic.labels):
            if index >= len(topic.topic.labels):
                break
            if label.name == topic.topic.labels[index]:
                continue
            topic.topic.labels[index] = blender_topic.labels[index].name
        return {"FINISHED"}


class RemoveBcfReferenceLink(bpy.types.Operator):
    bl_idname = "bim.remove_bcf_reference_link"
    bl_label = "Remove BCF Reference Link"
    bl_options = {"REGISTER", "UNDO"}
    index: bpy.props.IntProperty()

    def execute(self, context):
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        props = context.scene.BCFProperties
        blender_topic = props.active_topic
        topic = bcfxml.topics[blender_topic.name]
        del topic.topic.reference_link[self.index]
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
        blender_topic = props.active_topic
        topic = bcfxml.topics[blender_topic.name]
        del topic.topic.labels[self.index]
        blender_topic.labels.remove(self.index)
        return {"FINISHED"}


class RemoveBcfBimSnippet(bpy.types.Operator):
    bl_idname = "bim.remove_bcf_bim_snippet"
    bl_label = "Remove BCF BIM Snippet"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        props = context.scene.BCFProperties
        blender_topic = props.active_topic
        topic = bcfxml.topics[blender_topic.name]
        topic.topic.bim_snippet = None
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
        blender_topic = props.active_topic
        topic = bcfxml.topics[blender_topic.name]
        del topic.topic.document_reference[self.index]
        bpy.ops.bim.load_bcf_topic(topic_guid=topic.guid, topic_index=props.active_topic_index)
        return {"FINISHED"}


class RemoveBcfRelatedTopic(bpy.types.Operator):
    bl_idname = "bim.remove_bcf_related_topic"
    bl_label = "Remove BCF Related Topic"
    bl_options = {"REGISTER", "UNDO"}
    index: bpy.props.IntProperty()

    def execute(self, context):
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        props = context.scene.BCFProperties
        blender_topic = props.active_topic
        topic = bcfxml.topics[blender_topic.name]
        del topic.topic.related_topic[self.index]
        bpy.ops.bim.load_bcf_topic(topic_guid=topic.guid, topic_index=props.active_topic_index)
        return {"FINISHED"}


class RemoveBcfComment(bpy.types.Operator):
    bl_idname = "bim.remove_bcf_comment"
    bl_label = "Remove BCF Comment"
    bl_options = {"REGISTER", "UNDO"}
    comment_guid: bpy.props.StringProperty()

    def execute(self, context):
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        props = context.scene.BCFProperties
        blender_topic = props.active_topic
        topic = bcfxml.topics[blender_topic.name]
        for i, comment in enumerate(topic.comments):
            if comment.guid == self.comment_guid:
                break
        del topic.comments[i]
        bpy.ops.bim.load_bcf_comments(topic_guid=topic.guid)
        return {"FINISHED"}


class EditBcfComment(bpy.types.Operator):
    bl_idname = "bim.edit_bcf_comment"
    bl_label = "Edit BCF Comment"
    bl_options = {"REGISTER", "UNDO"}
    comment_guid: bpy.props.StringProperty()

    def execute(self, context):
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        props = context.scene.BCFProperties
        blender_topic = props.active_topic
        blender_comment = blender_topic.comments.get(self.comment_guid)
        topic = bcfxml.topics[blender_topic.name]
        for i, comment in enumerate(topic.comments):
            if comment.guid == self.comment_guid:
                comment.comment = blender_comment.comment
                comment.modified_date = XmlDateTime.now()
                comment.modified_author = context.scene.BCFProperties.author
        bpy.ops.bim.load_bcf_comments(topic_guid=topic.guid)
        return {"FINISHED"}


class AddBcfComment(bpy.types.Operator):
    bl_idname = "bim.add_bcf_comment"
    bl_label = "Add BCF Comment"
    bl_options = {"REGISTER", "UNDO"}
    comment_guid: bpy.props.StringProperty()

    @classmethod
    def poll(cls, context):
        props = context.scene.BCFProperties
        if not props.comment:
            return False
        if props.has_related_viewpoint and not bcf_prop.getBcfViewpoints(None, context):
            return False
        return True

    def execute(self, context):
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        props = context.scene.BCFProperties
        blender_topic = props.active_topic
        topic = bcfxml.topics[blender_topic.name]
        comment = bcf.v2.model.Comment(
            date=XmlDateTime.now(),
            author=context.scene.BCFProperties.author,
            comment=props.comment,
            guid=str(uuid.uuid4()),
        )
        if props.has_related_viewpoint:
            comment.viewpoint = bcf.v2.model.CommentViewpoint(guid=blender_topic.viewpoints)
        topic.comments.append(comment)
        bpy.ops.bim.load_bcf_comments(topic_guid=topic.guid)
        props.comment = ""
        props.has_related_viewpoint = False
        return {"FINISHED"}


class ActivateBcfViewpoint(bpy.types.Operator):
    bl_idname = "bim.activate_bcf_viewpoint"
    bl_label = "Activate BCF Viewpoint"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        props = context.scene.BCFProperties
        blender_topic = props.active_topic
        if blender_topic is None:
            return False
        topic = bcfxml.topics[blender_topic.name]
        return topic.viewpoints

    def execute(self, context):
        self.file = IfcStore.get_file()
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        props = context.scene.BCFProperties
        blender_topic = props.active_topic
        topic = bcfxml.topics[blender_topic.name]

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

        obj.data.background_images.clear()
        if viewpoint.snapshot:
            obj.data.show_background_images = True
            background = obj.data.background_images.new()
            with tempfile.NamedTemporaryFile(delete=False) as f:
                f.write(viewpoint.snapshot)
                background.image = bpy.data.images.load(f.name)
            src_width = background.image.size[0]
            src_height = background.image.size[1]
            src_aspect = src_width / src_height

            if src_aspect > cam_aspect:
                background.frame_method = "FIT"
            else:
                background.frame_method = "CROP"
            background.display_depth = "FRONT"
        else:
            obj.data.show_background_images = False

        area = next(area for area in context.screen.areas if area.type == "VIEW_3D")
        area.spaces[0].region_3d.view_perspective = "CAMERA"

        if self.file:
            self.set_viewpoint_components(viewpoint, context)

        gp = bpy.data.grease_pencils.get("BCF")
        if gp:
            bpy.data.grease_pencils.remove(gp)
        if viewpoint.visualization_info.lines:
            self.draw_lines(viewpoint, context)

        self.delete_clipping_planes(context)
        if viewpoint.visualization_info.clipping_planes:
            self.create_clipping_planes(viewpoint)

        self.delete_bitmaps(context)
        if viewpoint.visualization_info.bitmap:
            self.create_bitmaps(bcfxml, viewpoint, topic)

        self.setup_camera(viewpoint, obj, cam_aspect, context)
        return {"FINISHED"}

    def setup_camera(self, viewpoint, obj, cam_aspect, context):
        if viewpoint.visualization_info.orthogonal_camera:
            camera = viewpoint.visualization_info.orthogonal_camera
            obj.data.type = "ORTHO"
            obj.data.ortho_scale = viewpoint.visualization_info.orthogonal_camera.view_to_world_scale
        elif viewpoint.visualization_info.perspective_camera:
            camera = viewpoint.visualization_info.perspective_camera
            obj.data.type = "PERSP"
            if cam_aspect >= 1:
                obj.data.angle = radians(camera.field_of_view)
            else:
                # https://blender.stackexchange.com/questions/23431/how-to-set-camera-horizontal-and-vertical-fov
                obj.data.angle = 2 * atan(
                    (0.5 * cam_height) / (0.5 * cam_width / tan(radians(camera.field_of_view) / 2))
                )
        else:
            return

        z_axis = Vector(
            (-camera.camera_direction.x, -camera.camera_direction.y, -camera.camera_direction.z)
        ).normalized()
        y_axis = Vector((camera.camera_up_vector.x, camera.camera_up_vector.y, camera.camera_up_vector.z)).normalized()
        x_axis = y_axis.cross(z_axis).normalized()
        rotation = Matrix((x_axis, y_axis, z_axis))
        rotation.invert()
        matrix = np.matrix(
            (
                [x_axis[0], y_axis[0], z_axis[0], camera.camera_view_point.x],
                [x_axis[1], y_axis[1], z_axis[1], camera.camera_view_point.y],
                [x_axis[2], y_axis[2], z_axis[2], camera.camera_view_point.z],
                [0, 0, 0, 1],
            )
        )
        props = context.scene.BIMGeoreferenceProperties
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

    def set_viewpoint_components(self, viewpoint, context):
        if not viewpoint.visualization_info.components:
            return

        # Operators with context overrides are used because they are
        # significantly faster than looping through all objects

        exception_global_ids = {v.ifc_guid for v in viewpoint.visualization_info.components.visibility.exceptions.component or []}

        if viewpoint.visualization_info.components.visibility.default_visibility:
            old = context.area.type
            context.area.type = "VIEW_3D"
            bpy.ops.object.hide_view_clear()
            context.area.type = old
            for global_id in exception_global_ids:
                obj = IfcStore.get_element(global_id)
                if obj and bpy.context.view_layer.objects.get(obj.name):
                    obj.hide_set(True)
        else:
            objs = []
            for global_id in exception_global_ids:
                obj = IfcStore.get_element(global_id)
                if obj:
                    objs.append(obj)
            if objs:
                old = context.area.type
                context.area.type = "VIEW_3D"
                bpy.ops.object.hide_view_clear()
                context_override = {}
                context_override["object"] = context_override["active_object"] = objs[0]
                context_override["selected_objects"] = context_override["selected_editable_objects"] = objs
                with context.temp_override(**context_override):
                    bpy.ops.object.hide_view_set(unselected=True)
                    bpy.data.objects["Viewpoint"].hide_set(False)
                context.area.type = old

        if viewpoint.visualization_info.components.view_setup_hints:
            if not viewpoint.visualization_info.components.view_setup_hints.spaces_visible:
                self.hide_spaces(context)
            if viewpoint.visualization_info.components.view_setup_hints.openings_visible is not None:
                self.set_openings_visibility(
                    viewpoint.visualization_info.components.view_setup_hints.openings_visible, context
                )
        else:
            self.hide_spaces(context)
            self.set_openings_visibility(False, context)

        # set selection at the end not to conflict with .hide_spaces
        self.set_selection(viewpoint)
        self.set_colours(viewpoint)

    def hide_spaces(self, context):
        old = context.area.type
        context.area.type = "VIEW_3D"
        bpy.ops.object.select_all(action="DESELECT")
        bpy.ops.object.select_pattern(pattern="IfcSpace/*")
        bpy.ops.object.hide_view_set()
        context.area.type = old

    def set_openings_visibility(self, is_visible, context):
        pass # We no longer have an openings collection

    def set_selection(self, viewpoint):
        if not viewpoint.visualization_info.components or not viewpoint.visualization_info.components.selection:
            return
        selected_global_ids = [s.ifc_guid for s in viewpoint.visualization_info.components.selection.component or []]
        bpy.ops.object.select_all(action="DESELECT")
        for global_id in selected_global_ids:
            obj = IfcStore.get_element(global_id)
            if obj:
                obj.select_set(True)
                obj.hide_set(False)

    def set_colours(self, viewpoint):
        global_id_colours = {}
        for coloring in viewpoint.visualization_info.components.coloring or []:
            for component in coloring.components:
                global_id_colours.setdefault(component.ifc_guid, coloring.color)
        for global_id, color in global_id_colours.items():
            obj = IfcStore.get_element(global_id)
            if obj:
                obj.color = self.hex_to_rgb(color)

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
        stroke.points.add(len(viewpoint.visualization_info.lines.line) * 2)
        coords = []
        for l in viewpoint.visualization_info.lines.line:
            coords.extend(
                [l.start_point.x, l.start_point.y, l.start_point.z, l.end_point.x, l.end_point.y, l.end_point.z]
            )
        stroke.points.foreach_set("co", coords)

    def create_clipping_planes(self, viewpoint):
        n = 0
        for plane in viewpoint.visualization_info.clipping_planes.clipping_plane:
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
        for bitmap in viewpoint.visualization_info.bitmap:
            obj = bpy.data.objects.new("Bitmap", None)
            obj.empty_display_type = "IMAGE"
            # image = bpy.data.images.load(os.path.join(bcfxml.filepath, topic.guid, bitmap.reference))
            with tempfile.NamedTemporaryFile(delete=False) as f:
                topic.extract_file(bitmap, f.name)
                # f.write(bitmap.what)
                image = bpy.data.images.load(f.name)
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
    filter_glob: bpy.props.StringProperty(default="*.ifc;*.ifczip;*.ifcxml;*.ifcjson", options={"HIDDEN"})

    def execute(self, context):
        if self.filepath:
            context.scene.BCFProperties.file_reference = self.filepath
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
            context.scene.BCFProperties.bim_snippet_reference = self.filepath
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
            context.scene.BCFProperties.document_reference = self.filepath
        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}


class ExtractBcfFile(bpy.types.Operator):
    bl_idname = "bim.extract_bcf_file"
    bl_label = "Extract BCF Header File"
    bl_options = {"REGISTER", "UNDO"}
    entity_type: bpy.props.StringProperty()
    index: bpy.props.IntProperty()

    def execute(self, context):
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        topic = bcfxml.topics[context.scene.BCFProperties.active_topic.name]

        if self.entity_type == "HEADER_FILE":
            entity = topic.header.file[self.index]
        elif self.entity_type == "BIM_SNIPPET":
            entity = topic.markup.topic.bim_snippet
        elif self.entity_type == "DOCUMENT_REFERENCE":
            entity = topic.markup.topic.document_reference[self.index]

        webbrowser.open(str(topic.extract_file(entity).parent))
        return {"FINISHED"}
