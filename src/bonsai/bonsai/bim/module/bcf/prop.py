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

import bpy
from . import bcfstore
from bonsai.bim.prop import StrProperty
from bpy.types import PropertyGroup
from bpy.props import (
    PointerProperty,
    StringProperty,
    EnumProperty,
    BoolProperty,
    IntProperty,
    FloatProperty,
    FloatVectorProperty,
    CollectionProperty,
)
from functools import partial
from typing import Literal
from typing_extensions import assert_never
from bcf.agnostic.extensions import get_extensions_attributes


bcfviewpoints_enum = None


def purge():
    global bcfviewpoints_enum
    bcfviewpoints_enum = None


def updateBcfReferenceLink(self, context):
    if bcfstore.BcfStore.get_bcfxml():
        bpy.ops.bim.edit_bcf_reference_links()


def updateBcfLabel(self, context):
    if bcfstore.BcfStore.get_bcfxml():
        bpy.ops.bim.edit_bcf_labels()


def updateBcfProjectName(self, context):
    if bcfstore.BcfStore.get_bcfxml():
        bpy.ops.bim.edit_bcf_project_name()


def updateBcfTopicName(self, context):
    if bcfstore.BcfStore.get_bcfxml():
        bpy.ops.bim.edit_bcf_topic_name()


def updateBcfTopicIsEditable(self, context):
    if bcfstore.BcfStore.get_bcfxml() and not self.is_editable:
        bpy.ops.bim.edit_bcf_topic()


def updateBcfCommentIsEditable(self, context):
    if bcfstore.BcfStore.get_bcfxml() and not self.is_editable:
        bpy.ops.bim.edit_bcf_comment(comment_guid=self.name)


def refreshBcfTopic(self, context):
    self.clear_input_fields()
    getBcfViewpoints(None, context, force_update=True)


class BcfReferenceLink(PropertyGroup):
    name: StringProperty(name="Name", update=updateBcfReferenceLink)


class BcfLabel(PropertyGroup):
    name: StringProperty(
        name="Name",
        update=updateBcfLabel,
        search=lambda s, c, t: get_extensions_items(s, c, t, extensions_attr="topic_labels"),
    )


def getBcfViewpoints(self, context, force_update=False):
    global bcfviewpoints_enum
    if bcfviewpoints_enum is None or force_update:  # Retrieving Viewpoints is slow. Make sure we only do when needed
        bcfviewpoints_enum = []
        props = context.scene.BCFProperties
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        assert bcfxml
        topic = props.active_topic
        viewpoints = bcfxml.topics[topic.name].viewpoints.keys() if topic else []
        bcfviewpoints_enum.extend([(v, f"Viewpoint {i+1}", "") for i, v in enumerate(viewpoints)])
    return bcfviewpoints_enum


class BcfBimSnippet(PropertyGroup):
    schema: StringProperty(name="Schema")
    reference: StringProperty(name="Reference")
    type: StringProperty(name="Type")
    is_external: BoolProperty(name="Is External")


class BcfDocumentReference(PropertyGroup):
    reference: StringProperty(name="Reference")
    description: StringProperty(name="Description")
    guid: StringProperty(name="GUID")
    is_external: BoolProperty(name="Is External")


class BcfComment(PropertyGroup):
    name: StringProperty(name="GUID")
    date: StringProperty(name="Date")
    author: StringProperty(name="Author")
    comment: StringProperty(name="Comment")
    viewpoint: StringProperty(name="Viewpoint")
    modified_date: StringProperty(name="Modified Date")
    modified_author: StringProperty(name="Modified Author")
    is_editable: BoolProperty(name="Is Editable", default=False, update=updateBcfCommentIsEditable)


def get_extensions_items(
    self: "BCFProperties", context: bpy.types.Context, edit_text: str, extensions_attr: str
) -> list[str]:
    bcf_file = bcfstore.BcfStore.get_bcfxml()
    assert bcf_file
    extensions = bcf_file.extensions
    if extensions is None:
        return []

    extension_data = getattr(extensions, extensions_attr)
    if extension_data is None:
        return []

    attrs = get_extensions_attributes(extensions)
    attribute_data = attrs[extensions_attr]
    return getattr(extension_data, attribute_data.subattr_name)


