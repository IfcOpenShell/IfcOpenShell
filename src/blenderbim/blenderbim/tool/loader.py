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
import mathutils


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
        alpha = 1.0
        # Transparency was added in IFC4
        if hasattr(surface_style, "Transparency") and surface_style.Transparency:
            alpha = 1 - surface_style.Transparency
        blender_material.diffuse_color = (
            surface_style.SurfaceColour.Red,
            surface_style.SurfaceColour.Green,
            surface_style.SurfaceColour.Blue,
            alpha,
        )

    @classmethod
    def restart_material_node_tree(cls, blender_material):
        nodes = blender_material.node_tree.nodes
        links = blender_material.node_tree.links
        for n in nodes[:]:
            nodes.remove(n)
        output = nodes.new("ShaderNodeOutputMaterial")
        bsdf = nodes.new("ShaderNodeBsdfPrincipled")
        links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])

    @classmethod
    def create_surface_style_rendering(cls, blender_material, surface_style):
        cls.create_surface_style_shading(blender_material, surface_style)
        if surface_style.ReflectanceMethod in ["PHYSICAL", "NOTDEFINED"]:
            blender_material.use_nodes = True
            cls.restart_material_node_tree(blender_material)
            bsdf = blender_material.node_tree.nodes["Principled BSDF"]
            if surface_style.DiffuseColour:
                if surface_style.DiffuseColour.is_a("IfcColourRgb"):
                    bsdf.inputs["Base Color"].default_value = (
                        surface_style.DiffuseColour.Red,
                        surface_style.DiffuseColour.Green,
                        surface_style.DiffuseColour.Blue,
                        1,
                    )
                elif surface_style.DiffuseColour.is_a("IfcNormalisedRatioMeasure"):
                    bsdf.inputs["Base Color"].default_value = (
                        surface_style.SurfaceColour.Red * surface_style.DiffuseColour.wrappedValue,
                        surface_style.SurfaceColour.Green * surface_style.DiffuseColour.wrappedValue,
                        surface_style.SurfaceColour.Blue * surface_style.DiffuseColour.wrappedValue,
                        1,
                    )
            if surface_style.SpecularColour and surface_style.SpecularColour.is_a("IfcNormalisedRatioMeasure"):
                bsdf.inputs["Metallic"].default_value = surface_style.SpecularColour.wrappedValue
            if surface_style.SpecularHighlight and surface_style.SpecularHighlight.is_a("IfcSpecularRoughness"):
                bsdf.inputs["Roughness"].default_value = surface_style.SpecularHighlight.wrappedValue
            if hasattr(surface_style, "Transparency") and surface_style.Transparency:
                bsdf.inputs["Alpha"].default_value = 1 - surface_style.Transparency
                blender_material.blend_method = "BLEND"

        elif surface_style.ReflectanceMethod == "FLAT":
            blender_material.use_nodes = True
            cls.restart_material_node_tree(blender_material)

            output = {n.type: n for n in blender_material.node_tree.nodes}.get("OUTPUT_MATERIAL", None)
            bsdf = blender_material.node_tree.nodes["Principled BSDF"]

            mix = blender_material.node_tree.nodes.new(type="ShaderNodeMixShader")
            mix.location = bsdf.location
            blender_material.node_tree.links.new(mix.outputs[0], output.inputs["Surface"])

            blender_material.node_tree.nodes.remove(bsdf)

            lightpath = blender_material.node_tree.nodes.new(type="ShaderNodeLightPath")
            lightpath.location = mix.location - mathutils.Vector((200, -200))
            blender_material.node_tree.links.new(lightpath.outputs[0], mix.inputs[0])

            bsdf = blender_material.node_tree.nodes.new(type="ShaderNodeBsdfTransparent")
            bsdf.location = mix.location - mathutils.Vector((200, 0))
            blender_material.node_tree.links.new(bsdf.outputs[0], mix.inputs[1])

            rgb = blender_material.node_tree.nodes.new(type="ShaderNodeRGB")
            rgb.location = mix.location - mathutils.Vector((200, 200))
            blender_material.node_tree.links.new(rgb.outputs[0], mix.inputs[2])

            if surface_style.DiffuseColour and surface_style.DiffuseColour.is_a("IfcColourRgb"):
                rgb.outputs[0].default_value = (
                    surface_style.DiffuseColour.Red,
                    surface_style.DiffuseColour.Green,
                    surface_style.DiffuseColour.Blue,
                    1,
                )

    @classmethod
    def create_surface_style_with_textures(cls, blender_material, rendering_style, texture_style):
        for texture in texture_style.Textures:
            mode = getattr(texture, "Mode", None)
            node = None

            if texture.is_a("IfcImageTexture"):
                image_url = texture.URLReference
                if not os.path.abspath(texture.URLReference) and tool.Ifc.get_path():
                    image_url = os.path.join(os.path.dirname(tool.Ifc.get_path()), texture.URLReference)

            if rendering_style.ReflectanceMethod in ["PHYSICAL", "NOTDEFINED"]:
                bsdf = blender_material.node_tree.nodes["Principled BSDF"]
                if mode == "NORMAL":
                    normalmap = blender_material.node_tree.nodes.new(type="ShaderNodeNormalMap")
                    normalmap.location = bsdf.location - mathutils.Vector((200, 0))
                    blender_material.node_tree.links.new(normalmap.outputs[0], bsdf.inputs["Normal"])

                    node = blender_material.node_tree.nodes.new(type="ShaderNodeTexImage")
                    node.location = normalmap.location - mathutils.Vector((200, 0))
                    image = bpy.data.images.load(image_url)
                    image.colorspace_settings.name = "Non-Color"
                    node.image = image
                    blender_material.node_tree.links.new(node.outputs[0], normalmap.inputs["Color"])
                elif mode == "EMISSIVE":
                    output = {n.type: n for n in blender_material.node_tree.nodes}.get("OUTPUT_MATERIAL", None)

                    add = blender_material.node_tree.nodes.new(type="ShaderNodeAddShader")
                    add.location = bsdf.location + mathutils.Vector((200, 0))
                    blender_material.node_tree.links.new(bsdf.outputs[0], add.inputs[1])
                    blender_material.node_tree.links.new(add.outputs[0], output.inputs[0])

                    emission = blender_material.node_tree.nodes.new(type="ShaderNodeEmission")
                    emission.location = add.location - mathutils.Vector((200, 0))
                    blender_material.node_tree.links.new(emission.outputs[0], add.inputs[0])

                    node = blender_material.node_tree.nodes.new(type="ShaderNodeTexImage")
                    node.location = emission.location - mathutils.Vector((200, 0))
                    image = bpy.data.images.load(image_url)
                    node.image = image
                    blender_material.node_tree.links.new(node.outputs[0], emission.inputs[0])
                elif mode == "METALLICROUGHNESS":
                    separate = blender_material.node_tree.nodes.new(type="ShaderNodeSeparateRGB")
                    separate.location = bsdf.location - mathutils.Vector((200, 0))
                    blender_material.node_tree.links.new(separate.outputs[1], bsdf.inputs["Roughness"])
                    blender_material.node_tree.links.new(separate.outputs[2], bsdf.inputs["Metallic"])

                    node = blender_material.node_tree.nodes.new(type="ShaderNodeTexImage")
                    node.location = separate.location - mathutils.Vector((200, 0))
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
                    node.location = bsdf.location - mathutils.Vector((400, 0))
                    image = bpy.data.images.load(image_url)
                    node.image = image
                    blender_material.node_tree.links.new(node.outputs[0], bsdf.inputs["Base Color"])
                    blender_material.node_tree.links.new(node.outputs[1], bsdf.inputs["Alpha"])
                    blender_material.blend_method = "BLEND"
            elif rendering_style.ReflectanceMethod == "FLAT":
                bsdf = blender_material.node_tree.nodes["Mix Shader"]
                if mode == "EMISSIVE":
                    node = blender_material.node_tree.nodes.new(type="ShaderNodeTexImage")
                    node.location = bsdf.location - mathutils.Vector((200, 0))
                    image = bpy.data.images.load(image_url)
                    node.image = image
                    blender_material.node_tree.links.new(node.outputs[0], bsdf.inputs[2])

            if node and getattr(texture, "IsMappedBy", None):
                coordinates = texture.IsMappedBy[0]
                coord = blender_material.node_tree.nodes.new(type="ShaderNodeTexCoord")
                coord.location = node.location - mathutils.Vector((200, 0))
                if coordinates.is_a("IfcTextureCoordinateGenerator") and coordinates.Mode == "COORD":
                    blender_material.node_tree.links.new(coord.outputs["Generated"], node.inputs["Vector"])
                elif coordinates.is_a("IfcTextureCoordinateGenerator") and coordinates.Mode == "COORD-EYE":
                    blender_material.node_tree.links.new(coord.outputs["Camera"], node.inputs["Vector"])
                else:
                    blender_material.node_tree.links.new(coord.outputs["UV"], node.inputs["Vector"])
