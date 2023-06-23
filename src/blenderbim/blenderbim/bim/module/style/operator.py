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
import blenderbim.bim.handler
import blenderbim.tool as tool
import blenderbim.core.style as core
import ifcopenshell.util.representation
from blenderbim.bim.ifc import IfcStore
from blenderbim.bim.module.style.data import StylesData, StyleAttributesData
from pathlib import Path
import os


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

    def _execute(self, context):
        core.enable_editing_style(tool.Style, obj=context.active_object.active_material)


class DisableEditingStyle(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.disable_editing_style"
    bl_options = {"REGISTER", "UNDO"}
    bl_label = "Disable Editing Style"

    def _execute(self, context):
        core.disable_editing_style(tool.Style, obj=context.active_object.active_material)


class EditStyle(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.edit_style"
    bl_label = "Edit Style"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.edit_style(tool.Ifc, tool.Style, obj=context.active_object.active_material)


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
            filepath = os.path.relpath(self.filepath, bpy.path.abspath("//"))
        else:
            filepath = self.filepath

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
    bl_label = "Select By Material"
    bl_options = {"REGISTER", "UNDO"}
    style: bpy.props.IntProperty()

    def _execute(self, context):
        core.select_by_style(tool.Style, tool.Spatial, style=tool.Ifc.get().by_id(self.style))
