# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
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
import ifcopenshell
import blenderbim.core.tool
import blenderbim.tool as tool
from test.bim.bootstrap import NewFile
from blenderbim.tool.loader import Loader as subject
import numpy as np


class TestImplementsTool(NewFile):
    def test_run(self):
        assert isinstance(subject(), blenderbim.core.tool.Loader)


class TestCreatingStyles(NewFile):
    def test_create_surface_style_with_textures(self):
        # this case occurs when we edit shader properties without saving them to IFC
        bpy.ops.bim.create_project()

        bpy.ops.mesh.primitive_cube_add(size=10, location=(0, 0, 4))
        obj = bpy.data.objects["Cube"]
        bpy.ops.bim.assign_class(ifc_class="IfcActuator", predefined_type="ELECTRICACTUATOR", userdefined_type="")
        material = bpy.data.materials.new(name="Material")
        obj.data.materials.append(None)  # new slot
        obj.material_slots[0].material = material
        bpy.ops.bim.add_style()

        style_data = {
            "ReflectanceMethod": "NOTDEFINED",
            "DiffuseColour": ("IfcColourRgb", (0.5, 0.5, 0.5, 1.0)),
            "SurfaceColour": (0.3, 0.3, 0.3, 1.0),
            "Transparency": 0.3,
            "SpecularHighlight": 0.4,
            "SpecularColour": 0.03,
        }
        texture_data = [
            {
                "Mode": "DIFFUSE",
                "URLReference": "blenderbim/test/files/image.jpg",
                "type": "IfcImageTexture",
                "uv_mode": "Generated",
            },
        ]

        subject.create_surface_style_rendering(material, style_data)
        subject.create_surface_style_with_textures(material, style_data, texture_data)

        used_node_types = set([n.type for n in material.node_tree.nodes[:]])
        assert used_node_types == set((["OUTPUT_MATERIAL", "BSDF_PRINCIPLED", "TEX_IMAGE", "TEX_COORD"]))

        bsdf = tool.Blender.get_material_node(material, "BSDF_PRINCIPLED")
        alpha = 1 - style_data["Transparency"]
        diffuse_color = style_data["SurfaceColour"][:3] + (alpha,)
        assert np.allclose(material.diffuse_color[:], diffuse_color)
        assert np.allclose(bsdf.inputs["Base Color"].default_value[:], style_data["DiffuseColour"][1])
        assert np.isclose(bsdf.inputs["Alpha"].default_value, alpha)
        assert np.isclose(bsdf.inputs["Roughness"].default_value, style_data["SpecularHighlight"])
        assert np.isclose(bsdf.inputs["Metallic"].default_value, style_data["SpecularColour"])

        image_node = tool.Blender.get_material_node(material, "TEX_IMAGE")
        assert image_node.outputs["Color"].links[0].to_socket.name == "Base Color"
        assert image_node.inputs["Vector"].links[0].from_socket.name == "Generated"
