# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021, 2022 Dion Moult <dion@thinkmoult.com>
#
# This file is part of Bonsai.
#
# Bonsai is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Bonsai is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Bonsai.  If not, see <http://www.gnu.org/licenses/>.
#
# This file was modified with the assistance of an AI coding tool.

import math
from collections.abc import Callable
from math import pi, radians
from typing import TYPE_CHECKING, Any, Literal, Optional, Union, get_args

import bpy
import ifcopenshell.util.element
from bpy.types import NodeTree, PropertyGroup
from mathutils import Vector

import bonsai.tool as tool
from bonsai.bim.module.drawing.decoration import CutDecorator
from bonsai.bim.module.model.data import AuthoringData
from bonsai.bim.module.model.decorator import (
    BoundingBoxDecorator,
    MEPSystemPathDecorator,
    SlabDirectionDecorator,
    WallAxisDecorator,
    WallSystemPathDecorator,
)
from bonsai.bim.module.model.door import update_door_modifier_bmesh
from bonsai.bim.module.model.window import update_window_modifier_bmesh
from bonsai.bim.prop import ObjProperty

if TYPE_CHECKING:
    import sverchok.node_tree


def get_ifc_class(self: "BIMModelProperties", context: bpy.types.Context) -> list[tuple[str, str, str]]:
    if not AuthoringData.is_loaded:
        AuthoringData.load()
    return AuthoringData.data["ifc_classes"]


def get_boundary_class(self: "BIMModelProperties", context: bpy.types.Context) -> list[tuple[str, str, str]]:
    if not AuthoringData.is_loaded:
        AuthoringData.load()
    return AuthoringData.data["boundary_class"]


def get_relating_type_id(self: "BIMModelProperties", context: bpy.types.Context) -> list[tuple[str, str, str]]:
    if not AuthoringData.is_loaded:
        AuthoringData.load()
    return AuthoringData.data["relating_type_id"]


def get_materials(
    self: Union["BIMWindowProperties", "BIMDoorProperties"], context: bpy.types.Context
) -> list[tuple[str, str, str]]:
    if not AuthoringData.is_loaded:
        AuthoringData.load()
    return AuthoringData.data["materials"]


def update_ifc_class(self: "BIMModelProperties", context: bpy.types.Context) -> None:
    bpy.ops.bim.load_type_thumbnails()
    AuthoringData.data["ifc_class_current"] = self.ifc_class
    AuthoringData.data["type_elements"] = AuthoringData.type_elements()
    AuthoringData.data["type_elements_filtered"] = AuthoringData.type_elements_filtered()
    AuthoringData.data["relating_type_id"] = AuthoringData.relating_type_id()
    AuthoringData.data["relating_type_data"] = AuthoringData.relating_type_data()
    if tool.Blender.get_enum_safe(self, "relating_type_id") is None:
        self["relating_type_id"] = 0

    AuthoringData.data["total_types"] = AuthoringData.total_types()
    AuthoringData.data["total_pages"] = AuthoringData.total_pages()
    AuthoringData.data["prev_page"] = AuthoringData.prev_page()
    AuthoringData.data["next_page"] = AuthoringData.next_page()
    AuthoringData.data["paginated_relating_types"] = AuthoringData.paginated_relating_types()


def update_relating_type_id(self: "BIMModelProperties", context: bpy.types.Context) -> None:
    AuthoringData.data["relating_type_id"] = AuthoringData.relating_type_id()
    AuthoringData.data["relating_type_data"] = AuthoringData.relating_type_data()
    self.type_page = [e[0] for e in AuthoringData.data["relating_type_id"]].index(self.relating_type_id) // 9 + 1


def update_type_page(self: "BIMModelProperties", context: bpy.types.Context) -> None:
    AuthoringData.data["paginated_relating_types"] = AuthoringData.paginated_relating_types()
    AuthoringData.data["next_page"] = AuthoringData.next_page()
    AuthoringData.data["prev_page"] = AuthoringData.prev_page()
    bpy.ops.bim.load_type_thumbnails()
    self["type_page"] = min(self["type_page"], AuthoringData.data["total_pages"])
    self["type_page"] = max(self["type_page"], 1)


def update_relating_array_from_object(self: "BIMArrayProperties", context: bpy.types.Context) -> None:
    # Skip the cleanup-time clear: Finish/Cancel sets relating_array_object back to None,
    # which has no source to hydrate from. Only the user-driven pick (None → some array)
    # should auto-enter edit on the picked source's layer 0.
    if self.relating_array_object is None:
        return
    bpy.ops.bim.enable_editing_array(item=0)


def is_object_array_applicable(self: "BIMArrayProperties", obj: bpy.types.Object) -> bool:
    element = tool.Ifc.get_entity(obj)
    if not element:
        return False
    return ifcopenshell.util.element.get_pset(element, "BBIM_Array")


def update_wall_axis_decorator(self: "BIMModelProperties", context: bpy.types.Context) -> None:
    if self.show_wall_axis:
        WallAxisDecorator.install(bpy.context)
    else:
        WallAxisDecorator.uninstall()


def update_slab_direction_decorator(self: "BIMModelProperties", context: bpy.types.Context) -> None:
    if self.show_slab_direction:
        SlabDirectionDecorator.install(bpy.context)
    else:
        SlabDirectionDecorator.uninstall()


def update_paths_decorator(self: "BIMModelProperties", context: bpy.types.Context) -> None:
    """Unified toggle for connected-element path overlays. Drives both the
    MEP and wall path decorators — each decorator's ``draw`` short-circuits
    when its kind of element isn't selected, so leaving both installed is
    cheap and lets one toggle cover any connected-element family."""
    if self.show_paths:
        MEPSystemPathDecorator.install(bpy.context)
        WallSystemPathDecorator.install(bpy.context)
    else:
        MEPSystemPathDecorator.uninstall()
        WallSystemPathDecorator.uninstall()


def update_measure_xyz(self: "BIMModelProperties", context: bpy.types.Context) -> None:
    if self.show_bounding_box:
        BoundingBoxDecorator.install(context)
    else:
        BoundingBoxDecorator.uninstall()


def update_cut_decorator(self: "BIMModelProperties", context: bpy.types.Context) -> None:
    if self.show_cut_decorator:
        CutDecorator.install(bpy.context)
    else:
        CutDecorator.uninstall()


def update_search_name(self: "BIMModelProperties", context: bpy.types.Context) -> None:
    AuthoringData.load()
    # Total number of pages may decrease when using the search bar :
    if self.type_page > AuthoringData.data["total_pages"]:
        self.type_page = max(1, AuthoringData.data["total_pages"])
    bpy.ops.bim.load_type_thumbnails()


def update_x_angle(self: "BIMModelProperties", context: bpy.types.Context) -> None:
    angle_deg = math.degrees(self.x_angle)
    if tool.Cad.is_x(angle_deg, -90, 0.5) or tool.Cad.is_x(angle_deg, 90, 0.5):
        self.x_angle = 0


def update_door(self: "BIMDoorProperties", context: bpy.types.Context) -> None:
    update_door_modifier_bmesh(context)


def update_window(self: "BIMWindowProperties", context: bpy.types.Context) -> None:
    update_window_modifier_bmesh(context)


# Lazy-loaded module references for parametric element updates
# Using module-level lazy loading avoids circular imports and repeated import overhead
_updater_cache: dict[str, Callable] = {}


def _get_updater(module_name: str, func_name: str) -> Callable:
    """Lazy-load an updater function to avoid circular imports.

    Args:
        module_name: Module name within bonsai.bim.module.model (e.g., "stair")
        func_name: Function name to import (e.g., "regenerate_stair_mesh")

    Returns:
        The imported function, cached for subsequent calls.
    """
    cache_key = f"{module_name}.{func_name}"
    if cache_key not in _updater_cache:
        import importlib

        module = importlib.import_module(f"bonsai.bim.module.model.{module_name}")
        _updater_cache[cache_key] = getattr(module, func_name)
    return _updater_cache[cache_key]


def update_stair(self: "BIMStairProperties", context: bpy.types.Context) -> None:
    """Regenerate stair mesh when property changes."""
    obj = context.active_object
    if obj and self.is_editing:
        _get_updater("stair", "regenerate_stair_mesh")(obj)


def update_wall(self: "BIMWallProperties", context: bpy.types.Context) -> None:
    """Regenerate wall mesh preview when property changes. Does NOT touch IFC."""
    obj = context.active_object
    if obj and self.is_editing:
        _get_updater("wall", "regenerate_wall_mesh_from_props")(obj)


def update_wall_offset_baseline(self: "BIMWallProperties", context: bpy.types.Context) -> None:
    """Recompute the preview-only ``offset`` when the draft baseline cycles. Does not touch IFC.

    ``offset`` itself has no ``update`` callback on purpose — adding one would make
    every baseline cycle rebuild the bmesh twice (once via offset's callback, once
    explicitly below)."""
    obj = context.active_object
    if not (obj and self.is_editing):
        return
    t = self.thickness
    if self.desired_offset_baseline == "CENTER":
        self.offset = -t / 2
    elif self.desired_offset_baseline == "INTERIOR":
        self.offset = -t
    else:  # EXTERIOR
        self.offset = 0.0
    _get_updater("wall", "regenerate_wall_mesh_from_props")(obj)


def update_railing(self: "BIMRailingProperties", context: bpy.types.Context) -> None:
    """Regenerate railing mesh when property changes."""
    if self.is_editing:
        _get_updater("railing", "update_railing_modifier_bmesh")(context)


def update_roof(self: "BIMRoofProperties", context: bpy.types.Context) -> None:
    """Regenerate roof mesh when property changes."""
    obj = context.active_object
    if obj and self.is_editing:
        _get_updater("roof", "update_roof_modifier_bmesh")(obj)


def update_pipe_segment(self: "BIMPipeSegmentProperties", context: bpy.types.Context) -> None:
    """Regenerate pipe-segment preview mesh from props during edit. Does NOT touch IFC."""
    obj = context.active_object
    if obj and self.is_editing:
        _get_updater("mep", "regenerate_pipe_segment_mesh_from_props")(obj)


def update_duct_segment(self: "BIMDuctSegmentProperties", context: bpy.types.Context) -> None:
    """Regenerate duct-segment preview mesh from props during edit. Does NOT touch IFC."""
    obj = context.active_object
    if obj and self.is_editing:
        _get_updater("mep", "regenerate_duct_segment_mesh_from_props")(obj)


