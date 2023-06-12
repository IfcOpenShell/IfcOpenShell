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
from blenderbim.bim.ifc import IfcStore
from blenderbim.bim.prop import StrProperty, Attribute
from blenderbim.bim.module.style.data import StylesData
from bpy.types import PropertyGroup
from bpy.props import (
    PointerProperty,
    StringProperty,
    EnumProperty,
    BoolProperty,
    IntProperty,
    FloatProperty,
    FloatVectorProperty,
    CollectionProperty,
)
import blenderbim.tool as tool


def get_style_types(self, context):
    if not StylesData.is_loaded:
        StylesData.load()
    return StylesData.data["style_types"]


class Style(PropertyGroup):
    name: StringProperty(name="Name")
    ifc_definition_id: IntProperty(name="IFC Definition ID")
    total_elements: IntProperty(name="Total Elements")


STYLE_TYPES = [
    ("Shading", "Shading", ""),
    ("External", "External", ""),
]


def update_shading_styles(self, context):
    materials_to_objects = dict()

    for obj in bpy.data.objects:
        blender_material = obj.active_material
        if blender_material and blender_material.BIMMaterialProperties.ifc_style_id != 0:
            materials_to_objects[blender_material] = obj

    for mat, obj in materials_to_objects.items():
        tool.Style.change_current_style_type(mat, self.active_style_type)


class BIMStylesProperties(PropertyGroup):
    is_editing: BoolProperty(name="Is Editing")
    style_type: EnumProperty(items=get_style_types, name="Style Type")
    styles: CollectionProperty(name="Styles", type=Style)
    active_style_index: IntProperty(name="Active Style Index")
    active_style_type: EnumProperty(
        name="Active Style Type",
        description="Update current blender material to match style type for all objects in the scene",
        items=STYLE_TYPES,
        default="Shading",
        update=update_shading_styles,
    )


def update_shading_style(self, context):
    blender_material = self.id_data
    style_elements = tool.Style.get_style_elements(blender_material)
    if self.active_style_type == "External":
        if tool.Style.has_blender_external_style(style_elements):
            bpy.ops.bim.activate_external_style(material_name=blender_material.name)

    elif self.active_style_type == "Shading":
        style_elements = tool.Style.get_style_elements(blender_material)
        rendering_style = None
        texture_style = None

        for surface_style in style_elements.values():
            if surface_style.is_a() == "IfcSurfaceStyleShading":
                tool.Loader.create_surface_style_shading(blender_material, surface_style)
            elif surface_style.is_a("IfcSurfaceStyleRendering"):
                rendering_style = surface_style
                tool.Loader.create_surface_style_rendering(blender_material, surface_style)
            elif surface_style.is_a("IfcSurfaceStyleWithTextures"):
                texture_style = surface_style

        if rendering_style and texture_style:
            tool.Loader.create_surface_style_with_textures(blender_material, rendering_style, texture_style)
    tool.Style.record_shading(blender_material)


class BIMStyleProperties(PropertyGroup):
    attributes: CollectionProperty(name="Attributes", type=Attribute)
    is_editing: BoolProperty(name="Is Editing")

    external_style_attributes: CollectionProperty(name="External Style Attributes", type=Attribute)
    is_editing_external_style: BoolProperty(name="Is Editing External Style")

    active_style_type: EnumProperty(
        name="Active Style Type",
        description="Update current blender material to match style type",
        items=STYLE_TYPES,
        default="Shading",
        update=update_shading_style,
    )
