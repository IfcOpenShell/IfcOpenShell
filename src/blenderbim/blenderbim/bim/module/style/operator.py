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

import os
import bpy
import blenderbim.bim.helper
import blenderbim.bim.handler
import blenderbim.tool as tool
import blenderbim.core.style as core
import ifcopenshell.util.representation
from pathlib import Path
from blenderbim.bim.ifc import IfcStore
from blenderbim.bim.module.style.data import StylesData, StyleAttributesData
from mathutils import Vector


class UpdateStyleColours(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.update_style_colours"
    bl_label = "Save Current Shading Style"
    bl_description = (
        "Save current style values to IfcSurfaceStyleShading.\n\n" + "ALT+CLICK to see saved values details"
    )
    bl_options = {"REGISTER", "UNDO"}

    verbose: bpy.props.BoolProperty(default=False, options={"SKIP_SAVE"})

    def invoke(self, context, event):
        # verobse print to console on alt+click
        # make sure to use SKIP_SAVE on property, otherwise it might get stuck
        if event.type == "LEFTMOUSE" and event.alt:
            self.verbose = True
        return self.execute(context)

    def _execute(self, context):
        mat = context.active_object.active_material
        core.update_style_colours(tool.Ifc, tool.Style, obj=mat, verbose=self.verbose)
        if self.verbose:
            self.report({"INFO"}, "Check the system console to see saved style properties")
        tool.Style.set_surface_style_props(mat)


class UpdateStyleTextures(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.update_style_textures"
    bl_label = "Update Style Textures"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        representation = ifcopenshell.util.representation.get_representation(
            tool.Ifc.get_entity(context.active_object), "Model", "Body", "MODEL_VIEW"
        )
        if representation:
            core.update_style_textures(
                tool.Ifc, tool.Style, obj=context.active_object.active_material, representation=representation
            )


class RemoveStyle(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_style"
    bl_label = "Remove Style"
    bl_options = {"REGISTER", "UNDO"}
    style: bpy.props.IntProperty()

    def _execute(self, context):
        core.remove_style(tool.Ifc, tool.Material, tool.Style, style=tool.Ifc.get().by_id(self.style))


class AddStyle(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_style"
    bl_label = "Add Style"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.add_style(tool.Ifc, tool.Style, obj=context.active_object.active_material)


class UnlinkStyle(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.unlink_style"
    bl_label = "Unlink Style"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.unlink_style(tool.Ifc, tool.Style, obj=context.active_object.active_material)


class EnableEditingStyle(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.enable_editing_style"
    bl_label = "Enable Editing Style"
    bl_options = {"REGISTER", "UNDO"}
    style: bpy.props.IntProperty(default=0)

    def _execute(self, context):
        props = bpy.context.scene.BIMStylesProperties
        style = tool.Ifc.get().by_id(self.style)
        props.is_editing_style = style.id()
        props.is_editing_class = "IfcSurfaceStyle"
        attributes = props.attributes
        attributes.clear()
        blenderbim.bim.helper.import_attributes2(style, attributes)


class DisableEditingStyle(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.disable_editing_style"
    bl_options = {"REGISTER", "UNDO"}
    bl_label = "Disable Editing Style"

    def _execute(self, context):
        props = bpy.context.scene.BIMStylesProperties
        props.is_editing_style = 0


class EditStyle(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.edit_style"
    bl_label = "Edit Style"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        props = bpy.context.scene.BIMStylesProperties
        style = tool.Ifc.get().by_id(props.is_editing_style)
        attributes = blenderbim.bim.helper.export_attributes(props.attributes)
        ifcopenshell.api.run("style.edit_presentation_style", tool.Ifc.get(), style=style, attributes=attributes)
        props.is_editing_style = 0
        core.load_styles(tool.Style, style_type=props.style_type)


class UpdateCurrentStyle(bpy.types.Operator):
    bl_idname = "bim.update_current_style"
    bl_label = "Update Current Style"
    bl_description = (
        "Update style for all selected objects according to current style type\n(Shading/External).\n\n"
        + "SHIFT+CLICK to update ALL styles in the .ifc file to current style type"
    )
    bl_options = {"REGISTER", "UNDO"}
    update_all: bpy.props.BoolProperty(name="Update All", default=False, options={"SKIP_SAVE"})

    @classmethod
    def poll(cls, context):
        poll = (
            context.active_object is not None
            and context.active_object.active_material is not None
            and context.active_object.active_material.BIMMaterialProperties.ifc_style_id != 0
        )
        if not poll:
            cls.poll_message_set(
                "Object is not selected or material is not assigned or material doesn't have IFC Style"
            )
        return poll

    def invoke(self, context, event):
        # updating all styles on shift+click
        # make sure to use SKIP_SAVE on property, otherwise it might get stuck
        if event.type == "LEFTMOUSE" and event.shift:
            self.update_all = True
        return self.execute(context)

    def execute(self, context):
        current_style_type = context.active_object.active_material.BIMStyleProperties.active_style_type
        if self.update_all:
            context.scene.BIMStylesProperties.active_style_type = current_style_type
            return {"FINISHED"}

        materials = []
        for obj in context.selected_objects:
            mat = obj.active_material
            if mat and mat.BIMMaterialProperties.ifc_style_id != 0:
                mat.BIMStyleProperties.active_style_type = current_style_type
        return {"FINISHED"}


class BrowseExternalStyle(bpy.types.Operator):
    bl_idname = "bim.browse_external_style"
    bl_label = "Browse External Style"
    bl_options = {"REGISTER", "UNDO"}

    filepath: bpy.props.StringProperty(
        name="File Path", description="Filepath used to import from", maxlen=1024, default="", subtype="FILE_PATH"
    )

    filter_glob: bpy.props.StringProperty(
        default="*.blend",
        options={"HIDDEN"},
    )

    def get_data_block_types(self, context):
        return [("materials", "materials", "materials")]
        # NOTE: the code below can be used later when we'll be adding other data-blocks besides materials
        l = [("0", "", "")]
        SUPPORTED_DATA_BLOCKS = ("materials", "textures", "brushes")
        if os.path.exists(self.filepath) and self.filepath.endswith(".blend"):
            with bpy.data.libraries.load(self.filepath) as (data_from, data_to):
                for data_block_type in dir(data_from):
                    if data_block_type not in SUPPORTED_DATA_BLOCKS:
                        continue
                    data = getattr(data_from, data_block_type)
                    if data:
                        item = (data_block_type,) * 3
                        l.append(item)
        return l

    def get_data_blocks(self, context):
        l = [("", "", "")]
        if self.data_block_type != "0" and os.path.exists(self.filepath) and self.filepath.endswith(".blend"):
            with bpy.data.libraries.load(self.filepath) as (data_from, data_to):
                objects = getattr(data_from, self.data_block_type)
                for o in objects:
                    l.append((o, o, o))
        return l

    data_block_type: bpy.props.EnumProperty(
        name="Data Block Type",
        description="List of data blocks in the .blend file",
        items=get_data_block_types,
    )

    data_block: bpy.props.EnumProperty(
        name="List of objects in the .blend file",
        description="List of objects in the .blend file",
        items=get_data_blocks,
    )
    use_relative_path: bpy.props.BoolProperty(name="Use Relative Path", default=True)
    directory: bpy.props.StringProperty(
        name="Directory",
        description="Start file browsing directory",
        default="",
    )

    def invoke(self, context, event):
        mat = context.active_object.active_material
        external_style = tool.Style.get_style_elements(mat).get("IfcExternallyDefinedSurfaceStyle", None)
        # automatically select previously selected external style in file browser
        if external_style and self.filepath == "":
            style_path = Path(tool.Ifc.resolve_uri(external_style.Location))
            self.directory = str(style_path.parent)
            self.filepath = str(style_path)
            self.data_block_type, self.data_block = external_style.Identification.split("/")

        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def draw(self, context):
        layout = self.layout
        layout.label(text="Data Block Type")
        layout.prop(self, "data_block_type", text="", icon="GROUP")
        layout.label(text="Data Block")
        layout.prop(self, "data_block", text="")
        if bpy.data.is_saved:
            layout.prop(self, "use_relative_path")
        else:
            self.use_relative_path = False
            layout.label(text="Save the .blend file first ")
            layout.label(text="to use relative paths for .ifc.")

    def execute(self, context):
        if self.data_block_type == "0":
            self.report({"ERROR"}, "Select a data block type")
            return {"CANCELLED"}

        if self.data_block == "":
            self.report({"ERROR"}, "Select a data block")
            return {"CANCELLED"}

        if not os.path.exists(self.filepath):
            self.report({"ERROR"}, f"File not found:\n'{self.filepath}'")
            return {"CANCELLED"}

        db = tool.Blender.append_data_block(self.filepath, self.data_block_type, self.data_block)
        if not db["data_block"]:
            self.report({"ERROR"}, db["msg"])
            return {"CANCELLED"}

        bpy.data.materials.remove(db["data_block"])

        if not StyleAttributesData.is_loaded:
            StyleAttributesData.load()
        external_style = StyleAttributesData.data["style_elements"].get("IfcExternallyDefinedSurfaceStyle", None)

        if self.use_relative_path:
            filepath = os.path.relpath(self.filepath, tool.Ifc.get_path())
        else:
            filepath = self.filepath
        filepath = Path(filepath).as_posix()

        attributes = {
            "Location": filepath,
            "Identification": f"{self.data_block_type}/{self.data_block}",
            "Name": self.data_block,
        }
        if not external_style:
            core.add_external_style(
                tool.Ifc, tool.Style, obj=context.active_object.active_material, attributes=attributes
            )
        else:
            core.update_external_style(tool.Ifc, tool.Style, external_style=external_style, attributes=attributes)

        StyleAttributesData.is_loaded = False
        return {"FINISHED"}


class EnableEditingExternalStyle(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.enable_editing_external_style"
    bl_label = "Enable Editing External Style"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.enable_editing_external_style(tool.Style, obj=context.active_object.active_material)


class DisableEditingExternalStyle(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.disable_editing_external_style"
    bl_options = {"REGISTER", "UNDO"}
    bl_label = "Disable Editing External Style"

    def _execute(self, context):
        core.disable_editing_external_style(tool.Style, obj=context.active_object.active_material)


class EditExternalStyle(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.edit_external_style"
    bl_label = "Edit External Style"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.edit_external_style(tool.Ifc, tool.Style, obj=context.active_object.active_material)


class ActivateExternalStyle(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.activate_external_style"
    bl_label = "Activate External Style"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    material_name: bpy.props.StringProperty(name="Material Name", default="")

    def _execute(self, context):
        if not self.material_name:
            material = context.active_object.active_material
        else:
            material = bpy.data.materials[self.material_name]
        external_style = tool.Style.get_style_elements(material)["IfcExternallyDefinedSurfaceStyle"]
        data_block_type, data_block = external_style.Identification.split("/")
        style_path = Path(tool.Ifc.resolve_uri(external_style.Location))

        if style_path.suffix != ".blend":
            self.report({"ERROR"}, f"Only Blender external styles are supported")
            return {"CANCELLED"}

        if not style_path.exists():
            self.report({"ERROR"}, f"File not found:\n'{style_path}'")
            return {"CANCELLED"}

        db = tool.Blender.append_data_block(str(style_path), data_block_type, data_block)
        if not db["data_block"]:
            self.report({"ERROR"}, db["msg"])
            return {"CANCELLED"}

        props_to_copy = [
            "diffuse_color",
            "metallic",
            "roughness",
            "specular_intensity",
            "use_nodes",
        ]
        for prop_name in props_to_copy:
            setattr(material, prop_name, getattr(db["data_block"], prop_name))

        if material.use_nodes:
            tool.Blender.copy_node_graph(material, db["data_block"])
        bpy.data.materials.remove(db["data_block"])


class DisableEditingStyles(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.disable_editing_styles"
    bl_options = {"REGISTER", "UNDO"}
    bl_label = "Disable Editing Styles"

    def _execute(self, context):
        core.disable_editing_styles(tool.Style)


class LoadStyles(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.load_styles"
    bl_label = "Load Styles"
    bl_options = {"REGISTER", "UNDO"}
    style_type: bpy.props.StringProperty()

    def _execute(self, context):
        core.load_styles(tool.Style, style_type=self.style_type)


class SelectByStyle(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.select_by_style"
    bl_label = "Select By Style"
    bl_options = {"REGISTER", "UNDO"}
    style: bpy.props.IntProperty()

    def _execute(self, context):
        core.select_by_style(tool.Style, tool.Spatial, style=tool.Ifc.get().by_id(self.style))


class ClearTextureMapPath(bpy.types.Operator):
    bl_idname = "bim.clear_texture_map_path"
    bl_label = "Clear Texture Map Path"
    bl_options = {"REGISTER", "UNDO"}
    texture_map_prop: bpy.props.StringProperty(default="")

    @classmethod
    def poll(cls, context):
        poll = getattr(context, "material", None)
        if not poll:
            cls.poll_message_set("Select a material")
        return poll

    def execute(self, context):
        if not self.texture_map_prop:
            self.report({"ERROR"}, "Provide a texture map")
            return {"CANCELLED"}
        props = context.material.BIMStyleProperties
        setattr(props, self.texture_map_prop, "")
        return {"FINISHED"}


class EnableAddingPresentationStyle(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.enable_adding_presentation_style"
    bl_label = "Enable Add Presentation Style"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        props = bpy.context.scene.BIMStylesProperties
        props.is_adding = True


class DisableAddingPresentationStyle(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.disable_adding_presentation_style"
    bl_label = "Disable Add Presentation Style"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        props = bpy.context.scene.BIMStylesProperties
        props.is_adding = False


class AddPresentationStyle(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_presentation_style"
    bl_label = "Add Presentation Style"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        props = bpy.context.scene.BIMStylesProperties
        if props.style_type == "IfcSurfaceStyle":
            style = ifcopenshell.api.run("style.add_style", tool.Ifc.get(), name=props.style_name)
            if props.surface_style_class in ("IfcSurfaceStyleShading", "IfcSurfaceStyleRendering"):
                surface_style = ifcopenshell.api.run(
                    "style.add_surface_style",
                    tool.Ifc.get(),
                    style=style,
                    ifc_class=props.surface_style_class,
                    attributes={
                        "SurfaceColour": {
                            "Name": None,
                            "Red": props.surface_colour[0],
                            "Green": props.surface_colour[1],
                            "Blue": props.surface_colour[2],
                        }
                    },
                )
                if props.surface_style_class == "IfcSurfaceStyleRendering":
                    surface_style.ReflectanceMethod = "NOTDEFINED"
            material = bpy.data.materials.new(style.Name)
            tool.Ifc.link(style, material)
            material.use_fake_user = True
            if surface_style.is_a("IfcSurfaceStyleShading"):
                tool.Loader.create_surface_style_shading(material, surface_style)
            elif surface_style.is_a("IfcSurfaceStyleRendering"):
                tool.Loader.create_surface_style_rendering(material, surface_style)
        props.is_adding = False
        core.load_styles(tool.Style, style_type=props.style_type)


class EnableEditingSurfaceStyle(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.enable_editing_surface_style"
    bl_label = "Enable Editing Surface Style"
    bl_options = {"REGISTER", "UNDO"}
    style: bpy.props.IntProperty(default=0)
    ifc_class: bpy.props.StringProperty(default="")

    def _execute(self, context):
        props = bpy.context.scene.BIMStylesProperties
        style = tool.Ifc.get().by_id(self.style)

        shading = None

        surface_style = None
        for style2 in style.Styles:
            if style2.is_a() == self.ifc_class:
                surface_style = style2
            if style2.is_a() == "IfcSurfaceStyleShading":
                shading = style2

        color_to_tuple = lambda x: (x.Red, x.Green, x.Blue)

        if surface_style:
            if self.ifc_class == "IfcSurfaceStyleShading":
                props.surface_colour = color_to_tuple(surface_style.SurfaceColour)
                props.transparency = surface_style.Transparency or 0.0
            elif self.ifc_class == "IfcSurfaceStyleRendering":
                props.surface_colour = color_to_tuple(surface_style.SurfaceColour)
                props.transparency = surface_style.Transparency or 0.0

                if surface_style.DiffuseColour:
                    props.is_diffuse_colour_null = False
                    if surface_style.DiffuseColour.is_a("IfcColourRgb"):
                        props.diffuse_colour_class = "IfcColourRgb"
                        props.diffuse_colour = color_to_tuple(surface_style.DiffuseColour)
                    else:
                        props.diffuse_colour_class = "IfcNormalisedRatioMeasure"
                        props.diffuse_colour_ratio = surface_style.DiffuseColour.wrappedValue
                else:
                    props.is_diffuse_colour_null = False

                if surface_style.SpecularColour:
                    props.is_specular_colour_null = False
                    if surface_style.SpecularColour.is_a("IfcColourRgb"):
                        props.specular_colour_class = "IfcColourRgb"
                        props.specular_colour = color_to_tuple(surface_style.SpecularColour)
                    else:
                        props.specular_colour_class = "IfcNormalisedRatioMeasure"
                        props.specular_colour_ratio = surface_style.SpecularColour.wrappedValue
                else:
                    props.is_specular_colour_null = False

                if surface_style.SpecularHighlight:
                    props.is_specular_highlight_null = False
                    if surface_style.SpecularHighlight.is_a("IfcSpecularRoughness"):
                        props.specular_highlight = surface_style.SpecularHighlight.wrappedValue
                    else:
                        props.is_specular_highlight_null = False  # Exponent is meaningless
                else:
                    props.is_specular_highlight_null = True

                props.reflectance_method = surface_style.ReflectanceMethod
            elif self.ifc_class == "IfcExternallyDefinedSurfaceStyle":
                attributes = props.external_style_attributes
                attributes.clear()
                blenderbim.bim.helper.import_attributes2(surface_style, attributes)
        else:
            if self.ifc_class == "IfcSurfaceStyleRendering":
                if shading:
                    props.surface_colour = color_to_tuple(shading.SurfaceColour)
                    props.transparency = shading.Transparency or 0.0
            elif self.ifc_class == "IfcExternallyDefinedSurfaceStyle":
                attributes = props.external_style_attributes
                attributes.clear()
                blenderbim.bim.helper.import_attributes2(self.ifc_class, attributes)

        props.is_editing_style = self.style
        props.is_editing_class = self.ifc_class


class EditSurfaceStyle(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.edit_surface_style"
    bl_label = "Edit Surface Style"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        self.props = bpy.context.scene.BIMStylesProperties
        self.style = tool.Ifc.get().by_id(self.props.is_editing_style)

        self.surface_style = None
        self.shading_style = None
        self.rendering_style = None
        for style2 in self.style.Styles:
            if style2.is_a() == self.props.is_editing_class:
                self.surface_style = style2
            if style2.is_a() == "IfcSurfaceStyleShading":
                self.shading_style = style2
            if style2.is_a() == "IfcSurfaceStyleRendering":
                self.rendering_style = style2

        if self.surface_style:
            self.edit_existing_style()
        else:
            self.add_new_style()

        self.props.is_editing_style = 0
        core.load_styles(tool.Style, style_type=self.props.style_type)

    def edit_existing_style(self):
        material = tool.Ifc.get_object(self.style)
        if self.surface_style.is_a() == "IfcSurfaceStyleShading":
            ifcopenshell.api.run(
                "style.edit_surface_style",
                tool.Ifc.get(),
                style=self.surface_style,
                attributes={
                    "SurfaceColour": self.color_to_dict(self.props.surface_colour),
                    "Transparency": self.props.transparency or None,
                },
            )
            tool.Loader.create_surface_style_shading(material, self.surface_style)
        elif self.surface_style.is_a() == "IfcSurfaceStyleRendering":
            ifcopenshell.api.run(
                "style.edit_surface_style",
                tool.Ifc.get(),
                style=self.surface_style,
                attributes=self.get_rendering_attributes(),
            )
            tool.Loader.create_surface_style_rendering(material, self.surface_style)
        elif self.surface_style.is_a() == "IfcExternallyDefinedSurfaceStyle":
            surface_style = ifcopenshell.api.run(
                "style.edit_surface_style",
                tool.Ifc.get(),
                style=self.surface_style,
                attributes=blenderbim.bim.helper.export_attributes(self.props.external_style_attributes),
            )

    def add_new_style(self):
        material = tool.Ifc.get_object(self.style)
        if self.props.is_editing_class == "IfcSurfaceStyleShading":
            surface_style = ifcopenshell.api.run(
                "style.add_surface_style",
                tool.Ifc.get(),
                style=self.style,
                ifc_class="IfcSurfaceStyleShading",
                attributes=self.get_shading_attributes(),
            )
            tool.Loader.create_surface_style_shading(material, surface_style)
        elif self.props.is_editing_class == "IfcSurfaceStyleRendering":
            surface_style = ifcopenshell.api.run(
                "style.add_surface_style",
                tool.Ifc.get(),
                style=self.style,
                ifc_class="IfcSurfaceStyleRendering",
                attributes=self.get_rendering_attributes(),
            )
            tool.Loader.create_surface_style_rendering(material, surface_style)
        elif self.props.is_editing_class == "IfcExternallyDefinedSurfaceStyle":
            surface_style = ifcopenshell.api.run(
                "style.add_surface_style",
                tool.Ifc.get(),
                style=self.style,
                ifc_class="IfcExternallyDefinedSurfaceStyle",
                attributes=blenderbim.bim.helper.export_attributes(self.props.external_style_attributes),
            )

    def get_shading_attributes(self):
        return {
            "SurfaceColour": self.color_to_dict(self.props.surface_colour),
            "Transparency": self.props.transparency or None,
        }

    def get_rendering_attributes(self):
        if self.props.is_diffuse_colour_null:
            diffuse_colour = None
        elif self.props.diffuse_colour_class == "IfcColourRgb":
            diffuse_colour = self.color_to_dict(self.props.diffuse_colour)
        elif self.props.diffuse_colour_class == "IfcNormalisedRatioMeasure":
            diffuse_colour = self.props.diffuse_colour_ratio

        if self.props.is_specular_colour_null:
            specular_colour = None
        elif self.props.specular_colour_class == "IfcColourRgb":
            specular_colour = self.color_to_dict(self.props.specular_colour)
        elif self.props.specular_colour_class == "IfcNormalisedRatioMeasure":
            specular_colour = self.props.specular_colour_ratio

        if self.props.is_specular_highlight_null:
            specular_highlight = None
        else:
            specular_highlight = {"SpecularRoughness": self.props.specular_highlight}

        return {
            "SurfaceColour": self.color_to_dict(self.props.surface_colour),
            "Transparency": self.props.transparency or None,
            "ReflectanceMethod": self.props.reflectance_method,
            "DiffuseColour": diffuse_colour,
            "SpecularColour": specular_colour,
            "SpecularHighlight": specular_highlight,
        }

    def color_to_dict(self, x):
        return {"Red": x[0], "Green": x[1], "Blue": x[2]}


class SaveUVToStyle(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.save_uv_to_style"
    bl_label = "Save UV To Style"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        context = bpy.context
        ifc_file = tool.Ifc.get()
        material = context.active_object.active_material
        obj = context.active_object

        # find active style item
        style_id = material.BIMMaterialProperties.ifc_style_id
        style = ifc_file.by_id(style_id)

        def get_active_representation_items():
            representation = tool.Geometry.get_active_representation(obj)
            representation = ifcopenshell.util.representation.resolve_representation(representation)
            items = []
            for item in representation.Items:
                if item.is_a("IfcMappedItem"):
                    items.extend(item.MappingSource.MappedRepresentation.Items)
                items.append(item)
            return items

        all_styled_items = set(tool.Style.get_styled_items(style))
        active_representation_items = set(get_active_representation_items())

        if not active_representation_items.issubset(all_styled_items):
            self.report(
                {"ERROR"},
                "Not all items of the current representation are styled by the active style, not yet supported",
            )
            return {"CANCELLED"}

        if any(not i.is_a("IfcPolygonalFaceSet") for i in active_representation_items):
            self.report({"ERROR"}, "One of the items is not IfcPolygonalFaceSet, not yet supported.")
            return {"CANCELLED"}

        for faceset in active_representation_items:
            if any(len(f.CoordIndex) != 3 for f in faceset.Faces):
                self.report({"ERROR"}, "One of the facesets is not triangulated, not yet supported.")
                return {"CANCELLED"}

        if len(active_representation_items) != 1:
            self.report({"ERROR"}, "Only 1 faceset item is supported.")
            return {"CANCELLED"}

        texture_style = tool.Style.get_texture_style(material)
        if not texture_style:
            self.report({"ERROR"}, "No texture style found, not yet supported.")
            return {"CANCELLED"}

        # unmap preivously used IfcIndexedTextureMap
        # TODO: remove orphaned data?
        textures = set(texture_style.Textures)
        coords = set()
        for texture in textures:
            coords.update(texture.IsMappedBy or [])
        for coord in coords:
            if coord.is_a("IfcIndexedTextureMap") and coord.MappedTo in active_representation_items:
                coord.Maps = list(set(coord.Maps) - textures)

        mesh = obj.data
        uv_indices = []
        uv_verts = [uv.vector for uv in mesh.uv_layers.active.uv]

        si_conversion = ifcopenshell.util.unit.calculate_unit_scale(ifc_file)

        for faceset in active_representation_items:
            # remap the faceset CoordList index to the vertices in blender mesh
            coordinates_remap = []
            remap_failed = False
            ifc_coordinates = faceset.Coordinates.CoordList
            for co in ifc_coordinates:
                co = Vector(co) * si_conversion
                index = next((v.index for v in mesh.vertices if (v.co - co).length_squared < 1e-5), None)
                coordinates_remap.append(index)
                if index is None:
                    remap_failed = True
            # ifc indices start with 1
            remap_verts_to_blender = lambda ifc_verts: [coordinates_remap[i - 1] for i in ifc_verts]

            if remap_failed or len(ifc_coordinates) != len(mesh.vertices):
                self.report({"ERROR"}, "Mesh vertices doesn't match IFC faceset vertices.")
                return {"CANCELLED"}

            # safe check as I'm not sure indices in Blender and IFC match
            faces_remap = [remap_verts_to_blender(triangle_face.CoordIndex) for triangle_face in faceset.Faces]

            for ifc_face_remapped in faces_remap:
                for blender_face in mesh.polygons:
                    blender_face_verts = blender_face.vertices[:]
                    # assume that blender verts order can be different
                    if set(blender_face_verts) == set(ifc_face_remapped):
                        blender_face_loops = blender_face.loop_indices[:]
                        face_uv_indices = [
                            blender_face_loops[blender_face_verts.index(i)] + 1 for i in ifc_face_remapped
                        ]
                        uv_indices.append(face_uv_indices)
                        break
                else:
                    self.report({"ERROR"}, "Couldn't find matching blender face for ifc face.")
                    return {"CANCELLED"}

            texture_coord = ifc_file.create_entity("IfcIndexedTriangleTextureMap")
            texture_coord.Maps = list(textures)
            texture_coord.MappedTo = faceset

            texture_coord.TexCoordIndex = uv_indices
            uv_verts_list = ifc_file.create_entity("IfcTextureVertexList")
            uv_verts_list.TexCoordsList = uv_verts
            texture_coord.TexCoords = uv_verts_list

        self.report({"INFO"}, f"UV saved to the style {style.Name}")

        return {"FINISHED"}
