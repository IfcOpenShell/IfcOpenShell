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
import bcf.v3
import bcf.v3.bcfxml
import bcf.v3.document
import bcf.v3.model
import bcf.v3.topic
import bcf.v3.visinfo
import bpy
import bcf
import bcf.bcfxml
import bcf.v2.bcfxml
import bcf.v2.model
import bcf.v2.topic
import bcf.v2.visinfo
import bcf.agnostic.topic
import bcf.agnostic.visinfo
import uuid
import numpy as np
import tempfile
import webbrowser
import ifcopenshell
import ifcopenshell.util.geolocation
import ifcopenshell.util.unit
import bonsai.tool as tool
import bonsai.bim.module.bcf.prop as bcf_prop
import bonsai.bim.module.bcf.bcfstore as bcfstore
from pathlib import Path
from bonsai.bim.ifc import IfcStore
from math import radians, degrees, atan, tan, cos, sin
from mathutils import Vector, Matrix, Euler, geometry
from xsdata.models.datatype import XmlDateTime


class NewBcfProject(bpy.types.Operator):
    bl_idname = "bim.new_bcf_project"
    bl_label = "New BCF Project"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = context.scene.BCFProperties
        bcf_v2 = props.bcf_version == "2"
        bcf_class = bcf.v2.bcfxml.BcfXml if bcf_v2 else bcf.v3.bcfxml.BcfXml
        bcfxml = bcf_class.create_new("New Project")
        bcfstore.BcfStore.set(bcfxml, "")
        bpy.ops.bim.load_bcf_project()
        return {"FINISHED"}


class LoadBcfProject(bpy.types.Operator):
    bl_idname = "bim.load_bcf_project"
    bl_label = "Load BCF Project"
    bl_options = {"REGISTER", "UNDO"}
    filepath: bpy.props.StringProperty(subtype="FILE_PATH", options={"SKIP_SAVE"})
    filter_glob: bpy.props.StringProperty(default="*.bcf;*.bcfzip", options={"HIDDEN"})

    def execute(self, context):
        # Operator is also used when new project is created by not yet saved.
        if self.filepath:
            bcfstore.BcfStore.set_by_filepath(self.filepath)

        bcfxml = bcfstore.BcfStore.get_bcfxml()
        assert bcfxml
        bcf_v2 = (bcfxml.version.version_id or "").startswith("2")

        # BCF v2.1/v3 does not need to have a project, but BBIM likes to have one
        # https://github.com/buildingSMART/BCF-XML/tree/release_2_1/Documentation#bcf-file-structure
        nameless = "Unknown"
        if bcfxml.project is None:
            print("No project, we will create one for BBIM.")
            project_info = bcfxml.project_info
            if bcf_v2:
                assert isinstance(bcfxml, bcf.v2.bcfxml.BcfXml)
                if project_info is None:
                    project_info = bcf.v2.model.ProjectExtension(extension_schema="")
                    bcfxml.project_info = project_info
                if project_info.project is None:
                    project_info.project = bcf.v2.model.Project(name=nameless, project_id=str(uuid.uuid4()))
            else:
                assert isinstance(bcfxml, bcf.v3.bcfxml.BcfXml)
                project_info = bcf.v3.model.ProjectInfo(
                    project=bcf.v3.model.Project(name=nameless, project_id=str(uuid.uuid4()))
                )
                bcfxml.project_info = project_info

        assert bcfxml.project
        if bcfxml.project.name is None:
            bcfxml.project.name = nameless
        context.scene.BCFProperties.name = bcfxml.project.name
        bpy.ops.bim.load_bcf_topics()
        self.report({"INFO"}, f"BCF Project '{Path(self.filepath).name}' is loaded.")
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
        assert bcfxml
        props = context.scene.BCFProperties
        props.topics.clear()
        # workaround, one non standard topic would break reading entire bcf
        # ignored these topics ATM
        # happens on non standard nodes or on missing nodes in markup
        topics2use = []
        for topic_guid in bcfxml.topics.keys():
            try:
                topics2use.append(topic_guid)
            except:
                print("Problems on reading topic, thus ignored: {}".format(topic_guid))
                continue
        for index, topic_guid in enumerate(topics2use):
            new = props.topics.add()
            bpy.ops.bim.load_bcf_topic(topic_guid=topic_guid, topic_index=index)

        props.refresh_topic(context)
        return {"FINISHED"}


class LoadBcfTopic(bpy.types.Operator):
    bl_idname = "bim.load_bcf_topic"
    bl_label = "Load BCF Topics"
    bl_options = {"REGISTER", "UNDO"}
    topic_guid: bpy.props.StringProperty()
    topic_index: bpy.props.IntProperty()

    def execute(self, context):
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        assert bcfxml
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
        for reference_link in tool.Bcf.get_topic_reference_links(topic):
            new_reference_link = new.reference_links.add()
            new_reference_link.name = reference_link

        new.labels.clear()
        for label in tool.Bcf.get_topic_labels(topic):
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
        for doc in tool.Bcf.get_topic_document_references(topic):
            new_document_references = new.document_references.add()

            if isinstance(doc, bcf.v2.model.TopicDocumentReference):
                reference = doc.referenced_document
                is_external = doc.is_external
            else:
                is_external = doc.document_guid is None
                reference = doc.url if is_external else doc.document_guid

            data_map = {
                "reference": reference,
                "description": doc.description,
                "guid": doc.guid,
                "is_external": is_external,
            }
            for key, value in data_map.items():
                if value is not None:
                    setattr(new_document_references, key, value)

        new.related_topics.clear()
        for related_topic in tool.Bcf.get_topic_related_topics(topic):
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
        assert bcfxml

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
        assert bcfxml

        # Bonsai creates default project on load.
        assert bcfxml.project
        bcfxml.project.name = context.scene.BCFProperties.name
        return {"FINISHED"}


