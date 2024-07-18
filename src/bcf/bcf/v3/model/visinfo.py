from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class BitmapFormat(Enum):
    PNG = "png"
    JPG = "jpg"


@dataclass(slots=True, kw_only=True)
class Component:
    originating_system: Optional[str] = field(
        default=None,
        metadata={
            "name": "OriginatingSystem",
            "type": "Element",
            "min_length": 1,
            "white_space": "collapse",
        }
    )
    authoring_tool_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "AuthoringToolId",
            "type": "Element",
            "min_length": 1,
            "white_space": "collapse",
        }
    )
    ifc_guid: Optional[str] = field(
        default=None,
        metadata={
            "name": "IfcGuid",
            "type": "Attribute",
            "length": 22,
            "pattern": r"[0-9A-Za-z_$]*",
        }
    )


@dataclass(slots=True, kw_only=True)
class Direction:
    x: float = field(
        metadata={
            "name": "X",
            "type": "Element",
            "required": True,
        }
    )
    y: float = field(
        metadata={
            "name": "Y",
            "type": "Element",
            "required": True,
        }
    )
    z: float = field(
        metadata={
            "name": "Z",
            "type": "Element",
            "required": True,
        }
    )


@dataclass(slots=True, kw_only=True)
class Point:
    x: float = field(
        metadata={
            "name": "X",
            "type": "Element",
            "required": True,
        }
    )
    y: float = field(
        metadata={
            "name": "Y",
            "type": "Element",
            "required": True,
        }
    )
    z: float = field(
        metadata={
            "name": "Z",
            "type": "Element",
            "required": True,
        }
    )


@dataclass(slots=True, kw_only=True)
class ViewSetupHints:
    spaces_visible: bool = field(
        default=False,
        metadata={
            "name": "SpacesVisible",
            "type": "Attribute",
        }
    )
    space_boundaries_visible: bool = field(
        default=False,
        metadata={
            "name": "SpaceBoundariesVisible",
            "type": "Attribute",
        }
    )
    openings_visible: bool = field(
        default=False,
        metadata={
            "name": "OpeningsVisible",
            "type": "Attribute",
        }
    )


@dataclass(slots=True, kw_only=True)
class Bitmap:
    format: BitmapFormat = field(
        metadata={
            "name": "Format",
            "type": "Element",
            "required": True,
        }
    )
    reference: str = field(
        metadata={
            "name": "Reference",
            "type": "Element",
            "required": True,
            "min_length": 1,
            "white_space": "collapse",
        }
    )
    location: Point = field(
        metadata={
            "name": "Location",
            "type": "Element",
            "required": True,
        }
    )
    normal: Direction = field(
        metadata={
            "name": "Normal",
            "type": "Element",
            "required": True,
        }
    )
    up: Direction = field(
        metadata={
            "name": "Up",
            "type": "Element",
            "required": True,
        }
    )
    height: float = field(
        metadata={
            "name": "Height",
            "type": "Element",
            "required": True,
        }
    )


@dataclass(slots=True, kw_only=True)
class ClippingPlane:
    location: Point = field(
        metadata={
            "name": "Location",
            "type": "Element",
            "required": True,
        }
    )
    direction: Direction = field(
        metadata={
            "name": "Direction",
            "type": "Element",
            "required": True,
        }
    )


@dataclass(slots=True, kw_only=True)
class ComponentColoringColorComponents:
    class Meta:
        global_type = False

    component: List[Component] = field(
        default_factory=list,
        metadata={
            "name": "Component",
            "type": "Element",
            "min_occurs": 1,
        }
    )


@dataclass(slots=True, kw_only=True)
class ComponentSelection:
    component: List[Component] = field(
        default_factory=list,
        metadata={
            "name": "Component",
            "type": "Element",
        }
    )


@dataclass(slots=True, kw_only=True)
class ComponentVisibilityExceptions:
    class Meta:
        global_type = False

    component: List[Component] = field(
        default_factory=list,
        metadata={
            "name": "Component",
            "type": "Element",
        }
    )


@dataclass(slots=True, kw_only=True)
class Line:
    start_point: Point = field(
        metadata={
            "name": "StartPoint",
            "type": "Element",
            "required": True,
        }
    )
    end_point: Point = field(
        metadata={
            "name": "EndPoint",
            "type": "Element",
            "required": True,
        }
    )


@dataclass(slots=True, kw_only=True)
class OrthogonalCamera:
    """
    Attributes
        camera_view_point:
        camera_direction:
        camera_up_vector:
        view_to_world_scale: view's visible vertical size in meters
        aspect_ratio: Proportional relationship between the width and
            the height of the view (w/h).
    """
    camera_view_point: Point = field(
        metadata={
            "name": "CameraViewPoint",
            "type": "Element",
            "required": True,
        }
    )
    camera_direction: Direction = field(
        metadata={
            "name": "CameraDirection",
            "type": "Element",
            "required": True,
        }
    )
    camera_up_vector: Direction = field(
        metadata={
            "name": "CameraUpVector",
            "type": "Element",
            "required": True,
        }
    )
    view_to_world_scale: float = field(
        metadata={
            "name": "ViewToWorldScale",
            "type": "Element",
            "required": True,
        }
    )
    aspect_ratio: float = field(
        metadata={
            "name": "AspectRatio",
            "type": "Element",
            "required": True,
            "min_exclusive": 0.0,
        }
    )


