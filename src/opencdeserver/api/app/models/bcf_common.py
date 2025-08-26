from pydantic import BaseModel
from typing import Optional
from enum import Enum


class BimSnippet(BaseModel):
    snippet_type: str
    is_external: str
    reference: str
    reference_schema: str


class Point(BaseModel):
    x: Optional[float] = None
    y: Optional[float] = None
    z: Optional[float] = None


class Line(BaseModel):
    start_point: Optional[Point] = None
    end_point: Optional[Point] = None


class Direction(BaseModel):
    x: Optional[float] = None
    y: Optional[float] = None
    z: Optional[float] = None


class OrthogonalCamera(BaseModel):
    camera_view_point: Optional[Point] = None
    camera_direction: Optional[Direction] = None
    camera_up_vector: Optional[Direction] = None
    view_to_world_scale: Optional[float] = None
    aspect_ratio: Optional[float] = None


class PerspectiveCamera(BaseModel):
    camera_view_point: Optional[Point] = None
    camera_direction: Optional[Direction] = None
    camera_up_vector: Optional[Direction] = None
    field_of_view: Optional[float] = None
    aspect_ratio: Optional[float] = None


class Location(BaseModel):
    x: Optional[float] = None
    y: Optional[float] = None
    z: Optional[float] = None


class ClippingPlane(BaseModel):
    location: Optional[Location] = None
    direction: Optional[Direction] = None


class SnapshotType(Enum):
    jpg = "jpg"
    png = "png"


class BitmapType(Enum):
    jpg = "jpg"
    png = "png"


class Component(BaseModel):
    ifc_guid: Optional[str] = None
    originating_system: Optional[str] = None
    authoring_tool_id: Optional[str] = None


class Coloring(BaseModel):
    color: Optional[str] = None
    components: Optional[list[Component]] = None


class ViewSetupHints(BaseModel):
    spaces_visible: Optional[bool] = False
    space_boundaries_visible: Optional[bool] = False
    openings_visible: Optional[bool] = False


class Visibility(BaseModel):
    default_visibility: Optional[bool] = False
    exceptions: Optional[list[Component]] = None
    view_setup_hints: Optional[ViewSetupHints] = None
