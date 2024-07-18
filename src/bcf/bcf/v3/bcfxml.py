"""BCF XML V3 handlers."""
import uuid
import warnings
import zipfile
from pathlib import Path
from typing import Any, NoReturn, Optional, TypeVar

import bcf.v3.model as mdl
from bcf.inmemory_zipfile import InMemoryZipFile, ZipFileInterface
from bcf.v3.document import DocumentsHandler
from bcf.v3.topic import TopicHandler
from bcf.xml_parser import AbstractXmlParserSerializer, XmlParserSerializer

T = TypeVar("T")


class BcfXml:
    """BCF XML handler."""

    def __init__(
        self, filename: Optional[Path] = None, xml_handler: Optional[AbstractXmlParserSerializer] = None
    ) -> None:
        self._filename = filename
        self._xml_handler = xml_handler or XmlParserSerializer()
        self._version: Optional[mdl.Version] = None
        self._project_info: Optional[mdl.ProjectInfo] = None
        self._extensions: Optional[mdl.Extensions] = None
        self._topics: dict[str, TopicHandler] = {}
        self._documents: Optional[DocumentsHandler] = None
        self._zip_file = self._load_zip_file()

    def __enter__(self) -> "BcfXml":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    def __del__(self) -> None:
        self.close()

    def close(self) -> None:
        if self._zip_file:
            self._zip_file.close()

    def _load_zip_file(self) -> Optional[zipfile.ZipFile]:
        return zipfile.ZipFile(self._filename) if self._filename else None

    @property
    def version(self) -> mdl.Version:
        """Bcf Version."""
        if not self._version:
            self._version = (
                self._xml_handler.parse(self._zip_file.read("bcf.version"), mdl.Version)
                if self._zip_file
                else mdl.Version(version_id="3.0")
            )
        return self._version

    @version.setter
    def version(self, value: mdl.Version) -> None:
        self._version = value

    @property
    def project_info(self) -> Optional[mdl.ProjectInfo]:
        """BCF project information."""
        if not self._project_info and self._zip_file and zipfile.Path(self._zip_file, "project.bcfp").exists():
            self._project_info = self._xml_handler.parse(self._zip_file.read("project.bcfp"), mdl.ProjectInfo)
        return self._project_info

    @project_info.setter
    def project_info(self, value: Optional[mdl.ProjectInfo]) -> None:
        self._project_info = value

    @property
    def project(self) -> Optional[mdl.Project]:
        """BCF project."""
        return self.project_info.project if self.project_info else None

    @property
    def extensions(self) -> Optional[mdl.Extensions]:
        """BCF extensions."""
        if not self._extensions and self._zip_file:
            self._extensions = self._xml_handler.parse(self._zip_file.read("extensions.xml"), mdl.Extensions)
        return self._extensions

    @extensions.setter
    def extensions(self, value: Optional[mdl.Extensions]) -> None:
        self._extensions = value

    @property
    def topics(self) -> dict[str, TopicHandler]:
        """BCF topics."""
        if not self._topics and self._zip_file:
            self._load_topics()
        return self._topics

    def _load_topics(self) -> None:
        for topic_dir in zipfile.Path(self._zip_file).iterdir():
            if not topic_dir.is_dir():
                continue
            markup_path = topic_dir.joinpath("markup.bcf")
            if not markup_path.exists():
                continue
            self._topics[topic_dir.name] = TopicHandler(topic_dir, self._xml_handler)

    @property
    def documents(self) -> Optional[DocumentsHandler]:
        """Documents stored in the BCF file."""
        if not self._documents and self._zip_file:
            self._documents = DocumentsHandler.load(self._zip_file, self._xml_handler)
        return self._documents

    @classmethod
    def load(cls, filename: Path, xml_handler: Optional[AbstractXmlParserSerializer] = None) -> Optional["BcfXml"]:
        """
        Create a BcfXml object from a file.

        Args:
            filename: Path to the file.
            xml_handler: XML parser and serializer.

        Returns:
            A BcfXml object with the file contents.

        Raises:
            ValueError: If the file name is null or empty
        """
        if not filename:
            raise ValueError("filename is required")
        xml_handler = xml_handler or XmlParserSerializer()
        return cls(xml_handler=xml_handler, filename=filename)

    @classmethod
    def create_new(
        cls,
        project_name: Optional[str] = None,
        extensions: Optional[mdl.Extensions] = None,
        xml_handler: Optional[AbstractXmlParserSerializer] = None,
    ) -> "BcfXml":
        """
        Create a new BcfXml object.

        Args:
            project_name: The name of the project.
            extensions: The Extension XML object. Defaults to an empty one.
            xml_handler: XML parser and serializer.

        Returns:
            A new BcfXml object.
        """
        instance = cls(xml_handler=xml_handler or XmlParserSerializer())
        instance.project_info = mdl.ProjectInfo(project=mdl.Project(name=project_name, project_id=str(uuid.uuid4())))
        instance.extensions = extensions or mdl.Extensions()
        return instance

    def save(self, filename: Optional[Path] = None, keep_open: bool = False) -> None:
        """Save the BCF file to the given filename."""
        if not filename and not self._filename:
            raise ValueError("No file name specified, cannot save BCF file.")
        if filename:
            self._filename = filename
        with InMemoryZipFile(self._filename) as bcf_zip:
            self._save_project(bcf_zip)
            self._save_version(bcf_zip)
            self._save_extensions(bcf_zip)
            self._save_documents(bcf_zip)
            self._save_topics(bcf_zip)
        if keep_open:
            self._zip_file = self._load_zip_file()

    def _save_project(self, destination_zip: ZipFileInterface) -> None:
        self._smart_save_xml(destination_zip, self._project_info, "project.bcfp")

    def _save_version(self, destination_zip: ZipFileInterface) -> None:
        if not self._version and self._zip_file:
            destination_zip.writestr("bcf.version", self._zip_file.read("bcf.version"))
        else:
            self._save_xml(destination_zip, "bcf.version", self.version)

    def _save_extensions(self, destination_zip: ZipFileInterface) -> None:
        self._smart_save_xml(destination_zip, self._extensions, "extensions.xml")

    def _smart_save_xml(self, destination_zip: ZipFileInterface, item: Any, target: str) -> None:
        if item:
            self._save_xml(destination_zip, target, item)
        elif self._zip_file and zipfile.Path(self._zip_file, target).exists():
            destination_zip.writestr(target, self._zip_file.read(target))

    def _save_xml(self, destination_zip: ZipFileInterface, inner_file: str, xml_obj: Any) -> None:
        destination_zip.writestr(inner_file, self._xml_handler.serialize(xml_obj))

    def _save_documents(self, bcf_zip: ZipFileInterface) -> None:
        if self.documents:
            self.documents.save(bcf_zip)

    def _save_topics(self, destination_zip: ZipFileInterface) -> None:
        for topic_handler in self.topics.values():
            topic_handler.save(destination_zip)

    def add_topic(
        self, title: str, description: str, author: str, topic_type: str = "", topic_status: str = ""
    ) -> TopicHandler:
        """
        Add a new topic to the BCF.

        Args:
            title: The title of the topic.
            description: The description of the topic.
            author: The author of the topic.
            topic_type: The type of the topic.
            topic_status: The status of the topic.

        Returns:
            The newly created topic wrapped inside a TopicHandler object.
        """
        topic_handler = TopicHandler.create_new(
            title,
            description,
            author,
            topic_type=topic_type,
            topic_status=topic_status,
            xml_handler=self._xml_handler,
        )
        self.topics[topic_handler.guid] = topic_handler
        return topic_handler

    def __eq__(self, other: object) -> bool | NoReturn:
        return (
            self.version == other.version
            and self.project_info == other.project_info
            and self.extensions == other.extensions
            if isinstance(other, BcfXml)
            else NotImplemented
        )

    # region Deprecated methods
    def new_project(self) -> "BcfXml":
        """Deprecated method."""
        warnings.warn("new_project is deprecated, use create_new instead.", DeprecationWarning)
        return self.create_new()

    def get_project(self, _filepath: Optional[str] = None) -> Optional[mdl.Project]:
        """Deprecated method."""
        warnings.warn("get_project is deprecated, use project_info.project instead.", DeprecationWarning)
        return self.project

    def edit_project(self) -> None:
        """Deprecated method."""
        warnings.warn("edit_project is deprecated, there's no need to use it.", DeprecationWarning)

    def save_project(self, filepath: Path) -> None:
        """Deprecated method."""
        warnings.warn("save_project is deprecated, use save instead.", DeprecationWarning)
        self.save(filepath)

    def get_version(self) -> str:
        warnings.warn("get_version is deprecated, use version.version_id instead.", DeprecationWarning)
        return self.version.version_id

    def edit_version(self) -> None:
        """Deprecated method."""
        warnings.warn("edit_version is deprecated, there's no need to use it.", DeprecationWarning)

    def get_topics(self) -> dict[str, TopicHandler]:
        """Deprecated method."""
        warnings.warn("get_topics is deprecated, use topics instead.", DeprecationWarning)
        return self.topics

    def get_topic(self, guid: str) -> TopicHandler:
        """Return a topic by its GUID."""
        warnings.warn("get_topic is deprecated, use topics[guid] instead", DeprecationWarning)
        return self.topics[guid]

    def get_header(self, guid: str) -> Optional[mdl.Header]:
        """Return the header of a Topic by its GUID."""
        return self.topics[guid].header

    def edit_topic(self) -> None:
        """Deprecated method."""
        warnings.warn("edit_topic is deprecated, there's no need to use it.", DeprecationWarning)

    def add_comment(self, _topic: mdl.Topic, _comment: Optional[mdl.Comment] = None) -> None:
        """Deprecated method."""
        warnings.warn("add_comment is deprecated, use topics methods instead.", DeprecationWarning)

    def edit_comment(self) -> None:
        """Deprecated method."""
        warnings.warn("edit_comment is deprecated, there's no need to use it.", DeprecationWarning)

    # TODO: deprecate other methods
    # endregion
