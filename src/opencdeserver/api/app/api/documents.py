import collections
import os
import shutil
import traceback
import sys

from fastapi import HTTPException, status, APIRouter, Request, Depends
from fastapi import UploadFile, Form
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.encoders import jsonable_encoder

from typing import Union
from uuid import UUID, uuid4

from pydantic import ValidationError
from security.secure import get_current_active_user

from repository.documents import doc_db

from models.documents_request import *
from models.documents_response import *
from models.documents_common import *
from models.documents_other import *

from api.logging import LoggingRoute

router = APIRouter(route_class=LoggingRoute)

templates = Jinja2Templates(directory="templates")


################################################################
# DOCUMENTS API UPLOAD FLOW
################################################################

# ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ----
# summary: 'Initiate the upload flow'
#
# description: 'The client will call this endpoint to initiate the flow of uploading documents to the CDE.'
#
# requestBody:
# description: 'The body of this request contains a list of files to upload and a callback URL to the client,
# which is used later in the flow to communicate from the CDE server back to the client via query parameters.'
#
# {
#   "server_context": "7188a2be-6c4e-4e3b-b7e7-cd27f0d4ad67",
#   "callback": {
#     "url": "http://localhost:8080/cde-callback-example",
#     "expires_in": 3600
#   },
#   "files": [
#     {
#       "file_name": "model.ifc",
#       "session_file_id": "76ec9d91-0731-4405-b3c4-9bf945f9955b"
#     }
#   ]
# }
#
# The client is using the optional server_context in this example to provide a guid value
# which was obtained, from the CDE, in a previous document exchange. The server_context
# informs the CDE of the user's previous activity (e.g. a "project" or a directory on
# the CDE). The CDE can use the server_context to resume the document selection session
# from where the user has last left.
#
# description: 'The CDE returns a URL for the client to open in a local browser.
#
# {
#   "upload_ui_url": "https://cde.example.com/document-upload?upload_session=7c41c859-c0c1-4914-ac6c-8fbd50fb8247",
#   "expires_in": 60,
#   "max_size_in_bytes": 1073741824
# }
#
# The user will then be presented with the CDE UI to enter document metadata'
#
# links /server-provided-path-upload-documents-url
#
# * Once the user has completed entering document metadata in the CDE UI,
# the CDE will append `?upload_documents_url=/server-provided-path-upload-documents-url`
# to the client's callback (see request) and provide it to the client via a browser redirect
#
# * If the user has cancelled the download the CDE server will append `?user_cancelled_selection=true`
# to the client's callback (see request) and provide it to the client via a browser redirect.

# implemented


@router.post("/documents/1.0/upload-documents", tags=[""])
def upload_documents_post(
    upload_documents: UploadDocuments, current_user: User = Depends(get_current_active_user)
) -> DocumentUploadSessionInitialization:
    post_upload_documents_response = doc_db.post_upload_documents(upload_documents, current_user)
    doc_db.debug(
        endpoint="upload_documents_post",
        request={"upload_documents": upload_documents},
        response=post_upload_documents_response.dict(),
    )
    return post_upload_documents_response


# This goes to a website UI where the user can enter document metadata.
@router.get("/documents/1.0/document-upload", tags=[""], response_class=HTMLResponse)
def upload_documents_get(request: Request, upload_session: UUID):

    data_for_upload_documents = doc_db.get_data_for_upload_documents(upload_session)
    print("Data for site: ", data_for_upload_documents)

    return templates.TemplateResponse(
        "upload_files.html",
        {
            "request": request,
            "upload_session": upload_session,
            "username": data_for_upload_documents.current_user.username,
            "email": data_for_upload_documents.current_user.email,
            "full_name": data_for_upload_documents.current_user.full_name,
            "server_context": data_for_upload_documents.server_context,
            "callback_url": data_for_upload_documents.callback.url,
            "callback_expires_in": data_for_upload_documents.callback.expires_in,
            "documents": data_for_upload_documents.documents,
            "projects": data_for_upload_documents.projects,
        },
    )


