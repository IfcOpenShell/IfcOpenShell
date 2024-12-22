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

import os
import bpy
import bonsai.bim.helper
import bonsai.tool as tool
import bonsai.core.style as core
import ifcopenshell.api
import ifcopenshell.api.style
import ifcopenshell.util.representation
import ifcopenshell.util.unit
from pathlib import Path
from mathutils import Vector
from typing import Any, Union


# TODO: is this still relevant or can it be deleted?
class UpdateStyleColours(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.update_style_colours"
    bl_label = "Save Current Shading Style"
    bl_description = (
        "Update IfcSurfaceStyleShading based on current blender material shading graph.\n\n"
        + "ALT+CLICK to see saved values details"
    )
    bl_options = {"REGISTER", "UNDO"}

    verbose: bpy.props.BoolProperty(default=False, options={"SKIP_SAVE"})

    def invoke(self, context, event):
        # verbose print to console on alt+click
        # make sure to use SKIP_SAVE on property, otherwise it might get stuck
        if event.type == "LEFTMOUSE" and event.alt:
            self.verbose = True
        return self.execute(context)

    def _execute(self, context):
        mat = context.active_object.active_material
        core.update_style_colours(tool.Ifc, tool.Style, obj=mat, verbose=self.verbose)
        if self.verbose:
            self.report({"INFO"}, "Check the system console to see saved style properties")


# TODO: is this still relevant or can it be deleted?
class UpdateStyleTextures(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.update_style_textures"
    bl_label = "Update Style Textures"
    bl_description = "Update IfcSurfaceStyleWithTextures based on current blender material shading graph"
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
        core.remove_style(tool.Ifc, tool.Style, style=tool.Ifc.get().by_id(self.style), reload_styles_ui=True)


class AddStyle(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_style"
    bl_label = "Add Style"
    bl_description = "Add IfcSurfaceStyle to the active material"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.add_style(tool.Ifc, tool.Style, obj=context.active_object.active_material)


class UnlinkStyle(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.unlink_style"
    bl_label = "Unlink Style"
    bl_description = (
        "Unlink Blender material from it's linked IFC style.\n\n"
        "You can either remove style the material is linked to from IFC or keep it. "
        "Note that keeping the style in IFC might lead to unpredictable issues "
        "and should be used only by advanced users"
    )
    bl_options = {"REGISTER", "UNDO"}
    blender_material: bpy.props.StringProperty(name="Blender Material")
    should_delete: bpy.props.BoolProperty(name="Delete IFC Style", default=True)

    def draw(self, context):
        row = self.layout.row()
        row.prop(self, "should_delete")

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def _execute(self, context):
        # TODO: move to core.style
        # Don't check blender_material and style_id as this operator is only called from UI.
        assert isinstance(self.blender_material, str)  # Type checker.
        material = bpy.data.materials[self.blender_material]
        style_id = material.BIMStyleProperties.ifc_definition_id
        style = tool.Ifc.get_entity_by_id(style_id)

        # Material is linked to a style from a different project.
        if not style or tool.Ifc.get_object(style) != material:
            tool.Ifc.unlink(obj=material)
            return {"FINISHED"}

        # Create a copy that will be removed / left unassigned
        # and leave user with unlinked original material.
        #
        # Note should_delete=False creates a weird session state
        # when style is assigned to geometry in IFC
        # but mesh material is using some non-IFC Blender material instead.
        # In this case we still create a material copy and relink style to it,
        # so it will be still safe to assume that get_object(surface_style) is not None
        # saving us from possible errors.
        material_copy = material.copy()
        tool.Ifc.unlink(element=style)
        tool.Ifc.link(style, material_copy)
        if self.should_delete:
            core.remove_style(tool.Ifc, tool.Style, style)
        else:
            material_copy.use_fake_user = True
            # Need to reload Styles UI since it's item is now pointing to wrong Blender material.
            if (
                tool.Style.is_editing_styles()
                and (style_type := tool.Style.get_active_style_type())
                and style_type == style.is_a()
            ):
                tool.Style.import_presentation_styles(style_type)

        # Ensure there won't be any style sync on project save:
        # bim.update_representation would create new IfcSurfaceStyle
        # for unlinked blender material.
        updated_meshes = set()
        for obj in bpy.data.objects:
            mesh = obj.data
            if not isinstance(mesh, bpy.types.Mesh):
                continue
            if not mesh.BIMMeshProperties.ifc_definition_id:
                continue
            if mesh in updated_meshes:
                continue
            if not mesh.materials.get(material.name):
                continue
            tool.Geometry.record_object_materials(obj)
            updated_meshes.add(mesh)

        return {"FINISHED"}


class EnableEditingStyle(bpy.types.Operator):
    bl_idname = "bim.enable_editing_style"
    bl_label = "Enable Editing Style"
    bl_options = {"REGISTER", "UNDO"}
    style: bpy.props.IntProperty(default=0)

    def execute(self, context):
        core.enable_editing_style(tool.Style, tool.Ifc.get().by_id(self.style))
        return {"FINISHED"}


class DisableEditingStyle(bpy.types.Operator):
    bl_idname = "bim.disable_editing_style"
    bl_options = {"REGISTER", "UNDO"}
    bl_label = "Disable Editing Style"

    def execute(self, context):
        core.disable_editing_style(tool.Style)
        return {"FINISHED"}


class EditStyle(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.edit_style"
    bl_label = "Edit Style"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.edit_style(tool.Ifc, tool.Style)


class UpdateCurrentStyle(bpy.types.Operator):
    bl_idname = "bim.update_current_style"
    bl_label = "Update Current Style"
    bl_description = (
        "Update style for all selected objects according to current style type\n(Shading/External).\n\n"
        + "SHIFT+CLICK to update ALL styles in the .ifc file to current style type"
    )
    bl_options = {"REGISTER", "UNDO"}
    update_all: bpy.props.BoolProperty(name="Update All", default=False, options={"SKIP_SAVE"})
    style_id: bpy.props.IntProperty(default=0, options={"SKIP_SAVE"})

    def invoke(self, context, event):
        # updating all styles on shift+click
        # make sure to use SKIP_SAVE on property, otherwise it might get stuck
        if event.type == "LEFTMOUSE" and event.shift:
            self.update_all = True
        return self.execute(context)

    def execute(self, context):
        style = tool.Ifc.get().by_id(self.style_id)
        material = tool.Ifc.get_object(style)
        current_style_type = material.BIMStyleProperties.active_style_type

        if self.update_all:
            context.scene.BIMStylesProperties.active_style_type = current_style_type
            return {"FINISHED"}

        updated_materials = set()
        for obj in context.selected_objects:
            for mat in obj.data.materials:
                if mat and mat not in updated_materials and mat.BIMStyleProperties.ifc_definition_id != 0:
                    mat.BIMStyleProperties.active_style_type = current_style_type
                    updated_materials.add(mat)
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
    use_relative_path: bpy.props.BoolProperty(
        name="Use Relative Path", description="Save path relative to IFC file", default=True
    )
    directory: bpy.props.StringProperty(
        name="Directory",
        description="Start file browsing directory",
        default="",
    )
    active_surface_style_id: bpy.props.IntProperty(
        description="Currently selected IfcSurfaceStyle ID to automatically select it in the file browser",
        options={"HIDDEN", "SKIP_SAVE"},
    )

    def invoke(self, context, event):
        style_elements = None
        if self.active_surface_style_id:
            style = tool.Ifc.get().by_id(self.active_surface_style_id)
            style_elements = tool.Style.get_style_elements(style)

        # automatically select previously selected external style in file browser
        # if it exists in the file
        if style_elements and self.filepath == "" and tool.Style.has_blender_external_style(style_elements):
            external_style = style_elements["IfcExternallyDefinedSurfaceStyle"]
            style_path = Path(tool.Ifc.resolve_uri(external_style.Location))
            self.directory = str(style_path.parent)
            self.filepath = str(style_path)

            data_block_type, data_block = external_style.Identification.split("/")
            self.data_block_type = data_block_type
            data_blocks = [d[0] for d in self.get_data_blocks(context)]
            if data_block in data_blocks:
                self.data_block = data_block

        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def draw(self, context):
        layout = self.layout
        layout.label(text="Data Block Type")
        layout.prop(self, "data_block_type", text="", icon="GROUP")
        layout.label(text="Data Block")
        cls = BrowseExternalStyle
        bonsai.bim.helper.prop_with_search(
            layout, self, "data_block", text="", original_operator_path=f"{cls.__module__}.{cls.__name__}"
        )
        if Path(tool.Ifc.get_path()).is_file():
            layout.prop(self, "use_relative_path")
        else:
            self.use_relative_path = False
            layout.label(text="Save the .ifc file first ")
            layout.label(text="to use relative paths.")

    def execute(self, context):
        if self.data_block_type == "0":
            self.report({"ERROR"}, "Select a data block type in the side panel of the file browser")
            return {"CANCELLED"}

        if self.data_block == "":
            self.report({"ERROR"}, "Select a data block in the side panel of the file browser")
            return {"CANCELLED"}

        if not os.path.exists(self.filepath):
            self.report({"ERROR"}, f"File not found:\n'{self.filepath}'")
            return {"CANCELLED"}

        db = tool.Blender.append_data_block(self.filepath, self.data_block_type, self.data_block)
        if not db["data_block"]:
            self.report({"ERROR"}, db["msg"])
            return {"CANCELLED"}

        bpy.data.materials.remove(db["data_block"])

        if self.use_relative_path:
            filepath = os.path.relpath(self.filepath, Path(tool.Ifc.get_path()).parent)
        else:
            filepath = self.filepath
        filepath = Path(filepath).as_posix()

        attributes = context.scene.BIMStylesProperties.external_style_attributes
        attributes["Location"].string_value = filepath
        attributes["Identification"].string_value = f"{self.data_block_type}/{self.data_block}"
        attributes["Name"].string_value = self.data_block

        style = tool.Ifc.get().by_id(self.active_surface_style_id)
        bpy.ops.bim.activate_external_style(material_name=tool.Ifc.get_object(style).name)
        return {"FINISHED"}


class ActivateExternalStyle(bpy.types.Operator):
    bl_idname = "bim.activate_external_style"
    bl_label = "Activate External Style"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    material_name: bpy.props.StringProperty(name="Material Name", default="")

    def execute(self, context):
        if not self.material_name:
            material = context.active_object.active_material
        else:
            material = bpy.data.materials[self.material_name]

        style = tool.Ifc.get_entity(material)
        if not style:
            self.report({"INFO"}, "Material '{self.material_name}' is not an IFC style.")
            return {"CANCELLED"}

        props = context.scene.BIMStylesProperties
        if props.is_editing_style == style.id() and props.is_editing_class == "IfcExternallyDefinedSurfaceStyle":
            location = props.external_style_attributes["Location"].string_value
            identification = props.external_style_attributes["Identification"].string_value
        else:
            external_style = tool.Style.get_style_elements(material)["IfcExternallyDefinedSurfaceStyle"]
            location = external_style.Location
            identification = external_style.Identification

        data_block_type, data_block = identification.split("/")
        style_path = Path(tool.Ifc.resolve_uri(location))

        if style_path.suffix != ".blend":
            self.report(
                {"ERROR"},
                f'Error loading external style for "{material.name}" - only Blender external styles are supported',
            )
            return {"CANCELLED"}

        if not style_path.exists():
            self.report(
                {"ERROR"}, f"Error loading external style for \"{material.name}\" - cannot find file: '{style_path}'"
            )
            return {"CANCELLED"}

        db = tool.Blender.append_data_block(str(style_path), data_block_type, data_block)
        if not db["data_block"]:
            self.report({"ERROR"}, f"Error loading external style for \"{material.name}\" - {db['msg']}")
            return {"CANCELLED"}

        self.copy_material_attributes(db["data_block"], material)
        if material.use_nodes:
            tool.Blender.copy_node_graph(material, db["data_block"])
        bpy.data.materials.remove(db["data_block"])
        return {"FINISHED"}

    def copy_material_attributes(self, source, target):
        ID_properties = bpy.types.ID.bl_rna.properties
        material_props = bpy.types.Material.bl_rna.properties
        allowed_prop_groups = ("grease_pencil", "lineart", "cycles")

        def set_prop(prop_name):
            # temporary workaround for Blender bug https://projects.blender.org/blender/blender/issues/116325
            if prop_name == "paint_active_slot":
                return
            setattr(target, prop_name, getattr(source, prop_name))

        def set_prop_group(prop_group):
            source_prop_group = getattr(source, prop_group)
            target_prop_group = getattr(target, prop_group)
            if target_prop_group is None or target_prop_group is None:
                return
            for prop_name in source_prop_group.bl_rna.properties.keys():
                prop = source_prop_group.bl_rna.properties[prop_name]
                if prop.type in ("POINTER", "COLLECTION"):
                    continue
                if prop.is_readonly:
                    continue
                source_value = getattr(source_prop_group, prop_name)
                setattr(target_prop_group, prop_name, source_value)

        for prop_name in material_props.keys():
            if prop_name in ID_properties:
                continue
            prop = material_props[prop_name]
            if prop.type == "COLLECTION":
                continue
            if prop.type == "POINTER":
                if prop_name in allowed_prop_groups:
                    set_prop_group(prop_name)
                continue
            if prop.is_readonly:
                continue
            set_prop(prop_name)


class DisableEditingStyles(bpy.types.Operator):
    bl_idname = "bim.disable_editing_styles"
    bl_options = {"REGISTER", "UNDO"}
    bl_label = "Disable Editing Styles"

    def execute(self, context):
        core.disable_editing_styles(tool.Style)
        return {"FINISHED"}


class LoadStyles(bpy.types.Operator):
    bl_idname = "bim.load_styles"
    bl_label = "Load Styles"
    bl_options = {"REGISTER", "UNDO"}
    style_type: bpy.props.StringProperty()

    def execute(self, context):
        style_type = self.style_type if self.style_type else context.scene.BIMStylesProperties.style_type
        core.load_styles(tool.Style, style_type=style_type)
        bonsai.bim.handler.refresh_ui_data()
        return {"FINISHED"}


class SelectByStyle(bpy.types.Operator):
    bl_idname = "bim.select_by_style"
    bl_label = "Select By Style"
    bl_description = "Select objects using the provided style"
    bl_options = {"REGISTER", "UNDO"}
    style: bpy.props.IntProperty()

    def execute(self, context):
        core.select_by_style(tool.Style, tool.Spatial, style=tool.Ifc.get().by_id(self.style))
        return {"FINISHED"}


class ChooseTextureMapPath(bpy.types.Operator):
    bl_idname = "bim.choose_texture_map_path"
    bl_label = "Choose Texture Map Path"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}
    texture_map_index: bpy.props.IntProperty(default=-1, options={"SKIP_SAVE"})

    use_relative_path: bpy.props.BoolProperty(
        name="Use Relative Path", description="Save path relative to IFC file", default=True
    )
    filepath: bpy.props.StringProperty(
        name="File Path", description="Filepath used to import from", maxlen=1024, default="", subtype="FILE_PATH"
    )
    filter_image: bpy.props.BoolProperty(default=True, options={"HIDDEN", "SKIP_SAVE"})
    filter_folder: bpy.props.BoolProperty(default=True, options={"HIDDEN", "SKIP_SAVE"})

    def draw(self, context):
        layout = self.layout
        if Path(tool.Ifc.get_path()).is_file():
            layout.prop(self, "use_relative_path")
        else:
            self.use_relative_path = False
            layout.label(text="Save the .ifc file first ")
            layout.label(text="to use relative paths.")

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        if self.texture_map_index < 0:
            self.report({"ERROR"}, "Provide a texture map index")
            return {"CANCELLED"}

        abs_path = Path(self.filepath)
        if self.use_relative_path:
            parent = Path(tool.Ifc.get_path()).parent
            if abs_path.is_relative_to(parent):
                image_filepath = abs_path.relative_to(parent)
            else:
                self.report({"INFO"}, "Path is not relative to the .ifc file, it will be saved as absolute.")
                image_filepath = abs_path
        else:
            image_filepath = abs_path

        texture = context.scene.BIMStylesProperties.textures[self.texture_map_index]
        texture.path = image_filepath.as_posix()
        return {"FINISHED"}


class RemoveTextureMap(bpy.types.Operator):
    bl_idname = "bim.remove_texture_map"
    bl_label = "Remove Texture Map"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}
    texture_map_index: bpy.props.IntProperty(default=-1, options={"SKIP_SAVE"})

    def execute(self, context):
        if self.texture_map_index < 0:
            self.report({"ERROR"}, "Provide a texture map index")
            return {"CANCELLED"}

        props = context.scene.BIMStylesProperties
        props.textures.remove(self.texture_map_index)
        # just to trigger shader graph update
        props.surface_colour = props.surface_colour
        return {"FINISHED"}


class EnableAddingPresentationStyle(bpy.types.Operator):
    bl_idname = "bim.enable_adding_presentation_style"
    bl_label = "Enable Add Presentation Style"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if not tool.Ifc.get():
            return False
        style_type = tool.Style.get_active_style_type()
        if style_type != "IfcSurfaceStyle":
            cls.poll_message_set(f"Adding {style_type} is not currently supported.")
            return False
        return True

    def execute(self, context):
        tool.Style.enable_adding_presentation_style()
        return {"FINISHED"}


class DuplicateStyle(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.duplicate_style"
    bl_label = "Duplicate Style"
    bl_options = {"REGISTER", "UNDO"}

    style: bpy.props.IntProperty(name="Style ID")

    def _execute(self, context):
        style_type = context.scene.BIMStylesProperties.style_type
        ifc_file = tool.Ifc.get()
        style = ifc_file.by_id(self.style)
        tool.Style.duplicate_style(style)
        bpy.ops.bim.disable_editing_styles()
        bpy.ops.bim.load_styles(style_type=style_type)


class DisableAddingPresentationStyle(bpy.types.Operator):
    bl_idname = "bim.disable_adding_presentation_style"
    bl_label = "Disable Add Presentation Style"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        tool.Style.disable_adding_presentation_style()
        return {"FINISHED"}


class AddPresentationStyle(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_presentation_style"
    bl_label = "Add Presentation Style"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        props = bpy.context.scene.BIMStylesProperties
        if props.style_type == "IfcSurfaceStyle":
            style = ifcopenshell.api.run("style.add_style", tool.Ifc.get(), name=props.style_name)

            # setup surface style element
            surface_style = None
            if props.surface_style_class in ("IfcSurfaceStyleShading", "IfcSurfaceStyleRendering"):
                attributes = {
                    "SurfaceColour": {
                        "Name": None,
                        "Red": props.surface_colour[0],
                        "Green": props.surface_colour[1],
                        "Blue": props.surface_colour[2],
                    }
                }
                if props.surface_style_class == "IfcSurfaceStyleRendering":
                    attributes["ReflectanceMethod"] = "NOTDEFINED"
            else:
                # NOTE: for all other styles we produce just empty styles.
                # In the future we might need to expose to adding presentation style UI
                # LightingStyle colors and TextureStyle textures UI
                # as they are required for those surface styles to keep IFC valid
                attributes = {}

            surface_style = ifcopenshell.api.run(
                "style.add_surface_style",
                tool.Ifc.get(),
                style=style,
                ifc_class=props.surface_style_class,
                attributes=attributes,
            )

            # setup blender material
            material = bpy.data.materials.new(style.Name)
            tool.Ifc.link(style, material)
            material.use_fake_user = True
            if surface_style:
                if surface_style.is_a("IfcSurfaceStyleRendering"):
                    tool.Loader.create_surface_style_rendering(material, surface_style)
                elif surface_style.is_a("IfcSurfaceStyleShading"):
                    tool.Loader.create_surface_style_shading(material, surface_style)
        else:
            self.report({"INFO"}, f"Adding style of type {props.style_type} is not yet supported.")

        tool.Style.disable_adding_presentation_style()
        core.load_styles(tool.Style, style_type=props.style_type)


class EnableEditingSurfaceStyle(bpy.types.Operator):
    bl_idname = "bim.enable_editing_surface_style"
    bl_label = "Enable Editing Surface Style"
    bl_options = {"REGISTER", "UNDO"}
    style: bpy.props.IntProperty(default=0)
    ifc_class: bpy.props.StringProperty(default="")

    def execute(self, context):
        props = bpy.context.scene.BIMStylesProperties
        style = tool.Ifc.get().by_id(self.style)
        style_elements = tool.Style.get_style_elements(style)

        if self.ifc_class == "IfcSurfaceStyleWithTextures":
            rendering_style = style_elements.get("IfcSurfaceStyleRendering", None)
            # TODO: support creating texture styles without defining rendering style first.
            if rendering_style is None:
                self.report(
                    {"ERROR"},
                    "Editing texture style without defining rendering style is not yet supported. "
                    "Define render style first",
                )
                return {"CANCELLED"}

        props.is_editing_style = self.style
        props.is_editing_class = self.ifc_class
        props.is_editing_existing_style = self.ifc_class in style_elements
        tool.Style.set_surface_style_props()

        surface_style = style_elements.get(self.ifc_class, None)
        attributes = tool.Style.get_style_ui_props_attributes(self.ifc_class)

        # lighting style require special handling since Attribute doesn't support colors
        callback = None
        if self.ifc_class == "IfcSurfaceStyleLighting":

            def callback(attribute_name, _, data):
                color = attributes.add()
                color.name = attribute_name
                color_value = data[attribute_name]
                if color_value is None:
                    return
                color.color_name = color_value.Name or ""
                color.color_value = (color_value.Red, color_value.Green, color_value.Blue)

        if attributes is not None:
            attributes.clear()
            bonsai.bim.helper.import_attributes2(surface_style or self.ifc_class, attributes, callback)

        material = tool.Ifc.get_object(style)
        active_style_type = material.BIMStyleProperties.active_style_type
        if self.ifc_class == "IfcExternallyDefinedSurfaceStyle" and active_style_type != "External":
            if tool.Style.has_blender_external_style(style_elements):
                tool.Style.switch_shading(material, "External")
        elif (
            self.ifc_class in ("IfcSurfaceStyleShading", "IfcSurfaceStyleRendering", "IfcSurfaceStyleWithTextures")
            and active_style_type != "Shading"
        ):
            tool.Style.switch_shading(material, "Shading")
        return {"FINISHED"}


class EditSurfaceStyle(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.edit_surface_style"
    bl_label = "Edit Surface Style"
    bl_options = {"REGISTER", "UNDO"}

    surface_style: Union[ifcopenshell.entity_instance, None]

    def _execute(self, context):
        self.props = bpy.context.scene.BIMStylesProperties
        self.style = tool.Ifc.get().by_id(self.props.is_editing_style)

        style_elements = tool.Style.get_style_elements(self.style)
        self.surface_style = style_elements.get(self.props.is_editing_class, None)
        self.shading_style = style_elements.get("IfcSurfaceStyleShading", None)
        self.rendering_style = style_elements.get("IfcSurfaceStyleRendering", None)
        self.texture_style = style_elements.get("IfcSurfaceStyleWithTextures", None)

        if self.surface_style:
            result = self.edit_existing_style()
        else:
            result = self.add_new_style()

        if result:
            return result

        self.props.is_editing_style = 0
        core.load_styles(tool.Style, style_type=self.props.style_type)

        # restore selected style type
        material = tool.Ifc.get_object(self.style)
        material.BIMStyleProperties.active_style_type = material.BIMStyleProperties.active_style_type

    def edit_existing_style(self):
        ifc_file = tool.Ifc.get()
        material = tool.Ifc.get_object(self.style)
        assert self.surface_style

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
        elif self.props.is_editing_class == "IfcSurfaceStyleWithTextures":
            # TODO: fix same issues as with creating new IfcSurfaceStyleWithTextures
            material = tool.Ifc.get_object(self.style)
            textures = self.get_texture_attributes()
            if not textures:
                assert self.texture_style
                ifcopenshell.api.style.remove_surface_style(ifc_file, self.texture_style)
                return
            textures = tool.Ifc.run("style.add_surface_textures", textures=textures, uv_maps=[])
            texture_style = tool.Ifc.run(
                "style.add_surface_style",
                style=self.style,
                ifc_class="IfcSurfaceStyleWithTextures",
                attributes={"Textures": textures},
            )
            tool.Loader.create_surface_style_with_textures(material, self.rendering_style, texture_style)
        else:
            attributes = tool.Style.get_style_ui_props_attributes(self.surface_style.is_a())
            ifcopenshell.api.run(
                "style.edit_surface_style",
                tool.Ifc.get(),
                style=self.surface_style,
                attributes=bonsai.bim.helper.export_attributes(attributes),
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
        elif self.props.is_editing_class == "IfcSurfaceStyleWithTextures":
            # TODO: provide `uv_maps` - need to rework .get_uv_maps not to depend on a single representation
            material = tool.Ifc.get_object(self.style)
            textures = self.get_texture_attributes()
            if not textures:
                return
            textures = tool.Ifc.run("style.add_surface_textures", textures=textures, uv_maps=[])
            texture_style = tool.Ifc.run(
                "style.add_surface_style",
                style=self.style,
                ifc_class="IfcSurfaceStyleWithTextures",
                attributes={"Textures": textures},
            )
            tool.Loader.create_surface_style_with_textures(material, self.rendering_style, texture_style)
        else:
            attributes = tool.Style.get_style_ui_props_attributes(self.props.is_editing_class)
            surface_style = ifcopenshell.api.run(
                "style.add_surface_style",
                tool.Ifc.get(),
                style=self.style,
                ifc_class=self.props.is_editing_class,
                attributes=bonsai.bim.helper.export_attributes(attributes),
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
            specular_highlight = {"IfcSpecularRoughness": self.props.specular_highlight}

        return {
            "SurfaceColour": self.color_to_dict(self.props.surface_colour),
            "Transparency": self.props.transparency or None,
            "ReflectanceMethod": self.props.reflectance_method,
            "DiffuseColour": diffuse_colour,
            "SpecularColour": specular_colour,
            "SpecularHighlight": specular_highlight,
        }

    # TODO: support RepeatS/RepeatT params in UI:
    # add it to prop.Texture and Style.get_texture_style_data_from_props
    def get_texture_attributes(self) -> list[dict[str, Any]]:
        textures = []
        for texture in self.props.textures:
            texture_data = {
                "URLReference": texture.path,
                "Mode": texture.mode,
                "RepeatS": True,
                "RepeatT": True,
                "uv_mode": self.props.uv_mode,
            }
            textures.append(texture_data)
        return textures

    def color_to_dict(self, x):
        return {"Red": x[0], "Green": x[1], "Blue": x[2]}


class AddSurfaceTexture(bpy.types.Operator):
    bl_idname = "bim.add_surface_texture"
    bl_label = "Add Surface Texture"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if len(context.scene.BIMStylesProperties.textures) >= 8:
            cls.poll_message_set("Only 8 texture maps available")
            return False
        return True

    def execute(self, context):
        props = context.scene.BIMStylesProperties
        props.textures.add()
        return {"FINISHED"}


class SaveUVToStyle(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.save_uv_to_style"
    bl_label = "Save UV To Style"
    bl_description = (
        "Save active object UV to the IfcSurfaceStyle's IfcSurfaceTexture.\n\n"
        "If object already has IfcSurfaceStyleWithTextures, then it will be used.\n"
        "Otherwise operator will use currently selected surface style (style will be autoassigned)"
    )
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if not (obj := context.active_object) or not tool.Ifc.get_entity(obj):
            cls.poll_message_set("No IFC object selected")
            return False
        return True

    def _execute(self, context):
        context = bpy.context
        ifc_file = tool.Ifc.get()
        obj = context.active_object
        assert obj

        # We need IFC material with a texture style since in IFC
        # UV indexing (IfcTextureCoordinate) requires some IfcSurfaceTexture.
        material, style = None, None
        style_is_assigned = False
        material = obj.active_material
        if material:
            style = tool.Ifc.get_entity(material)

        if style:
            style_is_assigned = True
        else:
            style_item = tool.Style.get_active_style_in_ui()
            if not style_item:
                self.report({"ERROR"}, "Object has no style and no style is selected.")
                return {"CANCELLED"}
            style = ifc_file.by_id(style_item.ifc_definition_id)

        texture_style = tool.Style.get_texture_style(style)
        if not texture_style:
            self.report({"ERROR"}, "IfcSurfaceStyle has no texture style.")
            return {"CANCELLED"}

        def get_active_representation_items() -> list[ifcopenshell.entity_instance]:
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

        if style_is_assigned and not active_representation_items.issubset(all_styled_items):
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

        mesh = obj.data
        assert isinstance(mesh, bpy.types.Mesh)
        uv_layer = mesh.uv_layers.active
        if not uv_layer:
            self.report({"ERROR"}, "Object has no UV.")
            return {"CANCELLED"}
        uv_layer = uv_layer.uv

        # unmap preivously used IfcIndexedTextureMap
        # TODO: remove orphaned data?
        textures = set(texture_style.Textures)
        coords = set()
        for texture in textures:
            coords.update(texture.IsMappedBy or [])
        for coord in coords:
            if coord.is_a("IfcIndexedTextureMap") and coord.MappedTo in active_representation_items:
                coord.Maps = list(set(coord.Maps) - textures)

        uv_indices = []
        uv_verts = [uv.vector for uv in uv_layer]

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

        if not style_is_assigned:
            with context.temp_override(selected_objects=[obj]):
                bpy.ops.bim.assign_style_to_selected(style_id=style.id())

        self.report({"INFO"}, f"UV saved to the style '{style.Name}'.")

        return {"FINISHED"}


class AssignStyleToSelected(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.assign_style_to_selected"
    bl_label = "Assign Style To Selected"
    bl_description = "Assign style to the selected objects' active representations"
    bl_options = {"REGISTER", "UNDO"}
    style_id: bpy.props.IntProperty(name="Style ID")

    @classmethod
    def poll(cls, context):
        if not context.selected_objects:
            cls.poll_message_set("No objects selected")
            return False
        return True

    def _execute(self, context):
        if self.style_id == 0:
            self.report({"ERROR"}, "No style provided")
            return {"CANCELLED"}
        ifc_file = tool.Ifc.get()
        style = ifc_file.by_id(self.style_id)
        material = tool.Ifc.get_object(style)

        has_items = False
        representations: dict[ifcopenshell.entity_instance, bpy.types.Object] = {}
        for obj in context.selected_objects:
            if tool.Geometry.is_representation_item(obj):
                has_items = True
                item = tool.Ifc.get().by_id(obj.data.BIMMeshProperties.ifc_definition_id)
                tool.Style.assign_style_to_representation_item(item, style)
                obj.data.materials.clear()
                obj.data.materials.append(material)
            elif representation := tool.Geometry.get_active_representation(obj):
                representation = tool.Geometry.resolve_mapped_representation(representation)
                representations.setdefault(representation, obj)

        if not has_items and not representations:
            self.report({"INFO"}, "No IFC objects with representations selected.")
            return {"FINISHED"}

        if has_items:
            tool.Geometry.reload_representation(context.scene.BIMGeometryProperties.representation_obj)
            bpy.ops.bim.disable_editing_representation_items()
            bpy.ops.bim.enable_editing_representation_items()

        for representation in representations:
            ifcopenshell.api.style.assign_representation_styles(
                ifc_file,
                shape_representation=representation,
                styles=[style],
                should_use_presentation_style_assignment=tool.Geometry.should_use_presentation_style_assignment(),
            )

        tool.Geometry.reload_representation(representations.values())
        return {"FINISHED"}


class SelectStyleInStylesUI(bpy.types.Operator):
    bl_idname = "bim.styles_ui_select"
    bl_label = "Select Style In Styles UI"
    bl_options = {"REGISTER", "UNDO"}
    style_id: bpy.props.IntProperty()

    def execute(self, context):
        props = bpy.context.scene.BIMStylesProperties
        ifc_file = tool.Ifc.get()
        style = ifc_file.by_id(self.style_id)
        core.load_styles(tool.Style, style.is_a())

        props.active_style_index = next((i for i, m in enumerate(props.styles) if m.ifc_definition_id == self.style_id))
        self.report(
            {"INFO"},
            f"Style '{style.Name or 'Unnamed'}' is selected in Styles UI.",
        )
        return {"FINISHED"}


class RemoveSurfaceStyle(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_surface_style"
    bl_label = "Remove Surface Style"
    bl_description = "Remove the currently edited surface style from the active style"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        ifc_file = tool.Ifc.get()
        props = context.scene.BIMStylesProperties
        style = ifc_file.by_id(props.is_editing_style)
        surface_style = tool.Style.get_style_elements(style)[props.is_editing_class]
        ifcopenshell.api.style.remove_surface_style(ifc_file, surface_style)
        core.disable_editing_style(tool.Style)
        return {"FINISHED"}
