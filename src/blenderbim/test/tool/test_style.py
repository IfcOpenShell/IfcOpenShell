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

import os
import bpy
import ifcopenshell
import blenderbim.core.tool
import blenderbim.tool as tool
from test.bim.bootstrap import NewFile
from blenderbim.tool.style import Style as subject


class TestImplementsTool(NewFile):
    def test_run(self):
        assert isinstance(subject(), blenderbim.core.tool.Style)


class TestCanSupportRenderingStyle(NewFile):
    def test_anything_with_nodes_can_support_a_rendering_style(self):
        obj = bpy.data.materials.new("Material")
        obj.use_nodes = True
        assert subject.can_support_rendering_style(obj) is True

    def test_without_nodes_we_do_not_support_rendering(self):
        obj = bpy.data.materials.new("Material")
        obj.use_nodes = False
        assert subject.can_support_rendering_style(obj) is False


class TestDisableEditing(NewFile):
    def test_run(self):
        obj = bpy.data.materials.new("Material")
        obj.BIMStyleProperties.is_editing = True
        subject.disable_editing(obj)
        assert obj.BIMStyleProperties.is_editing is False


class TestEnableEditing(NewFile):
    def test_run(self):
        obj = bpy.data.materials.new("Material")
        subject.enable_editing(obj)
        assert obj.BIMStyleProperties.is_editing is True


class TestExportSurfaceAttributes(NewFile):
    def test_run(self):
        TestImportSurfaceAttributes().test_run()
        obj = bpy.data.materials.get("Material")
        assert subject.export_surface_attributes(obj) == {"Name": "Name", "Side": "BOTH"}


class TestGetContext(NewFile):
    def test_run(self):
        bpy.ops.bim.create_project()
        context = ifcopenshell.util.representation.get_context(tool.Ifc.get(), "Model", "Body", "MODEL_VIEW")
        assert subject.get_context("obj") == context


class TestGetName(NewFile):
    def test_run(self):
        assert subject.get_name(bpy.data.materials.new("Material")) == "Material"


class TestGetStyle(NewFile):
    def test_getting_no_style(self):
        assert subject.get_style(bpy.data.materials.new("Material")) is None

    def test_getting_a_linked_style(self):
        tool.Ifc.set(ifcopenshell.file())
        style = tool.Ifc.get().createIfcSurfaceStyle()
        obj = bpy.data.materials.new("Material")
        obj.BIMMaterialProperties.ifc_style_id = style.id()
        assert subject.get_style(obj) == style

    def test_getting_nothing_for_a_broken_link_style(self):
        obj = bpy.data.materials.new("Material")
        obj.BIMMaterialProperties.ifc_style_id = 1
        assert subject.get_style(obj) == None


