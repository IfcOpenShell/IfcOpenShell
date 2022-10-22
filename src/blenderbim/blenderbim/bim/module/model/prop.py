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
from blenderbim.bim.prop import ObjProperty
from blenderbim.bim.module.model.data import AuthoringData
from blenderbim.bim.module.model.root import ConstrTypeEntityNotFound
from bpy.types import PropertyGroup


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


def store_cursor_position(context, event, cursor=True, window=True):
    browser_state = context.scene.BIMModelProperties.constr_browser_state
    if cursor:
        browser_state.cursor_x, browser_state.cursor_y = event.mouse_x, event.mouse_y
    if window:
        browser_state.window_x, browser_state.window_y = event.mouse_x, event.mouse_y


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
    rl1: bpy.props.FloatProperty(name="RL", default=1) # Used for things like walls, doors, flooring, skirting, etc
    rl2: bpy.props.FloatProperty(name="RL", default=1) # Used for things like windows, other hosted furniture
    x_angle: bpy.props.FloatProperty(name="X Angle", default=0)
    type_page: bpy.props.IntProperty(name="Type Page", default=1, update=update_type_page)
    type_template: bpy.props.EnumProperty(
        items=(
            ("1", "Custom Mesh", ""),
            ("2", "Vertical Layers", ""),
            ("2", "Horizontal Layers", ""),
            ("3", "Extruded Profile", ""),
            ("4", "Non-Geometric Type", ""),
        ),
        name="Type Template",
        default="1",
    )
    type_class: bpy.props.EnumProperty(items=get_type_class, name="IFC Class", update=update_type_class)
    type_predefined_type: bpy.props.EnumProperty(items=get_type_predefined_type, name="Predefined Type", default=None)
