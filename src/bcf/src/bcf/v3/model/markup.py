from dataclasses import dataclass, field
from typing import List, Optional

from xsdata.models.datatype import XmlDateTime


@dataclass(slots=True, kw_only=True)
class BimSnippet:
    reference: str = field(
        metadata={
            "name": "Reference",
            "type": "Element",
            "namespace": "",
            "required": True,
            "min_length": 1,
            "white_space": "collapse",
        }
    )
    reference_schema: str = field(
        metadata={
            "name": "ReferenceSchema",
            "type": "Element",
            "namespace": "",
            "required": True,
            "min_length": 1,
            "white_space": "collapse",
        }
    )
    snippet_type: str = field(
        metadata={
            "name": "SnippetType",
            "type": "Attribute",
            "required": True,
            "min_length": 1,
            "white_space": "collapse",
        }
    )
    is_external: bool = field(
        default=False,
        metadata={
            "name": "IsExternal",
            "type": "Attribute",
        }
    )


@dataclass(slots=True, kw_only=True)
class CommentViewpoint:
    class Meta:
        global_type = False

    guid: str = field(
        metadata={
            "name": "Guid",
            "type": "Attribute",
            "required": True,
            "pattern": r"[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}",
        }
    )


@dataclass(slots=True, kw_only=True)
class DocumentReference:
    document_guid: Optional[str] = field(
        default=None,
        metadata={
            "name": "DocumentGuid",
            "type": "Element",
            "namespace": "",
            "pattern": r"[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}",
        }
    )
    url: Optional[str] = field(
        default=None,
        metadata={
            "name": "Url",
            "type": "Element",
            "namespace": "",
            "min_length": 1,
            "white_space": "collapse",
        }
    )
    description: Optional[str] = field(
        default=None,
        metadata={
            "name": "Description",
            "type": "Element",
            "namespace": "",
            "min_length": 1,
            "white_space": "collapse",
        }
    )
    guid: str = field(
        metadata={
            "name": "Guid",
            "type": "Attribute",
            "required": True,
            "pattern": r"[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}",
        }
    )


@dataclass(slots=True, kw_only=True)
class File:
    filename: Optional[str] = field(
        default=None,
        metadata={
            "name": "Filename",
            "type": "Element",
            "namespace": "",
            "min_length": 1,
            "white_space": "collapse",
        }
    )
    date: Optional[XmlDateTime] = field(
        default=None,
        metadata={
            "name": "Date",
            "type": "Element",
            "namespace": "",
        }
    )
    reference: Optional[str] = field(
        default=None,
        metadata={
            "name": "Reference",
            "type": "Element",
            "namespace": "",
            "min_length": 1,
            "white_space": "collapse",
        }
    )
    ifc_project: Optional[str] = field(
        default=None,
        metadata={
            "name": "IfcProject",
            "type": "Attribute",
            "length": 22,
            "pattern": r"[0-9A-Za-z_$]*",
        }
    )
    ifc_spatial_structure_element: Optional[str] = field(
        default=None,
        metadata={
            "name": "IfcSpatialStructureElement",
            "type": "Attribute",
            "length": 22,
            "pattern": r"[0-9A-Za-z_$]*",
        }
    )
    is_external: bool = field(
        default=True,
        metadata={
            "name": "IsExternal",
            "type": "Attribute",
        }
    )


@dataclass(slots=True, kw_only=True)
class TopicLabels:
    class Meta:
        global_type = False

    label: List[str] = field(
        default_factory=list,
        metadata={
            "name": "Label",
            "type": "Element",
            "namespace": "",
            "min_length": 1,
            "white_space": "collapse",
        }
    )


@dataclass(slots=True, kw_only=True)
class TopicReferenceLinks:
    class Meta:
        global_type = False

    reference_link: List[str] = field(
        default_factory=list,
        metadata={
            "name": "ReferenceLink",
            "type": "Element",
            "namespace": "",
            "min_length": 1,
            "white_space": "collapse",
        }
    )


@dataclass(slots=True, kw_only=True)
class TopicRelatedTopicsRelatedTopic:
    class Meta:
        global_type = False

    guid: str = field(
        metadata={
            "name": "Guid",
            "type": "Attribute",
            "required": True,
            "pattern": r"[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}",
        }
    )


