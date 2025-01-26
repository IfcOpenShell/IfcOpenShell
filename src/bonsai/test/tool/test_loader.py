# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
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

import bpy
import bmesh
import ifcopenshell
import ifcopenshell.util.schema
import bonsai.core.tool
import bonsai.tool as tool
from test.bim.bootstrap import NewFile
from bonsai.tool.loader import Loader as subject
import numpy as np
from ifcopenshell.util.shape_builder import ShapeBuilder
from mathutils import Vector
from pathlib import Path


class TestImplementsTool(NewFile):
    def test_run(self):
        assert isinstance(subject(), bonsai.core.tool.Loader)


class TestCreatingStyles(NewFile):
    def test_create_surface_style_with_textures_from_data(self):
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
            "DiffuseColour": ("IfcColourRgb", (0.5, 0.5, 0.5)),
            "SurfaceColour": (0.3, 0.3, 0.3),
            "Transparency": 0.3,
            "SpecularHighlight": 0.4,
            "SpecularColour": ("IfcNormalisedRatioMeasure", 0.03),
        }
        texture_data = [
            {
                "Mode": "DIFFUSE",
                "URLReference": "bonsai/test/files/image.jpg",
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
        diffuse_color = style_data["SurfaceColour"] + (alpha,)
        assert np.allclose(material.diffuse_color[:], diffuse_color)
        base_color = style_data["DiffuseColour"][1] + (1.0,)
        assert np.allclose(bsdf.inputs["Base Color"].default_value[:], base_color)
        assert np.isclose(bsdf.inputs["Alpha"].default_value, alpha)
        assert np.isclose(bsdf.inputs["Roughness"].default_value, style_data["SpecularHighlight"])
        assert np.isclose(bsdf.inputs["Metallic"].default_value, style_data["SpecularColour"][1])

        image_node = tool.Blender.get_material_node(material, "TEX_IMAGE")
        assert image_node.outputs["Color"].links[0].to_socket.name == "Base Color"
        assert image_node.inputs["Vector"].links[0].from_socket.name == "Generated"

        original_path = Path(tool.Ifc.get_path()).parent / Path(texture_data[0]["URLReference"])
        loaded_filepath = Path(image_node.image.filepath)
        assert original_path == loaded_filepath

    def test_create_surface_style_with_textures_from_ifc(self):
        # this case occurs when we edit shader properties without saving them to IFC
        bpy.ops.bim.create_project()

        style = tool.Ifc.run("style.add_style", name="test")
        material = bpy.data.materials.new(style.Name)
        tool.Ifc.link(style, material)
        get_color = lambda value: {color: value for color in ("Red", "Green", "Blue")}
        rendering_attributes = {
            "ReflectanceMethod": "NOTDEFINED",
            "DiffuseColour": get_color(0.5),
            "SurfaceColour": get_color(0.3),
            "Transparency": 0.3,
            "SpecularHighlight": {"IfcSpecularRoughness": 0.4},
            "SpecularColour": 0.03,
        }
        rendering_style = tool.Ifc.run(
            "style.add_surface_style",
            style=style,
            ifc_class="IfcSurfaceStyleRendering",
            attributes=rendering_attributes,
        )

        textures = [
            {
                "URLReference": "bonsai/test/files/image.jpg",
                "Mode": "DIFFUSE",
                "RepeatS": True,
                "RepeatT": True,
                "uv_mode": "Generated",
            }
        ]
        textures = tool.Ifc.run("style.add_surface_textures", textures=textures, uv_maps=[])
        texture_style = tool.Ifc.run(
            "style.add_surface_style",
            style=style,
            ifc_class="IfcSurfaceStyleWithTextures",
            attributes={"Textures": textures},
        )

        subject.create_surface_style_rendering(material, rendering_style)
        subject.create_surface_style_with_textures(material, rendering_style, texture_style)

        used_node_types = set([n.type for n in material.node_tree.nodes[:]])
        assert used_node_types == set((["OUTPUT_MATERIAL", "BSDF_PRINCIPLED", "TEX_IMAGE", "TEX_COORD"]))

        color_to_tuple = lambda x: (x.Red, x.Green, x.Blue)
        bsdf = tool.Blender.get_material_node(material, "BSDF_PRINCIPLED")
        alpha = 1 - rendering_style.Transparency
        diffuse_color = color_to_tuple(rendering_style.SurfaceColour) + (alpha,)
        assert np.allclose(material.diffuse_color[:], diffuse_color)
        base_color = color_to_tuple(rendering_style.DiffuseColour) + (1.0,)
        assert np.allclose(bsdf.inputs["Base Color"].default_value[:], base_color)
        assert np.isclose(bsdf.inputs["Alpha"].default_value, alpha)
        assert np.isclose(bsdf.inputs["Roughness"].default_value, rendering_style.SpecularHighlight.wrappedValue)
        assert np.isclose(bsdf.inputs["Metallic"].default_value, rendering_style.SpecularColour.wrappedValue)

        image_node = tool.Blender.get_material_node(material, "TEX_IMAGE")
        assert image_node.outputs["Color"].links[0].to_socket.name == "Base Color"
        assert image_node.inputs["Vector"].links[0].from_socket.name == "Generated"
        original_path = Path(tool.Ifc.get_path()).parent / Path(textures[0].URLReference)
        loaded_filepath = Path(image_node.image.filepath)
        assert original_path == loaded_filepath

    def test_create_surface_style_with_textures_from_ifc_blob_image(self):
        # this case occurs when we edit shader properties without saving them to IFC
        bpy.ops.bim.create_project()

        ifc_file = tool.Ifc.get()
        style = tool.Ifc.run("style.add_style", name="test")
        material = bpy.data.materials.new(style.Name)
        tool.Ifc.link(style, material)
        get_color = lambda value: {color: value for color in ("Red", "Green", "Blue")}
        rendering_attributes = {
            "ReflectanceMethod": "NOTDEFINED",
            "DiffuseColour": get_color(0.5),
            "SurfaceColour": get_color(0.3),
            "Transparency": 0.3,
            "SpecularHighlight": {"IfcSpecularRoughness": 0.4},
            "SpecularColour": 0.03,
        }
        rendering_style = tool.Ifc.run(
            "style.add_surface_style",
            style=style,
            ifc_class="IfcSurfaceStyleRendering",
            attributes=rendering_attributes,
        )

        def get_png_raster_code():
            import base64
            import zlib
            import struct

            # https://blender.stackexchange.com/questions/62072/does-blender-have-a-method-to-a-get-png-formatted-bytearray-for-an-image-via-pyt
            width = 2
            height = 2
            # 2x2 image:
            # R G
            # B W
            # fmt: off
            pixels = (
                1,0,0,1,
                0,1,0,1,
                0,0,1,1,
                1,1,1,1,
            )
            # fmt: on
            buf = bytearray([int(p * 255) for p in pixels])

            # add null bytes at the start
            width_byte_4 = width * 4
            raw_data = b"".join(
                b"\x00" + buf[span : span + width_byte_4] for span in range(0, height * width_byte_4, width_byte_4)
            )

            def png_pack(png_tag, data):
                header = png_tag + data
                chunk = struct.pack("!I", len(data))
                chunk += header
                chunk += struct.pack("!I", 0xFFFFFFFF & zlib.crc32(header))
                return chunk

            png_bytes = b"".join(
                [
                    b"\x89PNG\r\n\x1a\n",
                    png_pack(b"IHDR", struct.pack("!2I5B", width, height, 8, 6, 0, 0, 0)),
                    png_pack(b"IDAT", zlib.compress(raw_data, 9)),
                    png_pack(b"IEND", b""),
                ]
            )

            raster_code = "".join(["{:08b}".format(x) for x in png_bytes])
            return raster_code

        texture_data = {
            "RasterCode": get_png_raster_code(),
            "RasterFormat": "PNG",
            "Mode": "DIFFUSE",
            "RepeatS": True,
            "RepeatT": True,
        }
        # setup texture manually as `style.add_surface_textures` doesn't support non-IfcImageTexture textures
        textures = [ifc_file.create_entity("IfcBlobTexture", **texture_data)]
        # setup UV
        ifc_file.create_entity("IfcTextureCoordinateGenerator", Maps=textures, Mode="COORD")

        texture_style = tool.Ifc.run(
            "style.add_surface_style",
            style=style,
            ifc_class="IfcSurfaceStyleWithTextures",
            attributes={"Textures": textures},
        )

        subject.create_surface_style_rendering(material, rendering_style)
        subject.create_surface_style_with_textures(material, rendering_style, texture_style)

        used_node_types = set([n.type for n in material.node_tree.nodes[:]])
        assert used_node_types == set((["OUTPUT_MATERIAL", "BSDF_PRINCIPLED", "TEX_IMAGE", "TEX_COORD"]))

        image_node = tool.Blender.get_material_node(material, "TEX_IMAGE")
        assert image_node.outputs["Color"].links[0].to_socket.name == "Base Color"
        assert image_node.inputs["Vector"].links[0].from_socket.name == "Generated"
        assert image_node.image.filepath == ""
        # fmt: off
        # blender has reversed pixels rows order
        assert image_node.image.pixels[:] == (0.0, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0)
        # fmt: on

    def test_create_surface_style_with_textures_from_ifc_pixel_image(self):
        # fmt: off
        # blender has reversed pixels rows order
        # 2x2 image:
        # R G
        # B W
        ifc_pixel_data = {
            1: (
                0.7,
                1.0,
                0.5,
                0.6,
            ),
            2: (
                0.7, 0.5,
                1.0, 0.5,
                0.5, 0.5,
                0.6, 0.5
            ),
            3: (
                0,   0,   0.7,
                1,   1,   1,
                0.5, 0,   0,
                0,   0.6, 0,
            ),
            4: (
                0,   0,   0.7, 0.5,
                1,   1,   1,   0.5,
                0.5, 0,   0,   0.5,
                0,   0.6, 0,   0.5,
            )
        }
        expected_pixel_data = {
            1: (
                0.7, 0.7, 0.7, 1.0,
                1.0, 1.0, 1.0, 1.0,
                0.5, 0.5, 0.5, 1.0,
                0.6, 0.6, 0.6, 1.0,
            ),
            2: (
                0.7, 0.7, 0.7, 0.5,
                1.0, 1.0, 1.0, 0.5,
                0.5, 0.5, 0.5, 0.5,
                0.6, 0.6, 0.6, 0.5,
            ),
            3: (
                0,   0,   0.7, 1.0,
                1,   1,   1,   1.0,
                0.5, 0,   0,   1.0,
                0,   0.6, 0,   1.0,
            ),
            4: (
                0,   0,   0.7, 0.5,
                1,   1,   1,   0.5,
                0.5, 0,   0,   0.5,
                0,   0.6, 0,   0.5,
            )
        }
        # fmt: on
        for i in range(1, 5):
            self.run_test_create_surface_style_with_textures_from_ifc_pixel_image(
                i, ifc_pixel_data[i], expected_pixel_data[i]
            )

    def run_test_create_surface_style_with_textures_from_ifc_pixel_image(
        self, n_components, ifc_pixel_data, expected_pixel_data
    ):
        # this case occurs when we edit shader properties without saving them to IFC
        bpy.ops.bim.create_project()

        ifc_file = tool.Ifc.get()
        style = tool.Ifc.run("style.add_style", name="test")
        material = bpy.data.materials.new(style.Name)
        tool.Ifc.link(style, material)
        get_color = lambda value: {color: value for color in ("Red", "Green", "Blue")}
        rendering_attributes = {
            "ReflectanceMethod": "NOTDEFINED",
            "DiffuseColour": get_color(0.5),
            "SurfaceColour": get_color(0.3),
            "Transparency": 0.3,
            "SpecularHighlight": {"IfcSpecularRoughness": 0.4},
            "SpecularColour": 0.03,
        }
        rendering_style = tool.Ifc.run(
            "style.add_surface_style",
            style=style,
            ifc_class="IfcSurfaceStyleRendering",
            attributes=rendering_attributes,
        )

        def get_pixels_binary():
            # just 4 pixels - red, green, blue, white
            # IfcPixelTexture as Blender has reversed order of pixels rows: (0,0) - bottom left of the image
            # https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcPixelTexture.htm
            # fmt: off
            pixels = np.array(ifc_pixel_data) * 255
            pixels = pixels.reshape((4, n_components))
            return ["".join(["{:08b}".format(int(i)) for i in pixel]) for pixel in pixels]

        texture_data = {
            "Pixel": get_pixels_binary(),
            "ColourComponents": n_components,
            "Width": 2,
            "Height": 2,
            "Mode": "DIFFUSE",
            "RepeatS": True,
            "RepeatT": True,
        }
        # setup texture manually as `style.add_surface_textures` doesn't support non-IfcImageTexture textures
        textures = [ifc_file.create_entity("IfcPixelTexture", **texture_data)]
        # setup UV
        ifc_file.create_entity("IfcTextureCoordinateGenerator", Maps=textures, Mode="COORD")

        texture_style = tool.Ifc.run(
            "style.add_surface_style",
            style=style,
            ifc_class="IfcSurfaceStyleWithTextures",
            attributes={"Textures": textures},
        )

        subject.create_surface_style_rendering(material, rendering_style)
        subject.create_surface_style_with_textures(material, rendering_style, texture_style)

        used_node_types = set([n.type for n in material.node_tree.nodes[:]])
        assert used_node_types == set((["OUTPUT_MATERIAL", "BSDF_PRINCIPLED", "TEX_IMAGE", "TEX_COORD"]))

        image_node = tool.Blender.get_material_node(material, "TEX_IMAGE")
        assert image_node.outputs["Color"].links[0].to_socket.name == "Base Color"
        assert image_node.inputs["Vector"].links[0].from_socket.name == "Generated"
        assert image_node.image.filepath == ""
        assert np.allclose(
            image_node.image.pixels[:], expected_pixel_data, atol=0.01
        ), f"Failed to match pixels for {n_components}.\nBlender pixel_data: {image_node.image.pixels[:]}.\nExpected data: {expected_pixel_data}"


class TestLoadingIndexedMap(NewFile):
    def test_load_texture_map(self):
        bpy.context.scene.unit_settings.length_unit = "MILLIMETERS"
        bpy.ops.bim.create_project()

        # create a cube without uv and triangulate it
        mesh = bpy.data.meshes.new("Cube")
        bm = tool.Blender.get_bmesh_for_mesh(mesh, clean=True)
        bmesh.ops.create_cube(bm, size=2.0, calc_uvs=False)
        bmesh.ops.triangulate(bm, faces=bm.faces[:])
        tool.Blender.apply_bmesh(mesh, bm)

        ifc_file = tool.Ifc.get()
        builder = ShapeBuilder(ifc_file)

        # tesselated cube
        face_set = builder.polygonal_face_set([v.co for v in mesh.vertices], [p.vertices[:] for p in mesh.polygons])

        uv_indices = (
            (1, 2, 3),
            (4, 5, 6),
            (7, 8, 9),
            (10, 11, 12),
            (13, 14, 15),
            (16, 17, 18),
            (19, 20, 21),
            (22, 23, 24),
            (25, 26, 27),
            (28, 29, 30),
            (31, 32, 33),
            (34, 35, 36),
        )
        uv_verts = (
            (0.625, 0.0),
            (0.375, 0.25),
            (0.375, 0.0),
            (0.625, 0.25),
            (0.375, 0.5),
            (0.375, 0.25),
            (0.625, 0.5),
            (0.375, 0.75),
            (0.375, 0.5),
            (0.625, 0.75),
            (0.375, 1.0),
            (0.375, 0.75),
            (0.375, 0.5),
            (0.125, 0.75),
            (0.125, 0.5),
            (0.875, 0.5),
            (0.625, 0.75),
            (0.625, 0.5),
            (0.625, 0.0),
            (0.625, 0.25),
            (0.375, 0.25),
            (0.625, 0.25),
            (0.625, 0.5),
            (0.375, 0.5),
            (0.625, 0.5),
            (0.625, 0.75),
            (0.375, 0.75),
            (0.625, 0.75),
            (0.625, 1.0),
            (0.375, 1.0),
            (0.375, 0.5),
            (0.375, 0.75),
            (0.125, 0.75),
            (0.875, 0.5),
            (0.875, 0.75),
            (0.625, 0.75),
        )
        uv_verts_list = ifc_file.createIfcTextureVertexList()
        uv_verts_list.TexCoordsList = uv_verts
        texture_coord = ifc_file.createIfcIndexedTriangleTextureMap()
        texture_coord.MappedTo = face_set
        texture_coord.TexCoordIndex = uv_indices
        texture_coord.TexCoords = uv_verts_list

        subject.load_indexed_map(texture_coord, mesh)

        uv_layer = mesh.uv_layers.active
        assert uv_layer is not None
        for ifc_uv, blender_uv in zip(uv_verts, uv_layer.uv, strict=True):
            assert tool.Cad.are_vectors_equal(Vector(ifc_uv), blender_uv.vector)

    def test_load_color_map(self):
        bpy.context.scene.unit_settings.length_unit = "MILLIMETERS"
        bpy.ops.bim.create_project()

        # create a cube without uv and triangulate it
        mesh = bpy.data.meshes.new("Cube")
        bm = tool.Blender.get_bmesh_for_mesh(mesh, clean=True)
        bmesh.ops.create_cube(bm, size=2.0, calc_uvs=False)
        bmesh.ops.triangulate(bm, faces=bm.faces[:])
        tool.Blender.apply_bmesh(mesh, bm)

        ifc_file = tool.Ifc.get()
        builder = ShapeBuilder(ifc_file)

        # tesselated cube
        face_set = builder.polygonal_face_set([v.co for v in mesh.vertices], [p.vertices[:] for p in mesh.polygons])

        colors = ((1.0, 0.0, 0.0), (0.0, 0.5, 0.0), (1.0, 1.0, 0.0))
        color_index = (0, 0, 0, 0, 2, 1, 0, 0, 0, 0, 2, 1)

        ifc_colors_list = ifc_file.create_entity("IfcColourRgbList", colors)
        colour_map = ifc_file.create_entity("IfcIndexedColourMap")
        colour_map.MappedTo = face_set
        colour_map.Colours = ifc_colors_list
        colour_map.ColourIndex = [i + 1 for i in color_index]

        subject.load_indexed_map(colour_map, mesh)

        layer = mesh.color_attributes.active_color
        assert layer is not None
        for face_i, face in enumerate(mesh.polygons):
            for loop_i in face.loop_indices:
                blender_color = Vector(layer.data[loop_i].color)
                ifc_color = Vector(colors[color_index[face_i]] + (1.0,))
                assert tool.Cad.are_vectors_equal(blender_color, ifc_color)


class TestSetupActiveBsddClassification(NewFile):
    def run_test(self, schema: ifcopenshell.util.schema.IFC_SCHEMA) -> None:
        schema_ = "IFC4X3_ADD2" if schema == "IFC4X3" else schema
        bpy.context.scene.BIMProjectProperties.export_schema = schema_
        bpy.ops.bim.create_project()
        ifc_file = tool.Ifc.get()
        name = "CCI Construction"
        base_uri = "https://identifier.buildingsmart.org/uri/molio/cciconstruction/1.0"
        if schema == "IFC2X3":
            uri = "https://identifier.buildingsmart.org/uri/molio/cciconstruction/1.0/class/A-BDC"
            classification = ifc_file.create_entity("IfcClassification", Name=name)
            ifc_file.create_entity("IfcClassificationReference", Location=uri, ReferencedSource=classification)
        else:
            attr_name = "Specification" if schema == "IFC4X3" else "Location"
            classification = ifc_file.create_entity("IfcClassification", Name=name)
            setattr(classification, attr_name, base_uri)
        filepath = "test/files/temp/test.ifc"
        ifc_file.write(filepath)
        bpy.ops.bim.load_project(filepath=filepath)
        props = bpy.context.scene.BIMBSDDProperties
        assert props.active_domain == name
        assert props.active_uri == base_uri

    def test_set_load_and_set_active_bsdd_ifc2x3(self):
        self.run_test("IFC2X3")

    def test_set_load_and_set_active_bsdd_ifc4(self):
        self.run_test("IFC4")

    def test_set_load_and_set_active_bsdd_ifc4x3(self):
        self.run_test("IFC4X3")
