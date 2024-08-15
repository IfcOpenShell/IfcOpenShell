# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
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

import bcf.agnostic.visinfo
import bcf.v2.visinfo
import bonsai.core.tool
import bonsai.tool as tool
import bpy
import bcf.v2.model
import bcf.v2.topic
import bcf.v3.model
import bcf.v3.topic
import bcf.agnostic.topic
from typing import Any, Union, TypeVar, TypeGuard


T = TypeVar("T")


class Bcf(bonsai.core.tool.Bcf):
    @classmethod
    def get_path(cls) -> str:
        return bpy.context.scene.BCFProperties.bcf_file

    @classmethod
    def is_list_of(cls, a: list[Any], t: type[T]) -> TypeGuard[list[T]]:
        """Narrow type for a list assuming list is not mixing types."""
        if not a:
            return True
        return isinstance(a[0], t)

    # BCF version agnostic API.
    ## topic
    @classmethod
    def get_topic_document_references(
        cls, topic: bcf.agnostic.topic.TopicHandler
    ) -> Union[list[bcf.v2.model.TopicDocumentReference], list[bcf.v3.model.DocumentReference]]:
        if isinstance(topic, bcf.v2.topic.TopicHandler):
            document_references = topic.topic.document_reference
        else:
            document_references = topic.topic.document_references
            document_references = document_references.document_reference if document_references else []
        return document_references

    @classmethod
    def set_topic_document_references(
        cls,
        topic: bcf.agnostic.topic.TopicHandler,
        document_references: Union[list[bcf.v2.model.TopicDocumentReference], list[bcf.v3.model.DocumentReference]],
    ) -> None:
        topic_ = topic.topic
        if isinstance(topic_, bcf.v2.model.Topic):
            assert cls.is_list_of(document_references, bcf.v2.model.TopicDocumentReference)
            topic_.document_reference = document_references
        else:
            assert cls.is_list_of(document_references, bcf.v3.model.DocumentReference)
            topic_document_references = topic_.document_references
            if topic_document_references is None:
                if not document_references:
                    return
                topic_.document_references = (topic_document_references := bcf.v3.model.TopicDocumentReferences())
                return
            topic_document_references.document_reference = document_references

    @classmethod
    def get_topic_header_files(
        cls, topic: bcf.agnostic.topic.TopicHandler
    ) -> Union[list[bcf.v2.model.HeaderFile], list[bcf.v3.model.File]]:
        header = topic.header
        if not header:
            return []
        if isinstance(header, bcf.v2.model.Header):
            header_files = header.file
        else:
            header_files = header.files
            header_files = header_files.file if header_files else []
        return header_files

    @classmethod
    def get_topic_labels(cls, topic: bcf.agnostic.topic.TopicHandler) -> list[str]:
        if isinstance(topic, bcf.v2.topic.TopicHandler):
            labels = topic.topic.labels
        else:
            labels = topic.topic.labels
            labels = labels.label if labels else []
        return labels

    @classmethod
    def set_topic_labels(cls, topic: bcf.agnostic.topic.TopicHandler, labels: list[str]) -> None:
        topic_ = topic.topic
        if isinstance(topic_, bcf.v2.model.Topic):
            topic_.labels = labels
        else:
            topic_labels = topic_.labels
            if topic_labels is None:
                if not labels:
                    return
                topic_.labels = (topic_labels := bcf.v3.model.TopicLabels())
                return
            topic_labels.label = labels

    @classmethod
    def get_topic_reference_links(cls, topic: bcf.agnostic.topic.TopicHandler) -> list[str]:
        if isinstance(topic, bcf.v2.topic.TopicHandler):
            reference_links = topic.topic.reference_link
        else:
            reference_links = topic.topic.reference_links
            reference_links = reference_links.reference_link if reference_links else []
        return reference_links

    @classmethod
    def set_topic_reference_links(cls, topic: bcf.agnostic.topic.TopicHandler, reference_links: list[str]) -> None:
        topic_ = topic.topic
        if isinstance(topic_, bcf.v2.model.Topic):
            topic_.reference_link = reference_links
        else:
            topic_links = topic_.reference_links
            if topic_links is None:
                if not reference_links:
                    return
                topic_.reference_links = (topic_links := bcf.v3.model.TopicReferenceLinks())
                return
            topic_links.reference_link = reference_links

    @classmethod
    def get_topic_related_topics(
        cls, topic: bcf.agnostic.topic.TopicHandler
    ) -> Union[list[bcf.v2.model.TopicRelatedTopic], list[bcf.v3.model.TopicRelatedTopicsRelatedTopic]]:
        if isinstance(topic, bcf.v2.topic.TopicHandler):
            related_topics = topic.topic.related_topic
        else:
            related_topics = topic.topic.related_topics
            related_topics = related_topics.related_topic if related_topics else []
        return related_topics

    ## visinfo
    @classmethod
    def get_viewpoint_bitmaps(
        cls, viewpoint: bcf.agnostic.visinfo.VisualizationInfoHandler
    ) -> Union[list[bcf.v2.model.VisualizationInfoBitmap], list[bcf.v3.model.Bitmap]]:
        if isinstance(viewpoint, bcf.v2.visinfo.VisualizationInfoHandler):
            bitmaps = viewpoint.visualization_info.bitmap
        else:
            bitmaps = viewpoint.visualization_info.bitmaps
            bitmaps = bitmaps.bitmap if bitmaps else []
        return bitmaps
