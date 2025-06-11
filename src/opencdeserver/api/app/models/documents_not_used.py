from typing import Optional
from pydantic import BaseModel
from models.documents_common import Document, DocumentVersion


# This file contains models that are not used at all, at least not yet.


# ---- not used at all, at least not yet ----


class DocumentQuery(BaseModel):
    document_ids: list[str]


class DocumentUpload(Document):
    session_file_id: Optional[str]
    ifc_project: Optional[str]


class MetadataForDocumentsSaved(BaseModel):
    documents: Optional[list[str]]


class DocumentQueryResult(BaseModel):
    versions: list[DocumentVersion]
