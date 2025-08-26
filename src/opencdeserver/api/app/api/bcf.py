from uuid import UUID
from fastapi import APIRouter, Depends, UploadFile, HTTPException
from fastapi.responses import FileResponse

from security.secure import get_current_active_user

from models.bcf_request import *
from models.bcf_response import *
from models.request import *
from models.other import *

from repository.bcf import bcf_db

from api.logging import LoggingRoute


router = APIRouter(route_class=LoggingRoute)

# ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ----
#
#
# BCF API (endpoints below only applies to BCF API versions 2.1 and 1.0)


# @router.get("/bcf/versions")
# def versions_get():
#     return {"What": "Returns a list of all supported BCF API versions of the server."}
#
#
# @router.get("/bcf/3.0/auth")
# def auth_get(version: str):
#     return {"What": "Obtaining Authentication Information."}
#
#
# @router.get("/bcf/3.0/current-user")
# def current_user_get(version: str):
#     return {"What": "Get current user."}


# ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ----
#
#
# Projects


@router.get("/bcf/3.0/projects", tags=["projects_get"])
def projects_get(current_user: User = Depends(get_current_active_user)) -> list[ProjectGET]:
    projects_response = bcf_db.get_projects(current_user)
    bcf_db.debug(
        endpoint="projects_get",
        request={},
        response={count: value.dict() for count, value in enumerate(projects_response)},
    )
    return projects_response


@router.get("/bcf/3.0/projects/{project_id}", tags=["project_get"])
def project_get(project_id: UUID, current_user: User = Depends(get_current_active_user)) -> ProjectGET:
    project_response = bcf_db.get_project(project_id, current_user)
    bcf_db.debug(endpoint="project_get", request={"project_id": project_id}, response=project_response.dict())
    return project_response


@router.put("/bcf/3.0/projects/{project_id}", tags=["project_put"], status_code=200)
def project_put(
    project_id: UUID, project_request: ProjectPUT, current_user: User = Depends(get_current_active_user)
) -> ProjectGET:
    project_response = bcf_db.put_project(project_id, project_request, current_user)
    bcf_db.debug(
        endpoint="project_put",
        request={"project_id": project_id, "project_request": project_request},
        response=project_response.dict(),
    )
    return project_response


@router.get("/bcf/3.0/projects/{project_id}/extensions", tags=["project_extensions_get"])
def project_extensions_get(project_id: UUID, current_user: User = Depends(get_current_active_user)) -> ExtensionsGET:
    extensions_response = bcf_db.get_project_extensions(project_id, current_user)
    bcf_db.debug(
        endpoint="project_extensions_get", request={"project_id": project_id}, response=extensions_response.dict()
    )
    return extensions_response


# ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ----
#
#
# Topics


@router.get("/bcf/3.0/projects/{project_id}/topics", tags=["topics_get"])
def topics_get(project_id: str, current_user: User = Depends(get_current_active_user)) -> list[TopicGET]:
    topics_response = bcf_db.get_topics(project_id, current_user)
    bcf_db.debug(
        endpoint="topics_get",
        request={"project_id": project_id},
        response={count: value.dict() for count, value in enumerate(topics_response)},
    )
    return topics_response


@router.post("/bcf/3.0/projects/{project_id}/topics", tags=["topic_post"], status_code=201)
def topic_post(
    project_id: UUID, topic_request: TopicPOST, current_user: User = Depends(get_current_active_user)
) -> TopicGET:
    topic_response = bcf_db.post_topic(project_id, topic_request, current_user)
    if topic_response is None:
        raise HTTPException(status_code=400, detail="Could not create topic.")
    bcf_db.debug(
        endpoint="topic_post",
        request={"project_id": project_id, "topic_request": topic_request.dict()},
        response=topic_response.dict(),
    )
    return topic_response


