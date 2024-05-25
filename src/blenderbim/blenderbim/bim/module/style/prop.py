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
import blenderbim.tool as tool
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

import gettext
from typing import Literal


_ = gettext.gettext


def get_style_types(self, context):
    if not StylesData.is_loaded:
        StylesData.load()
    return StylesData.data["style_types"]


def get_reflectance_methods(self, context):
    if not StylesData.is_loaded:
        StylesData.load()
    return StylesData.data["reflectance_methods"]


class Style(PropertyGroup):
    name: StringProperty(name="Name")
    ifc_definition_id: IntProperty(name="IFC Definition ID")
    total_elements: IntProperty(name="Total Elements")
    style_classes: CollectionProperty(name="Style Classes", type=StrProperty)
    has_surface_colour: BoolProperty(name="Has Surface Colour", default=False)
    surface_colour: bpy.props.FloatVectorProperty(
        name="Surface Colour", subtype="COLOR", default=(1, 1, 1), min=0.0, max=1.0, size=3
    )
    has_diffuse_colour: BoolProperty(name="Has Diffuse Colour", default=False)
    diffuse_colour: bpy.props.FloatVectorProperty(
        name="Diffuse Colour", subtype="COLOR", default=(1, 1, 1), min=0.0, max=1.0, size=3
    )


STYLE_TYPES = [
    ("Shading", "Shading", ""),
    ("External", "External", ""),
]


def update_shading_styles(self, context):
    for mat in bpy.data.materials:
        if mat.BIMMaterialProperties.ifc_style_id == 0:
            continue
        tool.Style.change_current_style_type(mat, self.active_style_type)


def update_shader_graph(self, context):
    props = self.id_data.BIMStylesProperties if isinstance(self, Texture) else self

    if not props.update_graph:
        return
    style = tool.Ifc.get().by_id(props.is_editing_style)
    material = tool.Ifc.get_object(style)

    shading_data = tool.Style.get_shading_style_data_from_props()
    textures_data = tool.Style.get_texture_style_data_from_props()
    tool.Loader.create_surface_style_rendering(material, shading_data)
    tool.Loader.create_surface_style_with_textures(material, shading_data, textures_data)


UV_MODES = [
    ("UV", "UV", _("Actual UV data presented on the geometry")),
    ("Generated", "Generated", _("Automatically-generated UV from the vertex positions of the mesh")),
    ("Camera", "Camera", _("UV from position coordinate in camera space")),
]


TEXTURE_MAPS_MODS = (
    ("DIFFUSE", "DIFFUSE", ""),
    ("NORMAL", "NORMAL", ""),
    ("METALLICROUGHNESS", "METALLICROUGHNESS", "Green Channel = Roughness,\nBlue Channel = Metallic"),
    ("SPECULAR", "SPECULAR", ""),
    ("SHININESS", "SHININESS", ""),
    ("EMISSIVE", "EMISSIVE", ""),
    ("OCCLUSION", "OCCLUSION", ""),
    ("AMBIENT", "AMBIENT", ""),
)


class Texture(PropertyGroup):
    mode: EnumProperty(name="Type Of Texture", items=TEXTURE_MAPS_MODS, update=update_shader_graph)
    # NOTE: subtype `FILE_PATH` is not used to avoid .blend relative paths
    path: StringProperty(name="Texture Path", update=update_shader_graph)


class ColourRgb(PropertyGroup):
    name: StringProperty()
    color_value: FloatVectorProperty(size=3, subtype="COLOR", default=(1, 1, 1))
    # not exposed in the UI, here just to preserve the data
    color_name: StringProperty(name="Color Name")

    # to fit blender.bim.helper.export_attributes
    def get_value(self):
        return {
            "Name": self.color_name or None,
            "Red": self.color_value[0],
            "Green": self.color_value[1],
            "Blue": self.color_value[2],
        }

    # to fit blender.bim.helper.draw_attribute
    is_uri = False
    is_optional = False

    def get_value_name(self):
        return "color_value"