class TestGetSurfaceRenderingAttributes(NewFile):
    def test_get_different_surface_and_diffuse_colours_from_a_principled_bsdf(self):
        obj = bpy.data.materials.new("Material")
        obj.diffuse_color = [1, 1, 1, 1]
        obj.use_nodes = True
        node = obj.node_tree.nodes["Principled BSDF"]
        node.inputs["Alpha"].default_value = 0.8
        node.inputs["Base Color"].default_value = [0.5, 0.5, 0.5, 0.5]
        node.inputs["Roughness"].default_value = 0.2
        assert subject.get_surface_rendering_attributes(obj) == {
            "SurfaceColour": {
                "Name": None,
                "Red": 1,
                "Green": 1,
                "Blue": 1,
            },
            "Transparency": 1 - node.inputs["Alpha"].default_value,
            "DiffuseColour": {
                "Name": None,
                "Red": 0.5,
                "Green": 0.5,
                "Blue": 0.5,
            },
            "SpecularColour": 0.0,
            "SpecularHighlight": {"IfcSpecularRoughness": 0.2},
            "ReflectanceMethod": "NOTDEFINED",
        }

    def test_get_rendering_styles_from_a_glossy_bsdf(self):
        obj = bpy.data.materials.new("Material")
        obj.diffuse_color = [1, 1, 1, 1]
        obj.use_nodes = True
        node = obj.node_tree.nodes["Principled BSDF"]
        obj.node_tree.nodes.remove(node)
        node = obj.node_tree.nodes.new(type="ShaderNodeBsdfGlossy")
        node.inputs["Color"].default_value = [0.5, 0.5, 0.5, 0.5]
        node.inputs["Roughness"].default_value = 0.2
        assert subject.get_surface_rendering_attributes(obj) == {
            "SurfaceColour": {
                "Name": None,
                "Red": 1,
                "Green": 1,
                "Blue": 1,
            },
            "Transparency": 1,
            "DiffuseColour": {
                "Name": None,
                "Red": 0.5,
                "Green": 0.5,
                "Blue": 0.5,
            },
            "SpecularHighlight": {"IfcSpecularRoughness": 0.2},
            "ReflectanceMethod": "METAL",
        }

    def test_get_rendering_styles_from_a_diffuse_bsdf(self):
        obj = bpy.data.materials.new("Material")
        obj.diffuse_color = [1, 1, 1, 1]
        obj.use_nodes = True
        node = obj.node_tree.nodes["Principled BSDF"]
        obj.node_tree.nodes.remove(node)
        node = obj.node_tree.nodes.new(type="ShaderNodeBsdfDiffuse")
        node.inputs["Color"].default_value = [0.5, 0.5, 0.5, 0.5]
        node.inputs["Roughness"].default_value = 0.2
        assert subject.get_surface_rendering_attributes(obj) == {
            "SurfaceColour": {
                "Name": None,
                "Red": 1,
                "Green": 1,
                "Blue": 1,
            },
            "Transparency": 1,
            "DiffuseColour": {
                "Name": None,
                "Red": 0.5,
                "Green": 0.5,
                "Blue": 0.5,
            },
            "SpecularHighlight": {"IfcSpecularRoughness": 0.2},
            "ReflectanceMethod": "MATT",
        }

    def test_get_rendering_styles_from_a_glass_bsdf(self):
        obj = bpy.data.materials.new("Material")
        obj.diffuse_color = [1, 1, 1, 1]
        obj.use_nodes = True
        node = obj.node_tree.nodes["Principled BSDF"]
        obj.node_tree.nodes.remove(node)
        node = obj.node_tree.nodes.new(type="ShaderNodeBsdfGlass")
        node.inputs["Color"].default_value = [0.5, 0.5, 0.5, 0.5]
        node.inputs["Roughness"].default_value = 0.2
        assert subject.get_surface_rendering_attributes(obj) == {
            "SurfaceColour": {
                "Name": None,
                "Red": 1,
                "Green": 1,
                "Blue": 1,
            },
            "Transparency": 1,
            "DiffuseColour": {
                "Name": None,
                "Red": 0.5,
                "Green": 0.5,
                "Blue": 0.5,
            },
            "SpecularHighlight": {"IfcSpecularRoughness": 0.2},
            "ReflectanceMethod": "GLASS",
        }

    def test_get_rendering_styles_from_a_emission_bsdf(self):
        obj = bpy.data.materials.new("Material")
        obj.diffuse_color = [1, 1, 1, 1]
        obj.use_nodes = True
        node = obj.node_tree.nodes["Principled BSDF"]
        obj.node_tree.nodes.remove(node)
        node = obj.node_tree.nodes.new(type="ShaderNodeEmission")
        node.inputs["Color"].default_value = [0.5, 0.5, 0.5, 0.5]
        assert subject.get_surface_rendering_attributes(obj) == {
            "SurfaceColour": {
                "Name": None,
                "Red": 1,
                "Green": 1,
                "Blue": 1,
            },
            "Transparency": 1,
            "DiffuseColour": {
                "Name": None,
                "Red": 0.5,
                "Green": 0.5,
                "Blue": 0.5,
            },
            "SpecularHighlight": None,
            "ReflectanceMethod": "FLAT",
        }

    def test_other_unsupported_bsdfs_copy_the_rendering_style_from_the_shading_colours_as_a_fallback(self):
        obj = bpy.data.materials.new("Material")
        obj.diffuse_color = [1, 1, 1, 1]
        obj.use_nodes = True
        node = obj.node_tree.nodes["Principled BSDF"]
        obj.node_tree.nodes.remove(node)
        node = obj.node_tree.nodes.new(type="ShaderNodeVolumePrincipled")
        node.inputs["Color"].default_value = [0.5, 0.5, 0.5, 0.5]
        assert subject.get_surface_rendering_attributes(obj) == {
            "SurfaceColour": {
                "Name": None,
                "Red": 1,
                "Green": 1,
                "Blue": 1,
            },
            "Transparency": 1,
            "DiffuseColour": {
                "Name": None,
                "Red": 1,
                "Green": 1,
                "Blue": 1,
            },
            "SpecularHighlight": None,
            "ReflectanceMethod": "NOTDEFINED",
        }


