# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021, 2022 Dion Moult <dion@thinkmoult.com>
#
# This file is part of BlenderBIM Add-on.
#
# BlenderBIM Add-on is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BlenderBIM Add-on is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with BlenderBIM Add-on.  If not, see <http://www.gnu.org/licenses/>.

import bpy
import ifcopenshell
import blenderbim.tool as tool
from blenderbim.bim.prop import ObjProperty
from blenderbim.bim.module.model.data import AuthoringData
from blenderbim.bim.module.model.root import ConstrTypeEntityNotFound
from bpy.types import PropertyGroup, NodeTree
from math import pi


def get_ifc_class(self, context):
    if not AuthoringData.is_loaded:
        AuthoringData.load()
    return AuthoringData.data["ifc_classes"]


def get_type_class(self, context):
    if not AuthoringData.is_loaded:
        AuthoringData.load()
    return AuthoringData.data["type_class"]


def get_relating_type(self, context):
    if not AuthoringData.is_loaded:
        AuthoringData.load()
    return AuthoringData.data["relating_types_ids"]


def get_relating_type_browser(self, context):
    if not AuthoringData.is_loaded:
        AuthoringData.load()
    return AuthoringData.data["relating_types_ids_browser"]


def get_type_predefined_type(self, context):
    if not AuthoringData.is_loaded:
        AuthoringData.load()
    return AuthoringData.data["type_predefined_type"]


def update_icon_id(self, context, browser=False):
    if context == "lost_context" or (context.region is not None and context.region.type != "TOOL_HEADER"):
        ifc_class = self.ifc_class_browser if browser else self.ifc_class
        relating_type_id = self.relating_type_id_browser if browser else self.relating_type_id
        # relating_type = AuthoringData.relating_type_name_by_id(ifc_class, relating_type_id)

        if ifc_class not in self.constr_classes or relating_type_id not in self.constr_classes[ifc_class].constr_types:
            try:
                AuthoringData.assetize_relating_type_from_selection(browser=browser)
            except ConstrTypeEntityNotFound:
                return

        def set_icon(update_interval_seconds=1e-4):
            if (
                ifc_class not in self.constr_classes
                or relating_type_id not in self.constr_classes[ifc_class].constr_types
            ):
                return update_interval_seconds
            else:
                self.icon_id = self.constr_classes[ifc_class].constr_types[relating_type_id].icon_id

        bpy.app.timers.register(set_icon)


def update_ifc_class(self, context):
    bpy.ops.bim.load_type_thumbnails(ifc_class=self.ifc_class)
    AuthoringData.data["relating_types_ids"] = AuthoringData.relating_types()
    AuthoringData.data["type_thumbnail"] = AuthoringData.type_thumbnail()


def update_type_class(self, context):
    AuthoringData.data["total_types"] = AuthoringData.total_types()
    AuthoringData.data["total_pages"] = AuthoringData.total_pages()
    AuthoringData.data["prev_page"] = AuthoringData.prev_page()
    AuthoringData.data["next_page"] = AuthoringData.next_page()
    AuthoringData.data["paginated_relating_types"] = AuthoringData.paginated_relating_types()
    AuthoringData.data["type_predefined_type"] = AuthoringData.type_predefined_type()


def update_ifc_class_browser(self, context):
    if context.region is not None and context.region.type != "TOOL_HEADER":
        AuthoringData.load_ifc_classes()
        AuthoringData.load_relating_types_browser()
        if self.updating:
            return
        ifc_class = self.ifc_class_browser
        constr_class_info = AuthoringData.constr_class_info(ifc_class)

        if constr_class_info is None or not constr_class_info.fully_loaded:
            AuthoringData.assetize_constr_class(ifc_class)


def update_relating_type(self, context):
    AuthoringData.load_relating_types()
    AuthoringData.data["type_thumbnail"] = AuthoringData.type_thumbnail()


def update_type_page(self, context):
    AuthoringData.data["paginated_relating_types"] = AuthoringData.paginated_relating_types()


def update_relating_type_browser(self, context):
    AuthoringData.load_relating_types_browser()
    if not self.updating:
        update_icon_id(self, context, browser=True)


def update_relating_type_by_name(self, context):
    AuthoringData.load_relating_types()
    relating_type_id = AuthoringData.relating_type_id_by_name(self.ifc_class, self.relating_type)
    if relating_type_id is not None:
        self.relating_type_id = relating_type_id


def get_constr_class_info(props, ifc_class):
    return props.constr_classes[ifc_class] if ifc_class in props.constr_classes else None


