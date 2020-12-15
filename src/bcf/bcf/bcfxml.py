import os
import tempfile
import shutil
import zipfile
import logging
import bcf.data
from xmlschema import XMLSchema
from contextlib import contextmanager


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
        self.project = bcf.data.Project()
        self.topics = {}

    def get_project(self, filepath=None):
        if not filepath:
            return self.project
        zip_file = zipfile.ZipFile(filepath)
        self.filepath = tempfile.mkdtemp()
        zip_file.extractall(self.filepath)
        data = self._read_xml("project.bcfp", "project.xsd")
        self.project.project_id = data["Project"]["@ProjectId"]
        self.project.name = data["Project"]["Name"]
        return self.project

    def edit_project(self):
        pass

    def save_project(self, filepath):
        with cd(self.filepath):
            zip_file = zipfile.ZipFile(filepath, "w", zipfile.ZIP_DEFLATED)
            for root, dirs, files in os.walk("./"):
                for file in files:
                    zip_file.write(os.path.join(root, file))
            zip_file.close()

    def get_version(self):
        data = self._read_xml("bcf.version", "version.xsd")
        return data["@VersionId"]

    def get_topics(self):
        self.topics = {}
        topics = []
        subdirs = []
        for (dirpath, dirnames, filenames) in os.walk(self.filepath):
            subdirs = dirnames
            break
        for subdir in subdirs:
            self.topics[subdir] = self.get_topic(subdir)
        return self.topics

    def get_topic(self, guid):
        if guid in self.topics:
            return self.topics[guid]
        data = self._read_xml(os.path.join(guid, "markup.bcf"), "markup.xsd")
        topic = bcf.data.Topic()
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
            "modified_date": "ModifiedDate",
            "modified_author": "ModifiedAuthor",
            "due_date": "DueDate",
            "assigned_to": "AssignedTo",
            "stage": "Stage",
            "description": "Description",
            "topic_status": "TopicStatus",
            "topic_type": "TopicType",
        }
        for key, value in optional_keys.items():
            if value in data["Topic"]:
                setattr(topic, key, data["Topic"][value])

        if "BimSnippet" in data["Topic"]:
            bim_snippet = bcf.data.BimSnippet()
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
                document_reference = bcf.data.DocumentReference()
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
                related_topic = bcf.data.RelatedTopic()
                related_topic.guid = item["@Guid"]
                topic.related_topics.append(related_topic)
        return topic

    def get_header(self, guid):
        data = self._read_xml(os.path.join(guid, "markup.bcf"), "markup.xsd")

    def get_comments(self, guid):
        comments = []
        data = self._read_xml(os.path.join(guid, "markup.bcf"), "markup.xsd")
        if "Comment" not in data:
            return comments
        for item in data["Comment"]:
            comment = bcf.data.Comment()
            mandatory_keys = {"guid": "@Guid", "date": "Date", "author": "Author", "comment": "Comment"}
            for key, value in mandatory_keys.items():
                setattr(comment, key, item[value])
            optional_keys = {"modified_date": "ModifiedDate", "modified_author": "ModifiedAuthor"}
            for key, value in optional_keys.items():
                if value in item:
                    setattr(comment, key, item[value])
            if "Viewpoint" in item:
                viewpoint = bcf.data.Viewpoint()
                viewpoint.guid = item["Viewpoint"]["@Guid"]
                comment.viewpoint = viewpoint
            comments.append(comment)
        return comments

    def get_viewpoints(self, guid):
        viewpoints = []
        data = self._read_xml(os.path.join(guid, "markup.bcf"), "markup.xsd")
        if "Viewpoints" not in data:
            return viewpoints
        for item in data["Viewpoints"]:
            viewpoints.append(self.get_viewpoint(item, guid))
        return viewpoints

    def get_viewpoint(self, data, topic_guid):
        viewpoint = bcf.data.Viewpoint()
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
        components = bcf.data.Components()
        data = visinfo["Components"]
        if "ViewSetupHints" in data:
            view_setup_hints = bcf.data.ViewSetupHints()
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
            component_visibility = bcf.data.ComponentVisibility()
            if "@DefaultVisibility" in data["Visibility"]:
                component_visibility.default_visibility = data["Visibility"]["@DefaultVisibility"]
            if "Exceptions" in data["Visibility"] and "Component" in data["Visibility"]["Exceptions"]:
                for item in data["Visibility"]["Exceptions"]["Component"]:
                    component_visibility.exceptions.append(self.get_component(item))
            components.visibility = component_visibility
        if "Coloring" in data and "Color" in data["Coloring"]:
            for item in data["Coloring"]["Color"]:
                color = bcf.data.Color()
                color.color = item["@Color"]
                for item2 in item["Component"]:
                    color.components.append(self.get_component(item2))
                components.coloring.append(color)
        return components

    def get_viewpoint_orthogonal_camera(self, visinfo):
        if "OrthogonalCamera" not in visinfo:
            return None
        camera = bcf.data.OrthogonalCamera()
        data = visinfo["OrthogonalCamera"]
        self.set_vector(camera.camera_view_point, data["CameraViewPoint"])
        self.set_vector(camera.camera_direction, data["CameraDirection"])
        self.set_vector(camera.camera_up_vector, data["CameraUpVector"])
        camera.view_to_world_scale = data["ViewToWorldScale"]

    def get_viewpoint_perspective_camera(self, visinfo):
        if "PerspectiveCamera" not in visinfo:
            return None
        camera = bcf.data.PerspectiveCamera()
        data = visinfo["PerspectiveCamera"]
        self.set_vector(camera.camera_view_point, data["CameraViewPoint"])
        self.set_vector(camera.camera_direction, data["CameraDirection"])
        self.set_vector(camera.camera_up_vector, data["CameraUpVector"])
        camera.field_of_view = data["FieldOfView"]

    def get_viewpoint_lines(self, visinfo):
        if "Lines" not in visinfo:
            return []
        lines = []
        for item in visinfo["Lines"]["Line"]:
            line = bcf.data.Line()
            self.set_vector(line.start_point, item["StartPoint"])
            self.set_vector(line.end_point, item["EndPoint"])
            lines.append(line)
        return lines

    def get_viewpoint_clipping_planes(self, visinfo):
        if "ClippingPlanes" not in visinfo:
            return []
        planes = []
        for item in visinfo["ClippingPlanes"]["ClippingPlane"]:
            plane = bcf.data.ClippingPlane()
            self.set_vector(plane.location, item["Location"])
            self.set_vector(plane.direction, item["Direction"])
            planes.append(plane)
        return planes

    def get_viewpoint_bitmaps(self, visinfo):
        if "Bitmap" not in visinfo:
            return []
        bitmaps = []
        for item in visinfo["Bitmap"]:
            bitmap = bcf.data.Bitmap()
            bitmap.reference = item["Reference"]
            bitmap.bitmap_type = item["Bitmap"].lower()
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
        component = bcf.data.Component()
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

    def __del__(self):
        self.close_project()
