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
