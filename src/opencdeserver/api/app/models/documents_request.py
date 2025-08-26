from pydantic import BaseModel, Field, constr
from typing import Optional
from enum import Enum

from models.documents_common import CallbackLink


# This file contains models used in requests during upload and download of documents.


# ---- UPLOAD MODELS ----


class FileToUpload(BaseModel):
    file_name: constr(min_length=1) = Field(
        description="The CDE UI will display this value to the User when entering document metadata. This is the "
        "original name of the file. This attribute is the same as the name attribute in a document model."
    )
    session_file_id: constr(min_length=1) = Field(
        description="This is a client provided id to differentiate between multiple files that are being uploaded in "
        "the same session"
    )
    document_id: Optional[constr(min_length=1)] = Field(
        description="When present, indicates that this upload is a new version of an existing document"
    )


class UploadDocuments(BaseModel):
    callback: CallbackLink
    server_context: Optional[str] = Field(
        description="A CDE controlled identifier recording the user's context on the CDE. For example which project "
        "and folder the user was on. If the client provides the `server_context` in subsequent calls then "
        "the CDE will attemp to load the UI at the same place."
    )
    files: list[FileToUpload]


class UploadFileDetail(BaseModel):
    size_in_bytes: int = Field(description="The uploaded file size")
    session_file_id: constr(min_length=1) = Field(
        description="This is a client provided id to differentiate between multiple files that are being uploaded in "
        "the same session"
    )


class UploadFileDetails(BaseModel):
    files: list[UploadFileDetail]


# ---- DOWNLOAD MODELS ----


class SelectDocuments(BaseModel):
    callback: CallbackLink
    server_context: Optional[str] = Field(
        description="A CDE controlled identifier recording the user's context on the CDE. For example which project "
        "and folder the user was on. If the client provides the `server_context` in subsequent calls then "
        "the CDE will attemp to load the UI at the same place."
    )
    supported_file_extensions: Optional[list[str]] = Field(
        description="The client may optionally provide an array of accepted file extensions that should be opened "
        "during this flow. The CDE server UI should make an attempt to only show files matching these "
        "extensions to the user for the download selection or help the user in selecting the desired "
        "files. However, the server does not have to guarantee that only files matching the extensions "
        "will be selected. The extensions here must contain the dot separator.",
        example=[".ifc", ".ifczip"],
    )


class DataType(Enum):
    string = "string"
    boolean = "boolean"
    date_time = "date-time"
    date = "date"
    integer32 = "integer32"
    integer64 = "integer64"
    number = "number"
    url = "url"


class DocumentMetadataEntry(BaseModel):
    name: constr(min_length=1) = Field(description="The name of the metadata property")
    value: list[constr(min_length=1)] = Field(description="The value of the metadata property, can be a list")
    data_type: DataType = Field(description="The data type of the items in the value array")
