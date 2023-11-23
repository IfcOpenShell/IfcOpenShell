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


class BIMStylesProperties(PropertyGroup):
    is_adding: BoolProperty(name="Is Adding")
    is_editing: BoolProperty(name="Is Editing")
    is_editing_style: IntProperty(name="Is Editing Style")
    is_editing_class: StringProperty(name="Is Editing Class")
    attributes: CollectionProperty(name="Attributes", type=Attribute)
    external_style_attributes: CollectionProperty(name="External Style Attributes", type=Attribute)
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
    surface_colour: bpy.props.FloatVectorProperty(
        name="Surface Colour", subtype="COLOR", default=(1, 1, 1), min=0.0, max=1.0, size=3
    )
    transparency: bpy.props.FloatProperty(name="Transparency", default=0.0, min=0.0, max=1.0)
    is_diffuse_colour_null: BoolProperty(name="Is Null")
    diffuse_colour_class: EnumProperty(
        items=[(x, x, "") for x in ("IfcColourRgb", "IfcNormalisedRatioMeasure")],
        name="Diffuse Colour Class",
    )
    diffuse_colour: bpy.props.FloatVectorProperty(
        name="Diffuse Colour", subtype="COLOR", default=(1, 1, 1), min=0.0, max=1.0, size=3
    )
    diffuse_colour_ratio: bpy.props.FloatProperty(name="Diffuse Ratio", default=0.0, min=0.0, max=1.0)
    is_specular_colour_null: BoolProperty(name="Is Null")
    specular_colour_class: EnumProperty(
        items=[(x, x, "") for x in ("IfcColourRgb", "IfcNormalisedRatioMeasure")],
        name="Specular Colour Class",
    )
    specular_colour: bpy.props.FloatVectorProperty(
        name="Specular Colour", subtype="COLOR", default=(1, 1, 1), min=0.0, max=1.0, size=3
    )
    specular_colour_ratio: bpy.props.FloatProperty(name="Specular Ratio", default=0.0, min=0.0, max=1.0)
    is_specular_highlight_null: BoolProperty(name="Is Null")
    specular_highlight: bpy.props.FloatProperty(name="Specular Highlight", default=0.0, min=0.0, max=1.0)
    reflectance_method: EnumProperty(name="Reflectance Method", items=get_reflectance_methods)
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
    tool.Style.set_surface_style_props(blender_material)
    tool.Style.record_shading(blender_material)


# TODO: support more more methods
REFLECTANCE_METHODS = [
    ("PHYSICAL", "PHYSICAL", ""),
    ("FLAT", "FLAT", ""),
    ("METAL", "METAL", ""),
    ("MATT", "MATT", ""),
    ("GLASS", "GLASS", ""),
    ("NOTDEFINED", "NOTDEFINED", ""),
]


def update_shader_graph(self, context):
    if not self.update_graph:
        return

    material = self.id_data
    style_data = tool.Style.get_surface_style_from_props(material)
    textures_data = tool.Style.get_texture_style_from_props(material)
    tool.Loader.create_surface_style_rendering(material, style_data)
    tool.Loader.create_surface_style_with_textures(material, style_data, textures_data)


def update_graph_get(self):
    return self.get("update_graph", True)


def update_graph_set(self, value):
    self["update_graph"] = value
    if value:
        material = self.id_data
        tool.Style.set_surface_style_props(material)


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

    # GLTF style properties
    update_graph: BoolProperty(
        name="Update Shade Graph on Prop Change",
        description="Update shader graph in real time\nas you update style properties",
        default=True,
        get=update_graph_get,
        set=update_graph_set,
    )
    reflectance_method: EnumProperty(
        name="Reflectance Method",
        description="Reflectance method to use for the material",
        items=REFLECTANCE_METHODS,
        default="PHYSICAL",
        update=update_shader_graph,
    )
    surface_color: bpy.props.FloatVectorProperty(
        name="Surface Color",
        subtype="COLOR",
        default=(1, 1, 1, 1),
        min=0.0,
        max=1.0,
        size=4,
        update=update_shader_graph,
    )
    diffuse_color: bpy.props.FloatVectorProperty(
        name="Diffuse Color",
        subtype="COLOR",
        default=(1, 1, 1, 1),
        min=0.0,
        max=1.0,
        size=4,
        update=update_shader_graph,
    )
    transparency: bpy.props.FloatProperty(
        name="Transparency", default=0.0, min=0.0, max=1.0, update=update_shader_graph
    )
    roughness: bpy.props.FloatProperty(name="Roughness", default=0.0, min=0.0, max=1.0, update=update_shader_graph)
    metallic: bpy.props.FloatProperty(name="Metallic", default=0.0, min=0.0, max=1.0, update=update_shader_graph)
    normal_path: bpy.props.StringProperty(
        name="NormalMap",
        maxlen=1024,
        default="",
        subtype="FILE_PATH",
        update=update_shader_graph,
    )
    emissive_path: bpy.props.StringProperty(
        name="Emissive",
        maxlen=1024,
        default="",
        subtype="FILE_PATH",
        update=update_shader_graph,
    )
    metallic_roughness_path: bpy.props.StringProperty(
        name="Metallic/Roughness",
        maxlen=1024,
        default="",
        subtype="FILE_PATH",
        update=update_shader_graph,
        description="Green Channel = Roughness,\nBlue Channel = Metallic",
    )
    diffuse_path: bpy.props.StringProperty(
        name="Diffuse",
        maxlen=1024,
        default="",
        subtype="FILE_PATH",
        update=update_shader_graph,
    )
    occlusion_path: bpy.props.StringProperty(
        name="Occlusion",
        description="Note that occlusion isn't actually used in Blender shader, we're just storing the data",
        maxlen=1024,
        default="",
        subtype="FILE_PATH",
        update=update_shader_graph,
    )
