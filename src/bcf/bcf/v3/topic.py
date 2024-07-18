"""BCF XML V3 Topic handler."""
import datetime
import uuid
import zipfile
from pathlib import Path
from typing import Any, NoReturn, Optional

import numpy as np
from ifcopenshell import entity_instance
from numpy.typing import NDArray
from xsdata.models.datatype import XmlDateTime

import bcf.v3.model as mdl
from bcf.inmemory_zipfile import ZipFileInterface
from bcf.v3.visinfo import VisualizationInfoHandler
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
        self._bim_snippet: Optional[bytes] = None
        self._xml_handler = xml_handler or XmlParserSerializer()
        self._topic_dir = topic_dir

    @property
    def markup(self) -> Optional[mdl.Markup]:
        if not self._markup and self._topic_dir:
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
    def guid(self) -> Optional[str]:
        """Return the GUID of the topic."""
        if self._markup:
            return self.topic.guid
        return self._topic_dir.name if self._topic_dir else None

    @property
    def header(self) -> Optional[mdl.Header]:
        """Return the header of the topic."""
        return self.markup.header

    @property
    def comments(self) -> list[mdl.Comment]:
        """Return the comments of the topic."""
        return self.topic.comments.comment if self.topic.comments else []

    @property
    def bim_snippet(self) -> Optional[bytes]:
        if not self._bim_snippet and self._topic_dir:
            self._bim_snippet = self._load_bim_snippet()
        return self._bim_snippet

    @bim_snippet.setter
    def bim_snippet(self, value: bytes) -> None:
        self._bim_snippet = value

    @property
    def viewpoints(self) -> dict[str, "VisualizationInfoHandler"]:
        if (
            not self._viewpoints
            and self._topic_dir
            and self.topic.viewpoints
            and (viewpoints := self.topic.viewpoints.view_point)
        ):
            self._viewpoints = VisualizationInfoHandler.from_topic_viewpoints(self._topic_dir, viewpoints)
        return self._viewpoints

    def _load_bim_snippet(self) -> Optional[bytes]:
        bim_snippet_obj = self.topic.bim_snippet
        if bim_snippet_obj and not bim_snippet_obj.is_external and self._topic_dir:
            bim_snippet_path = self._topic_dir.joinpath(bim_snippet_obj.reference)
            if bim_snippet_path.exists():
                return bim_snippet_path.read_bytes()
        return None

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

    def _save_viewpoints(self, destination_zip: ZipFileInterface, topic_dir: str) -> None:
        if not self.topic.viewpoints or not (viewpoints := self.topic.viewpoints.view_point):
            return
        for vpt in viewpoints:
            if vpt.viewpoint:
                self.viewpoints[vpt.viewpoint].save(destination_zip, topic_dir, vpt)

    def _save_xml(self, destination_zip: ZipFileInterface, item: Any, target: str) -> None:
        to_write = self._xml_handler.serialize(item) if item else self._topic_dir.joinpath(target).read_bytes()
        destination_zip.writestr(f"{self._topic_dir.name}/{target}", to_write)

    def _save_bim_snippet(self, destination_zip: ZipFileInterface) -> None:
        snippet = self.topic.bim_snippet
        if not snippet or snippet.is_external:
            return
        ref_filename = Path(snippet.reference).name
        if self.bim_snippet:
            destination_zip.writestr(f"{self.topic.guid}/{ref_filename}", self.bim_snippet)

    def add_viewpoint(self, element: entity_instance) -> None:
        """
        Add a viewpoint tergeting an IFC element to the topic.

        Args:
            element: The IFC element.
        """
        new_viewpoint = VisualizationInfoHandler.create_new(element, self._xml_handler)
        self.add_visinfo_handler(new_viewpoint)

    def add_viewpoint_from_point_and_guids(self, position: NDArray[np.float_], *guids: str) -> None:
        """
        Add a viewpoint tergeting an IFC element to the topic.

        Args:
            element: The IFC element.
        """
        vi_handler = VisualizationInfoHandler.create_from_point_and_guids(
            position, *guids, xml_handler=self._xml_handler
        )
        self.add_visinfo_handler(vi_handler)

    def add_visinfo_handler(self, new_viewpoint: VisualizationInfoHandler) -> None:
        self.viewpoints[new_viewpoint.guid + ".bcfv"] = new_viewpoint
        if self.topic.viewpoints is None:
            self.topic.viewpoints = mdl.TopicViewpoints()
        self.topic.viewpoints.view_point.append(
            mdl.ViewPoint(viewpoint=new_viewpoint.guid + ".bcfv", guid=new_viewpoint.guid)
        )

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
