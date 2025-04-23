import collections
import os
import traceback
import sys

from fastapi import APIRouter, Request, Depends
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.encoders import jsonable_encoder

from uuid import UUID

from pydantic import ValidationError
from security.secure import get_current_active_user

from repository.documents import doc_db

from models.documents_request import *
from models.documents_response import *
from models.documents_other import *

from api.logging import LoggingRoute

router = APIRouter(route_class=LoggingRoute)

templates = Jinja2Templates(directory="templates")

################################################################
# UPLOAD FLOW
################################################################


@router.post("/user/1.0/upload-documents", tags=[""])
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
@router.get("/user/1.0/document-upload", tags=[""], response_class=HTMLResponse)
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


@router.post("/user/1.0/save-metadata-for-documents", tags=[""])
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


@router.post("/user/1.0/upload-part/{part_id}", tags=[""])
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


################################################################
# DOWNLOAD FLOW
################################################################


@router.get("/user/1.0/document/{document_id}/version/{version_index}/download", tags=[""])
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