@router.post("/documents/1.0/save-metadata-for-documents", tags=[""])
async def save_metadata_for_documents_post(request: Request) -> list:

    form_data = await request.form()
    form_data_json = jsonable_encoder(form_data)

    print("Form values: ")
    print(form_data_json)

    documents = collections.defaultdict(dict)
    names = ("session_file_id", "document", "title", "version_number", "filename")

    for whole_form_key, value in form_data_json.items():
        if whole_form_key.startswith(names):
            start_form_key, document_id = whole_form_key.split("@", 1)
            print("New field: ", start_form_key, " for document id: ", document_id)
            documents[document_id][start_form_key] = value

    print("Documents: ")
    print(documents)

    username = form_data_json["username"]
    upload_session = form_data_json["upload_session"]
    server_context = form_data_json["server_context"]
    callback_url = form_data_json["callback_url"]
    callback_expires_in = form_data_json["callback_expires_in"]
    project = form_data_json["project"]

    documents_saved = list()

    for key in documents:
        try:
            documents[key]["project"] = project
            document = DocumentMetadata(**documents[key])
            save_metadata_response = doc_db.save_metadata_for_documents(document, upload_session, username)
            documents_saved.append(save_metadata_response)
        except ValidationError as e:
            print(e)
            continue

    doc_db.debug(
        endpoint="save_metadata_for_documents_post",
        request={"documents": documents},
        response={"response": documents_saved},
    )

    return documents_saved


# http://localhost:8080/cde-callback-example?upload_documents_url=
# https%3A%2F%2Fcde.example.com%2Fupload-instructions%3Fupload_session%3Dee56b8f3-8f93-4819-976e-46a45a5a996f


@router.post("/documents/1.0/upload-instructions", tags=[""])
def upload_instructions(
    session_id: str,
    server_context: str,
    upload_files: UploadFileDetails,
    current_user: User = Depends(get_current_active_user),
) -> DocumentsToUpload:
    documents_to_upload_model = DocumentsToUpload()
    documents_to_upload_model.server_context = server_context
    documents_to_upload_model.documents_to_upload = list()
    for upload_file in upload_files.files:
        get_upload_instructions_response = doc_db.get_upload_instructions(
            session_id, server_context, upload_file, current_user
        )
        doc_db.debug(
            endpoint="upload_instructions",
            request={"session_id": session_id, "server_context": server_context, "document": upload_file},
            response=get_upload_instructions_response.dict(),
        )
        documents_to_upload_model.documents_to_upload.append(get_upload_instructions_response)
    return documents_to_upload_model


# ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ----
# summary: 'Upload a single file part'
#
# description: This endpoint allows the client to upload the content of a single file part.
# * The `/server-provided-path-upload-documents-url` operation specifies the list of part
#     upload requests for each file
# * For each part, the URL, method (put or post), headers and request body are specified
# * The client must upload all parts before proceeding to complete the upload
# * Parts can be uploaded concurrently and in any order
#
# requestbody: 'The file content', application/octet-stream, type: string, format: binary
#
# responses: DocumentsToUpload
#
# links:
# /server-provided-path-document-upload-completion
# description: This operation should be called when all the parts have been successfully uploaded
#
# /server-provided-path-document-upload-cancellation
# description: This operation should be called to cancel the upload


@router.post("/documents/1.0/upload-part/{part_id}", tags=[""])
async def upload_part(part_id: str, request: Request, current_user: User = Depends(get_current_active_user)):

    # file_name = doc_db.safe_path(part_id)
    file_name = part_id

    # see if the user really has the part-node in the database, before receiving upload of this part
    # and get the document_id of the part
    document = doc_db.user_has_part(part_id, current_user)

    request_body = await request.body()

    if document:

        # try to receive the uploaded part
        try:
            print("File contents: ", request_body)

            # use document_id instead as dir_name
            # dir_name = doc_db.safe_path(document.document_id)
            dir_name = document.document_id

            path = "./data/document_parts/" + dir_name + "/"

            if not os.path.exists(path):
                os.makedirs(path)

            with open(path + file_name, "wb") as f:
                f.write(request_body)

        except Exception:
            print("Error uploading file")
            print(traceback.format_exc())
            print("Error uploading file")
            print(sys.exc_info()[2])

        finally:
            # We will write to the database, information about part successfully uploaded.
            doc_db.mark_part_as_uploaded(part_id, current_user)

        doc_db.debug(endpoint="upload-part", request={"part_id": part_id}, response={"uploaded": True})

        return {"message": f"Successfully uploaded part {file_name}"}


# ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ----
# summary: 'Complete a file upload after all the parts have been successfully uploaded'
#
# description: The `/server-provided-path-upload-documents-url` operation specifies
# the upload completion URL for each file. The upload completion endpoint must be
# called by the client when the file content upload has completed successfully.
#
# responses: DocumentVersion
#
# links:
# /server-provided-path-document-upload-completion
# description: This operation should be called when all the parts have been successfully uploaded
#
# /server-provided-path-document-upload-cancellation
# description: This operation should be called to cancel the upload


@router.post("/documents/1.0/upload-completion", tags=[""])
def upload_completion(
    upload_session: str, current_user: User = Depends(get_current_active_user)
) -> Union[DocumentVersion, bool]:

    # check if all parts really are marked as uploaded in database
    # retrieve document_id, file_type, file_ending, and parts_id (in order)

    if not doc_db.all_parts_uploaded(upload_session, current_user):
        raise HTTPException(status_code=400, detail="All parts not uploaded.")

    parts = doc_db.retrieve_uploaded_parts(upload_session, current_user)
    print("Number of parts: " + str(len(parts)))
    document = doc_db.get_document_from_session(upload_session, current_user)

    # check if all parts really are uploaded to document_id-dir
    document_name = doc_db.safe_path(document.document_id)

    path = "./data/document_parts/" + document_name + "/"

    for part in parts:
        part = doc_db.safe_path(part)
        print("Checking for part " + part + " in dir " + path)

        if not os.path.isfile(path + part):
            print(part + " is not in dir " + path)
            raise HTTPException(status_code=400, detail="All parts not in dir.")
        else:
            print(part + " is in dir " + path)

    # merge parts to a new temporary document
    temp_doc_path = path
    temp_doc_file_name = path + document_name
    if not os.path.exists(temp_doc_path):
        os.makedirs(temp_doc_path)

    new_doc_path = "./data/documents/"
    new_doc_path_name = new_doc_path + document.file_description.name

    # Read parts and write to temp doc.
    with open(temp_doc_file_name, "ab") as temp_doc:
        for part in parts:
            part = doc_db.safe_path(part)
            with open(temp_doc_path + part, "rb") as part_doc:
                temp_doc.write(part_doc.read())

    # move document to new location in documents dir
    os.rename(temp_doc_file_name, new_doc_path_name)

    # remove temp parts
    for part in parts:
        os.remove(temp_doc_path + part)

    # remove temp path
    os.rmdir(temp_doc_path)

    # clean database and create new document node under correct project
    if doc_db.document_upload_finish(upload_session, current_user, document.project):
        # get DocumentVersion
        document = doc_db.get_document_version(document.document_id, document.version_index, current_user)

        doc_db.debug(endpoint="upload_completion", request={"upload_session": upload_session}, response=document.dict())
        return document
    else:
        return False


# ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ----
# summary: 'Cancel the upload of a single file'
#
# description: The `/server-provided-path-upload-documents-url` operation specifies the
# upload cancellation URL for each file. This endpoint must be called by the client when
# the file content upload has been cancelled.
#
# responses: 204


@router.post("/documents/1.0/upload-cancellation", tags=[""], status_code=status.HTTP_204_NO_CONTENT)
def upload_cancellation(upload_session: str, current_user: User = Depends(get_current_active_user)):

    try:
        # remove session and leaf nodes from database
        document = doc_db.get_upload_cancellation(upload_session, current_user)

        # clean temp dir
        document_name = doc_db.safe_path(document.document_id)
        path = "./data/document_parts/" + document_name + "/"
        shutil.rmtree(path)

    except Exception as e:
        print(e)

    finally:
        print("Upload cancellation complete.")

    return


# ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ----
# summary: 'Query for the latest versions of multiple documents'
#
# description: This endpoint can be called when querying for the latest versions for multiple
# documents. It's an aggregate endpoint that should make periodic polling of a collection
# of documents easier.
#
# parameters:
#  in: header
#  name: If-None-Match
#  description: 'Clients may provide a previosuly received etag value to avoid receiving
#  a response object if there were no changes since the last query'
# schema: type: string, format: etag_value
#
# responses
# description: 'A list of DocumentVersion objects, where each DocumentVersion
# represents the latest version for each given document on the server.'
#
# headers:
#  ETag:
# schema: type: string, format: etag_value
#
# description: A unique identifier of the response that allows CDEs to save bandwidth and the
# clients to implement caching and avoid computation when the document versions haven't changed
# since the last query
#
# links
# /server-provided-path-document-versions
# These operations allows listing all the versions of a document
# that has been flagged to have a new version in the response.
#