@dataclass(slots=True, kw_only=True)
class PerspectiveCamera:
    """
    Attributes
        camera_view_point:
        camera_direction:
        camera_up_vector:
        field_of_view: Vertical field of view, in degrees. It is
            currently limited to a value between 45 and 60 degrees. This
            limitation will be dropped in the next release and viewers
            should be expect values outside this range in current
            implementations.
        aspect_ratio: Proportional relationship between the width and
            the height of the view (w/h).
    """
    camera_view_point: Point = field(
        metadata={
            "name": "CameraViewPoint",
            "type": "Element",
            "required": True,
        }
    )
    camera_direction: Direction = field(
        metadata={
            "name": "CameraDirection",
            "type": "Element",
            "required": True,
        }
    )
    camera_up_vector: Direction = field(
        metadata={
            "name": "CameraUpVector",
            "type": "Element",
            "required": True,
        }
    )
    field_of_view: float = field(
        metadata={
            "name": "FieldOfView",
            "type": "Element",
            "required": True,
            "min_exclusive": 0.0,
            "max_exclusive": 180.0,
        }
    )
    aspect_ratio: float = field(
        metadata={
            "name": "AspectRatio",
            "type": "Element",
            "required": True,
            "min_exclusive": 0.0,
        }
    )


@dataclass(slots=True, kw_only=True)
class ComponentColoringColor:
    class Meta:
        global_type = False

    components: ComponentColoringColorComponents = field(
        metadata={
            "name": "Components",
            "type": "Element",
            "required": True,
        }
    )
    color: str = field(
        metadata={
            "name": "Color",
            "type": "Attribute",
            "required": True,
            "pattern": r"[0-9A-Fa-f]{6}([0-9A-Fa-f]{2})?",
        }
    )


@dataclass(slots=True, kw_only=True)
class ComponentVisibility:
    view_setup_hints: Optional[ViewSetupHints] = field(
        default=None,
        metadata={
            "name": "ViewSetupHints",
            "type": "Element",
        }
    )
    exceptions: Optional[ComponentVisibilityExceptions] = field(
        default=None,
        metadata={
            "name": "Exceptions",
            "type": "Element",
        }
    )
    default_visibility: bool = field(
        default=False,
        metadata={
            "name": "DefaultVisibility",
            "type": "Attribute",
        }
    )


@dataclass(slots=True, kw_only=True)
class VisualizationInfoBitmaps:
    class Meta:
        global_type = False

    bitmap: List[Bitmap] = field(
        default_factory=list,
        metadata={
            "name": "Bitmap",
            "type": "Element",
        }
    )


@dataclass(slots=True, kw_only=True)
class VisualizationInfoClippingPlanes:
    class Meta:
        global_type = False

    clipping_plane: List[ClippingPlane] = field(
        default_factory=list,
        metadata={
            "name": "ClippingPlane",
            "type": "Element",
        }
    )


@dataclass(slots=True, kw_only=True)
class VisualizationInfoLines:
    class Meta:
        global_type = False

    line: List[Line] = field(
        default_factory=list,
        metadata={
            "name": "Line",
            "type": "Element",
        }
    )


@dataclass(slots=True, kw_only=True)
class ComponentColoring:
    color: List[ComponentColoringColor] = field(
        default_factory=list,
        metadata={
            "name": "Color",
            "type": "Element",
        }
    )


@dataclass(slots=True, kw_only=True)
class Components:
    selection: Optional[ComponentSelection] = field(
        default=None,
        metadata={
            "name": "Selection",
            "type": "Element",
        }
    )
    visibility: Optional[ComponentVisibility] = field(
        default=None,
        metadata={
            "name": "Visibility",
            "type": "Element",
        }
    )
    coloring: Optional[ComponentColoring] = field(
        default=None,
        metadata={
            "name": "Coloring",
            "type": "Element",
        }
    )


@dataclass(slots=True, kw_only=True)
class VisualizationInfo:
    """
    VisualizationInfo documentation.
    """
    components: Optional[Components] = field(
        default=None,
        metadata={
            "name": "Components",
            "type": "Element",
        }
    )
    orthogonal_camera: Optional[OrthogonalCamera] = field(
        default=None,
        metadata={
            "name": "OrthogonalCamera",
            "type": "Element",
        }
    )
    perspective_camera: Optional[PerspectiveCamera] = field(
        default=None,
        metadata={
            "name": "PerspectiveCamera",
            "type": "Element",
        }
    )
    lines: Optional[VisualizationInfoLines] = field(
        default=None,
        metadata={
            "name": "Lines",
            "type": "Element",
        }
    )
    clipping_planes: Optional[VisualizationInfoClippingPlanes] = field(
        default=None,
        metadata={
            "name": "ClippingPlanes",
            "type": "Element",
        }
    )
    bitmaps: Optional[VisualizationInfoBitmaps] = field(
        default=None,
        metadata={
            "name": "Bitmaps",
            "type": "Element",
        }
    )
    guid: str = field(
        metadata={
            "name": "Guid",
            "type": "Attribute",
            "required": True,
            "pattern": r"[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}",
        }
    )
