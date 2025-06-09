from pydantic import BaseModel, Field
from typing import Optional

from models.documents_common import CallbackLink, Document
from models.documents_request import FileToUpload, DocumentMetadataEntry
from models.request import User


# This file contains models that are neither used in requests nor in responses,
# and they can be used during both upload and download of documents.


# ---- UPLOAD MODELS ----


class ProjectOnly(BaseModel):
    project_id: str
    name: str


class DataForUploadDocuments(BaseModel):
    server_context: Optional[str] = Field(
        description="A CDE controlled identifier recording the user's context on the CDE. For example which project "
        "and folder the user was on. If the client provides the `server_context` in subsequent calls then "
        "the CDE will attemp to load the UI at the same place."
    )
    documents: list[FileToUpload]
    callback: Optional[CallbackLink]
    current_user: Optional[User]
    projects: list[ProjectOnly]


# ---- DOWNLOAD MODELS ----


class DocumentMetadataEntries(BaseModel):
    metadata: list[DocumentMetadataEntry] = Field(description="An array of metadata entries")


class Project(BaseModel):
    project_id: str
    name: str
    documents: Optional[list[Document]] = Field(
        description="An array containing all the documents selected by the user"
    )


class DataForDocumentSelection(BaseModel):
    server_context: Optional[str] = Field(
        description="A CDE controlled identifier recording the user's context on the CDE. For example which project "
        "and folder the user was on. If the client provides the `server_context` in subsequent calls then "
        "the CDE will attemp to load the UI at the same place."
    )
    projects: list[Project]
    callback: Optional[CallbackLink]
    current_user: Optional[User]


# ---- OTHER MODELS ----


file_types = {
    "smc": {"file_type": "Solibri Model Checker", "file_ending": ".smc", "mime_type": "application/octet-stream"},
    "ifc": {"file_type": "STEP Physical File", "file_ending": ".ifc", "mime_type": "application/x-step"},
    "ifczip": {"file_type": "ZIP of a STEP Physical File", "file_ending": ".ifcZIP", "mime_type": "application/zip"},
    "pdf": {"file_type": "Adobe Portable Document Format", "file_ending": ".pdf", "mime_type": "application/pdf"},
}
