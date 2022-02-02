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
    def __init__(self, file, **settings):
        # TODO: This usecase currently depends on Blender's data model
        self.file = file
        # Textures is assumed to be a dictionary of texture maps.
        # The key is the texture map name, and the value is the last texture manipulation in the graph.
        self.settings = {"textures": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        self.textures = []
        for texture, node in self.settings["textures"].items():
            parameters = self.get_default_parameters(texture)
            self.traverse_node(node, parameters)
        return list(reversed(self.textures))

    def get_default_parameters(self, texture):
        return {"mode": "REPLACE", "source": "", "function": "", "rgb": "1 1 1", "alpha": "1", "texture": texture}

    def traverse_node(self, node, parameters):
        if node.type == "MIX_RGB":
            if node.blend_type == "MIX":
                parameters["mode"] = "REPLACE"
            elif node.blend_type == "ADD":
                parameters["mode"] = "ADD"
            elif node.blend_type == "MULTIPLY":
                parameters["mode"] = "MODULATE"

            if not node.inputs["Fac"].links:
                if parameters["mode"] == "REPLACE":
                    parameters["mode"] = "BLEND"
                parameters["mode"] += "FACTORALPHA"
                parameters["alpha"] = str(node.inputs["Fac"].default_value)

            if node.inputs["Color1"].links and node.inputs["Color2"].links:
                self.traverse_node(node.inputs["Color2"].links[0].from_node, parameters)
                self.traverse_node(
                    node.inputs["Color1"].links[0].from_node, self.get_default_parameters(parameters["texture"])
                )
            elif node.inputs["Color1"].links:
                parameters["rgb"] = " ".join(map(str, list(node.inputs["Color2"].default_value)[0:3]))
                parameters["source"] = "FACTOR"
                self.traverse_node(node.inputs["Color1"].links[0].from_node, parameters)
            elif node.inputs["Color2"].links:
                parameters["rgb"] = " ".join(map(str, list(node.inputs["Color1"].default_value)[0:3]))
                parameters["source"] = "FACTOR"
                self.traverse_node(node.inputs["Color2"].links[0].from_node, parameters)
        elif node.type == "VECT_MATH":
            # TODO Handle 2X, 4X, and signed
            pass
        elif node.type == "INVERT":
            parameters["function"] = "COMPLEMENT" if parameters["function"] == "" else ""
        elif node.type == "TEX_IMAGE":
            return self.create_surface_texture(node, parameters)
        else:
            # TODO keep traversing backwards
            pass

    def create_surface_texture(self, node, parameters):
        self.textures.append(
            self.file.create_entity(
                "IfcImageTexture",
                RepeatS=node.extension == "REPEAT",
                RepeatT=node.extension == "REPEAT",
                Mode=parameters["mode"],
                Parameter=[parameters[p] for p in ["source", "function", "rgb", "alpha", "texture"]],
                URLReference=node.image.filepath,
            )
        )
