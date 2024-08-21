from models.bcf_common import *


class ProjectAction(Enum):
    update = "update"
    createTopic = "createTopic"
    createDocument = "createDocument"


class ProjectGETAuthorization(BaseModel):
    project_actions: Optional[List[ProjectAction]] = None


class ProjectGET(BaseModel):
    project_id: str
    name: str
    authorization: Optional[ProjectGETAuthorization] = None


class TopicAction(Enum):
    update = "update"
    updateBimSnippet = "updateBimSnippet"
    updateRelatedTopics = "updateRelatedTopics"
    updateDocumentReferences = "updateDocumentReferences"
    updateFiles = "updateFiles"
    createComment = "createComment"
    createViewpoint = "createViewpoint"
    delete = "delete"


class CommentAction(Enum):
    update = "update"
    delete = "delete"


class ExtensionsGET(BaseModel):
    topic_type: List[str]
    custom_information: List[str]
    topic_status: List[str]
    topic_label: List[str]
    snippet_type: List[str]
    priority: List[str]
    users: List[str]
    stage: List[str]
    project_actions: Optional[List[str]] = None
    topic_actions: Optional[List[str]] = None
    comment_actions: Optional[List[str]] = None


class TopicGETAuthorization(BaseModel):
    topic_actions: Optional[List[TopicAction]] = None
    topic_status: Optional[List[str]] = None


class TopicGET(BaseModel):
    guid: str
    server_assigned_id: str
    topic_type: Optional[str] = None
    topic_status: Optional[str] = None
    reference_links: Optional[List[str]] = None
    title: str
    priority: Optional[str] = None
    index: Optional[int] = None
    labels: Optional[List[str]] = None
    creation_date: str
    creation_author: str
    modified_date: Optional[str] = None
    modified_author: Optional[str] = None
    assigned_to: Optional[str] = None
    stage: Optional[str] = None
    description: Optional[str] = None
    bim_snippet: Optional[BimSnippet] = None
    due_date: Optional[str] = None
    authorization: Optional[TopicGETAuthorization] = None


class ProjectFileDisplayInformation(BaseModel):
    field_display_name: str
    field_value: str


class FileGET(BaseModel):
    ifc_project: Optional[str] = None
    ifc_spatial_structure_element: Optional[str] = None
    filename: Optional[str] = None
    date: Optional[str] = None
    reference: Optional[str] = None


class ProjectFileInformation(BaseModel):
    display_information: Optional[List[ProjectFileDisplayInformation]] = None
    file: Optional[FileGET] = None


class CommentGETAuthorization(BaseModel):
    comment_actions: Optional[List[CommentAction]] = None


class CommentGET(BaseModel):
    guid: str
    date: str
    author: str
    comment: str
    topic_guid: str
    viewpoint_guid: Optional[str] = None
    reply_to_comment_guid: Optional[str] = None
    modified_date: Optional[str] = None
    modified_author: Optional[str] = None
    authorization: Optional[CommentGETAuthorization] = None


class BitmapGET(BaseModel):
    guid: Optional[str] = None
    bitmap_type: Optional[BitmapType] = None
    location: Optional[Location] = None
    normal: Optional[Direction] = None
    up: Optional[Direction] = None
    height: Optional[float] = None


class SnapshotGET(BaseModel):
    snapshot_type: Optional[SnapshotType] = None


class ViewpointAction(Enum):
    delete = "delete"


class ViewpointGETAuthorization(BaseModel):
    viewpoint_actions: Optional[List[ViewpointAction]] = None


class ViewpointGET(BaseModel):
    index: Optional[int] = None
    guid: str
    orthogonal_camera: Optional[OrthogonalCamera] = None
    perspective_camera: Optional[PerspectiveCamera] = None
    lines: Optional[List[Line]] = None
    clipping_planes: Optional[List[ClippingPlane]] = None
    bitmaps: Optional[List[BitmapGET]] = None
    snapshot: Optional[SnapshotGET] = None
    authorization: Optional[ViewpointGETAuthorization] = None


class ColoringGET(BaseModel):
    coloring: Optional[List[Coloring]] = None


class SelectionGET(BaseModel):
    selection: Optional[List[Component]] = None


class VisibilityGET(BaseModel):
    visibility: Optional[Visibility] = None


class RelatedTopicGET(BaseModel):
    related_topic_guid: str


class DocumentReferenceGET(BaseModel):
    guid: str
    document_guid: Optional[str] = None
    url: Optional[str] = None
    description: Optional[str] = None


class DocumentGET(BaseModel):
    guid: str
    filename: str


class TopicEventGET(BaseModel):
    topic_guid: str
    date: str
    author: str


#     actions: Optional[List[EventAction]] = Field(None, min_items=1)


class CommentEventGET(BaseModel):
    comment_guid: str
    topic_guid: str
    date: str
    author: str


#     actions: Optional[List[EventAction]] = Field(None, min_items=1)


# ---- maybe not necessary now


class EventAction(BaseModel):
    type: str
    value: Optional[str] = None


class Error(BaseModel):
    message: str