class BIMModelProperties(PropertyGroup):
    ifc_class: bpy.props.EnumProperty(items=get_ifc_class, name="Construction Class", update=update_ifc_class)
    relating_type_id: bpy.props.EnumProperty(
        items=get_relating_type_id, name="Relating Type", update=update_relating_type_id
    )
    search_name: bpy.props.StringProperty(
        name="Search Name",
        default="",
        description="Use this property to filter the list of available types",
        update=update_search_name,
        options={"SKIP_SAVE", "TEXTEDIT_UPDATE"},
    )
    menu_relating_type_id: bpy.props.IntProperty()
    icon_id: bpy.props.IntProperty()
    updating: bpy.props.BoolProperty(default=False)
    getter_enum = {"ifc_class": get_ifc_class, "relating_type": get_relating_type_id}
    extrusion_depth: bpy.props.FloatProperty(name="Extrusion Depth", min=0.001, default=42.0, subtype="DISTANCE")
    cardinal_point: bpy.props.EnumProperty(
        items=(
            # TODO: complain to buildingSMART
            ("1", "bottom left", ""),
            ("2", "bottom centre", ""),
            ("3", "bottom right", ""),
            ("4", "mid-depth left", ""),
            ("5", "mid-depth centre", ""),
            ("6", "mid-depth right", ""),
            ("7", "top left", ""),
            ("8", "top centre", ""),
            ("9", "top right", ""),
            ("10", "geometric centroid", ""),
            ("11", "bottom in line with the geometric centroid", ""),
            ("12", "left in line with the geometric centroid", ""),
            ("13", "right in line with the geometric centroid", ""),
            ("14", "top in line with the geometric centroid", ""),
            ("15", "shear centre", ""),
            ("16", "bottom in line with the shear centre", ""),
            ("17", "left in line with the shear centre", ""),
            ("18", "right in line with the shear centre", ""),
            ("19", "top in line with the shear centre", ""),
        ),
        name="Cardinal Point",
        default="5",
    )
    length: bpy.props.FloatProperty(name="Length", default=42.0, subtype="DISTANCE")
    openings: bpy.props.CollectionProperty(type=ObjProperty)
    x: bpy.props.FloatProperty(name="X", default=0.5, subtype="DISTANCE", description="Size by X axis for the opening")
    y: bpy.props.FloatProperty(name="Y", default=0.5, subtype="DISTANCE", description="Size by Y axis for the opening")
    z: bpy.props.FloatProperty(name="Z", default=0.5, subtype="DISTANCE", description="Size by Z axis for the opening")
    rl_mode: bpy.props.EnumProperty(
        items=(
            ("BOTTOM", "Bottom", "Snaps the element's lowest geometry to the container's Z value."),
            ("CONTAINER", "Container", "Positions the element's placement origin at the container's Z value."),
            ("CURSOR", "Cursor", "Places the object placement at the 3D cursor's Z value."),
        ),
        name="RL Mode",
        default="BOTTOM",
    )
    # Used for things like walls, doors, flooring, skirting, etc
    rl1: bpy.props.FloatProperty(name="RL", default=1, subtype="DISTANCE", description="Z offset for walls")
    # Used for things like windows, other hosted furniture, and MEP
    rl2: bpy.props.FloatProperty(name="RL", default=1, subtype="DISTANCE", description="Z offset for windows")
    # Used for plan calculation points such as in room generation
    rl3: bpy.props.FloatProperty(name="RL", default=1, subtype="DISTANCE", description="Z offset for space calculation")
    type_page: bpy.props.IntProperty(name="Type Page", default=1, min=1, update=update_type_page)
    x_angle: bpy.props.FloatProperty(
        name="X Angle",
        default=0,
        subtype="ANGLE",
        min=math.radians(-180),
        max=math.radians(180),
        update=update_x_angle,
    )
    type_name: bpy.props.StringProperty(name="Name", default="TYPEX")
    boundary_class: bpy.props.EnumProperty(items=get_boundary_class, name="Boundary Class")
    direction_sense: bpy.props.EnumProperty(
        items=[("POSITIVE", "Positive", ""), ("NEGATIVE", "Negative", "")],
        name="Material Usage Direction Sense",
        default="POSITIVE",
    )
    offset_type_vertical: bpy.props.EnumProperty(
        items=[("EXTERIOR", "Exterior", ""), ("CENTER", "Center", ""), ("INTERIOR", "Interior", "")],
        name="Vertical Layer Offset Type",
        default="EXTERIOR",
        description="Offset convention to reference line",
    )
    offset_type_horizontal: bpy.props.EnumProperty(
        items=[("TOP", "Top", ""), ("CENTER", "Center", ""), ("BOTTOM", "Bottom", "")],
        name="Horizontal Layer Offset Type",
        default="TOP",
        description="Offset convention to reference line",
    )
    offset: bpy.props.FloatProperty(name="Offset", default=0.0, description="Material usage offset from reference line")
    show_wall_axis: bpy.props.BoolProperty(
        name="Show Wall Axis",
        default=False,
        update=update_wall_axis_decorator,
    )
    show_slab_direction: bpy.props.BoolProperty(
        name="Show Slab Direction",
        default=False,
        update=update_slab_direction_decorator,
    )
    show_paths: bpy.props.BoolProperty(
        name="Show Paths",
        default=False,
        update=update_paths_decorator,
        description=(
            "Trace the connected element path from the selected element. For "
            "walls, follows IfcRelConnectsPathElements and draws each "
            "connected wall's reference axis with endpoint dots. For MEP "
            "elements, follows IfcRelConnectsPorts and draws each segment's "
            "axis plus a port-to-port spider for each fitting. Toggle off to "
            "skip the BFS traversal entirely."
        ),
    )

    prev_transform_orientation_slot_type: bpy.props.StringProperty(name="Previous Gizmo Orientation Type")
    prev_show_gizmo_object_translate: bpy.props.BoolProperty(name="Previous Gizmo Translate")

    show_bounding_box: bpy.props.BoolProperty(name="Measure XYZ Dimensions", default=False, update=update_measure_xyz)
    show_cut_decorator: bpy.props.BoolProperty(
        name="Show Cut Decorator",
        default=True,
        update=update_cut_decorator,
        description="Shows the cut decorator",
    )
    show_cut_decorator_fill: bpy.props.BoolProperty(
        name="Show Cut Decorator Fill",
        default=True,
        description="Show Cut Decorator Fill",
    )

    if TYPE_CHECKING:
        ifc_class: str
        relating_type_id: str
        search_name: str
        menu_relating_type_id: int
        icon_id: int
        updating: bool
        extrusion_depth: float
        cardinal_point: Literal[
            "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19"
        ]
        length: float
        openings: bpy.types.bpy_prop_collection_idprop[ObjProperty]
        x: float
        y: float
        z: float
        rl_mode: Literal["BOTTOM", "CONTAINER", "CURSOR"]
        rl1: float
        rl2: float
        rl3: float
        type_page: int
        x_angle: float
        type_name: str
        boundary_class: str
        direction_sense: Literal["POSITIVE", "NEGATIVE"]
        offset_type_vertical: Literal["EXTERIOR", "CENTER", "INTERIOR"]
        offset_type_horizontal: Literal["TOP", "CENTER", "BOTTOM"]
        offset: float
        show_wall_axis: bool
        show_slab_direction: bool
        show_paths: bool

        prev_transform_orientation_slot_type: str
        prev_show_gizmo_object_translate: bool

        show_bounding_box: bool
        show_cut_decorator: bool
        show_cut_decorator_fill: bool


class BIMArrayProperties(PropertyGroup):
    is_editing: bpy.props.BoolProperty(
        default=False,
        description="True while an array layer is in parametric edit mode. The specific layer is in editing_item_index.",
    )
    editing_item_index: bpy.props.IntProperty(
        default=-1,
        description="Index of the array layer currently being edited; -1 when not in edit mode.",
    )
    count: bpy.props.IntProperty(name="Count", default=0, min=0)
    x: bpy.props.FloatProperty(name="X", default=0, subtype="DISTANCE")
    y: bpy.props.FloatProperty(name="Y", default=0, subtype="DISTANCE")
    z: bpy.props.FloatProperty(name="Z", default=0, subtype="DISTANCE")
    use_local_space: bpy.props.BoolProperty(
        name="Use Local Space",
        description="Use local space for array items offset instead of world space",
        default=True,
    )
    method: bpy.props.EnumProperty(
        items=(("OFFSET", "Offset", ""), ("DISTRIBUTE", "Distribute", "")),
        name="Method",
        default="OFFSET",
    )
    per_child_opening: bpy.props.BoolProperty(
        name="Per-Child Opening",
        description=(
            "When the array parent fills a wall (or any voidable host), give each array child its own opening + "
            "filling pair so the host is cut once per child. Disable to leave the host uncut by the children — "
            "only the parent's original opening remains"
        ),
        default=True,
    )
    relating_array_object: bpy.props.PointerProperty(
        type=bpy.types.Object,
        name="Copy Array Properties",
        update=update_relating_array_from_object,
        poll=is_object_array_applicable,
    )

    if TYPE_CHECKING:
        is_editing: bool
        editing_item_index: int
        count: int
        x: float
        y: float
        z: float
        use_local_space: bool
        method: Literal["OFFSET", "DISTRIBUTE"]
        per_child_opening: bool
        sync_children: bool
        relating_array_object: Union[bpy.types.Object, None]


def update_total_length_target(self: "BIMStairProperties", context: bpy.types.Context) -> None:
    """Update tread_run when total_length_target changes."""
    self.update_tread_run_from_length()
    # Must call update_stair here because self["prop"] bypasses property update callbacks
    update_stair(self, context)


def update_tread_run(self: "BIMStairProperties", context: bpy.types.Context) -> None:
    """Update either number_of_treads or total_length_target when tread_run changes."""
    if self.total_length_lock:
        # Calculate how many default treads fit in remaining space
        custom_length, custom_count = self.get_custom_tread_info()
        available_length = self.total_length_target - custom_length
        if self.tread_run > 0:
            n_default_treads = available_length / self.tread_run
            # number_of_treads = number_of_risers - 1
            self["number_of_treads"] = int(n_default_treads + custom_count - 1)
    else:
        self.update_total_length_from_treads()
    # Must call update_stair here because self["prop"] bypasses property update callbacks
    update_stair(self, context)