@router.post("/documents/1.0/document-versions", tags=[""])
def document_versions_post(
    document_ids: list[UUID], current_user: User = Depends(get_current_active_user)
) -> list[DocumentVersion]:

    document_versions = list()
    for document_id in document_ids:
        document_versions.append(doc_db.get_document_version(document_id, 1, current_user))

    doc_db.debug(endpoint="document_versions_post", request={document_ids}, response={document_versions})

    return document_versions


################################################################
# DOWNLOAD FLOW
################################################################

# ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ----
# summary: 'Initiate document selection and download flow'
#
# description: The client will call this endpoint to initiate the flow of selecting and downloading documents.
#
# requestBody: 'The body of this request contains a callback URL to the client, which is used later in the
# flow to communicate from the CDE server back to the client via query parameters.'
#
# {
#   "server_context": "711c0744-0a92-489f-8ca1-13813aa2dee7",
#   "callback": {
#     "url": "http://localhost:8080/cde-callback-example",
#     "expires_in": 3600
#   },
#   "supported_file_extensions": [
#     ".ifc",
#     ".ifczip"
#   ]
# }
#
# responses: 'The CDE returns a URL for the client to open in a local browser.
# The user will then be presented with the CDE UI to select and download documents'
#
# {
#   "select_documents_url": "https://cde.example.com/document-selection?selection_session=7c41c859-c0c1-4914-ac6c-8fbd50fb8247",
#   "expires_in": 60
# }
#
# links /server-provided-path-selected-documents-url
#
# * Once the user has completed selecting documents in the CDE UI, the CDE will append
# `?selected_documents_url=/server-provided-path-selected-documents-url` to the client's
# callback (see request) and provide it to the client via a browser redirect.
#
# in this case we use a static url: selected-documents-url (but this is not safe)
#
# * IF the user has cancelled the download, the CDE server will append `?user_cancelled_selection=true`
# to the client's callback (see request) and provide it to the client via a browser redirect.
#


@router.post("/documents/1.0/select-documents", tags=[""])
def select_documents_post(
    select_documents: SelectDocuments, current_user: User = Depends(get_current_active_user)
) -> DocumentDiscoverySessionInitialization:
    post_select_documents_response = doc_db.post_select_documents(select_documents, current_user)
    doc_db.debug(
        endpoint="select_documents_post",
        request={"select_documents": select_documents},
        response=post_select_documents_response.dict(),
    )
    print("Returns ", post_select_documents_response)
    return post_select_documents_response


# ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ----
# summary: 'Retrieve the user''s selection from the CDE'
#
# description: This endpoint returns the document selection. The client retrieves its URL
# via the callback URL from the CDE after the selection has finished from a query parameter
# named `selected_documents_url`. In case when the user cancels the selection on the CDE UI,
# this callback will still be called, but the `selected_documents_url` query parameter will
# not be present, instead the server will provide a query parameter called
# `user_cancelled_selection=true`.
#
# responses: SelectedDocuments
#
# links /server-provided-path-document-download
# Use the `document_version_download` operation to download the file contents
#
# links /server-provided-path-document-metadata
# Use the `document_version_metadata` URL operation to retrieve document metadata

# documents/1.0/document-selection?selection_session=7cf3dd70-c880-4fb1-9897-f60472959533


@router.get("/documents/1.0/document-selection", tags=[""], response_class=HTMLResponse)
def selected_documents_get(request: Request, selection_session: UUID):
    data_for_document_selection = doc_db.get_data_for_document_selection(selection_session)
    return templates.TemplateResponse(
        "select_files.html",
        {
            "request": request,
            "selection_session": selection_session,
            "current_user": data_for_document_selection.current_user,
            "server_context": data_for_document_selection.server_context,
            "callback_url": data_for_document_selection.callback.url,
            "callback_expires_in": data_for_document_selection.callback.expires_in,
            "projects": data_for_document_selection.projects,
        },
    )


