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

import os
import bpy
import ifcopenshell
import ifcopenshell.api
import ifcopenshell.util.representation
import bonsai.core.tool
import bonsai.tool as tool
from test.bim.bootstrap import NewFile
from bonsai.tool.style import Style as subject
from ifcopenshell.util.shape_builder import ShapeBuilder


class TestImplementsTool(NewFile):
    def test_run(self):
        assert isinstance(subject(), bonsai.core.tool.Style)


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
        props = bpy.context.scene.BIMStylesProperties
        props.is_editing_style = 1
        subject.disable_editing()
        assert props.is_editing_style == 0


class TestDisableEditingStyles(NewFile):
    def test_run(self):
        bpy.context.scene.BIMStylesProperties.is_editing = True
        subject.disable_editing_styles()
        assert bpy.context.scene.BIMStylesProperties.is_editing is False


class TestEnableEditing(NewFile):
    def test_run(self):
        props = bpy.context.scene.BIMStylesProperties
        style = ifcopenshell.file().create_entity("IfcSurfaceStyle")
        subject.enable_editing(style)
        assert props.is_editing_style is style.id()


class TestEnableEditingStyles(NewFile):
    def test_run(self):
        bpy.context.scene.BIMStylesProperties.is_editing = False
        subject.enable_editing_styles()
        assert bpy.context.scene.BIMStylesProperties.is_editing is True


class TestExportSurfaceAttributes(NewFile):
    def test_run(self):
        TestImportSurfaceAttributes().test_run()
        assert subject.export_surface_attributes() == {"Name": "Name", "Side": "BOTH"}


