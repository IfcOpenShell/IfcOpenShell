# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
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
import blenderbim.bim.helper
from bpy.types import Panel, UIList
from blenderbim.bim.ifc import IfcStore
from blenderbim.bim.module.style.data import StylesData, StyleAttributesData
from bl_ui.properties_material import MaterialButtonsPanel
from blenderbim.tool.style import TEXTURE_MAPS_BY_METHODS, STYLE_TEXTURE_PROPS_MAP


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

        if self.props.is_editing:
            row = self.layout.row(align=True)
            row.label(text="{} {}s".format(len(self.props.styles), self.props.style_type), icon="SHADING_RENDERED")
            if not self.props.is_adding:
                row.operator("bim.enable_add_presentation_style", text="", icon="ADD")
            row.operator("bim.disable_editing_styles", text="", icon="CANCEL")
        else:
            row = self.layout.row(align=True)
            row.label(text="{} Styles".format(StylesData.data["total_styles"]), icon="SHADING_RENDERED")
            blenderbim.bim.helper.prop_with_search(row, self.props, "style_type", text="")
            row.operator("bim.load_styles", text="", icon="IMPORT").style_type = self.props.style_type
            return

        if self.props.is_adding:
            box = self.layout.box()
            row = box.row()
            row.prop(self.props, "style_name", text="Name")
            if self.props.style_type == "IfcSurfaceStyle":
                row = box.row()
                row.prop(self.props, "surface_style_class", text="Class")
                if self.props.surface_style_class in ("IfcSurfaceStyleShading", "IfcSurfaceStyleRendering"):
                    row = box.row()
                    row.prop(self.props, "surface_colour", text="Colour")
            row = box.row(align=True)
            row.operator("bim.add_presentation_style", text="Save New Style", icon="CHECKMARK")
            row.operator("bim.disable_add_presentation_style", text="", icon="CANCEL")

        if self.props.styles and self.props.active_style_index < len(self.props.styles):
            row = self.layout.row(align=True)
            style = self.props.styles[self.props.active_style_index]
            op = row.operator("bim.enable_editing_style", text="Edit Style", icon="GREASEPENCIL")
            op.style = style.ifc_definition_id
            row.operator("bim.select_by_style", text="", icon="RESTRICT_SELECT_OFF").style = style.ifc_definition_id
            row.operator("bim.remove_style", text="", icon="X").style = style.ifc_definition_id

            if self.props.style_type == "IfcSurfaceStyle":
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

        self.layout.template_list("BIM_UL_styles", "", self.props, "styles", self.props, "active_style_index")

        if self.props.is_editing_style:
            if self.props.is_editing_class == "IfcSurfaceStyle":
                blenderbim.bim.helper.draw_attributes(self.props.attributes, self.layout)
                row = self.layout.row(align=True)
                row.operator("bim.edit_style", text="Save Attributes", icon="CHECKMARK")
                row.operator("bim.disable_editing_style", text="", icon="CANCEL")
            elif self.props.is_editing_class == "IfcSurfaceStyleShading":
                self.draw_surface_style_shading()
            elif self.props.is_editing_class == "IfcSurfaceStyleRendering":
                self.draw_surface_style_rendering()

    def draw_surface_style_shading(self):
        row = self.layout.row()
        row.prop(self.props, "surface_colour")
        row = self.layout.row()
        row.prop(self.props, "transparency")
        row = self.layout.row(align=True)
        row.operator("bim.edit_surface_style", text="Save Shading Style", icon="CHECKMARK")
        row.operator("bim.disable_editing_style", text="", icon="CANCEL")

    def draw_surface_style_rendering(self):
        row = self.layout.row()
        row.prop(self.props, "surface_colour")
        row = self.layout.row()
        row.prop(self.props, "transparency")
        row = self.layout.row()
        row.prop(self.props, "reflectance_method")

        row = self.layout.row(align=True)
        row.label(text="Diffuse")
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

        row = self.layout.row(align=True)
        row.operator("bim.edit_surface_style", text="Save Rendering Style", icon="CHECKMARK")
        row.operator("bim.disable_editing_style", text="", icon="CANCEL")


def draw_style_ui(self, context):
    mat = context.material
    props = mat.BIMMaterialProperties
    style_props = mat.BIMStyleProperties
    row = self.layout.row(align=True)
    if not props.ifc_style_id:
        row.operator("bim.add_style", icon="ADD")
        return

    row.prop(style_props, "active_style_type", icon="SHADING_RENDERED", text="")
    row.operator("bim.update_current_style", icon="FILE_REFRESH", text="")
    row = self.layout.row(align=True)
    row.operator("bim.update_style_colours", icon="GREASEPENCIL")
    row.operator("bim.update_style_textures", icon="TEXTURE", text="")
    row.operator("bim.unlink_style", icon="UNLINKED", text="")
    row.operator("bim.remove_style", icon="X", text="").style = props.ifc_style_id


class BIM_PT_style(MaterialButtonsPanel, Panel):
    bl_label = "Style"
    bl_idname = "BIM_PT_style"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "material"

    @classmethod
    def poll(cls, context):
        return (
            IfcStore.get_file()
            and context.active_object is not None
            and context.active_object.active_material is not None
        )

    def draw(self, context):
        mat = context.material
        props = mat.BIMMaterialProperties
        draw_style_ui(self, context)
        if not props.ifc_style_id:
            return
        row = self.layout.row(align=True)
        row.prop(mat, "diffuse_color", text="Viewport Color" if mat.use_nodes else "Render Color")