def update_number_of_treads(self: "BIMStairProperties", context: bpy.types.Context) -> None:
    """Update either tread_run or total_length_target when number_of_treads changes."""
    if self.total_length_lock:
        self.update_tread_run_from_length()
    else:
        self.update_total_length_from_treads()
    # Must call update_stair here because self["prop"] bypasses property update callbacks
    update_stair(self, context)


def update_custom_first_last_tread_run(self: "BIMStairProperties", context: bpy.types.Context) -> None:
    """Update tread_run or total_length when custom treads change."""
    if self.total_length_lock:
        self.update_tread_run_from_length()
    else:
        self.update_total_length_from_treads()
    # Must call update_stair here because self["prop"] bypasses property update callbacks
    update_stair(self, context)


class BIMStairProperties(PropertyGroup):
    def validate_nosing_value(self, context: bpy.types.Context) -> None:
        if self.stair_type != "WOOD/STEEL" and self.nosing_length < 0:
            self["nosing_length"] = 0
        update_stair(self, context)

    def update_custom_tread_lock(self, context: bpy.types.Context) -> None:
        """When lock is enabled, sync custom treads with tread_run"""
        if self.custom_tread_lock:
            self["custom_first_last_tread_run"] = (self.tread_run, self.tread_run)
        update_stair(self, context)

    non_si_units_props = ("is_editing", "number_of_treads", "has_top_nib", "stair_type", "custom_tread_lock")

    is_editing: bpy.props.BoolProperty(default=False)
    width: bpy.props.FloatProperty(name="Width", default=1.2, min=0.01, subtype="DISTANCE", update=update_stair)
    height: bpy.props.FloatProperty(name="Height", default=1.0, min=0.01, subtype="DISTANCE", update=update_stair)
    number_of_treads: bpy.props.IntProperty(
        name="Number of Treads", default=6, soft_min=1, min=0, update=update_number_of_treads
    )
    total_length_target: bpy.props.FloatProperty(
        name="Total Length Target",
        default=3.0,
        min=0.01,
        subtype="DISTANCE",
        update=update_total_length_target,
        description="Total Length Target, might not be exactly respected depending on the parameters",
    )
    total_length_lock: bpy.props.BoolProperty(
        default=False,
        name="Lock Total Length",
        description="Lock Total Length when changing number of treads or tread run",
    )
    tread_depth: bpy.props.FloatProperty(
        name="Tread Depth", default=0.25, min=0.01, subtype="DISTANCE", update=update_stair
    )
    tread_run: bpy.props.FloatProperty(
        name="Tread Run", default=0.3, min=0.01, subtype="DISTANCE", update=update_tread_run
    )
    base_slab_depth: bpy.props.FloatProperty(
        name="Base Slab Depth", default=0.25, min=0, subtype="DISTANCE", update=update_stair
    )
    top_slab_depth: bpy.props.FloatProperty(
        name="Top Slab Depth", default=0.25, min=0, subtype="DISTANCE", update=update_stair
    )
    has_top_nib: bpy.props.BoolProperty(name="Has Top Nib", default=True, update=update_stair)
    stair_type: bpy.props.EnumProperty(
        name="Stair Type",
        items=[(i, i.replace("/", " / ").title(), "") for i in get_args(tool.Model.StairType)],
        default="CONCRETE",
        update=validate_nosing_value,
    )
    custom_tread_lock: bpy.props.BoolProperty(
        name="Lock First/Last Treads to Tread Run",
        description="When enabled, first and last treads automatically use the Tread Run value",
        default=True,
        update=update_custom_tread_lock,
    )
    custom_first_last_tread_run: bpy.props.FloatVectorProperty(
        name="Custom First / Last Treads Widths",
        description='Specify custom first / last treads widths, different from the general "Tread Run". Leave 0 to disable.',
        default=(0, 0),
        min=0,
        unit="LENGTH",
        size=2,
        update=update_custom_first_last_tread_run,
    )
    nosing_length: bpy.props.FloatProperty(
        name="Nosing Length",
        description=(
            "Overhang of the tread, not counted as a part of the tread run.\n"
            "Can be negative for WOOD/STEEL stair (then it becomes a tread gap)"
        ),
        default=0,
        unit="LENGTH",
        update=validate_nosing_value,
    )
    nosing_depth: bpy.props.FloatProperty(
        name="Nosing Depth",
        description="Depth of the tread's nosing",
        min=0,
        default=0,
        unit="LENGTH",
        update=update_stair,
    )

    if TYPE_CHECKING:
        is_editing: bool
        width: float
        height: float
        number_of_treads: int
        total_length_target: float
        total_length_lock: bool
        tread_depth: float
        tread_run: float
        base_slab_depth: float
        top_slab_depth: float
        has_top_nib: bool
        stair_type: str
        custom_tread_lock: bool
        custom_first_last_tread_run: tuple[float, float]
        nosing_length: float
        nosing_depth: float

    def get_props_kwargs(self, convert_to_project_units=False, stair_type=None):
        if not stair_type:
            stair_type = self.stair_type
        stair_kwargs = {
            "stair_type": stair_type,
            "width": self.width,
            "height": self.height,
            "number_of_treads": self.number_of_treads,
            "tread_run": self.tread_run,
            "nosing_length": self.nosing_length,
        }

        if stair_type == "CONCRETE":
            concrete_props = {
                "nosing_depth": self.nosing_depth,
                "base_slab_depth": self.base_slab_depth,
                "top_slab_depth": self.top_slab_depth,
                "has_top_nib": self.has_top_nib,
                "tread_depth": self.tread_depth,
            }
            stair_kwargs.update(concrete_props)

        elif stair_type == "WOOD/STEEL":
            wood_steel_props = {
                "tread_depth": self.tread_depth,
            }
            stair_kwargs.update(wood_steel_props)

        elif stair_type == "GENERIC":
            generic_props = {
                "nosing_depth": self.nosing_depth,
            }
            stair_kwargs.update(generic_props)

        non_si_units_props = self.non_si_units_props
        # If locked, use tread_run for both first and last treads
        if self.custom_tread_lock:
            non_si_units_props += ("custom_first_last_tread_run",)
            stair_kwargs["custom_first_last_tread_run"] = (None, None)
        else:
            stair_kwargs["custom_first_last_tread_run"] = self.custom_first_last_tread_run

        if not convert_to_project_units:
            return stair_kwargs

        stair_kwargs = tool.Model.convert_data_to_project_units(stair_kwargs, non_si_units_props)
        return stair_kwargs

    def get_props_kwargs_for_ifc_export(self, convert_to_project_units=False, stair_type=None):
        """Get props including custom_tread_lock for saving to IFC"""
        stair_kwargs = self.get_props_kwargs(convert_to_project_units, stair_type)
        # Add the lock state for IFC storage (after getting base kwargs to avoid passing to generate function)
        stair_kwargs["custom_tread_lock"] = self.custom_tread_lock
        return stair_kwargs

    def set_props_kwargs_from_ifc_data(self, kwargs):
        kwargs = tool.Model.convert_data_to_si_units(kwargs, self.non_si_units_props)
        tread_run = kwargs.get("tread_run", 0.3)

        # Determine lock state based on whether custom treads match tread_run
        # If custom_tread_lock wasn't saved (old files), infer it from the data
        if "custom_tread_lock" not in kwargs:
            custom_treads = kwargs.get("custom_first_last_tread_run", (0.0, 0.0))
            # Lock is off if either custom tread differs from tread_run and is not 0
            kwargs["custom_tread_lock"] = all(ct not in (0.0, tread_run) for ct in custom_treads)

        if "custom_first_last_tread_run" in kwargs:
            custom_treads = kwargs["custom_first_last_tread_run"]
            custom_treads = [tread_run if v is None else v for v in custom_treads]
            kwargs["custom_first_last_tread_run"] = custom_treads

        for prop_name in kwargs:
            setattr(self, prop_name, kwargs[prop_name])

    def copy_to(self, target_props: "BIMStairProperties") -> None:
        """Copy preset values to target stair properties."""
        target_props.custom_tread_lock = self.custom_tread_lock
        for prop_name, prop_value in self.get_props_kwargs().items():
            # Skip custom_first_last_tread_run if it contains None values (when lock is enabled)
            if prop_name == "custom_first_last_tread_run" and None in prop_value:
                continue
            setattr(target_props, prop_name, prop_value)

    def is_concrete_stair(self) -> bool:
        return self.stair_type == "CONCRETE"

    def has_nosing(self) -> bool:
        return self.nosing_length != 0.0 and self.stair_type != "WOOD/STEEL"

    def has_custom_treads(self) -> bool:
        return not self.custom_tread_lock

    def has_tread_run_gizmo(self) -> bool:
        return self.custom_tread_lock or self.number_of_treads > 2

    def has_tread_depth(self) -> bool:
        return self.stair_type != "GENERIC"

    def get_riser_height(self) -> float:
        """Compute the riser height from total height and number of treads."""
        return self.height / (self.number_of_treads + 1)

    def set_riser_height(self, value: float) -> None:
        """Apply riser height by adjusting the total stair height."""
        self.height = max(0.01, value) * (self.number_of_treads + 1)

    def get_total_run(self) -> float:
        """Calculate the total horizontal run of the stair.

        Takes into account custom first/last tread runs when custom_tread_lock is False.
        """
        number_of_rises = self.number_of_treads + 1
        total_run = 0.0
        default_rises = number_of_rises

        if not self.custom_tread_lock:
            if self.custom_first_last_tread_run[0] is not None:  # May be 0 though
                default_rises -= 1
                total_run += self.custom_first_last_tread_run[0]
            if self.custom_first_last_tread_run[1] is not None:  # May be 0 though
                default_rises -= 1
                total_run += self.custom_first_last_tread_run[1]

        total_run += self.tread_run * default_rises
        return total_run

    def get_custom_tread_run(self, index: int) -> float:
        """Get custom tread run value for first (0) or last (1) tread."""
        return self.custom_first_last_tread_run[index]

    def set_custom_tread_run(self, index: int, value: float) -> None:
        """Set custom tread run value for first (0) or last (1) tread."""
        current = self.custom_first_last_tread_run
        if index == 0:
            self.custom_first_last_tread_run = (max(0.01, value), current[1])
        else:
            self.custom_first_last_tread_run = (current[0], max(0.01, value))

    def get_custom_tread_info(self) -> tuple[float, int]:
        """Calculate total custom tread length and count.

        Returns:
            Tuple of (custom_length, custom_count)
        """
        custom_length = 0.0
        custom_count = 0
        if not self.custom_tread_lock:
            if self.custom_first_last_tread_run[0] != 0:
                custom_length += self.custom_first_last_tread_run[0]
                custom_count += 1
            if self.custom_first_last_tread_run[1] != 0:
                custom_length += self.custom_first_last_tread_run[1]
                custom_count += 1
        return custom_length, custom_count

    def calculate_total_length(self) -> float:
        """Calculate total stair run length from current properties."""
        custom_length, custom_count = self.get_custom_tread_info()
        n_default_treads = self.number_of_treads + 1 - custom_count
        return custom_length + n_default_treads * self.tread_run

    def update_tread_run_from_length(self) -> None:
        """Recalculate tread_run to maintain total_length_target."""
        custom_length, custom_count = self.get_custom_tread_info()
        available_length = self.total_length_target - custom_length
        n_default_treads = self.number_of_treads + 1 - custom_count

        if n_default_treads > 0:
            self["tread_run"] = available_length / n_default_treads
        else:
            # All treads are custom, use fallback
            self["tread_run"] = self.total_length_target / (self.number_of_treads + 1)

    def update_total_length_from_treads(self) -> None:
        """Recalculate total_length_target from current tread settings."""
        self["total_length_target"] = self.calculate_total_length()