class EditBcfTopicName(bpy.types.Operator):
    bl_idname = "bim.edit_bcf_topic_name"
    bl_label = "Edit BCF Topic Name"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = context.scene.BCFProperties
        blender_topic = props.active_topic
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        assert bcfxml

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
        assert bcfxml
        bcf_v2 = (bcfxml.version.version_id or "").startswith("2")

        topic = bcfxml.topics[blender_topic.name].topic
        topic.title = blender_topic.title or ""
        topic.priority = blender_topic.priority or None
        topic.due_date = blender_topic.due_date or None
        topic.assigned_to = blender_topic.assigned_to or None
        topic.stage = blender_topic.stage or None
        topic.description = blender_topic.description or None

        if bcf_v2:
            assert isinstance(topic, bcf.v2.model.Topic)
            topic.topic_status = blender_topic.status or None
            topic.topic_type = blender_topic.type or None
        else:
            error_msg = None
            if not blender_topic.status:
                error_msg = "Topic Status field is not optional."
            if not blender_topic.type:
                error_msg = "Topic Type field is not optional."
            if error_msg:
                # Use show_info_message as this operator is not called directly
                # but from prop callback and user won't see a popup from self.report.
                tool.Blender.show_info_message(error_msg, "ERROR")
                self.report({"INFO"}, error_msg)
                return {"CANCELLED"}
            topic.topic_status = blender_topic.status
            topic.topic_type = blender_topic.type

        props.refresh_topic(context)
        return {"FINISHED"}


class SaveBcfProject(bpy.types.Operator):
    bl_idname = "bim.save_bcf_project"
    bl_label = "Save BCF Project"
    bl_options = {"REGISTER", "UNDO"}
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    filter_glob: bpy.props.StringProperty(default="*.bcf;*.bcfzip", options={"HIDDEN"})
    save_current_bcf: bpy.props.BoolProperty(default=False, options={"SKIP_SAVE"})

    def execute(self, context):
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        assert bcfxml
        bcfxml.save(self.filepath)
        bcfstore.BcfStore.set(bcfxml, self.filepath)
        self.report({"INFO"}, f"BCF Project '{Path(self.filepath).name}' is saved.")
        return {"FINISHED"}

    def invoke(self, context, event):
        if self.save_current_bcf:
            path = tool.Bcf.get_path()
            if path:
                self.filepath = str(path)
                return self.execute(context)

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
        assert bcfxml

        bcfxml.add_topic("New Topic", "", context.scene.BCFProperties.author)
        bpy.ops.bim.load_bcf_topics()
        return {"FINISHED"}


class AddBcfBimSnippet(bpy.types.Operator):
    bl_idname = "bim.add_bcf_bim_snippet"
    bl_label = "Add BCF BIM Snippet"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        props = context.scene.BCFProperties
        props_are_filled = all(
            (getattr(props, attr) for attr in ("bim_snippet_reference", "bim_snippet_schema", "bim_snippet_type"))
        )
        if not props_are_filled:
            cls.poll_message_set("Some BIM snippet fields are empty.")
            return False
        return True

    def execute(self, context):
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        assert bcfxml
        bcf_v2 = (bcfxml.version.version_id or "").startswith("2")

        props = context.scene.BCFProperties
        blender_topic = props.active_topic
        topic = bcfxml.topics[blender_topic.name]
        is_external = "://" in props.bim_snippet_reference
        bim_snippet_class = bcf.v2.model.BimSnippet if bcf_v2 else bcf.v3.model.BimSnippet
        bim_snippet = bim_snippet_class(
            reference=props.bim_snippet_reference if is_external else Path(props.bim_snippet_reference).name,
            reference_schema=props.bim_snippet_schema,
            snippet_type=props.bim_snippet_type,
            is_external=is_external,
        )

        bim_snippet_bytes = None
        if not is_external:
            with open(props.bim_snippet_reference, "rb") as f:
                bim_snippet_bytes = f.read()
        tool.Bcf.set_topic_bim_snippet(topic, bim_snippet, bim_snippet_bytes)

        bpy.ops.bim.load_bcf_topic(topic_guid=topic.guid, topic_index=props.active_topic_index)
        return {"FINISHED"}