def update_preview_multiple(self, context):
    if context.region is not None and context.region.type != "TOOL_HEADER":
        if self.preview_multiple_constr_types:
            ifc_class = self.ifc_class
            constr_class_info = get_constr_class_info(self, ifc_class)
            if constr_class_info is None or not constr_class_info.fully_loaded:
                AuthoringData.assetize_constr_class(ifc_class)
        else:
            update_relating_type(self, context)


class ConstrTypeInfo(PropertyGroup):
    name: bpy.props.StringProperty(name="Construction type ID")
    icon_id: bpy.props.IntProperty(name="Icon ID")
    object: bpy.props.PointerProperty(name="Object", type=bpy.types.Object)


class ConstrClassInfo(PropertyGroup):
    name: bpy.props.StringProperty(name="Construction class")
    constr_types: bpy.props.CollectionProperty(type=ConstrTypeInfo)
    fully_loaded: bpy.props.BoolProperty(default=False)


class ConstrBrowserState(PropertyGroup):
    cursor_x: bpy.props.IntProperty()
    cursor_y: bpy.props.IntProperty()
    window_x: bpy.props.IntProperty()
    window_y: bpy.props.IntProperty()
    far_away_x: bpy.props.IntProperty(default=10)  # lower left corner to temporarily warp the mouse
    far_away_y: bpy.props.IntProperty(default=10)  # useful to close popup operators
    updating: bpy.props.BoolProperty()
    update_delay: bpy.props.FloatProperty(default=3e-2)


class BIMModelProperties(PropertyGroup):
    ifc_class: bpy.props.EnumProperty(items=get_ifc_class, name="Construction Class", update=update_ifc_class)
    ifc_class_browser: bpy.props.EnumProperty(
        items=get_ifc_class, name="Construction Class", update=update_ifc_class_browser
    )
    relating_type: bpy.props.StringProperty(update=update_relating_type_by_name)
    relating_type_id: bpy.props.EnumProperty(
        items=get_relating_type, name="Construction Type", update=update_relating_type
    )
    relating_type_id_browser: bpy.props.EnumProperty(
        items=get_relating_type_browser, name="Construction Type", update=update_relating_type_browser
    )
    icon_id: bpy.props.IntProperty()
    preview_multiple_constr_types: bpy.props.BoolProperty(default=False, update=update_preview_multiple)
    updating: bpy.props.BoolProperty(default=False)
    occurrence_name_style: bpy.props.EnumProperty(
        items=[("CLASS", "By Class", ""), ("TYPE", "By Type", ""), ("CUSTOM", "Custom", "")],
        name="Occurrence Name Style",
    )
    occurrence_name_function: bpy.props.StringProperty(name="Occurrence Name Function")
    getter_enum = {"ifc_class": get_ifc_class, "relating_type": get_relating_type}
    constr_classes: bpy.props.CollectionProperty(type=ConstrClassInfo)
    constr_browser_state: bpy.props.PointerProperty(type=ConstrBrowserState)
    extrusion_depth: bpy.props.FloatProperty(default=42.0)
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
    length: bpy.props.FloatProperty(default=42.0)
    openings: bpy.props.CollectionProperty(type=ObjProperty)
    x: bpy.props.FloatProperty(name="X", default=0.5)
    y: bpy.props.FloatProperty(name="Y", default=0.5)
    z: bpy.props.FloatProperty(name="Z", default=0.5)
    rl1: bpy.props.FloatProperty(name="RL", default=1)  # Used for things like walls, doors, flooring, skirting, etc
    rl2: bpy.props.FloatProperty(name="RL", default=1)  # Used for things like windows, other hosted furniture
    x_angle: bpy.props.FloatProperty(name="X Angle", default=0)
    type_page: bpy.props.IntProperty(name="Type Page", default=1, update=update_type_page)
    type_template: bpy.props.EnumProperty(
        items=(
            ("MESH", "Custom Mesh", ""),
            ("LAYERSET_AXIS2", "Vertical Layers", ""),
            ("LAYERSET_AXIS3", "Horizontal Layers", ""),
            ("PROFILESET", "Extruded Profile", ""),
            ("EMPTY", "Non-Geometric Type", ""),
            ("WINDOW", "Window", ""),
            ("DOOR", "Door", ""),
            ("STAIR", "Stair", ""),
            ("RAILING", "Railing", ""),
            ("ROOF", "Roof", ""),
        ),
        name="Type Template",
        default="MESH",
    )
    type_class: bpy.props.EnumProperty(items=get_type_class, name="IFC Class", update=update_type_class)
    type_predefined_type: bpy.props.EnumProperty(items=get_type_predefined_type, name="Predefined Type", default=None)
    type_name: bpy.props.StringProperty(name="Name", default="TYPEX")