class TestGetSurfaceRenderingStyle(NewFile):
    def test_run(self):
        tool.Ifc.set(ifcopenshell.file())
        style_item = tool.Ifc.get().createIfcSurfaceStyleRendering()
        style = tool.Ifc.get().createIfcSurfaceStyle(Styles=[style_item])
        obj = bpy.data.materials.new("Material")
        obj.BIMMaterialProperties.ifc_style_id = style.id()
        assert subject.get_surface_rendering_style(obj) == style_item


class TestGetSurfaceShadingAttributes(NewFile):
    def test_get_colours_from_a_basic_material(self):
        tool.Ifc.set(ifcopenshell.file())
        obj = bpy.data.materials.new("Material")
        obj.diffuse_color = [1, 1, 1, 1]
        assert subject.get_surface_shading_attributes(obj) == {
            "SurfaceColour": {
                "Name": None,
                "Red": 1,
                "Green": 1,
                "Blue": 1,
            },
            "Transparency": 0,
        }

    def test_get_colours_from_a_basic_material_ifc2x3(self):
        tool.Ifc.set(ifcopenshell.file(schema="IFC2X3"))
        obj = bpy.data.materials.new("Material")
        obj.diffuse_color = [1, 1, 1, 1]
        assert subject.get_surface_shading_attributes(obj) == {
            "SurfaceColour": {
                "Name": None,
                "Red": 1,
                "Green": 1,
                "Blue": 1,
            },
        }


class TestGetSurfaceShadingStyle(NewFile):
    def test_run(self):
        tool.Ifc.set(ifcopenshell.file())
        style_item = tool.Ifc.get().createIfcSurfaceStyleShading()
        style = tool.Ifc.get().createIfcSurfaceStyle(Styles=[style_item])
        obj = bpy.data.materials.new("Material")
        obj.BIMMaterialProperties.ifc_style_id = style.id()
        assert subject.get_surface_shading_style(obj) == style_item

    def test_do_not_get_rendering_styles(self):
        tool.Ifc.set(ifcopenshell.file())
        style_item = tool.Ifc.get().createIfcSurfaceStyleRendering()
        style = tool.Ifc.get().createIfcSurfaceStyle(Styles=[style_item])
        obj = bpy.data.materials.new("Material")
        obj.BIMMaterialProperties.ifc_style_id = style.id()
        assert subject.get_surface_shading_style(obj) is None


class TestGetSurfaceTextureStyle(NewFile):
    def test_run(self):
        tool.Ifc.set(ifcopenshell.file())
        style_item = tool.Ifc.get().createIfcSurfaceStyleWithTextures()
        style = tool.Ifc.get().createIfcSurfaceStyle(Styles=[style_item])
        obj = bpy.data.materials.new("Material")
        obj.BIMMaterialProperties.ifc_style_id = style.id()
        assert subject.get_surface_texture_style(obj) == style_item


class TestGetUVMaps(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        item = ifc.createIfcTriangulatedFaceSet()
        uv_map = ifc.createIfcIndexedTriangleTextureMap(MappedTo=item)
        representation = ifc.createIfcShapeRepresentation(Items=[item])
        assert subject.get_uv_maps(representation) == [uv_map]


class TestImportSurfaceAttributes(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        style = ifc.createIfcSurfaceStyle("Name", "BOTH")
        obj = bpy.data.materials.new("Material")
        subject.import_surface_attributes(style, obj)
        assert obj.BIMStyleProperties.attributes.get("Name").string_value == "Name"
        assert obj.BIMStyleProperties.attributes.get("Side").enum_value == "BOTH"

    def test_importing_surface_attributes_twice(self):
        ifc = ifcopenshell.file()
        style = ifc.createIfcSurfaceStyle("Name", "BOTH")
        obj = bpy.data.materials.new("Material")
        subject.import_surface_attributes(style, obj)
        assert len(obj.BIMStyleProperties.attributes) == 2
        assert obj.BIMStyleProperties.attributes.get("Name").string_value == "Name"
        assert obj.BIMStyleProperties.attributes.get("Side").enum_value == "BOTH"
        subject.import_surface_attributes(style, obj)
        assert len(obj.BIMStyleProperties.attributes) == 2
        assert obj.BIMStyleProperties.attributes.get("Name").string_value == "Name"
        assert obj.BIMStyleProperties.attributes.get("Side").enum_value == "BOTH"
