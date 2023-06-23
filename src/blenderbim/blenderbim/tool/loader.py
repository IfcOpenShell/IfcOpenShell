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
import ifcopenshell.util.element
import blenderbim.core.tool
import blenderbim.tool as tool
import os
from mathutils import Vector


# Progressively we'll refactor loading elements into Blender objects into this
# class. This will break down the monolithic import_ifc module and allow us to
# partially load and unload objects for huge models, partial model editing, and
# supplementary objects (e.g. drawings, structural analysis models, etc).


class Loader(blenderbim.core.tool.Loader):
    @classmethod
    def get_mesh_name(cls, geometry):
        representation_id = geometry.id
        if "-" in representation_id:
            representation_id = int(re.sub(r"\D", "", representation_id.split("-")[0]))
        else:
            representation_id = int(re.sub(r"\D", "", representation_id))
        representation = tool.Ifc.get().by_id(representation_id)
        context_id = representation.ContextOfItems.id() if hasattr(representation, "ContextOfItems") else 0
        return "{}/{}".format(context_id, representation_id)

    @classmethod
    def get_name(cls, element):
        return "{}/{}".format(element.is_a(), element.Name)

    @classmethod
    def link_mesh(cls, shape, mesh):
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
        blender_material.diffuse_color = surface_style["SurfaceColour"][:3] + (alpha,)

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
        color_to_tuple = lambda x: (x.Red, x.Green, x.Blue, 1)

        if surface_style["SurfaceColour"]:
            surface_style["SurfaceColour"] = color_to_tuple(surface_style["SurfaceColour"])

        if surface_style["DiffuseColour"] and surface_style["DiffuseColour"].is_a("IfcColourRgb"):
            surface_style["DiffuseColour"] = ("IfcColourRgb", color_to_tuple(surface_style["DiffuseColour"]))

        elif surface_style["DiffuseColour"] and surface_style["DiffuseColour"].is_a("IfcNormalisedRatioMeasure"):
            diffuse_color_value = surface_style["DiffuseColour"].wrappedValue
            diffuse_color = [v * diffuse_color_value for v in surface_style["SurfaceColor"][:3]] + [1]
            surface_style["DiffuseColour"] = ("IfcNormalisedRatioMeasure", diffuse_color)
        else:
            surface_style["DiffuseColour"] = None

        if surface_style["SpecularColour"] and surface_style["SpecularColour"].is_a("IfcNormalisedRatioMeasure"):
            surface_style["SpecularColour"] = surface_style["SpecularColour"].wrappedValue
        else:
            surface_style["SpecularColour"] = None

        if surface_style["SpecularHighlight"] and surface_style["SpecularHighlight"].is_a("IfcSpecularRoughness"):
            surface_style["SpecularHighlight"] = surface_style["SpecularHighlight"].wrappedValue
        else:
            surface_style["SpecularHighlight"] = None
        return surface_style

    @classmethod
    def create_surface_style_rendering(cls, blender_material, surface_style):
        surface_style = cls.surface_style_to_dict(surface_style)
        cls.create_surface_style_shading(blender_material, surface_style)

        reflectance_method = surface_style["ReflectanceMethod"]
        if reflectance_method not in ("PHYSICAL", "NOTDEFINED", "FLAT"):
            print(f'WARNING. Unsupported reflectance method "{reflectance_method}" on style {surface_style}')
            return

        if reflectance_method in ["PHYSICAL", "NOTDEFINED"]:
            blender_material.use_nodes = True
            cls.restart_material_node_tree(blender_material)
            bsdf = tool.Blender.get_material_node(blender_material, "BSDF_PRINCIPLED")
            if surface_style["DiffuseColour"]:
                color_type, color_value = surface_style["DiffuseColour"]
                if color_type == "IfcColourRgb":
                    bsdf.inputs["Base Color"].default_value = color_value
                elif color_type == "IfcNormalisedRatioMeasure":
                    bsdf.inputs["Base Color"].default_value = color_value
            if surface_style["SpecularColour"]:
                bsdf.inputs["Metallic"].default_value = surface_style["SpecularColour"]
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
                    rgb.outputs[0].default_value = color_value

    @classmethod
    def create_surface_style_with_textures(cls, blender_material, rendering_style, texture_style):
        for texture in texture_style.Textures:
            mode = getattr(texture, "Mode", None)
            node = None

            if texture.is_a("IfcImageTexture"):
                image_url = texture.URLReference
                if not os.path.abspath(texture.URLReference) and tool.Ifc.get_path():
                    image_url = os.path.join(os.path.dirname(tool.Ifc.get_path()), texture.URLReference)

            reflectance_method = rendering_style.ReflectanceMethod
            if reflectance_method not in ("PHYSICAL", "NOTDEFINED", "FLAT"):
                print(f'WARNING. Unsupported reflectance method "{reflectance_method}" on style {rendering_style}')
                return

            if rendering_style.ReflectanceMethod in ["PHYSICAL", "NOTDEFINED"]:
                bsdf = tool.Blender.get_material_node(blender_material, "BSDF_PRINCIPLED")
                if mode == "NORMAL":
                    # add normal map node
                    normalmap = blender_material.node_tree.nodes.new(type="ShaderNodeNormalMap")
                    normalmap.location = bsdf.location - Vector((200, 0))
                    blender_material.node_tree.links.new(normalmap.outputs[0], bsdf.inputs["Normal"])

                    # add normal map sampler
                    node = blender_material.node_tree.nodes.new(type="ShaderNodeTexImage")
                    node.location = normalmap.location - Vector((200, 0))
                    image = bpy.data.images.load(image_url)
                    image.colorspace_settings.name = "Non-Color"
                    node.image = image
                    blender_material.node_tree.links.new(node.outputs[0], normalmap.inputs["Color"])

                elif mode == "EMISSIVE":
                    output = tool.Blender.get_material_node(blender_material, "OUTPUT_MATERIAL")

                    # add "Add Shader" node
                    add = blender_material.node_tree.nodes.new(type="ShaderNodeAddShader")
                    add.location = bsdf.location + Vector((200, 0))
                    blender_material.node_tree.links.new(bsdf.outputs[0], add.inputs[1])
                    blender_material.node_tree.links.new(add.outputs[0], output.inputs[0])

                    # add emssion shader node
                    emission = blender_material.node_tree.nodes.new(type="ShaderNodeEmission")
                    emission.location = add.location - Vector((200, 0))
                    blender_material.node_tree.links.new(emission.outputs[0], add.inputs[0])

                    # add emission texture sampler
                    node = blender_material.node_tree.nodes.new(type="ShaderNodeTexImage")
                    node.location = emission.location - Vector((200, 0))
                    image = bpy.data.images.load(image_url)
                    node.image = image
                    blender_material.node_tree.links.new(node.outputs[0], emission.inputs[0])

                elif mode == "METALLICROUGHNESS":
                    separate = blender_material.node_tree.nodes.new(type="ShaderNodeSeparateRGB")
                    separate.location = bsdf.location - Vector((200, 0))
                    blender_material.node_tree.links.new(separate.outputs[1], bsdf.inputs["Roughness"])
                    blender_material.node_tree.links.new(separate.outputs[2], bsdf.inputs["Metallic"])

                    node = blender_material.node_tree.nodes.new(type="ShaderNodeTexImage")
                    node.location = separate.location - Vector((200, 0))
                    image = bpy.data.images.load(image_url)
                    image.colorspace_settings.name = "Non-Color"
                    node.image = image
                    blender_material.node_tree.links.new(node.outputs[0], separate.inputs[0])

                elif mode == "OCCLUSION":
                    # TODO work out how to implement glTF settings here
                    # https://docs.blender.org/manual/en/dev/addons/import_export/scene_gltf2.html
                    pass

                elif mode == "DIFFUSE":
                    node = blender_material.node_tree.nodes.new(type="ShaderNodeTexImage")
                    node.location = bsdf.location - Vector((400, 0))
                    image = bpy.data.images.load(image_url)
                    node.image = image
                    blender_material.node_tree.links.new(node.outputs[0], bsdf.inputs["Base Color"])
                    blender_material.node_tree.links.new(node.outputs[1], bsdf.inputs["Alpha"])
                    blender_material.blend_method = "BLEND"

            elif rendering_style.ReflectanceMethod == "FLAT":
                bsdf = tool.Blender.get_material_node(blender_material, "MIX_SHADER")
                if mode != "EMISSIVE":
                    continue

                node = blender_material.node_tree.nodes.new(type="ShaderNodeTexImage")
                node.location = bsdf.location - Vector((200, 0))
                image = bpy.data.images.load(image_url)
                # TODO: orphaned textures after shader recreated?
                node.image = image
                blender_material.node_tree.links.new(node.outputs[0], bsdf.inputs[2])

            if node and getattr(texture, "IsMappedBy", None):
                coordinates = texture.IsMappedBy[0]
                coord = blender_material.node_tree.nodes.new(type="ShaderNodeTexCoord")
                coord.location = node.location - Vector((200, 0))
                if coordinates.is_a("IfcTextureCoordinateGenerator") and coordinates.Mode == "COORD":
                    blender_material.node_tree.links.new(coord.outputs["Generated"], node.inputs["Vector"])
                elif coordinates.is_a("IfcTextureCoordinateGenerator") and coordinates.Mode == "COORD-EYE":
                    blender_material.node_tree.links.new(coord.outputs["Camera"], node.inputs["Vector"])
                else:
                    blender_material.node_tree.links.new(coord.outputs["UV"], node.inputs["Vector"])
