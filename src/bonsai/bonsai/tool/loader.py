# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2023 Dion Moult <dion@thinkmoult.com>
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

from __future__ import annotations
import os
import re
import bpy
import math
import bmesh
import logging
import ifcopenshell.geom
import ifcopenshell.util.element
import ifcopenshell.util.geolocation
import ifcopenshell.util.placement
import ifcopenshell.util.representation
import ifcopenshell.util.shape
import ifcopenshell.util.unit
import bonsai.core.tool
import bonsai.tool as tool
import bonsai.bim.import_ifc
import numpy as np
import numpy.typing as npt
from mathutils import Vector, Matrix
from pathlib import Path
from typing import Union, Any


# Progressively we'll refactor loading elements into Blender objects into this
# class. This will break down the monolithic import_ifc module and allow us to
# partially load and unload objects for huge models, partial model editing, and
# supplementary objects (e.g. drawings, structural analysis models, etc).


OBJECT_DATA_TYPE = Union[bpy.types.Mesh, bpy.types.Curve]


class Loader(bonsai.core.tool.Loader):
    unit_scale: float = 1
    settings: bonsai.bim.import_ifc.IfcImportSettings = None

    @classmethod
    def set_unit_scale(cls, unit_scale: float) -> None:
        cls.unit_scale = unit_scale

    @classmethod
    def load_settings(cls) -> None:
        logger = logging.getLogger("ImportIFC")
        cls.settings = bonsai.bim.import_ifc.IfcImportSettings.factory(bpy.context, None, logger)
        cls.settings.contexts = ifcopenshell.util.representation.get_prioritised_contexts(tool.Ifc.get())
        cls.settings.context_settings = cls.create_settings()
        cls.settings.gross_context_settings = cls.create_settings(is_gross=True)

    @classmethod
    def set_settings(cls, settings: bonsai.bim.import_ifc.IfcImportSettings) -> None:
        cls.settings = settings

    @classmethod
    def get_representation_id_from_shape(cls, geometry: ifcopenshell.geom.ShapeType) -> int:
        representation_id: str = geometry.id
        if "-" in representation_id:
            # Example: 2432-openings-2468, where
            # 2432 is mapped representation id
            # and 2468 is IFCRELVOIDSELEMENT
            representation_id = re.sub(r"\D", "", representation_id.split("-")[0])
        else:
            representation_id = re.sub(r"\D", "", representation_id)
        return int(representation_id)

    @classmethod
    def get_mesh_name_from_shape(cls, geometry: ifcopenshell.geom.ShapeType) -> str:
        representation_id = cls.get_representation_id_from_shape(geometry)
        representation = tool.Ifc.get().by_id(representation_id)
        context_id = representation.ContextOfItems.id() if hasattr(representation, "ContextOfItems") else 0
        return cls.get_mesh_name(context_id, representation_id)

    @classmethod
    def get_mesh_name(cls, context_id: int, representation_id: int) -> str:
        return "{}/{}".format(context_id, representation_id)

    @classmethod
    def get_name(cls, element: ifcopenshell.entity_instance) -> str:
        if element.is_a("IfcGridAxis"):
            return "{}/{}".format(element.is_a(), element.AxisTag)
        return "{}/{}".format(element.is_a(), getattr(element, "Name", "None"))

    @classmethod
    def link_mesh(
        cls,
        shape: Union[ifcopenshell.geom.ShapeElementType, ifcopenshell.geom.ShapeType],
        mesh: tool.Geometry.TYPES_WITH_MESH_PROPERTIES,
    ) -> None:
        geometry = shape.geometry if hasattr(shape, "geometry") else shape
        mesh.BIMMeshProperties.ifc_definition_id = int(geometry.id.split("-")[0])

    @classmethod
    def create_surface_style_shading(
        cls, blender_material: bpy.types.Material, surface_style: ifcopenshell.entity_instance
    ) -> None:
        # Shading style is simple and use no node graph.
        surface_style = cls.surface_style_to_dict(surface_style)
        alpha = 1.0
        # Transparency was added in IFC4
        if transparency := surface_style.get("Transparency", None):
            alpha = 1 - transparency
        blender_material.diffuse_color = surface_style["SurfaceColour"] + (alpha,)
        blender_material.use_nodes = False

    @classmethod
    def restart_material_node_tree(cls, blender_material: bpy.types.Material) -> None:
        nodes = blender_material.node_tree.nodes
        links = blender_material.node_tree.links
        for n in nodes[:]:
            nodes.remove(n)
        output = nodes.new("ShaderNodeOutputMaterial")
        output.location = Vector((300, 300))
        bsdf = nodes.new("ShaderNodeBsdfPrincipled")
        bsdf.location = Vector((10, 300))
        links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])

    @classmethod
    def surface_style_to_dict(
        cls, surface_style: Union[ifcopenshell.entity_instance, dict[str, Any]]
    ) -> dict[str, Any]:
        if isinstance(surface_style, dict):
            return surface_style
        surface_style = surface_style.get_info()

        color_to_tuple = lambda x: (x.Red, x.Green, x.Blue)

        def convert_ifc_color_or_factor(color_or_factor):
            if color_or_factor is None:
                return
            if color_or_factor.is_a("IfcColourRgb"):
                return ("IfcColourRgb", color_to_tuple(color_or_factor))
            # IfcNormalisedRatioMeasure
            return ("IfcNormalisedRatioMeasure", color_or_factor.wrappedValue)

        # can be only IfcColourRgb
        if surface_style["SurfaceColour"]:
            surface_style["SurfaceColour"] = color_to_tuple(surface_style["SurfaceColour"])

        if surface_style["type"] == "IfcSurfaceStyleShading":
            return surface_style

        # IfcSurfaceStyleRendering
        # IfcColourOrFactor
        surface_style["DiffuseColour"] = convert_ifc_color_or_factor(surface_style["DiffuseColour"])
        surface_style["SpecularColour"] = convert_ifc_color_or_factor(surface_style["SpecularColour"])

        if specular_highlight := surface_style["SpecularHighlight"]:
            if specular_highlight.is_a("IfcSpecularRoughness"):
                surface_style["SpecularHighlight"] = specular_highlight.wrappedValue
            else:  # discard IfcSpecularExponent value
                surface_style["SpecularHighlight"] = None

        # NOTE: IfcSurfaceStyleRendering also has following attributes but we ignore them
        # as they're about to get deprecated:
        # TransmissionColour, DiffuseTransmissionColour, ReflectionColour

        return surface_style

    @classmethod
    def surface_texture_to_dict(cls, surface_texture):
        if isinstance(surface_texture, dict):
            return surface_texture
        mappings = surface_texture.IsMappedBy or []
        surface_texture = surface_texture.get_info()
        uv_mode = None
        if mappings:
            coordinates = mappings[0]
            if coordinates.is_a("IfcTextureCoordinateGenerator") and coordinates.Mode == "COORD":
                uv_mode = "Generated"
            elif coordinates.is_a("IfcTextureCoordinateGenerator") and coordinates.Mode == "COORD-EYE":
                uv_mode = "Camera"
        surface_texture["uv_mode"] = uv_mode or "UV"
        return surface_texture

    @classmethod
    def create_surface_style_rendering(
        cls, blender_material: bpy.types.Material, surface_style: ifcopenshell.entity_instance
    ) -> None:
        surface_style = cls.surface_style_to_dict(surface_style)
        surface_style: dict[str, Any]

        cls.create_surface_style_shading(blender_material, surface_style)

        reflectance_method = surface_style["ReflectanceMethod"]
        if reflectance_method not in ("PHYSICAL", "NOTDEFINED", "FLAT"):
            print(f'WARNING. Unsupported reflectance method "{reflectance_method}" on style {surface_style}')
            return

        # TODO: reset pins to default values if no values passed
        if reflectance_method in ["PHYSICAL", "NOTDEFINED"]:
            blender_material.use_nodes = True
            cls.restart_material_node_tree(blender_material)
            bsdf = tool.Blender.get_material_node(blender_material, "BSDF_PRINCIPLED")
            assert bsdf

            if surface_style["DiffuseColour"]:
                color_type, color_value = surface_style["DiffuseColour"]
                if color_type == "IfcColourRgb":
                    bsdf.inputs["Base Color"].default_value = color_value + (1,)
                else:  # "IfcNormalisedRatioMeasure"
                    color_value = tuple(v * color_value for v in surface_style["SurfaceColour"])
                    bsdf.inputs["Base Color"].default_value = color_value + (1,)

            if surface_style["SpecularColour"]:
                color_type, color_value = surface_style["SpecularColour"]
                if color_type == "IfcNormalisedRatioMeasure":
                    bsdf.inputs["Metallic"].default_value = color_value
                # IfcColourRgb is ignored

            if surface_style["SpecularHighlight"]:
                bsdf.inputs["Roughness"].default_value = surface_style["SpecularHighlight"]

            if transparency := surface_style.get("Transparency", None):
                bsdf.inputs["Alpha"].default_value = 1 - transparency
                blender_material.blend_method = "BLEND"

        elif reflectance_method == "FLAT":
            blender_material.use_nodes = True
            cls.restart_material_node_tree(blender_material)

            output = tool.Blender.get_material_node(blender_material, "OUTPUT_MATERIAL")
            bsdf = tool.Blender.get_material_node(blender_material, "BSDF_PRINCIPLED")
            assert bsdf
            assert output

            assert blender_material.node_tree
            mix = blender_material.node_tree.nodes.new(type="ShaderNodeMixShader")
            mix.location = bsdf.location
            blender_material.node_tree.links.new(mix.outputs[0], output.inputs["Surface"])

            blender_material.node_tree.nodes.remove(bsdf)

            lightpath = blender_material.node_tree.nodes.new(type="ShaderNodeLightPath")
            lightpath.location = mix.location - Vector((200, -200))
            blender_material.node_tree.links.new(lightpath.outputs[0], mix.inputs[0])

            bsdf = blender_material.node_tree.nodes.new(type="ShaderNodeBsdfTransparent")
            bsdf.location = mix.location - Vector((200, 150))
            blender_material.node_tree.links.new(bsdf.outputs[0], mix.inputs[1])

            rgb = blender_material.node_tree.nodes.new(type="ShaderNodeRGB")
            rgb.location = mix.location - Vector((200, 250))
            blender_material.node_tree.links.new(rgb.outputs[0], mix.inputs[2])

            if surface_style["DiffuseColour"]:
                color_type, color_value = surface_style["DiffuseColour"]
                if color_type == "IfcColourRgb":
                    rgb.outputs[0].default_value = color_value + (1,)

    @classmethod
    def create_surface_style_with_textures(cls, blender_material, rendering_style, texture_style):
        """supposed to be called after `create_surface_style_rendering`"""
        if not isinstance(texture_style, list):  # assume it's IfcSurfaceStyleWithTextures
            textures = [cls.surface_texture_to_dict(t) for t in texture_style.Textures]
        else:
            textures = texture_style
        rendering_style = cls.surface_style_to_dict(rendering_style)

        # `rendering_style` is a dict and `textures` is a list of dicts
        # containing ifc data, that way method can be called by just providing those dictionaries
        # without actually changing IFC data

        reflectance_method = rendering_style["ReflectanceMethod"]
        if reflectance_method not in ("PHYSICAL", "NOTDEFINED", "FLAT"):
            print(f'WARNING. Unsupported reflectance method "{reflectance_method}" on style {rendering_style}')
            return

        for texture in textures:
            mode = texture.get("Mode", None)
            node = None

            image_url = None

            def get_image() -> Union[bpy.types.Image, None]:
                # TODO: orphaned textures after shader recreated?
                if texture["type"] == "IfcImageTexture":
                    original_image_url = texture["URLReference"]
                    is_relative = not os.path.isabs(original_image_url)
                    nonlocal image_url
                    image_url = Path(original_image_url)
                    if is_relative:
                        ifc_path = Path(tool.Ifc.get_path())
                        image_url = ifc_path.parent / image_url

                    if not image_url.exists():
                        print(f"WARNING. Couldn't find texture by path {image_url}, it will be skipped.")
                        return

                    # keep url relative if it was before
                    image_url = str(image_url)
                    if is_relative and bpy.data.filepath:
                        image_url = bpy.path.relpath(image_url)
                    return bpy.data.images.load(image_url)

                elif texture["type"] == "IfcBlobTexture":
                    # https://blender.stackexchange.com/questions/173206/how-to-efficiently-convert-a-pil-image-to-bpy-types-image
                    # https://blender.stackexchange.com/questions/62072/does-blender-have-a-method-to-a-get-png-formatted-bytearray-for-an-image-via-pyt
                    import io
                    from PIL import Image

                    value = texture["RasterCode"]
                    image_bytes = int(value, 2).to_bytes(len(value) // 8, "big")
                    pil_image = Image.open(io.BytesIO(image_bytes))
                    byte_to_normalized = 1.0 / 255.0
                    bpy_image = bpy.data.images.new("blob_texture", width=pil_image.width, height=pil_image.height)
                    # PIL returns rows ordered from top to bottom, blender from bottom to top
                    pil_pixel_data = np.asarray(pil_image.convert("RGBA"), dtype=np.float32)
                    bpy_image.pixels[:] = (pil_pixel_data * byte_to_normalized)[::-1].ravel()
                    bpy_image.pack()
                    return bpy_image

                # IfcPixelTexture
                n_components = texture["ColourComponents"]
                width, height = texture["Width"], texture["Height"]
                blender_pixel_data = np.ones(width * height * 4, dtype=np.float32)

                # according to https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcPixelTexture.htm
                # 1 component - grey scale intensity value
                # 2 components - grey scale + alpha
                # 3 components - RGB
                # 4 components - RGBA
                for i, pixel_str in enumerate(iterable=texture["Pixel"]):
                    pixel_bytes = int(pixel_str, 2).to_bytes(len(pixel_str) // 8, "big")
                    pixel_values = np.array(list(pixel_bytes)) / 255
                    cur_pos = i * 4

                    if n_components in (1, 2):
                        blender_pixel_data[cur_pos : cur_pos + 3] = pixel_values[0]
                        if n_components == 2:
                            blender_pixel_data[cur_pos + 3] = pixel_values[1]
                        continue

                    # 3, 4 components
                    blender_pixel_data[cur_pos : cur_pos + 3] = pixel_values[:3]
                    if n_components == 4:
                        blender_pixel_data[cur_pos + 3] = pixel_values[3]

                bpy_image = bpy.data.images.new("pixel_texture", width=width, height=height)
                bpy_image.pixels[:] = blender_pixel_data
                bpy_image.pack()
                return bpy_image

            if reflectance_method in ["PHYSICAL", "NOTDEFINED"]:
                bsdf = tool.Blender.get_material_node(blender_material, "BSDF_PRINCIPLED")

                SUPPORTED_PBR_TEXTURES = ("NORMAL", "EMISSIVE", "METALLICROUGHNESS", "OCCLUSION", "DIFFUSE")
                if mode not in SUPPORTED_PBR_TEXTURES:
                    print(
                        f"WARNING. Texture with {mode} Mode is not supported for style with PHYSICAL reflectance method.\n"
                        f"Supported types are: {', '.join(SUPPORTED_PBR_TEXTURES)}"
                    )
                    if texture["type"] == "IfcImageTexture":
                        print(f"Texture by path {image_url} will be skipped.")
                    continue

                if (image := get_image()) is None:
                    continue

                if mode == "NORMAL":
                    # add normal map node
                    normalmap = blender_material.node_tree.nodes.new(type="ShaderNodeNormalMap")
                    normalmap.location = bsdf.location - Vector((200, 600))
                    blender_material.node_tree.links.new(normalmap.outputs[0], bsdf.inputs["Normal"])

                    # add normal map sampler
                    node = blender_material.node_tree.nodes.new(type="ShaderNodeTexImage")
                    node.location = normalmap.location - Vector((300, 0))
                    image.colorspace_settings.name = "Non-Color"
                    node.image = image
                    blender_material.node_tree.links.new(node.outputs[0], normalmap.inputs["Color"])

                elif mode == "EMISSIVE":
                    output = tool.Blender.get_material_node(blender_material, "OUTPUT_MATERIAL")

                    # add "Add Shader" node
                    add = blender_material.node_tree.nodes.new(type="ShaderNodeAddShader")
                    add.location = bsdf.location + Vector((200, 350))
                    blender_material.node_tree.links.new(bsdf.outputs[0], add.inputs[1])
                    blender_material.node_tree.links.new(add.outputs[0], output.inputs[0])

                    # add emssion shader node
                    emission = blender_material.node_tree.nodes.new(type="ShaderNodeEmission")
                    emission.location = add.location - Vector((200, 0))
                    blender_material.node_tree.links.new(emission.outputs[0], add.inputs[0])

                    # add emission texture sampler
                    node = blender_material.node_tree.nodes.new(type="ShaderNodeTexImage")
                    node.location = emission.location - Vector((350, 0))
                    node.image = image
                    blender_material.node_tree.links.new(node.outputs[0], emission.inputs[0])

                elif mode == "METALLICROUGHNESS":
                    separate = blender_material.node_tree.nodes.new(type="ShaderNodeSeparateRGB")
                    separate.location = bsdf.location - Vector((200, 300))
                    blender_material.node_tree.links.new(separate.outputs[1], bsdf.inputs["Roughness"])
                    blender_material.node_tree.links.new(separate.outputs[2], bsdf.inputs["Metallic"])

                    node = blender_material.node_tree.nodes.new(type="ShaderNodeTexImage")
                    node.location = separate.location - Vector((300, 0))
                    image.colorspace_settings.name = "Non-Color"
                    node.image = image
                    blender_material.node_tree.links.new(node.outputs[0], separate.inputs[0])

                elif mode == "OCCLUSION":

                    def get_gltf_occlusion_output():
                        gltf_node_group_name = "glTF Material Output"
                        if node_group := bpy.data.node_groups.get(gltf_node_group_name, None):
                            return node_group

                        gltf_node_group = bpy.data.node_groups.new(gltf_node_group_name, "ShaderNodeTree")
                        gltf_node_group.inputs.new("NodeSocketFloat", "Occlusion")
                        gltf_node_group.nodes.new("NodeGroupOutput")
                        gltf_node_group_input = gltf_node_group.nodes.new("NodeGroupInput")
                        gltf_node_group_input.location = Vector((-200, 0))
                        return gltf_node_group

                    gltf_output_node_group = get_gltf_occlusion_output()
                    group = blender_material.node_tree.nodes.new(type="ShaderNodeGroup")
                    group.node_tree = gltf_output_node_group
                    group.location = bsdf.location + Vector((800, 0))

                    node = blender_material.node_tree.nodes.new(type="ShaderNodeTexImage")
                    node.location = group.location - Vector((300, 0))
                    image.colorspace_settings.name = "Non-Color"
                    node.image = image
                    blender_material.node_tree.links.new(node.outputs[0], group.inputs["Occlusion"])

                elif mode == "DIFFUSE":
                    node = blender_material.node_tree.nodes.new(type="ShaderNodeTexImage")
                    node.location = bsdf.location - Vector((400, 0))
                    node.image = image
                    blender_material.node_tree.links.new(node.outputs[0], bsdf.inputs["Base Color"])
                    # leave it to default(OPAQUE) when no Transparency defined
                    if transparency := rendering_style.get("Transparency", None):
                        blender_material.node_tree.links.new(node.outputs[1], bsdf.inputs["Alpha"])
                        blender_material.blend_method = "BLEND"

            elif reflectance_method == "FLAT":
                bsdf = tool.Blender.get_material_node(blender_material, "MIX_SHADER")
                if mode != "EMISSIVE":
                    print("WARNING. Only EMISSIVE Mode textures are supported for style with FLAT reflectance method.")
                    if texture["type"] == "IfcImageTexture":
                        print(f"{mode} Mode texture by path {image_url} will be skipped.")
                    else:
                        print(f"{mode} Mode texture will be skipped.")
                    continue

                if (image := get_image) is None:
                    continue

                # remove RGB node from `create_surface_style_rendering`
                prev_node = bsdf.inputs[2].links[0].from_node
                blender_material.node_tree.nodes.remove(prev_node)

                node = blender_material.node_tree.nodes.new(type="ShaderNodeTexImage")
                node.location = bsdf.location - Vector((200, 250))
                node.image = image

                blender_material.node_tree.links.new(node.outputs[0], bsdf.inputs[2])

            # extend the image by repeating pixels on its edges if RepeatS or RepeatT is False
            repeat_s = texture.get("RepeatS", True)
            repeat_t = texture.get("RepeatT", True)
            if not repeat_s or not repeat_t:
                node.extension = "EXTEND"

            # IsMappedBy could only get with the entity_instance for IFC4/IFC4x3
            coord = blender_material.node_tree.nodes.new(type="ShaderNodeTexCoord")
            coord.location = node.location - Vector((200, 0))
            if texture["uv_mode"] == "Generated":
                blender_material.node_tree.links.new(coord.outputs["Generated"], node.inputs["Vector"])
            elif texture["uv_mode"] == "Camera":
                blender_material.node_tree.links.new(coord.outputs["Camera"], node.inputs["Vector"])
            else:  # uv_mode == UV
                blender_material.node_tree.links.new(coord.outputs["UV"], node.inputs["Vector"])

    @classmethod
    def load_indexed_colour_map(
        cls, representation_or_item: ifcopenshell.entity_instance, mesh: bpy.types.Mesh
    ) -> None:
        """Ensure indexed colour map is loaded for representation if it's available.

        Method doesn't support elements with openings, see #5405.

        :param representation: IfcShapeRepresentation or IfcRepresentationItem of any type.
            Representation may not have an indexed colour map,
            method will automatically check if it does and will skip it otherwise.

        :raises AssertionError: If mesh doesn't match the representation exactly, which usually occurs
            if element geometry is altered by openings.
        """

        is_representation = representation_or_item.is_a("IfcShapeRepresentation")

        if is_representation:
            if representation_or_item.RepresentationType != "Tessellation":
                return
            items = representation_or_item.Items
        else:
            items = [representation_or_item]

        colours = []
        for item in items:
            if not item.is_a("IfcTessellatedFaceSet"):
                continue
            # It's unclear what has priority, styled by item or indexed maps
            # Given that indexed maps currently are super expensive, I'll prioritise styled by item
            # May lead to issues if external style is using vertex colors
            # but probably don't need to worry about until we add a way save vertex colors to indexed map in BBIM.
            if item.StyledByItem:
                continue
            colours.extend(item.HasColours)

        if not colours:
            return

        for colour in colours:
            cls.load_indexed_map(colour, mesh)

    @classmethod
    def load_indexed_map(cls, index_map: ifcopenshell.entity_instance, mesh: bpy.types.Mesh) -> None:
        """Add data from index map as blender mesh attribute.

        :param index_map: IfcIndexedTextureMap or IfcIndexedColourMap
        """

        map_type = "UV" if index_map.is_a("IfcIndexedTextureMap") else "Color"

        # Get a BMesh representation
        bm = bmesh.new()
        bm.from_mesh(mesh)
        if map_type == "UV":
            # constistent naming with how Blender does it
            layer = bm.loops.layers.uv.active or bm.loops.layers.uv.new("UVMap")
        else:
            layer = bm.loops.layers.float_color.new("Color")

        # remap the faceset CoordList index to the vertices in blender mesh
        coordinates_remap = []
        si_conversion = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        faceset = index_map.MappedTo
        for co in faceset.Coordinates.CoordList:
            co = Vector(co) * si_conversion
            index = min(bm.verts, key=lambda v: (v.co - co).length_squared).index
            coordinates_remap.append(index)

        # ifc indices start with 1
        remap_verts_to_blender = lambda ifc_verts: [coordinates_remap[i - 1] for i in ifc_verts]

        # faces_remap - ifc faces described using blender verts indices
        # IFC4.3+
        if index_map.is_a("IfcIndexedPolygonalTextureMap"):
            faces_remap = [
                remap_verts_to_blender(tex_coord_index.TexCoordsOf.CoordIndex)
                for tex_coord_index in index_map.TexCoordIndices
            ]
            texture_map = [tex_coord_index.TexCoordIndex for tex_coord_index in index_map.TexCoordIndices]
        else:  # IfcIndexedTriangleTextureMap or IfcIndexedColourMap
            if faceset.is_a("IfcTriangulatedFaceSet"):
                faces_remap = [remap_verts_to_blender(triangle_face) for triangle_face in faceset.CoordIndex]
            else:  # IfcPolygonalFaceSet
                faces_remap = [remap_verts_to_blender(face.CoordIndex) for face in faceset.Faces]
            if index_map.is_a("IfcIndexedTriangleTextureMap"):
                texture_map = index_map.TexCoordIndex
            else:
                texture_map = index_map.ColourIndex

        if map_type == "UV":
            data_list = index_map.TexCoords.TexCoordsList
        else:
            data_list = index_map.Colours.ColourList
            opacity = index_map.Opacity
            opacity = opacity if opacity is not None else 1.0
            data_list = [d + (opacity,) for d in data_list]

        # Apply attribute to each face
        for bface in bm.faces:
            face = [loop.vert.index for loop in bface.loops]
            # Find the corresponding index in data list by matching ifc faceset with blender face.
            data_index = None
            for tex_coord_index, face_remap in zip(texture_map, faces_remap, strict=True):
                if not all(i in face_remap for i in face):
                    continue
                # Subtract 1 as tex_coord_index starts with 1.
                if map_type == "UV":
                    data_index = [tex_coord_index[face_remap.index(i)] - 1 for i in face]
                else:
                    data_index = [tex_coord_index - 1 for i in face]
                break

            if data_index is None:
                # This face may be part of another representation item
                # Or we couldn't match it due to georeferencing.
                continue

            # apply uv to each loop
            for loop, i in zip(bface.loops, data_index):
                if map_type == "UV":
                    loop[layer].uv = data_list[i]
                else:
                    loop[layer] = data_list[i]

        # Finish up, write the bmesh back to the mesh
        bm.to_mesh(mesh)
        bm.free()

        if map_type == "Color":
            # Couldn't find a way to do it from bmesh.
            mesh.color_attributes.active_color_index = 0

    @classmethod
    def is_point_far_away(
        cls, point: Union[ifcopenshell.entity_instance, npt.NDArray[np.float64]], is_meters: bool = True
    ) -> bool:
        limit = cls.settings.distance_limit
        limit = limit if is_meters else (limit / cls.unit_scale)
        coords = getattr(point, "Coordinates", point)
        return abs(coords[0]) > limit or abs(coords[1]) > limit or abs(coords[2]) > limit

    @classmethod
    def is_element_far_away(cls, element: ifcopenshell.entity_instance) -> bool:
        try:
            placement = ifcopenshell.util.placement.get_local_placement(element.ObjectPlacement)
            point = placement[:, 3][0:3]
            return tool.Loader.is_point_far_away(point, is_meters=False)
        except:
            return False

    @classmethod
    def create_settings(cls, is_gross=False):
        results = []
        for context in cls.settings.contexts:
            settings = ifcopenshell.geom.settings()
            settings.set("mesher-linear-deflection", cls.settings.deflection_tolerance)
            settings.set("mesher-angular-deflection", cls.settings.angular_tolerance)
            settings.set("dimensionality", ifcopenshell.ifcopenshell_wrapper.CURVES_SURFACES_AND_SOLIDS)
            settings.set("context-ids", [context.id()])
            settings.set("apply-default-materials", False)
            settings.set("keep-bounding-boxes", True)
            settings.set("layerset-first", True)
            # settings.set("triangulation-type", ifcopenshell.ifcopenshell_wrapper.POLYHEDRON_WITHOUT_HOLES)
            if is_gross:
                settings.set("disable-opening-subtractions", True)
            results.append(settings)
        return results

    @classmethod
    def set_manual_blender_offset(cls, ifc_file: ifcopenshell.file) -> None:
        false_origin = np.array(cls.settings.false_origin)
        model_offset = np.array(
            ifcopenshell.util.geolocation.auto_enh2xyz(
                ifc_file, *cls.settings.false_origin, is_specified_in_map_units=False
            )
        )
        zero_origin = np.array((0, 0, 0))
        has_offset = not np.allclose(model_offset, zero_origin)

        model_north = ifcopenshell.util.geolocation.get_grid_north(ifc_file)
        project_north = cls.settings.project_north
        model_rotation = tool.Cad.normalise_angle(project_north - model_north)
        has_rotation = not np.isclose(model_north, project_north)

        if not has_offset:
            model_offset = false_origin = (0, 0, 0)

        if np.isclose(project_north, 0):
            project_north = 0

        if has_offset or has_rotation:
            props = bpy.context.scene.BIMGeoreferenceProperties
            props.blender_offset_x = str(model_offset[0])
            props.blender_offset_y = str(model_offset[1])
            props.blender_offset_z = str(model_offset[2])
            xaa, xao = ifcopenshell.util.geolocation.angle2xaxis(model_rotation)
            props.blender_x_axis_abscissa = str(xaa)
            props.blender_x_axis_ordinate = str(xao)
            props.has_blender_offset = True

    @classmethod
    def guess_false_origin_and_project_north(
        cls, ifc_file: ifcopenshell.file, element: ifcopenshell.entity_instance
    ) -> None:
        if not element.ObjectPlacement or not element.ObjectPlacement.is_a("IfcLocalPlacement"):
            return
        placement = ifcopenshell.util.placement.get_local_placement(element.ObjectPlacement)
        offset_point = [placement[0][3], placement[1][3], placement[2][3]]
        cls.settings.false_origin = ifcopenshell.util.geolocation.auto_xyz2enh(
            ifc_file, *offset_point, should_return_in_map_units=False
        )

        # Prioritise coordinate operation angles
        angle = ifcopenshell.util.geolocation.get_grid_north(ifc_file)
        if np.isclose(angle, 0.0):
            # Fallback to the placement angle as a good guess
            xaa, xao = placement[:, 0][0:2]
            angle = ifcopenshell.util.geolocation.xaxis2angle(xaa, xao)

        cls.settings.project_north = 0 if np.isclose(angle, 0) else angle
        cls.set_manual_blender_offset(ifc_file)

    @classmethod
    def find_decomposed_ifc_class(
        cls, element: ifcopenshell.entity_instance, ifc_class: str
    ) -> Union[ifcopenshell.entity_instance, None]:
        if element.is_a(ifc_class):
            return element
        rel_aggregates = element.IsDecomposedBy
        for rel_aggregate in rel_aggregates:
            for part in rel_aggregate.RelatedObjects:
                result = cls.find_decomposed_ifc_class(part, ifc_class)
                if result:
                    return result

    @classmethod
    def create_generic_shape(
        cls, element: ifcopenshell.entity_instance, is_gross: bool = False
    ) -> Union[ifcopenshell.geom.ShapeElementType, None]:
        context_settings = cls.settings.gross_context_settings if is_gross else cls.settings.context_settings
        geometry_library = bpy.context.scene.BIMProjectProperties.geometry_library
        for settings in context_settings:
            try:
                result = ifcopenshell.geom.create_shape(settings, element, geometry_library=geometry_library)
                if result:
                    return result
            except:
                pass

    @classmethod
    def create_point_cloud_mesh(cls, representation: ifcopenshell.entity_instance) -> Union[bpy.types.Mesh, None]:
        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        vertex_list = []
        for item in representation.Items:
            if item.is_a("IfcCartesianPointList3D"):
                vertex_list.extend(Vector(list(coordinates)) * unit_scale for coordinates in item.CoordList)
            elif item.is_a("IfcCartesianPointList2D"):
                vertex_list.extend(Vector(list(coordinates)).to_3d() * unit_scale for coordinates in item.CoordList)
            elif item.is_a("IfcCartesianPoint"):
                vertex_list.append(Vector(list(item.Coordinates)) * unit_scale)

        if len(vertex_list) == 0:
            return None

        mesh_name = tool.Geometry.get_representation_name(representation)
        mesh = bpy.data.meshes.new(mesh_name)
        mesh.from_pydata(vertex_list, [], [])
        return mesh

    @classmethod
    def create_camera(
        cls,
        element: ifcopenshell.entity_instance,
        representation: ifcopenshell.entity_instance,
        shape: Union[ifcopenshell.geom.ShapeElementType, ifcopenshell.geom.ShapeType],
    ) -> bpy.types.Camera:
        from bonsai.bim.module.drawing.prop import get_diagram_scales

        if isinstance(shape, ifcopenshell.geom.ShapeElementType):
            geometry = shape.geometry
        else:
            geometry = shape

        v = geometry.verts
        x = [v[i] for i in range(0, len(v), 3)]
        y = [v[i + 1] for i in range(0, len(v), 3)]
        z = [v[i + 2] for i in range(0, len(v), 3)]
        width = max(x) - min(x)
        height = max(y) - min(y)
        depth = max(z) - min(z)

        camera_type = "ORTHO"
        if "IfcRectangularPyramid" in {e.is_a() for e in tool.Ifc.get().traverse(representation)}:
            camera_type = "PERSP"

        camera = bpy.data.cameras.new(tool.Loader.get_mesh_name_from_shape(geometry))
        camera.type = camera_type
        camera.show_limits = True

        if camera_type == "ORTHO":
            camera.clip_start = 0.002  # Technically 0, but Blender doesn't allow this, so 2mm it is!
            camera.clip_end = depth

            camera.BIMCameraProperties.width = width
            camera.BIMCameraProperties.height = height
        elif camera_type == "PERSP":
            abs_min_z = abs(min(z))
            abs_max_z = abs(max(z))
            camera.clip_start = abs_max_z
            camera.clip_end = abs_min_z
            max_res = 1000

            camera.BIMCameraProperties.width = width
            camera.BIMCameraProperties.height = height

            if width > height:
                fov = 2 * math.atan(width / (2 * abs_min_z))
            else:
                fov = 2 * math.atan(height / (2 * abs_min_z))

            camera.angle = fov

        tool.Drawing.import_camera_props(element, camera)
        return camera

    @classmethod
    def get_offset_point(cls, ifc_file: ifcopenshell.file) -> Union[npt.NDArray[np.float64], None]:
        # Check walls first, as they're usually cheap
        elements = ifc_file.by_type("IfcWall")
        elements += ifc_file.by_type("IfcElement")

        if ifc_file.schema not in ("IFC2X3", "IFC4"):
            elements += ifc_file.by_type("IfcLinearPositioningElement")
            elements += ifc_file.by_type("IfcReferent")
            elements += ifc_file.by_type("IfcGrid")

        if ifc_file.schema == "IFC2X3":
            elements += ifc_file.by_type("IfcSpatialStructureElement")
        else:
            elements += ifc_file.by_type("IfcSpatialElement")

        for element in elements:
            if not element.Representation:
                continue
            shape = cls.create_generic_shape(element, is_gross=True)
            if not shape:
                continue
            mat = ifcopenshell.util.shape.get_shape_matrix(shape)
            point = mat @ np.array((shape.geometry.verts[0], shape.geometry.verts[1], shape.geometry.verts[2], 1.0))
            if cls.is_point_far_away(point, is_meters=True):
                # Arbitrary origins should be to the nearest millimeter.
                # Anything more precise is just ridiculous from a practical surveying perspective.
                return [round(float(p), 3) / cls.unit_scale for p in point[:3]]
            break

    @classmethod
    def guess_false_origin_from_elements(cls, ifc_file: ifcopenshell.file) -> None:
        # Civil BIM applications like to work in absolute coordinates, where the
        # ObjectPlacement is usually 0,0,0 (but not always, so we'll need to
        # check for the actual transformation) but each individual coordinate of
        # the shape representation is in absolute values.
        offset_point = cls.get_offset_point(ifc_file)
        if offset_point is None:
            return
        cls.settings.false_origin = ifcopenshell.util.geolocation.auto_xyz2enh(
            ifc_file, *offset_point, should_return_in_map_units=False
        )
        if (angle := ifcopenshell.util.geolocation.get_grid_north(ifc_file)) and not tool.Cad.is_x(angle, 0):
            cls.settings.project_north = angle
        cls.set_manual_blender_offset(ifc_file)

    @classmethod
    def guess_false_origin(cls, ifc_file: ifcopenshell.file) -> None:
        if ifc_file.schema == "IFC2X3":
            project = ifc_file.by_type("IfcProject")[0]
        else:
            project = ifc_file.by_type("IfcContext")[0]
        site = cls.find_decomposed_ifc_class(project, "IfcSite")
        if site and cls.is_element_far_away(site):
            return cls.guess_false_origin_and_project_north(ifc_file, site)
        building = cls.find_decomposed_ifc_class(project, "IfcBuilding")
        if building and cls.is_element_far_away(building):
            return cls.guess_false_origin_and_project_north(ifc_file, building)
        return cls.guess_false_origin_from_elements(ifc_file)

    @classmethod
    def apply_blender_offset_to_matrix_world(cls, obj: bpy.types.Object, matrix: np.ndarray) -> Matrix:
        if (
            not obj.data
            and tool.Cad.is_x(matrix[0][3], 0)
            and tool.Cad.is_x(matrix[1][3], 0)
            and tool.Cad.is_x(matrix[2][3], 0)
        ):
            # We assume any non-geometric matrix at 0,0,0 is not
            # positionally significant and is left alone. This handles
            # scenarios where often spatial elements are left at 0,0,0 and
            # everything else is at map coordinates.
            obj.BIMObjectProperties.blender_offset_type = "NOT_APPLICABLE"
            return Matrix(matrix.tolist())

        if obj.data and obj.data.get("has_cartesian_point_offset", None):
            obj.BIMObjectProperties.blender_offset_type = "CARTESIAN_POINT"
            if cartesian_point_offset := obj.data.get("cartesian_point_offset", None):
                obj.BIMObjectProperties.cartesian_point_offset = cartesian_point_offset
                offset_xyz = list(map(float, cartesian_point_offset.split(","))) + [1.0]
                offset_xyz = matrix @ offset_xyz
                matrix[0][3] = offset_xyz[0]
                matrix[1][3] = offset_xyz[1]
                matrix[2][3] = offset_xyz[2]

        props = bpy.context.scene.BIMGeoreferenceProperties
        if props.has_blender_offset:
            if obj.BIMObjectProperties.blender_offset_type == "NONE":
                obj.BIMObjectProperties.blender_offset_type = "OBJECT_PLACEMENT"
            matrix = ifcopenshell.util.geolocation.global2local(
                matrix,
                float(props.blender_offset_x) * cls.unit_scale,
                float(props.blender_offset_y) * cls.unit_scale,
                float(props.blender_offset_z) * cls.unit_scale,
                float(props.blender_x_axis_abscissa),
                float(props.blender_x_axis_ordinate),
            )
        return Matrix(matrix.tolist())

    @classmethod
    def convert_geometry_to_mesh(
        cls, geometry: ifcopenshell.geom.ShapeType, mesh: bpy.types.Mesh, verts=None
    ) -> bpy.types.Mesh:
        if verts is None:
            verts = geometry.verts
        if geometry.faces:
            num_vertices = len(verts) // 3

            # See bug 3546
            # ios_edges holds true edges that aren't triangulated.
            #
            # we do `.tolist()` because Blender can't assign `np.int32` to it's custom attributes
            mesh["ios_edges"] = list(set(tuple(e) for e in ifcopenshell.util.shape.get_edges(geometry).tolist()))
            mesh["ios_item_ids"] = ifcopenshell.util.shape.get_faces_representation_item_ids(geometry).tolist()

            mesh.vertices.add(num_vertices)
            mesh.vertices.foreach_set("co", verts)

            is_triangulated = True
            if is_triangulated:
                total_faces = len(geometry.faces)
                num_vertex_indices = len(geometry.faces)
                loop_start = range(0, total_faces, 3)
                num_loops = total_faces // 3
                loop_total = [3] * num_loops

                mesh.loops.add(num_vertex_indices)
                mesh.loops.foreach_set("vertex_index", geometry.faces)
                mesh.polygons.add(num_loops)
                mesh.polygons.foreach_set("loop_start", loop_start)
                mesh.polygons.foreach_set("loop_total", loop_total)
                mesh.polygons.foreach_set("use_smooth", [0] * total_faces)
            else:
                faces_array = np.array(geometry.faces, dtype=object)
                loop_total = tuple(len(face) for face in faces_array)
                loop_start = np.cumsum((0,) + loop_total)[:-1]
                vertex_index = np.concatenate(faces_array)

                mesh.loops.add(len(vertex_index))
                mesh.loops.foreach_set("vertex_index", vertex_index)
                mesh.polygons.add(len(loop_start))
                mesh.polygons.foreach_set("loop_start", loop_start)
                mesh.polygons.foreach_set("loop_total", loop_total)
                mesh.polygons.foreach_set("use_smooth", [0] * len(geometry.faces))

            mesh.update()

            rep_str: str = geometry.id
            if "openings" not in rep_str:
                rep_id = rep_str.split("-", 1)[0]
                rep = tool.Ifc.get().by_id(int(rep_id))
                # For now, not necessary to load maps in Item mode
                if rep.is_a("IfcShapeRepresentation"):
                    tool.Loader.load_indexed_colour_map(rep, mesh)
        else:
            e = geometry.edges
            v = verts
            vertices = [[v[i], v[i + 1], v[i + 2]] for i in range(0, len(v), 3)]
            edges = [[e[i], e[i + 1]] for i in range(0, len(e), 2)]
            mesh.from_pydata(vertices, edges, [])
            # TODO: remove error handling after we update build in Bonsai.
            try:
                edges_item_ids = ifcopenshell.util.shape.get_edges_representation_item_ids(geometry).tolist()
            except AttributeError:
                edges_item_ids = []
            mesh["ios_edges_item_ids"] = edges_item_ids

        mesh["ios_materials"] = [m.instance_id() for m in geometry.materials]
        mesh["ios_material_ids"] = geometry.material_ids
        return mesh

    @classmethod
    def setup_active_bsdd_classification(cls) -> None:
        ifc_file = tool.Ifc.get()
        schema = ifc_file.schema

        # In IFC2X3 IfcClassification doesn't have an attribute for uri.
        if schema == "IFC2X3":
            classifications = [c for c in ifc_file.by_type("IfcClassification") if c.Name]
            if not classifications:
                return
            pattern = r"^https://identifier\.buildingsmart\.org/uri/([a-zA-Z0-9]+)/([a-zA-Z0-9]+)/([0-9]+\.[0-9]+)"

            # No inverse attribute in IFC2X3...
            for ref in ifc_file.by_type("IfcClassificationReference"):
                if (
                    not (uri := ref.Location)
                    or not uri.startswith("https://identifier.buildingsmart.org/uri/")
                    or not (pattern_match := re.match(pattern, uri))
                    or not (classification := ref.ReferencedSource)
                    or classification not in classifications
                    or not classification.is_a("IfcClassification")
                ):
                    continue
                tool.Bsdd.set_active_bsdd(classification.Name, pattern_match.group(0))
            return

        attr_name = "Specification" if schema == "IFC4X3" else "Location"
        bsdd_classification, uri, name = None, None, None
        for c in ifc_file.by_type("IfcClassification"):
            if (
                (uri := getattr(c, attr_name))
                and uri.startswith("https://identifier.buildingsmart.org/uri/")
                and (name := c.Name)
            ):
                bsdd_classification = c
                break
        if not bsdd_classification:
            return
        assert name and uri
        tool.Bsdd.set_active_bsdd(name, uri)

    @classmethod
    def is_native_swept_disk_solid(
        cls, element: ifcopenshell.entity_instance, representation: ifcopenshell.entity_instance
    ) -> bool:
        items = [i["item"] for i in ifcopenshell.util.representation.resolve_items(representation)]
        if len(items) == 1 and items[0].is_a("IfcSweptDiskSolid"):
            if tool.Blender.Modifier.is_railing(element):
                return False
            return True
        elif len(items) and (  # See #2508 why we accommodate for invalid IFCs here
            items[0].is_a("IfcSweptDiskSolid")
            and len({i.is_a() for i in items}) == 1
            and len({i.Radius for i in items}) == 1
        ):
            if tool.Blender.Modifier.is_railing(element):
                return False
            return True
        return False

    @classmethod
    def create_native_swept_disk_solid(
        cls, element: ifcopenshell.entity_instance, mesh_name: str, native_data: dict[str, Any]
    ) -> tuple[bpy.types.Curve, Union[float, None]]:
        """Create Blender curve based on element using IfcSweptDiskAreaSolid.

        :return: created curve and it's thickness (suppose to add the thickness to the object
            using solidify modifier). Returns `None` instead of thickness if disk has no inner radius
            or if it's invalid.
        """
        # TODO: georeferencing?
        ifc_file = tool.Ifc.get()
        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(ifc_file)
        curve = bpy.data.curves.new(mesh_name, type="CURVE")
        curve.dimensions = "3D"
        curve.resolution_u = 2

        rep_items = ifcopenshell.util.representation.resolve_items(native_data["representation"])

        # Find item styles and add them to the curve.
        material_style = None
        material = ifcopenshell.util.element.get_material(element)
        if material:
            material_style = tool.Material.get_style(material)
        item_styles: list[Union[bpy.types.Material, None]] = []
        for item_data in rep_items:
            item = item_data["item"]
            item_style = tool.Style.get_representation_item_style(item) or material_style
            if item_style is not None:
                item_style = tool.Ifc.get_object(item_style)
                assert isinstance(item_style, bpy.types.Material)
            item_styles.append(item_style)
        item_styles_unique = list(set(item_styles))
        for item_style in item_styles_unique:
            curve.materials.append(item_style)
        use_same_material_index = len(item_styles_unique) < 2

        def new_polyline(item_style: Union[bpy.types.Material, None]) -> bpy.types.Spline:
            if use_same_material_index:
                material_index = 0
            else:
                material_index = item_styles_unique.index(item_style)

            polyline = curve.splines.new("POLY")
            polyline.material_index = material_index
            return polyline

        for item_data, item_style in zip(rep_items, item_styles):
            item = item_data["item"]

            polyline = new_polyline(item_style)
            matrix = item_data["matrix"]
            matrix[0][3] *= unit_scale
            matrix[1][3] *= unit_scale
            matrix[2][3] *= unit_scale

            # TODO: start param, and end param
            geometry = tool.Loader.create_generic_shape(item.Directrix)
            if not geometry:
                continue
            e = geometry.edges
            v = geometry.verts
            vertices = [list(matrix @ [v[i], v[i + 1], v[i + 2], 1]) for i in range(0, len(v), 3)]
            edges = [[e[i], e[i + 1]] for i in range(0, len(e), 2)]
            v2 = None
            for edge in edges:
                v1 = vertices[edge[0]]
                if v1 != v2:
                    polyline = new_polyline(item_style)
                    polyline.points[-1].co = native_data["matrix"] @ Vector(v1)
                v2 = vertices[edge[1]]
                polyline.points.add(1)
                polyline.points[-1].co = native_data["matrix"] @ Vector(v2)

        curve.bevel_depth = unit_scale * item.Radius
        thickness = None
        if (inner_radius := item.InnerRadius) and (thickness := max(item.Radius - inner_radius, 0)):
            thickness *= unit_scale
            curve.use_fill_caps = False
            # Shade flat.
            for spline in curve.splines:
                spline.use_smooth = False
        else:
            curve.use_fill_caps = True
        return curve, thickness

    @classmethod
    def setup_native_swept_disk_solid_thickness(cls, obj: bpy.types.Object, thickness: Union[float, None]) -> None:
        if not thickness:
            return
        modifier = obj.modifiers.new("Curve Thickness", type="SOLIDIFY")
        assert isinstance(modifier, bpy.types.SolidifyModifier)
        modifier.thickness = thickness