class AddBcfRelatedTopic(bpy.types.Operator):
    bl_idname = "bim.add_bcf_related_topic"
    bl_label = "Add BCF Related Topic"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        assert bcfxml
        bcf_v2 = (bcfxml.version.version_id or "").startswith("2")

        props = context.scene.BCFProperties
        blender_topic = props.active_topic
        topic = bcfxml.topics[blender_topic.name]
        related_topics = tool.Bcf.get_topic_related_topics(topic)
        related_topic_guid = props.related_topic

        if bcf_v2:
            assert tool.Bcf.is_list_of(related_topics, bcf.v2.model.TopicRelatedTopic)
            related_topic = bcf.v2.model.TopicRelatedTopic(guid=related_topic_guid)
            related_topics.append(related_topic)
        else:
            assert tool.Bcf.is_list_of(related_topics, bcf.v3.model.TopicRelatedTopicsRelatedTopic)
            related_topic = bcf.v3.model.TopicRelatedTopicsRelatedTopic(guid=related_topic_guid)
            related_topics.append(related_topic)

        tool.Bcf.set_topic_related_topics(topic, related_topics)
        bpy.ops.bim.load_bcf_topic(topic_guid=topic.guid, topic_index=props.active_topic_index)
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
        assert bcfxml
        bcf_v2 = (bcfxml.version.version_id or "").startswith("2")

        props = context.scene.BCFProperties
        blender_topic = props.active_topic
        topic = bcfxml.topics[blender_topic.name]

        is_external = "://" in props.file_reference
        filepath = Path(props.file_reference)
        file_bytes, filename = None, None
        if filepath.is_file():
            filename = filepath.name
            file_bytes = filepath.read_bytes()

        header_files = tool.Bcf.get_topic_header_files(topic)
        if filename and file_bytes:
            topic.reference_files[filename] = file_bytes
        if bcf_v2:
            header_file = bcf.v2.model.HeaderFile(
                filename=filename,
                date=XmlDateTime.now(),
                reference=props.file_reference if is_external else filename,
                ifc_project=props.file_ifc_project,
                ifc_spatial_structure_element=props.file_ifc_spatial_structure_element,
                is_external=is_external,
            )
            assert tool.Bcf.is_list_of(header_files, bcf.v2.model.HeaderFile)
            header_files.append(header_file)
        else:
            header_file = bcf.v3.model.File(
                filename=filename,
                date=XmlDateTime.now(),
                reference=props.file_reference if is_external else filename,
                ifc_project=props.file_ifc_project,
                ifc_spatial_structure_element=props.file_ifc_spatial_structure_element,
                is_external=is_external,
            )
            assert tool.Bcf.is_list_of(header_files, bcf.v3.model.File)
            header_files.append(header_file)

        tool.Bcf.set_topic_header_files(topic, header_files)

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
        if not context.scene.camera:
            cls.poll_message_set("Scene has no active camera.")
            return False
        return True

    def execute(self, context):
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        assert bcfxml
        bcf_v2 = (bcfxml.version.version_id or "").startswith("2")

        blender_camera = context.scene.camera
        assert blender_camera

        props = context.scene.BCFProperties
        blender_topic = props.active_topic
        topic = bcfxml.topics[blender_topic.name]

        direction = blender_camera.matrix_world.to_quaternion() @ Vector((0.0, 0.0, -1.0))
        up = blender_camera.matrix_world.to_quaternion() @ Vector((0.0, 1.0, 0.0))

        blender_render = context.scene.render
        assert isinstance(blender_camera.data, bpy.types.Camera)
        visinfo_guid = str(uuid.uuid4())
        if bcf_v2:
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
                visualization_info = bcf.v2.model.VisualizationInfo(guid=visinfo_guid, orthogonal_camera=camera)
            elif blender_camera.data.type == "PERSP":
                camera = bcf.v2.model.PerspectiveCamera(
                    field_of_view=degrees(blender_camera.data.angle),
                    camera_view_point=camera_view_point,
                    camera_direction=camera_direction,
                    camera_up_vector=camera_up_vector,
                )
                visualization_info = bcf.v2.model.VisualizationInfo(guid=visinfo_guid, perspective_camera=camera)
            else:
                self.report({"INFO"}, f"Unsupported camera type: '{blender_camera.data.type}'.")
                return {"FINISHED"}
        else:
            camera_view_point = bcf.v3.model.Point(
                x=blender_camera.location.x, y=blender_camera.location.y, z=blender_camera.location.z
            )
            camera_direction = bcf.v3.model.Direction(x=direction.x, y=direction.y, z=direction.z)
            camera_up_vector = bcf.v3.model.Direction(x=up.x, y=up.y, z=up.z)
            cam_aspect = blender_render.resolution_x / blender_render.resolution_y
            if blender_camera.data.type == "ORTHO":
                camera = bcf.v3.model.OrthogonalCamera(
                    view_to_world_scale=blender_camera.data.ortho_scale,
                    camera_view_point=camera_view_point,
                    camera_direction=camera_direction,
                    camera_up_vector=camera_up_vector,
                    aspect_ratio=cam_aspect,
                )
                visualization_info = bcf.v3.model.VisualizationInfo(guid=visinfo_guid, orthogonal_camera=camera)
            elif blender_camera.data.type == "PERSP":
                camera = bcf.v3.model.PerspectiveCamera(
                    field_of_view=degrees(blender_camera.data.angle),
                    camera_view_point=camera_view_point,
                    camera_direction=camera_direction,
                    camera_up_vector=camera_up_vector,
                    aspect_ratio=cam_aspect,
                )
                visualization_info = bcf.v3.model.VisualizationInfo(guid=visinfo_guid, perspective_camera=camera)
            else:
                self.report({"INFO"}, f"Unsupported camera type: '{blender_camera.data.type}'.")
                return {"FINISHED"}

        # TODO allow the user to enable or disable snapshotting
        snapshot = None

        old_file_format = blender_render.image_settings.file_format
        blender_render.image_settings.file_format = "PNG"
        old_filepath = blender_render.filepath
        blender_render.filepath = os.path.join(context.scene.BIMProperties.data_dir, "snapshot.png")
        bpy.ops.render.opengl(write_still=True)
        with open(blender_render.filepath, "rb") as f:
            snapshot = f.read()
        # viewpoint.snapshot = blender_render.filepath

        if isinstance(visualization_info, bcf.v2.model.VisualizationInfo):
            vizinfo = bcf.v2.visinfo.VisualizationInfoHandler(visualization_info=visualization_info, snapshot=snapshot)
            assert isinstance(topic, bcf.v2.topic.TopicHandler)
            topic.viewpoints[vizinfo.guid + ".bcfv"] = vizinfo
            viewpoints = tool.Bcf.get_topic_viewpoints(topic)
            viewpoint = bcf.v2.model.ViewPoint(
                viewpoint=vizinfo.guid + ".bcfv", guid=vizinfo.guid, snapshot=vizinfo.guid + ".png"
            )
            assert tool.Bcf.is_list_of(viewpoints, bcf.v2.model.ViewPoint)
            viewpoints.append(viewpoint)
        else:
            vizinfo = bcf.v3.visinfo.VisualizationInfoHandler(visualization_info=visualization_info, snapshot=snapshot)
            assert isinstance(topic, bcf.v3.topic.TopicHandler)
            topic.viewpoints[vizinfo.guid + ".bcfv"] = vizinfo
            viewpoints = tool.Bcf.get_topic_viewpoints(topic)
            viewpoint = bcf.v3.model.ViewPoint(
                viewpoint=vizinfo.guid + ".bcfv", guid=vizinfo.guid, snapshot=vizinfo.guid + ".png"
            )
            assert tool.Bcf.is_list_of(viewpoints, bcf.v3.model.ViewPoint)
            viewpoints.append(viewpoint)
        tool.Bcf.set_topic_viewpoints(topic, viewpoints)

        def get_ifc_elements(objs: list[bpy.types.Object]) -> list[ifcopenshell.entity_instance]:
            elements = []
            for obj in objs:
                if e := tool.Ifc.get_entity(obj):
                    elements.append(e)
            return elements

        selected_elements = get_ifc_elements(context.selected_objects)
        if selected_elements:
            vizinfo.set_selected_elements(selected_elements)

        visible_elements = get_ifc_elements(context.visible_objects)
        if visible_elements:
            vizinfo.set_visible_elements(visible_elements)

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
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        if not bcfxml:
            return False
        props = context.scene.BCFProperties
        topic = props.active_topic
        if not topic:
            return False

        topic = props.topics[topic.name]
        if not tool.Blender.get_enum_safe(topic, "viewpoints"):
            cls.poll_message_set("No viewpoint selected.")
            return False
        return True

    def execute(self, context):
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        assert bcfxml

        props = context.scene.BCFProperties
        blender_topic = props.active_topic
        topic = bcfxml.topics[blender_topic.name]
        del topic.viewpoints[blender_topic.viewpoints]

        viewpoints = tool.Bcf.get_topic_viewpoints(topic)
        # Only guid is required attribute for a viewpoint.
        vp_index = next(i for i, vp in enumerate(viewpoints) if vp.guid in blender_topic.viewpoints)
        del viewpoints[vp_index]
        tool.Bcf.set_topic_viewpoints(topic, viewpoints)

        props.refresh_topic(context)
        return {"FINISHED"}