@dataclass(slots=True, kw_only=True)
class ViewPoint:
    viewpoint: Optional[str] = field(
        default=None,
        metadata={
            "name": "Viewpoint",
            "type": "Element",
            "namespace": "",
            "min_length": 1,
            "white_space": "collapse",
        }
    )
    snapshot: Optional[str] = field(
        default=None,
        metadata={
            "name": "Snapshot",
            "type": "Element",
            "namespace": "",
            "min_length": 1,
            "white_space": "collapse",
        }
    )
    index: Optional[int] = field(
        default=None,
        metadata={
            "name": "Index",
            "type": "Element",
            "namespace": "",
        }
    )
    guid: str = field(
        metadata={
            "name": "Guid",
            "type": "Attribute",
            "required": True,
            "pattern": r"[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}",
        }
    )


@dataclass(slots=True, kw_only=True)
class Comment:
    date: XmlDateTime = field(
        metadata={
            "name": "Date",
            "type": "Element",
            "namespace": "",
            "required": True,
        }
    )
    author: str = field(
        metadata={
            "name": "Author",
            "type": "Element",
            "namespace": "",
            "required": True,
            "min_length": 1,
            "white_space": "collapse",
        }
    )
    comment: Optional[str] = field(
        default=None,
        metadata={
            "name": "Comment",
            "type": "Element",
            "namespace": "",
            "min_length": 1,
            "white_space": "collapse",
        }
    )
    viewpoint: Optional[CommentViewpoint] = field(
        default=None,
        metadata={
            "name": "Viewpoint",
            "type": "Element",
            "namespace": "",
        }
    )
    modified_date: Optional[XmlDateTime] = field(
        default=None,
        metadata={
            "name": "ModifiedDate",
            "type": "Element",
            "namespace": "",
        }
    )
    modified_author: Optional[str] = field(
        default=None,
        metadata={
            "name": "ModifiedAuthor",
            "type": "Element",
            "namespace": "",
            "min_length": 1,
            "white_space": "collapse",
        }
    )
    guid: str = field(
        metadata={
            "name": "Guid",
            "type": "Attribute",
            "required": True,
            "pattern": r"[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}",
        }
    )


@dataclass(slots=True, kw_only=True)
class HeaderFiles:
    class Meta:
        global_type = False

    file: List[File] = field(
        default_factory=list,
        metadata={
            "name": "File",
            "type": "Element",
            "namespace": "",
        }
    )


@dataclass(slots=True, kw_only=True)
class TopicDocumentReferences:
    class Meta:
        global_type = False

    document_reference: List[DocumentReference] = field(
        default_factory=list,
        metadata={
            "name": "DocumentReference",
            "type": "Element",
            "namespace": "",
        }
    )


@dataclass(slots=True, kw_only=True)
class TopicRelatedTopics:
    class Meta:
        global_type = False

    related_topic: List[TopicRelatedTopicsRelatedTopic] = field(
        default_factory=list,
        metadata={
            "name": "RelatedTopic",
            "type": "Element",
            "namespace": "",
        }
    )


@dataclass(slots=True, kw_only=True)
class TopicViewpoints:
    class Meta:
        global_type = False

    view_point: List[ViewPoint] = field(
        default_factory=list,
        metadata={
            "name": "ViewPoint",
            "type": "Element",
            "namespace": "",
        }
    )


@dataclass(slots=True, kw_only=True)
class Header:
    files: Optional[HeaderFiles] = field(
        default=None,
        metadata={
            "name": "Files",
            "type": "Element",
            "namespace": "",
        }
    )


@dataclass(slots=True, kw_only=True)
class TopicComments:
    class Meta:
        global_type = False

    comment: List[Comment] = field(
        default_factory=list,
        metadata={
            "name": "Comment",
            "type": "Element",
            "namespace": "",
        }
    )