@router.post("/documents/1.0/mark-documents-as-selected", tags=[""])
async def mark_documents_as_selected_post(request: Request) -> DocumentsMarkedAsSelected:

    form_data = await request.form()
    form_data_json = jsonable_encoder(form_data)

    print("Form values: ")
    print(form_data_json)

    documents = list()
    for key, value in form_data_json.items():
        if "document_" in key:
            document_id = key.split("ocument_", 1)[1]
            documents.append(document_id)

    print("Sends ", documents)

    get_selected_response = doc_db.post_mark_documents_as_selected(documents, form_data_json["selection_session"])
    doc_db.debug(
        endpoint="mark_some_documents_as_selected_post",
        request={"documents": documents, "form_data_json[selection_session]": form_data_json["selection_session"]},
        response=get_selected_response.dict(),
    )

    return get_selected_response


@router.get("/documents/1.0/download-instructions", tags=[""])
def download_instructions(
    session_id: UUID, server_context: str, current_user: User = Depends(get_current_active_user)
) -> SelectedDocuments:
    get_download_instructions_response = doc_db.get_download_instructions(session_id, server_context, current_user)
    doc_db.debug(
        endpoint="download_instructions",
        request={"session_id": session_id, "server_context": server_context},
        response=get_download_instructions_response.dict(),
    )
    return get_download_instructions_response


# download links


@router.get("/documents/1.0/document/{document_id}/version/{version_index}", tags=[""])
def document_version(
    document_id: str, version_index: int, current_user: User = Depends(get_current_active_user)
) -> DocumentVersion:
    # This endpoint returns the document version model itself.
    get_document_version = doc_db.get_document_version(document_id, version_index, current_user)
    doc_db.debug(
        endpoint="document_version",
        request={"document_id": document_id, "version_index": version_index},
        response=get_document_version.dict(),
    )
    return get_document_version


# ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ----
# summary: 'Get document metadata for a single document'
#
# description: This endpoint returns the metadata for a single document. Its URL is retrieved
# from the links object in the initial document selection response, with the `document_version_metadata`
# property.
#
# responses: 'The file content', application/octet-stream, type: string, format: binary
#
#
# links /server-provided-path-document-download
# Use the `document_version_download` operation to download the file contents
#
# links /server-provided-path-document-metadata
# Use the `document_version_metadata` URL operation to retrieve document metadata


@router.get("/documents/1.0/document/{document_id}/version/{version_index}/metadata", tags=[""])
def document_version_metadata(
    document_id: str, version_index: int, current_user: User = Depends(get_current_active_user)
) -> DocumentMetadataEntries:
    # The metadata for document versions is a list of key-value pairs
    get_document_version_metadata_result = doc_db.get_document_version_metadata(
        document_id, version_index, current_user
    )
    doc_db.debug(
        endpoint="document_version",
        request={"document_id": document_id, "version_index": version_index},
        response=get_document_version_metadata_result.dict(),
    )
    return get_document_version_metadata_result


# ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ----
# summary: 'Download the document'
#
# description: Use this endpoint to download the document.
# Its URL is retrieved from the links object in the initial document selection response,
# with the `document_version_download` property.
#
# responses: 'The file content', application/octet-stream, type: string, format: binary
#
#
# links /server-provided-path-document-download
# Use the `document_version_download` operation to download the file contents
#
# links /server-provided-path-document-metadata
# Use the `document_version_metadata` URL operation to retrieve document metadata


@router.get("/documents/1.0/document/{document_id}/version/{version_index}/download", tags=[""])
def document_version_download(
    document_id: str, version_index: int, current_user: User = Depends(get_current_active_user)
) -> FileResponse:
    # The url to download the binary content of this document version.
    # May either directly return the result or redirect to a storage provider
    keep_characters = (" ", ".", "_", "-")
    document_id = "".join(c for c in document_id if c.isalnum() or c in keep_characters).rstrip()
    file_location = "./data/documents/" + document_id + ".ifc"
    return FileResponse(
        file_location, media_type="application/x-step", filename="6dbd4d52-14db-11ee-be56-0242ac120002.ifc"
    )


@router.get("/documents/1.0/document/{document_id}/version/{version_index}/versions", tags=[""])
def document_versions(
    document_id: str, version_index: int, current_user: User = Depends(get_current_active_user)
) -> DocumentVersions:
    # This url returns a list of all document versions for the parent document.
    # The client can use this URL to monitor for new document versions
    get_document_versions_result = doc_db.get_document_versions(document_id, current_user)
    doc_db.debug(
        endpoint="document_version", request={"document_id": document_id}, response=get_document_versions_result.dict()
    )
    return get_document_versions_result