class RemoveBcfFile(bpy.types.Operator):
    bl_idname = "bim.remove_bcf_file"
    bl_label = "Remove BCF File"
    bl_options = {"REGISTER", "UNDO"}
    index: bpy.props.IntProperty()

    def execute(self, context):
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        assert bcfxml

        props = context.scene.BCFProperties
        blender_topic = props.active_topic
        topic = bcfxml.topics[blender_topic.name]
        header_files = tool.Bcf.get_topic_header_files(topic)
        del header_files[self.index]
        tool.Bcf.set_topic_header_files(topic, header_files)
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
        assert bcfxml

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
        assert bcfxml

        props = context.scene.BCFProperties
        blender_topic = props.active_topic
        topic = bcfxml.topics[blender_topic.name]
        reference_links = tool.Bcf.get_topic_reference_links(topic)
        reference_links.append(props.reference_link)
        tool.Bcf.set_topic_reference_links(topic, reference_links)
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
        assert bcfxml

        bcf_v2 = (bcfxml.version.version_id or "").startswith("2")
        props = context.scene.BCFProperties
        blender_topic = props.active_topic
        topic = bcfxml.topics[blender_topic.name]

        is_external = "://" in props.document_reference

        document_path = Path(props.document_reference)
        document_bytes, filename = None, None
        if document_path.is_file():
            filename = document_path.name
            document_bytes = document_path.read_bytes()

        document_references = tool.Bcf.get_topic_document_references(topic)
        if bcf_v2:
            assert isinstance(topic, bcf.v2.topic.TopicHandler)
            if document_bytes and filename:
                topic.document_references[filename] = document_bytes
            assert tool.Bcf.is_list_of(document_references, bcf.v2.model.TopicDocumentReference)
            document_reference = bcf.v2.model.TopicDocumentReference(
                referenced_document=props.document_reference if is_external else filename,
                description=props.document_reference_description or None,
                guid=str(uuid.uuid4()),
                is_external=is_external,
            )
            document_references.append(document_reference)
        else:
            document_guid = None
            if not is_external:
                assert filename and document_bytes
                assert isinstance(bcfxml, bcf.v3.bcfxml.BcfXml)
                bcf_docs = bcfxml.documents

                if bcf_docs:
                    doc_definition = bcf_docs.definition
                else:
                    doc_definition = bcf.v3.model.DocumentInfo()
                    bcf_docs = bcf.v3.document.DocumentsHandler(doc_definition)
                    bcfxml._documents = bcf_docs

                bcf_docs.documents[filename] = document_bytes
                document_guid = str(uuid.uuid4())
                document = bcf.v3.model.Document(
                    filename=filename, description=props.document_description, guid=document_guid
                )
                doc_definition_docs = doc_definition.documents
                if not doc_definition_docs:
                    doc_definition.documents = (doc_definition_docs := bcf.v3.model.DocumentInfoDocuments())
                doc_definition_docs.document.append(document)

            assert tool.Bcf.is_list_of(document_references, bcf.v3.model.DocumentReference)
            document_reference = bcf.v3.model.DocumentReference(
                document_guid=document_guid,
                url=props.document_reference if is_external else None,
                description=props.document_reference_description or None,
                guid=str(uuid.uuid4()),
            )
            document_references.append(document_reference)
        tool.Bcf.set_topic_document_references(topic, document_references)

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
        assert bcfxml

        props = context.scene.BCFProperties
        blender_topic = props.active_topic
        topic = bcfxml.topics[blender_topic.name]
        new = blender_topic.labels.add()
        new.name = props.label

        labels = tool.Bcf.get_topic_labels(topic)
        labels.append(props.label)
        tool.Bcf.set_topic_labels(topic, labels)
        props.label = ""
        return {"FINISHED"}