# Implemented
@router.get("/bcf/3.0/projects/{project_id}/topics/{topic_id}", tags=["topic_get"])
def topic_get(project_id: UUID, topic_id: UUID, current_user: User = Depends(get_current_active_user)) -> TopicGET:
    topic_response = bcf_db.get_topic(project_id, topic_id, current_user)
    if topic_response is None:
        raise HTTPException(status_code=404, detail="Item not found.")
    bcf_db.debug(
        endpoint="topic_get", request={"project_id": project_id, "topic_id": topic_id}, response=topic_response.dict()
    )
    return topic_response


# Implemented
@router.put("/bcf/3.0/projects/{project_id}/topics/{topic_id}", tags=["topic_put"], status_code=200)
def topic_put(
    project_id: UUID, topic_id: UUID, topic_request: TopicPUT, current_user: User = Depends(get_current_active_user)
) -> TopicGET:
    topic_response = bcf_db.put_topic(project_id, topic_id, topic_request, current_user)
    bcf_db.debug(
        endpoint="topic_put",
        request={"project_id": project_id, "topic_id": topic_id, "topic_request": topic_request.dict()},
        response=topic_response.dict(),
    )
    return topic_response


# Implemented
@router.delete("/bcf/3.0/projects/{project_id}/topics/{topic_id}", tags=["topic_delete"], status_code=200)
def topic_delete(project_id: UUID, topic_id: UUID, current_user: User = Depends(get_current_active_user)) -> int:
    topic_response = bcf_db.delete_topic(project_id, topic_id, current_user)
    if topic_response is None:
        raise HTTPException(status_code=404, detail="Item not found.")
    bcf_db.debug(
        endpoint="topic_delete", request={"project_id": project_id, "topic_id": topic_id}, response={topic_response}
    )
    return topic_response


# ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ----
#
#
# BIM snippets (not used by any client)


# Implemented
@router.get("/bcf/3.0/projects/{project_id}/topics/{topic_id}/snippet", tags=["bim_snippet_get"])
def bim_snippet_get(
    project_id: UUID, topic_id: UUID, current_user: User = Depends(get_current_active_user)
) -> BimSnippet:
    bim_snippet_response = bcf_db.get_bim_snippet(project_id, topic_id, current_user)
    if bim_snippet_response is None:
        raise HTTPException(status_code=404, detail="Item not found.")
    bcf_db.debug(
        endpoint="bim_snippet_get",
        request={"project_id": project_id, "topic_id": topic_id},
        response=bim_snippet_response.dict(),
    )
    return bim_snippet_response


# Implemented
@router.put("/bcf/3.0/projects/{project_id}/topics/{topic_id}/snippet", tags=["bim_snippet_put"], status_code=200)
def bim_snippet_put(
    project_id: UUID, topic_id: UUID, snippet: BimSnippet, current_user: User = Depends(get_current_active_user)
) -> BimSnippet:
    bim_snippet_response = bcf_db.put_bim_snippet(project_id, topic_id, snippet, current_user)
    bcf_db.debug(
        endpoint="bim_snippet_put",
        request={"project_id": project_id, "topic_id": topic_id, "snippet": snippet.dict()},
        response=bim_snippet_response.dict(),
    )
    return bim_snippet_response


# ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ----
#
#
# Files


@router.get("/bcf/3.0/projects/{project_id}/files_information", tags=["files_information_get"])
def files_information_get(
    project_id: UUID, current_user: User = Depends(get_current_active_user)
) -> list[ProjectFileInformation]:
    files_information_response = bcf_db.get_files_information(project_id, current_user)
    bcf_db.debug(
        endpoint="files_information_get",
        request={"project_id": project_id},
        response={count: value.dict() for count, value in enumerate(files_information_response)},
    )
    return files_information_response


# Implemented
@router.get("/bcf/3.0/projects/{project_id}/topics/{topic_id}/files", tags=["files_get"])
def files_get(project_id: UUID, topic_id: UUID, current_user: User = Depends(get_current_active_user)) -> list[FileGET]:
    files_response = bcf_db.get_files(project_id, topic_id, current_user)
    bcf_db.debug(
        endpoint="files_get",
        request={"project_id": project_id, "topic_id": topic_id},
        response={count: value.dict() for count, value in enumerate(files_response)},
    )
    return files_response


