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
from typing import TYPE_CHECKING, Optional, Any

if TYPE_CHECKING:
    import bpy
    import ifcopenshell
    import bonsai.tool as tool


def add_style(ifc: tool.Ifc, style: tool.Style, obj: bpy.types.Material) -> ifcopenshell.entity_instance:
    element = ifc.run("style.add_style", name=style.get_name(obj))
    ifc.link(element, obj)
    if style.can_support_rendering_style(obj):
        attributes = style.get_surface_rendering_attributes(obj)
        ifc.run("style.add_surface_style", style=element, ifc_class="IfcSurfaceStyleRendering", attributes=attributes)
    else:
        attributes = style.get_surface_shading_attributes(obj)
        ifc.run("style.add_surface_style", style=element, ifc_class="IfcSurfaceStyleShading", attributes=attributes)
    return element


# TODO: outdated.
def add_external_style(ifc: tool.Ifc, style: tool.Style, obj: bpy.types.Material, attributes: dict[str, Any]) -> None:
    element = ifc.get_entity(obj)
    ifc.run(
        "style.add_surface_style", style=element, ifc_class="IfcExternallyDefinedSurfaceStyle", attributes=attributes
    )


# TODO: unused `style` argument?
def update_external_style(
    ifc: tool.Ifc,
    style: ifcopenshell.entity_instance,
    external_style: ifcopenshell.entity_instance,
    attributes: dict[str, Any],
) -> None:
    ifc.run("style.edit_surface_style", style=external_style, attributes=attributes)


def remove_style(
    ifc: tool.Ifc, style_tool: tool.Style, style: ifcopenshell.entity_instance, reload_styles_ui: bool = False
) -> None:
    """Remove IfcPresentationStyle and associated Blender material.

    :param reload_styles_ui: Whether to reload Styles UI after removal.
        Useful to disable if you plan to remove many styles and want to
        avoid unnecessary reloads.
    """
    obj = ifc.get_object(style)
    # Get style_type before removing object as later StylesData might fail to load
    # due object not yet removed completely.
    style_type = style_tool.get_active_style_type()
    ifc.unlink(element=style)
    ifc.run("style.remove_style", style=style)
    if obj:
        style_tool.delete_object(obj)
    if reload_styles_ui and style_tool.is_editing_styles():
        style_tool.import_presentation_styles(style_type)


def update_style_colours(ifc: tool.Ifc, style: tool.Style, obj: bpy.types.Material, verbose: bool = False) -> None:
    element = ifc.get_entity(obj)

    if style.can_support_rendering_style(obj):
        rendering_style = style.get_surface_rendering_style(obj)
        texture_style = style.get_texture_style(obj)
        attributes = style.get_surface_rendering_attributes(obj, verbose)
        if rendering_style:
            ifc.run("style.edit_surface_style", style=rendering_style, attributes=attributes)
        else:
            ifc.run(
                "style.add_surface_style", style=element, ifc_class="IfcSurfaceStyleRendering", attributes=attributes
            )

        # TODO: uvs?
        textures = ifc.run("style.add_surface_textures", material=obj)
        if not texture_style and textures:
            ifc.run(
                "style.add_surface_style",
                style=element,
                ifc_class="IfcSurfaceStyleWithTextures",
                attributes={"Textures": textures},
            )
        elif texture_style:
            # TODO: should we remove blender images and IFCIMAGETEXTURE here if they're not used by other objects?
            ifc.run("style.edit_surface_style", style=texture_style, attributes={"Textures": textures})
    else:
        shading_style = style.get_surface_shading_style(obj)
        attributes = style.get_surface_shading_attributes(obj)
        if shading_style:
            ifc.run("style.edit_surface_style", style=shading_style, attributes=attributes)
        else:
            ifc.run("style.add_surface_style", style=element, ifc_class="IfcSurfaceStyleShading", attributes=attributes)


def update_style_textures(
    ifc: tool.Ifc, style: tool.Style, obj: ifcopenshell.entity_instance, representation: ifcopenshell.entity_instance
) -> None:
    element = ifc.get_entity(obj)

    uv_maps = style.get_uv_maps(representation)
    textures = ifc.run("style.add_surface_textures", material=obj, uv_maps=uv_maps)
    texture_style = style.get_surface_texture_style(obj)

    if textures:
        if texture_style:
            ifc.run("style.remove_surface_style", style=texture_style)
        ifc.run(
            "style.add_surface_style",
            style=element,
            ifc_class="IfcSurfaceStyleWithTextures",
            attributes={"Textures": textures},
        )
    elif texture_style:
        ifc.run("style.remove_surface_style", style=texture_style)


# TODO: outdated.
def unlink_style(ifc: tool.Ifc, style: ifcopenshell.entity_instance) -> None:
    ifc.unlink(element=style)


def enable_editing_style(style_tool: tool.Style, style: ifcopenshell.entity_instance) -> None:
    style_tool.enable_editing(style)
    style_tool.import_surface_attributes(style)


def disable_editing_style(style: tool.Style) -> None:
    obj = style.get_currently_edited_material()
    style.disable_editing()
    style.reload_material_from_ifc(obj)


def edit_style(ifc: tool.Ifc, style: tool.Style) -> None:
    obj = style.get_currently_edited_material()
    style_element = ifc.get_entity(obj)
    assert style_element
    attributes = style.export_surface_attributes()
    is_style_side_attribute_edited = style.is_style_side_attribute_edited(style_element, attributes)
    ifc.run("style.edit_presentation_style", style=style_element, attributes=attributes)
    style.disable_editing()
    load_styles(style, style.get_active_style_type())
    if is_style_side_attribute_edited:
        style.reload_repersentations(style_element)


def load_styles(style: tool.Style, style_type: str) -> None:
    style.import_presentation_styles(style_type)
    style.enable_editing_styles()


def disable_editing_styles(style: tool.Style) -> None:
    style.disable_editing_styles()


def select_by_style(style_tool: tool.Style, spatial: tool.Spatial, style: ifcopenshell.entity_instance) -> None:
    spatial.select_products(style_tool.get_elements_by_style(style))