class BIMSverchokProperties(PropertyGroup):
    node_group: bpy.props.PointerProperty(name="Node Group", type=NodeTree)

    if TYPE_CHECKING:
        node_group: bpy.types.NodeTree | None


def window_type_prop_update(self, context):
    number_of_panels, panels_data = self.window_types_panels[self.window_type]
    self.first_mullion_offset, self.second_mullion_offset = panels_data[0]
    self.first_transom_offset, self.second_transom_offset = panels_data[1]
    update_window(self, context)


# default prop values are in mm and converted later
class BIMWindowProperties(PropertyGroup):
    non_si_units_props = (
        "is_editing",
        "window_type",
        "lining_material",
        "framing_material",
        "glazing_material",
    )

    # number of panels and default mullion/transom values
    # fmt: off
    window_types_panels = {
        "SINGLE_PANEL":            (1, ((0,   0  ), (0,    0  ))),
        "DOUBLE_PANEL_HORIZONTAL": (2, ((0,   0  ), (0.45, 0  ))),
        "DOUBLE_PANEL_VERTICAL":   (2, ((0.3, 0  ), (0,    0  ))),
        "TRIPLE_PANEL_BOTTOM":     (3, ((0.3, 0  ), (0.45, 0  ))),
        "TRIPLE_PANEL_TOP":        (3, ((0.3, 0  ), (0.45, 0  ))),
        "TRIPLE_PANEL_LEFT":       (3, ((0.3, 0  ), (0.45, 0  ))),
        "TRIPLE_PANEL_RIGHT":      (3, ((0.3, 0  ), (0.45, 0  ))),
        "TRIPLE_PANEL_HORIZONTAL": (3, ((0,   0  ), (0.3,  0.6))),
        "TRIPLE_PANEL_VERTICAL":   (3, ((0.2, 0.4), (0,    0  ))),
    }
    # fmt: on

    is_editing: bpy.props.BoolProperty(default=False)
    window_type: bpy.props.EnumProperty(
        name="Window Type",
        items=[(i, i, "") for i in get_args(tool.Model.WindowType)],
        default="SINGLE_PANEL",
        update=window_type_prop_update,
    )
    overall_height: bpy.props.FloatProperty(
        name="Overall Height", default=0.9, subtype="DISTANCE", update=update_window
    )
    overall_width: bpy.props.FloatProperty(name="Overall Width", default=0.6, subtype="DISTANCE", update=update_window)

    # lining properties
    lining_depth: bpy.props.FloatProperty(
        name="Lining Depth", default=0.050, min=0.001, subtype="DISTANCE", update=update_window
    )
    lining_thickness: bpy.props.FloatProperty(
        name="Lining Thickness", default=0.050, min=0.001, subtype="DISTANCE", update=update_window
    )
    lining_offset: bpy.props.FloatProperty(
        name="Lining Offset", default=0.050, subtype="DISTANCE", update=update_window
    )
    lining_to_panel_offset_x: bpy.props.FloatProperty(
        name="Lining to Panel Offset X", default=0.025, subtype="DISTANCE", update=update_window
    )
    lining_to_panel_offset_y: bpy.props.FloatProperty(
        name="Lining to Panel Offset Y", default=0.025, subtype="DISTANCE", update=update_window
    )
    mullion_thickness: bpy.props.FloatProperty(
        name="Mullion Thickness", default=0.050, subtype="DISTANCE", update=update_window
    )
    first_mullion_offset: bpy.props.FloatProperty(
        name="First Mullion Offset",
        description="Distance from the first lining to the first mullion center",
        default=0.3,
        subtype="DISTANCE",
        update=update_window,
    )
    second_mullion_offset: bpy.props.FloatProperty(
        name="Second Mullion Offset",
        description="Distance from the first lining to the second mullion center",
        default=0.45,
        subtype="DISTANCE",
        update=update_window,
    )
    transom_thickness: bpy.props.FloatProperty(
        name="Transom Thickness", default=0.050, min=0.001, subtype="DISTANCE", update=update_window
    )
    first_transom_offset: bpy.props.FloatProperty(
        name="First Transom Offset",
        description="Distance from the first lining to the first transom center",
        default=0.3,
        min=0.001,
        subtype="DISTANCE",
        update=update_window,
    )
    second_transom_offset: bpy.props.FloatProperty(
        name="Second Transom Offset",
        description="Distance from the first lining to the second transom center",
        default=0.6,
        subtype="DISTANCE",
        update=update_window,
    )

    # panel properties
    frame_depth: bpy.props.FloatVectorProperty(
        name="Frame Depth", size=3, default=[0.035] * 3, subtype="TRANSLATION", update=update_window
    )
    frame_thickness: bpy.props.FloatVectorProperty(
        name="Frame Thickness", size=3, default=[0.035] * 3, subtype="TRANSLATION", update=update_window
    )

    # Material properties
    lining_material: bpy.props.EnumProperty(name="Lining Material", items=get_materials, options=set())
    framing_material: bpy.props.EnumProperty(name="Framing Material", items=get_materials, options=set())
    glazing_material: bpy.props.EnumProperty(name="Glazing Material", items=get_materials, options=set())

    if TYPE_CHECKING:
        is_editing: bool
        window_type: tool.Model.WindowType
        overall_height: float
        overall_width: float
        lining_depth: float
        lining_thickness: float
        lining_offset: float
        lining_to_panel_offset_x: float
        lining_to_panel_offset_y: float
        mullion_thickness: float
        first_mullion_offset: float
        second_mullion_offset: float
        first_transom_offset: float
        second_transom_offset: float

        # Panel properties.
        frame_depth: tuple[float, float, float]
        frame_thickness: tuple[float, float, float]

        # Material properties.
        lining_material: str
        framing_material: str
        glazing_material: str

    def get_general_kwargs(self, convert_to_project_units: bool = False) -> dict[str, Any]:
        kwargs = {
            "window_type": self.window_type,
            "overall_height": self.overall_height,
            "overall_width": self.overall_width,
        }
        if not convert_to_project_units:
            return kwargs
        return tool.Model.convert_data_to_project_units(kwargs, ["window_type"])

    def get_lining_kwargs(
        self, window_type: Optional[tool.Model.WindowType] = None, convert_to_project_units: bool = False
    ) -> dict[str, Any]:
        if not window_type:
            window_type = self.window_type
        kwargs = {
            "lining_depth": self.lining_depth,
            "lining_thickness": self.lining_thickness,
            "lining_offset": self.lining_offset,
            "lining_to_panel_offset_x": self.lining_to_panel_offset_x,
            "lining_to_panel_offset_y": self.lining_to_panel_offset_y,
        }

        if window_type in (
            "DOUBLE_PANEL_VERTICAL",
            "TRIPLE_PANEL_BOTTOM",
            "TRIPLE_PANEL_TOP",
            "TRIPLE_PANEL_LEFT",
            "TRIPLE_PANEL_RIGHT",
            "TRIPLE_PANEL_VERTICAL",
        ):
            kwargs["mullion_thickness"] = self.mullion_thickness
            kwargs["first_mullion_offset"] = self.first_mullion_offset

        if window_type in (
            "DOUBLE_PANEL_HORIZONTAL",
            "TRIPLE_PANEL_BOTTOM",
            "TRIPLE_PANEL_TOP",
            "TRIPLE_PANEL_LEFT",
            "TRIPLE_PANEL_RIGHT",
            "TRIPLE_PANEL_HORIZONTAL",
        ):
            kwargs["transom_thickness"] = self.transom_thickness
            kwargs["first_transom_offset"] = self.first_transom_offset

        if window_type in ("TRIPLE_PANEL_VERTICAL",):
            kwargs["second_mullion_offset"] = self.second_mullion_offset

        if window_type in ("TRIPLE_PANEL_HORIZONTAL",):
            kwargs["second_transom_offset"] = self.second_transom_offset

        if not convert_to_project_units:
            return kwargs
        return tool.Model.convert_data_to_project_units(kwargs)

    def get_panel_kwargs(self, convert_to_project_units: bool = False) -> dict[str, Any]:
        kwargs = {
            "frame_depth": self.frame_depth,
            "frame_thickness": self.frame_thickness,
        }
        if not convert_to_project_units:
            return kwargs
        return tool.Model.convert_data_to_project_units(kwargs)

    def set_props_kwargs_from_ifc_data(self, kwargs: dict[str, Any]):
        kwargs = tool.Model.convert_data_to_si_units(kwargs, self.non_si_units_props)
        for prop_name in kwargs:
            setattr(self, prop_name, kwargs[prop_name])

    def copy_to(self, target_props: "BIMWindowProperties") -> None:
        """Copy preset values to target window properties, excluding materials."""
        exclude_props = {"lining_material", "framing_material", "glazing_material"}
        for kwargs_dict in (self.get_general_kwargs(), self.get_lining_kwargs(), self.get_panel_kwargs()):
            for prop_name, prop_value in kwargs_dict.items():
                if prop_name not in exclude_props:
                    setattr(target_props, prop_name, prop_value)

    # Window type feature mapping - centralized configuration for all window type checks
    # Each window type maps to its features: mullion, second_mullion, transom, second_transom, panels
    WINDOW_TYPE_FEATURES: dict[str, dict[str, bool | int]] = {
        "SINGLE_PANEL": {"panels": 1},
        "DOUBLE_PANEL_VERTICAL": {"mullion": True, "panels": 2},
        "DOUBLE_PANEL_HORIZONTAL": {"transom": True, "panels": 2},
        "TRIPLE_PANEL_BOTTOM": {"mullion": True, "transom": True, "panels": 3},
        "TRIPLE_PANEL_TOP": {"mullion": True, "transom": True, "panels": 3},
        "TRIPLE_PANEL_LEFT": {"mullion": True, "transom": True, "panels": 3},
        "TRIPLE_PANEL_RIGHT": {"mullion": True, "transom": True, "panels": 3},
        "TRIPLE_PANEL_HORIZONTAL": {"transom": True, "second_transom": True, "panels": 3},
        "TRIPLE_PANEL_VERTICAL": {"mullion": True, "second_mullion": True, "panels": 3},
    }

    def _get_feature(self, feature: str, default: bool | int = False) -> bool | int:
        return self.WINDOW_TYPE_FEATURES.get(self.window_type, {}).get(feature, default)

    def has_mullion(self) -> bool:
        return bool(self._get_feature("mullion"))

    def has_second_mullion(self) -> bool:
        return bool(self._get_feature("second_mullion"))

    def has_transom(self) -> bool:
        return bool(self._get_feature("transom"))

    def has_second_transom(self) -> bool:
        return bool(self._get_feature("second_transom"))

    def has_second_panel(self) -> bool:
        return int(self._get_feature("panels", 1)) >= 2

    def has_third_panel(self) -> bool:
        return int(self._get_feature("panels", 1)) >= 3

    def get_lining_to_panel_offset_y_full(self) -> float:
        """Get the full Y offset for lining-to-panel positioning."""
        return (self.lining_depth - self.frame_depth[0]) + self.lining_to_panel_offset_y

    def get_panel_geometry(self, panel_index: int) -> tuple[float, float, float, float]:
        """Get panel geometry (x_offset, z_offset, height, center_z) for a given panel index.

        Args:
            panel_index: 0 for first panel, 1 for second, 2 for third

        Returns:
            Tuple of (x_offset, z_offset, height, center_z)
        """
        window_type = self.window_type

        if panel_index == 0:
            # First panel position and height
            if window_type == "DOUBLE_PANEL_HORIZONTAL":
                x, z = 0, self.first_transom_offset
            elif window_type == "TRIPLE_PANEL_HORIZONTAL":
                x, z = 0, self.second_transom_offset
            elif window_type in ("TRIPLE_PANEL_BOTTOM", "TRIPLE_PANEL_RIGHT", "TRIPLE_PANEL_TOP"):
                x, z = 0, self.first_transom_offset
            else:
                x, z = 0, 0

            if window_type == "TRIPLE_PANEL_HORIZONTAL":
                height = self.overall_height - self.second_transom_offset
            elif window_type in (
                "DOUBLE_PANEL_HORIZONTAL",
                "TRIPLE_PANEL_BOTTOM",
                "TRIPLE_PANEL_RIGHT",
                "TRIPLE_PANEL_TOP",
            ):
                height = self.overall_height - self.first_transom_offset
            else:
                height = self.overall_height

        elif panel_index == 1:
            # Second panel position and height
            if window_type == "DOUBLE_PANEL_VERTICAL":
                x, z = self.first_mullion_offset, 0
            elif window_type == "DOUBLE_PANEL_HORIZONTAL":
                x, z = 0, 0
            elif window_type in ("TRIPLE_PANEL_BOTTOM", "TRIPLE_PANEL_LEFT", "TRIPLE_PANEL_RIGHT"):
                x, z = self.first_mullion_offset, self.first_transom_offset
            elif window_type == "TRIPLE_PANEL_TOP":
                x, z = 0, 0
            elif window_type == "TRIPLE_PANEL_HORIZONTAL":
                x, z = 0, self.first_transom_offset
            elif window_type == "TRIPLE_PANEL_VERTICAL":
                x, z = self.first_mullion_offset, 0
            else:
                x, z = 0, 0

            if window_type == "DOUBLE_PANEL_HORIZONTAL":
                height = self.first_transom_offset
            elif window_type == "DOUBLE_PANEL_VERTICAL":
                height = self.overall_height
            elif window_type in ("TRIPLE_PANEL_BOTTOM", "TRIPLE_PANEL_LEFT", "TRIPLE_PANEL_RIGHT"):
                height = self.overall_height - self.first_transom_offset
            elif window_type == "TRIPLE_PANEL_TOP":
                height = self.first_transom_offset
            elif window_type == "TRIPLE_PANEL_HORIZONTAL":
                height = self.second_transom_offset - self.first_transom_offset
            elif window_type == "TRIPLE_PANEL_VERTICAL":
                height = self.overall_height
            else:
                height = self.overall_height

        else:  # panel_index == 2
            # Third panel position and height
            if window_type in ("TRIPLE_PANEL_BOTTOM", "TRIPLE_PANEL_RIGHT", "TRIPLE_PANEL_HORIZONTAL"):
                x, z = 0, 0
            elif window_type in ("TRIPLE_PANEL_TOP", "TRIPLE_PANEL_LEFT"):
                x, z = self.first_mullion_offset, 0
            elif window_type == "TRIPLE_PANEL_VERTICAL":
                x, z = self.second_mullion_offset, 0
            else:
                x, z = 0, 0

            height = self.overall_height if window_type == "TRIPLE_PANEL_VERTICAL" else self.first_transom_offset

        center_z = z + height / 2
        return x, z, height, center_z

    def get_frame_position(self, panel_index: int, is_depth: bool) -> Vector:
        """Get frame gizmo position for a given panel.

        Args:
            panel_index: 0 for first panel, 1 for second, 2 for third
            is_depth: True for depth gizmo, False for thickness gizmo

        Returns:
            Position vector for the gizmo
        """
        x_offset, _, _, center_z = self.get_panel_geometry(panel_index)
        frame_depth = self.frame_depth[panel_index]
        y_full = (self.lining_depth - frame_depth) + self.lining_to_panel_offset_y
        y_pos = y_full + frame_depth + self.lining_offset
        return Vector((x_offset + self.lining_to_panel_offset_x, y_pos, center_z))

    def get_frame_value(self, attr_name: str, panel_index: int) -> float:
        """Get frame property value (frame_depth or frame_thickness) for a specific panel.

        Args:
            attr_name: Property name ("frame_depth" or "frame_thickness")
            panel_index: Panel index (0, 1, or 2)

        Returns:
            The value at the specified panel index
        """
        return getattr(self, attr_name)[panel_index]

    def set_frame_value(self, attr_name: str, panel_index: int, value: float) -> None:
        """Set frame property value (frame_depth or frame_thickness) for a specific panel.

        Args:
            attr_name: Property name ("frame_depth" or "frame_thickness")
            panel_index: Panel index (0, 1, or 2)
            value: New value (clamped to min 0.0)
        """
        current = getattr(self, attr_name)
        new_value = tuple(current[:panel_index]) + (max(0.0, value),) + tuple(current[panel_index + 1 :])
        setattr(self, attr_name, new_value)