# request body file = FilePUT
@router.put("/bcf/3.0/projects/{project_id}/topics/{topic_id}/files", tags=["files_put"], status_code=200)
def files_put(
    project_id: UUID, topic_id: UUID, files: list[FilePUT], current_user: User = Depends(get_current_active_user)
) -> list[FileGET]:
    files_response = bcf_db.put_files(project_id, topic_id, files, current_user)
    bcf_db.debug(
        endpoint="files_put",
        request={
            "project_id": project_id,
            "topic_id": topic_id,
            "files": {count: value.dict() for count, value in enumerate(files)},
        },
        response={count: value.dict() for count, value in enumerate(files_response)},
    )
    return files_response


# ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ----
#
#
# Comments


@router.get("/bcf/3.0/projects/{project_id}/topics/{topic_id}/comments", tags=["comments_get"])
def comments_get(
    project_id: UUID, topic_id: UUID, current_user: User = Depends(get_current_active_user)
) -> list[CommentGET]:
    comments_response = bcf_db.get_comments(project_id, topic_id, current_user)
    bcf_db.debug(
        endpoint="comments_get",
        request={"project_id": project_id, "topic_id": topic_id},
        response={count: value.dict() for count, value in enumerate(comments_response)},
    )
    return comments_response


# request body comment = CommentPOST
@router.post("/bcf/3.0/projects/{project_id}/topics/{topic_id}/comments", tags=["comment_post"], status_code=201)
def comment_post(
    project_id: UUID, topic_id: UUID, comment: CommentPOST, current_user: User = Depends(get_current_active_user)
) -> CommentGET:
    comment_response = bcf_db.post_comment(project_id, topic_id, comment, current_user)
    bcf_db.debug(
        endpoint="comment_post",
        request={"project_id": project_id, "topic_id": topic_id, "comment": comment},
        response=comment_response.dict(),
    )
    return comment_response


@router.get("/bcf/3.0/projects/{project_id}/topics/{topic_id}/comments/{comment_id}", tags=["comment_get"])
def comment_get(
    project_id: UUID, topic_id: UUID, comment_id: UUID, current_user: User = Depends(get_current_active_user)
) -> CommentGET:
    comment_response = bcf_db.get_comment(project_id, topic_id, comment_id, current_user)
    bcf_db.debug(
        endpoint="comment_get",
        request={"project_id": project_id, "topic_id": topic_id, "comment_id": comment_id},
        response=comment_response.dict(),
    )
    return comment_response


# request body comment = CommentPUT
@router.put(
    "/bcf/3.0/projects/{project_id}/topics/{topic_id}/comments/{comment_id}", tags=["comment_put"], status_code=200
)
def comment_put(
    project_id: UUID,
    topic_id: UUID,
    comment_id: UUID,
    comment: CommentPUT,
    current_user: User = Depends(get_current_active_user),
) -> CommentGET:
    comment_response = bcf_db.put_comment(project_id, topic_id, comment_id, comment, current_user)
    bcf_db.debug(
        endpoint="comment_put",
        request={"project_id": project_id, "topic_id": topic_id, "comment": comment},
        response=comment_response.dict(),
    )
    return comment_response


# Implemented
@router.delete(
    "/bcf/3.0/projects/{project_id}/topics/{topic_id}/comments/{comment_id}", tags=["comment_delete"], status_code=200
)
def comment_delete(
    project_id: UUID, topic_id: UUID, comment_id: UUID, current_user: User = Depends(get_current_active_user)
) -> int:
    comment_response = bcf_db.delete_comment(project_id, topic_id, comment_id, current_user)
    if comment_response is None:
        raise HTTPException(status_code=404, detail="Item not found.")
    bcf_db.debug(
        endpoint="comment_delete",
        request={"project_id": project_id, "topic_id": topic_id, "comment_id": comment_id},
        response={comment_response},
    )
    return comment_response


# ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ----
#
#
# Viewpoints


@router.get("/bcf/3.0/projects/{project_id}/topics/{topic_id}/viewpoints", tags=["viewpoints_get"])
def viewpoints_get(
    project_id: UUID, topic_id: UUID, current_user: User = Depends(get_current_active_user)
) -> list[ViewpointGET]:
    viewpoints_response = bcf_db.get_viewpoints(project_id, topic_id, current_user)
    bcf_db.debug(
        endpoint="viewpoints_get",
        request={"project_id": project_id, "topic_id": topic_id},
        response={count: value.dict() for count, value in enumerate(viewpoints_response)},
    )
    return viewpoints_response


# request body viewpoint = viewpointPOST
@router.post("/bcf/3.0/projects/{project_id}/topics/{topic_id}/viewpoints", tags=["viewpoint_post"], status_code=201)
def viewpoint_post(
    project_id: UUID, topic_id: UUID, viewpoint: ViewpointPOST, current_user: User = Depends(get_current_active_user)
) -> ViewpointGET:
    viewpoint_response = bcf_db.post_viewpoint(project_id, topic_id, viewpoint, current_user)
    bcf_db.debug(
        endpoint="viewpoint_post",
        request={"project_id": project_id, "topic_id": topic_id, "viewpoint": viewpoint.dict()},
        response=viewpoint_response.dict(),
    )
    return viewpoint_response


@router.get("/bcf/3.0/projects/{project_id}/topics/{topic_id}/viewpoints/{viewpoint_id}", tags=["viewpoint_get"])
def viewpoint_get(
    project_id: UUID, topic_id: UUID, viewpoint_id: UUID, current_user: User = Depends(get_current_active_user)
) -> ViewpointGET:
    viewpoint_response = bcf_db.get_viewpoint(project_id, topic_id, viewpoint_id, current_user)
    bcf_db.debug(
        endpoint="viewpoint_get",
        request={"project_id": project_id, "topic_id": topic_id, "viewpoint_id": viewpoint_id},
        response=viewpoint_response.dict(),
    )
    return viewpoint_response


@router.get(
    "/bcf/3.0/projects/{project_id}/topics/{topic_id}/viewpoints/{viewpoint_id}/snapshot",
    tags=["viewpoint_snapshot_get"],
)
async def viewpoint_snapshot_get(
    project_id: UUID, topic_id: UUID, viewpoint_id: UUID, current_user: User = Depends(get_current_active_user)
) -> FileResponse:
    viewpoint_snapshot_response = bcf_db.get_viewpoint_snapshot(project_id, topic_id, viewpoint_id, current_user)
    bcf_db.debug(
        endpoint="viewpoint_snapshot_get",
        request={"project_id": project_id, "topic_id": topic_id, "viewpoint_id": viewpoint_id},
        response=viewpoint_snapshot_response,
    )
    snapshot_name = "snapshot_" + str(viewpoint_id)
    file_ending = "." + viewpoint_snapshot_response.split("/", 2)[1]
    snapshot_path = "data/snapshots/" + snapshot_name + file_ending
    snapshot_type = viewpoint_snapshot_response
    return FileResponse(path=snapshot_path, media_type=snapshot_type)


