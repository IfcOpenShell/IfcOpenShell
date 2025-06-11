from pydantic import BaseModel, Field, constr
from typing import Optional


# This file contains models used in both requests and responses during upload and download of documents.


# ---- REQUEST MODELS ---- #


class CallbackLink(BaseModel):
    url: constr(min_length=1) = Field(
        description="The server will web-browser-redirect to this URL once the user has completed selecting "
        "documents or entering document metadata on the CDE"
    )
    expires_in: int = Field(description="The expiry period for the URL, in seconds")


# ---- RESPONSE MODELS ---- #


class LinkData(BaseModel):
    url: constr(min_length=1)


class DocumentVersionLinks(BaseModel):
    document_version: LinkData
    document_version_metadata: LinkData
    document_version_download: LinkData
    document_versions: LinkData
    document_details: Optional[LinkData] = None


class FileDescription(BaseModel):
    name: constr(min_length=1) = Field(
        description="The name of the document version file on the server. The files are named by "
        "document_id.file_ending",
        example="908e1cd4-2e09-11ee-be56-0242ac120002.ifc",
    )
    size_in_bytes: int = Field(description="The size of the file in bytes", example="124563")


class Document(BaseModel):
    document_id: constr(min_length=1) = Field(
        description="A machine readable identifier that can be used to uniquely identify this version in future calls "
        "UUID is used - see `Query` section",
        example="908e1cd4-2e09-11ee-be56-0242ac120002",
    )
    session_file_id: Optional[str] = Field(
        description="A machine readable identifier that can be used to uniquely the file "
        "during the upload session, UUID is used",
        example="908e1cd4-2e09-11ee-be56-0242ac120002",
    )
    version_index: int = Field(
        description="A machine readable sequence number of the version of the document. The sequence must be ordered, "
        "so that newer versions have higher values than previous ones. Each version index must be unique "
        "for that document, but there may be gaps in the sequence",
        example="12",
    )
    version_number: Optional[constr(min_length=1)] = Field(
        description="A human readable version number. This is not expected to be in any specific format across CDEs "
        "and may hold any value",
        example="V2.0-larger",
    )
    creation_date: str = Field(
        description="The creation date of the document revision", example="2016-04-28T16:31:12.270+02:00"
    )
    title: Optional[constr(min_length=1)] = Field(
        description="A human readable code or identifier. Metadata entered by user in CDE.", example="Large garage"
    )
    original_file_name: Optional[str] = Field(
        description="The full name of the file as sent to the API", example="First_floor_vent.ifc"
    )
    file_ending: Optional[str] = Field(description="The ending of the file name, including the dot", example=".ifc")
    mime_type: Optional[str] = Field(description="The mime type identifier", example="application/x-step")
    file_type: Optional[str] = Field(description="The full name of the file type", example="STEP Physical File (SPF)")
    project: Optional[str] = Field(
        description="The project to which the document will belong once it has been uploaded,"
        "this information is added as metadata by the user in the CDE",
        example="908e1cd4-2e09-11ee-be56-0242ac120003",
    )
    file_description: FileDescription
    parts: Optional[list[str]]


class DocumentVersion(Document):
    links: DocumentVersionLinks
