import sys
from dataclasses import dataclass, field
from typing import Optional

DATACLASS_KWARGS = {} if sys.version_info < (3, 10) else {"slots": True, "kw_only": True}


@dataclass(**DATACLASS_KWARGS)
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
        },
    )
    guid: str = field(
        metadata={
            "name": "Guid",
            "type": "Attribute",
            "required": True,
            "pattern": r"[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}",
        }
    )


@dataclass(**DATACLASS_KWARGS)
class DocumentInfoDocuments:
    class Meta:
        global_type = False

    document: list[Document] = field(
        default_factory=list,
        metadata={
            "name": "Document",
            "type": "Element",
            "namespace": "",
        },
    )


@dataclass(**DATACLASS_KWARGS)
class DocumentInfo:
    documents: Optional[DocumentInfoDocuments] = field(
        default=None,
        metadata={
            "name": "Documents",
            "type": "Element",
            "namespace": "",
        },
    )