@router.get(
    "/bcf/3.0/projects/{project_id}/topics/{topic_id}/viewpoints/{viewpoint_id}/bitmaps/{bitmap_id}",
    tags=["viewpoint_bitmap_get"],
)
async def viewpoint_bitmap_get(
    project_id: UUID,
    topic_id: UUID,
    viewpoint_id: UUID,
    bitmap_id: UUID,
    current_user: User = Depends(get_current_active_user),
) -> FileResponse:
    viewpoint_bitmap_response = bcf_db.get_viewpoint_bitmap(project_id, topic_id, viewpoint_id, bitmap_id, current_user)
    bcf_db.debug(
        endpoint="viewpoint_bitmap_get",
        request={"project_id": project_id, "topic_id": topic_id, "viewpoint_id": viewpoint_id, "bitmap_id": bitmap_id},
        response=viewpoint_bitmap_response.dict(),
    )
    bitmap_name = "bitmap_" + str(viewpoint_id)
    file_ending = "." + viewpoint_bitmap_response["bitmap_type"].split("/", 2)[1]
    bitmap_path = "data/bitmaps/" + bitmap_name + file_ending
    bitmap_type = viewpoint_bitmap_response["bitmap_type"]
    return FileResponse(path=bitmap_path, media_type=bitmap_type)


@router.get(
    "/bcf/3.0/projects/{project_id}/topics/{topic_id}/viewpoints/{viewpoint_id}/coloring",
    tags=["viewpoint_colored_components_get"],
)
def viewpoint_colored_components_get(
    project_id: UUID, topic_id: UUID, viewpoint_id: UUID, current_user: User = Depends(get_current_active_user)
) -> ColoringGET:
    viewpoint_colored_components_response = bcf_db.get_viewpoint_colored_components(
        project_id, topic_id, viewpoint_id, current_user
    )
    bcf_db.debug(
        endpoint="viewpoint_colored_components_get",
        request={"project_id": project_id, "topic_id": topic_id, "viewpoint_id": viewpoint_id},
        response=viewpoint_colored_components_response.dict(),
    )
    return viewpoint_colored_components_response


@router.get(
    "/bcf/3.0/projects/{project_id}/topics/{topic_id}/viewpoints/{viewpoint_id}/selection",
    tags=["viewpoint_selected_components_get"],
)
def viewpoint_selected_components_get(
    project_id: UUID, topic_id: UUID, viewpoint_id: UUID, current_user: User = Depends(get_current_active_user)
) -> SelectionGET:
    viewpoint_selected_components_response = bcf_db.get_viewpoint_selected_components(
        project_id, topic_id, viewpoint_id, current_user
    )
    bcf_db.debug(
        endpoint="viewpoint_selected_components_get",
        request={"project_id": project_id, "topic_id": topic_id, "viewpoint_id": viewpoint_id},
        response=viewpoint_selected_components_response.dict(),
    )
    return viewpoint_selected_components_response


@router.get(
    "/bcf/3.0/projects/{project_id}/topics/{topic_id}/viewpoints/{viewpoint_id}/visibility",
    tags=["viewpoint_components_visibility_get"],
)
def viewpoint_components_visibility_get(
    project_id: UUID, topic_id: UUID, viewpoint_id: UUID, current_user: User = Depends(get_current_active_user)
) -> VisibilityGET:
    viewpoint_components_visibility_response = bcf_db.get_viewpoint_components_visibility(
        project_id, topic_id, viewpoint_id, current_user
    )
    bcf_db.debug(
        endpoint="viewpoint_components_visibility_get",
        request={"project_id": project_id, "topic_id": topic_id, "viewpoint_id": viewpoint_id},
        response=viewpoint_components_visibility_response.dict(),
    )
    return viewpoint_components_visibility_response


# Implemented
@router.delete(
    "/bcf/3.0/projects/{project_id}/topics/{topic_id}/viewpoints/{viewpoint_id}",
    tags=["viewpoint_delete"],
    status_code=200,
)
def viewpoint_delete(
    project_id: UUID, topic_id: UUID, viewpoint_id: UUID, current_user: User = Depends(get_current_active_user)
) -> int:
    viewpoint_response = bcf_db.delete_viewpoint(project_id, topic_id, viewpoint_id, current_user)
    if viewpoint_response is None:
        raise HTTPException(status_code=404, detail="Item not found.")
    bcf_db.debug(
        endpoint="viewpoint_delete",
        request={"project_id": project_id, "topic_id": topic_id, "viewpoint_id": viewpoint_id},
        response={viewpoint_response},
    )
    return viewpoint_response


# ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ----
#
#
# Related topics


@router.get("/bcf/3.0/projects/{project_id}/topics/{topic_id}/related_topics", tags=["related_topics_get"])
def related_topics_get(
    project_id: UUID, topic_id: UUID, current_user: User = Depends(get_current_active_user)
) -> list[RelatedTopicGET]:
    related_topics_response = bcf_db.get_related_topics(project_id, topic_id, current_user)
    bcf_db.debug(
        endpoint="related_topics_get",
        request={"project_id": project_id, "topic_id": topic_id},
        response={count: value.dict() for count, value in enumerate(related_topics_response)},
    )
    return related_topics_response


# request body related_topic = RelatedTopicPUT
@router.put(
    "/bcf/3.0/projects/{project_id}/topics/{topic_id}/related_topics", tags=["related_topics_put"], status_code=200
)
def related_topics_put(
    project_id: UUID,
    topic_id: UUID,
    related_topics: list[RelatedTopicPUT],
    current_user: User = Depends(get_current_active_user),
) -> list[RelatedTopicGET]:
    related_topics_response = bcf_db.put_related_topics(project_id, topic_id, related_topics, current_user)
    bcf_db.debug(
        endpoint="related_topics_put",
        request={
            "project_id": project_id,
            "topic_id": topic_id,
            "related_topics": {count: value.dict() for count, value in enumerate(related_topics)},
        },
        response={count: value.dict() for count, value in enumerate(related_topics_response)},
    )
    return related_topics_response


# ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ----
#
#
# Document references <- from topic


@router.get(
    "/bcf/3.0/projects/{project_id}/topics/{topic_id}/document_references", tags=["topic_document_references_get"]
)
def topic_document_references_get(
    project_id: UUID, topic_id: UUID, current_user: User = Depends(get_current_active_user)
) -> list[DocumentReferenceGET]:
    topic_document_references_response = bcf_db.get_topic_document_references(project_id, topic_id, current_user)
    bcf_db.debug(
        endpoint="topic_document_references_get",
        request={"project_id": project_id, "topic_id": topic_id},
        response={count: value.dict() for count, value in enumerate(topic_document_references_response)},
    )
    return topic_document_references_response


# request body document_reference = DocumentReferencePOST
@router.post(
    "/bcf/3.0/projects/{project_id}/topics/{topic_id}/document_references",
    tags=["topic_document_references_post"],
    status_code=201,
)
def topic_document_reference_post(
    project_id: UUID,
    topic_id: UUID,
    document_reference: DocumentReferencePOST,
    current_user: User = Depends(get_current_active_user),
) -> DocumentReferenceGET:
    topic_document_references_response = bcf_db.post_topic_document_references(
        project_id, topic_id, document_reference, current_user
    )
    bcf_db.debug(
        endpoint="topic_document_references_post",
        request={"project_id": project_id, "topic_id": topic_id, "document_reference": document_reference},
        response={count: value.dict() for count, value in enumerate(topic_document_references_response)},
    )
    return topic_document_references_response


# request body document_reference = DocumentReferencePUT
@router.put(
    "/bcf/3.0/projects/{project_id}/topics/{topic_id}/document_references/{reference_id}",
    tags=["topic_document_references_put"],
    status_code=200,
)
def topic_document_references_put(
    project_id: UUID,
    topic_id: UUID,
    reference_id: UUID,
    document_reference: DocumentReferencePUT,
    current_user: User = Depends(get_current_active_user),
) -> DocumentReferenceGET:
    topic_document_references_response = bcf_db.put_topic_document_references(
        project_id, topic_id, reference_id, document_reference, current_user
    )
    bcf_db.debug(
        endpoint="topic_document_references_put",
        request={
            "project_id": project_id,
            "topic_id": topic_id,
            "reference_id": reference_id,
            "document_reference": document_reference.dict(),
        },
        response={count: value.dict() for count, value in enumerate(topic_document_references_response)},
    )
    return topic_document_references_response


# ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ----
#
#
# Documents project


@router.get("/bcf/3.0/projects/{project_id}/documents", tags=["documents_get"])
def documents_get(project_id: UUID, current_user: User = Depends(get_current_active_user)) -> list[DocumentGET]:
    documents_response = bcf_db.get_documents(project_id, current_user)
    bcf_db.debug(
        endpoint="documents_get",
        request={"project_id": project_id},
        response={count: value.dict() for count, value in enumerate(documents_response)},
    )
    return documents_response


# request body file = UploadFile
@router.post("/bcf/3.0/projects/{project_id}/documents", tags=["document_post"], status_code=201)
async def document_post(
    project_id: UUID, file: UploadFile, current_user: User = Depends(get_current_active_user)
) -> DocumentGET:
    document_response = bcf_db.post_document(project_id, file, current_user)
    bcf_db.debug(endpoint="document_post", request={"project_id": project_id}, response=document_response.dict())
    return document_response


@router.get("/bcf/3.0/projects/{project_id}/documents/{document_id}", tags=["document_get"])
def document_get(
    project_id: UUID, document_id: UUID, current_user: User = Depends(get_current_active_user)
) -> DocumentGET:
    document_response = bcf_db.get_document(project_id, document_id, current_user)
    bcf_db.debug(
        endpoint="document_get",
        request={"project_id": project_id, "document_id": document_id},
        response=document_response.dict(),
    )
    return document_response


# ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ----
#
#
# Topics events


# ...
@router.get("/bcf/3.0/projects/{project_id}/topics/events", tags=["topics_events_get"])
def topics_events_get(project_id: UUID, current_user: User = Depends(get_current_active_user)) -> list[TopicEventGET]:
    topic_events_response = bcf_db.get_topics_events(project_id, current_user)
    bcf_db.debug(
        endpoint="topics_events_get",
        request={"project_id": project_id},
        response={count: value.dict() for count, value in enumerate(topic_events_response)},
    )
    return topic_events_response


@router.get("/bcf/3.0/projects/{project_id}/topics/{topic_id}/events", tags=["topic_events_get"])
def topic_events_get(
    project_id: UUID, topic_id: UUID, current_user: User = Depends(get_current_active_user)
) -> list[TopicEventGET]:
    topic_events_response = bcf_db.get_topic_events(project_id, topic_id, current_user)
    bcf_db.debug(
        endpoint="topic_events_get",
        request={"project_id": project_id, "topic_id": topic_id},
        response={count: value.dict() for count, value in enumerate(topic_events_response)},
    )
    return topic_events_response


# ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ----
#
#
# Comments events


@router.get("/bcf/3.0/projects/{project_id}/topics/comments/events", tags=["comments_events_get"])
def comments_events_get(
    project_id: UUID, current_user: User = Depends(get_current_active_user)
) -> list[CommentEventGET]:
    comments_events_response = bcf_db.get_comments_events(project_id, current_user)
    bcf_db.debug(
        endpoint="comments_events_get",
        request={"project_id": project_id},
        response={count: value.dict() for count, value in enumerate(comments_events_response)},
    )
    return comments_events_response


@router.get(
    "/bcf/3.0/projects/{project_id}/topics/{topic_id}/comments/{comment_id}/events", tags=["comment_events_get"]
)
def comment_events_get(
    project_id: UUID, topic_id: UUID, comment_id: UUID, current_user: User = Depends(get_current_active_user)
) -> list[CommentEventGET]:
    comment_events_response = bcf_db.get_comment_events(project_id, topic_id, comment_id, current_user)
    bcf_db.debug(
        endpoint="comment_events_get",
        request={"project_id": project_id, "topic_id": topic_id, "comment_id": comment_id},
        response={count: value.dict() for count, value in enumerate(comment_events_response)},
    )
    return comment_events_response
