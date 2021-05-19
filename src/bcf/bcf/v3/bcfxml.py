import os
import uuid
import shutil
import zipfile
import logging
import tempfile
import bcf.v3.data
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
        self.project = bcf.v3.data.Project()
        self.version = "3.0"
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
        if os.path.isfile(os.path.join(self.filepath, "project.bcfp")):
            data = self._read_xml("project.bcfp", "project.xsd")
            self.project.project_id = data["Project"]["@ProjectId"]
            self.project.name = data["Project"].get("Name")
        return self.project

    def edit_project(self):
        self.document = minidom.Document()
        root = self._create_element(self.document, "ProjectInfo")
        project = self._create_element(root, "Project", {"ProjectId": self.project.project_id})
        if self.project.name:
            self._create_element(project, "Name", text=self.project.name)
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
            self.topics[subdir] = self.get_topic(subdir)
        return self.topics

    def get_header(self, guid):
        data = self._read_xml(os.path.join(guid, "markup.bcf"), "markup.xsd")
        if "Header" not in data:
            return
        header = bcf.v3.data.Header()
        for item in data["Header"]["Files"]["File"]:
            header_file = bcf.v3.data.HeaderFile()
            optional_keys = {
                "filename": "Filename",
                "date": "Date",
                "reference": "Reference",
                "ifc_project": "@IfcProject",
                "ifc_spatial_structure_element": "@IfcSpatialStructureElement",
                "is_external": "@IsExternal",
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
        topic = bcf.v3.data.Topic()
        self.topics[guid] = topic

        mandatory_keys = {
            "guid": "@Guid",
            "title": "Title",
            "creation_date": "CreationDate",
            "creation_author": "CreationAuthor",
            "topic_status": "@TopicStatus",
            "topic_type": "@TopicType",
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
            "server_assigned_id": "@ServerAssignedId",
        }
        for key, value in optional_keys.items():
            if value in data["Topic"]:
                setattr(topic, key, data["Topic"][value])

        if "BimSnippet" in data["Topic"]:
            bim_snippet = bcf.v3.data.BimSnippet()
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

        for item in data["Topic"]["DocumentReferences"]["DocumentReference"]:
            document_reference = bcf.v3.data.DocumentReference()
            keys = {
                "document_guid": "DocumentGuid",
                "url": "Url",
                "guid": "@Guid",
                "description": "Description",
            }
            for key, value in keys.items():
                if value in item:
                    setattr(document_reference, key, item[value])
            topic.document_references.append(document_reference)

        for item in data["Topic"]["RelatedTopics"]["RelatedTopic"]:
            related_topic = bcf.v3.data.RelatedTopic()
            related_topic.guid = item["@Guid"]
            topic.related_topics.append(related_topic)
        return topic

    def add_topic(self, topic=None):
        if topic is None:
            topic = bcf.v3.data.Topic()
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
        if topic.header:
            self.write_header(topic.header, root)

        topic_el = self._create_element(
            root,
            "Topic",
            {
                "Guid": topic.guid,
                "ServerAssignedId": topic.server_assigned_id,
                "TopicType": topic.topic_type,
                "TopicStatus": topic.topic_status,
            },
        )
        if topic.reference_links:
            reference_Links_el = self._create_element(topic_el, "ReferenceLinks")
            for reference_link in topic.reference_links:
                self._create_element(reference_Links_el, "ReferenceLink", text=reference_link)

        text_map = {
            "Title": topic.title,
            "Priority": topic.priority,
            "Index": topic.index,
        }
        for key, value in text_map.items():
            if value:
                self._create_element(topic_el, key, text=value)
        if topic.labels:
            label_el = self._create_element(topic_el, "Labels")
            for label in topic.labels:
                self._create_element(label_el, "Label", text=label)

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
                {
                    "SnippetType": topic.bim_snippet.snippet_type,
                    "IsExternal": topic.bim_snippet.is_external,
                },
            )
            self._create_element(bim_snippet, "Reference", text=topic.bim_snippet.reference)
            self._create_element(
                bim_snippet,
                "ReferenceSchema",
                text=topic.bim_snippet.reference_schema,
            )
        if topic.document_references:
            reference_el = self._create_element(topic_el, "DocumentReferences")
            self.write_document_references(topic.document_references, reference_el)
        if topic.related_topics:
            related_topic_el = self._create_element(topic_el, "RelatedTopics")
            for related_topic in topic.related_topics:
                self._create_element(related_topic_el, "RelatedTopic", {"Guid": related_topic.guid})
        if topic.comments:
            comment_el = self._create_element(topic_el, "Comments")
            self.write_comments(topic.comments, comment_el)
        if topic.viewpoints:
            viewpoint_el = self._create_element(topic_el, "Viewpoints")
            self.write_viewpoints(topic.viewpoints, viewpoint_el, topic)
        with open(os.path.join(self.filepath, topic.guid, "markup.bcf"), "wb") as f:
            f.write(self.document.toprettyxml(encoding="utf-8"))

    def write_document_references(self, reference, root):

        for refer in reference:
            document_reference_el = self._create_element(root, "DocumentReference", {"Guid": refer.guid})
            if refer.document_guid:
                self._create_element(document_reference_el, "DocumentGuid", text=refer.document_guid)
            if refer.url:
                self._create_element(document_reference_el, "Url", text=refer.url)
            if refer.description:
                self._create_element(document_reference_el, "Description", text=refer.description)

    def write_header(self, header, root):
        if not header or not header.files:
            return
        header_el = self._create_element(root, "Header")
        files_el = self._create_element(header_el, "Files")
        for f in header.files:
            file_el = self._create_element(
                files_el,
                "File",
                {
                    "IfcProject": f.ifc_project,
                    "IfcSpatialStructureElement": f.ifc_spatial_structure_element,
                    "IsExternal": f.is_external,
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
            comment = bcf.v3.data.Comment()
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
            viewpoint_el = self._create_element(root, "ViewPoint", {"Guid": viewpoint.guid})
            text_map = {
                "Viewpoint": viewpoint.viewpoint,
                "Snapshot": viewpoint.snapshot,
                "Index": viewpoint.index,
            }
            for key, value in text_map.items():
                if value:
                    self._create_element(viewpoint_el, key, text=value)
            self.write_viewpoint(viewpoint, topic)

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
