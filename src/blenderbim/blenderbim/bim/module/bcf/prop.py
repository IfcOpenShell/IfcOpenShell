# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of BlenderBIM Add-on.
#
# BlenderBIM Add-on is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BlenderBIM Add-on is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with BlenderBIM Add-on.  If not, see <http://www.gnu.org/licenses/>.

import bpy
from . import bcfstore
from blenderbim.bim.prop import StrProperty
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


bcfviewpoints_enum = None


def purge():
    global bcfviewpoints_enum
    bcfviewpoints_enum = None


def updateBcfReferenceLink(self, context):
    if context.scene.BCFProperties.is_loaded:
        bpy.ops.bim.edit_bcf_reference_links()


def updateBcfLabel(self, context):
    if context.scene.BCFProperties.is_loaded:
        bpy.ops.bim.edit_bcf_labels()


def updateBcfProjectName(self, context):
    if self.is_loaded:
        bpy.ops.bim.edit_bcf_project_name()


def updateBcfAuthor(self, context):
    if self.is_loaded:
        bpy.ops.bim.edit_bcf_author()


def updateBcfTopicName(self, context):
    if context.scene.BCFProperties.is_loaded:
        bpy.ops.bim.edit_bcf_topic_name()


def updateBcfTopicIsEditable(self, context):
    if context.scene.BCFProperties.is_loaded and not self.is_editable:
        bpy.ops.bim.edit_bcf_topic()


def updateBcfCommentIsEditable(self, context):
    if context.scene.BCFProperties.is_loaded and not self.is_editable:
        bpy.ops.bim.edit_bcf_comment(comment_guid=self.name)


def refreshBcfTopic(self, context):
    self.clear_input_fields()
    getBcfViewpoints(None, context, force_update=True)


class BcfReferenceLink(PropertyGroup):
    name: StringProperty(name="Name", update=updateBcfReferenceLink)


class BcfLabel(PropertyGroup):
    name: StringProperty(name="Name", update=updateBcfLabel)


def getBcfViewpoints(self, context, force_update=False):
    global bcfviewpoints_enum
    if bcfviewpoints_enum is None or force_update:  # Retrieving Viewpoints is slow. Make sure we only do when needed
        bcfviewpoints_enum = []
        props = context.scene.BCFProperties
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        topic = props.active_topic
        viewpoints = bcfxml.get_viewpoints(topic.name) if topic else {}
        bcfviewpoints_enum.extend([(v, f"Viewpoint {i+1}", "") for i, v in enumerate(viewpoints.keys())])
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


class BcfTopic(PropertyGroup):
    name: StringProperty(name="GUID")
    title: StringProperty(default="", name="Title", update=updateBcfTopicName)
    type: StringProperty(default="", name="Type")
    status: StringProperty(default="", name="Status")
    priority: StringProperty(default="", name="Priority")
    stage: StringProperty(default="", name="Stage")
    creation_date: StringProperty(default="", name="Date")
    creation_author: StringProperty(default="", name="Author")
    modified_date: StringProperty(default="", name="Modified Date")
    modified_author: StringProperty(default="", name="Modified By")
    assigned_to: StringProperty(default="", name="Assigned To")
    due_date: StringProperty(default="", name="Due Date")
    description: StringProperty(default="", name="Description")
    viewpoints: EnumProperty(items=lambda _, context: getBcfViewpoints(_, context), name="BCF Viewpoints")
    files: CollectionProperty(name="Files", type=StrProperty)
    reference_links: CollectionProperty(name="Reference Links", type=BcfReferenceLink)
    labels: CollectionProperty(name="Labels", type=BcfLabel)
    bim_snippet: PointerProperty(type=BcfBimSnippet)
    document_references: CollectionProperty(name="Document References", type=BcfDocumentReference)
    related_topics: CollectionProperty(name="Related Topics", type=StrProperty)
    comments: CollectionProperty(name="Comments", type=BcfComment)
    is_editable: BoolProperty(name="Is Editable", default=False, update=updateBcfTopicIsEditable)


class BCFProperties(PropertyGroup):
    is_loaded: BoolProperty(name="Is Loaded", default=False)
    comment_text_width: IntProperty(name="Comment Text Width", default=40)
    name: StringProperty(default="", name="Project Name", update=updateBcfProjectName)
    author: StringProperty(default="john@doe.com", name="Author Email", update=updateBcfAuthor)
    topics: CollectionProperty(name="BCF Topics", type=BcfTopic)
    active_topic_index: IntProperty(name="Active BCF Topic Index", update=refreshBcfTopic)
    file_reference: StringProperty(default="", name="Reference")
    file_ifc_project: StringProperty(default="", name="IFC Project")
    file_ifc_spatial_structure_element: StringProperty(default="", name="IFC Spatial Structure Element")
    reference_link: StringProperty(default="", name="Reference Link")
    label: StringProperty(default="", name="Label")
    bim_snippet_reference: StringProperty(default="", name="Reference")
    bim_snippet_type: StringProperty(default="", name="Type")
    bim_snippet_schema: StringProperty(default="", name="Schema")
    document_reference: StringProperty(default="", name="Referenced Document")
    document_reference_description: StringProperty(default="", name="Description")
    related_topic: StringProperty(name="Related Topic")
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
        self.related_topic = ""
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