class TestGetActiveStyleType(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        bpy.context.scene.BIMStylesProperties.style_type = "IfcSurfaceStyle"
        assert subject.get_active_style_type() == "IfcSurfaceStyle"
        bpy.context.scene.BIMStylesProperties.style_type = "IfcCurveStyle"
        assert subject.get_active_style_type() == "IfcCurveStyle"


class TestGetContext(NewFile):
    def test_run(self):
        bpy.ops.bim.create_project()
        context = ifcopenshell.util.representation.get_context(tool.Ifc.get(), "Model", "Body", "MODEL_VIEW")
        assert subject.get_context() == context


class TestGetElementsByStyle(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        element = ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcWall")
        style = ifc.createIfcSurfaceStyle()
        item = ifc.createIfcExtrudedAreaSolid()
        ifc.createIfcStyledItem(Item=item, Styles=[style])
        element.Representation = ifc.createIfcProductDefinitionShape(
            Representations=[ifc.createIfcShapeRepresentation(Items=[item])]
        )
        assert subject.get_elements_by_style(style) == {element}


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
        obj.BIMStyleProperties.ifc_definition_id = style.id()
        assert subject.get_style(obj) == style

    def test_getting_nothing_for_a_broken_link_style(self):
        obj = bpy.data.materials.new("Material")
        obj.BIMStyleProperties.ifc_definition_id = 1
        assert subject.get_style(obj) == None


class TestGetSurfaceRenderingAttributes(NewFile):
    def test_get_different_surface_and_diffuse_colours_from_a_principled_bsdf(self):
        obj = bpy.data.materials.new("Material")
        obj.diffuse_color = [1, 1, 1, 1]
        obj.use_nodes = True
        node = tool.Blender.get_material_node(obj, "BSDF_PRINCIPLED")
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
        output = tool.Blender.get_material_node(obj, "OUTPUT_MATERIAL")
        node = tool.Blender.get_material_node(obj, "BSDF_PRINCIPLED")
        obj.node_tree.nodes.remove(node)

        node = obj.node_tree.nodes.new(type="ShaderNodeBsdfGlossy")
        node.inputs["Color"].default_value = [0.5, 0.5, 0.5, 0.5]
        node.inputs["Roughness"].default_value = 0.2
        obj.node_tree.links.new(node.outputs[0], output.inputs[0])

        assert subject.get_surface_rendering_attributes(obj) == {
            "SurfaceColour": {
                "Name": None,
                "Red": 1,
                "Green": 1,
                "Blue": 1,
            },
            "Transparency": 0,
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
        output = tool.Blender.get_material_node(obj, "OUTPUT_MATERIAL")
        node = tool.Blender.get_material_node(obj, "BSDF_PRINCIPLED")
        obj.node_tree.nodes.remove(node)

        node = obj.node_tree.nodes.new(type="ShaderNodeBsdfDiffuse")
        node.inputs["Color"].default_value = [0.5, 0.5, 0.5, 0.5]
        node.inputs["Roughness"].default_value = 0.2
        obj.node_tree.links.new(node.outputs[0], output.inputs[0])

        assert subject.get_surface_rendering_attributes(obj) == {
            "SurfaceColour": {
                "Name": None,
                "Red": 1,
                "Green": 1,
                "Blue": 1,
            },
            "Transparency": 0,
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
        output = tool.Blender.get_material_node(obj, "OUTPUT_MATERIAL")
        node = tool.Blender.get_material_node(obj, "BSDF_PRINCIPLED")
        obj.node_tree.nodes.remove(node)

        node = obj.node_tree.nodes.new(type="ShaderNodeBsdfGlass")
        node.inputs["Color"].default_value = [0.5, 0.5, 0.5, 0.5]
        node.inputs["Roughness"].default_value = 0.2
        obj.node_tree.links.new(node.outputs[0], output.inputs[0])

        assert subject.get_surface_rendering_attributes(obj) == {
            "SurfaceColour": {
                "Name": None,
                "Red": 1,
                "Green": 1,
                "Blue": 1,
            },
            "Transparency": 0,
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
        output = tool.Blender.get_material_node(obj, "OUTPUT_MATERIAL")
        node = tool.Blender.get_material_node(obj, "BSDF_PRINCIPLED")
        obj.node_tree.nodes.remove(node)

        node = obj.node_tree.nodes.new(type="ShaderNodeEmission")
        node.inputs["Color"].default_value = [0.5, 0.5, 0.5, 0.5]
        obj.node_tree.links.new(node.outputs[0], output.inputs[0])

        assert subject.get_surface_rendering_attributes(obj) == {
            "SurfaceColour": {
                "Name": None,
                "Red": 1,
                "Green": 1,
                "Blue": 1,
            },
            "Transparency": 0,
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
        output = tool.Blender.get_material_node(obj, "OUTPUT_MATERIAL")
        node = tool.Blender.get_material_node(obj, "BSDF_PRINCIPLED")
        obj.node_tree.nodes.remove(node)

        node = obj.node_tree.nodes.new(type="ShaderNodeVolumePrincipled")
        node.inputs["Color"].default_value = [0.5, 0.5, 0.5, 0.5]
        obj.node_tree.links.new(node.outputs[0], output.inputs[0])

        assert subject.get_surface_rendering_attributes(obj) == {
            "SurfaceColour": {
                "Name": None,
                "Red": 1,
                "Green": 1,
                "Blue": 1,
            },
            "Transparency": 0,
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
        obj.BIMStyleProperties.ifc_definition_id = style.id()
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
        obj.BIMStyleProperties.ifc_definition_id = style.id()
        assert subject.get_surface_shading_style(obj) == style_item

    def test_do_not_get_rendering_styles(self):
        tool.Ifc.set(ifcopenshell.file())
        style_item = tool.Ifc.get().createIfcSurfaceStyleRendering()
        style = tool.Ifc.get().createIfcSurfaceStyle(Styles=[style_item])
        obj = bpy.data.materials.new("Material")
        obj.BIMStyleProperties.ifc_definition_id = style.id()
        assert subject.get_surface_shading_style(obj) is None


class TestGetSurfaceTextureStyle(NewFile):
    def test_run(self):
        tool.Ifc.set(ifcopenshell.file())
        style_item = tool.Ifc.get().createIfcSurfaceStyleWithTextures()
        style = tool.Ifc.get().createIfcSurfaceStyle(Styles=[style_item])
        obj = bpy.data.materials.new("Material")
        obj.BIMStyleProperties.ifc_definition_id = style.id()
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
        tool.Ifc.set(ifc := ifcopenshell.file())
        props = bpy.context.scene.BIMStylesProperties
        style = ifc.create_entity("IfcSurfaceStyle", "Name", "BOTH")
        subject.import_surface_attributes(style)
        assert props.attributes.get("Name").string_value == "Name"
        assert props.attributes.get("Side").enum_value == "BOTH"

    def test_importing_surface_attributes_twice(self):
        tool.Ifc.set(ifc := ifcopenshell.file())
        style = ifc.create_entity("IfcSurfaceStyle", "Name", "BOTH")
        props = bpy.context.scene.BIMStylesProperties
        subject.import_surface_attributes(style)
        assert len(props.attributes) == 2
        assert props.attributes.get("Name").string_value == "Name"
        assert props.attributes.get("Side").enum_value == "BOTH"
        subject.import_surface_attributes(style)
        assert len(props.attributes) == 2
        assert props.attributes.get("Name").string_value == "Name"
        assert props.attributes.get("Side").enum_value == "BOTH"


class TestImportPresentationStyles(NewFile):
    def test_import_curve_styles(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        style = ifc.createIfcCurveStyle(Name="Name")
        subject.import_presentation_styles("IfcCurveStyle")
        props = bpy.context.scene.BIMStylesProperties
        assert props.styles[0].ifc_definition_id == style.id()
        assert props.styles[0].name == "Name"
        assert props.styles[0].total_elements == 0

    def test_import_fillarea_styles(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        style = ifc.createIfcFillAreaStyle(Name="Name")
        subject.import_presentation_styles("IfcFillAreaStyle")
        props = bpy.context.scene.BIMStylesProperties
        assert props.styles[0].ifc_definition_id == style.id()
        assert props.styles[0].name == "Name"
        assert props.styles[0].total_elements == 0

    def test_import_surface_styles(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        style = ifc.createIfcSurfaceStyle(Name="Name")
        subject.import_presentation_styles("IfcSurfaceStyle")
        props = bpy.context.scene.BIMStylesProperties
        assert props.styles[0].ifc_definition_id == style.id()
        assert props.styles[0].name == "Name"
        assert props.styles[0].total_elements == 0

    def test_import_text_styles(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        style = ifc.createIfcTextStyle(Name="Name")
        subject.import_presentation_styles("IfcTextStyle")
        props = bpy.context.scene.BIMStylesProperties
        assert props.styles[0].ifc_definition_id == style.id()
        assert props.styles[0].name == "Name"
        assert props.styles[0].total_elements == 0


class TestIsEditingStyles(NewFile):
    def test_run(self):
        bpy.context.scene.BIMStylesProperties.is_editing = False
        assert subject.is_editing_styles() is False
        bpy.context.scene.BIMStylesProperties.is_editing = True
        assert subject.is_editing_styles() is True


class TestGetRepresentationStyleItem(NewFile):
    def test_run(self):
        tool.Ifc.set(ifc := ifcopenshell.file())
        builder = ShapeBuilder(ifc)
        rectangle = builder.rectangle()

        assert subject.get_representation_item_style(rectangle) == None
        style = ifc.createIfcSurfaceStyle()
        subject.assign_style_to_representation_item(rectangle, style)
        assert subject.get_representation_item_style(rectangle) == style


class TestAssignStyleToRepresentationItem(NewFile):
    def test_run(self):
        tool.Ifc.set(ifc := ifcopenshell.file())
        builder = ShapeBuilder(ifc)
        rectangle = builder.rectangle()

        # assigning new style
        style1 = ifc.createIfcSurfaceStyle()
        subject.assign_style_to_representation_item(rectangle, style1)
        assert subject.get_representation_item_style(rectangle) == style1

        # changing style
        style2 = ifc.createIfcSurfaceStyle()
        subject.assign_style_to_representation_item(rectangle, style2)
        assert subject.get_representation_item_style(rectangle) == style2

        # unassigning styles
        subject.assign_style_to_representation_item(rectangle, None)
        assert subject.get_representation_item_style(rectangle) == None