class BIMArrayProperties(PropertyGroup):
    is_editing: bpy.props.IntProperty(
        default=-1, description="Currently edited array index. -1 if not in array editing mode."
    )
    count: bpy.props.IntProperty(name="Count", default=0)
    x: bpy.props.FloatProperty(name="X", default=0)
    y: bpy.props.FloatProperty(name="Y", default=0)
    z: bpy.props.FloatProperty(name="Z", default=0)
    use_local_space: bpy.props.BoolProperty(
        name="Use Local Space",
        description="Use local space for array items offset instead of world space",
        default=True,
    )


class BIMStairProperties(PropertyGroup):
    stair_types = (
        ("CONCRETE", "Concrete", ""),
        ("WOOD/STEEL", "Wood / Steel", ""),
        ("GENERIC", "Generic", ""),
    )

    stair_added_previously: bpy.props.BoolProperty(default=False)
    is_editing: bpy.props.IntProperty(default=-1)
    width: bpy.props.FloatProperty(name="Width", default=1.2, soft_min=0.01)
    height: bpy.props.FloatProperty(name="Height", default=1.0, soft_min=0.01)
    number_of_treads: bpy.props.IntProperty(name="Number of treads", default=6, soft_min=1)
    tread_depth: bpy.props.FloatProperty(name="Tread Depth", default=0.25, soft_min=0.01)
    tread_run: bpy.props.FloatProperty(name="Tread Run", default=0.3, soft_min=0.01)
    base_slab_depth: bpy.props.FloatProperty(name="Base slab depth", default=0.25, soft_min=0)
    top_slab_depth: bpy.props.FloatProperty(name="Top slab depth", default=0.25, soft_min=0)
    has_top_nib: bpy.props.BoolProperty(name="Has top nib", default=True)
    stair_type: bpy.props.EnumProperty(name="Stair type", items=stair_types, default="CONCRETE")

    def get_props_kwargs(self):
        stair_kwargs = {
            "stair_type": self.stair_type,
            "width": self.width,
            "height": self.height,
            "number_of_treads": self.number_of_treads,
            "tread_run": self.tread_run,
        }

        if self.stair_type == "CONCRETE":
            stair_kwargs.update(
                {
                    "base_slab_depth": self.base_slab_depth,
                    "top_slab_depth": self.top_slab_depth,
                    "has_top_nib": self.has_top_nib,
                    "tread_depth": self.tread_depth,
                }
            )
            return stair_kwargs

        elif self.stair_type == "WOOD/STEEL":
            stair_kwargs.update(
                {
                    "tread_depth": self.tread_depth,
                }
            )
            return stair_kwargs

        elif self.stair_type == "GENERIC":
            return stair_kwargs


class BIMSverchokProperties(PropertyGroup):
    node_group: bpy.props.PointerProperty(name="Node Group", type=NodeTree)


def window_type_prop_update(self, context):
    number_of_panels, panels_data = self.window_types_panels[self.window_type]

    si_coversion = 1.0 / ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
    panels_data = [[v * si_coversion for v in data] for data in panels_data]
    self.first_mullion_offset, self.second_mullion_offset = panels_data[0]
    self.first_transom_offset, self.second_transom_offset = panels_data[1]


