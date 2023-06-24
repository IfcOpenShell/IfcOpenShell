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

import blenderbim.bim.helper
from bpy.types import Panel, UIList
from blenderbim.bim.ifc import IfcStore
from blenderbim.bim.module.style.data import StylesData, StyleAttributesData
from bl_ui.properties_material import MaterialButtonsPanel


class BIM_PT_styles(Panel):
    bl_label = "IFC Styles"
    bl_idname = "BIM_PT_styles"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_geometry"

    @classmethod
    def poll(cls, context):
        return IfcStore.get_file()

    def draw(self, context):
        if not StylesData.is_loaded:
            StylesData.load()

        self.props = context.scene.BIMStylesProperties

        row = self.layout.row(align=True)
        row.label(text="{} Styles Found".format(StylesData.data["total_styles"]), icon="MATERIAL")
        row = self.layout.row(align=True)
        if self.props.is_editing:
            row.operator("bim.disable_editing_styles", text="", icon="CANCEL")
        else:
            blenderbim.bim.helper.prop_with_search(row, self.props, "style_type", text="")
            row.operator("bim.load_styles", text="", icon="IMPORT").style_type = self.props.style_type
            return

        row = self.layout.row(align=True)
        row.alignment = "RIGHT"

        # row.operator("bim.add_presentation_style", text="", icon="ADD")
        if self.props.styles and self.props.active_style_index < len(self.props.styles):
            style = self.props.styles[self.props.active_style_index]
            op = row.operator("bim.select_by_style", text="", icon="RESTRICT_SELECT_OFF")
            op.style = style.ifc_definition_id
            row.operator("bim.remove_style", text="", icon="X").style = style.ifc_definition_id

        self.layout.template_list("BIM_UL_styles", "", self.props, "styles", self.props, "active_style_index")


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
    bl_label = "IFC Style"
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
    bl_label = "IFC Style Attributes"
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
            row = self.layout.row()
            row.operator("bim.enable_editing_style", icon="GREASEPENCIL", text="Edit")

            row = self.layout.row(align=True)
            row.label(text="STEP ID")
            row.label(text=str(mprops.ifc_style_id))

            for attribute in StyleAttributesData.data["attributes"]:
                row = self.layout.row(align=True)
                row.label(text=attribute["name"])
                row.label(text=attribute["value"])


class BIM_PT_external_style_attributes(Panel):
    bl_label = "IFC External Surface Style"
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
            row2 = row.row()
            row2.alignment = "RIGHT"
            row2.label(text=str(item.total_elements))


class BIM_PT_STYLE_GRAPH(Panel):
    bl_idname = "BIM_PT_style_graph"
    bl_space_type = "NODE_EDITOR"
    bl_label = "IFC Style Graph Settings"
    bl_region_type = "UI"
    bl_category = "BBIM"

    @classmethod
    def poll(cls, context):
        return getattr(context, "mat", None)

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
        layout.prop(props, "diffuse_color")

        if props.reflectance_method == "PHYSICAL":
            layout.prop(props, "metallic")

        if props.reflectance_method not in ("FLAT", "NOTDEFINED"):
            layout.prop(props, "roughness")
