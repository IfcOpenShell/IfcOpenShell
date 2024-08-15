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

import bonsai.core.tool
import bonsai.tool as tool
import bpy
import bcf.v2.model
import bcf.v2.topic
import bcf.v3.model
import bcf.v3.topic
from typing import Any, Union, Optional


class Bcf(bonsai.core.tool.Bcf):
    @classmethod
    def get_path(cls) -> str:
        return bpy.context.scene.BCFProperties.bcf_file

    @classmethod
    def get_topic_document_references(
        cls, topic: Union[bcf.v2.topic.TopicHandler, bcf.v3.topic.TopicHandler]
    ) -> Union[list[bcf.v2.model.TopicDocumentReference], list[bcf.v3.model.DocumentReference]]:
        if isinstance(topic, bcf.v2.topic.TopicHandler):
            document_references = topic.topic.document_reference
        else:
            document_references = topic.topic.document_references
            document_references = document_references.document_reference if document_references else []
        return document_references

    @classmethod
    def get_topic_labels(cls, topic: Union[bcf.v2.topic.TopicHandler, bcf.v3.topic.TopicHandler]) -> list[str]:
        if isinstance(topic, bcf.v2.topic.TopicHandler):
            labels = topic.topic.labels
        else:
            labels = topic.topic.labels
            labels = labels.label if labels else []
        return labels

    @classmethod
    def get_topic_reference_links(cls, topic: Union[bcf.v2.topic.TopicHandler, bcf.v3.topic.TopicHandler]) -> list[str]:
        if isinstance(topic, bcf.v2.topic.TopicHandler):
            reference_links = topic.topic.reference_link
        else:
            reference_links = topic.topic.reference_links
            reference_links = reference_links.reference_link if reference_links else []
        return reference_links

    @classmethod
    def get_topic_related_topics(
        cls, topic: Union[bcf.v2.topic.TopicHandler, bcf.v3.topic.TopicHandler]
    ) -> Union[list[bcf.v2.model.TopicRelatedTopic], list[bcf.v3.model.TopicRelatedTopicsRelatedTopic]]:
        if isinstance(topic, bcf.v2.topic.TopicHandler):
            related_topics = topic.topic.related_topic
        else:
            related_topics = topic.topic.related_topics
            related_topics = related_topics.related_topic if related_topics else []
        return related_topics