class EditBcfReferenceLinks(bpy.types.Operator):
    bl_idname = "bim.edit_bcf_reference_links"
    bl_label = "Edit BCF Reference Link"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        assert bcfxml

        props = context.scene.BCFProperties
        blender_topic = props.active_topic
        topic = bcfxml.topics[blender_topic.name]
        reference_links = [r.name for r in blender_topic.reference_links]
        tool.Bcf.set_topic_reference_links(topic, reference_links)
        return {"FINISHED"}


class EditBcfLabels(bpy.types.Operator):
    bl_idname = "bim.edit_bcf_labels"
    bl_label = "Edit BCF Labels"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        assert bcfxml

        props = context.scene.BCFProperties
        blender_topic = props.active_topic
        topic = bcfxml.topics[blender_topic.name]
        labels = [l.name for l in blender_topic.labels]
        tool.Bcf.set_topic_labels(topic, labels)
        return {"FINISHED"}


class RemoveBcfReferenceLink(bpy.types.Operator):
    bl_idname = "bim.remove_bcf_reference_link"
    bl_label = "Remove BCF Reference Link"
    bl_options = {"REGISTER", "UNDO"}
    index: bpy.props.IntProperty()

    def execute(self, context):
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        assert bcfxml

        props = context.scene.BCFProperties
        blender_topic = props.active_topic
        topic = bcfxml.topics[blender_topic.name]
        reference_links = tool.Bcf.get_topic_reference_links(topic)
        del reference_links[self.index]
        tool.Bcf.set_topic_reference_links(topic, reference_links)
        blender_topic.reference_links.remove(self.index)
        return {"FINISHED"}


class RemoveBcfLabel(bpy.types.Operator):
    bl_idname = "bim.remove_bcf_label"
    bl_label = "Remove BCF Label"
    bl_options = {"REGISTER", "UNDO"}
    index: bpy.props.IntProperty()

    def execute(self, context):
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        assert bcfxml

        props = context.scene.BCFProperties
        blender_topic = props.active_topic
        topic = bcfxml.topics[blender_topic.name]
        labels = tool.Bcf.get_topic_labels(topic)
        del labels[self.index]
        tool.Bcf.set_topic_labels(topic, labels)
        blender_topic.labels.remove(self.index)
        return {"FINISHED"}


class RemoveBcfBimSnippet(bpy.types.Operator):
    bl_idname = "bim.remove_bcf_bim_snippet"
    bl_label = "Remove BCF BIM Snippet"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        assert bcfxml

        props = context.scene.BCFProperties
        blender_topic = props.active_topic
        topic = bcfxml.topics[blender_topic.name]
        tool.Bcf.set_topic_bim_snippet(topic, None)
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
        assert bcfxml
        bcf_v2 = (bcfxml.version.version_id or "").startswith("2")

        props = context.scene.BCFProperties
        blender_topic = props.active_topic
        topic = bcfxml.topics[blender_topic.name]

        document_references = tool.Bcf.get_topic_document_references(topic)
        topic_index: int = self.index
        document_reference = document_references[topic_index]

        # Remove document contents.
        if bcf_v2:
            assert isinstance(topic, bcf.v2.topic.TopicHandler)
            assert isinstance(document_reference, bcf.v2.model.TopicDocumentReference)
            if not document_reference.is_external:
                ref_document = document_reference.referenced_document
                assert ref_document
                del topic.document_references[ref_document]
        else:
            assert isinstance(document_reference, bcf.v3.model.DocumentReference)
            document_guid = document_reference.document_guid
            # For bcf v3 documents are stored in bcfxml, not in the topic.
            if document_guid:
                assert isinstance(bcfxml, bcf.v3.bcfxml.BcfXml)

                # As there's no bcfxml document manager ui yet,
                # we remove document if it's not referenced by any topic.
                present_in_other_topics = False
                for topic_ in bcfxml.topics.values():
                    if topic_ == topic:
                        continue
                    document_references = tool.Bcf.get_topic_document_references(topic_)
                    assert tool.Bcf.is_list_of(document_references, bcf.v3.model.DocumentReference)
                    for ref_ in document_references:
                        if ref_.document_guid == document_guid:
                            present_in_other_topics = True
                            break
                    if present_in_other_topics:
                        break

                if not present_in_other_topics:
                    doc_handler = bcfxml.documents
                    assert doc_handler
                    docs = doc_handler.definition.documents
                    assert docs
                    doc = next(d for d in docs.document if d.guid == document_guid)
                    del doc_handler.documents[doc.filename]
                    docs.document.remove(doc)

        # Remove document reference.
        del document_references[topic_index]
        tool.Bcf.set_topic_document_references(topic, document_references)

        bpy.ops.bim.load_bcf_topic(topic_guid=topic.guid, topic_index=props.active_topic_index)
        return {"FINISHED"}


