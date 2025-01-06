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

import bpy
import ifcopenshell
import ifcopenshell.util.element
import bonsai.tool as tool
import math
from bonsai.bim.prop import ObjProperty
from bonsai.bim.module.model.data import AuthoringData
from bpy.types import PropertyGroup, NodeTree
from math import pi, radians


def get_ifc_class(self, context):
    if not AuthoringData.is_loaded:
        AuthoringData.load()
    return AuthoringData.data["ifc_classes"]


def get_boundary_class(self, context):
    if not AuthoringData.is_loaded:
        AuthoringData.load()
    return AuthoringData.data["boundary_class"]


def get_relating_type_id(self, context):
    if not AuthoringData.is_loaded:
        AuthoringData.load()
    return AuthoringData.data["relating_type_id"]


def update_ifc_class(self, context):
    bpy.ops.bim.load_type_thumbnails(ifc_class=self.ifc_class)
    AuthoringData.data["relating_type_id"] = AuthoringData.relating_type_id()
    AuthoringData.data["type_thumbnail"] = AuthoringData.type_thumbnail()
    if tool.Blender.get_enum_safe(self, "relating_type_id") is None:
        self["relating_type_id"] = 0

    AuthoringData.data["total_types"] = AuthoringData.total_types()
    AuthoringData.data["total_pages"] = AuthoringData.total_pages()
    AuthoringData.data["prev_page"] = AuthoringData.prev_page()
    AuthoringData.data["next_page"] = AuthoringData.next_page()
    AuthoringData.data["paginated_relating_types"] = AuthoringData.paginated_relating_types()


def update_relating_type_id(self, context):
    AuthoringData.data["relating_type_id"] = AuthoringData.relating_type_id()
    AuthoringData.data["relating_type_name"] = AuthoringData.relating_type_name()
    AuthoringData.data["type_thumbnail"] = AuthoringData.type_thumbnail()
    AuthoringData.data["predefined_type"] = AuthoringData.predefined_type()


def update_type_page(self, context):
    AuthoringData.data["paginated_relating_types"] = AuthoringData.paginated_relating_types()


def update_relating_array_from_object(self, context):
    bpy.ops.bim.enable_editing_array(item=self.is_editing)
    return


def is_object_array_applicable(self, obj):
    element = tool.Ifc.get_entity(obj)
    if not element:
        return False
    return ifcopenshell.util.element.get_pset(element, "BBIM_Array")


class BIMModelProperties(PropertyGroup):
    ifc_class: bpy.props.EnumProperty(items=get_ifc_class, name="Construction Class", update=update_ifc_class)
    relating_type_id: bpy.props.EnumProperty(
        items=get_relating_type_id, name="Relating Type", update=update_relating_type_id
    )
    menu_relating_type_id: bpy.props.IntProperty()
    icon_id: bpy.props.IntProperty()
    updating: bpy.props.BoolProperty(default=False)
    occurrence_name_style: bpy.props.EnumProperty(
        items=[("CLASS", "By Class", ""), ("TYPE", "By Type", ""), ("CUSTOM", "Custom", "")],
        name="Occurrence Name Style",
    )
    occurrence_name_function: bpy.props.StringProperty(
        name="Occurrence Name Function",
        description="Code that will be evaluated to generate occurrence name for CUSTOM occurrence name style",
    )
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
    x_angle: bpy.props.FloatProperty(name="X Angle", default=0, subtype="ANGLE", min=-pi / 180 * 89, max=pi / 180 * 89)
    type_page: bpy.props.IntProperty(name="Type Page", default=1, update=update_type_page)
    type_name: bpy.props.StringProperty(name="Name", default="TYPEX")
    boundary_class: bpy.props.EnumProperty(items=get_boundary_class, name="Boundary Class")
    direction_sense: bpy.props.EnumProperty(
        items=[("POSITIVE", "Positive", ""), ("NEGATIVE", "Negative", "")],
        name="Material Usage Direction Sense",
        default="POSITIVE",
    )
    offset_type: bpy.props.EnumProperty(
        items=[("EXTERIOR", "Exterior", ""), ("CENTER", "Center", ""), ("INTERIOR", "Interior", "")],
        name="Layer Offset Type",
        default="EXTERIOR",
        description="It's a convention that affects the offset to reference line",
    )
    offset: bpy.props.FloatProperty(name="Offset", default=0.0, description="Material usage offset from reference line")