class BcfTopic(PropertyGroup):
    name: StringProperty(name="GUID")
    title: StringProperty(default="", name="Title", update=updateBcfTopicName)
    type: StringProperty(
        default="", name="Type", search=lambda s, c, t: get_extensions_items(s, c, t, extensions_attr="topic_types")
    )
    status: StringProperty(
        default="",
        name="Status",
        search=lambda s, c, t: get_extensions_items(s, c, t, extensions_attr="topic_statuses"),
    )
    priority: StringProperty(
        default="", name="Priority", search=lambda s, c, t: get_extensions_items(s, c, t, extensions_attr="priorities")
    )
    stage: StringProperty(
        default="", name="Stage", search=lambda s, c, t: get_extensions_items(s, c, t, extensions_attr="stages")
    )
    creation_date: StringProperty(default="", name="Date")
    creation_author: StringProperty(default="", name="Author")
    modified_date: StringProperty(default="", name="Modified Date")
    modified_author: StringProperty(default="", name="Modified By")
    assigned_to: StringProperty(
        default="", name="Assigned To", search=lambda s, c, t: get_extensions_items(s, c, t, extensions_attr="users")
    )
    due_date: StringProperty(default="", name="Due Date")
    description: StringProperty(default="", name="Topic Description")
    viewpoints: EnumProperty(items=lambda _, context: getBcfViewpoints(_, context), name="BCF Viewpoints")
    files: CollectionProperty(name="Files", type=StrProperty)
    reference_links: CollectionProperty(name="Reference Links", type=BcfReferenceLink)
    labels: CollectionProperty(name="Labels", type=BcfLabel)
    bim_snippet: PointerProperty(type=BcfBimSnippet)
    document_references: CollectionProperty(name="Document References", type=BcfDocumentReference)
    related_topics: CollectionProperty(name="Related Topics", type=StrProperty)
    comments: CollectionProperty(name="Comments", type=BcfComment)
    is_editable: BoolProperty(name="Edit Topic Attributes", default=False, update=updateBcfTopicIsEditable)


def get_related_topics(self: "BCFProperties", context: bpy.types.Context) -> list[tuple[str, str, str]]:
    global RELATED_TOPICS_ENUM_ITEMS
    props = self
    active_topic = props.active_topic
    active_related_topics = active_topic.related_topics.keys()
    RELATED_TOPICS_ENUM_ITEMS = []
    for t in props.topics:
        if t.name == active_topic.name:
            continue
        if t.name in active_related_topics:
            continue
        RELATED_TOPICS_ENUM_ITEMS.append((t.name, t.title, t.description))
    return RELATED_TOPICS_ENUM_ITEMS


class BCFProperties(PropertyGroup):
    bcf_file: StringProperty(name="BCF File")
    bcf_version: EnumProperty(
        name="BCF Version",
        description="Currently loaded BCF project version / BCF version to use for created projects",
        items=[("2", "v2.1", ""), ("3", "v3.0", "")],
        default="3",
    )
    comment_text_width: IntProperty(name="Comment Text Width", default=40)
    name: StringProperty(default="", name="Project Name", update=updateBcfProjectName)
    author: StringProperty(
        default="john@doe.com",
        name="Author Email",
        description="Author name that will be used for added comments, topics",
    )
    topics: CollectionProperty(name="BCF Topics", type=BcfTopic)
    active_topic_index: IntProperty(name="Active BCF Topic Index", update=refreshBcfTopic)
    file_reference: StringProperty(default="", name="Reference")
    file_ifc_project: StringProperty(default="", name="IFC Project")
    file_ifc_spatial_structure_element: StringProperty(default="", name="IFC Spatial Structure Element")
    reference_link: StringProperty(default="", name="Reference Link")
    label: StringProperty(
        default="", name="Label", search=lambda s, c, t: get_extensions_items(s, c, t, extensions_attr="topic_labels")
    )
    bim_snippet_reference: StringProperty(default="", name="Reference", description="URI or filepath to BimSnippet")
    bim_snippet_type: StringProperty(
        default="", name="Type", search=lambda s, c, t: get_extensions_items(s, c, t, extensions_attr="snippet_types")
    )
    bim_snippet_schema: StringProperty(default="", name="Schema")
    document_reference: StringProperty(default="", name="Referenced Document")
    document_reference_description: StringProperty(default="", name="Description")
    document_description: StringProperty(default="", name="Document Description")
    related_topic: EnumProperty(name="Related Topic", items=get_related_topics)
    comment: StringProperty(default="", name="Comment")
    has_related_viewpoint: BoolProperty(name="Has Related Viewpoint", default=False)

    def clear_input_fields(self):
        self.file_reference = ""
        self.file_ifc_project = ""
        self.file_ifc_spatial_structure_element = ""
        self.reference_link = ""
        self.label = ""
        self.bim_snippet_reference = ""
        self.bim_snippet_type = ""
        self.bim_snippet_schema = ""
        self.document_reference = ""
        self.document_reference_description = ""
        self.comment = ""
        self.has_related_viewpoint = False

    @property
    def active_topic(self):
        if len(self.topics) == 0:
            return None
        if self.active_topic_index < 0:
            self.active_topic_index = 0
        if self.active_topic_index >= len(self.topics):
            self.active_topic_index = len(self.topics) - 1
        return self.topics[self.active_topic_index]

    def refresh_topic(self, context):
        refreshBcfTopic(self, context)
