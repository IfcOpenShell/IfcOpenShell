# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
#
# This file is part of IfcOpenShell.
#
# IfcOpenShell is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcOpenShell is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcOpenShell.  If not, see <http://www.gnu.org/licenses/>.

import ifcopenshell
import ifcopenshell.api


class Usecase:
    def __init__(self, file, material=None, uv_maps=None):
        """Add a surface texture based on a Blender material definition

        Warning: this API can only be used with Blender data structures.

        :param material: The Blender material definition with a node tree that
            is compatible with glTF. See one of the valid combinations here:
            https://docs.blender.org/manual/en/dev/addons/import_export/scene_gltf2.html
        :type material: bpy.types.Material
        :param uv_maps: A list of IfcIndexedTextureMap for any
            IfcTessellatedFaceSets that the representation has, obtained from
            the HasTextures attribute.
        :type uv_maps: list[ifcopenshell.entity_instance.entity_instance]
        :return: A list of IfcImageTexture
        :rtype: list[ifcopenshell.entity_instance.entity_instance]
        """
        # TODO: This usecase currently depends on Blender's data model
        self.file = file
        self.settings = {"material": material, "uv_maps": uv_maps or []}

    def execute(self):
        if self.file.schema == "IFC2X3":
            # TODO: research how compatible IFC2X3 and IFC4 textures are
            return []

        # We optimistically assume the user has specified one of these valid combinations
        # https://docs.blender.org/manual/en/dev/addons/import_export/scene_gltf2.html
        # glTF, X3D, and IFC are compatible. As long as they have something that
        # loosely resembles the node tree, we treat it as valid.
        self.textures = []
        output = {n.type: n for n in self.settings["material"].node_tree.nodes}.get("OUTPUT_MATERIAL", None)

        if not output:
            return self.textures

        bsdf = output.inputs["Surface"].links[0].from_node

        if bsdf.type == "ADD_SHADER":
            for socket in bsdf.inputs:
                if socket.links and socket.links[0].from_node.type == "BSDF_PRINCIPLED":
                    bsdf = socket.links[0].from_node
                    break

        if bsdf.type == "MIX_SHADER":
            self.detect_unlit_emissive_map(bsdf)
        elif bsdf.type == "BSDF_PRINCIPLED":
            self.detect_normal_map(bsdf)
            self.detect_emissive_map(bsdf)
            self.detect_metallicroughness_map(bsdf)
            self.detect_occlusion_map()
            self.detect_diffuse_map(bsdf)
        # We do not support Phong shading. What year is this, 1995?
        return self.textures

    def detect_unlit_emissive_map(self, bsdf):
        for socket in bsdf.inputs:
            if socket.links and socket.links[0].from_node.type == "TEX_IMAGE":
                return self.create_surface_texture(socket.links[0].from_node, "EMISSIVE")

    def detect_normal_map(self, bsdf):
        if bsdf.inputs["Normal"].links and bsdf.inputs["Normal"].links[0].from_node.type == "NORMAL_MAP":
            normal = bsdf.inputs["Normal"].links[0].from_node
            if normal.inputs["Color"].links and normal.inputs["Color"].links[0].from_node.type == "TEX_IMAGE":
                return self.create_surface_texture(normal.inputs["Color"].links[0].from_node, "NORMAL")

    def detect_emissive_map(self, bsdf):
        if bsdf.outputs[0].links[0].to_node.type != "ADD_SHADER":
            return
        bsdf = bsdf.outputs[0].links[0].to_node
        for socket in bsdf.inputs:
            if socket.links and socket.links[0].from_node.type == "EMISSION":
                bsdf = socket.links[0].from_node
                if bsdf.inputs["Color"].links and bsdf.inputs["Color"].links[0].from_node.type == "TEX_IMAGE":
                    return self.create_surface_texture(bsdf.inputs["Color"].links[0].from_node, "EMISSIVE")

    def detect_metallicroughness_map(self, bsdf):
        if bsdf.inputs["Metallic"].links and bsdf.inputs["Metallic"].links[0].from_node.type == "SEPRGB":
            seprgb = bsdf.inputs["Metallic"].links[0].from_node
            if seprgb.inputs["Image"].links and seprgb.inputs["Image"].links[0].from_node.type == "TEX_IMAGE":
                return self.create_surface_texture(seprgb.inputs["Image"].links[0].from_node, "METALLICROUGHNESS")
        if bsdf.inputs["Roughness"].links and bsdf.inputs["Roughness"].links[0].from_node.type == "SEPRGB":
            seprgb = bsdf.inputs["Roughness"].links[0].from_node
            if seprgb.inputs["Image"].links and seprgb.inputs["Image"].links[0].from_node.type == "TEX_IMAGE":
                return self.create_surface_texture(seprgb.inputs["Image"].links[0].from_node, "METALLICROUGHNESS")

    def detect_occlusion_map(self):
        for node in self.settings["material"].node_tree.nodes:
            if (
                node.type != "GROUP"
                or not node.node_tree
                or node.node_tree.name != "glTF Material Output"
                or not node.inputs
                or not node.inputs[0].links
            ):
                continue
            from_node = node.inputs[0].links[0].from_node
            if from_node.type == "SEPRGB":
                sep = from_node
                if sep.inputs["Image"].links and sep.inputs["Image"].links[0].from_node.type == "TEX_IMAGE":
                    return self.create_surface_texture(sep.inputs["Image"].links[0].from_node, "OCCLUSION")
            elif from_node.type == "TEX_IMAGE":
                return self.create_surface_texture(from_node, "OCCLUSION")

    def detect_diffuse_map(self, bsdf):
        links = bsdf.inputs["Base Color"].links
        if links and links[0].from_node.type == "TEX_IMAGE":
            return self.create_surface_texture(links[0].from_node, "DIFFUSE")

    def create_surface_texture(self, node, mode):
        import blenderbim.tool as tool

        texture = self.file.create_entity(
            "IfcImageTexture",
            RepeatS=node.extension == "REPEAT",
            RepeatT=node.extension == "REPEAT",
            Mode=mode,
            URLReference=tool.Blender.blender_path_to_posix(node.image.filepath),
        )
        self.textures.append(texture)
        self.process_texture_coordinates(node, texture)

    def process_texture_coordinates(self, node, texture):
        if node.inputs["Vector"].links and node.inputs["Vector"].links[0].from_node.type == "TEX_COORD":
            if node.inputs["Vector"].links[0].from_socket.name == "UV":
                self.apply_uv_map_to_texture(texture)
            elif node.inputs["Vector"].links[0].from_socket.name == "Generated":
                self.file.create_entity("IfcTextureCoordinateGenerator", Maps=[texture], Mode="COORD")
            elif node.inputs["Vector"].links[0].from_socket.name == "Camera":
                self.file.create_entity("IfcTextureCoordinateGenerator", Maps=[texture], Mode="COORD-EYE")
        elif node.inputs["Vector"].links and node.inputs["Vector"].links[0].from_node.type == "UVMAP":
            self.apply_uv_map_to_texture(texture)

    def apply_uv_map_to_texture(self, texture):
        for uv_map in self.settings["uv_maps"]:
            maps = set(uv_map.Maps or [])
            maps.add(texture)
            uv_map.Maps = list(maps)
