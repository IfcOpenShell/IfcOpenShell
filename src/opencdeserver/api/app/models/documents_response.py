from pydantic import BaseModel, Field, constr
from typing import Optional
from enum import Enum

from models.documents_common import DocumentVersion, LinkData


# This file contains models used in responses during upload and download of documents.


# ---- UPLOAD MODELS ----


class DocumentUploadSessionInitialization(BaseModel):
    upload_ui_url: constr(min_length=1) = Field(
        description="A CDE UI URL for the client to open in a local browser. The user would enter document metadata "
        "directly in the CDE"
    )
    expires_in: int = Field(description="`upload_ui_url` expiry in seconds")
    max_size_in_bytes: int = Field(
        description="The maximum file size supported by the CDE. Attempts to upload a larger file will fail"
    )


class HttpMethod(Enum):
    POST = "POST"
    PUT = "PUT"


class HeaderValue(BaseModel):
    name: constr(min_length=1)
    value: constr(min_length=1)


class Headers(BaseModel):
    values: list[HeaderValue]


class MultipartFormData(BaseModel):
    prefix: str = Field(
        description="This is a server provided value. Its value must be prefixed to the binary content body when "
        "uploading this part"
    )
    suffix: str = Field(
        description="This is a server provided value. Its value must be suffixed to the binary content body when "
        "uploading this part. Typically, this is the end boundary for a multipart/form-data request"
    )


class UploadFilePartInstruction(BaseModel):
    url: constr(min_length=1)
    http_method: HttpMethod
    additional_headers: Optional[Headers] = None
    include_authorization: Optional[bool] = Field(
        description="Whether or not to include the authorization request header in the file upload request. "
        "Including the authorization header with some cloud storage providers might fail the request"
    )
    multipart_form_data: Optional[MultipartFormData] = None
    content_range_start: int = Field(description="The inclusive, zero index based start for this part")
    content_range_end: int = Field(description="The inclusive, zero index based end for this part")


class DocumentToUpload(BaseModel):
    session_file_id: constr(min_length=1) = Field(
        description="A client-provided identifier that allows matching the specification with the correct file on the "
        "user's machine"
    )
    upload_file_parts: list[UploadFilePartInstruction] = Field(
        description="An array of request specifications detailing how to split the file to parts and upload each part "
        "to the CDE"
        # min_length=1,
    )
    upload_completion: LinkData
    upload_cancellation: LinkData


class DocumentsToUpload(BaseModel):
    server_context: Optional[str] = Field(
        description="A CDE controlled identifier recording the user's context on the CDE. For example which project "
        "and folder the user was on. If the client provides the `server_context` in subsequent calls then "
        "the CDE will attemp to load the UI at the same place."
    )
    documents_to_upload: Optional[list[DocumentToUpload]]


# ---- DOWNLOAD MODELS ----


class DocumentDiscoverySessionInitialization(BaseModel):
    select_documents_url: constr(min_length=1) = Field(
        description="A CDE UI URL for the client to open in a local browser. The user would search and select "
        "documents directly in the CDE"
    )
    expires_in: int = Field(description="`select_documents_url` expiry in seconds")


class DocumentsMarkedAsSelected(BaseModel):
    documents: Optional[list[str]]


class SelectedDocuments(BaseModel):
    server_context: Optional[str] = Field(
        description="A CDE controlled identifier recording the user's context on the CDE. For example which project "
        "and folder the user was on. If the client provides the `server_context` in subsequent calls then "
        "the CDE will attemp to load the UI at the same place."
    )
    documents: list[DocumentVersion] = Field(description="An array containing all the documents selected by the user")


class DocumentMetadata(BaseModel):
    session_file_id: constr(min_length=1) = Field(
        description="This is a client provided id to differentiate between multiple files that are being uploaded in "
        "the same session"
    )
    document_id: Optional[constr(min_length=1)] = Field(
        description="When present, indicates that this upload is a new version of an existing document"
    )
    version_number: constr(min_length=1) = Field(
        description="A human readable version number. This is not expected to be in any specific format across CDEs "
        "and may hold any value"
    )
    title: constr(min_length=1) = Field(description="A human readable code or identifier")
    project: Optional[str]


class DocumentVersions(BaseModel):
    documents: list[DocumentVersion]
