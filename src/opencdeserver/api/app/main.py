from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates

from api import foundation
from api import bcf
from api import documents

endpoint_metadata = [
    {"name": "api_versions_get", "description": "/foundation/versions"},
    {"name": "foundation_auth_get", "description": "/foundation/1.0/auth"},
    {"name": "authentication_get", "description": "/authentication"},
    {"name": "login_for_access_token_post", "description": "/foundation/oauth2/token"},
    {"name": "current_user_get", "description": "/foundation/1.0/current-user"},
    {
        "name": "projects_get",
        "description": "Retrieve a collection of projects that the currently logged on user has access to.",
    },
    {
        "name": "project_get",
        "description": "Retrieve a specific project. The top level data container is known as the BCF project, "
        "with a UUID and a project name attribute.",
    },
    {
        "name": "project_put",
        "description": "Modify a specific project. This operation is only possible when the server returns the update "
        "flag in the Project authorization.",
    },
    {
        "name": "project_extensions_get",
        "description": "Retrieve a specific projects extensions. Project extensions are used to define possible values "
        "that can be used in topics and comments, for example topic labels and priorities. They may "
        "change during the course of a project. The most recent extensions state which values are valid "
        "at a given moment for newly created topics and comments.",
    },
    {
        "name": "topics_get",
        "description": "Retrieve a collection of topics related to a project (default sort order is creation_date).",
    },
    {
        "name": "topic_post",
        "description": "Add a new topic. The BCF project contains zero or more topics. Each topic represents a model "
        "issue. A topic will have a UUID, a title, description, priority, stage, labels (similar to "
        "tags), creation date / author, due date, and assigned to. If modified, it may contain the "
        "modification date and author.",
    },
    {"name": "topic_get", "description": "Retrieve a specific topic."},
    {"name": "topic_put", "description": "Modify a specific topic, description similar to POST."},
    {
        "name": "bim_snippet_get",
        "description": "Retrieves a topics BIM-Snippet as binary file. BIM snippet has been in BCF specification since "
        "the very beginning, but is has never been used. Snippets have originally been added to provide "
        "for 'changes in IFC'. To get this really working in a CDE environment changes to the IFC format "
        "is necessary.",
    },
    {
        "name": "bim_snippet_put",
        "description": "Puts a new BIM Snippet binary file to a topic. If this is used, the parent topics BIM Snippet "
        "property is_external must be set to false and the reference must be the file name with "
        "extension.",
    },
    {"name": "files_get", "description": "Retrieve a collection of file references as topic header."},
    {"name": "files_put", "description": "Update a collection of file references on the topic header."},
    {
        "name": "comments_get",
        "description": "Retrieve a collection of all comments related to a topic (default ordering is date).",
    },
    {"name": "comment_post", "description": "Add a new comment to a topic."},
    {"name": "comment_put", "description": "Update a single comment, description similar to POST."},
    {"name": "comment_get", "description": "Get a single comment."},
    {"name": "viewpoints_get", "description": "Retrieve a collection of all viewpoints related to a topic."},
    {
        "name": "viewpoint_post",
        "description": "Add a new viewpoint. Viewpoints are immutable, meaning that they should never change. "
        "Requirements for different visualizations should be handled by creating new viewpoint elements.",
    },
    {"name": "viewpoint_get", "description": "Retrieve a specific viewpoint."},
    {
        "name": "viewpoint_selected_components_get",
        "description": "Retrieve a collection of all selected components in a viewpoint.",
    },
    {
        "name": "viewpoint_colored_components_get",
        "description": "Retrieve a collection of all colored components in a viewpoint.",
    },
    {"name": "viewpoint_components_visibility_get", "description": "Retrieve visibility of components in a viewpoint."},
    {"name": "viewpoint_snapshot_get", "description": "Retrieve a specific viewpoints bitmap image file (png or jpg)."},
    {"name": "related_topics_get", "description": "Retrieve a collection of all related topics to a topic."},
    {"name": "related_topics_put", "description": "Add or update a collection of all related topics to a topic."},
    {
        "name": "topic_document_references_get",
        "description": "Retrieve a collection of all document references to a topic.",
    },
    {"name": "topic_document_references_post", "description": "Add or update document references to a topic."},
    {"name": "topic_document_references_put", "description": "Add or update document references to a topic."},
    {"name": "documents_get", "description": "Retrieve a collection of all documents uploaded to a project."},
    {"name": "document_post", "description": "Upload a document (binary file) to a project."},
    {"name": "document_get", "description": "Retrieves a document as binary file."},
    {
        "name": "topics_events_get",
        "description": "Retrieve a collection of topic events related to a project (default sort order is date).",
    },
    {
        "name": "topic_events_get",
        "description": "Retrieve a collection of topic events related to a project (default sort order is date).",
    },
    {
        "name": "comments_events_get",
        "description": "Retrieve a collection of comment events related to a project (default sort order is date).",
    },
    {
        "name": "comment_events_get",
        "description": "Retrieve a collection of comment events related to a comment (default sort order is date).",
    },
]

app = FastAPI(
    title="Kontroll API", description="Implementering av BCF API 3.0", version="0.0.1", openapi_tags=endpoint_metadata
)

# Configure app to accept requests from anywhere
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(foundation.router, prefix="")
app.include_router(bcf.router, prefix="")
app.include_router(documents.router, prefix="")

templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


favicon_path = "favicon.ico"


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse(favicon_path)
