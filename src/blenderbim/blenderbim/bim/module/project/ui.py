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
from blenderbim.bim.helper import prop_with_search
from bpy.types import Panel, UIList
from blenderbim.bim.ifc import IfcStore
from blenderbim.bim.module.project.data import ProjectData


class BIM_PT_project(Panel):
    bl_label = "IFC Project"
    bl_idname = "BIM_PT_project"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_project_info"

    def draw(self, context):
        if not ProjectData.is_loaded:
            ProjectData.load()

        self.layout.use_property_decorate = False
        self.layout.use_property_split = True
        props = context.scene.BIMProperties
        pprops = context.scene.BIMProjectProperties
        self.file = IfcStore.get_file()
        if pprops.is_loading:
            self.draw_load_ui(context)
        elif self.file or props.ifc_file:
            self.draw_project_ui(context)
        else:
            self.draw_create_project_ui(context)

    def draw_load_ui(self, context):
        pprops = context.scene.BIMProjectProperties
        prop_with_search(self.layout, pprops, "collection_mode")
        prop_with_search(self.layout, pprops, "filter_mode")
        if pprops.filter_mode in ["DECOMPOSITION", "IFC_CLASS", "IFC_TYPE"]:
            row = self.layout.row(align=True)
            row.label(text=f"Total: {pprops.total_elements}")
            row.operator("bim.toggle_filter_categories", text="", icon="CHECKBOX_HLT").should_select = True
            row.operator("bim.toggle_filter_categories", text="", icon="CHECKBOX_DEHLT").should_select = False
            self.layout.template_list(
                "BIM_UL_filter_categories",
                "",
                pprops,
                "filter_categories",
                pprops,
                "active_filter_category_index",
            )
        elif pprops.filter_mode in ["WHITELIST", "BLACKLIST"]:
            row = self.layout.row()
            row.prop(pprops, "filter_query")
        if pprops.filter_mode != "NONE":
            row = self.layout.row()
            row.prop(pprops, "should_filter_spatial_elements")
        row = self.layout.row()
        row.prop(pprops, "should_use_cpu_multiprocessing")
        row = self.layout.row()
        row.prop(pprops, "should_clean_mesh")
        row = self.layout.row()
        row.prop(pprops, "should_cache")
        row = self.layout.row()
        row.prop(pprops, "should_use_native_meshes")
        row = self.layout.row()
        row.prop(pprops, "should_merge_materials_by_colour")
        row = self.layout.row()
        row.prop(pprops, "is_coordinating")
        if pprops.is_coordinating:
            prop_with_search(self.layout, pprops, "merge_mode")
        row = self.layout.row()
        row.prop(pprops, "deflection_tolerance")
        row = self.layout.row()
        row.prop(pprops, "angular_tolerance")
        row = self.layout.row()
        row.prop(pprops, "distance_limit")
        row = self.layout.row()
        row.prop(pprops, "false_origin")

        row = self.layout.row()
        row.label(text="Element Range")
        row = self.layout.row(align=True)
        row.prop(pprops, "element_offset", text="")
        row.prop(pprops, "element_limit", text="")

        row = self.layout.row(align=True)
        row.operator("bim.load_project_elements")
        row.operator("bim.unload_project", text="", icon="CANCEL")

    def draw_project_ui(self, context):
        props = context.scene.BIMProperties
        pprops = context.scene.BIMProjectProperties
        row = self.layout.row(align=True)
        row.label(text=os.path.basename(props.ifc_file) or "No File Found", icon="FILE")

        if IfcStore.get_file():
            row.prop(pprops, "is_authoring", icon="MODIFIER", text="")
            if pprops.is_editing:
                row.operator("bim.edit_header", icon="CHECKMARK", text="")
                row.operator("bim.disable_editing_header", icon="CANCEL", text="")
            else:
                row.operator("bim.enable_editing_header", icon="GREASEPENCIL", text="")

            row = self.layout.row(align=True)
            row.label(text="IFC Schema", icon="FILE_CACHE")
            row.label(text=IfcStore.get_file().schema)

            if pprops.is_editing:
                row = self.layout.row(align=True)
                row.prop(pprops, "mvd")

                row = self.layout.row(align=True)
                row.prop(pprops, "author_name")
                row = self.layout.row(align=True)
                row.prop(pprops, "author_email")

                row = self.layout.row(align=True)
                row.prop(pprops, "organisation_name")
                row = self.layout.row(align=True)
                row.prop(pprops, "organisation_email")

                row = self.layout.row(align=True)
                row.prop(pprops, "authorisation")
            else:
                row = self.layout.row(align=True)
                row.label(text="IFC MVD", icon="FILE_HIDDEN")
                mvd = "".join(IfcStore.get_file().wrapped_data.header.file_description.description)
                if "[" in mvd:
                    mvd = mvd.split("[")[1][0:-1]
                row.label(text=mvd)
        else:
            row = self.layout.row(align=True)
            row.label(text="File Not Loaded", icon="ERROR")

        if props.ifc_file:
            row = self.layout.row(align=True)
            row.label(text="Saved", icon="EXPORT")
            row.label(text=ProjectData.data["last_saved"])

            row = self.layout.row(align=True)
            row.prop(props, "ifc_file", text="")
            row.operator("bim.reload_ifc_file", icon="FILE_REFRESH", text="")
            row.operator("bim.select_ifc_file", icon="FILE_FOLDER", text="")

        row = self.layout.row(align=True)
        op = row.operator("export_ifc.bim", icon="EXPORT", text="Save Project")
        op.should_save_as = False
        op = row.operator("export_ifc.bim", icon="FILE_TICK", text="Save As")
        op.should_save_as = True
        row.operator("bim.unload_project", text="", icon="X")

    def draw_create_project_ui(self, context):
        props = context.scene.BIMProperties
        pprops = context.scene.BIMProjectProperties
        prop_with_search(self.layout, pprops, "export_schema")
        row = self.layout.row()
        row.prop(context.scene.unit_settings, "system")
        row = self.layout.row()
        row.prop(context.scene.unit_settings, "length_unit")
        row = self.layout.row()
        row.prop(props, "area_unit", text="Area Unit")
        row = self.layout.row()
        row.prop(props, "volume_unit", text="Volume Unit")
        prop_with_search(self.layout, pprops, "template_file", text="Template")

        row = self.layout.row(align=True)
        row.operator("bim.create_project")
        row.operator("bim.load_project")