class RemoveBcfRelatedTopic(bpy.types.Operator):
    bl_idname = "bim.remove_bcf_related_topic"
    bl_label = "Remove BCF Related Topic"
    bl_options = {"REGISTER", "UNDO"}
    index: bpy.props.IntProperty()

    def execute(self, context):
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        assert bcfxml

        props = context.scene.BCFProperties
        blender_topic = props.active_topic
        topic = bcfxml.topics[blender_topic.name]
        related_topics = tool.Bcf.get_topic_related_topics(topic)
        del related_topics[self.index]
        tool.Bcf.set_topic_related_topics(topic, related_topics)
        bpy.ops.bim.load_bcf_topic(topic_guid=topic.guid, topic_index=props.active_topic_index)
        return {"FINISHED"}


class RemoveBcfComment(bpy.types.Operator):
    bl_idname = "bim.remove_bcf_comment"
    bl_label = "Remove BCF Comment"
    bl_options = {"REGISTER", "UNDO"}
    comment_guid: bpy.props.StringProperty()

    def execute(self, context):
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        assert bcfxml

        props = context.scene.BCFProperties
        blender_topic = props.active_topic
        topic = bcfxml.topics[blender_topic.name]
        comments = topic.comments
        i = next(i for i, c in enumerate(comments) if c.guid == self.comment_guid)
        del comments[i]
        topic.coments = comments
        bpy.ops.bim.load_bcf_comments(topic_guid=topic.guid)
        return {"FINISHED"}


class EditBcfComment(bpy.types.Operator):
    bl_idname = "bim.edit_bcf_comment"
    bl_label = "Edit BCF Comment"
    bl_options = {"REGISTER", "UNDO"}
    comment_guid: bpy.props.StringProperty()

    def execute(self, context):
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        assert bcfxml

        props = context.scene.BCFProperties
        blender_topic = props.active_topic
        blender_comment = blender_topic.comments.get(self.comment_guid)
        topic = bcfxml.topics[blender_topic.name]
        for comment in topic.comments:
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
            cls.poll_message_set("No comment to add.")
            return False

        topic = props.active_topic
        if not topic:
            cls.poll_message_set("No topic is active.")
            return False

        if props.has_related_viewpoint:
            topic = props.topics[topic.name]
            viewpoint = tool.Blender.get_enum_safe(topic, "viewpoints")
            if not viewpoint:
                cls.poll_message_set("No viewpoint is active to add a comment with viewpoint.")
                return False
        return True

    def execute(self, context):
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        assert bcfxml
        bcf_v2 = (bcfxml.version.version_id or "").startswith("2")

        props = context.scene.BCFProperties
        blender_topic = props.active_topic
        topic = bcfxml.topics[blender_topic.name]
        comments = topic.comments

        if bcf_v2:
            comment = bcf.v2.model.Comment(
                date=XmlDateTime.now(),
                author=context.scene.BCFProperties.author,
                comment=props.comment,
                guid=str(uuid.uuid4()),
            )
            if props.has_related_viewpoint:
                comment.viewpoint = bcf.v2.model.CommentViewpoint(guid=blender_topic.viewpoints)
            assert tool.Bcf.is_list_of(comments, bcf.v2.model.Comment)
            comments.append(comment)
            assert isinstance(topic, bcf.v2.topic.TopicHandler)
            topic.comments = comments
        else:
            comment = bcf.v3.model.Comment(
                date=XmlDateTime.now(),
                author=context.scene.BCFProperties.author,
                comment=props.comment,
                guid=str(uuid.uuid4()),
            )
            if props.has_related_viewpoint:
                comment.viewpoint = bcf.v3.model.CommentViewpoint(guid=blender_topic.viewpoints)
            assert tool.Bcf.is_list_of(comments, bcf.v3.model.Comment)
            comments.append(comment)
            assert isinstance(topic, bcf.v3.topic.TopicHandler)
            topic.comments = comments

        bpy.ops.bim.load_bcf_comments(topic_guid=topic.guid)
        props.comment = ""
        props.has_related_viewpoint = False
        return {"FINISHED"}


