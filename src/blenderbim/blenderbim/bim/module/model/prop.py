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


def get_constr_class(self, context):
    if not AuthoringData.is_loaded:
        AuthoringData.load()
    return AuthoringData.data["constr_classes"]


def get_constr_type(self, context):
    if not AuthoringData.is_loaded:
        AuthoringData.load()
    return AuthoringData.data["constr_types_ids"]


def get_constr_type_browser(self, context):
    if not AuthoringData.is_loaded:
        AuthoringData.load()
    return AuthoringData.data["constr_types_ids_browser"]


def update_icon_id(self, context):
    constr_class_browser = self.constr_class_browser
    constr_type_id_browser = self.constr_type_id_browser
    constr_type_browser = AuthoringData.constr_type_name_by_id(constr_class_browser, constr_type_id_browser)
    if ((constr_class_browser not in AuthoringData.data["preview_constr_types"]
            or constr_type_id_browser not in AuthoringData.data["preview_constr_types"][constr_class_browser])
            and constr_type_browser is not None):
        if not AuthoringData.assetize_constr_type_from_selection():
            return
    props = bpy.context.scene.BIMModelProperties
    props.icon_id = AuthoringData.data["preview_constr_types"][constr_class_browser][constr_type_id_browser]["icon_id"]


def update_constr_class(self, context):
    AuthoringData.load_constr_classes()
    AuthoringData.load_constr_types()
    self.constr_type_id = AuthoringData.data["constr_types_ids"][0][0]


def update_constr_class_browser(self, context):
    AuthoringData.load_constr_classes()
    AuthoringData.load_constr_types_browser()
    props = context.scene.BIMModelProperties
    if props.unfold_relating_type:
        constr_class_browser = props.constr_class_browser
        constr_type_info = AuthoringData.constr_type_info(constr_class_browser)
        if constr_type_info is None or not constr_type_info.fully_loaded:
            curr_selection = props.constr_class, props.constr_type_id
            AuthoringData.assetize_constr_class(constr_class_browser)
            props.constr_class, props.constr_type_id = curr_selection
    else:
        self.constr_type_id_browser = AuthoringData.data["constr_types_ids_browser"][0][0]


def update_constr_type(self, context):
    AuthoringData.load_constr_types()


def update_constr_type_by_name(self, context):
    AuthoringData.load_constr_types()
    constr_type_id = AuthoringData.constr_type_id_by_name(self.constr_class, self.constr_type)
    if constr_type_id is not None:
        self.constr_type_id = constr_type_id


def update_constr_type_browser_by_name(self, context):
    AuthoringData.load_constr_types_browser()
    constr_type_id_browser = AuthoringData.constr_type_id_by_name(self.constr_class_browser, self.constr_type_browser)
    if constr_type_id_browser is not None:
        self.constr_type_id_browser = constr_type_id_browser


def update_constr_type_browser(self, context):
    AuthoringData.load_constr_types_browser()
    update_icon_id(self, context)


def update_unfold_constr_type(self, context):
    update_constr_class_browser(self, context)


class BIMModelProperties(PropertyGroup):
    constr_class: bpy.props.EnumProperty(items=get_constr_class, name="Construction Class", update=update_constr_class)
    constr_class_browser: bpy.props.EnumProperty(
        items=get_constr_class, name="Construction Class", update=update_constr_class_browser
    )
    constr_type: bpy.props.StringProperty(update=update_constr_type_by_name)
    constr_type_id: bpy.props.EnumProperty(
        items=get_constr_type, name="Construction Type", update=update_constr_type
    )
    constr_type_browser: bpy.props.StringProperty(update=update_constr_type_browser_by_name)
    constr_type_id_browser: bpy.props.EnumProperty(
        items=get_constr_type_browser, name="Construction Type", update=update_constr_type_browser
    )
    icon_id: bpy.props.IntProperty()
    unfold_relating_type: bpy.props.BoolProperty(update=update_unfold_constr_type)
    occurrence_name_style: bpy.props.EnumProperty(
        items=[("CLASS", "By Class", ""), ("TYPE", "By Type", ""), ("CUSTOM", "Custom", "")],
        name="Occurrence Name Style",
    )
    occurrence_name_function: bpy.props.StringProperty(name="Occurrence Name Function")
    getter_enum = {
        "constr_class_browser": get_constr_class,
        "constr_type_browser": get_constr_type_browser
    }


def get_constr_type_info(self, context):
    return AuthoringData.relating_types(constr_class=self.name)


class ConstrTypeInfo(PropertyGroup):
    name: bpy.props.StringProperty(name="Construction class")
    constr_type: bpy.props.EnumProperty(
        name="Construction type", items=get_constr_type_info
    )
    fully_loaded: bpy.props.BoolProperty(default=False)


