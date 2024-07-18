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
        }
    )
    reference_schema: str = field(
        metadata={
            "name": "ReferenceSchema",
            "type": "Element",
            "namespace": "",
            "required": True,
        }
    )
    snippet_type: str = field(
        metadata={
            "name": "SnippetType",
            "type": "Attribute",
            "required": True,
        }
    )
    is_external: bool = field(
        default=False,
        metadata={
            "name": "isExternal",
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
            "pattern": r"[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}",
        }
    )


@dataclass(slots=True, kw_only=True)
class HeaderFile:
    class Meta:
        global_type = False

    filename: Optional[str] = field(
        default=None,
        metadata={
            "name": "Filename",
            "type": "Element",
            "namespace": "",
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
        }
    )
    ifc_project: Optional[str] = field(
        default=None,
        metadata={
            "name": "IfcProject",
            "type": "Attribute",
            "length": 22,
            "pattern": r"[0-9,A-Z,a-z,_$]*",
        }
    )
    ifc_spatial_structure_element: Optional[str] = field(
        default=None,
        metadata={
            "name": "IfcSpatialStructureElement",
            "type": "Attribute",
            "length": 22,
            "pattern": r"[0-9,A-Z,a-z,_$]*",
        }
    )
    is_external: bool = field(
        default=True,
        metadata={
            "name": "isExternal",
            "type": "Attribute",
        }
    )


@dataclass(slots=True, kw_only=True)
class TopicDocumentReference:
    class Meta:
        global_type = False

    referenced_document: Optional[str] = field(
        default=None,
        metadata={
            "name": "ReferencedDocument",
            "type": "Element",
            "namespace": "",
        }
    )
    description: Optional[str] = field(
        default=None,
        metadata={
            "name": "Description",
            "type": "Element",
            "namespace": "",
        }
    )
    guid: Optional[str] = field(
        default=None,
        metadata={
            "name": "Guid",
            "type": "Attribute",
            "pattern": r"[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}",
        }
    )
    is_external: bool = field(
        default=False,
        metadata={
            "name": "isExternal",
            "type": "Attribute",
        }
    )


@dataclass(slots=True, kw_only=True)
class TopicRelatedTopic:
    class Meta:
        global_type = False

    guid: str = field(
        metadata={
            "name": "Guid",
            "type": "Attribute",
            "required": True,
            "pattern": r"[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}",
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
        }
    )
    snapshot: Optional[str] = field(
        default=None,
        metadata={
            "name": "Snapshot",
            "type": "Element",
            "namespace": "",
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
            "pattern": r"[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}",
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
        }
    )
    comment: str = field(
        metadata={
            "name": "Comment",
            "type": "Element",
            "namespace": "",
            "required": True,
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
        }
    )
    guid: str = field(
        metadata={
            "name": "Guid",
            "type": "Attribute",
            "required": True,
            "pattern": r"[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}",
        }
    )


@dataclass(slots=True, kw_only=True)
class Header:
    file: List[HeaderFile] = field(
        default_factory=list,
        metadata={
            "name": "File",
            "type": "Element",
            "namespace": "",
            "min_occurs": 1,
        }
    )


@dataclass(slots=True, kw_only=True)
class Topic:
    reference_link: List[str] = field(
        default_factory=list,
        metadata={
            "name": "ReferenceLink",
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
        }
    )
    priority: Optional[str] = field(
        default=None,
        metadata={
            "name": "Priority",
            "type": "Element",
            "namespace": "",
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
    labels: List[str] = field(
        default_factory=list,
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
        }
    )
    stage: Optional[str] = field(
        default=None,
        metadata={
            "name": "Stage",
            "type": "Element",
            "namespace": "",
        }
    )
    description: Optional[str] = field(
        default=None,
        metadata={
            "name": "Description",
            "type": "Element",
            "namespace": "",
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
    document_reference: List[TopicDocumentReference] = field(
        default_factory=list,
        metadata={
            "name": "DocumentReference",
            "type": "Element",
            "namespace": "",
        }
    )
    related_topic: List[TopicRelatedTopic] = field(
        default_factory=list,
        metadata={
            "name": "RelatedTopic",
            "type": "Element",
            "namespace": "",
        }
    )
    guid: str = field(
        metadata={
            "name": "Guid",
            "type": "Attribute",
            "required": True,
            "pattern": r"[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}",
        }
    )
    topic_type: Optional[str] = field(
        default=None,
        metadata={
            "name": "TopicType",
            "type": "Attribute",
        }
    )
    topic_status: Optional[str] = field(
        default=None,
        metadata={
            "name": "TopicStatus",
            "type": "Attribute",
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
    comment: List[Comment] = field(
        default_factory=list,
        metadata={
            "name": "Comment",
            "type": "Element",
            "namespace": "",
        }
    )
    viewpoints: List[ViewPoint] = field(
        default_factory=list,
        metadata={
            "name": "Viewpoints",
            "type": "Element",
            "namespace": "",
        }
    )
