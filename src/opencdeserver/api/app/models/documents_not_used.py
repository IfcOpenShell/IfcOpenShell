from typing import List, Optional
from pydantic import BaseModel
from models.documents_common import Document, DocumentVersion


# This file contains models that are not used at all, at least not yet.


# ---- not used at all, at least not yet ----


class DocumentQuery(BaseModel):
    document_ids: List[str]


class DocumentUpload(Document):
    session_file_id: Optional[str]
    ifc_project: Optional[str]


class MetadataForDocumentsSaved(BaseModel):
    documents: Optional[List[str]]


class DocumentQueryResult(BaseModel):
    versions: List[DocumentVersion]
