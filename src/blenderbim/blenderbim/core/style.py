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


def add_style(ifc, style, obj=None):
    element = ifc.run("style.add_style", name=style.get_name(obj))
    ifc.link(element, obj)
    if style.can_support_rendering_style(obj):
        attributes = style.get_surface_rendering_attributes(obj)
        ifc.run("style.add_surface_style", style=element, ifc_class="IfcSurfaceStyleRendering", attributes=attributes)
    else:
        attributes = style.get_surface_shading_attributes(obj)
        ifc.run("style.add_surface_style", style=element, ifc_class="IfcSurfaceStyleShading", attributes=attributes)

    material = ifc.get_entity(obj)
    if material:
        ifc.run("style.assign_material_style", material=material, style=element, context=style.get_context(obj))
    return element


def remove_style(ifc, style, obj=None):
    element = style.get_style(obj)
    ifc.unlink(obj=obj, element=element)
    ifc.run("style.remove_style", style=element)


def update_style_colours(ifc, style, obj=None):
    element = style.get_style(obj)

    if style.can_support_rendering_style(obj):
        rendering_style = style.get_surface_rendering_style(obj)
        attributes = style.get_surface_rendering_attributes(obj)
        if rendering_style:
            ifc.run("style.edit_surface_style", style=rendering_style, attributes=attributes)
        else:
            ifc.run(
                "style.add_surface_style", style=element, ifc_class="IfcSurfaceStyleRendering", attributes=attributes
            )
    else:
        shading_style = style.get_surface_shading_style(obj)
        attributes = style.get_surface_shading_attributes(obj)
        if shading_style:
            ifc.run("style.edit_surface_style", style=shading_style, attributes=attributes)
        else:
            ifc.run("style.add_surface_style", style=element, ifc_class="IfcSurfaceStyleShading", attributes=attributes)


def update_style_textures(ifc, style, obj=None, representation=None):
    element = style.get_style(obj)

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


def unlink_style(ifc, style, obj=None):
    ifc.unlink(obj=obj, element=style.get_style(obj))


def enable_editing_style(style, obj=None):
    style.enable_editing(obj)
    style.import_surface_attributes(style.get_style(obj), obj)


def disable_editing_style(style, obj=None):
    style.disable_editing(obj)


def edit_style(ifc, style, obj=None):
    attributes = style.export_surface_attributes(obj)
    ifc.run("style.edit_presentation_style", style=style.get_style(obj), attributes=attributes)
    style.disable_editing(obj)