class BIM_PT_style_attributes(Panel):
    bl_label = "Style Attributes"
    bl_idname = "BIM_PT_style_attributes"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "material"
    bl_parent_id = "BIM_PT_style"

    @classmethod
    def poll(cls, context):
        if not IfcStore.get_file():
            return False
        try:
            return bool(context.active_object.active_material.BIMMaterialProperties.ifc_style_id)
        except:
            return False

    def draw(self, context):
        if not StyleAttributesData.is_loaded:
            StyleAttributesData.load()
        elif (
            context.active_object.active_material.BIMMaterialProperties.ifc_style_id
            != StyleAttributesData.data["ifc_style_id"]
        ):
            StyleAttributesData.load()

        obj = context.active_object.active_material
        mprops = obj.BIMMaterialProperties
        props = obj.BIMStyleProperties
        if props.is_editing:
            row = self.layout.row(align=True)
            row.operator("bim.edit_style", icon="CHECKMARK")
            row.operator("bim.disable_editing_style", icon="CANCEL", text="")
            blenderbim.bim.helper.draw_attributes(props.attributes, self.layout)
        else:
            row = self.layout.row(align=True)
            row.label(text="STEP ID")
            row.label(text=str(mprops.ifc_style_id))

            for attribute in StyleAttributesData.data["attributes"]:
                row = self.layout.row(align=True)
                row.label(text=attribute["name"])
                row.label(text=attribute["value"])


class BIM_PT_external_style_attributes(Panel):
    bl_label = "External Surface Style"
    bl_idname = "BIM_PT_external_style_attributes"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "material"
    bl_parent_id = "BIM_PT_style"

    @classmethod
    def poll(cls, context):
        if not IfcStore.get_file():
            return False
        try:
            return bool(context.active_object.active_material.BIMMaterialProperties.ifc_style_id)
        except:
            return False

    def draw(self, context):
        if not StyleAttributesData.is_loaded or (
            context.active_object.active_material.BIMMaterialProperties.ifc_style_id
            != StyleAttributesData.data["ifc_style_id"]
        ):
            StyleAttributesData.load()

        mat = context.active_object.active_material
        mprops = mat.BIMMaterialProperties
        props = mat.BIMStyleProperties

        external_style = StyleAttributesData.data["style_elements"].get("IfcExternallyDefinedSurfaceStyle", None)
        if not external_style:
            row = self.layout.row(align=True)
            row.operator("bim.browse_external_style", text="Add External Style", icon="ADD")
            return

        row = self.layout.row(align=True)
        row.label(text="Parameters:")

        if props.is_editing_external_style:
            row.operator("bim.edit_external_style", icon="CHECKMARK", text="")
            row.operator("bim.disable_editing_external_style", icon="CANCEL", text="")
            blenderbim.bim.helper.draw_attributes(props.external_style_attributes, self.layout)
        else:
            row.operator("bim.browse_external_style", icon="APPEND_BLEND", text="")
            row.operator("bim.enable_editing_external_style", icon="GREASEPENCIL", text="")

            row = self.layout.row(align=True)
            row.label(text="STEP ID")
            row.label(text=str(external_style.id()))

            for attribute in StyleAttributesData.data["external_style_attributes"]:
                row = self.layout.row(align=True)
                row.label(text=attribute["name"])
                row.label(text=attribute["value"])


class BIM_UL_styles(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if item:
            row = layout.row(align=True)
            row.label(text=item.name)
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


class BIM_PT_STYLE_GRAPH(Panel):
    bl_idname = "BIM_PT_style_graph"
    bl_space_type = "NODE_EDITOR"
    bl_label = "Style Graph Settings"
    bl_region_type = "UI"
    bl_category = "BBIM"

    @classmethod
    def poll(cls, context):
        return getattr(context, "material", None)

    def draw(self, context):
        layout = self.layout
        props = context.active_object.active_material.BIMStyleProperties

        draw_style_ui(self, context)
        layout.separator()
        box = layout.box()
        box.label(text="Creating shader from this panel")
        box.label(text="ensures that shader is")
        box.label(text="GLTF compatible")
        box.label(text="and therefore will be ")
        box.label(text="stored in IFC safely.")
        layout.separator()

        layout.prop(props, "update_graph", text="Graph Auto Update")
        layout.label(text="Reflectance Method:")
        layout.prop(props, "reflectance_method", text="")
        layout.prop(props, "surface_color")
        layout.prop(props, "transparency")

        if not (props.reflectance_method == "PHYSICAL" and props.diffuse_path) and not (
            props.reflectance_method == "FLAT" and props.emissive_path
        ):
            prop_name = "Emissive Color" if props.reflectance_method == "FLAT" else "Diffuse Color"
            layout.prop(props, "diffuse_color", text=prop_name)

        if props.reflectance_method == "PHYSICAL" and not props.metallic_roughness_path:
            layout.prop(props, "metallic")

        if props.reflectance_method not in ("PHYSICAL", "FLAT", "NOTDEFINED") or (
            props.reflectance_method == "PHYSICAL" and not props.metallic_roughness_path
        ):
            layout.prop(props, "roughness")

        def add_texture_path(path_name):
            row = layout.row(align=True)
            row.prop(props, path_name)
            op = row.operator("bim.clear_texture_map_path", text="", icon="X")
            op.texture_map_prop = path_name

        layout.separator()
        texture_maps = TEXTURE_MAPS_BY_METHODS.get(props.reflectance_method, [])
        if not texture_maps:
            return
        if not bpy.data.filepath:
            layout.label(text="Save .blend file to keep relative paths", icon="ERROR")

        layout.label(text="Texture Maps:")
        for texture_type in texture_maps:
            add_texture_path(STYLE_TEXTURE_PROPS_MAP[texture_type])
