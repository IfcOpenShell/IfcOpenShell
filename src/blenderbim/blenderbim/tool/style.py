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

import ifcopenshell
import blenderbim.core.tool
import blenderbim.tool as tool
import blenderbim.bim.helper


class Style(blenderbim.core.tool.Style):
    @classmethod
    def disable_editing(cls, obj):
        obj.BIMStyleProperties.is_editing = False

    @classmethod
    def enable_editing(cls, obj):
        obj.BIMStyleProperties.is_editing = True

    @classmethod
    def export_surface_attributes(cls, obj):
        return blenderbim.bim.helper.export_attributes(obj.BIMStyleProperties.attributes)

    @classmethod
    def get_context(cls, obj):
        return ifcopenshell.util.representation.get_context(tool.Ifc.get(), "Model", "Body", "MODEL_VIEW")

    @classmethod
    def get_name(cls, obj):
        return obj.name

    @classmethod
    def get_style(cls, obj):
        if obj.BIMMaterialProperties.ifc_style_id:
            return tool.Ifc.get().by_id(obj.BIMMaterialProperties.ifc_style_id)

    @classmethod
    def get_surface_rendering_attributes(cls, obj):
        transparency = obj.diffuse_color[3]
        diffuse_colour = obj.diffuse_color
        if obj.use_nodes and hasattr(obj.node_tree, "nodes") and "Principled BSDF" in obj.node_tree.nodes:
            bsdf = obj.node_tree.nodes["Principled BSDF"]
            transparency = bsdf.inputs["Alpha"].default_value
            diffuse_colour = bsdf.inputs["Base Color"].default_value
        transparency = 1 - transparency
        return {
            "SurfaceColour": {
                "Name": None,
                "Red": obj.diffuse_color[0],
                "Green": obj.diffuse_color[1],
                "Blue": obj.diffuse_color[2],
            },
            "Transparency": transparency,
            "DiffuseColour": {
                "Name": None,
                "Red": obj.diffuse_color[0],
                "Green": obj.diffuse_color[1],
                "Blue": obj.diffuse_color[2],
            },
        }

    @classmethod
    def get_surface_rendering_style(cls, obj):
        if obj.BIMMaterialProperties.ifc_style_id:
            style = tool.Ifc.get().by_id(obj.BIMMaterialProperties.ifc_style_id)
            items = [s for s in style.Styles if s.is_a("IfcSurfaceStyleRendering")]
            if items:
                return items[0]

    @classmethod
    def get_surface_shading_attributes(cls, obj):
        return {
            "SurfaceColour": {
                "Name": None,
                "Red": obj.diffuse_color[0],
                "Green": obj.diffuse_color[1],
                "Blue": obj.diffuse_color[2],
            },
            "Transparency": 1 - obj.diffuse_color[3],
        }

    @classmethod
    def get_surface_shading_style(cls, obj):
        if obj.BIMMaterialProperties.ifc_style_id:
            style = tool.Ifc.get().by_id(obj.BIMMaterialProperties.ifc_style_id)
            items = [s for s in style.Styles if s.is_a("IfcSurfaceStyleShading")]
            if items:
                return items[0]

    @classmethod
    def import_surface_attributes(cls, style, obj):
        blenderbim.bim.helper.import_attributes2(style, obj.BIMStyleProperties.attributes)

    @classmethod
    def link(cls, style, obj):
        obj.BIMMaterialProperties.ifc_style_id = style.id()

    @classmethod
    def unlink(self, obj):
        obj.BIMMaterialProperties.ifc_style_id = 0