class BIMDoorProperties(PropertyGroup):
    non_si_units_props = (
        "is_editing",
        "door_type",
        "panel_width_ratio",
        "lining_material",
        "framing_material",
        "glazing_material",
    )
    is_editing: bpy.props.BoolProperty(default=False)
    door_type: bpy.props.EnumProperty(
        name="Door Operation Type",
        items=tuple((i, i, "") for i in get_args(tool.Model.DoorType)),
        default="SINGLE_SWING_LEFT",
        update=update_door,
    )
    overall_height: bpy.props.FloatProperty(
        name="Overall Height",
        default=2.0,
        min=0,
        subtype="DISTANCE",
        update=update_door,
    )
    overall_width: bpy.props.FloatProperty(
        name="Overall Width",
        default=0.9,
        min=0,
        subtype="DISTANCE",
        update=update_door,
    )

    # lining properties
    lining_depth: bpy.props.FloatProperty(
        name="Lining Depth",
        default=0.050,
        min=0.001,
        subtype="DISTANCE",
        update=update_door,
    )
    lining_thickness: bpy.props.FloatProperty(
        name="Lining Thickness",
        default=0.050,
        min=0.001,
        subtype="DISTANCE",
        update=update_door,
    )
    lining_offset: bpy.props.FloatProperty(
        name="Lining Offset",
        description="Offset from the outer side of the wall (by Y-axis). "
        "If present then adding casing is not possible.\n"
        "`0.025 mm` is good as default value",
        default=0.0,
        subtype="DISTANCE",
        update=update_door,
    )
    lining_to_panel_offset_x: bpy.props.FloatProperty(
        name="Lining to Panel Offset X", default=0.025, subtype="DISTANCE", update=update_door
    )
    lining_to_panel_offset_y: bpy.props.FloatProperty(
        name="Lining to Panel Offset Y", default=0.025, subtype="DISTANCE", update=update_door
    )

    transom_thickness: bpy.props.FloatProperty(
        name="Transom Thickness",
        description="Set values > 0 to add a transom.\n" "`0.050 mm` is good as default value",
        default=0.000,
        min=0,
        subtype="DISTANCE",
        update=update_door,
    )
    transom_offset: bpy.props.FloatProperty(
        name="Transom Offset",
        description="Distance from the bottom door opening to the beginning of the transom (unlike windows)",
        default=1.525,
        min=0,
        subtype="DISTANCE",
        update=update_door,
    )

    casing_thickness: bpy.props.FloatProperty(
        name="Casing Thickness",
        description="Set values > 0 and LiningOffset = 0 to add a casing.",
        default=0.075,
        min=0,
        subtype="DISTANCE",
        update=update_door,
    )
    casing_depth: bpy.props.FloatProperty(
        name="Casing Depth",
        default=0.005,
        min=0.001,
        subtype="DISTANCE",
        update=update_door,
    )

    threshold_thickness: bpy.props.FloatProperty(
        name="Threshold Thickness",
        description="Set values > 0 to add a threshold.",
        default=0.025,
        min=0,
        subtype="DISTANCE",
        update=update_door,
    )
    threshold_depth: bpy.props.FloatProperty(
        name="Threshold Depth",
        default=0.1,
        min=0.001,
        subtype="DISTANCE",
        update=update_door,
    )
    threshold_offset: bpy.props.FloatProperty(
        name="Threshold Offset",
        description="`0.025 mm` is good as default value",
        default=0.000,
        subtype="DISTANCE",
        update=update_door,
    )

    # panel properties
    panel_depth: bpy.props.FloatProperty(
        name="Panel Depth",
        default=0.035,
        min=0,
        subtype="DISTANCE",
        update=update_door,
    )
    panel_width_ratio: bpy.props.FloatProperty(
        name="Panel Width Ratio",
        description="Width of this panel, given as ratio " "relative to the total clear opening width of the door",
        default=1.0,
        soft_min=0,
        soft_max=1,
        update=update_door,
    )
    frame_thickness: bpy.props.FloatProperty(
        name="Window Frame Thickness",
        default=0.035,
        min=0,
        subtype="DISTANCE",
        update=update_door,
    )
    frame_depth: bpy.props.FloatProperty(
        name="Window Frame Depth",
        default=0.035,
        min=0,
        subtype="DISTANCE",
        update=update_door,
    )

    # Material properties
    lining_material: bpy.props.EnumProperty(name="Lining Material", items=get_materials, options=set())
    framing_material: bpy.props.EnumProperty(name="Framing Material", items=get_materials, options=set())
    glazing_material: bpy.props.EnumProperty(name="Glazing Material", items=get_materials, options=set())

    if TYPE_CHECKING:
        is_editing: bool
        door_type: tool.Model.DoorType
        overall_height: float
        overall_width: float

        # Lining.
        lining_depth: float
        lining_thickness: float
        lining_offset: float
        lining_to_panel_offset_x: float
        lining_to_panel_offset_y: float

        # Transom.
        transom_thickness: float
        transom_offset: float

        # Casing.
        casing_thickness: float
        casing_depth: float

        # Threshold.
        threshold_thickness: float
        threshold_depth: float
        threshold_offset: float

        # Panel.
        panel_depth: float
        panel_width_ratio: float
        frame_thickness: float
        frame_depth: float

        # Material.
        panel_material: str
        lining_material: str
        glazing_material: str

    def get_general_kwargs(self, convert_to_project_units=False):
        kwargs = {
            "door_type": self.door_type,
            "overall_height": self.overall_height,
            "overall_width": self.overall_width,
        }
        if not convert_to_project_units:
            return kwargs
        return tool.Model.convert_data_to_project_units(kwargs, ["door_type"])

    def get_lining_kwargs(self, convert_to_project_units=False, door_type=None, lining_data=None):
        if not door_type:
            door_type = self.door_type

        transom_thickness = lining_data["transom_thickness"] if lining_data else self.transom_thickness
        lining_offset = lining_data["lining_offset"] if lining_data else self.lining_offset
        threshold_thickness = lining_data["threshold_thickness"] if lining_data else self.threshold_thickness

        kwargs = {
            "lining_depth": self.lining_depth,
            "lining_thickness": self.lining_thickness,
            "lining_offset": lining_offset,
        }

        if "SLIDING" not in door_type:
            kwargs["lining_to_panel_offset_x"] = self.lining_to_panel_offset_x
            kwargs["lining_to_panel_offset_y"] = self.lining_to_panel_offset_y

        kwargs["transom_thickness"] = transom_thickness
        if transom_thickness:
            kwargs["transom_offset"] = self.transom_offset

        if not lining_offset:
            kwargs["casing_thickness"] = self.casing_thickness
            if self.casing_thickness:
                kwargs["casing_depth"] = self.casing_depth

        kwargs["threshold_thickness"] = threshold_thickness
        if threshold_thickness:
            kwargs["threshold_depth"] = self.threshold_depth
            kwargs["threshold_offset"] = self.threshold_offset

        if not convert_to_project_units:
            return kwargs
        return tool.Model.convert_data_to_project_units(kwargs)

    def get_panel_kwargs(self, convert_to_project_units=False, lining_data=None):
        transom_thickness = lining_data["transom_thickness"] if lining_data else self.transom_thickness
        kwargs = {"panel_depth": self.panel_depth, "panel_width_ratio": self.panel_width_ratio}

        if transom_thickness:
            kwargs["frame_thickness"] = self.frame_thickness
            kwargs["frame_depth"] = self.frame_depth

        if not convert_to_project_units:
            return kwargs
        return tool.Model.convert_data_to_project_units(kwargs, ("panel_width_ratio",))

    def set_props_kwargs_from_ifc_data(self, kwargs):
        kwargs = tool.Model.convert_data_to_si_units(kwargs, self.non_si_units_props)
        for prop_name in kwargs:
            setattr(self, prop_name, kwargs[prop_name])

    def copy_to(self, target_props: "BIMDoorProperties") -> None:
        """Copy properties to target door properties, excluding materials."""
        exclude_props = {"lining_material", "framing_material", "glazing_material"}
        for kwargs_dict in (self.get_general_kwargs(), self.get_lining_kwargs(), self.get_panel_kwargs()):
            for prop_name, prop_value in kwargs_dict.items():
                if prop_name not in exclude_props:
                    setattr(target_props, prop_name, prop_value)

    def has_threshold_depth(self) -> bool:
        """Check if threshold depth gizmo should be visible (has threshold)."""
        return self.threshold_thickness > 0.0

    def has_transom(self) -> bool:
        """Check if transom-related gizmos should be visible (has transom)."""
        return self.transom_thickness > 0.0

    def has_casing(self) -> bool:
        """Check if casing gizmos should be visible (no lining offset)."""
        return self.lining_offset == 0.0

    def has_casing_depth(self) -> bool:
        """Check if casing depth gizmo should be visible (has casing and casing thickness > 0)."""
        return self.lining_offset == 0.0 and self.casing_thickness > 0.0

    def get_panel_center_z(self) -> float:
        """Get the vertical center of the door panel for gizmo positioning."""
        if self.transom_thickness > 0:
            return (self.transom_offset - self.threshold_thickness) / 2
        return (self.overall_height - self.threshold_thickness) / 2

    def get_transom_window_center_z(self) -> float:
        """Get the vertical center of the transom window for frame gizmo positioning."""
        return (self.transom_offset + self.transom_thickness / 2 + self.overall_height - self.lining_thickness) / 2

    def get_casing_offset(self) -> float:
        """Get casing offset for gizmo positioning (casing_thickness when lining_offset is 0)."""
        return self.casing_thickness if self.lining_offset == 0.0 else 0.0


