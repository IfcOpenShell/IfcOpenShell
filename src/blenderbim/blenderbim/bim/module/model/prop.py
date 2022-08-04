# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
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
from blenderbim.bim.module.model.data import AuthoringData
from bpy.types import PropertyGroup


def get_ifc_class(self, context):
    if not AuthoringData.is_loaded:
        AuthoringData.load()
    return AuthoringData.data["ifc_classes"]


def get_relating_type(self, context):
    if not AuthoringData.is_loaded:
        AuthoringData.load()
    return AuthoringData.data["relating_types_ids"]


def get_relating_type_browser(self, context):
    if not AuthoringData.is_loaded:
        AuthoringData.load()
    return AuthoringData.data["relating_types_browser_ids"]


def update_icon_id(self, context, browser=False):
    ifc_class = self.ifc_class_browser if browser else self.ifc_class
    relating_type_id = self.relating_type_id_browser if browser else self.relating_type_id
    relating_type = AuthoringData.relating_type_name_by_id(ifc_class, relating_type_id)
    if (
        ifc_class not in AuthoringData.data["preview_constr_types"]
        or relating_type_id not in AuthoringData.data["preview_constr_types"][ifc_class]
    ) and relating_type is not None:
        if not AuthoringData.assetize_relating_type_from_selection(browser=browser):
            return
    if ifc_class not in AuthoringData.data["preview_constr_types"]:
        pass
    self.icon_id = AuthoringData.data["preview_constr_types"][ifc_class][relating_type_id]["icon_id"]


def update_ifc_class(self, context):
    AuthoringData.load_ifc_classes()
    AuthoringData.load_relating_types()
    if self.updating:
        return


def update_ifc_class_browser(self, context):
    AuthoringData.load_ifc_classes()
    AuthoringData.load_relating_types_browser()
    if self.updating:
        return
    ifc_class = self.ifc_class_browser
    relating_type_info = AuthoringData.relating_type_info(ifc_class)
    if relating_type_info is None or not relating_type_info.fully_loaded:
        AuthoringData.assetize_constr_class(ifc_class)


def update_relating_type(self, context):
    AuthoringData.load_relating_types()
    if not self.updating:
        update_icon_id(self, context)


def update_relating_type_browser(self, context):
    AuthoringData.load_relating_types_browser()
    if not self.updating:
        update_icon_id(self, context, browser=True)


def update_relating_type_by_name(self, context):
    AuthoringData.load_relating_types()
    relating_type_id = AuthoringData.relating_type_id_by_name(self.ifc_class, self.relating_type)
    if relating_type_id is not None:
        self.relating_type_id = relating_type_id


def update_preview_multiple(self, context):
    if self.preview_multiple_constr_types:
        ifc_class = self.ifc_class
        relating_type_info = AuthoringData.relating_type_info(ifc_class)
        if relating_type_info is None or not relating_type_info.fully_loaded:
            AuthoringData.assetize_constr_class(ifc_class)
    else:
        update_relating_type(self, context)


class BIMModelProperties(PropertyGroup):
    ifc_class: bpy.props.EnumProperty(items=get_ifc_class, name="Construction Class", update=update_ifc_class)
    ifc_class_browser: bpy.props.EnumProperty(items=get_ifc_class, name="Construction Class",
                                              update=update_ifc_class_browser)
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


def get_relating_type_info(self, context):
    return AuthoringData.relating_types(ifc_class=self.name)


class ConstrTypeInfo(PropertyGroup):
    name: bpy.props.StringProperty(name="Construction class")
    relating_type: bpy.props.EnumProperty(name="Construction type", items=get_relating_type_info)
    fully_loaded: bpy.props.BoolProperty(default=False)