@dataclass(slots=True, kw_only=True)
class Topic:
    reference_links: Optional[TopicReferenceLinks] = field(
        default=None,
        metadata={
            "name": "ReferenceLinks",
            "type": "Element",
            "namespace": "",
        }
    )
    title: str = field(
        metadata={
            "name": "Title",
            "type": "Element",
            "namespace": "",
            "required": True,
            "min_length": 1,
            "white_space": "collapse",
        }
    )
    priority: Optional[str] = field(
        default=None,
        metadata={
            "name": "Priority",
            "type": "Element",
            "namespace": "",
            "min_length": 1,
            "white_space": "collapse",
        }
    )
    index: Optional[int] = field(
        default=None,
        metadata={
            "name": "Index",
            "type": "Element",
            "namespace": "",
        }
    )
    labels: Optional[TopicLabels] = field(
        default=None,
        metadata={
            "name": "Labels",
            "type": "Element",
            "namespace": "",
        }
    )
    creation_date: XmlDateTime = field(
        metadata={
            "name": "CreationDate",
            "type": "Element",
            "namespace": "",
            "required": True,
        }
    )
    creation_author: str = field(
        metadata={
            "name": "CreationAuthor",
            "type": "Element",
            "namespace": "",
            "required": True,
            "min_length": 1,
            "white_space": "collapse",
        }
    )
    modified_date: Optional[XmlDateTime] = field(
        default=None,
        metadata={
            "name": "ModifiedDate",
            "type": "Element",
            "namespace": "",
        }
    )
    modified_author: Optional[str] = field(
        default=None,
        metadata={
            "name": "ModifiedAuthor",
            "type": "Element",
            "namespace": "",
            "min_length": 1,
            "white_space": "collapse",
        }
    )
    due_date: Optional[XmlDateTime] = field(
        default=None,
        metadata={
            "name": "DueDate",
            "type": "Element",
            "namespace": "",
        }
    )
    assigned_to: Optional[str] = field(
        default=None,
        metadata={
            "name": "AssignedTo",
            "type": "Element",
            "namespace": "",
            "min_length": 1,
            "white_space": "collapse",
        }
    )
    stage: Optional[str] = field(
        default=None,
        metadata={
            "name": "Stage",
            "type": "Element",
            "namespace": "",
            "min_length": 1,
            "white_space": "collapse",
        }
    )
    description: Optional[str] = field(
        default=None,
        metadata={
            "name": "Description",
            "type": "Element",
            "namespace": "",
            "min_length": 1,
            "white_space": "collapse",
        }
    )
    bim_snippet: Optional[BimSnippet] = field(
        default=None,
        metadata={
            "name": "BimSnippet",
            "type": "Element",
            "namespace": "",
        }
    )
    document_references: Optional[TopicDocumentReferences] = field(
        default=None,
        metadata={
            "name": "DocumentReferences",
            "type": "Element",
            "namespace": "",
        }
    )
    related_topics: Optional[TopicRelatedTopics] = field(
        default=None,
        metadata={
            "name": "RelatedTopics",
            "type": "Element",
            "namespace": "",
        }
    )
    comments: Optional[TopicComments] = field(
        default=None,
        metadata={
            "name": "Comments",
            "type": "Element",
            "namespace": "",
        }
    )
    viewpoints: Optional[TopicViewpoints] = field(
        default=None,
        metadata={
            "name": "Viewpoints",
            "type": "Element",
            "namespace": "",
        }
    )
    guid: str = field(
        metadata={
            "name": "Guid",
            "type": "Attribute",
            "required": True,
            "pattern": r"[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}",
        }
    )
    server_assigned_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "ServerAssignedId",
            "type": "Attribute",
            "min_length": 1,
            "white_space": "collapse",
        }
    )
    topic_type: str = field(
        metadata={
            "name": "TopicType",
            "type": "Attribute",
            "required": True,
            "min_length": 1,
            "white_space": "collapse",
        }
    )
    topic_status: str = field(
        metadata={
            "name": "TopicStatus",
            "type": "Attribute",
            "required": True,
            "min_length": 1,
            "white_space": "collapse",
        }
    )


@dataclass(slots=True, kw_only=True)
class Markup:
    header: Optional[Header] = field(
        default=None,
        metadata={
            "name": "Header",
            "type": "Element",
            "namespace": "",
        }
    )
    topic: Topic = field(
        metadata={
            "name": "Topic",
            "type": "Element",
            "namespace": "",
            "required": True,
        }
    )
