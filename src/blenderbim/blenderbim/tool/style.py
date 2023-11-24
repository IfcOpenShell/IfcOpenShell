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
import numpy as np
import ifcopenshell
import blenderbim.core.tool
import blenderbim.tool as tool
import blenderbim.bim.helper
import os.path

# fmt: off
TEXTURE_MAPS_BY_METHODS = {
    "PHYSICAL": ("NORMAL", "EMISSIVE", "METALLICROUGHNESS", "DIFFUSE", "OCCLUSION"),
    "FLAT": ("EMISSIVE",)
}
# fmt: on

STYLE_PROPS_MAP = {
    "reflectance_method": "ReflectanceMethod",
    "diffuse_color": "DiffuseColour",
    "surface_color": "SurfaceColour",
    "transparency": "Transparency",
    "roughness": "SpecularHighlight",
    "metallic": "SpecularColour",
}

STYLE_TEXTURE_PROPS_MAP = {
    "EMISSIVE": "emissive_path",
    "NORMAL": "normal_path",
    "METALLICROUGHNESS": "metallic_roughness_path",
    "DIFFUSE": "diffuse_path",
    "OCCLUSION": "occlusion_path",
}


class Style(blenderbim.core.tool.Style):
    @classmethod
    def can_support_rendering_style(cls, obj):
        return obj.use_nodes and hasattr(obj.node_tree, "nodes")

    @classmethod
    def disable_editing(cls, obj):
        obj.BIMStyleProperties.is_editing = False

    @classmethod
    def disable_editing_external_style(cls, obj):
        obj.BIMStyleProperties.is_editing_external_style = False

    @classmethod
    def disable_editing_styles(cls):
        bpy.context.scene.BIMStylesProperties.is_editing = False

    @classmethod
    def enable_editing(cls, obj):
        obj.BIMStyleProperties.is_editing = True

    @classmethod
    def enable_editing_external_style(cls, obj):
        obj.BIMStyleProperties.is_editing_external_style = True

    @classmethod
    def enable_editing_styles(cls):
        bpy.context.scene.BIMStylesProperties.is_editing = True

    @classmethod
    def export_surface_attributes(cls, obj):
        return blenderbim.bim.helper.export_attributes(obj.BIMStyleProperties.attributes)

    @classmethod
    def export_external_style_attributes(cls, obj):
        return blenderbim.bim.helper.export_attributes(obj.BIMStyleProperties.external_style_attributes)

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
    def get_style_elements(cls, blender_material):
        if not blender_material.BIMMaterialProperties.ifc_style_id:
            return {}
        style = tool.Ifc.get().by_id(blender_material.BIMMaterialProperties.ifc_style_id)
        style_elements = {}
        for style in style.Styles:
            style_elements[style.is_a()] = style
        return style_elements

    @classmethod
    def get_surface_style_from_props(cls, blender_material):
        """convert blender style props to ifc props"""
        surface_style_data = dict()
        props = blender_material.BIMStyleProperties
        for prop_blender, prop_ifc in STYLE_PROPS_MAP.items():
            surface_style_data[prop_ifc] = getattr(props, prop_blender)
        if surface_style_data["ReflectanceMethod"] == "PHYSICAL" and tool.Ifc.get_schema() != "IFC4X3":
            surface_style_data["ReflectanceMethod"] = "NOTDEFINED"
        surface_style_data["DiffuseColour"] = ("IfcColourRgb", surface_style_data["DiffuseColour"])
        return surface_style_data

    @classmethod
    def get_texture_style_from_props(cls, blender_material):
        props = blender_material.BIMStyleProperties

        textures = []
        texture_maps = TEXTURE_MAPS_BY_METHODS[props.reflectance_method]
        for prop_mode in texture_maps:
            prop_name = STYLE_TEXTURE_PROPS_MAP[prop_mode]
            path = getattr(props, prop_name)
            if not path:
                continue
            texture_data = {
                "Mode": prop_mode,
                "type": "IfcImageTexture",
                "URLReference": tool.Blender.blender_path_to_posix(path),
            }
            textures.append(texture_data)

        return textures

    @classmethod
    def set_surface_style_props(cls, blender_material):
        """set blender style props based on current surface material"""
        props = blender_material.BIMStyleProperties
        # make sure won't be updating while we changing it
        prev_update_graph_value = props.update_graph
        props["update_graph"] = False

        style_elements = tool.Style.get_style_elements(blender_material)
        surface_style = style_elements.get("IfcSurfaceStyleRendering", None)
        texture_style = style_elements.get("IfcSurfaceStyleWithTextures", None)

        # in case we have just IfcSurfaceStyleShading
        if not surface_style:
            return

        style_data = tool.Loader.surface_style_to_dict(surface_style)
        if style_data["ReflectanceMethod"] == "NOTDEFINED":
            style_data["ReflectanceMethod"] = "PHYSICAL"
        diffuse_color = style_data["DiffuseColour"]
        style_data["DiffuseColour"] = diffuse_color[1] if diffuse_color else None

        for prop_blender, prop_ifc in STYLE_PROPS_MAP.items():
            prop_value = style_data[prop_ifc]
            if prop_value is None:
                prop_value = tool.Blender.get_blender_prop_default_value(props, prop_blender)
            setattr(props, prop_blender, prop_value)

        texture_maps = TEXTURE_MAPS_BY_METHODS[style_data["ReflectanceMethod"]]
        unused_texture_maps = list(STYLE_TEXTURE_PROPS_MAP.keys())

        if texture_style:
            for texture in texture_style.Textures:
                if texture.Mode not in texture_maps:
                    print(f"WARNING. Unsupported texture mode: {texture.Mode}. Supported maps: {texture_maps}")
                    continue
                prop_blender = STYLE_TEXTURE_PROPS_MAP.get(texture.Mode, None)
                setattr(props, prop_blender, texture.URLReference)
                unused_texture_maps.remove(texture.Mode)

        # clear empty texture fields
        for texture_mode in unused_texture_maps:
            prop_blender = STYLE_TEXTURE_PROPS_MAP[texture_mode]
            setattr(props, prop_blender, "")

        props["update_graph"] = prev_update_graph_value

    @classmethod
    def get_surface_rendering_attributes(cls, obj, verbose=False):
        report = (lambda *x: print(*x)) if verbose else (lambda *x: None)

        def color_to_ifc_format(color):
            return {
                "Name": None,
                "Red": color[0],
                "Green": color[1],
                "Blue": color[2],
            }

        def get_input_node(node, input_name=None, of_type=None, input_index=None):
            input_pin = node.inputs[input_name] if input_index is None else node.inputs[input_index]
            if of_type:
                return next((l.from_node for l in input_pin.links if l.from_node.type == of_type), None)
            return next((l.from_node for l in input_pin.links), None)

        props = obj.BIMStyleProperties
        transparency = 1 - obj.diffuse_color[3]
        diffuse_color = obj.diffuse_color
        viewport_color = color_to_ifc_format(obj.diffuse_color)
        attributes = {
            "SurfaceColour": viewport_color,
            "Transparency": transparency,
        }
        GREEN = "\033[32m"
        BLUE = "\033[1;34m"
        R = "\033[0m"  # RESET symbol

        report("--------------------")
        report("Verbose method of getting surface rendering attributes enabled.")
        report("If some attribute is not mentioned below, then it won't be saved to IFC.")
        report("--------------------")
        report(f"{GREEN}Viewport color{R} saved as {GREEN}SurfaceColour{R}")

        # TODO: make sure bsdf is connected to the output?
        bsdfs = {n.type: n for n in obj.node_tree.nodes if n.outputs and n.outputs[0].is_linked}
        if "BSDF_PRINCIPLED" not in bsdfs:
            report(f"{GREEN}Viewport color alpha{R} saved as {GREEN}Transparency{R}")

        # TODO: should escape referring to pins by their name to support different languages
        material_output = tool.Blender.get_material_node(obj, "OUTPUT_MATERIAL", {"is_active_output": True})
        surface_output = get_input_node(material_output, "Surface")

        if surface_output and surface_output.type == "MIX_SHADER":
            mix_shader = surface_output
            if (
                get_input_node(mix_shader, "Fac", "LIGHT_PATH")
                and get_input_node(mix_shader, input_index=1, of_type="BSDF_TRANSPARENT")
                and (second_input_node := get_input_node(mix_shader, input_index=2))
                and second_input_node.type in ("RGB", "TEX_IMAGE")
            ):
                report(
                    f"Because of {BLUE}MIX_SHADER + LIGHT_PATH + BSDF_TRANSPARENT + RGB/TEX{R} node setup reflectance method identified as {BLUE}FLAT{R}"
                )
                attributes["ReflectanceMethod"] = "FLAT"
                attributes["SpecularHighlight"] = None

                if second_input_node.type == "RGB":
                    report(f"RGB {GREEN}Color{R} saved as {GREEN}DiffuseColour{R}")
                    diffuse_color = second_input_node.outputs[0].default_value
                elif second_input_node.type == "TEX_IMAGE":
                    report(f"{GREEN}BBIM Panel Diffuse Color{R} saved as {GREEN}DiffuseColour{R}")
                    diffuse_color = props.diffuse_color

        elif surface_output and (
            (surface_output.type == "BSDF_PRINCIPLED" and (bsdf := surface_output))
            or (
                surface_output.type == "ADD_SHADER"
                and (bsdf := get_input_node(surface_output, input_index=1, of_type="BSDF_PRINCIPLED"))
            )
        ):
            report(f"Because of {BLUE}BSDF_PRINCIPLED{R} node reflectance method identified as {BLUE}PHYSICAL{R}")
            attributes["ReflectanceMethod"] = "NOTDEFINED" if tool.Ifc.get_schema() != "IFC4X3" else "PHYSICAL"

            report(f"BSDF {GREEN}Base Color{R} saved as {GREEN}DiffuseColour{R}")
            diffuse_color = bsdf.inputs["Base Color"].default_value

            report(f"BSDF {GREEN}Metallic{R} saved as {GREEN}SpecularColour{R}")
            attributes["SpecularColour"] = round(bsdf.inputs["Metallic"].default_value, 3)

            report(f"BSDF {GREEN}Roughness{R} saved as {GREEN}IfcSpecularRoughness{R}")
            attributes["SpecularHighlight"] = {"IfcSpecularRoughness": round(bsdf.inputs["Roughness"].default_value, 3)}

            report(f"BSDF {GREEN}Alpha{R} saved as {GREEN}Transparency{R}")
            attributes["Transparency"] = 1 - bsdf.inputs["Alpha"].default_value

        elif "BSDF_GLOSSY" in bsdfs:
            attributes["ReflectanceMethod"] = "METAL"
            report(f"Because of {BLUE}BSDF_GLOSSY{R} node reflectance method identified as {BLUE}METAL{R}")
            bsdf = bsdfs["BSDF_GLOSSY"]

            report(f"BSDF {GREEN}Roughness{R} saved as {GREEN}IfcSpecularRoughness{R}")
            attributes["SpecularHighlight"] = {"IfcSpecularRoughness": round(bsdf.inputs["Roughness"].default_value, 3)}

            report(f"BSDF {GREEN}Color{R} saved as {GREEN}DiffuseColour{R}")
            diffuse_color = bsdf.inputs["Color"].default_value

        elif "BSDF_DIFFUSE" in bsdfs:
            report(f"Because of {BLUE}BSDF_DIFFUSE{R} node reflectance method identified as {BLUE}MATT{R}")
            attributes["ReflectanceMethod"] = "MATT"
            bsdf = bsdfs["BSDF_DIFFUSE"]

            report(f"BSDF {GREEN}Roughness{R} saved as {GREEN}IfcSpecularRoughness{R}")
            attributes["SpecularHighlight"] = {"IfcSpecularRoughness": round(bsdf.inputs["Roughness"].default_value, 3)}

            report(f"BSDF {GREEN}Color{R} saved as {GREEN}DiffuseColour{R}")
            diffuse_color = bsdf.inputs["Color"].default_value

        elif "BSDF_GLASS" in bsdfs:
            report(f"Because of {BLUE}BSDF_GLASS{R} node reflectance method identified as {BLUE}GLASS{R}")
            attributes["ReflectanceMethod"] = "GLASS"
            bsdf = bsdfs["BSDF_GLASS"]

            report(f"BSDF {GREEN}Roughness{R} saved as {GREEN}IfcSpecularRoughness{R}")
            attributes["SpecularHighlight"] = {"IfcSpecularRoughness": round(bsdf.inputs["Roughness"].default_value, 3)}

            report(f"BSDF {GREEN}Color{R} saved as {GREEN}DiffuseColour{R}")
            diffuse_color = bsdf.inputs["Color"].default_value

        # TODO: remove?
        elif "EMISSION" in bsdfs:
            report(f"Because of {BLUE}EMISSION{R} node reflectance method identified as {BLUE}FLAT{R}")
            attributes["ReflectanceMethod"] = "FLAT"
            bsdf = bsdfs["EMISSION"]

            attributes["SpecularHighlight"] = None
            report(f"BSDF {GREEN}Color{R} saved as {GREEN}DiffuseColour{R}")

            diffuse_color = bsdf.inputs["Color"].default_value

        # TODO: remove?
        elif "BSDF_PRINCIPLED" in bsdfs:
            report(f"Because of {BLUE}BSDF_PRINCIPLED{R} node reflectance method identified as {BLUE}PHYSICAL{R}")
            attributes["ReflectanceMethod"] = "NOTDEFINED" if tool.Ifc.get_schema() != "IFC4X3" else "PHYSICAL"
            bsdf = bsdfs["BSDF_PRINCIPLED"]

            report(f"BSDF {GREEN}Base Color{R} saved as {GREEN}DiffuseColour{R}")
            diffuse_color = bsdf.inputs["Base Color"].default_value

            report(f"BSDF {GREEN}Metallic{R} saved as {GREEN}SpecularColour{R}")
            attributes["SpecularColour"] = round(bsdf.inputs["Metallic"].default_value, 3)

            report(f"BSDF {GREEN}Roughness{R} saved as {GREEN}IfcSpecularRoughness{R}")
            attributes["SpecularHighlight"] = {"IfcSpecularRoughness": round(bsdf.inputs["Roughness"].default_value, 3)}

            report(f"BSDF {GREEN}Alpha{R} saved as {GREEN}Transparency{R}")
            attributes["Transparency"] = 1 - bsdf.inputs["Alpha"].default_value

        else:
            report(f"No supported bsdfs found - reflectance method identified as {BLUE}NOTDEFINED{R}")
            attributes["ReflectanceMethod"] = "NOTDEFINED"

            attributes["SpecularHighlight"] = None
            report(f"{GREEN}Viewport color{R} saved as {GREEN}DiffuseColour{R}")
            attributes["DiffuseColour"] = viewport_color
            return attributes

        attributes["DiffuseColour"] = color_to_ifc_format(diffuse_color)
        return attributes

    @classmethod
    def get_surface_rendering_style(cls, obj):
        style_elements = cls.get_style_elements(obj)
        return style_elements.get("IfcSurfaceStyleRendering", None)

    @classmethod
    def get_texture_style(cls, obj):
        style_elements = cls.get_style_elements(obj)
        return style_elements.get("IfcSurfaceStyleWithTextures", None)

    @classmethod
    def get_external_style(cls, obj):
        style_elements = cls.get_style_elements(obj)
        return style_elements.get("IfcExternallyDefinedSurfaceStyle", None)

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
            # only IfcTessellatedFaceSet has HasTextures
            for uv_map in getattr(item, "HasTextures", None) or []:
                results.append(uv_map)
        return results

    @classmethod
    def import_presentation_styles(cls, style_type):
        color_to_tuple = lambda x: (x.Red, x.Green, x.Blue)
        props = bpy.context.scene.BIMStylesProperties
        props.styles.clear()
        styles = sorted(tool.Ifc.get().by_type(style_type), key=lambda x: x.Name or "Unnamed")
        for style in styles:
            new = props.styles.add()
            new.ifc_definition_id = style.id()
            new.name = style.Name or "Unnamed"
            new.ifc_class = style.is_a()
            for surface_style in getattr(style, "Styles", []) or []:
                new2 = new.style_classes.add()
                new2.name = surface_style.is_a()
                if surface_style.is_a("IfcSurfaceStyleShading"):
                    new.has_surface_colour = True
                    new.surface_colour = color_to_tuple(surface_style.SurfaceColour)
                if surface_style.is_a("IfcSurfaceStyleRendering"):
                    if surface_style.DiffuseColour and surface_style.DiffuseColour.is_a("IfcColourRgb"):
                        new.has_diffuse_colour = True
                        new.diffuse_colour = color_to_tuple(surface_style.DiffuseColour)
            new.total_elements = len(ifcopenshell.util.element.get_elements_by_style(tool.Ifc.get(), style))

    @classmethod
    def import_surface_attributes(cls, style, obj):
        attributes = obj.BIMStyleProperties.attributes
        attributes.clear()
        blenderbim.bim.helper.import_attributes2(style, attributes)

    @classmethod
    def import_external_style_attributes(cls, style, obj):
        attributes = obj.BIMStyleProperties.external_style_attributes
        attributes.clear()
        blenderbim.bim.helper.import_attributes2(style, attributes)

    @classmethod
    def has_blender_external_style(cls, style_elements):
        external_style = style_elements.get("IfcExternallyDefinedSurfaceStyle", None)
        return bool(external_style and external_style.Location.endswith(".blend"))

    @classmethod
    def is_editing_styles(cls):
        return bpy.context.scene.BIMStylesProperties.is_editing

    @classmethod
    def record_shading(cls, obj):
        obj.BIMMaterialProperties.shading_checksum = repr(np.array(obj.diffuse_color).tobytes())

    @classmethod
    def select_elements(cls, elements):
        for element in elements:
            obj = tool.Ifc.get_object(element)
            if obj:
                obj.select_set(True)

    @classmethod
    def change_current_style_type(cls, blender_material, style_type):
        blender_material.BIMStyleProperties.active_style_type = style_type