RailingType = Literal["FRAMELESS_PANEL", "WALL_MOUNTED_HANDRAIL"]
CapType = Literal["TO_END_POST_AND_FLOOR", "TO_END_POST", "TO_FLOOR", "TO_WALL", "180", "NONE"]


class BIMRailingProperties(PropertyGroup):
    non_si_units_props = (
        "is_editing",
        "railing_type",
        "use_manual_supports",
        "terminal_type",
        "path_data",
    )

    is_editing: bpy.props.BoolProperty(default=False)
    is_editing_path: bpy.props.BoolProperty(default=False)

    railing_type: bpy.props.EnumProperty(
        name="Railing Type",
        items=[(i, i, "") for i in get_args(RailingType)],
        default="FRAMELESS_PANEL",
        update=update_railing,
    )
    height: bpy.props.FloatProperty(name="Height", default=1.0, subtype="DISTANCE", update=update_railing)
    thickness: bpy.props.FloatProperty(name="Thickness", default=0.050, subtype="DISTANCE", update=update_railing)
    spacing: bpy.props.FloatProperty(name="Spacing", default=0.050, subtype="DISTANCE", update=update_railing)

    # wall mounted handrail specific properties
    use_manual_supports: bpy.props.BoolProperty(
        name="Use Manual Supports",
        default=False,
        description="If enabled, supports are added on every vertex on the edges of the railing path.\n"
        "If disabled, supports are added automatically based on the support spacing",
        update=update_railing,
    )
    support_spacing: bpy.props.FloatProperty(
        name="Support Spacing",
        default=1.0,
        min=0.01,
        description="Distance between supports if automatic supports are used",
        subtype="DISTANCE",
        update=update_railing,
    )
    railing_diameter: bpy.props.FloatProperty(
        name="Railing Diameter", default=0.050, subtype="DISTANCE", update=update_railing
    )
    clear_width: bpy.props.FloatProperty(
        name="Clear Width",
        default=0.040,
        description="Clear width between the railing and the wall",
        subtype="DISTANCE",
        update=update_railing,
    )
    terminal_type: bpy.props.EnumProperty(
        name="Terminal Type", items=[(i, i, "") for i in get_args(CapType)], default="180", update=update_railing
    )

    if TYPE_CHECKING:
        is_editing: bool
        is_editing_path: bool

        railing_type: RailingType
        height: float
        thickness: float
        spacing: float

        use_manual_supports: bool
        support_spacing: float
        railing_diameter: float
        clear_width: float
        terminal_type: CapType

    def get_general_kwargs(self, railing_type=None, convert_to_project_units=False):
        if railing_type is None:
            railing_type = self.railing_type

        base_kwargs = {
            "railing_type": railing_type,
            "height": self.height,
        }
        additional_kwargs = {}
        if railing_type == "FRAMELESS_PANEL":
            additional_kwargs = {
                "thickness": self.thickness,
                "spacing": self.spacing,
            }
        elif railing_type == "WALL_MOUNTED_HANDRAIL":
            additional_kwargs = {
                "railing_diameter": self.railing_diameter,
                "clear_width": self.clear_width,
                "use_manual_supports": self.use_manual_supports,
                "support_spacing": self.support_spacing,
                "terminal_type": self.terminal_type,
            }
        kwargs = base_kwargs | additional_kwargs

        if not convert_to_project_units:
            return kwargs

        kwargs = tool.Model.convert_data_to_project_units(kwargs, self.non_si_units_props)
        return kwargs

    def set_props_kwargs_from_ifc_data(self, kwargs):
        kwargs = tool.Model.convert_data_to_si_units(kwargs, self.non_si_units_props)
        for prop_name in kwargs:
            setattr(self, prop_name, kwargs[prop_name])

    def copy_to(self, target_props: "BIMRailingProperties") -> None:
        """Copy preset values to target railing properties."""
        for prop_name, prop_value in self.get_general_kwargs().items():
            setattr(target_props, prop_name, prop_value)


