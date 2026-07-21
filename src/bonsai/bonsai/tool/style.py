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

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, Any, Literal, Optional, Union

import bpy
import ifcopenshell
import ifcopenshell.api.style
import ifcopenshell.util.element
import ifcopenshell.util.representation
from mathutils import Color

import bonsai.bim.helper
import bonsai.core.style
import bonsai.core.tool
import bonsai.tool as tool

if TYPE_CHECKING:
    from bonsai.bim.module.style.prop import (
        BIMStyleProperties,
        BIMStylesProperties,
        ColourRgb,
    )
    from bonsai.bim.prop import Attribute

# fmt: off
TEXTURE_MAPS_BY_METHODS = {
    "PHYSICAL": ("NORMAL", "EMISSIVE", "METALLICROUGHNESS", "DIFFUSE", "OCCLUSION"),
    "FLAT": ("EMISSIVE",)
}
# fmt: on

STYLE_PROPS_MAP = {
    "reflectance_method": "ReflectanceMethod",
    "diffuse_colour": "DiffuseColour",
    "surface_colour": "SurfaceColour",
    "transparency": "Transparency",
    "specular_highlight": "SpecularHighlight",
    "specular_colour": "SpecularColour",
}


class Style(bonsai.core.tool.Style):
    StyleType = Literal["Shading", "External"]

    @classmethod
    def get_style_props(cls) -> BIMStylesProperties:
        return bpy.context.scene.BIMStylesProperties

    @classmethod
    def get_material_style_props(cls, material: bpy.types.Material) -> BIMStyleProperties:
        return material.BIMStyleProperties

    @classmethod
    def get_use_nodes(cls, obj: bpy.types.Material) -> bool:
        """Since Blender 5.0 ``use_nodes`` are always ``True`` and considered deprecated."""
        if tool.Blender.BLENDER_5:
            return True
        return obj.use_nodes

    @classmethod
    def set_use_nodes(cls, obj: bpy.types.Material, use_nodes: bool) -> None:
        """Since Blender 5.0 ``use_nodes`` are always ``True`` and considered deprecated."""
        if tool.Blender.BLENDER_5:
            return
        obj.use_nodes = use_nodes

    @classmethod
    def can_support_rendering_style(cls, obj: bpy.types.Material) -> bool:
        return tool.Blender.BLENDER_5 or (obj.use_nodes and hasattr(obj.node_tree, "nodes"))

    @classmethod
    def delete_object(cls, obj: bpy.types.Material) -> None:
        tool.Blender.remove_data_block(obj)

    @classmethod
    def enable_adding_presentation_style(cls) -> None:
        props = tool.Style.get_style_props()
        props.is_adding = True
        props.update_graph = False

    @classmethod
    def disable_adding_presentation_style(cls) -> None:
        props = tool.Style.get_style_props()
        props.is_adding = False
        props.update_graph = True

    @classmethod
    def disable_editing(cls) -> None:
        props = tool.Style.get_style_props()
        props.is_editing_style = 0
        props.is_editing_class = ""
        props.attributes.clear()
        props.external_style_attributes.clear()
        props.refraction_style_attributes.clear()
        props.lighting_style_colours.clear()
        props.textures.clear()

    @classmethod
    def disable_editing_styles(cls) -> None:
        props = tool.Style.get_style_props()
        props.is_editing = False
        props.styles.clear()

    @classmethod
    def duplicate_style(cls, style: ifcopenshell.entity_instance) -> ifcopenshell.entity_instance:
        new_style = ifcopenshell.util.element.copy_deep(tool.Ifc.get(), style)
        name = (style.Name or "Unnamed") + "_copy"
        new_style.Name = name

        blender_material = tool.Ifc.get_object(style).copy()
        blender_material.use_fake_user = True
        blender_material.name = name
        tool.Ifc.link(new_style, blender_material)

        return new_style

    @classmethod
    def enable_editing(cls, style: ifcopenshell.entity_instance) -> None:
        props = tool.Style.get_style_props()
        props.is_editing_style = style.id()
        props.is_editing_class = "IfcSurfaceStyle"

    @classmethod
    def enable_editing_styles(cls) -> None:
        props = cls.get_style_props()
        props.is_editing = True

    @classmethod
    def export_surface_attributes(cls) -> dict[str, Any]:
        props = cls.get_style_props()
        return bonsai.bim.helper.export_attributes(props.attributes)

    @classmethod
    def get_active_style_in_ui(cls) -> Union[bpy.types.PropertyGroup, None]:
        props = cls.get_style_props()
        return props.active_style

    @classmethod
    def get_active_style_type(cls) -> str:
        props = cls.get_style_props()
        return props.style_type

    @classmethod
    def get_context(cls) -> Union[ifcopenshell.entity_instance, None]:
        return ifcopenshell.util.representation.get_context(tool.Ifc.get(), "Model", "Body", "MODEL_VIEW")

    @classmethod
    def get_elements_by_style(cls, style: ifcopenshell.entity_instance) -> list[ifcopenshell.entity_instance]:
        return ifcopenshell.util.element.get_elements_by_style(tool.Ifc.get(), style)

    @classmethod
    def get_name(cls, obj: bpy.types.Material) -> str:
        return obj.name

    @classmethod
    def get_currently_edited_material(cls) -> bpy.types.Material:
        props = tool.Style.get_style_props()
        style = tool.Ifc.get().by_id(props.is_editing_style)
        obj = tool.Ifc.get_object(style)
        assert isinstance(obj, bpy.types.Material)
        return obj

    @classmethod
    def get_style_elements(
        cls, blender_material_or_style: Union[bpy.types.Material, ifcopenshell.entity_instance]
    ) -> dict[str, ifcopenshell.entity_instance]:
        if isinstance(blender_material_or_style, bpy.types.Material):
            style = tool.Ifc.get_entity(blender_material_or_style)
            if not style:
                return {}
        else:
            style = blender_material_or_style
        style_elements = {}
        for style_ in style.Styles:
            style_elements[style_.is_a()] = style_
        return style_elements

    @classmethod
    def get_shading_style_data_from_props(cls) -> dict[str, Any]:
        """returns style data from blender props in similar way to `Loader.surface_style_to_dict`
        to be compatible with `Loader.create_surface_style_rendering`"""
        surface_style_data = dict()
        props = tool.Style.get_style_props()

        available_props = props.bl_rna.properties.keys()
        for prop_blender, prop_ifc in STYLE_PROPS_MAP.items():
            null_prop_name = f"is_{prop_blender}_null"
            if null_prop_name in available_props and getattr(props, null_prop_name):
                surface_style_data[prop_ifc] = None
                continue

            class_prop_name = f"{prop_blender}_class"

            # get detailed color properties if available
            if class_prop_name in available_props:
                prop_class = getattr(props, class_prop_name)
                if prop_class == "IfcColourRgb":
                    prop_value = tuple(getattr(props, prop_blender))
                else:  # IfcNormalisedRatioMeasure
                    ratio_prop_name = f"{prop_blender}_ratio"
                    prop_value = getattr(props, ratio_prop_name)
                prop_value = (prop_class, prop_value)
            else:
                prop_value = getattr(props, prop_blender)
                if isinstance(prop_value, Color):
                    prop_value = tuple(prop_value)

            surface_style_data[prop_ifc] = prop_value
        return surface_style_data

    @classmethod
    def get_texture_style_data_from_props(cls) -> list[dict[str, Any]]:
        """returns style data from blender props in similar way to `Loader.surface_texture_to_dict`
        to be compatible with `Loader.create_surface_style_with_textures`"""
        props = tool.Style.get_style_props()

        textures = []
        for texture in props.textures:
            if not texture.path:
                continue
            texture_data = {
                "Mode": texture.mode,
                "type": "IfcImageTexture",
                "URLReference": texture.path,
                "uv_mode": props.uv_mode,
            }
            textures.append(texture_data)

        return textures

    @classmethod
    def set_surface_style_props(cls) -> None:
        """set blender style props based on currently edited IfcSurfaceStyle,
        reset unrelated props to default values"""

        props = tool.Style.get_style_props()
        style = tool.Ifc.get().by_id(props.is_editing_style)
        # make sure won't be updating while we changing it
        prev_update_graph_value = props.update_graph
        props["update_graph"] = False

        style_elements = tool.Style.get_style_elements(style)
        surface_style = style_elements.get("IfcSurfaceStyleRendering", None)
        if surface_style is None:
            surface_style = style_elements.get("IfcSurfaceStyleShading", None)
        style_data = tool.Loader.surface_style_to_dict(surface_style) if surface_style else {}
        texture_style = style_elements.get("IfcSurfaceStyleWithTextures", None)

        def set_prop(prop_blender, prop_value):
            if prop_value is None:
                prop_value = tool.Blender.get_blender_prop_default_value(props, prop_blender)
            setattr(props, prop_blender, prop_value)

        available_props = props.bl_rna.properties.keys()
        # fallback value for reflectance method
        if style_data.get("ReflectanceMethod", None) is None:
            style_data["ReflectanceMethod"] = "NOTDEFINED"
        for prop_blender, prop_ifc in STYLE_PROPS_MAP.items():
            prop_value = style_data.get(prop_ifc, None)
            is_null = prop_value is None

            # set null property if available
            null_prop_name = f"is_{prop_blender}_null"
            if null_prop_name in available_props:
                set_prop(null_prop_name, is_null)

            # set detailed color properties if available
            class_prop_name = f"{prop_blender}_class"
            if class_prop_name in available_props:
                prop_class, prop_value = prop_value or (None, None)
                # set class enum
                set_prop(class_prop_name, prop_class)
                # set prop value
                ratio_prop_name = f"{prop_blender}_ratio"
                if prop_class == "IfcColourRgb":
                    set_prop(prop_blender, prop_value)
                    set_prop(ratio_prop_name, None)
                else:  # IfcNormalisedRatioMeasure
                    set_prop(ratio_prop_name, prop_value)
                    set_prop(prop_blender, None)
                continue

            set_prop(prop_blender, prop_value)

        uv_mode = None
        props.textures.clear()
        if texture_style:
            for texture in texture_style.Textures:
                # we use surface_texture_to_dict as it calculates uv_mode
                texture_data = tool.Loader.surface_texture_to_dict(texture)
                texture_prop = props.textures.add()
                texture_prop.mode = texture_data["Mode"]
                texture_prop.path = texture_data["URLReference"]
                uv_mode = texture_data["uv_mode"]
        props.uv_mode = uv_mode if uv_mode else "UV"
        props["update_graph"] = prev_update_graph_value

    @classmethod
    def get_surface_rendering_attributes(cls, obj: bpy.types.Material, verbose: bool = False) -> dict[str, Any]:
        report = (lambda *x: print(*x)) if verbose else (lambda *x: None)

        def color_to_ifc_format(color: Sequence[float]) -> dict[str, Any]:
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

        props = tool.Style.get_material_style_props(obj)
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
        assert obj.node_tree
        bsdfs = {n.type: n for n in obj.node_tree.nodes if n.outputs and n.outputs[0].is_linked}
        if "BSDF_PRINCIPLED" not in bsdfs:
            report(f"{GREEN}Viewport color alpha{R} saved as {GREEN}Transparency{R}")

        # TODO: should escape referring to pins by their name to support different languages
        material_output = tool.Blender.get_material_node(obj, "OUTPUT_MATERIAL", {"is_active_output": True})
        surface_output = get_input_node(material_output, "Surface")

        # TODO: this variable is not really needed,
        # just workaround a for ty issue detecting unresolved refs.
        bsdf = None

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
            assert bsdf
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

        elif "BSDF_DIFFUSE" in bsdfs or "DIFFUSE_BSDF" in bsdfs:
            report(f"Because of {BLUE}BSDF_DIFFUSE{R} node reflectance method identified as {BLUE}MATT{R}")
            attributes["ReflectanceMethod"] = "MATT"
            bsdf = bsdfs["BSDF_DIFFUSE"] if "BSDF_DIFFUSE" in bsdfs else bsdfs["DIFFUSE_BSDF"]

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
    def get_surface_rendering_style(
        cls, blender_material_or_style: Union[bpy.types.Material, ifcopenshell.entity_instance]
    ) -> Union[ifcopenshell.entity_instance, None]:
        style_elements = cls.get_style_elements(blender_material_or_style)
        return style_elements.get("IfcSurfaceStyleRendering", None)

    @classmethod
    def get_texture_style(
        cls, blender_material_or_style: Union[bpy.types.Material, ifcopenshell.entity_instance]
    ) -> Union[ifcopenshell.entity_instance, None]:
        style_elements = cls.get_style_elements(blender_material_or_style)
        return style_elements.get("IfcSurfaceStyleWithTextures", None)

    @classmethod
    def get_external_style(
        cls, blender_material_or_style: Union[bpy.types.Material, ifcopenshell.entity_instance]
    ) -> Union[ifcopenshell.entity_instance, None]:
        style_elements = cls.get_style_elements(blender_material_or_style)
        return style_elements.get("IfcExternallyDefinedSurfaceStyle", None)

    @classmethod
    def get_surface_shading_attributes(cls, obj: bpy.types.Material) -> dict[str, Any]:
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
    def get_surface_shading_style(cls, obj: bpy.types.Material) -> Union[ifcopenshell.entity_instance, None]:
        if style := tool.Ifc.get_entity(obj):
            items = [s for s in style.Styles if s.is_a() == "IfcSurfaceStyleShading"]
            if items:
                return items[0]

    @classmethod
    def get_surface_texture_style(cls, obj: bpy.types.Material) -> Union[ifcopenshell.entity_instance, None]:
        if style := tool.Ifc.get_entity(obj):
            items = [s for s in style.Styles if s.is_a("IfcSurfaceStyleWithTextures")]
            if items:
                return items[0]

    @classmethod
    def get_uv_maps(cls, representation: ifcopenshell.entity_instance) -> list[ifcopenshell.entity_instance]:
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
    def get_style_ui_props_attributes(cls, style_type: str) -> Union[
        bpy.types.bpy_prop_collection_idprop[Attribute],
        bpy.types.bpy_prop_collection_idprop[ColourRgb],
        None,
    ]:
        props = tool.Style.get_style_props()
        if style_type == "IfcExternallyDefinedSurfaceStyle":
            return props.external_style_attributes
        elif style_type == "IfcSurfaceStyleRefraction":
            return props.refraction_style_attributes
        elif style_type == "IfcSurfaceStyleLighting":
            return props.lighting_style_colours

    @classmethod
    def import_presentation_styles(cls, style_type: str) -> None:
        color_to_tuple = lambda x: (x.Red, x.Green, x.Blue)
        props = tool.Style.get_style_props()
        props.styles.clear()
        styles = sorted(tool.Ifc.get().by_type(style_type), key=lambda x: x.Name or "Unnamed")
        for style in styles:
            new = props.styles.add()
            new.ifc_definition_id = style.id()
            new.blender_material = tool.Ifc.get_object(style)
            new["name"] = style.Name or "Unnamed"  # Avoid writing to IFC through callback.
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
    def import_surface_attributes(cls, style: ifcopenshell.entity_instance) -> None:
        props = cls.get_style_props()
        attributes = props.attributes
        attributes.clear()
        bonsai.bim.helper.import_attributes(style, attributes)

    @classmethod
    def has_blender_external_style(cls, style_elements: dict[str, ifcopenshell.entity_instance]) -> bool:
        external_style = style_elements.get("IfcExternallyDefinedSurfaceStyle", None)
        return bool(external_style and external_style.Location and external_style.Location.endswith(".blend"))

    @classmethod
    def _color_from_principled(cls, node: bpy.types.Node) -> tuple[tuple[float, float, float], float]:
        color = cls._resolve_color_socket(node.inputs["Base Color"])
        alpha_socket = node.inputs["Alpha"]
        alpha_source = cls._upstream_color_source(alpha_socket)
        if alpha_source and alpha_source[0] == "IMAGE":
            pixels = alpha_source[1].pixels[:]
            n = len(pixels) // 4
            step = max(1, n // 4096)
            a_sum = sum(pixels[i * 4 + 3] for i in range(0, n, step))
            count = len(range(0, n, step)) or 1
            transparency = 1.0 - (a_sum / count)
        else:
            transparency = 1.0 - alpha_socket.default_value
        return color, transparency

    @classmethod
    def _color_from_shader_socket(
        cls, socket: bpy.types.NodeSocket, seen: set[str] | None = None
    ) -> tuple[tuple[float, float, float], float] | None:
        if seen is None:
            seen = set()
        for link in socket.links:
            node = link.from_node
            if node.name in seen:
                continue
            seen.add(node.name)
            if node.type == "BSDF_PRINCIPLED":
                return cls._color_from_principled(node)
            if node.type in ("BSDF_DIFFUSE", "DIFFUSE_BSDF"):
                return cls._resolve_color_socket(node.inputs["Color"]), 0.0
            if node.type == "BSDF_GLASS":
                return cls._resolve_color_socket(node.inputs["Color"]), 0.0
            if node.type in ("MIX_SHADER", "ADD_SHADER"):
                for inp in node.inputs:
                    if inp.type == "SHADER" and inp.is_linked:
                        result = cls._color_from_shader_socket(inp, seen)
                        if result:
                            return result
        return None

    @classmethod
    def get_representative_material_color(
        cls, material: bpy.types.Material
    ) -> tuple[tuple[float, float, float], float]:
        if material.node_tree:
            nodes = material.node_tree.nodes
            output_node = next(
                (n for n in nodes if n.type == "OUTPUT_MATERIAL" and n.is_active_output), None
            ) or next((n for n in nodes if n.type == "OUTPUT_MATERIAL"), None)
            if output_node:
                result = cls._color_from_shader_socket(output_node.inputs["Surface"])
                if result:
                    return result
            # Fallback: scan all shader nodes if no output node or graph traversal found nothing
            for node in nodes:
                if node.type == "BSDF_PRINCIPLED":
                    return cls._color_from_principled(node)
            for node in nodes:
                if node.type in ("BSDF_DIFFUSE", "DIFFUSE_BSDF"):
                    return cls._resolve_color_socket(node.inputs["Color"]), 0.0
            for node in nodes:
                if node.type == "BSDF_GLASS":
                    return cls._resolve_color_socket(node.inputs["Color"]), 0.0
        color = tuple(material.diffuse_color[:3])
        transparency = 1.0 - material.diffuse_color[3]
        return color, transparency

    @classmethod
    def _collect_upstream_sources(cls, socket: bpy.types.NodeSocket, seen: set[str]) -> list[tuple[str, object]]:
        """Recursively collect all upstream colour/image sources reachable from *socket*."""
        results = []
        for link in socket.links:
            node = link.from_node
            if node.name in seen:
                continue
            seen.add(node.name)
            if node.type == "TEX_IMAGE":
                results.append(("IMAGE", node.image))
            elif node.type == "VALTORGB":
                results.append(("COLORRAMP", node))
            else:
                for inp in node.inputs:
                    if inp.is_linked:
                        results.extend(cls._collect_upstream_sources(inp, seen))
        return results

    @classmethod
    def _upstream_color_source(
        cls, socket: bpy.types.NodeSocket, seen: set[str] | None = None
    ) -> tuple[str, object] | None:
        sources = cls._collect_upstream_sources(socket, set() if seen is None else seen)
        # Prefer a concrete image texture over a colour ramp (which may be greyscale/procedural).
        for s in sources:
            if s[0] == "IMAGE":
                return s
        for s in sources:
            if s[0] == "COLORRAMP":
                return s
        return None

    @classmethod
    def _resolve_color_socket(cls, socket: bpy.types.NodeSocket) -> tuple[float, float, float]:
        source = cls._upstream_color_source(socket)
        if source is None:
            return tuple(socket.default_value[:3])
        kind, obj = source
        if kind == "IMAGE":
            return cls._average_image_color(obj)
        if kind == "COLORRAMP":
            return cls._average_colorramp_color(obj)
        return tuple(socket.default_value[:3])

    @staticmethod
    def _average_image_color(image: bpy.types.Image) -> tuple[float, float, float]:
        pixels = image.pixels[:]
        n = len(pixels) // 4
        if n == 0:
            return (0.5, 0.5, 0.5)
        step = max(1, n // 4096)
        r_sum = g_sum = b_sum = 0.0
        count = 0
        for i in range(0, n, step):
            base = i * 4
            r_sum += pixels[base]
            g_sum += pixels[base + 1]
            b_sum += pixels[base + 2]
            count += 1
        return (r_sum / count, g_sum / count, b_sum / count)

    @staticmethod
    def _average_colorramp_color(node: bpy.types.Node) -> tuple[float, float, float]:
        elements = node.color_ramp.elements
        if not elements:
            return (0.5, 0.5, 0.5)
        r = sum(e.color[0] for e in elements) / len(elements)
        g = sum(e.color[1] for e in elements) / len(elements)
        b = sum(e.color[2] for e in elements) / len(elements)
        return (r, g, b)

    @classmethod
    def is_editing_styles(cls) -> bool:
        props = cls.get_style_props()
        return props.is_editing

    @classmethod
    def is_editing_style(cls) -> bool:
        props = cls.get_style_props()
        return bool(props.is_editing_style)

    @classmethod
    def select_elements(cls, elements: list[ifcopenshell.entity_instance]) -> None:
        for element in elements:
            obj = tool.Ifc.get_object(element)
            if obj:
                obj.select_set(True)

    @classmethod
    def change_current_style_type(cls, blender_material: bpy.types.Material, style_type: str) -> None:
        props = cls.get_material_style_props(blender_material)
        props.active_style_type = style_type

    @classmethod
    def get_styled_items(cls, style: ifcopenshell.entity_instance) -> list[ifcopenshell.entity_instance]:
        ifc_file = tool.Ifc.get()

        inverses = list(ifc_file.get_inverse(style))
        items = []
        while inverses:
            inverse = inverses.pop()
            if inverse.is_a("IfcPresentationStyleAssignment"):
                inverses.extend(ifc_file.get_inverse(inverse))
                continue

            if not (item := inverse.Item):
                continue

            if item.is_a("IfcMappedItem"):
                items.extend(item.MappingSource.MappedRepresentation.Items)
            else:
                items.append(item)
        return items

    @classmethod
    def assign_style_to_object(cls, style: ifcopenshell.entity_instance, obj: bpy.types.Object) -> None:
        """assigns `style` to `object` current representation"""
        representation = tool.Geometry.get_active_representation(obj)
        assert representation
        ifcopenshell.api.style.assign_representation_styles(
            tool.Ifc.get(), shape_representation=representation, styles=[style]
        )

    @classmethod
    def assign_style_to_representation_item(
        cls, item: ifcopenshell.entity_instance, style: Optional[ifcopenshell.entity_instance] = None
    ) -> None:
        return ifcopenshell.api.style.assign_item_style(tool.Ifc.get(), item=item, style=style)

    @classmethod
    def get_representation_item_style(
        cls, representation_item: ifcopenshell.entity_instance
    ) -> Union[ifcopenshell.entity_instance, None]:
        """Return IfcPresentationStyle associated with a representation item."""
        is_4x3 = representation_item.file.schema == "IFC4X3"
        for style in representation_item.StyledByItem:
            for style_or_assignment in style.Styles:
                if not is_4x3 and style_or_assignment.is_a("IfcPresentationStyleAssignment"):
                    for assignment_style in style_or_assignment.Styles:
                        return assignment_style
                else:  # IfcPresentationStyle
                    return style_or_assignment

    @classmethod
    def reload_material_from_ifc(cls, blender_material: bpy.types.Material) -> None:
        props = cls.get_material_style_props(blender_material)
        props.active_style_type = props.active_style_type

    @classmethod
    def get_branch_outputs(
        cls, material: bpy.types.Material
    ) -> tuple[bpy.types.ShaderNode | None, bpy.types.ShaderNode | None]:
        """Return (external_output_node, flat_output_node), or (None, None) if not dual-branch."""
        if not material.node_tree:
            return None, None
        ext = material.node_tree.nodes.get("BIM_Output_External")
        fast = material.node_tree.nodes.get("BIM_Output_Flat")
        return ext, fast

    @classmethod
    def _remove_external_branch(cls, material: bpy.types.Material) -> None:
        """Remove all nodes reachable from BIM_Output_External (walks links backwards)."""
        if not material.node_tree:
            return
        nodes = material.node_tree.nodes
        output = nodes.get("BIM_Output_External")
        if not output:
            return
        to_remove: set[str] = set()
        stack = [output]
        while stack:
            node = stack.pop()
            if node.name in to_remove:
                continue
            to_remove.add(node.name)
            for inp in node.inputs:
                for link in inp.links:
                    stack.append(link.from_node)
        for name in list(to_remove):
            n = nodes.get(name)
            if n:
                nodes.remove(n)

    @classmethod
    def _build_flat_branch_nodes(cls, material: bpy.types.Material) -> bpy.types.ShaderNode:
        """Add a Principled BSDF flat-branch to material's existing node tree.

        Reads IfcSurfaceStyleRendering or IfcSurfaceStyleShading from the linked IFC entity.
        Defaults to a white BSDF when no IFC shading data is available.
        Returns the new Material Output node (named BIM_Output_Flat, is_active_output=False).
        """
        from mathutils import Vector

        style_elements = cls.get_style_elements(material)
        nodes = material.node_tree.nodes
        links = material.node_tree.links

        bsdf = nodes.new("ShaderNodeBsdfPrincipled")
        bsdf.location = Vector((10, -600))
        output = nodes.new("ShaderNodeOutputMaterial")
        output.name = "BIM_Output_Flat"
        output.location = Vector((300, -600))
        output.is_active_output = False
        links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])

        rendering_style = None
        shading_only = None
        for surface_style in style_elements.values():
            if surface_style.is_a() == "IfcSurfaceStyleShading":
                shading_only = surface_style
            elif surface_style.is_a("IfcSurfaceStyleRendering"):
                rendering_style = surface_style
                shading_only = None

        if rendering_style:
            d = tool.Loader.surface_style_to_dict(rendering_style)
            if d.get("DiffuseColour"):
                ctype, cval = d["DiffuseColour"]
                if ctype == "IfcColourRgb":
                    bsdf.inputs["Base Color"].default_value = cval + (1,)
                    solid_color = cval
                else:
                    cval = tuple(v * cval for v in d["SurfaceColour"])
                    bsdf.inputs["Base Color"].default_value = cval + (1,)
                    solid_color = cval
            else:
                r, g, b = d["SurfaceColour"]
                bsdf.inputs["Base Color"].default_value = (r, g, b, 1.0)
                solid_color = (r, g, b)
            if d.get("SpecularColour"):
                ctype, cval = d["SpecularColour"]
                if ctype == "IfcNormalisedRatioMeasure":
                    bsdf.inputs["Metallic"].default_value = cval
            if d.get("SpecularHighlight"):
                bsdf.inputs["Roughness"].default_value = d["SpecularHighlight"]
            transparency = d.get("Transparency") or 0.0
            bsdf.inputs["Alpha"].default_value = 1 - transparency
            if transparency > 0:
                material.blend_method = "BLEND"
            material.diffuse_color = solid_color + (1.0 - transparency,)
        elif shading_only:
            d = tool.Loader.surface_style_to_dict(shading_only)
            r, g, b = d["SurfaceColour"]
            alpha = 1 - (d.get("Transparency") or 0.0)
            bsdf.inputs["Base Color"].default_value = (r, g, b, 1.0)
            bsdf.inputs["Alpha"].default_value = alpha
            if alpha < 1.0:
                material.blend_method = "BLEND"
            material.diffuse_color = (r, g, b, alpha)
        # else: leave default white Principled BSDF
        return output

    @classmethod
    def setup_dual_branch(cls, material: bpy.types.Material, ext_material: bpy.types.Material) -> bool:
        """Build a dual-branch node tree: flat branch from IFC data + external branch from ext_material.

        Clears any existing nodes and builds both branches from scratch.
        External branch output (BIM_Output_External) is set active — Pretty mode.
        Flat branch output (BIM_Output_Flat) is inactive — Flat mode.
        Returns True on success; False if no shader editor is available (falls back to single-branch).
        """
        cls.set_use_nodes(material, True)
        for n in material.node_tree.nodes[:]:
            material.node_tree.nodes.remove(n)

        cls._build_flat_branch_nodes(material)

        ext_output = tool.Blender.copy_node_graph_additive(material, ext_material)
        if not ext_output:
            # No shader editor available: fall back to single-branch
            tool.Blender.copy_node_graph(material, ext_material)
            return False

        ext_output.name = "BIM_Output_External"
        ext_output.is_active_output = True
        material["bim_dual_branch"] = True
        return True

    @classmethod
    def update_external_branch(cls, material: bpy.types.Material, ext_material: bpy.types.Material) -> None:
        """Replace the external-branch nodes of an already dual-branch material."""
        cls._remove_external_branch(material)
        ext_output = tool.Blender.copy_node_graph_additive(material, ext_material)
        if ext_output:
            ext_output.name = "BIM_Output_External"
            ext_output.is_active_output = True
            fast = material.node_tree.nodes.get("BIM_Output_Flat")
            if fast:
                fast.is_active_output = False

    @classmethod
    def sync_flat_branch_shading(
        cls, material: bpy.types.Material, surface_colour: tuple[float, float, float], transparency: float
    ) -> None:
        """Update the flat-branch Principled BSDF with new shading values.

        Call this after creating or editing IfcSurfaceStyleShading so the flat branch
        stays in sync without requiring a full setup_dual_branch rebuild.
        """
        if not material.node_tree:
            return
        fast_output = material.node_tree.nodes.get("BIM_Output_Flat")
        if not fast_output:
            return
        for link in fast_output.inputs["Surface"].links:
            if link.from_node.type == "BSDF_PRINCIPLED":
                bsdf = link.from_node
                r, g, b = surface_colour
                bsdf.inputs["Base Color"].default_value = (r, g, b, 1.0)
                bsdf.inputs["Alpha"].default_value = 1.0 - transparency
                break

    @classmethod
    def switch_shading(cls, blender_material: bpy.types.Material, style_type: StyleType) -> None:
        if style_type == "External":
            ext, fast = cls.get_branch_outputs(blender_material)
            if ext and fast:
                ext.is_active_output = True
                fast.is_active_output = False
                blender_material.update_tag()
                return
            try:
                bpy.ops.bim.activate_external_style(material_name=blender_material.name)
            except RuntimeError as error:
                if str(error).startswith("Error: Error loading external style for "):
                    return
                raise error
        elif style_type == "Shading":
            ext, fast = cls.get_branch_outputs(blender_material)
            if ext and fast:
                fast.is_active_output = True
                ext.is_active_output = False
                blender_material.update_tag()
                return
            style_elements = tool.Style.get_style_elements(blender_material)
            rendering_style = None
            texture_style = None
            shading_only_style = None

            for surface_style in style_elements.values():
                if surface_style.is_a() == "IfcSurfaceStyleShading":
                    shading_only_style = surface_style
                    tool.Loader.create_surface_style_shading(blender_material, surface_style)
                elif surface_style.is_a("IfcSurfaceStyleRendering"):
                    rendering_style = surface_style
                    shading_only_style = None  # rendering overrides shading-only path
                    tool.Loader.create_surface_style_rendering(blender_material, surface_style)
                elif surface_style.is_a("IfcSurfaceStyleWithTextures"):
                    texture_style = surface_style

            if rendering_style and texture_style:
                tool.Loader.create_surface_style_with_textures(blender_material, rendering_style, texture_style)
            elif shading_only_style and not rendering_style:
                # create a minimal Principled BSDF so Material Preview/Rendered shows the colour instead of white.
                tool.Style.set_use_nodes(blender_material, True)
                tool.Loader.restart_material_node_tree(blender_material)
                bsdf = tool.Blender.get_material_node(blender_material, "BSDF_PRINCIPLED")
                if bsdf:
                    r, g, b, a = blender_material.diffuse_color
                    bsdf.inputs["Base Color"].default_value = (r, g, b, 1)
                    bsdf.inputs["Alpha"].default_value = a
                    if a < 1.0:
                        blender_material.blend_method = "BLEND"
        else:
            assert False, f"Invalid style type found: {style_type}"

    @classmethod
    def rename_style(cls, style: ifcopenshell.entity_instance, name: str) -> None:
        """Rename style and related blender material."""
        if style.Name == name:
            return
        style.Name = name
        blender_material = tool.Ifc.get_object(style)
        assert isinstance(blender_material, bpy.types.Material)
        tool.Root.set_material_name(blender_material, name)

    @classmethod
    def purge_unused_styles(cls) -> int:
        """Purge unused styles (and related Blender materials).

        Note that Styles UI should be updated manually after using this method.
        """

        ifc_file = tool.Ifc.get()
        i = 0
        if ifc_file.schema in ("IFC2X3", "IFC4"):
            for element in ifc_file.by_type("IfcPresentationStyleAssignment"):
                if ifc_file.get_total_inverses(element) == 0:
                    ifc_file.remove(element)
        for element in ifc_file.by_type("IfcPresentationStyle"):
            if ifc_file.get_total_inverses(element) == 0:
                bonsai.core.style.remove_style(tool.Ifc, tool.Style, element, reload_styles_ui=False)
                i += 1
        return i

    @classmethod
    def is_style_side_attribute_edited(
        cls, style: ifcopenshell.entity_instance, new_attributes: dict[str, Any]
    ) -> bool:
        old_value, new_value = style.Side, new_attributes["Side"]
        # Only need to reload if there it was change from/become NEGATIVE.
        return old_value != new_value and "NEGATIVE" in (old_value, new_value)

    @classmethod
    def reload_representations(cls, style: ifcopenshell.entity_instance) -> None:
        elements = ifcopenshell.util.element.get_elements_by_style(tool.Ifc.get(), style)
        objects = [tool.Ifc.get_object(e) for e in elements]
        tool.Geometry.reload_representation(objects)

    @classmethod
    def restore_material_style_types(cls, shading_type: str) -> bool:
        """Set each IFC material's active_style_type to the richest available for the given viewport mode.

        In SOLID mode all materials use "Shading".
        In MATERIAL_PREVIEW / RENDERED, materials with an external .blend style use "External"
        unless prefer_ifc_shading is set on that material.

        Returns True if any IFC material has IfcSurfaceStyleWithTextures (used to decide color_type).
        """
        has_any_textures = False
        for material in bpy.data.materials:
            if not tool.Blender.get_ifc_definition_id(material):
                continue
            props = cls.get_material_style_props(material)
            style_elements = cls.get_style_elements(material)
            if style_elements.get("IfcSurfaceStyleWithTextures"):
                has_any_textures = True
            if shading_type == "SOLID":
                props.active_style_type = "Shading"
                shading = style_elements.get("IfcSurfaceStyleRendering") or style_elements.get("IfcSurfaceStyleShading")
                if shading:
                    d = tool.Loader.surface_style_to_dict(shading)
                    alpha = 1.0 - (d.get("Transparency") or 0.0)
                    material.diffuse_color = d["SurfaceColour"] + (alpha,)
            else:  # MATERIAL_PREVIEW or RENDERED
                if cls.has_blender_external_style(style_elements) and not props.prefer_ifc_shading:
                    props.active_style_type = "External"
                else:
                    props.active_style_type = "Shading"
            material.update_tag()
        return has_any_textures
