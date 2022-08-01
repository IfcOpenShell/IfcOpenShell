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
    return AuthoringData.data["relating_types_ids_browser"]


def update_icon_id(self, context):
    ifc_class_browser = self.ifc_class_browser
    relating_type_id_browser = self.relating_type_id_browser
    relating_type_browser = AuthoringData.relating_type_name_by_id(ifc_class_browser, relating_type_id_browser)
    if ((ifc_class_browser not in AuthoringData.data["preview_constr_types"]
            or relating_type_id_browser not in AuthoringData.data["preview_constr_types"][ifc_class_browser])
            and relating_type_browser is not None):
        if not AuthoringData.assetize_relating_type_from_selection():
            return
    self.icon_id = AuthoringData.data["preview_constr_types"][ifc_class_browser][relating_type_id_browser]["icon_id"]


def update_ifc_class(self, context):
    AuthoringData.load_ifc_classes()
    AuthoringData.load_relating_types()
    self.relating_type_id = AuthoringData.data["relating_types_ids"][0][0]


def update_ifc_class_browser(self, context):
    AuthoringData.load_ifc_classes()
    AuthoringData.load_relating_types_browser()
    props = context.scene.BIMModelProperties
    if props.unfold_relating_types:
        ifc_class_browser = props.ifc_class_browser
        relating_type_info = AuthoringData.relating_type_info(ifc_class_browser)
        if relating_type_info is None or not relating_type_info.fully_loaded:
            curr_selection = props.ifc_class, props.relating_type_id
            AuthoringData.assetize_constr_class(ifc_class_browser)
            props.ifc_class, props.relating_type_id = curr_selection
    else:
        self.relating_type_id_browser = AuthoringData.data["relating_types_ids_browser"][0][0]


def update_relating_type(self, context):
    AuthoringData.load_relating_types()


def update_relating_type_by_name(self, context):
    AuthoringData.load_relating_types()
    relating_type_id = AuthoringData.relating_type_id_by_name(self.ifc_class, self.relating_type)
    if relating_type_id is not None:
        self.relating_type_id = relating_type_id


def update_relating_type_browser_by_name(self, context):
    AuthoringData.load_relating_types_browser()
    relating_type_id_browser = AuthoringData.relating_type_id_by_name(self.ifc_class_browser, self.relating_type_browser)
    if relating_type_id_browser is not None:
        self.relating_type_id_browser = relating_type_id_browser


def update_relating_type_browser(self, context):
    AuthoringData.load_relating_types_browser()
    update_icon_id(self, context)


def update_unfold_relating_type(self, context):
    update_ifc_class_browser(self, context)


class BIMModelProperties(PropertyGroup):
    ifc_class: bpy.props.EnumProperty(items=get_ifc_class, name="Construction Class", update=update_ifc_class)
    ifc_class_browser: bpy.props.EnumProperty(
        items=get_ifc_class, name="Construction Class", update=update_ifc_class_browser
    )
    relating_type: bpy.props.StringProperty(update=update_relating_type_by_name)
    relating_type_id: bpy.props.EnumProperty(
        items=get_relating_type, name="Construction Type", update=update_relating_type
    )
    relating_type_browser: bpy.props.StringProperty(update=update_relating_type_browser_by_name)
    relating_type_id_browser: bpy.props.EnumProperty(
        items=get_relating_type_browser, name="Construction Type", update=update_relating_type_browser
    )
    icon_id: bpy.props.IntProperty()
    unfold_relating_types: bpy.props.BoolProperty(update=update_unfold_relating_type)
    occurrence_name_style: bpy.props.EnumProperty(
        items=[("CLASS", "By Class", ""), ("TYPE", "By Type", ""), ("CUSTOM", "Custom", "")],
        name="Occurrence Name Style",
    )
    occurrence_name_function: bpy.props.StringProperty(name="Occurrence Name Function")
    getter_enum = {
        "ifc_class_browser": get_ifc_class,
        "relating_type_browser": get_relating_type_browser
    }


def get_relating_type_info(self, context):
    return AuthoringData.relating_types(ifc_class=self.name)


class ConstrTypeInfo(PropertyGroup):
    name: bpy.props.StringProperty(name="Construction class")
    relating_type: bpy.props.EnumProperty(
        name="Construction type", items=get_relating_type_info
    )
    fully_loaded: bpy.props.BoolProperty(default=False)