@router.get(
    "/documents/1.0/document/{document_id}/version/{version_index}/details", tags=[""], response_class=HTMLResponse
)
def document_version_details(
    request: Request, document_id: str, version_index: int, current_user: User = Depends(get_current_active_user)
):
    # This url returns a list of all document versions for the parent document.
    # The client can use this URL to monitor for new document versions
    details = doc_db.get_document_version(document_id, version_index, current_user)
    doc_db.debug(
        endpoint="document_version",
        request={"document_id": document_id, "version_index": version_index},
        response=details.dict(),
    )
    return templates.TemplateResponse("document_details.html", {"request": request, "details": details})


# ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ----
# summary: 'Get the versions of a single document'
#
# description: This endpoint returns the versions for a single document. Its URL is retrieved
# from the links object in the initial document selection response, with the `document_versions` property.
#
# responses: DocumentVersions
#
# links: /document-versions
# parameters:
# document_id: '$response.body#..document_id'
# description: > Use the `document_id` to query for updates for this document

# @router.get("/documents/1.0/document-versions", tags=[""])
# def document_versions_get(current_user: User = Depends(get_current_active_user)) -> DocumentVersions:
#     xxx_response = doc_db.get_post_put_xxx(current_user)
#     doc_db.debug(endpoint='xxx_get_post_put',
#                  request={},
#                  response={count: value.dict() for count, value in enumerate(xxx_response)})
#     return xxx_response

# ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ----
# summary: 'Retrieve upload instructions after the user has entered document metadata on the CDE'
#
# description: This endpoint returns the document upload information. The client retrieves
# this URL via the callback URL from the server after the user's completion of the upload
# metadata entry from a query parameter named `upload_documents_url`. In case when the
# user cancels the upload on the CDE UI, this callback will still be called, but the
# `upload_documents_url` query parameter will not be present, instead the server will
# provide a query parameter called `user_cancelled_upload=true`.
#
# requestbody: description: 'The client sends the list of files to be uploaded with this
# request. The file sizes are then used by the server to break the file to multiple
# upload parts, as required.'
#
# responses: DocumentsToUpload
#
# links:
# /server-provided-path-document-upload-part
# description: This operation should be called for each part specified in this reponse
#
# /server-provided-path-document-upload-completion
# description: This operation should be called when all the parts have been successfully uploaded
#
# /server-provided-path-document-upload-cancellation
# description: This operation should be called to cancel the upload

################################################################
# CUSTOM UPLOAD FLOW, USING DOWNLOAD SESSION
################################################################

# TODO: Fortsätt här
#  include selection session i result


@router.post("/documents/1.0/upload_file_to_project", tags=[""])
async def upload_documents_post(
    file: UploadFile, project: str = Form(...), selection_session: str = Form(...)
) -> Document:

    # Get the file size (in bytes)
    file.file.seek(0, 2)
    file_size = file.file.tell()

    # Create document id for file
    document_id = str(uuid4())

    # Move cursor back to the beginning of the file
    await file.seek(0)

    # Find file name ending and create new storage file name
    if file.filename.lower().endswith(tuple(file_types)):
        file_ending = file.filename.split(".")[-1].lower()
        name = document_id + "." + file_ending
    else:
        file_ending = ""
        name = document_id

    # Get mime type and file type
    mime_type = ""
    file_type = ""
    if hasattr(file_types, file_ending):
        mime_type = file_types[file_ending]["mime_type"]
        file_type = file_types[file_ending]["file_type"]

    # Create document data
    document_version_dict = {
        "document_id": document_id,
        "session_file_id": "",
        "version_index": 1,
        "version_number": "1",
        "creation_date": doc_db.timestamp(),
        "title": file.filename,
        "original_file_name": file.filename,
        "file_ending": file_ending,
        "mime_type": mime_type,
        "file_type": file_type,
        "project": project,
        "file_description": {"name": name, "size_in_bytes": file_size},
    }

    document_version_model = Document(**document_version_dict)

    # Save file to disc
    upload_directory = "./data/documents/"
    destination_path = os.path.join(upload_directory, name)
    with open(destination_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # create database record
    inserted_document = doc_db.create_node_for_uploaded_file(selection_session, project, document_version_model)
    print("Created node for document id: " + str(inserted_document.document_id))
    doc_db.create_ifc_graph_for_document(inserted_document.document_id)

    # return document version of database record
    return inserted_document
