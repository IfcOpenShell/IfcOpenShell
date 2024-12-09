# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
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
import bonsai.bim.helper
import bonsai.tool as tool
from bpy.types import Panel, UIList
from bonsai.bim.ifc import IfcStore
from bonsai.bim.module.style.data import StylesData, BlenderMaterialStyleData
from typing import Union


class BIM_PT_styles(Panel):
    bl_label = "Styles"
    bl_idname = "BIM_PT_styles"
    bl_options = {"HIDE_HEADER"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_tab_styles"

    @classmethod
    def poll(cls, context):
        return IfcStore.get_file()

    def draw(self, context):
        if not StylesData.is_loaded:
            StylesData.load()

        self.props = context.scene.BIMStylesProperties

        if not self.props.is_editing:
            row = self.layout.row(align=True)
            style_type = self.props.style_type
            row.label(text="{} Styles".format(StylesData.data["total_styles"][style_type]), icon="SHADING_RENDERED")
            bonsai.bim.helper.prop_with_search(row, self.props, "style_type", text="")
            row.operator("bim.load_styles", text="", icon="IMPORT").style_type = style_type
            return

        active_style = bool(self.props.styles and self.props.active_style_index < len(self.props.styles))
        row = self.layout.row(align=True)
        row.label(text="{} {}s".format(len(self.props.styles), self.props.style_type), icon="SHADING_RENDERED")
        row.operator("bim.disable_editing_styles", text="", icon="CANCEL")

        row = self.layout.row(align=True)
        row.alignment = "RIGHT"
        if not self.props.is_adding:
            row.operator("bim.enable_adding_presentation_style", text="", icon="ADD")
        if active_style:
            style = self.props.styles[self.props.active_style_index]

            row.operator("bim.duplicate_style", text="", icon="DUPLICATE").style = style.ifc_definition_id
            row.operator("bim.select_by_style", text="", icon="RESTRICT_SELECT_OFF").style = style.ifc_definition_id
            op = row.operator("bim.assign_style_to_selected", text="", icon="BRUSH_DATA")
            op.style_id = style.ifc_definition_id
            op = row.operator("bim.save_uv_to_style", text="", icon="UV")
            op = row.operator("bim.enable_editing_style", text="", icon="GREASEPENCIL")
            op.style = style.ifc_definition_id
            row.operator("bim.remove_style", text="", icon="X").style = style.ifc_definition_id

        self.layout.template_list("BIM_UL_styles", "", self.props, "styles", self.props, "active_style_index")

        # adding a new IfcSurfaceStyle
        if self.props.is_adding:
            box = self.layout.box()
            row = box.row()
            row.prop(self.props, "style_name", text="Name")
            if self.props.style_type == "IfcSurfaceStyle":
                row = box.row()
                # NOTE: user must choose 1 of the style elements to create IfcSurfaceStyle
                # otherwise it won't be a valid IFC
                row.prop(self.props, "surface_style_class", text="Class")
                if self.props.surface_style_class in ("IfcSurfaceStyleShading", "IfcSurfaceStyleRendering"):
                    row = box.row()
                    row.prop(self.props, "surface_colour", text="Colour")
            row = box.row(align=True)
            row.operator("bim.add_presentation_style", text="Save New Style", icon="CHECKMARK")
            row.operator("bim.disable_adding_presentation_style", text="", icon="CANCEL")

        # style ui tools
        if active_style:
            row = self.layout.row(align=True)
            if material := style.blender_material:
                row.prop(material.BIMStyleProperties, "active_style_type", icon="SHADING_RENDERED", text="")
                op = row.operator("bim.update_current_style", icon="FILE_REFRESH", text="")
                op.style_id = style.ifc_definition_id

            if self.props.style_type == "IfcSurfaceStyle":
                self.layout.label(text="Surface Style Element:")
                col = self.layout.column(align=True)

                row = col.row(align=True)
                op = row.operator("bim.enable_editing_surface_style", text="Shade", icon="SHADING_SOLID")
                op.ifc_class = "IfcSurfaceStyleShading"
                op.style = style.ifc_definition_id
                op = row.operator("bim.enable_editing_surface_style", text="Render", icon="SHADING_RENDERED")
                op.ifc_class = "IfcSurfaceStyleRendering"
                op.style = style.ifc_definition_id
                op = row.operator("bim.enable_editing_surface_style", text="Texture", icon="SHADING_TEXTURE")
                op.ifc_class = "IfcSurfaceStyleWithTextures"
                op.style = style.ifc_definition_id

                row = col.row(align=True)
                op = row.operator("bim.enable_editing_surface_style", text="Lighting", icon="LIGHT_SUN")
                op.ifc_class = "IfcSurfaceStyleLighting"
                op.style = style.ifc_definition_id
                op = row.operator("bim.enable_editing_surface_style", text="Refract", icon="LIGHT_POINT")
                op.ifc_class = "IfcSurfaceStyleRefraction"
                op.style = style.ifc_definition_id
                op = row.operator("bim.enable_editing_surface_style", text="External", icon="APPEND_BLEND")
                op.ifc_class = "IfcExternallyDefinedSurfaceStyle"
                op.style = style.ifc_definition_id

        # display style elements props during edit
        if self.props.is_editing_style:
            if self.props.is_editing_class == "IfcSurfaceStyle":
                bonsai.bim.helper.draw_attributes(self.props.attributes, self.layout)
                edit_label = "Save Attributes"
            elif self.props.is_editing_class == "IfcSurfaceStyleShading":
                self.draw_surface_style_shading()
                edit_label = "Save Shading Style"
            elif self.props.is_editing_class == "IfcSurfaceStyleRendering":
                self.draw_surface_style_rendering()
                edit_label = "Save Rendering Style"
            elif self.props.is_editing_class == "IfcExternallyDefinedSurfaceStyle":
                self.draw_externally_defined_surface_style()
                edit_label = "Save External Style"
            elif self.props.is_editing_class == "IfcSurfaceStyleWithTextures":
                self.draw_surface_style_with_textures()
                edit_label = "Save Texture Style"
            elif self.props.is_editing_class == "IfcSurfaceStyleRefraction":
                self.draw_refraction_surface_style()
                edit_label = "Save Refaction Style"
            else:  # IfcSurfaceStyleLighting
                self.draw_lighting_surface_style()
                edit_label = "Save Lighting Style"
            self.draw_edit_ui(edit_label)

    def draw_surface_style_shading(self):
        row = self.layout.row()
        row.prop(self.props, "surface_colour")
        row = self.layout.row()
        row.prop(self.props, "transparency")

    def draw_surface_style_rendering(self):
        row = self.layout.row()
        row.prop(self.props, "surface_colour")
        row = self.layout.row()
        row.prop(self.props, "transparency")
        row = self.layout.row()
        row.prop(self.props, "reflectance_method")

        if self.props.reflectance_method not in ("PHYSICAL", "NOTDEFINED", "FLAT"):
            self.layout.label(text=f"Supported reflectance methods are:")
            self.layout.label(text=f"PHYSICAL / NOTDEFINED / FLAT")

        row = self.layout.row(align=True)
        row.label(text="Emissive" if self.props.reflectance_method == "FLAT" else "Diffuse")
        row.prop(self.props, "diffuse_colour_class", text="")
        if self.props.diffuse_colour_class == "IfcColourRgb":
            row.prop(self.props, "diffuse_colour", text="")
        else:
            row.prop(self.props, "diffuse_colour_ratio", text="")
        row.prop(
            self.props,
            "is_diffuse_colour_null",
            text="",
            icon="RADIOBUT_OFF" if self.props.is_diffuse_colour_null else "RADIOBUT_ON",
        )

        row = self.layout.row(align=True)
        if self.props.reflectance_method in ("PHYSICAL", "NOTDEFINED"):
            row.label(text="Metallic")
        else:
            row.label(text="Specular")
        row.prop(self.props, "specular_colour_class", text="")
        if self.props.specular_colour_class == "IfcColourRgb":
            row.prop(self.props, "specular_colour", text="")
        else:
            row.prop(self.props, "specular_colour_ratio", text="")
        row.prop(
            self.props,
            "is_specular_colour_null",
            text="",
            icon="RADIOBUT_OFF" if self.props.is_specular_colour_null else "RADIOBUT_ON",
        )

        row = self.layout.row(align=True)
        if self.props.reflectance_method in ("PHYSICAL", "NOTDEFINED"):
            row.label(text="Roughness")
        elif self.props.reflectance_method in ("PHONG"):
            row.label(text="Shininess")
        else:
            row.label(text="Highlight")
        row.prop(self.props, "specular_highlight", text="")
        row.prop(
            self.props,
            "is_specular_highlight_null",
            text="",
            icon="RADIOBUT_OFF" if self.props.is_specular_highlight_null else "RADIOBUT_ON",
        )

    def draw_surface_style_with_textures(self):
        textures = self.props.textures
        row = self.layout.row(align=True)
        row.label(text=f"Style has {len(textures)} textures", icon="SHADING_TEXTURE")
        row.operator("bim.add_surface_texture", text="", icon="ADD")
        self.layout.prop(self.props, "uv_mode")

        for i, texture in enumerate(textures):
            split = self.layout.split(factor=0.30, align=True)
            split.column(align=True).prop(texture, "mode", text="")

            # path
            row = split.column(align=True).row(align=True)
            row.prop(texture, "path", text="")
            op_path = row.operator("bim.choose_texture_map_path", text="", icon="FILEBROWSER")
            op_clear = row.operator("bim.remove_texture_map", text="", icon="X")
            op_path.texture_map_index = op_clear.texture_map_index = i

    def draw_externally_defined_surface_style(self):
        row = self.layout.row()
        op = row.operator("bim.browse_external_style", icon="APPEND_BLEND", text="Append From Blend File")
        style = self.props.styles[self.props.active_style_index]
        op.active_surface_style_id = style.ifc_definition_id
        bonsai.bim.helper.draw_attributes(self.props.external_style_attributes, self.layout)

    def draw_refraction_surface_style(self):
        bonsai.bim.helper.draw_attributes(self.props.refraction_style_attributes, self.layout)
        row = self.layout.row(align=True)

    def draw_lighting_surface_style(self):
        bonsai.bim.helper.draw_attributes(self.props.lighting_style_colours, self.layout)

    def draw_edit_ui(self, edit_label: str):
        row = self.layout.row(align=True)
        row.operator("bim.edit_surface_style", text=edit_label, icon="CHECKMARK")
        if self.props.is_editing_existing_style:
            row.operator("bim.remove_surface_style", text="", icon="X")
        row.operator("bim.disable_editing_style", text="", icon="CANCEL")


class BIM_UL_styles(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if item:
            row = layout.row(align=True)
            material_icon = 0
            if material := item.blender_material:
                preview = material.preview_ensure()
                material_icon = preview.icon_id
            row.prop(item, "name", text="", emboss=False, icon_value=material_icon)
            if item.has_surface_colour:
                row = row.row(align=True)
                row.enabled = False
                row.prop(item, "surface_colour", text="")
                if item.has_diffuse_colour:
                    row.prop(item, "diffuse_colour", text="")
            row2 = row.row()
            row2.alignment = "RIGHT"
            row2.label(text=str(item.total_elements))
            for style in item.style_classes:
                if style.name == "IfcSurfaceStyleShading":
                    row2.label(text="", icon="SHADING_SOLID")
                elif style.name == "IfcSurfaceStyleRendering":
                    row2.label(text="", icon="SHADING_RENDERED")
                elif style.name == "IfcSurfaceStyleWithTextures":
                    row2.label(text="", icon="SHADING_TEXTURE")
                elif style.name == "IfcSurfaceStyleLighting":
                    row2.label(text="", icon="LIGHT_SUN")
                elif style.name == "IfcSurfaceStyleRefraction":
                    row2.label(text="", icon="LIGHT_POINT")
                elif style.name == "IfcExternallyDefinedSurfaceStyle":
                    row2.label(text="", icon="APPEND_BLEND")


class BIM_PT_style(Panel):
    bl_label = "Style"
    bl_idname = "BIM_PT_style"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "material"

    @classmethod
    def poll(cls, context):
        return bool(tool.Ifc.get() and (material := context.material) and material.BIMStyleProperties.ifc_definition_id)

    def draw(self, context):
        # NOTE: this UI is needed only to indicate whether blender material is linked to IFC
        # and shouldn't be overloaded with any other features (they should be added to the general Styles UI).

        if not BlenderMaterialStyleData.is_loaded:
            BlenderMaterialStyleData.load()

        material = context.material
        style_id = material.BIMStyleProperties.ifc_definition_id
        row = self.layout.row(align=True)

        if style_id and not BlenderMaterialStyleData.data["is_linked_to_style"]:
            row.label(text="Material has linked IFC from a different project.")
            op = row.operator("bim.unlink_style", icon="UNLINKED", text="")
            op.blender_material = material.name
            return
        else:
            row.label(text="Material is linked to an IFC style.")
            op = row.operator("bim.unlink_style", icon="UNLINKED", text="")
            op.blender_material = material.name

        row = self.layout.row(align=True)
        row.label(text="IFC Style ID:")
        row.label(text=str(style_id))
        row = self.layout.row(align=True)
        row.label(text="IFC Style Name:")
        row.label(text=BlenderMaterialStyleData.data["linked_style_name"])
