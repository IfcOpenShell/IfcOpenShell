"""BCF XML V2 Topic handler."""
import datetime
import tempfile
import uuid
import zipfile
from pathlib import Path
from typing import Any, NoReturn, Optional

import numpy as np
from ifcopenshell import entity_instance
from numpy.typing import NDArray
from xsdata.models.datatype import XmlDateTime

import bcf.v2.model as mdl
from bcf.inmemory_zipfile import ZipFileInterface
from bcf.v2.visinfo import VisualizationInfoHandler
from bcf.xml_parser import AbstractXmlParserSerializer, XmlParserSerializer


class TopicHandler:
    """BCF Topic and related objects handler."""

    def __init__(
        self,
        topic_dir: Optional[zipfile.Path] = None,
        xml_handler: Optional[AbstractXmlParserSerializer] = None,
    ) -> None:
        self._markup: Optional[mdl.Markup] = None
        self._viewpoints: dict[str, VisualizationInfoHandler] = {}
        self._reference_files: dict[str, bytes] = {}
        self._document_references: dict[str, bytes] = {}
        self._bim_snippet: Optional[bytes] = None
        self._xml_handler = xml_handler or XmlParserSerializer()
        self._topic_dir = topic_dir

    @property
    def markup(self) -> Optional[mdl.Markup]:
        if not self._markup:
            markup_path = self._topic_dir.joinpath("markup.bcf")
            if markup_path.exists():
                self._markup = self._xml_handler.parse(markup_path.read_bytes(), mdl.Markup)
        return self._markup

    @markup.setter
    def markup(self, value: mdl.Markup) -> None:
        self._markup = value

    @property
    def topic(self) -> mdl.Topic:
        """Return the Topic object."""
        return self.markup.topic

    @property
    def guid(self) -> str:
        """Return the GUID of the topic."""
        if self._markup:
            return self.topic.guid
        return self._topic_dir.name if self._topic_dir else ""

    @property
    def header(self) -> Optional[mdl.Header]:
        """Return the header of the topic."""
        return self.markup.header if self.markup else None

    @property
    def comments(self) -> list[mdl.Comment]:
        """Return the comments of the topic."""
        return self.markup.comment if self.markup else []

    @property
    def bim_snippet(self) -> Optional[bytes]:
        if not self._bim_snippet and self._topic_dir:
            self._bim_snippet = self._load_bim_snippet()
        return self._bim_snippet

    @bim_snippet.setter
    def bim_snippet(self, value: bytes) -> None:
        self._bim_snippet = value

    @property
    def viewpoints(self) -> dict[str, VisualizationInfoHandler]:
        if not self._viewpoints and self._topic_dir:
            self._viewpoints = self._load_viewpoints()
        return self._viewpoints

    @property
    def reference_files(self) -> dict[str, bytes]:
        if self._reference_files or not self.header:
            return self._reference_files
        for ref in self.header.file:
            if ref.is_external:
                continue
            real_path = self._topic_dir
            for path_part in ref.reference.split("/"):
                real_path = real_path.parent if path_part == ".." else real_path.joinpath(path_part)
            self._reference_files[ref.reference] = real_path.read_bytes()
        return self._reference_files

    @property
    def document_references(self) -> dict[str, bytes]:
        if self._document_references or not self.topic:
            return self._document_references
        for doc in self.topic.document_reference:
            if doc.is_external or not doc.referenced_document:
                continue
            real_path = self._topic_dir
            for path_part in doc.referenced_document.split("/"):
                real_path = real_path.parent if path_part == ".." else real_path.joinpath(path_part)
            self._document_references[doc.referenced_document] = real_path.read_bytes()
        return self._document_references

    def _load_bim_snippet(self) -> Optional[bytes]:
        bim_snippet_obj = self.topic.bim_snippet
        if bim_snippet_obj and not bim_snippet_obj.is_external:
            bim_snippet_path = self._topic_dir.joinpath(bim_snippet_obj.reference)
            if bim_snippet_path.exists():
                return bim_snippet_path.read_bytes()
        return None

    def _load_viewpoints(self) -> dict[str, VisualizationInfoHandler]:
        if self.markup and (viewpoints := self.markup.viewpoints):
            return VisualizationInfoHandler.from_topic_viewpoints(self._topic_dir, viewpoints)
        return {}

    @classmethod
    def create_new(
        cls,
        title: str,
        description: str,
        author: str,
        topic_type: str = "",
        topic_status: str = "",
        xml_handler: Optional[AbstractXmlParserSerializer] = None,
    ) -> "TopicHandler":
        """
        Create a new BCF topic.

        Args:
            title: The title of the topic.
            description: The description of the topic.
            author: The author of the topic.
            topic_type: The type of the topic.
            topic_status: The status of the topic.
            xml_handler: The XML parser/serializer to use.

        Returns:
            The BCF topic definition.
        """
        creation_date = XmlDateTime.from_datetime(datetime.datetime.now())
        guid = str(uuid.uuid4())
        topic = mdl.Topic(
            title=title,
            description=description,
            creation_author=author,
            creation_date=creation_date,
            guid=guid,
            topic_type=topic_type,
            topic_status=topic_status,
        )
        markup = mdl.Markup(topic=topic)
        obj = cls(topic_dir=Path(guid), xml_handler=xml_handler or XmlParserSerializer())
        obj.markup = markup
        return obj

    def save(self, destination_zip: ZipFileInterface) -> None:
        """
        Save the topic to a BCF zip file.

        Args:
            bcf_zip: The BCF zip file to save to.
        """
        topic_dir = self.guid
        self._save_xml(destination_zip, self._markup, "markup.bcf")
        self._save_viewpoints(destination_zip, topic_dir)
        self._save_bim_snippet(destination_zip)
        self._save_reference_files(destination_zip)
        self._save_document_references(destination_zip)

    def _save_viewpoints(self, destination_zip: ZipFileInterface, topic_dir: str) -> None:
        if not self.markup or not (viewpoints := self.markup.viewpoints):
            return
        for vpt in viewpoints:
            if vpt.viewpoint:
                self.viewpoints[vpt.viewpoint].save(destination_zip, topic_dir, vpt)

    def _save_xml(self, destination_zip: ZipFileInterface, item: Any, target: str) -> None:
        if self._topic_dir is None:
            return
        to_write = self._xml_handler.serialize(item) if item else self._topic_dir.joinpath(target).read_bytes()
        destination_zip.writestr(f"{self._topic_dir.name}/{target}", to_write)

    def _save_bim_snippet(self, destination_zip: ZipFileInterface) -> None:
        snippet = self.topic.bim_snippet
        if not snippet or snippet.is_external:
            return
        ref_filename = Path(snippet.reference).name
        if self.bim_snippet:
            destination_zip.writestr(f"{self.topic.guid}/{ref_filename}", self.bim_snippet)

    def _save_reference_files(self, destination_zip: ZipFileInterface) -> None:
        if not self.header:
            return
        for ref in self.header.file:
            if ref.is_external or not ref.reference:
                continue
            real_path = self._topic_dir
            for path_part in ref.reference.split("/"):
                real_path = real_path.parent if path_part == ".." else real_path.joinpath(path_part)
            destination_zip.writestr(real_path.at, self.reference_files[ref.reference])

    def _save_document_references(self, destination_zip: ZipFileInterface) -> None:
        if not self.topic:
            return
        for doc in self.topic.document_reference:
            if doc.is_external or not doc.referenced_document:
                continue
            real_path = self._topic_dir
            for path_part in doc.referenced_document.split("/"):
                real_path = real_path.parent if path_part == ".." else real_path.joinpath(path_part)
            destination_zip.writestr(real_path.at, self.document_references[doc.referenced_document])

    def extract_file(self, entity, outfile: Optional[Path] = None) -> Path:
        """Extracts an element with a file into a temporary directory

        These include header files, bim snippets, document references, and
        viewpoint bitmaps. External reference are not downloaded. Instead, the
        URI reference is returned.

        :param entity: The entity with a file reference to extract
        :type entity: bcf.v2.model.HeaderFile,bcf.v2.model.BimSnippet,bcf.v2.model.TopicDocumentReference
        :param outfile: If provided, save the header file to that location.
            Otherwise, a temporary directory is created and the filename is
            derived from the header's original filename.
        :type outfile: pathlib.Path,optional
        :return: The filepath of the extracted file. It may be a URL if the
            header file is external.
        :rtype: Path
        """
        if hasattr(entity, "reference"):
            reference = entity.reference
        else:
            reference = entity.referenced_document

        if not reference:
            return

        if getattr(entity, "is_external", False):
            return entity.reference

        resolved_reference = self._topic_dir

        for part in Path(reference).parts:
            if part == "..":
                resolved_reference = resolved_reference.parent
            else:
                resolved_reference = resolved_reference.joinpath(part)

        if not outfile:
            if getattr(entity, "filename", None):
                filename = entity.filename
            else:
                filename = resolved_reference.name
            outfile = Path(tempfile.mkdtemp()) / filename

        with open(outfile, "wb") as f:
            f.write(resolved_reference.read_bytes())

        return outfile

    def add_viewpoint(self, element: entity_instance) -> None:
        """Add a viewpoint pointed at the placement of an IFC element to the topic.

        Args:
            element: The IFC element.
        """
        new_viewpoint = VisualizationInfoHandler.create_new(element, self._xml_handler)
        self.add_visinfo_handler(new_viewpoint)
        return new_viewpoint

    def add_viewpoint_from_point_and_guids(self, position: NDArray[np.float_], *guids: str) -> None:
        """Add a viewpoint pointing at an XYZ point in space

        Args:
            position: the XYZ point in space
            guids: one or more element GlobalIds.
        """
        vi_handler = VisualizationInfoHandler.create_from_point_and_guids(
            position, *guids, xml_handler=self._xml_handler
        )
        self.add_visinfo_handler(vi_handler)
        return vi_handler

    def add_visinfo_handler(self, new_viewpoint: VisualizationInfoHandler) -> None:
        self.viewpoints[new_viewpoint.guid + ".bcfv"] = new_viewpoint
        self.markup.viewpoints.append(mdl.ViewPoint(viewpoint=new_viewpoint.guid + ".bcfv", guid=new_viewpoint.guid))

    def __eq__(self, other: object) -> bool | NoReturn:
        return (
            (
                self.markup == other.markup
                and self.viewpoints == other.viewpoints
                and self.bim_snippet == other.bim_snippet
            )
            if isinstance(other, TopicHandler)
            else NotImplemented
        )
