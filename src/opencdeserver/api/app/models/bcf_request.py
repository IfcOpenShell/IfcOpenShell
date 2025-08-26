from pydantic import BaseModel
from typing import Optional
from models.bcf_common import BimSnippet, BitmapType, Location, Direction, SnapshotType, Component
from models.bcf_common import Coloring, OrthogonalCamera, Visibility, PerspectiveCamera, Line, ClippingPlane


class ProjectPUT(BaseModel):
    name: str


class TopicPOST(BaseModel):
    guid: Optional[str] = None
    topic_type: Optional[str] = None
    topic_status: Optional[str] = None
    reference_links: Optional[list[str]] = None
    title: str
    priority: Optional[str] = None
    index: Optional[int] = None
    labels: Optional[list[str]] = None
    assigned_to: Optional[str] = None
    stage: Optional[str] = None
    description: Optional[str] = None
    bim_snippet: Optional[BimSnippet] = None
    due_date: Optional[str] = None


class TopicPUT(BaseModel):
    topic_type: Optional[str] = None
    topic_status: Optional[str] = None
    reference_links: Optional[list[str]] = None
    title: str
    priority: Optional[str] = None
    index: Optional[int] = None
    labels: Optional[list[str]] = None
    assigned_to: Optional[str] = None
    stage: Optional[str] = None
    description: Optional[str] = None
    bim_snippet: Optional[BimSnippet] = None
    due_date: Optional[str] = None


class FilePUT(BaseModel):
    ifc_project: Optional[str] = None
    ifc_spatial_structure_element: Optional[str] = None
    filename: Optional[str] = None
    date: Optional[str] = None
    reference: Optional[str] = None


class CommentPOST(BaseModel):
    guid: Optional[str] = None  # comment id
    comment: str
    viewpoint_guid: Optional[str] = None
    # reply_to_comment_guid: Optional[str] = None


class CommentPUT(BaseModel):
    comment: str
    viewpoint_guid: Optional[str] = None


class BitmapPOST(BaseModel):
    bitmap_type: Optional[BitmapType] = None
    bitmap_data: Optional[str] = None
    location: Optional[Location] = None
    normal: Optional[Direction] = None
    up: Optional[Direction] = None
    height: Optional[float] = None


class SnapshotPOST(BaseModel):
    snapshot_type: Optional[SnapshotType] = None
    snapshot_data: Optional[str] = None


class Components(BaseModel):
    selection: Optional[list[Component]] = None
    coloring: Optional[list[Coloring]] = None
    visibility: Optional[Visibility] = None


class ViewpointPOST(BaseModel):
    guid: Optional[str] = None
    index: Optional[int] = None
    orthogonal_camera: Optional[OrthogonalCamera] = None
    perspective_camera: Optional[PerspectiveCamera] = None
    lines: Optional[list[Line]] = None
    clipping_planes: Optional[list[ClippingPlane]] = None
    bitmaps: Optional[list[BitmapPOST]] = None
    snapshot: Optional[SnapshotPOST] = None
    components: Optional[Components] = None


class RelatedTopicPUT(BaseModel):
    related_topic_guid: str


class DocumentReferencePOST(BaseModel):
    guid: Optional[str] = None
    document_guid: Optional[str] = None
    url: Optional[str] = None
    description: Optional[str] = None


class DocumentReferencePUT(BaseModel):
    document_guid: Optional[str] = None
    url: Optional[str] = None
    description: Optional[str] = None