class BIMStylesProperties(PropertyGroup):
    is_adding: BoolProperty(name="Is Adding")
    is_editing: BoolProperty(name="Is Editing")
    is_editing_style: IntProperty(name="Is Editing Style")
    is_editing_class: StringProperty(name="Is Editing Class")
    attributes: CollectionProperty(name="Attributes", type=Attribute)
    external_style_attributes: CollectionProperty(name="External Style Attributes", type=Attribute)
    refraction_style_attributes: CollectionProperty(name="Refraction Style Attributes", type=Attribute)
    lighting_style_colours: CollectionProperty(name="Lighting Style Colours", type=ColourRgb)
    style_type: EnumProperty(items=get_style_types, default=2, name="Style Type")
    style_name: StringProperty(name="Style Name")
    surface_style_class: EnumProperty(
        items=[
            (x, x, "")
            for x in (
                "IfcSurfaceStyleShading",
                "IfcSurfaceStyleRendering",
                "IfcSurfaceStyleWithTextures",
                "IfcSurfaceStyleLighting",
                "IfcSurfaceStyleRefraction",
                "IfcExternallyDefinedSurfaceStyle",
            )
        ],
        name="Surface Style Class",
        default="IfcSurfaceStyleShading",
    )
    update_graph: BoolProperty(
        name="Update Shade Graph on Prop Change",
        description="Update shader graph in real time\nas you update style properties",
        default=True,
    )

    # shading props
    surface_colour: bpy.props.FloatVectorProperty(
        name="Surface Colour", subtype="COLOR", default=(1, 1, 1), min=0.0, max=1.0, size=3, update=update_shader_graph
    )
    transparency: bpy.props.FloatProperty(
        name="Transparency", default=0.0, min=0.0, max=1.0, update=update_shader_graph
    )
    # TODO: do something on null?
    is_diffuse_colour_null: BoolProperty(name="Is Null")
    diffuse_colour_class: EnumProperty(
        items=[(x, x, "") for x in ("IfcColourRgb", "IfcNormalisedRatioMeasure")],
        name="Diffuse Colour Class",
        update=update_shader_graph,
    )
    diffuse_colour: bpy.props.FloatVectorProperty(
        name="Diffuse Colour", subtype="COLOR", default=(1, 1, 1), min=0.0, max=1.0, size=3, update=update_shader_graph
    )
    diffuse_colour_ratio: bpy.props.FloatProperty(
        name="Diffuse Ratio", default=0.0, min=0.0, max=1.0, update=update_shader_graph
    )
    is_specular_colour_null: BoolProperty(name="Is Null")
    specular_colour_class: EnumProperty(
        items=[(x, x, "") for x in ("IfcColourRgb", "IfcNormalisedRatioMeasure")],
        name="Specular Colour Class",
        update=update_shader_graph,
        default="IfcNormalisedRatioMeasure",
    )
    specular_colour: bpy.props.FloatVectorProperty(
        name="Specular Colour",
        subtype="COLOR",
        default=(1, 1, 1),
        min=0.0,
        max=1.0,
        size=3,
        update=update_shader_graph,
    )
    specular_colour_ratio: bpy.props.FloatProperty(
        name="Specular Ratio",
        description="Used as Metallic value in PHYSICAL Reflectance Method",
        default=0.0,
        min=0.0,
        max=1.0,
        update=update_shader_graph,
    )
    is_specular_highlight_null: BoolProperty(name="Is Null")
    specular_highlight: bpy.props.FloatProperty(
        name="Specular Highlight",
        description="Used as Roughness value in PHYSICAL Reflectance Method",
        default=0.0,
        min=0.0,
        max=1.0,
        update=update_shader_graph,
    )
    reflectance_method: EnumProperty(
        name="Reflectance Method",
        items=get_reflectance_methods,
        update=update_shader_graph,
    )

    # textures props
    textures: CollectionProperty(name="Textures", type=Texture)
    uv_mode: EnumProperty(
        name="UV Mode",
        description="Type of UV used for the textures",
        items=UV_MODES,
        default="UV",
        update=update_shader_graph,
    )

    styles: CollectionProperty(name="Styles", type=Style)
    active_style_index: IntProperty(name="Active Style Index")
    active_style_type: EnumProperty(
        name="Active Style Type",
        description="Update current blender material to match style type for all objects in the scene",
        items=STYLE_TYPES,
        default="Shading",
        update=update_shading_styles,
    )


def switch_shading(blender_material: bpy.types.Material, style_type: Literal["External", "Shading"]) -> None:
    if style_type == "External":
        try:
            bpy.ops.bim.activate_external_style(material_name=blender_material.name)
        except RuntimeError as error:
            if str(error).startswith("Error: Error loading external style for "):
                return
            raise error
    elif style_type == "Shading":
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


def update_shading_style(self, context):
    blender_material = self.id_data
    style_elements = tool.Style.get_style_elements(blender_material)
    if self.active_style_type == "External":
        if tool.Style.has_blender_external_style(style_elements):
            switch_shading(blender_material, self.active_style_type)
    elif self.active_style_type == "Shading":
        switch_shading(blender_material, self.active_style_type)
    tool.Style.record_shading(blender_material)


class BIMStyleProperties(PropertyGroup):
    # TODO: remove, as attributes already moved to styles ui
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
