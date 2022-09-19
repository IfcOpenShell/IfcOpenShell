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
import blenderbim.bim.helper


class Style(blenderbim.core.tool.Style):
    @classmethod
    def can_support_rendering_style(cls, obj):
        return obj.use_nodes and hasattr(obj.node_tree, "nodes")

    @classmethod
    def disable_editing(cls, obj):
        obj.BIMStyleProperties.is_editing = False

    @classmethod
    def disable_editing_styles(cls):
        bpy.context.scene.BIMStylesProperties.is_editing = False

    @classmethod
    def enable_editing(cls, obj):
        obj.BIMStyleProperties.is_editing = True

    @classmethod
    def enable_editing_styles(cls):
        bpy.context.scene.BIMStylesProperties.is_editing = True

    @classmethod
    def export_surface_attributes(cls, obj):
        return blenderbim.bim.helper.export_attributes(obj.BIMStyleProperties.attributes)

    @classmethod
    def get_active_style_type(cls):
        return bpy.context.scene.BIMStylesProperties.style_type

    @classmethod
    def get_context(cls, obj):
        return ifcopenshell.util.representation.get_context(tool.Ifc.get(), "Model", "Body", "MODEL_VIEW")

    @classmethod
    def get_elements_by_style(cls, style):
        return ifcopenshell.util.element.get_elements_by_style(tool.Ifc.get(), style)

    @classmethod
    def get_name(cls, obj):
        return obj.name

    @classmethod
    def get_style(cls, obj):
        if obj.BIMMaterialProperties.ifc_style_id:
            try:
                return tool.Ifc.get().by_id(obj.BIMMaterialProperties.ifc_style_id)
            except:
                return

    @classmethod
    def get_surface_rendering_attributes(cls, obj):
        transparency = 1 - obj.diffuse_color[3]
        diffuse_color = obj.diffuse_color

        attributes = {
            "SurfaceColour": {
                "Name": None,
                "Red": obj.diffuse_color[0],
                "Green": obj.diffuse_color[1],
                "Blue": obj.diffuse_color[2],
            },
            "Transparency": transparency,
        }

        bsdfs = {n.type: n for n in obj.node_tree.nodes}
        if "BSDF_GLOSSY" in bsdfs:
            attributes["ReflectanceMethod"] = "METAL"
            bsdf = bsdfs["BSDF_GLOSSY"]
            attributes["SpecularHighlight"] = {"IfcSpecularRoughness": round(bsdf.inputs["Roughness"].default_value, 3)}
            diffuse_color = bsdf.inputs["Color"].default_value
        elif "BSDF_DIFFUSE" in bsdfs:
            attributes["ReflectanceMethod"] = "MATT"
            bsdf = bsdfs["BSDF_DIFFUSE"]
            attributes["SpecularHighlight"] = {"IfcSpecularRoughness": round(bsdf.inputs["Roughness"].default_value, 3)}
            diffuse_color = bsdf.inputs["Color"].default_value
        elif "BSDF_GLASS" in bsdfs:
            attributes["ReflectanceMethod"] = "GLASS"
            bsdf = bsdfs["BSDF_GLASS"]
            attributes["SpecularHighlight"] = {"IfcSpecularRoughness": round(bsdf.inputs["Roughness"].default_value, 3)}
            diffuse_color = bsdf.inputs["Color"].default_value
        elif "EMISSION" in bsdfs:
            attributes["ReflectanceMethod"] = "FLAT"
            bsdf = bsdfs["EMISSION"]
            attributes["SpecularHighlight"] = None
            diffuse_color = bsdf.inputs["Color"].default_value
        elif "BSDF_PRINCIPLED" in bsdfs:
            attributes["ReflectanceMethod"] = "NOTDEFINED"
            bsdf = bsdfs["BSDF_PRINCIPLED"]
            attributes["SpecularColour"] = round(bsdf.inputs["Metallic"].default_value, 3)
            attributes["SpecularHighlight"] = {"IfcSpecularRoughness": round(bsdf.inputs["Roughness"].default_value, 3)}
            diffuse_color = bsdf.inputs["Base Color"].default_value
            attributes["Transparency"] = 1 - bsdf.inputs["Alpha"].default_value
        else:
            attributes["ReflectanceMethod"] = "NOTDEFINED"
            attributes["SpecularHighlight"] = None
            attributes["DiffuseColour"] = attributes["SurfaceColour"]
            return attributes

        attributes["DiffuseColour"] = {
            "Name": None,
            "Red": diffuse_color[0],
            "Green": diffuse_color[1],
            "Blue": diffuse_color[2],
        }

        return attributes

    @classmethod
    def get_surface_rendering_style(cls, obj):
        if obj.BIMMaterialProperties.ifc_style_id:
            style = tool.Ifc.get().by_id(obj.BIMMaterialProperties.ifc_style_id)
            items = [s for s in style.Styles if s.is_a("IfcSurfaceStyleRendering")]
            if items:
                return items[0]

    @classmethod
    def get_surface_shading_attributes(cls, obj):
        data = {
            "SurfaceColour": {
                "Name": None,
                "Red": obj.diffuse_color[0],
                "Green": obj.diffuse_color[1],
                "Blue": obj.diffuse_color[2],
            },
            "Transparency": 1 - obj.diffuse_color[3],
        }
        if tool.Ifc.get_schema() == "IFC2X3":
            del data["Transparency"]
        return data

    @classmethod
    def get_surface_shading_style(cls, obj):
        if obj.BIMMaterialProperties.ifc_style_id:
            style = tool.Ifc.get().by_id(obj.BIMMaterialProperties.ifc_style_id)
            items = [s for s in style.Styles if s.is_a() == "IfcSurfaceStyleShading"]
            if items:
                return items[0]

    @classmethod
    def get_surface_texture_style(cls, obj):
        if obj.BIMMaterialProperties.ifc_style_id:
            style = tool.Ifc.get().by_id(obj.BIMMaterialProperties.ifc_style_id)
            items = [s for s in style.Styles if s.is_a("IfcSurfaceStyleWithTextures")]
            if items:
                return items[0]

    @classmethod
    def get_uv_maps(cls, representation):
        items = []
        for item in representation.Items:
            if item.is_a("IfcMappedItem"):
                items.extend(item.MappingSource.MappedRepresentation.Items)
            items.append(item)

        results = []
        for item in items:
            for uv_map in item.HasTextures or []:
                results.append(uv_map)
        return results

    @classmethod
    def import_presentation_styles(cls, style_type):
        props = bpy.context.scene.BIMStylesProperties
        props.styles.clear()
        styles = sorted(tool.Ifc.get().by_type(style_type), key=lambda x: x.Name or "Unnamed")
        for style in styles:
            new = props.styles.add()
            new.ifc_definition_id = style.id()
            new.name = style.Name or "Unnamed"
            new.total_elements = len(ifcopenshell.util.element.get_elements_by_style(tool.Ifc.get(), style))

    @classmethod
    def import_surface_attributes(cls, style, obj):
        obj.BIMStyleProperties.attributes.clear()
        blenderbim.bim.helper.import_attributes2(style, obj.BIMStyleProperties.attributes)

    @classmethod
    def is_editing_styles(cls):
        return bpy.context.scene.BIMStylesProperties.is_editing

    @classmethod
    def select_elements(cls, elements):
        for element in elements:
            obj = tool.Ifc.get_object(element)
            if obj:
                obj.select_set(True)