def to_angle(percentage: float) -> float:
    return math.atan(percentage / 100)


def to_percentage(angle: float) -> float:
    return math.tan(angle) * 100


RoofType = Literal["HIP/GABLE ROOF"]
RoofGenerationMethod = Literal["HEIGHT", "ANGLE"]


class BIMRoofProperties(PropertyGroup):
    def update_angle(self, context: bpy.types.Context) -> None:
        self["angle"] = to_angle(self.percentage)
        update_roof(self, context)

    def update_percentage(self, context: bpy.types.Context) -> None:
        self["percentage"] = to_percentage(self.angle)
        update_roof(self, context)

    non_si_units_props = (
        "is_editing",
        "path_data",
        "roof_type",
        "generation_method",
        "angle",
        "percentage",
        "rafter_edge_angle",
    )

    is_editing: bpy.props.BoolProperty(default=False)
    is_editing_path: bpy.props.BoolProperty(default=False)

    roof_type: bpy.props.EnumProperty(
        name="Roof Type", items=[(i, i, "") for i in get_args(RoofType)], default="HIP/GABLE ROOF", update=update_roof
    )
    generation_method: bpy.props.EnumProperty(
        name="Roof Generation Method",
        items=[(i, i, "") for i in get_args(RoofGenerationMethod)],
        default="ANGLE",
        update=update_roof,
    )
    height: bpy.props.FloatProperty(
        name="Height",
        default=1.0,
        description="Maximum height of the roof to be generated.",
        subtype="DISTANCE",
        update=update_roof,
    )
    angle: bpy.props.FloatProperty(
        name="Slope Angle",
        default=pi / 18,
        subtype="ANGLE",
        update=update_percentage,
        min=0.0,
        max=pi / 2,
        soft_min=radians(5.0),
        soft_max=radians(60.0),
    )
    percentage: bpy.props.FloatProperty(
        name="Slope %",
        default=to_percentage(pi / 18),
        subtype="PERCENTAGE",
        update=update_angle,
        min=0.0,
        max=to_percentage(pi / 2),
        soft_min=to_percentage(radians(5.0)),
        soft_max=to_percentage(radians(60.0)),
    )
    roof_thickness: bpy.props.FloatProperty(name="Roof Thickness", default=0.1, subtype="DISTANCE", update=update_roof)
    rafter_edge_angle: bpy.props.FloatProperty(
        name="Rafter Edge Angle", min=0, max=pi / 2, default=pi / 2, subtype="ANGLE", update=update_roof
    )

    if TYPE_CHECKING:
        is_editing: bool
        is_editing_path: bool
        roof_type: Literal["HIP/GABLE ROOF"]
        generation_method: Literal["HEIGHT", "ANGLE"]
        height: float
        angle: float
        percentage: float
        roof_thickness: float
        rafter_edge_angle: float

    def get_general_kwargs(self, generation_method=None, convert_to_project_units=False):
        if generation_method is None:
            generation_method = self.generation_method
        kwargs = {
            "roof_type": self.roof_type,
            "generation_method": generation_method,
            "roof_thickness": self.roof_thickness,
            "rafter_edge_angle": self.rafter_edge_angle,
        }
        if generation_method == "HEIGHT":
            kwargs["height"] = self.height
        else:
            kwargs["angle"] = self.angle
            kwargs["percentage"] = self.percentage

        if not convert_to_project_units:
            return kwargs
        return tool.Model.convert_data_to_project_units(kwargs, self.non_si_units_props)

    def set_props_kwargs_from_ifc_data(self, kwargs):
        kwargs = tool.Model.convert_data_to_si_units(kwargs, self.non_si_units_props)
        for prop_name in kwargs:
            setattr(self, prop_name, kwargs[prop_name])

    def copy_to(self, target_props: "BIMRoofProperties") -> None:
        """Copy preset values to target roof properties."""
        for prop_name, prop_value in self.get_general_kwargs().items():
            setattr(target_props, prop_name, prop_value)


class BIMSlabProperties(PropertyGroup):
    """Transient state for the slab disconnect-access gizmo.

    ``is_editing`` flips True when the user clicks the pen icon on a slab
    that has wall connections — gating the per-wall disconnect icons in
    ``GizmoSlabUnjoinWalls`` so they're hidden until the user opts in. No
    IFC draft state lives here: the disconnect operator commits directly,
    so this PropertyGroup carries only the UI gate."""

    is_editing: bpy.props.BoolProperty(name="Slab Edit Active", default=False, options={"SKIP_SAVE"})

    if TYPE_CHECKING:
        is_editing: bool


class BIMWallProperties(PropertyGroup):
    """Transient draft state for parametric wall gizmo editing.

    Populated from IFC on `bim.enable_editing_wall`, mutated by gizmo drags during edit
    (preview only — no IFC writes), and either committed by `bim.finish_editing_wall`
    or discarded by `bim.cancel_editing_wall`.

    The `snap_*` fields are the values captured on enable; `finish_editing_wall` compares
    current vs snap to skip unchanged params and guarantee a no-op session leaves the
    IFC file byte-identical.
    """

    is_editing: bpy.props.BoolProperty(
        default=False,
        description="True while wall parametric edit mode is active.",
    )
    mesh_dirty: bpy.props.BoolProperty(
        default=False,
        options={"HIDDEN", "SKIP_SAVE"},
        description=(
            "True while the visible mesh is the preview box; cleared once the real "
            "IFC-derived geometry is restored (on commit or cancel)."
        ),
    )
    length: bpy.props.FloatProperty(
        name="Length",
        default=1.0,
        min=0.01,
        subtype="DISTANCE",
        update=update_wall,
        description="Wall length along its reference axis (preview value; committed on finish).",
    )
    height: bpy.props.FloatProperty(
        name="Height",
        default=3.0,
        min=0.01,
        subtype="DISTANCE",
        update=update_wall,
        description="Wall vertical height (preview value; committed on finish).",
    )
    x_angle: bpy.props.FloatProperty(
        name="Slope (X Angle)",
        default=0.0,
        soft_min=-math.pi / 3,
        soft_max=math.pi / 3,
        subtype="ANGLE",
        update=update_wall,
        description="Slope angle: tilt of the wall's top face along +Y (preview value; committed on finish).",
    )
    thickness: bpy.props.FloatProperty(
        name="Thickness",
        default=0.2,
        min=0.001,
        subtype="DISTANCE",
        description="Wall thickness captured from IFC at edit-enable; not gizmo-bound.",
    )
    offset: bpy.props.FloatProperty(
        name="Offset",
        default=0.0,
        subtype="DISTANCE",
        description="Layer-set offset captured from IFC at edit-enable; driven by desired_offset_baseline.",
    )
    desired_offset_baseline: bpy.props.EnumProperty(
        items=[
            ("EXTERIOR", "Exterior", "Reference axis at the exterior face"),
            ("CENTER", "Center", "Reference axis at the wall centreline"),
            ("INTERIOR", "Interior", "Reference axis at the interior face"),
        ],
        name="Desired Offset Baseline",
        default="CENTER",
        update=update_wall_offset_baseline,
        description="Which face of the wall the reference axis aligns to (preview value; committed on finish).",
    )
    anchor_x: bpy.props.FloatProperty(
        default=0.0,
        subtype="DISTANCE",
        description="Local-X of the wall's axis polyline start, so the preview box lands where the IFC mesh does.",
    )

    snap_length: bpy.props.FloatProperty(description="Snapshot of length at edit-enable; commit skips no-op writes.")
    snap_height: bpy.props.FloatProperty(description="Snapshot of height at edit-enable; commit skips no-op writes.")
    snap_thickness: bpy.props.FloatProperty(
        description="Snapshot of thickness at edit-enable; commit skips no-op writes."
    )
    snap_offset: bpy.props.FloatProperty(description="Snapshot of offset at edit-enable; commit skips no-op writes.")
    snap_x_angle: bpy.props.FloatProperty(
        subtype="ANGLE",
        description="Snapshot of x_angle at edit-enable; commit skips no-op writes.",
    )
    snap_offset_baseline: bpy.props.StringProperty(
        default="",
        description="Snapshot of desired_offset_baseline at edit-enable; commit skips no-op writes.",
    )

    if TYPE_CHECKING:
        is_editing: bool
        mesh_dirty: bool
        length: float
        height: float
        x_angle: float
        thickness: float
        offset: float
        desired_offset_baseline: Literal["EXTERIOR", "CENTER", "INTERIOR"]
        anchor_x: float
        snap_length: float
        snap_height: float
        snap_thickness: float
        snap_offset: float
        snap_x_angle: float
        snap_offset_baseline: str


class SnapMousePoint(PropertyGroup):
    x: bpy.props.FloatProperty(name="X")
    y: bpy.props.FloatProperty(name="Y")
    z: bpy.props.FloatProperty(name="Z")
    snap_type: bpy.props.StringProperty(name="Snap Type")
    snap_object: bpy.props.StringProperty(name="Object Name")

    if TYPE_CHECKING:
        x: float
        y: float
        z: float
        snap_type: str
        snap_object: str


class PolylinePoint(PropertyGroup):
    x: bpy.props.FloatProperty(name="X")
    y: bpy.props.FloatProperty(name="Y")
    z: bpy.props.FloatProperty(name="Z")
    dim: bpy.props.StringProperty(name="Dimension")
    angle: bpy.props.StringProperty(name="Angle")
    position: bpy.props.FloatVectorProperty(name="Decorator Position", size=3)

    if TYPE_CHECKING:
        x: float
        y: float
        z: float
        dim: str
        angle: str
        position: tuple[float, float, float]


class Polyline(PropertyGroup):
    id: bpy.props.StringProperty(name="Id")
    polyline_points: bpy.props.CollectionProperty(type=PolylinePoint)
    measurement_type: bpy.props.StringProperty(name="Measurement Type")
    area: bpy.props.StringProperty(name="Measured Area")
    total_length: bpy.props.StringProperty(name="Total Length")

    if TYPE_CHECKING:
        id: str
        polyline_points: bpy.types.bpy_prop_collection_idprop[PolylinePoint]
        measurement_type: str
        area: str
        total_length: str


