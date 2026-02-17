"""Miscellaneous PropertyGroups for 4D BIM scheduling.

This module contains miscellaneous PropertyGroup classes that don't fit into other
thematic categories:
- BIMTaskTypeColor: Legacy color system for task types
- IFCStatus: IFC status properties for visibility control
- BIMStatusProperties: Main status management properties

Each PropertyGroup maintains full compatibility with the original implementation.
"""

import bpy
from bpy.props import (
    StringProperty,
    BoolProperty,
    FloatVectorProperty,
    CollectionProperty
)
from bpy.types import PropertyGroup

try:
    from typing import TYPE_CHECKING
    if TYPE_CHECKING:
        import bpy.types
except ImportError:
    TYPE_CHECKING = False


class BIMTaskTypeColor(PropertyGroup):
    """Color by task type (legacy - maintain for compatibility)"""
    name: StringProperty(name="Name")
    animation_type: StringProperty(name="Type")
    color: FloatVectorProperty(
        name="Color",
        subtype="COLOR", size=4,
        default=(1.0, 0.0, 0.0, 1.0),
        min=0.0,
        max=1.0,
    )
    
    if TYPE_CHECKING:
        name: str
        animation_type: str
        color: tuple[float, float, float, float]


class IFCStatus(PropertyGroup):
    """IFC status properties for visibility control."""
    name: StringProperty(name="Name")
    is_visible: BoolProperty(
        name="Is Visible", 
        default=True, 
        update=lambda x, y: (None, bpy.ops.bim.activate_status_filters())[0]
    )
    
    if TYPE_CHECKING:
        name: str
        is_visible: bool


class BIMStatusProperties(PropertyGroup):
    """Main status management properties."""
    is_enabled: BoolProperty(name="Is Enabled")
    statuses: CollectionProperty(name="Statuses", type=IFCStatus)
    
    if TYPE_CHECKING:
        is_enabled: bool
        statuses: bpy.types.bpy_prop_collection_idprop[IFCStatus]