class BIM_PT_project_library(Panel):
    bl_label = "IFC Project Library"
    bl_idname = "BIM_PT_project_library"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_project_setup"

    def draw(self, context):
        self.layout.use_property_decorate = False
        self.layout.use_property_split = True
        self.props = context.scene.BIMProjectProperties
        row = self.layout.row(align=True)
        row.label(text=IfcStore.library_path or "No Library Loaded", icon="ASSET_MANAGER")
        if IfcStore.library_file:
            row.label(text=IfcStore.library_file.schema)
            row.operator("bim.save_library_file", text="", icon="EXPORT")
        row.operator("bim.select_library_file", icon="FILE_FOLDER", text="")
        if IfcStore.library_file:
            self.draw_library_ul()

    def draw_library_ul(self):
        if not self.props.library_elements:
            row = self.layout.row()
            row.label(text="No Assets Found", icon="ERROR")
            return
        row = self.layout.row(align=True)
        row.label(text=self.props.active_library_element or "Top Level Assets")
        if self.props.active_library_element:
            row.operator("bim.rewind_library", icon="FRAME_PREV", text="")
        row.operator("bim.refresh_library", icon="FILE_REFRESH", text="")
        self.layout.template_list(
            "BIM_UL_library",
            "",
            self.props,
            "library_elements",
            self.props,
            "active_library_element_index",
        )


class BIM_PT_links(Panel):
    bl_label = "IFC Links"
    bl_idname = "BIM_PT_links"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_project_setup"

    def draw(self, context):
        self.props = context.scene.BIMProjectProperties
        row = self.layout.row(align=True)
        row.operator("bim.link_ifc")
        if self.props.links:
            self.layout.template_list(
                "BIM_UL_links",
                "",
                self.props,
                "links",
                self.props,
                "active_link_index",
            )


class BIM_UL_library(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if item:
            row = layout.row(align=True)
            if not item.ifc_definition_id:
                op = row.operator("bim.change_library_element", text="", icon="DISCLOSURE_TRI_RIGHT", emboss=False)
                op.element_name = item.name
            row.label(text=item.name)
            if (
                item.ifc_definition_id
                and IfcStore.library_file.schema != "IFC2X3"
                and IfcStore.library_file.by_type("IfcProjectLibrary")
            ):
                if item.is_declared:
                    op = row.operator("bim.unassign_library_declaration", text="", icon="KEYFRAME_HLT", emboss=False)
                    op.definition = item.ifc_definition_id
                else:
                    op = row.operator("bim.assign_library_declaration", text="", icon="KEYFRAME", emboss=False)
                    op.definition = item.ifc_definition_id
            if item.ifc_definition_id:
                if item.is_appended:
                    row.label(text="", icon="CHECKMARK")
                else:
                    op = row.operator("bim.append_library_element", text="", icon="APPEND_BLEND")
                    op.definition = item.ifc_definition_id
                    op.prop_index = data.get_library_element_index(item)


class BIM_UL_filter_categories(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if item:
            row = layout.row(align=True)
            row.label(text=f"{item.name} ({item.total_elements})")
            row.prop(
                item,
                "is_selected",
                icon="CHECKBOX_HLT" if item.is_selected else "CHECKBOX_DEHLT",
                text="",
                emboss=False,
            )


class BIM_UL_links(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if item:
            row = layout.row(align=True)
            if item.is_loaded:
                row.label(text=item.name)
                op = row.operator(
                    "bim.toggle_link_visibility",
                    text="",
                    icon="CUBE" if item.is_wireframe else "MESH_CUBE",
                    emboss=False,
                )
                op.link = item.name
                op.mode = "WIREFRAME"
                op = row.operator(
                    "bim.toggle_link_visibility",
                    text="",
                    icon="HIDE_ON" if item.is_hidden else "HIDE_OFF",
                    emboss=False,
                )
                op.link = item.name
                op.mode = "VISIBLE"
                op = row.operator("bim.unload_link", text="", icon="UNLINKED")
                op.filepath = item.name
            else:
                row.prop(item, "name", text="")
                op = row.operator("bim.load_link", text="", icon="LINKED")
                op.filepath = item.name
                op = row.operator("bim.unlink_ifc", text="", icon="X")
                op.filepath = item.name
