import os
import uuid
import shutil
import zipfile
import logging
import tempfile
import bcf.v2.data
from datetime import datetime
from xml.dom import minidom
from xmlschema import XMLSchema
from contextlib import contextmanager
from shutil import copyfile


cwd = os.path.dirname(os.path.realpath(__file__))


@contextmanager
def cd(newdir):
    prevdir = os.getcwd()
    os.chdir(os.path.expanduser(newdir))
    try:
        yield
    finally:
        os.chdir(prevdir)


class BcfXml:
    def __init__(self):
        self.filepath = None
        self.logger = logging.getLogger("bcfxml")
        self.author = "john@doe.com"
        self.project = bcf.v2.data.Project()
        self.version = "2.1"
        self.topics = {}

    def new_project(self):
        self.project.project_id = str(uuid.uuid4())
        self.project.name = "New Project"
        self.topics = {}
        if self.filepath:
            self.close_project()
        self.filepath = tempfile.mkdtemp()
        self.edit_project()
        self.edit_version()

    def get_project(self, filepath=None):
        if not filepath:
            return self.project
        if os.path.isfile(os.path.join(self.filepath, "project.bcfp")):
            data = self._read_xml("project.bcfp", "project.xsd")
            self.project.extension_schema = data["ExtensionSchema"]
            if "Project" in data:
                self.project.project_id = data["Project"]["@ProjectId"]
                self.project.name = data["Project"].get("Name")
        return self.project

    def edit_project(self):
        self.document = minidom.Document()
        root = self._create_element(self.document, "ProjectExtension")
        project = self._create_element(root, "Project", {"ProjectId": self.project.project_id})
        self._create_element(project, "Name", text=self.project.name)
        self._create_element(root, "ExtensionSchema", text="extensions.xsd")
        with open(os.path.join(self.filepath, "project.bcfp"), "wb") as f:
            f.write(self.document.toprettyxml(encoding="utf-8"))

    def save_project(self, filepath):
        with cd(self.filepath):
            zip_file = zipfile.ZipFile(filepath, "w", zipfile.ZIP_DEFLATED)
            for root, dirs, files in os.walk("./"):
                for file in files:
                    zip_file.write(os.path.join(root, file))
            zip_file.close()

    def get_version(self):
        data = self._read_xml("bcf.version", "version.xsd")
        self.version = data["@VersionId"]
        return self.version

    def edit_version(self):
        self.document = minidom.Document()
        root = self._create_element(self.document, "Version", {"VersionId": self.version})
        version = self._create_element(root, "DetailedVersion", text=self.version)
        with open(os.path.join(self.filepath, "bcf.version"), "wb") as f:
            f.write(self.document.toprettyxml(encoding="utf-8"))

    def get_topics(self):
        self.topics = {}
        topics = []
        subdirs = []
        for (dirpath, dirnames, filenames) in os.walk(self.filepath):
            subdirs = dirnames
            break
        for subdir in subdirs:
            try:
                uuid.UUID(subdir)
            except ValueError:
                continue
            if not os.path.exists(os.path.join(self.filepath, subdir, "markup.bcf")):
                continue
            self.topics[subdir] = self.get_topic(subdir)
        return self.topics

    def get_header(self, guid):
        data = self._read_xml(os.path.join(guid, "markup.bcf"), "markup.xsd")
        if "Header" not in data:
            return
        header = bcf.v2.data.Header()
        for item in data["Header"]["File"]:
            header_file = bcf.v2.data.HeaderFile()
            optional_keys = {
                "filename": "Filename",
                "date": "Date",
                "reference": "Reference",
                "ifc_project": "@IfcProject",
                "ifc_spatial_structure_element": "@IfcSpatialStructureElement",
                "is_external": "@isExternal",
            }
            for key, value in optional_keys.items():
                if value in item:
                    setattr(header_file, key, item[value])
            header.files.append(header_file)
        self.topics[guid].header = header
        return header

    def get_topic(self, guid):
        if guid in self.topics:
            return self.topics[guid]
        data = self._read_xml(os.path.join(guid, "markup.bcf"), "markup.xsd")
        topic = bcf.v2.data.Topic()
        self.topics[guid] = topic

        mandatory_keys = {
            "guid": "@Guid",
            "title": "Title",
            "creation_date": "CreationDate",
            "creation_author": "CreationAuthor",
        }
        for key, value in mandatory_keys.items():
            setattr(topic, key, data["Topic"][value])

        optional_keys = {
            "priority": "Priority",
            "index": "Index",
            "labels": "Labels",
            "reference_links": "ReferenceLink",
            "modified_date": "ModifiedDate",
            "modified_author": "ModifiedAuthor",
            "due_date": "DueDate",
            "assigned_to": "AssignedTo",
            "stage": "Stage",
            "description": "Description",
            "topic_status": "@TopicStatus",
            "topic_type": "@TopicType",
        }
        for key, value in optional_keys.items():
            if value in data["Topic"]:
                setattr(topic, key, data["Topic"][value])

        if "BimSnippet" in data["Topic"]:
            bim_snippet = bcf.v2.data.BimSnippet()
            keys = {
                "snippet_type": "@SnippetType",
                "is_external": "@IsExternal",
                "reference": "Reference",
                "reference_schema": "ReferenceSchema",
            }
            for key, value in keys.items():
                if value in data["Topic"]["BimSnippet"]:
                    setattr(bim_snippet, key, data["Topic"]["BimSnippet"][value])
            topic.bim_snippet = bim_snippet

        if "DocumentReference" in data["Topic"]:
            for item in data["Topic"]["DocumentReference"]:
                document_reference = bcf.v2.data.DocumentReference()
                keys = {
                    "referenced_document": "ReferencedDocument",
                    "is_external": "@IsExternal",
                    "guid": "@Guid",
                    "description": "Description",
                }
                for key, value in keys.items():
                    if value in item:
                        setattr(document_reference, key, item[value])
                topic.document_references.append(document_reference)

        if "RelatedTopic" in data["Topic"]:
            for item in data["Topic"]["RelatedTopic"]:
                related_topic = bcf.v2.data.RelatedTopic()
                related_topic.guid = item["@Guid"]
                topic.related_topics.append(related_topic)
        return topic

    def add_topic(self, topic=None):
        if topic is None:
            topic = bcf.v2.data.Topic()
        if not topic.guid:
            topic.guid = str(uuid.uuid4())
        if not topic.title:
            topic.title = "New Topic"
        os.mkdir(os.path.join(self.filepath, topic.guid))
        self.edit_topic(topic)
        return topic

    def edit_topic(self, topic):
        if not topic.creation_date:
            topic.creation_date = datetime.utcnow().isoformat()
            topic.creation_author = self.author
        else:
            topic.modified_date = datetime.utcnow().isoformat()
            topic.modified_author = self.author

        self.document = minidom.Document()
        root = self._create_element(self.document, "Markup")

        self.write_header(topic.header, root)

        topic_el = self._create_element(
            root,
            "Topic",
            {
                "Guid": topic.guid,
                "TopicType": topic.topic_type,
                "TopicStatus": topic.topic_status,
            },
        )

        for reference_link in topic.reference_links:
            self._create_element(topic_el, "ReferenceLink", text=reference_link)

        text_map = {
            "Title": topic.title,
            "Priority": topic.priority,
            "Index": topic.index,
        }
        for key, value in text_map.items():
            if value:
                self._create_element(topic_el, key, text=value)

        for label in topic.labels:
            self._create_element(topic_el, "Labels", text=label)

        text_map = {
            "CreationDate": topic.creation_date,
            "CreationAuthor": topic.creation_author,
            "ModifiedDate": topic.modified_date,
            "ModifiedAuthor": topic.modified_author,
            "DueDate": topic.due_date,
            "AssignedTo": topic.assigned_to,
            "Stage": topic.stage,
            "Description": topic.description,
        }
        for key, value in text_map.items():
            if value:
                self._create_element(topic_el, key, text=value)

        if topic.bim_snippet:
            bim_snippet = self._create_element(
                topic_el,
                "BimSnippet",
                {"SnippetType": topic.bim_snippet.snippet_type, "isExternal": topic.bim_snippet.is_external},
            )
            self._create_element(bim_snippet, "Reference", text=topic.bim_snippet.reference)
            self._create_element(bim_snippet, "ReferenceSchema", text=topic.bim_snippet.reference_schema)
        for reference in topic.document_references:
            reference_el = self._create_element(
                topic_el, "DocumentReference", {"Guid": reference.guid, "isExternal": reference.is_external}
            )
            self._create_element(reference_el, "ReferencedDocument", text=reference.referenced_document)
            self._create_element(reference_el, "Description", text=reference.description)
        for related_topic in topic.related_topics:
            self._create_element(topic_el, "RelatedTopic", {"Guid": related_topic.guid})

        self.write_comments(topic.comments, root)
        self.write_viewpoints(topic.viewpoints, root, topic)

        with open(os.path.join(self.filepath, topic.guid, "markup.bcf"), "wb") as f:
            f.write(self.document.toprettyxml(encoding="utf-8"))

    def write_header(self, header, root):
        if not header or not header.files:
            return
        header_el = self._create_element(root, "Header")
        for f in header.files:
            file_el = self._create_element(
                header_el,
                "File",
                {
                    "IfcProject": f.ifc_project,
                    "IfcSpatialStructureElement": f.ifc_spatial_structure_element,
                    "isExternal": f.is_external,
                },
            )
            if f.filename:
                self._create_element(file_el, "Filename", text=f.filename)
            if f.date:
                self._create_element(file_el, "Date", text=f.date)
            if f.reference:
                self._create_element(file_el, "Reference", text=f.reference)

    def write_comments(self, comments, root):
        for comment in comments.values():
            comment_el = self._create_element(root, "Comment", {"Guid": comment.guid})
            text_map = {
                "Date": comment.date,
                "Author": comment.author,
                "Comment": comment.comment,
                "ModifiedDate": comment.modified_date,
                "ModifiedAuthor": comment.modified_author,
            }
            for key, value in text_map.items():
                if value:
                    self._create_element(comment_el, key, text=value)
            if comment.viewpoint:
                self._create_element(comment_el, "Viewpoint", {"Guid": comment.viewpoint.guid})

    def add_comment(self, topic, comment=None):
        if comment is None:
            comment = bcf.v2.data.Comment()
        if not comment.guid:
            comment.guid = str(uuid.uuid4())
        if not comment.comment:
            comment.comment = "'Free software' is a matter of liberty, not price. To understand the concept, you should think of 'free' as in 'free speech,' not as in 'free beer'."
        topic.comments[comment.guid] = comment
        self.edit_comment(comment, topic)

    def edit_comment(self, comment, topic):
        if not comment.date:
            comment.date = datetime.utcnow().isoformat()
            comment.author = self.author
        else:
            comment.modified_date = datetime.utcnow().isoformat()
            comment.modified_author = self.author
        self.edit_topic(topic)

    def delete_comment(self, guid, topic):
        if guid in topic.comments:
            del topic.comments[guid]
        self.edit_topic(topic)

    def delete_topic(self, guid):
        if guid in self.topics:
            del self.topics[guid]
        shutil.rmtree(os.path.join(self.filepath, guid))

    def write_viewpoints(self, viewpoints, root, topic):
        for viewpoint in viewpoints.values():
            viewpoint_el = self._create_element(root, "Viewpoints", {"Guid": viewpoint.guid})
            text_map = {"Viewpoint": viewpoint.viewpoint, "Snapshot": viewpoint.snapshot, "Index": viewpoint.index}
            for key, value in text_map.items():
                if value:
                    self._create_element(viewpoint_el, key, text=value)
            self.write_viewpoint(viewpoint, topic)

    def write_viewpoint(self, viewpoint, topic):
        document = minidom.Document()
        root = self._create_element(document, "VisualizationInfo", {"Guid": viewpoint.guid})
        self.write_viewpoint_components(viewpoint, root)
        self.write_viewpoint_orthogonal_camera(viewpoint, root)
        self.write_viewpoint_perspective_camera(viewpoint, root)
        self.write_viewpoint_lines(viewpoint, root)
        self.write_viewpoint_clipping_planes(viewpoint, root)
        self.write_viewpoint_bitmaps(viewpoint, root)
        with open(os.path.join(self.filepath, topic.guid, viewpoint.viewpoint), "wb") as f:
            f.write(document.toprettyxml(encoding="utf-8"))

    def write_viewpoint_components(self, viewpoint, parent):
        if not viewpoint.components:
            return
        components_el = self._create_element(parent, "Components")
        if viewpoint.components.view_setup_hints:
            view_setup_hints = self._create_element(
                components_el,
                "ViewSetupHints",
                {
                    "SpacesVisible": viewpoint.components.view_setup_hints.spaces_visible,
                    "SpaceBoundariesVisible": viewpoint.components.view_setup_hints.space_boundaries_visible,
                    "OpeningsVisible": viewpoint.components.view_setup_hints.openings_visible,
                },
            )
        if viewpoint.components.selection:
            selection_el = self._create_element(components_el, "Selection")
        for selection in viewpoint.components.selection:
            self.write_component(selection, selection_el)
        visibility = self._create_element(
            components_el, "Visibility", {"DefaultVisibility": viewpoint.components.visibility.default_visibility}
        )
        if viewpoint.components.visibility.exceptions:
            exceptions_el = self._create_element(visibility, "Exceptions")
        for exception in viewpoint.components.visibility.exceptions:
            self.write_component(exception, exceptions_el)
        if viewpoint.components.coloring:
            coloring_el = self._create_element(components_el, "Coloring")
        for color in viewpoint.components.coloring:
            color_el = self._create_element(coloring_el, "Color", {"Color": color.color})
            for component in color.components:
                self.write_component(component, color_el)

    def write_viewpoint_orthogonal_camera(self, viewpoint, parent):
        if not viewpoint.orthogonal_camera:
            return
        camera = viewpoint.orthogonal_camera
        camera_el = self._create_element(parent, "OrthogonalCamera")
        camera_view_point = self._create_element(camera_el, "CameraViewPoint")
        self.write_vector(camera_view_point, camera.camera_view_point)
        camera_direction = self._create_element(camera_el, "CameraDirection")
        self.write_vector(camera_direction, camera.camera_direction)
        camera_up_vector = self._create_element(camera_el, "CameraUpVector")
        self.write_vector(camera_up_vector, camera.camera_up_vector)
        self._create_element(camera_el, "ViewToWorldScale", text=camera.view_to_world_scale)

    def write_viewpoint_perspective_camera(self, viewpoint, parent):
        if not viewpoint.perspective_camera:
            return
        camera = viewpoint.perspective_camera
        camera_el = self._create_element(parent, "PerspectiveCamera")
        camera_view_point = self._create_element(camera_el, "CameraViewPoint")
        self.write_vector(camera_view_point, camera.camera_view_point)
        camera_direction = self._create_element(camera_el, "CameraDirection")
        self.write_vector(camera_direction, camera.camera_direction)
        camera_up_vector = self._create_element(camera_el, "CameraUpVector")
        self.write_vector(camera_up_vector, camera.camera_up_vector)
        self._create_element(camera_el, "FieldOfView", text=camera.field_of_view)

    def write_viewpoint_lines(self, viewpoint, parent):
        if not viewpoint.lines:
            return
        lines_el = self._create_element(parent, "Lines")
        for line in viewpoint.lines:
            line_el = self._create_element(lines_el, "Line")
            start_point_el = self._create_element(line_el, "StartPoint")
            self.write_vector(start_point_el, line.start_point)
            end_point_el = self._create_element(line_el, "EndPoint")
            self.write_vector(end_point_el, line.end_point)

    def write_viewpoint_clipping_planes(self, viewpoint, parent):
        if not viewpoint.clipping_planes:
            return
        planes_el = self._create_element(parent, "ClippingPlanes")
        for plane in viewpoint.clipping_planes:
            plane_el = self._create_element(planes_el, "ClippingPlane")
            location_el = self._create_element(plane_el, "Location")
            self.write_vector(location_el, plane.location)
            direction_el = self._create_element(plane_el, "Direction")
            self.write_vector(direction_el, plane.direction)

    def write_viewpoint_bitmaps(self, viewpoint, parent):
        if not viewpoint.bitmaps:
            return
        for bitmap in viewpoint.bitmaps:
            bitmap_el = self._create_element(parent, "Bitmap")

            text_map = {"Bitmap": bitmap.bitmap_format, "Reference": bitmap.reference}
            for key, value in text_map.items():
                self._create_element(bitmap_el, key, text=value)

            location_el = self._create_element(bitmap_el, "Location")
            self.write_vector(location_el, bitmap.location)
            normal_el = self._create_element(bitmap_el, "Normal")
            self.write_vector(normal_el, bitmap.normal)
            up_el = self._create_element(bitmap_el, "Up")
            self.write_vector(up_el, bitmap.up)

            self._create_element(bitmap_el, "Height", text=bitmap.height)

    def write_vector(self, parent, from_obj):
        self._create_element(parent, "X", text=from_obj.x)
        self._create_element(parent, "Y", text=from_obj.y)
        self._create_element(parent, "Z", text=from_obj.z)

    def write_component(self, data, parent):
        component_el = self._create_element(parent, "Component", {"IfcGuid": data.ifc_guid})
        text_map = {"OriginatingSystem": data.originating_system, "AuthoringToolId": data.authoring_tool_id}
        for key, value in text_map.items():
            if value:
                self._create_element(component_el, key, text=value)

    def add_viewpoint(self, topic, viewpoint=None):
        if not viewpoint:
            viewpoint = bcf.v2.data.Viewpoint()
        if not viewpoint.guid:
            viewpoint.guid = str(uuid.uuid4())
        if not viewpoint.viewpoint:
            viewpoint.viewpoint = f"{viewpoint.guid}.bcfv"
        if viewpoint.snapshot:
            topic_filepath = os.path.join(self.filepath, topic.guid)
            filepath = os.path.join(topic_filepath, viewpoint.snapshot)
            if not os.path.exists(filepath):
                filename = viewpoint.guid + os.path.splitext(viewpoint.snapshot)[-1]
                copyfile(viewpoint.snapshot, os.path.join(topic_filepath, filename))
                viewpoint.snapshot = filename
        topic.viewpoints[viewpoint.guid] = viewpoint
        self.edit_topic(topic)

    def delete_viewpoint(self, guid, topic):
        if guid not in topic.viewpoints:
            return
        viewpoint = topic.viewpoints[guid]
        if viewpoint.snapshot:
            filepath = os.path.join(self.filepath, topic.guid, viewpoint.snapshot)
            if os.path.exists(filepath):
                os.remove(filepath)
        if viewpoint.viewpoint:
            filepath = os.path.join(self.filepath, topic.guid, viewpoint.viewpoint)
            if os.path.exists(filepath):
                os.remove(filepath)
        for bitmap in viewpoint.bitmaps:
            if not bitmap.reference:
                continue
            filepath = os.path.join(self.filepath, topic.guid, bitmap.reference)
            if os.path.exists(filepath):
                os.remove(filepath)
        del topic.viewpoints[guid]
        self.edit_topic(topic)

    def delete_file(self, topic, index):
        if not topic.header:
            return
        f = topic.header.files.pop(index)
        filepath = os.path.join(self.filepath, topic.guid, f.reference)
        if not f.is_external and os.path.exists(filepath):
            os.remove(filepath)
        self.edit_topic(topic)

    def delete_bim_snippet(self, topic):
        if not topic.bim_snippet:
            return
        if topic.bim_snippet.reference and not topic.bim_snippet.is_external:
            filepath = os.path.join(self.filepath, topic.guid, topic.bim_snippet.reference)
            if os.path.exists(filepath):
                os.remove(filepath)
        topic.bim_snippet = None
        self.edit_topic(topic)

    def delete_document_reference(self, topic, index):
        document_reference = topic.document_references[index]
        if document_reference.referenced_document and not document_reference.is_external:
            filepath = os.path.join(self.filepath, topic.guid, document_reference.referenced_document)
            if os.path.exists(filepath):
                os.remove(filepath)
        del topic.document_references[index]
        self.edit_topic(topic)

    def add_document_reference(self, topic, document_reference):
        if os.path.exists(document_reference.referenced_document):
            topic_filepath = os.path.join(self.filepath, topic.guid)
            filename = os.path.basename(document_reference.referenced_document)
            copyfile(document_reference.referenced_document, os.path.join(topic_filepath, filename))
            document_reference.referenced_document = filename
            document_reference.is_external = False
        else:
            document_reference.is_external = True
        if not document_reference.guid:
            document_reference.guid = str(uuid.uuid4())
        topic.document_references.append(document_reference)
        self.edit_topic(topic)

    def add_bim_snippet(self, topic, bim_snippet):
        if topic.bim_snippet:
            self.delete_bim_snippet(topic)
        if os.path.exists(bim_snippet.reference):
            topic_filepath = os.path.join(self.filepath, topic.guid)
            filename = os.path.basename(bim_snippet.reference)
            copyfile(bim_snippet.reference, os.path.join(topic_filepath, filename))
            bim_snippet.reference = filename
            bim_snippet.is_external = False
        else:
            bim_snippet.is_external = True
        topic.bim_snippet = bim_snippet
        self.edit_topic(topic)

    def add_file(self, topic, header_file):
        if os.path.exists(header_file.reference):
            topic_filepath = os.path.join(self.filepath, topic.guid)
            header_file.filename = os.path.basename(header_file.reference)
            copyfile(header_file.reference, os.path.join(topic_filepath, header_file.filename))
            header_file.reference = header_file.filename
            header_file.is_external = False
        header_file.date = datetime.utcnow().isoformat()
        if not topic.header:
            topic.header = bcf.v2.data.Header()
        topic.header.files.append(header_file)
        self.edit_topic(topic)

    def get_comments(self, guid):
        comments = {}
        data = self._read_xml(os.path.join(guid, "markup.bcf"), "markup.xsd")
        if "Comment" not in data:
            return comments
        for item in data["Comment"]:
            comment = bcf.v2.data.Comment()
            mandatory_keys = {"guid": "@Guid", "date": "Date", "author": "Author", "comment": "Comment"}
            for key, value in mandatory_keys.items():
                setattr(comment, key, item[value])
            optional_keys = {"modified_date": "ModifiedDate", "modified_author": "ModifiedAuthor"}
            for key, value in optional_keys.items():
                if value in item:
                    setattr(comment, key, item[value])
            if "Viewpoint" in item:
                viewpoint = bcf.v2.data.Viewpoint()
                viewpoint.guid = item["Viewpoint"]["@Guid"]
                comment.viewpoint = viewpoint
            comments[comment.guid] = comment
        self.topics[guid].comments = comments
        return comments

    def get_viewpoints(self, guid):
        viewpoints = {}
        data = self._read_xml(os.path.join(guid, "markup.bcf"), "markup.xsd")
        if "Viewpoints" not in data:
            return viewpoints
        for item in data["Viewpoints"]:
            viewpoint = self.get_viewpoint(item, guid)
            viewpoints[viewpoint.guid] = viewpoint
        self.topics[guid].viewpoints = viewpoints
        return viewpoints

    def get_viewpoint(self, data, topic_guid):
        viewpoint = bcf.v2.data.Viewpoint()
        viewpoint.guid = data["@Guid"]
        optional_keys = {"viewpoint": "Viewpoint", "snapshot": "Snapshot", "index": "Index"}
        for key, value in optional_keys.items():
            if value in data:
                setattr(viewpoint, key, data[value])
        visinfo = self._read_xml(os.path.join(topic_guid, viewpoint.viewpoint), "visinfo.xsd")
        viewpoint.components = self.get_viewpoint_components(visinfo)
        viewpoint.orthogonal_camera = self.get_viewpoint_orthogonal_camera(visinfo)
        viewpoint.perspective_camera = self.get_viewpoint_perspective_camera(visinfo)
        viewpoint.lines = self.get_viewpoint_lines(visinfo)
        viewpoint.clipping_planes = self.get_viewpoint_clipping_planes(visinfo)
        viewpoint.bitmaps = self.get_viewpoint_bitmaps(visinfo)
        return viewpoint

    def get_viewpoint_components(self, visinfo):
        if "Components" not in visinfo:
            return None
        components = bcf.v2.data.Components()
        data = visinfo["Components"]
        if "ViewSetupHints" in data:
            view_setup_hints = bcf.v2.data.ViewSetupHints()
            optional_keys = {
                "spaces_visible": "@SpacesVisible",
                "space_boundaries_visible": "@SpaceBoundariesVisible",
                "openings_visible": "@OpeningsVisible",
            }
            for key, value in optional_keys.items():
                if value in data["ViewSetupHints"]:
                    setattr(view_setup_hints, key, data["ViewSetupHints"][value])
            components.view_setup_hints = view_setup_hints
        if "Selection" in data and "Component" in data["Selection"]:
            for item in data["Selection"]["Component"]:
                components.selection.append(self.get_component(item))
        if "Visibility" in data:
            component_visibility = bcf.v2.data.ComponentVisibility()
            if "@DefaultVisibility" in data["Visibility"]:
                component_visibility.default_visibility = data["Visibility"]["@DefaultVisibility"]
            if "Exceptions" in data["Visibility"] and "Component" in data["Visibility"]["Exceptions"]:
                for item in data["Visibility"]["Exceptions"]["Component"]:
                    component_visibility.exceptions.append(self.get_component(item))
            components.visibility = component_visibility
        if "Coloring" in data and "Color" in data["Coloring"]:
            for item in data["Coloring"]["Color"]:
                color = bcf.v2.data.Color()
                color.color = item["@Color"]
                for item2 in item["Component"]:
                    color.components.append(self.get_component(item2))
                components.coloring.append(color)
        return components

    def get_viewpoint_orthogonal_camera(self, visinfo):
        if "OrthogonalCamera" not in visinfo:
            return None
        camera = bcf.v2.data.OrthogonalCamera()
        data = visinfo["OrthogonalCamera"]
        self.set_vector(camera.camera_view_point, data["CameraViewPoint"])
        self.set_vector(camera.camera_direction, data["CameraDirection"])
        self.set_vector(camera.camera_up_vector, data["CameraUpVector"])
        camera.view_to_world_scale = data["ViewToWorldScale"]
        return camera

    def get_viewpoint_perspective_camera(self, visinfo):
        if "PerspectiveCamera" not in visinfo:
            return None
        camera = bcf.v2.data.PerspectiveCamera()
        data = visinfo["PerspectiveCamera"]
        self.set_vector(camera.camera_view_point, data["CameraViewPoint"])
        self.set_vector(camera.camera_direction, data["CameraDirection"])
        self.set_vector(camera.camera_up_vector, data["CameraUpVector"])
        camera.field_of_view = data["FieldOfView"]
        return camera

    def get_viewpoint_lines(self, visinfo):
        if "Lines" not in visinfo:
            return []
        lines = []
        for item in visinfo["Lines"]["Line"]:
            line = bcf.v2.data.Line()
            self.set_vector(line.start_point, item["StartPoint"])
            self.set_vector(line.end_point, item["EndPoint"])
            lines.append(line)
        return lines

    def get_viewpoint_clipping_planes(self, visinfo):
        if "ClippingPlanes" not in visinfo:
            return []
        planes = []
        for item in visinfo["ClippingPlanes"]["ClippingPlane"]:
            plane = bcf.v2.data.ClippingPlane()
            self.set_vector(plane.location, item["Location"])
            self.set_vector(plane.direction, item["Direction"])
            planes.append(plane)
        return planes

    def get_viewpoint_bitmaps(self, visinfo):
        if "Bitmap" not in visinfo:
            return []
        bitmaps = []
        for item in visinfo["Bitmap"]:
            bitmap = bcf.v2.data.Bitmap()
            bitmap.reference = item["Reference"]
            bitmap.bitmap_format = item["Bitmap"].upper()
            self.set_vector(bitmap.location, item["Location"])
            self.set_vector(bitmap.normal, item["Normal"])
            self.set_vector(bitmap.up, item["Up"])
            bitmap.height = item["Height"]
            bitmaps.append(bitmap)
        return bitmaps

    def set_vector(self, to_obj, from_xml):
        to_obj.x = from_xml["X"]
        to_obj.y = from_xml["Y"]
        to_obj.z = from_xml["Z"]

    def get_component(self, data):
        component = bcf.v2.data.Component()
        optional_keys = {
            "originating_system": "OriginatingSystem",
            "authoring_tool_id": "AuthoringToolId",
            "ifc_guid": "@IfcGuid",
        }
        for key, value in optional_keys.items():
            if value in data:
                setattr(component, key, data[value])
        return component

    def close_project(self):
        shutil.rmtree(self.filepath)

    def _read_xml(self, filename, xsd):
        schema = XMLSchema(os.path.join(cwd, "xsd", xsd))
        filepath = os.path.join(self.filepath, filename)
        (data, errors) = schema.to_dict(filepath, validation="lax")
        for error in errors:
            self.logger.error(error)
        return data

    def _create_element(self, parent, name, attributes={}, text=None):
        element = self.document.createElement(name)
        for key, value in attributes.items():
            if isinstance(value, bool):
                element.setAttribute(key, str(value).lower())
            elif value:
                element.setAttribute(key, value)
        if text is not None:
            text = self.document.createTextNode(str(text))
            element.appendChild(text)
        parent.appendChild(element)
        return element

    def __del__(self):
        self.close_project()