# default prop values are in mm and converted later
class BIMWindowProperties(PropertyGroup):
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

    window_added_previously: bpy.props.BoolProperty(default=False)
    is_editing: bpy.props.IntProperty(default=-1)
    window_type: bpy.props.EnumProperty(
        name="Window Type", items=window_types, default="SINGLE_PANEL", update=window_type_prop_update
    )
    overall_height: bpy.props.FloatProperty(name="Overall Height", default=0.9)
    overall_width: bpy.props.FloatProperty(name="Overall Width", default=0.6)

    # lining properties
    lining_depth: bpy.props.FloatProperty(name="Lining Depth", default=0.050)
    lining_thickness: bpy.props.FloatProperty(name="Lining Thickness", default=0.050)
    lining_offset: bpy.props.FloatProperty(name="Lining Offset", default=0.050)
    lining_to_panel_offset_x: bpy.props.FloatProperty(name="Lining to Panel Offset X", default=0.025)
    lining_to_panel_offset_y: bpy.props.FloatProperty(name="Lining to Panel Offset Y", default=0.025)
    mullion_thickness: bpy.props.FloatProperty(name="Mullion Thickness", default=0.050)
    first_mullion_offset: bpy.props.FloatProperty(
        name="First Mullion Offset",
        description="Distance from the first lining to the first mullion center",
        default=0.3,
    )
    second_mullion_offset: bpy.props.FloatProperty(
        name="Second Mullion Offset",
        description="Distance from the first lining to the second mullion center",
        default=0.45,
    )
    transom_thickness: bpy.props.FloatProperty(name="Transom Thickness", default=0.050)
    first_transom_offset: bpy.props.FloatProperty(
        name="First Transom Offset",
        description="Distance from the first lining to the first transom center",
        default=0.3,
    )
    second_transom_offset: bpy.props.FloatProperty(
        name="Second Transom Offset",
        description="Distance from the first lining to the second transom center",
        default=0.6,
    )

    # panel properties
    frame_depth: bpy.props.FloatVectorProperty(name="Frame Depth", size=3, default=[0.035] * 3)
    frame_thickness: bpy.props.FloatVectorProperty(name="Frame Thickness", size=3, default=[0.035] * 3)

    def get_general_kwargs(self):
        return {
            "window_type": self.window_type,
            "overall_height": self.overall_height,
            "overall_width": self.overall_width,
        }

    def get_lining_kwargs(self):
        kwargs = {
            "lining_depth": self.lining_depth,
            "lining_thickness": self.lining_thickness,
            "lining_offset": self.lining_offset,
            "lining_to_panel_offset_x": self.lining_to_panel_offset_x,
            "lining_to_panel_offset_y": self.lining_to_panel_offset_y,
        }

        if self.window_type in (
            "DOUBLE_PANEL_VERTICAL",
            "TRIPLE_PANEL_BOTTOM",
            "TRIPLE_PANEL_TOP",
            "TRIPLE_PANEL_LEFT",
            "TRIPLE_PANEL_RIGHT",
            "TRIPLE_PANEL_VERTICAL",
        ):
            kwargs["mullion_thickness"] = self.mullion_thickness
            kwargs["first_mullion_offset"] = self.first_mullion_offset

        if self.window_type in (
            "DOUBLE_PANEL_HORIZONTAL",
            "TRIPLE_PANEL_BOTTOM",
            "TRIPLE_PANEL_TOP",
            "TRIPLE_PANEL_LEFT",
            "TRIPLE_PANEL_RIGHT",
            "TRIPLE_PANEL_HORIZONTAL",
        ):
            kwargs["transom_thickness"] = self.transom_thickness
            kwargs["first_transom_offset"] = self.first_transom_offset

        if self.window_type in ("TRIPLE_PANEL_VERTICAL",):
            kwargs["second_mullion_offset"] = self.second_mullion_offset

        if self.window_type in ("TRIPLE_PANEL_HORIZONTAL",):
            kwargs["second_transom_offset"] = self.second_transom_offset

        return kwargs

    def get_panel_kwargs(self):
        return {
            "frame_depth": self.frame_depth,
            "frame_thickness": self.frame_thickness,
        }


