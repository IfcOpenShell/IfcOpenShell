from dataclasses import dataclass, field
from typing import List, Optional


@dataclass(slots=True, kw_only=True)
class Document:
    filename: str = field(
        metadata={
            "name": "Filename",
            "type": "Element",
            "namespace": "",
            "required": True,
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
class DocumentInfoDocuments:
    class Meta:
        global_type = False

    document: List[Document] = field(
        default_factory=list,
        metadata={
            "name": "Document",
            "type": "Element",
            "namespace": "",
        }
    )


@dataclass(slots=True, kw_only=True)
class DocumentInfo:
    documents: Optional[DocumentInfoDocuments] = field(
        default=None,
        metadata={
            "name": "Documents",
            "type": "Element",
            "namespace": "",
        }
    )
