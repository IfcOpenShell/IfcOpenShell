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
    if bpy.context.scene.BCFProperties.is_loaded:
        bpy.ops.bim.edit_bcf_reference_links()


def updateBcfLabel(self, context):
    if bpy.context.scene.BCFProperties.is_loaded:
        bpy.ops.bim.edit_bcf_labels()


def updateBcfProjectName(self, context):
    if bpy.context.scene.BCFProperties.is_loaded:
        bpy.ops.bim.edit_bcf_project_name()


def updateBcfAuthor(self, context):
    if bpy.context.scene.BCFProperties.is_loaded:
        bpy.ops.bim.edit_bcf_author()


def updateBcfTopicName(self, context):
    if bpy.context.scene.BCFProperties.is_loaded:
        bpy.ops.bim.edit_bcf_topic_name()


def updateBcfTopicIsEditable(self, context):
    if bpy.context.scene.BCFProperties.is_loaded and not self.is_editable:
        bpy.ops.bim.edit_bcf_topic()


def updateBcfCommentIsEditable(self, context):
    if bpy.context.scene.BCFProperties.is_loaded and not self.is_editable:
        bpy.ops.bim.edit_bcf_comment(comment_guid = self.name)


def refreshBcfTopic(self, context):
    global bcfviewpoints_enum
    bcfviewpoints_enum = None

    props = bpy.context.scene.BCFProperties
    bcfxml = bcfstore.BcfStore.get_bcfxml()
    topic = props.topics[props.active_topic_index]
    header = bcfxml.get_header(topic.name)
    getBcfViewpoints(self, context)


class BcfReferenceLink(PropertyGroup):
    name: StringProperty(name="Name", update=updateBcfReferenceLink)


class BcfLabel(PropertyGroup):
    name: StringProperty(name="Name", update=updateBcfLabel)


def getBcfViewpoints(self, context):
    global bcfviewpoints_enum
    if bcfviewpoints_enum is None:
        bcfviewpoints_enum = []
        props = bpy.context.scene.BCFProperties
        bcfxml = bcfstore.BcfStore.get_bcfxml()
        topic = props.topics[props.active_topic_index]
        viewpoints = bcfxml.get_viewpoints(topic.name)
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
    viewpoints: EnumProperty(items=getBcfViewpoints, name="BCF Viewpoints")
    files: CollectionProperty(name="Files", type=StrProperty)
    file_reference: StringProperty(default="", name="Reference")
    file_ifc_project: StringProperty(default="", name="IFC Project")
    file_ifc_spatial_structure_element: StringProperty(default="", name="IFC Spatial Structure Element")
    reference_links: CollectionProperty(name="Reference Links", type=BcfReferenceLink)
    reference_link: StringProperty(default="", name="Reference Link")
    labels: CollectionProperty(name="Labels", type=BcfLabel)
    label: StringProperty(default="", name="Label")
    bim_snippet: PointerProperty(type=BcfBimSnippet)
    bim_snippet_type: StringProperty(default="", name="Type")
    bim_snippet_reference: StringProperty(default="", name="Reference")
    bim_snippet_schema: StringProperty(default="", name="Schema")
    document_references: CollectionProperty(name="Document References", type=BcfDocumentReference)
    document_reference: StringProperty(default="", name="Referenced Document")
    document_reference_description: StringProperty(default="", name="Description")
    related_topics: CollectionProperty(name="Related Topics", type=StrProperty)
    related_topic: StringProperty(default="", name="Related Topic")
    comments: CollectionProperty(name="Comments", type=BcfComment)
    is_editable: BoolProperty(name="Is Editable", default=False, update=updateBcfTopicIsEditable)
    comment: StringProperty(default="", name="Comment")
    has_related_viewpoint: BoolProperty(name="Has Related Viewpoint", default=False)


class BCFProperties(PropertyGroup):
    is_loaded: BoolProperty(name="Is Loaded", default=False)
    comment_text_width: IntProperty(name="Comment Text Width", default=40)
    name: StringProperty(default="", name="Project Name", update=updateBcfProjectName)
    author: StringProperty(default="john@doe.com", name="Author Email", update=updateBcfAuthor)
    topics: CollectionProperty(name="BCF Topics", type=BcfTopic)
    active_topic_index: IntProperty(name="Active BCF Topic Index", update=refreshBcfTopic)