class ActivateBcfViewpoint(bpy.types.Operator):
    bl_idname = "bim.activate_bcf_viewpoint"
    bl_label = "Activate BCF Viewpoint"
    bl_options = {"REGISTER", "UNDO"}
    viewpoint_guid: bpy.props.StringProperty(
        name="Viewpoint GUID",
        description="Viewpoint GUID from the active topic to activate. If not provided active viewpoint will be used",
        default="",
        options={"SKIP_SAVE"},
    )

    @classmethod
    def poll(cls, context):
        props = context.scene.BCFProperties
        blender_topic = props.active_topic
        if blender_topic is None:
            cls.poll_message_set("No topic is active.")
            return False
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        assert bcfxml
        topic = bcfxml.topics[blender_topic.name]
        if not topic.viewpoints:
            cls.poll_message_set("No viewpoints in the active topic.")
            return False
        return True

    def execute(self, context):
        self.file = IfcStore.get_file()
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        assert bcfxml

        props = context.scene.BCFProperties
        blender_topic = props.active_topic
        topic = bcfxml.topics[blender_topic.name]
        if self.viewpoint_guid:
            viewpoint_guid = self.viewpoint_guid
            if viewpoint_guid not in topic.viewpoints:
                self.report({"ERROR"}, f"No such viewpoint in the active topic: '{viewpoint_guid}'.")
                return {"CANCELLED"}
        else:
            viewpoint_guid = tool.Blender.get_enum_safe(blender_topic, "viewpoints")
            if viewpoint_guid is None:
                self.report({"ERROR"}, "No viewpoint is active.")
                return {"CANCELLED"}

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
        if tool.Bcf.get_viewpoint_bitmaps(viewpoint):
            self.create_bitmaps(bcfxml, viewpoint, topic)

        self.setup_camera(viewpoint, obj, cam_aspect, context)
        return {"FINISHED"}

    def setup_camera(
        self,
        viewpoint: bcf.agnostic.visinfo.VisualizationInfoHandler,
        obj: bpy.types.Object,
        cam_aspect: float,
        context: bpy.types.Context,
    ) -> None:
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
                float(props.blender_offset_x) * unit_scale,
                float(props.blender_offset_y) * unit_scale,
                float(props.blender_offset_z) * unit_scale,
                float(props.blender_x_axis_abscissa),
                float(props.blender_x_axis_ordinate),
            )
        obj.matrix_world = Matrix(matrix.tolist())

    def set_viewpoint_components(
        self, viewpoint: bcf.agnostic.visinfo.VisualizationInfoHandler, context: bpy.types.Context
    ) -> None:
        if not viewpoint.visualization_info.components:
            return

        # Operators with context overrides are used because they are
        # significantly faster than looping through all objects

        self.set_exceptions(viewpoint, context)
        self.set_view_setup_hints(viewpoint, context)
        # set selection at the end not to conflict with .hide_spaces
        self.set_selection(viewpoint)
        self.set_colours(viewpoint)

    def set_exceptions(
        self, viewpoint: bcf.agnostic.visinfo.VisualizationInfoHandler, context: bpy.types.Context
    ) -> None:
        visibility_settings = viewpoint.get_elements_visibility()
        if visibility_settings is None:
            return

        default_visibility, exception_global_ids = visibility_settings

        objs: list[bpy.types.Object] = []
        for global_id in exception_global_ids:
            obj = IfcStore.get_element(global_id)
            if obj and context.view_layer.objects.get(obj.name):
                assert isinstance(obj, bpy.types.Object)
                objs.append(obj)

        context_override = tool.Blender.get_viewport_context()
        if default_visibility:
            # default_visibility is True: show all objs, hide the exceptions
            with context.temp_override(**context_override):
                bpy.ops.object.hide_view_clear(select=False)
                for obj in objs:
                    obj.hide_set(True)
        else:
            # default_visibility is False: hide all objs, show the exceptions
            with context.temp_override(**context_override):
                bpy.ops.object.hide_view_clear(select=False)
                bpy.ops.object.select_all(action="DESELECT")

                # We need to store unselectable objects and toggle unselectibility for them.
                # As hide_view_set requires them to be selected to work.
                unselectable = []
                for obj in objs:
                    if obj.hide_select:
                        unselectable.append(obj)
                        obj.hide_select = False
                    obj.select_set(True)

                # hide_view_set is checking actually selected objects, not context.selected objects.
                bpy.ops.object.hide_view_set(unselected=True)
                bpy.data.objects["Viewpoint"].hide_set(False)
                for obj in unselectable:
                    obj.hide_select = True

    def set_view_setup_hints(
        self, viewpoint: bcf.agnostic.visinfo.VisualizationInfoHandler, context: bpy.types.Context
    ) -> None:
        # TODO: handle view_setup_hints.openings_visible
        # should we reload elements with/without opening applied here or ...?
        if view_setup_hints := tool.Bcf.get_viewpoint_view_setup_hints(viewpoint):
            pass
            if not view_setup_hints.spaces_visible:
                self.hide_spaces(context)
        else:
            self.hide_spaces(context)

    def hide_spaces(self, context: bpy.types.Context) -> None:
        old = context.area.type
        context.area.type = "VIEW_3D"
        bpy.ops.object.select_all(action="DESELECT")
        bpy.ops.object.select_pattern(pattern="IfcSpace/*")
        bpy.ops.object.hide_view_set()
        context.area.type = old

    def set_selection(self, viewpoint: bcf.agnostic.visinfo.VisualizationInfoHandler) -> None:
        selected_global_ids = viewpoint.get_selected_guids()
        if selected_global_ids is None:
            return
        bpy.ops.object.select_all(action="DESELECT")
        for global_id in selected_global_ids:
            obj = IfcStore.get_element(global_id)
            if obj:
                obj.select_set(True)
                obj.hide_set(False)

    def set_colours(self, viewpoint: bcf.agnostic.visinfo.VisualizationInfoHandler) -> None:
        if not viewpoint.visualization_info.components or not viewpoint.visualization_info.components.coloring:
            return
        global_id_colours = {}
        for acoloring in viewpoint.visualization_info.components.coloring.color:
            for acomponent in acoloring.component:
                global_id_colours.setdefault(acomponent.ifc_guid, acoloring.color)
        for global_id, color in global_id_colours.items():
            obj = IfcStore.get_element(global_id)
            if obj:
                obj.color = self.hex_to_rgb(color)

    def draw_lines(self, viewpoint: bcf.agnostic.visinfo.VisualizationInfoHandler, context: bpy.types.Context) -> None:
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

    def create_clipping_planes(self, viewpoint: bcf.agnostic.visinfo.VisualizationInfoHandler) -> None:
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

    def delete_clipping_planes(self, context: bpy.types.Context) -> None:
        collection = bpy.data.collections.get("Sections")
        if not collection:
            return
        for section in collection.objects:
            context.view_layer.objects.active = section
            bpy.ops.bim.remove_section_plane()

    def delete_bitmaps(self, context: bpy.types.Context) -> None:
        collection = bpy.data.collections.get("Bitmaps")
        if not collection:
            collection = bpy.data.collections.new("Bitmaps")
            context.scene.collection.children.link(collection)
        for bitmap in collection.objects:
            bpy.data.objects.remove(bitmap)

    def create_bitmaps(
        self, bcfxml, viewpoint: bcf.agnostic.visinfo.VisualizationInfoHandler, topic: bcf.agnostic.topic.TopicHandler
    ) -> None:
        collection = bpy.data.collections.get("Bitmaps")
        if not collection:
            collection = bpy.data.collections.new("Bitmaps")
        for bitmap in tool.Bcf.get_viewpoint_bitmaps(viewpoint):
            obj = bpy.data.objects.new("Bitmap", None)
            obj.empty_display_type = "IMAGE"
            # image = bpy.data.images.load(os.path.join(bcfxml.filepath, topic.guid, bitmap.reference))
            with tempfile.NamedTemporaryFile(delete=False) as f:
                bcf.agnostic.topic.extract_file(topic, bitmap, outfile=Path(f.name))
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

    def hex_to_rgb(self, value: str) -> list[float]:
        value = value.lstrip("#")
        lv = len(value)
        # https://github.com/buildingSMART/BCF-XML/tree/release_3_0/Documentation#coloring
        if lv == 8:
            t = tuple(int(value[i : i + lv // 4], 16) for i in range(0, lv, lv // 4))
            col = [t[1] / 255.0, t[2] / 255.0, t[3] / 255.0, t[0] / 255.0]
        else:
            t = tuple(int(value[i : i + lv // 3], 16) for i in range(0, lv, lv // 3))
            col = [t[0] / 255.0, t[1] / 255.0, t[2] / 255.0, 1]
        return col


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


class LoadBcfHeaderIfcFile(bpy.types.Operator):
    bl_idname = "bim.load_bcf_header_ifc_file"
    bl_label = "Load BCF Header IFC File"
    bl_description = (
        "Extract BCF Header IFC file and load it in current session."
        "\n\nWarning. Current IFC and BCF sessions won't be saved, BCF file will be reloaded (if it's saved on disk)"
    )
    bl_options = {"REGISTER", "UNDO"}
    index: bpy.props.IntProperty()

    def execute(self, context):
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        assert bcfxml

        bcf_path = tool.Bcf.get_path()
        topic = bcfxml.topics[context.scene.BCFProperties.active_topic.name]
        entity = tool.Bcf.get_topic_header_files(topic)[self.index]
        ifc_path = bcf.agnostic.topic.extract_file(topic, entity)
        bpy.ops.bim.load_project(filepath=ifc_path)
        if bcf_path:
            bpy.ops.bim.load_bcf_project(filepath=bcf_path)
        return {"FINISHED"}


class ExtractBcfFile(bpy.types.Operator):
    bl_idname = "bim.extract_bcf_file"
    bl_label = "Extract BCF Header File"
    bl_options = {"REGISTER", "UNDO"}
    entity_type: bpy.props.StringProperty()
    index: bpy.props.IntProperty()

    def execute(self, context):
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        assert bcfxml

        topic = bcfxml.topics[context.scene.BCFProperties.active_topic.name]

        if self.entity_type == "HEADER_FILE":
            entity = tool.Bcf.get_topic_header_files(topic)[self.index]
        elif self.entity_type == "BIM_SNIPPET":
            entity = topic.topic.bim_snippet
        elif self.entity_type == "DOCUMENT_REFERENCE":
            entity = tool.Bcf.get_topic_document_references(topic)[self.index]
        else:
            assert False

        assert entity
        filepath = bcf.agnostic.topic.extract_file(topic, entity, bcfxml)
        assert isinstance(filepath, Path)
        webbrowser.open(str(filepath.parent))
        return {"FINISHED"}


class BCFFileHandlerOperator(bpy.types.Operator):
    bl_idname = "bim.load_bcf_project_file_handler"
    bl_label = "Import .bcf file"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    directory: bpy.props.StringProperty(subtype="FILE_PATH", options={"SKIP_SAVE", "HIDDEN"})
    files: bpy.props.CollectionProperty(type=bpy.types.OperatorFileListElement, options={"SKIP_SAVE", "HIDDEN"})

    def invoke(self, context, event):
        # Keeping code in .invoke() as we might add some
        # popup windows later.

        if len(self.files) > 1:
            self.report({"INFO"}, "Loading multiple BCF files is not supported.")
            return {"FINISHED"}

        if bcfstore.BcfStore.get_bcfxml():
            bpy.ops.bim.unload_bcf_project()

        # `files` contain only .bcf files.
        filepath = Path(self.directory)
        filename = self.files[0].name
        res = bpy.ops.bim.load_bcf_project(filepath=(filepath / filename).as_posix())
        if res != {"FINISHED"}:
            return res
        self.report({"INFO"}, f"BCF Project '{filename}' is loaded.")
        return {"FINISHED"}


class BIM_FH_import_bcf(bpy.types.FileHandler):
    bl_label = "BCF File Handler"
    bl_import_operator = BCFFileHandlerOperator.bl_idname
    bl_file_extensions = ".bcf"

    # FileHandler won't work without poll_drop defined.
    @classmethod
    def poll_drop(cls, context):
        return True