class BIMDoorProperties(PropertyGroup):
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

    door_added_previously: bpy.props.BoolProperty(default=False)
    is_editing: bpy.props.IntProperty(default=-1)
    door_type: bpy.props.EnumProperty(name="Door Operation Type", items=door_types, default="SINGLE_SWING_LEFT")
    overall_height: bpy.props.FloatProperty(name="Overall Height", default=2.0)
    overall_width: bpy.props.FloatProperty(name="Overall Width", default=0.9)

    # lining properties
    lining_depth: bpy.props.FloatProperty(name="Lining Depth", default=0.050)
    lining_thickness: bpy.props.FloatProperty(name="Lining Thickness", default=0.050)
    lining_offset: bpy.props.FloatProperty(
        name="Lining Offset",
        description="Offset from the outer side of the wall (by Y-axis). "
        "If present then adding casing is not possible.\n"
        "`0.025 mm` is good as default value",
        default=0.0,
    )
    lining_to_panel_offset_x: bpy.props.FloatProperty(name="Lining to Panel Offset X", default=0.025)
    lining_to_panel_offset_y: bpy.props.FloatProperty(name="Lining to Panel Offset Y", default=0.025)

    transom_thickness: bpy.props.FloatProperty(
        name="Transom Thickness",
        description="Set values > 0 to add a transom.\n" "`0.050 mm` is good as default value",
        default=0.000,
    )
    transom_offset: bpy.props.FloatProperty(
        name="Transom Offset",
        description="Distance from the bottom door opening to the beginning of the transom (unlike windows)",
        default=1.525,
    )

    casing_thickness: bpy.props.FloatProperty(
        name="Casing Thickness", description="Set values > 0 and LiningOffset = 0 to add a casing.", default=0.075
    )
    casing_depth: bpy.props.FloatProperty(name="Casing Depth", default=0.005)

    threshold_thickness: bpy.props.FloatProperty(
        name="Threshold Thickness", description="Set values > 0 to add a threshold.", default=0.025
    )
    threshold_depth: bpy.props.FloatProperty(name="Threshold Depth", default=0.1)
    threshold_offset: bpy.props.FloatProperty(
        name="Threshold Offset", description="`0.025 mm` is good as default value", default=0.000
    )

    # panel properties
    panel_depth: bpy.props.FloatProperty(name="Panel Depth", default=0.035)
    panel_width_ratio: bpy.props.FloatProperty(
        name="Panel Width Ratio",
        description="Width of this panel, given as ratio " "relative to the total clear opening width of the door",
        default=1.0,
        soft_min=0,
        soft_max=1,
    )
    frame_thickness: bpy.props.FloatProperty(name="Window Frame Thickness", default=0.035)
    frame_depth: bpy.props.FloatProperty(name="Window Frame Depth", default=0.035)

    def get_general_kwargs(self):
        return {
            "door_type": self.door_type,
            "overall_height": self.overall_height,
            "overall_width": self.overall_width,
        }

    def get_lining_kwargs(self):
        kwargs = {
            "lining_depth": self.lining_depth,
            "lining_thickness": self.lining_thickness,
            "lining_offset": self.lining_offset,
        }

        if "SLIDING" not in self.door_type:
            kwargs["lining_to_panel_offset_x"] = self.lining_to_panel_offset_x
            kwargs["lining_to_panel_offset_y"] = self.lining_to_panel_offset_y

        kwargs["transom_thickness"] = self.transom_thickness
        if self.transom_thickness:
            kwargs["transom_offset"] = self.transom_offset

        if not self.lining_offset:
            kwargs["casing_thickness"] = self.casing_thickness
            if self.casing_thickness:
                kwargs["casing_depth"] = self.casing_depth

        kwargs["threshold_thickness"] = self.threshold_thickness
        if self.threshold_thickness:
            kwargs["threshold_depth"] = self.threshold_depth
            kwargs["threshold_offset"] = self.threshold_offset

        return kwargs

    def get_panel_kwargs(self):
        kwargs = {"panel_depth": self.panel_depth, "panel_width_ratio": self.panel_width_ratio}

        if self.transom_thickness:
            kwargs["frame_thickness"] = self.frame_thickness
            kwargs["frame_depth"] = self.frame_depth

        return kwargs


class BIMRailingProperties(PropertyGroup):
    railing_types = (("FRAMELESS_PANEL", "FRAMELESS_PANEL", ""),)

    railing_added_previously: bpy.props.BoolProperty(default=False)
    is_editing: bpy.props.IntProperty(default=-1)
    is_editing_path: bpy.props.BoolProperty(default=False)

    railing_type: bpy.props.EnumProperty(name="Railing Type", items=railing_types, default="FRAMELESS_PANEL")
    height: bpy.props.FloatProperty(name="Height", default=1.0)
    thickness: bpy.props.FloatProperty(name="Thickness", default=0.050)
    spacing: bpy.props.FloatProperty(name="Spacing", default=0.050)

    def get_general_kwargs(self):
        return {
            "railing_type": self.railing_type,
            "height": self.height,
            "thickness": self.thickness,
            "spacing": self.spacing,
        }


class BIMRoofProperties(PropertyGroup):
    roof_types = (("HIP/GABLE ROOF", "HIP/GABLE ROOF", ""),)
    roof_generation_methods = (
        ("HEIGHT", "HEIGHT", ""),
        ("ANGLE", "ANGLE", ""),
    )

    roof_added_previously: bpy.props.BoolProperty(default=False)
    is_editing: bpy.props.IntProperty(default=-1)
    is_editing_path: bpy.props.BoolProperty(default=False)

    roof_type: bpy.props.EnumProperty(name="Roof Type", items=roof_types, default="HIP/GABLE ROOF")
    generation_method: bpy.props.EnumProperty(
        name="Roof Generation Method", items=roof_generation_methods, default="ANGLE"
    )
    height: bpy.props.FloatProperty(
        name="Height", default=1.0, description="Maximum height of the roof to be generated.", subtype="DISTANCE"
    )
    angle: bpy.props.FloatProperty(name="Slope Angle", default=pi / 18, subtype="ANGLE")

    def get_general_kwargs(self):
        kwargs = {
            "roof_type": self.roof_type,
            "generation_method": self.generation_method,
        }
        if self.generation_method == "HEIGHT":
            kwargs["height"] = self.height
        else:
            kwargs["angle"] = self.angle
        return kwargs