class BIMPolylineProperties(PropertyGroup):
    snap_mouse_point: bpy.props.CollectionProperty(type=SnapMousePoint)
    snap_mouse_ref: bpy.props.CollectionProperty(type=SnapMousePoint)
    insertion_polyline: bpy.props.CollectionProperty(type=Polyline)
    measurement_polyline: bpy.props.CollectionProperty(type=Polyline)

    if TYPE_CHECKING:
        snap_mouse_point: bpy.types.bpy_prop_collection_idprop[SnapMousePoint]
        snap_mouse_ref: bpy.types.bpy_prop_collection_idprop[SnapMousePoint]
        insertion_polyline: bpy.types.bpy_prop_collection_idprop[Polyline]
        measurement_polyline: bpy.types.bpy_prop_collection_idprop[Polyline]


class ProductPreviewItem(PropertyGroup):
    value_3d: bpy.props.FloatVectorProperty()
    value_2d: bpy.props.FloatVectorProperty(size=2)

    if TYPE_CHECKING:
        value_3d: tuple[float, float, float]
        value_2d: tuple[float, float]


def update_is_editing(self: "BIMExternalParametricGeometryProperties", context: bpy.types.Context) -> None:
    if self.is_editing:
        return

    assert isinstance(self.id_data, bpy.types.Object)
    tool.Model.clean_up_parametric_geometry(self.id_data)
    self.property_unset("is_editing")
    self.property_unset("geo_nodes")
    self.property_unset("sverchok_nodes")


def update_geo_nodes(self: "BIMExternalParametricGeometryProperties", context: bpy.types.Context) -> None:
    assert isinstance(self.id_data, bpy.types.Object)

    if self.geo_nodes:
        tool.Model.setup_parametric_geometry(self.id_data)
        return

    modifier = tool.Model.get_epg_modifier(self.id_data)
    assert modifier
    modifier.show_viewport = False
    del self["geo_nodes"]


def poll_sverchok_nodes(self: "BIMExternalParametricGeometryProperties", node_tree: bpy.types.NodeTree) -> bool:
    return node_tree.bl_idname == "SverchCustomTreeType"


class BIMExternalParametricGeometryProperties(bpy.types.PropertyGroup):
    is_editing: bpy.props.BoolProperty(
        name="Is Editing Paramteric Geometry",
        description="Toggle editing parametric geometry.",
        default=False,
        update=update_is_editing,
    )
    geometry_source: bpy.props.EnumProperty(
        name="Geometry Source",
        items=[
            ("GEONODES", "Geometry Nodes", ""),
            ("IFCSVERCHOK", "IFC Sverchok", ""),
        ],
    )
    geo_nodes: bpy.props.PointerProperty(
        name="Geometry Nodes",
        description="Geometry nodes tree to use as a source for representation.",
        type=bpy.types.GeometryNodeTree,
        update=update_geo_nodes,
        poll=lambda self, node_tree: not node_tree.name.startswith("BBIM_EPG"),
    )

    sverchok_nodes: bpy.props.PointerProperty(
        name="Sverchok Nodes",
        description="Sverchok node tree to use as a source for representation.",
        type=bpy.types.NodeTree,
        poll=poll_sverchok_nodes,
    )

    if TYPE_CHECKING:
        is_editing: bool
        geometry_source: Literal["GEONODES", "IFCSVERCHOK"]
        geo_nodes: Union[bpy.types.GeometryNodeTree, None]
        sverchok_nodes: Union[sverchok.node_tree.SverchCustomTree, None]


class BIMPipeSegmentProperties(PropertyGroup):
    """Transient draft state for parametric pipe-segment gizmo editing."""

    is_editing: bpy.props.BoolProperty(
        default=False,
        description="True while pipe-segment parametric edit mode is active.",
    )
    mesh_dirty: bpy.props.BoolProperty(
        default=False,
        options={"HIDDEN", "SKIP_SAVE"},
        description=(
            "True while the visible mesh is the preview shape; cleared once the "
            "real IFC-derived geometry is restored (on commit or cancel)."
        ),
    )
    length: bpy.props.FloatProperty(
        name="Length",
        default=1.0,
        min=0.01,
        subtype="DISTANCE",
        update=update_pipe_segment,
        description="Pipe-segment extrusion length (preview value; committed on finish).",
    )
    snap_length: bpy.props.FloatProperty(
        description="Snapshot of length at edit-enable; commit skips no-op writes.",
    )
    snap_object_scale_z: bpy.props.FloatProperty(
        default=1.0,
        description=(
            "Snapshot of obj.scale.z at edit-enable. Cancel / no-op-finish restore "
            "this exact value so a user's non-identity pre-edit scale isn't silently "
            "zeroed by the scale-based preview."
        ),
    )

    if TYPE_CHECKING:
        is_editing: bool
        mesh_dirty: bool
        length: float
        snap_length: float
        snap_object_scale_z: float


class BIMDuctSegmentProperties(PropertyGroup):
    """Transient draft state for parametric duct-segment gizmo editing."""

    is_editing: bpy.props.BoolProperty(
        default=False,
        description="True while duct-segment parametric edit mode is active.",
    )
    mesh_dirty: bpy.props.BoolProperty(
        default=False,
        options={"HIDDEN", "SKIP_SAVE"},
        description=(
            "True while the visible mesh is the preview shape; cleared once the "
            "real IFC-derived geometry is restored (on commit or cancel)."
        ),
    )
    length: bpy.props.FloatProperty(
        name="Length",
        default=1.0,
        min=0.01,
        subtype="DISTANCE",
        update=update_duct_segment,
        description="Duct-segment extrusion length (preview value; committed on finish).",
    )
    snap_length: bpy.props.FloatProperty(
        description="Snapshot of length at edit-enable; commit skips no-op writes.",
    )
    snap_object_scale_z: bpy.props.FloatProperty(
        default=1.0,
        description=(
            "Snapshot of obj.scale.z at edit-enable. Cancel / no-op-finish restore "
            "this exact value so a user's non-identity pre-edit scale isn't silently "
            "zeroed by the scale-based preview."
        ),
    )

    if TYPE_CHECKING:
        is_editing: bool
        mesh_dirty: bool
        length: float
        snap_length: float
        snap_object_scale_z: float


class BIMBendPreviewProperties(PropertyGroup):
    """Scene-level pending state for the bend-creation preview flow.

    Scene-level (not per-object) because the bend involves two segments by
    IFC id — neither alone owns the draft."""

    is_active: bpy.props.BoolProperty(
        default=False,
        options={"SKIP_SAVE"},
        description="True while the bend-creation preview flow is active.",
    )
    start_segment_id: bpy.props.IntProperty(
        default=0,
        options={"SKIP_SAVE"},
        description="IFC element id of the start (active) segment.",
    )
    end_segment_id: bpy.props.IntProperty(
        default=0,
        options={"SKIP_SAVE"},
        description="IFC element id of the end (other selected) segment.",
    )
    start_length: bpy.props.FloatProperty(
        name="Start Length",
        default=0.1,
        min=0.001,
        subtype="DISTANCE",
        description="Length of the bend fitting's tangent leg on the start (active) segment side",
    )
    end_length: bpy.props.FloatProperty(
        name="End Length",
        default=0.1,
        min=0.001,
        subtype="DISTANCE",
        description="Length of the bend fitting's tangent leg on the end (other) segment side",
    )
    radius: bpy.props.FloatProperty(
        name="Radius",
        default=0.2,
        min=0.001,
        subtype="DISTANCE",
        description="Inner radius of the bend curve",
    )
    editing_bend_id: bpy.props.IntProperty(
        default=0,
        options={"SKIP_SAVE"},
        description=(
            "IFC element id of an existing bend fitting being re-edited "
            "(non-zero only on the pen-icon re-edit flow). The create "
            "operator deletes this bend + its port connections before "
            "recreating with the new parameters."
        ),
    )

    if TYPE_CHECKING:
        is_active: bool
        start_segment_id: int
        end_segment_id: int
        start_length: float
        end_length: float
        radius: float
        editing_bend_id: int


class BIMWallFilletPreviewProperties(PropertyGroup):
    """Scene-level pending state for the wall-fillet preview flow.

    Scene-level because the fillet spans two walls and commits a third
    (corner) wall between them. ``SKIP_SAVE`` fields throughout."""

    is_active: bpy.props.BoolProperty(
        default=False,
        options={"SKIP_SAVE"},
        description="True while the wall-fillet preview flow is active.",
    )
    wall_a_id: bpy.props.IntProperty(
        default=0,
        options={"SKIP_SAVE"},
        description=(
            "IFC element id of the active wall — the corner wall inherits its "
            "material layer set, height, x_angle, and type."
        ),
    )
    wall_b_id: bpy.props.IntProperty(
        default=0,
        options={"SKIP_SAVE"},
        description="IFC element id of the other selected wall.",
    )
    radius: bpy.props.FloatProperty(
        name="Radius",
        default=0.5,
        soft_min=-10.0,
        soft_max=10.0,
        subtype="DISTANCE",
        unit="LENGTH",
        options={"SKIP_SAVE"},
        description="Radius of the circular arc connecting the two walls.",
    )
    editing_corner_id: bpy.props.IntProperty(
        default=0,
        options={"SKIP_SAVE"},
        description=(
            "IFC element id of an existing fillet corner being re-edited "
            "(non-zero only on the pen-icon re-edit flow). The create "
            "operator deletes this corner + its connections before recreating "
            "with the new radius."
        ),
    )

    if TYPE_CHECKING:
        is_active: bool
        wall_a_id: int
        wall_b_id: int
        radius: float
        editing_corner_id: int


class BIMPreviewProperties(PropertyGroup):
    """Umbrella for parametric-edit preview drafts attached to ``Scene``."""

    bend: bpy.props.PointerProperty(type=BIMBendPreviewProperties)
    wall_fillet: bpy.props.PointerProperty(type=BIMWallFilletPreviewProperties)

    if TYPE_CHECKING:
        bend: BIMBendPreviewProperties
        wall_fillet: BIMWallFilletPreviewProperties


class BIMParametricEditDialogPrefs(PropertyGroup):
    """Session-scoped flag for the parametric-edit pen-icon dispatcher.

    Attached to ``WindowManager`` so the state lives for one Blender session
    and resets on restart — the right scope for "don't show this again for
    this session" toggles."""

    suppress_shared_rep_warning: bpy.props.BoolProperty(
        name="Suppress shared-representation warning",
        description=(
            "When true, the pen-icon dispatcher skips the shared-geometry "
            "confirmation dialog. Resets on Blender restart."
        ),
        default=False,
    )

    if TYPE_CHECKING:
        suppress_shared_rep_warning: bool
