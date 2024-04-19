# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2023 Dion Moult <dion@thinkmoult.com>
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

import re
import bpy
import bmesh
import ifcopenshell.util.element
import blenderbim.core.tool
import blenderbim.tool as tool
import os
import numpy as np
from mathutils import Vector
from pathlib import Path
from typing import Union


# Progressively we'll refactor loading elements into Blender objects into this
# class. This will break down the monolithic import_ifc module and allow us to
# partially load and unload objects for huge models, partial model editing, and
# supplementary objects (e.g. drawings, structural analysis models, etc).


OBJECT_DATA_TYPE = Union[bpy.types.Mesh, bpy.types.Curve]


class Loader(blenderbim.core.tool.Loader):
    @classmethod
    def create_project_collection(cls, name: str) -> bpy.types.Collection:
        project_obj = tool.Ifc.get_object(tool.Ifc.get().by_type("IfcProject")[0])
        project_collection = project_obj.BIMObjectProperties.collection
        for collection in project_collection.children:
            if collection.name == name:
                return collection
        collection = bpy.data.collections.new(name)
        project_collection.children.link(collection)
        if name == "Types":
            project_layer = bpy.context.view_layer.layer_collection.children.get(project_collection.name)
            if project_layer:
                project_layer.children[collection.name].hide_viewport = True
        return collection

    @classmethod
    def get_mesh_name(cls, geometry) -> str:
        representation_id = geometry.id
        if "-" in representation_id:
            representation_id = int(re.sub(r"\D", "", representation_id.split("-")[0]))
        else:
            representation_id = int(re.sub(r"\D", "", representation_id))
        representation = tool.Ifc.get().by_id(representation_id)
        context_id = representation.ContextOfItems.id() if hasattr(representation, "ContextOfItems") else 0
        return "{}/{}".format(context_id, representation_id)

    @classmethod
    def get_name(cls, element: ifcopenshell.entity_instance) -> str:
        return "{}/{}".format(element.is_a(), getattr(element, "Name", "None"))

    @classmethod
    def link_mesh(cls, shape, mesh: OBJECT_DATA_TYPE) -> None:
        geometry = shape.geometry if hasattr(shape, "geometry") else shape
        if "-" in geometry.id:
            mesh.BIMMeshProperties.ifc_definition_id = int(geometry.id.split("-")[0])
        else:
            # TODO: See #2002
            mesh.BIMMeshProperties.ifc_definition_id = int(geometry.id.replace(",", ""))

    @classmethod
    def create_surface_style_shading(cls, blender_material, surface_style):
        surface_style = cls.surface_style_to_dict(surface_style)
        alpha = 1.0
        # Transparency was added in IFC4
        if transparency := surface_style.get("Transparency", None):
            alpha = 1 - transparency
        blender_material.diffuse_color = surface_style["SurfaceColour"] + (alpha,)
        blender_material.use_nodes = False

    @classmethod
    def restart_material_node_tree(cls, blender_material):
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
    def surface_style_to_dict(cls, surface_style):
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
    def create_surface_style_rendering(cls, blender_material, surface_style):
        surface_style = cls.surface_style_to_dict(surface_style)
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

            def get_image():
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
                    pil_image.save("test_image.png")
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
    def load_indexed_texture_map(cls, coordinates, mesh):
        # Get a BMesh representation
        bm = bmesh.new()
        bm.from_mesh(mesh)
        # constistent naming with how Blender does it
        uv_layer = bm.loops.layers.uv.active or bm.loops.layers.uv.new("UVMap")

        # remap the faceset CoordList index to the vertices in blender mesh
        coordinates_remap = []
        si_conversion = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        faceset = coordinates.MappedTo
        for co in faceset.Coordinates.CoordList:
            co = Vector(co) * si_conversion
            index = next(v.index for v in bm.verts if (v.co - co).length_squared < 1e-5)
            coordinates_remap.append(index)

        # ifc indices start with 1
        remap_verts_to_blender = lambda ifc_verts: [coordinates_remap[i - 1] for i in ifc_verts]

        # faces_remap - ifc faces described using blender verts indices
        # IFC4.3+
        if coordinates.is_a("IfcIndexedPolygonalTextureMap"):
            faces_remap = [
                remap_verts_to_blender(tex_coord_index.TexCoordsOf.CoordIndex)
                for tex_coord_index in coordinates.TexCoordIndices
            ]
            texture_map = [tex_coord_index.TexCoordIndex for tex_coord_index in coordinates.TexCoordIndices]
        else:  # IfcIndexedTriangleTextureMap
            if faceset.is_a("IfcTriangulatedFaceSet"):
                faces_remap = [remap_verts_to_blender(triangle_face) for triangle_face in faceset.CoordIndex]
            else:  # IfcPolygonalFaceSet
                faces_remap = [remap_verts_to_blender(triangle_face.CoordIndex) for triangle_face in faceset.Faces]
            texture_map = coordinates.TexCoordIndex

        # apply uv to each face
        for bface in bm.faces:
            face = [loop.vert.index for loop in bface.loops]
            # find the corresponding TexCoordIndex by matching ifc faceset with blender face
            # remap TexCoordIndex as the loop start may different from blender face
            texCoordIndex = next(
                [tex_coord_index[face_remap.index(i)] for i in face]
                for tex_coord_index, face_remap in zip(texture_map, faces_remap, strict=True)
                if all(i in face_remap for i in face)
            )
            # apply uv to each loop
            for loop, i in zip(bface.loops, texCoordIndex):
                loop[uv_layer].uv = coordinates.TexCoords.TexCoordsList[i - 1]

        # Finish up, write the bmesh back to the mesh
        bm.to_mesh(mesh)
        bm.free()