class BIMArrayProperties(PropertyGroup):
    is_editing: bpy.props.IntProperty(
        default=-1, description="Currently edited array index. -1 if not in array editing mode."
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
    sync_children: bpy.props.BoolProperty(
        name="Sync Children",
        description="Regenerate all children based on the parent object",
        default=False,
    )
    relating_array_object: bpy.props.PointerProperty(
        type=bpy.types.Object,
        name="Copy Array Properties",
        update=update_relating_array_from_object,
        poll=is_object_array_applicable,
    )


class BIMStairProperties(PropertyGroup):
    def validate_nosing_value(self, context):
        if self.stair_type != "WOOD/STEEL" and self.nosing_length < 0:
            self["nosing_length"] = 0

    non_si_units_props = ("is_editing", "number_of_treads", "has_top_nib", "stair_type")
    stair_types = (
        ("CONCRETE", "Concrete", ""),
        ("WOOD/STEEL", "Wood / Steel", ""),
        ("GENERIC", "Generic", ""),
    )

    is_editing: bpy.props.BoolProperty(default=False)
    width: bpy.props.FloatProperty(name="Width", default=1.2, soft_min=0.01, subtype="DISTANCE")
    height: bpy.props.FloatProperty(name="Height", default=1.0, soft_min=0.01, subtype="DISTANCE")
    number_of_treads: bpy.props.IntProperty(name="Number of Treads", default=6, soft_min=1)
    tread_depth: bpy.props.FloatProperty(name="Tread Depth", default=0.25, soft_min=0.01, subtype="DISTANCE")
    tread_run: bpy.props.FloatProperty(name="Tread Run", default=0.3, soft_min=0.01, subtype="DISTANCE")
    base_slab_depth: bpy.props.FloatProperty(name="Base Slab Depth", default=0.25, soft_min=0, subtype="DISTANCE")
    top_slab_depth: bpy.props.FloatProperty(name="Top Slab Depth", default=0.25, soft_min=0, subtype="DISTANCE")
    has_top_nib: bpy.props.BoolProperty(name="Has Top Nib", default=True)
    stair_type: bpy.props.EnumProperty(
        name="Stair Type", items=stair_types, default="CONCRETE", update=validate_nosing_value
    )
    custom_first_last_tread_run: bpy.props.FloatVectorProperty(
        name="Custom First / Last Treads Widths",
        description='Specify custom first / last treads widths, different from the general "Tread Run". Leave 0 to disable.',
        default=(0, 0),
        min=0,
        unit="LENGTH",
        size=2,
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
        name="Nosing Depth", description="Depth of the tread's nosing", min=0, default=0, unit="LENGTH"
    )

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

        # defined here to appear last in UI
        stair_kwargs["custom_first_last_tread_run"] = self.custom_first_last_tread_run

        if not convert_to_project_units:
            return stair_kwargs

        stair_kwargs = tool.Model.convert_data_to_project_units(stair_kwargs, self.non_si_units_props)
        return stair_kwargs

    def set_props_kwargs_from_ifc_data(self, kwargs):
        kwargs = tool.Model.convert_data_to_si_units(kwargs, self.non_si_units_props)
        for prop_name in kwargs:
            setattr(self, prop_name, kwargs[prop_name])


class BIMSverchokProperties(PropertyGroup):
    node_group: bpy.props.PointerProperty(name="Node Group", type=NodeTree)


def window_type_prop_update(self, context):
    number_of_panels, panels_data = self.window_types_panels[self.window_type]
    self.first_mullion_offset, self.second_mullion_offset = panels_data[0]
    self.first_transom_offset, self.second_transom_offset = panels_data[1]


# default prop values are in mm and converted later
class BIMWindowProperties(PropertyGroup):
    non_si_units_props = ("is_editing", "window_type")
    window_types = (
        ("SINGLE_PANEL", "SINGLE_PANEL", ""),
        ("DOUBLE_PANEL_HORIZONTAL", "DOUBLE_PANEL_HORIZONTAL", ""),
        ("DOUBLE_PANEL_VERTICAL", "DOUBLE_PANEL_VERTICAL", ""),
        ("TRIPLE_PANEL_BOTTOM", "TRIPLE_PANEL_BOTTOM", ""),
        ("TRIPLE_PANEL_TOP", "TRIPLE_PANEL_TOP", ""),
        ("TRIPLE_PANEL_LEFT", "TRIPLE_PANEL_LEFT", ""),
        ("TRIPLE_PANEL_RIGHT", "TRIPLE_PANEL_RIGHT", ""),
        ("TRIPLE_PANEL_HORIZONTAL", "TRIPLE_PANEL_HORIZONTAL", ""),
        ("TRIPLE_PANEL_VERTICAL", "TRIPLE_PANEL_VERTICAL", ""),
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
        name="Window Type", items=window_types, default="SINGLE_PANEL", update=window_type_prop_update
    )
    overall_height: bpy.props.FloatProperty(name="Overall Height", default=0.9, subtype="DISTANCE")
    overall_width: bpy.props.FloatProperty(name="Overall Width", default=0.6, subtype="DISTANCE")

    # lining properties
    lining_depth: bpy.props.FloatProperty(name="Lining Depth", default=0.050, subtype="DISTANCE")
    lining_thickness: bpy.props.FloatProperty(name="Lining Thickness", default=0.050, subtype="DISTANCE")
    lining_offset: bpy.props.FloatProperty(name="Lining Offset", default=0.050, subtype="DISTANCE")
    lining_to_panel_offset_x: bpy.props.FloatProperty(
        name="Lining to Panel Offset X", default=0.025, subtype="DISTANCE"
    )
    lining_to_panel_offset_y: bpy.props.FloatProperty(
        name="Lining to Panel Offset Y", default=0.025, subtype="DISTANCE"
    )
    mullion_thickness: bpy.props.FloatProperty(name="Mullion Thickness", default=0.050, subtype="DISTANCE")
    first_mullion_offset: bpy.props.FloatProperty(
        name="First Mullion Offset",
        description="Distance from the first lining to the first mullion center",
        default=0.3,
        subtype="DISTANCE",
    )
    second_mullion_offset: bpy.props.FloatProperty(
        name="Second Mullion Offset",
        description="Distance from the first lining to the second mullion center",
        default=0.45,
        subtype="DISTANCE",
    )
    transom_thickness: bpy.props.FloatProperty(name="Transom Thickness", default=0.050, subtype="DISTANCE")
    first_transom_offset: bpy.props.FloatProperty(
        name="First Transom Offset",
        description="Distance from the first lining to the first transom center",
        default=0.3,
        subtype="DISTANCE",
    )
    second_transom_offset: bpy.props.FloatProperty(
        name="Second Transom Offset",
        description="Distance from the first lining to the second transom center",
        default=0.6,
        subtype="DISTANCE",
    )

    # panel properties
    frame_depth: bpy.props.FloatVectorProperty(name="Frame Depth", size=3, default=[0.035] * 3, subtype="TRANSLATION")
    frame_thickness: bpy.props.FloatVectorProperty(
        name="Frame Thickness", size=3, default=[0.035] * 3, subtype="TRANSLATION"
    )

    def get_general_kwargs(self, convert_to_project_units=False):
        kwargs = {
            "window_type": self.window_type,
            "overall_height": self.overall_height,
            "overall_width": self.overall_width,
        }
        if not convert_to_project_units:
            return kwargs
        return tool.Model.convert_data_to_project_units(kwargs, ["window_type"])

    def get_lining_kwargs(self, window_type=None, convert_to_project_units=False):
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

    def get_panel_kwargs(self, convert_to_project_units=False):
        kwargs = {
            "frame_depth": self.frame_depth,
            "frame_thickness": self.frame_thickness,
        }
        if not convert_to_project_units:
            return kwargs
        return tool.Model.convert_data_to_project_units(kwargs)

    def set_props_kwargs_from_ifc_data(self, kwargs):
        kwargs = tool.Model.convert_data_to_si_units(kwargs, self.non_si_units_props)
        for prop_name in kwargs:
            setattr(self, prop_name, kwargs[prop_name])


class BIMDoorProperties(PropertyGroup):
    non_si_units_props = ("is_editing", "door_type", "panel_width_ratio")
    door_types = (
        ("SINGLE_SWING_LEFT", "SINGLE_SWING_LEFT", ""),
        ("SINGLE_SWING_RIGHT", "SINGLE_SWING_RIGHT", ""),
        ("DOUBLE_SWING_LEFT", "DOUBLE_SWING_LEFT", ""),
        ("DOUBLE_SWING_RIGHT", "DOUBLE_SWING_RIGHT", ""),
        ("DOUBLE_DOOR_SINGLE_SWING", "DOUBLE_DOOR_SINGLE_SWING", ""),
        ("SLIDING_TO_LEFT", "SLIDING_TO_LEFT", ""),
        ("SLIDING_TO_RIGHT", "SLIDING_TO_RIGHT", ""),
        ("DOUBLE_DOOR_SLIDING", "DOUBLE_DOOR_SLIDING", ""),
    )

    is_editing: bpy.props.BoolProperty(default=False)
    door_type: bpy.props.EnumProperty(name="Door Operation Type", items=door_types, default="SINGLE_SWING_LEFT")
    overall_height: bpy.props.FloatProperty(name="Overall Height", default=2.0, subtype="DISTANCE")
    overall_width: bpy.props.FloatProperty(name="Overall Width", default=0.9, subtype="DISTANCE")

    # lining properties
    lining_depth: bpy.props.FloatProperty(name="Lining Depth", default=0.050, subtype="DISTANCE")
    lining_thickness: bpy.props.FloatProperty(name="Lining Thickness", default=0.050, subtype="DISTANCE")
    lining_offset: bpy.props.FloatProperty(
        name="Lining Offset",
        description="Offset from the outer side of the wall (by Y-axis). "
        "If present then adding casing is not possible.\n"
        "`0.025 mm` is good as default value",
        default=0.0,
        subtype="DISTANCE",
    )
    lining_to_panel_offset_x: bpy.props.FloatProperty(
        name="Lining to Panel Offset X", default=0.025, subtype="DISTANCE"
    )
    lining_to_panel_offset_y: bpy.props.FloatProperty(
        name="Lining to Panel Offset Y", default=0.025, subtype="DISTANCE"
    )

    transom_thickness: bpy.props.FloatProperty(
        name="Transom Thickness",
        description="Set values > 0 to add a transom.\n" "`0.050 mm` is good as default value",
        default=0.000,
        subtype="DISTANCE",
    )
    transom_offset: bpy.props.FloatProperty(
        name="Transom Offset",
        description="Distance from the bottom door opening to the beginning of the transom (unlike windows)",
        default=1.525,
        subtype="DISTANCE",
    )

    casing_thickness: bpy.props.FloatProperty(
        name="Casing Thickness",
        description="Set values > 0 and LiningOffset = 0 to add a casing.",
        default=0.075,
        subtype="DISTANCE",
    )
    casing_depth: bpy.props.FloatProperty(name="Casing Depth", default=0.005, subtype="DISTANCE")

    threshold_thickness: bpy.props.FloatProperty(
        name="Threshold Thickness", description="Set values > 0 to add a threshold.", default=0.025, subtype="DISTANCE"
    )
    threshold_depth: bpy.props.FloatProperty(name="Threshold Depth", default=0.1, subtype="DISTANCE")
    threshold_offset: bpy.props.FloatProperty(
        name="Threshold Offset", description="`0.025 mm` is good as default value", default=0.000, subtype="DISTANCE"
    )

    # panel properties
    panel_depth: bpy.props.FloatProperty(name="Panel Depth", default=0.035, subtype="DISTANCE")
    panel_width_ratio: bpy.props.FloatProperty(
        name="Panel Width Ratio",
        description="Width of this panel, given as ratio " "relative to the total clear opening width of the door",
        default=1.0,
        soft_min=0,
        soft_max=1,
    )
    frame_thickness: bpy.props.FloatProperty(name="Window Frame Thickness", default=0.035, subtype="DISTANCE")
    frame_depth: bpy.props.FloatProperty(name="Window Frame Depth", default=0.035, subtype="DISTANCE")

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


class BIMRailingProperties(PropertyGroup):
    non_si_units_props = (
        "is_editing",
        "railing_type",
        "use_manual_supports",
        "terminal_type",
        "path_data",
    )

    railing_types = (
        ("FRAMELESS_PANEL", "FRAMELESS_PANEL", ""),
        ("WALL_MOUNTED_HANDRAIL", "WALL_MOUNTED_HANDRAIL", ""),
    )
    cap_types = (
        ("TO_END_POST_AND_FLOOR", "TO_END_POST_AND_FLOOR", ""),
        ("TO_END_POST", "TO_END_POST", ""),
        ("TO_FLOOR", "TO_FLOOR", ""),
        ("TO_WALL", "TO_WALL", ""),
        ("180", "180", ""),
        ("NONE", "NONE", ""),
    )

    is_editing: bpy.props.BoolProperty(default=False)
    is_editing_path: bpy.props.BoolProperty(default=False)

    railing_type: bpy.props.EnumProperty(name="Railing Type", items=railing_types, default="FRAMELESS_PANEL")
    height: bpy.props.FloatProperty(name="Height", default=1.0, subtype="DISTANCE")
    thickness: bpy.props.FloatProperty(name="Thickness", default=0.050, subtype="DISTANCE")
    spacing: bpy.props.FloatProperty(name="Spacing", default=0.050, subtype="DISTANCE")

    # wall mounted handrail specific properties
    use_manual_supports: bpy.props.BoolProperty(
        name="Use Manual Supports",
        default=False,
        description="If enabled, supports are added on every vertex on the edges of the railing path.\n"
        "If disabled, supports are added automatically based on the support spacing",
    )
    support_spacing: bpy.props.FloatProperty(
        name="Support Spacing",
        default=1.0,
        min=0.01,
        description="Distance between supports if automatic supports are used",
        subtype="DISTANCE",
    )
    railing_diameter: bpy.props.FloatProperty(name="Railing Diameter", default=0.050, subtype="DISTANCE")
    clear_width: bpy.props.FloatProperty(
        name="Clear Width",
        default=0.040,
        description="Clear width between the railing and the wall",
        subtype="DISTANCE",
    )
    terminal_type: bpy.props.EnumProperty(name="Terminal Type", items=cap_types, default="180")

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


def to_angle(percentage: float) -> float:
    return math.atan(percentage / 100)


def to_percentage(angle: float) -> float:
    return math.tan(angle) * 100


class BIMRoofProperties(PropertyGroup):
    def update_angle(self, context) -> None:
        self["angle"] = to_angle(self.percentage)

    def update_percentage(self, context) -> None:
        self["percentage"] = to_percentage(self.angle)

    non_si_units_props = (
        "is_editing",
        "path_data",
        "roof_type",
        "generation_method",
        "angle",
        "percentage",
        "rafter_edge_angle",
    )
    roof_types = (("HIP/GABLE ROOF", "HIP/GABLE ROOF", ""),)
    roof_generation_methods = (
        ("HEIGHT", "HEIGHT", ""),
        ("ANGLE", "ANGLE", ""),
    )

    is_editing: bpy.props.BoolProperty(default=False)
    is_editing_path: bpy.props.BoolProperty(default=False)

    roof_type: bpy.props.EnumProperty(name="Roof Type", items=roof_types, default="HIP/GABLE ROOF")
    generation_method: bpy.props.EnumProperty(
        name="Roof Generation Method", items=roof_generation_methods, default="ANGLE"
    )
    height: bpy.props.FloatProperty(
        name="Height", default=1.0, description="Maximum height of the roof to be generated.", subtype="DISTANCE"
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
    roof_thickness: bpy.props.FloatProperty(name="Roof Thickness", default=0.1, subtype="DISTANCE")
    rafter_edge_angle: bpy.props.FloatProperty(name="Rafter Edge Angle", min=0, max=pi, default=pi / 2, subtype="ANGLE")

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


class SnapMousePoint(PropertyGroup):
    x: bpy.props.FloatProperty(name="X")
    y: bpy.props.FloatProperty(name="Y")
    z: bpy.props.FloatProperty(name="Z")
    snap_type: bpy.props.StringProperty(name="Snap Type")
    snap_object: bpy.props.StringProperty(name="Object Name")


class PolylinePoint(PropertyGroup):
    x: bpy.props.FloatProperty(name="X")
    y: bpy.props.FloatProperty(name="Y")
    z: bpy.props.FloatProperty(name="Z")
    dim: bpy.props.StringProperty(name="Dimension")
    angle: bpy.props.StringProperty(name="Angle")
    position: bpy.props.FloatVectorProperty(name="Decorator Position", size=3)


class Polyline(PropertyGroup):
    polyline_points: bpy.props.CollectionProperty(type=PolylinePoint)
    measurement_type: bpy.props.StringProperty(name="Measurement Type")
    area: bpy.props.StringProperty(name="Measured Area")
    total_length: bpy.props.StringProperty(name="Total Length")


class BIMPolylineProperties(PropertyGroup):
    snap_mouse_point: bpy.props.CollectionProperty(type=SnapMousePoint)
    snap_mouse_ref: bpy.props.CollectionProperty(type=SnapMousePoint)
    insertion_polyline: bpy.props.CollectionProperty(type=Polyline)
    measurement_polyline: bpy.props.CollectionProperty(type=Polyline)
