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
import ifcopenshell.util.type
from blenderbim.bim.module.model.data import AuthoringData
from blenderbim.bim.prop import StrProperty, Attribute
from blenderbim.bim.ifc import IfcStore
import blenderbim.tool as tool
from bpy.types import PropertyGroup


def get_ifc_class(self, context):
    if not AuthoringData.is_loaded:
        AuthoringData.load()
    return AuthoringData.data["ifc_classes"]


def get_relating_type(self, context):
    if not AuthoringData.is_loaded:
        AuthoringData.load()
    return AuthoringData.data["relating_types"]


def update_icon_id(self, context):
    ifc_class = self.ifc_class
    relating_type_id = self.relating_type
    relating_type = AuthoringData.relating_type_name_by_id(ifc_class, relating_type_id)
    if ((ifc_class not in AuthoringData.data["preview_ifc_types"]
            or relating_type not in AuthoringData.data["preview_ifc_types"][ifc_class])
            and relating_type is not None):
        if not AuthoringData.assetize_relating_type_from_selection():
            return
    props = bpy.context.scene.BIMModelProperties
    props.icon_id = AuthoringData.data["preview_ifc_types"][ifc_class][relating_type]["icon_id"]


def update_ifc_class(self, context):
    if not AuthoringData.updating:
        AuthoringData.load_ifc_classes()
        AuthoringData.load_relating_types()
        props = context.scene.BIMModelProperties
        if props.unfold_relating_type:
            ifc_class = props.ifc_class
            ifc_type_info = AuthoringData.ifc_type_info(ifc_class)
            if ifc_type_info is None or not ifc_type_info.fully_loaded:
                AuthoringData.assetize_ifc_class(ifc_class)
        else:
            self.relating_type = AuthoringData.data["relating_types"][0][0]
            update_icon_id(self, context)


def update_relating_type(self, context):
    AuthoringData.load_relating_types()
    update_icon_id(self, context)


def update_unfold_relating_type(self, context):
    update_ifc_class(self, context)

    # if self.unfold_relating_type:
    #     props = context.scene.BIMModelProperties
    #     ifc_class = props.ifc_class
    #     ifc_type_info = AuthoringData.ifc_type_info(ifc_class)
    #     if ifc_type_info is None or not ifc_type_info.fully_loaded:
    #         AuthoringData.assetize_ifc_class(ifc_class)
    # else:
    #     update_ifc_class(self, context)


class BIMModelProperties(PropertyGroup):
    ifc_class: bpy.props.EnumProperty(items=get_ifc_class, name="IFC Class", update=update_ifc_class)
    relating_type: bpy.props.EnumProperty(items=get_relating_type, name="Relating Type", update=update_relating_type)
    icon_id: bpy.props.IntProperty()
    unfold_relating_type: bpy.props.BoolProperty(update=update_unfold_relating_type)
    occurrence_name_style: bpy.props.EnumProperty(
        items=[("CLASS", "By Class", ""), ("TYPE", "By Type", ""), ("CUSTOM", "Custom", "")],
        name="Occurrence Name Style",
    )
    occurrence_name_function: bpy.props.StringProperty(name="Occurrence Name Function")
    getter_enum = {
        "ifc_class": get_ifc_class,
        "relating_type": get_relating_type
    }


def get_ifc_type_info_relating_types(self, context):
    ifc_class = self.name
    return AuthoringData.relating_types(ifc_class=ifc_class)


class IfcTypeInfo(PropertyGroup):
    name: bpy.props.StringProperty(name="IFC class", description="IFC class")
    relating_type: bpy.props.EnumProperty(
        name="Relating type", description="Relating type", items=get_ifc_type_info_relating_types
    )
    fully_loaded: bpy.props.BoolProperty(default=False)


