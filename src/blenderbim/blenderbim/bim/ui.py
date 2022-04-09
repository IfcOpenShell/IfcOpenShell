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
from pathlib import Path
from . import ifc
from bpy.types import Panel
from bpy.props import StringProperty, IntProperty, BoolProperty
from blenderbim.bim.helper import IfcHeaderExtractor
import blenderbim.tool as tool


class IFCFileSelector:
    def is_existing_ifc_file(self, filepath=None):
        if filepath is None:
            filepath = self.filepath
        return os.path.exists(filepath) and "ifc" in os.path.splitext(filepath)[1].lower()

    def draw(self, context):
        # Access filepath & Directory https://blender.stackexchange.com/a/207665
        params = context.space_data.params
        # Decode byte string https://stackoverflow.com/a/47737082/
        directory = Path(params.directory.decode("utf-8"))
        filepath = os.path.join(directory, params.filename)
        if self.is_existing_ifc_file(filepath):
            box = self.layout.box()
            box.label(text="IFC Header Specifications", icon="INFO")
            header_data = IfcHeaderExtractor(filepath).extract()
            for key, value in header_data.items():
                if value != "":
                    split = box.split()
                    split.label(text=key.title().replace("_", " "))
                    split.label(text=str(value))
                    if (
                        key.lower() == "schema_name"
                        and str(value).lower() == "ifc2x3"
                        and filepath[-4:].lower() == ".ifc"
                    ):
                        row = box.row()
                        op = row.operator("bim.run_migrate_patch", text="Upgrade to IFC4")
                        op.infile = filepath
                        op.outfile = filepath[0:-4] + "-IFC4.ifc"
                        op.schema = "IFC4"


class BIM_PT_section_plane(Panel):
    bl_label = "Temporary Section Cutaways"
    bl_idname = "BIM_PT_section_plane"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "output"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        props = context.scene.BIMProperties

        row = layout.row()
        row.prop(props, "should_section_selected_objects")

        row = layout.row()
        row.prop(props, "section_plane_colour")

        row = layout.row(align=True)
        row.operator("bim.add_section_plane")
        row.operator("bim.remove_section_plane")


class BIM_UL_generic(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if item:
            layout.prop(item, "name", text="", emboss=False)
        else:
            layout.label(text="", translate=False)


class BIM_UL_topics(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        ob = data
        if item:
            layout.prop(item, "title", text="", emboss=False)
        else:
            layout.label(text="", translate=False)


class BIM_ADDON_preferences(bpy.types.AddonPreferences):
    bl_idname = "blenderbim"
    svg2pdf_command: StringProperty(name="SVG to PDF Command", description="E.g. [['inkscape', svg, '-o', pdf]]")
    svg2dxf_command: StringProperty(
        name="SVG to DXF Command",
        description="E.g. [['inkscape', svg, '-o', eps], ['pstoedit', '-dt', '-f', 'dxf:-polyaslines -mm', eps, dxf, '-psarg', '-dNOSAFER']]",
    )
    svg_command: StringProperty(name="SVG Command", description="E.g. [['firefox-bin', path]]")
    pdf_command: StringProperty(name="PDF Command", description="E.g. [['firefox-bin', path]]")
    openlca_port: IntProperty(name="OpenLCA IPC Port", default=8080)
    should_hide_empty_props: BoolProperty(name="Should Hide Empty Properties", default=True)
    should_play_chaching_sound: BoolProperty(
        name="Should Make A Cha-Ching Sound When Project Costs Updates", default=False
    )

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.label(
            text="To upgrade, first uninstall your current BlenderBIM Add-on, then install the new version.",
            icon="ERROR",
        )
        row = layout.row()
        row.label(
            text="To uninstall, first disable the add-on. Then restart Blender before pressing the 'Remove' button.",
            icon="ERROR",
        )
        row = layout.row()
        row.operator("bim.open_upstream", text="Visit Homepage").page = "home"
        row.operator("bim.open_upstream", text="Visit Documentation").page = "docs"
        row = layout.row()
        row.operator("bim.open_upstream", text="Visit Wiki").page = "wiki"
        row.operator("bim.open_upstream", text="Visit Community").page = "community"
        row = layout.row()
        row.prop(self, "svg2pdf_command")
        row = layout.row()
        row.prop(self, "svg2dxf_command")
        row = layout.row()
        row.prop(self, "svg_command")
        row = layout.row()
        row.prop(self, "pdf_command")
        row = layout.row()
        row.prop(self, "openlca_port")
        row = layout.row()
        row.prop(self, "should_hide_empty_props")
        row = layout.row()
        row.prop(self, "should_play_chaching_sound")

        row = layout.row()
        row.prop(context.scene.BIMModelProperties, "occurrence_name_style")
        row = layout.row()
        row.prop(context.scene.BIMModelProperties, "occurrence_name_function")

        row = self.layout.row()
        row.prop(context.scene.DocProperties, "decorations_colour")

        row = self.layout.row(align=True)
        row.prop(context.scene.BIMProperties, "schema_dir")
        row.operator("bim.select_schema_dir", icon="FILE_FOLDER", text="")

        row = self.layout.row(align=True)
        row.prop(context.scene.BIMProperties, "data_dir")
        row.operator("bim.select_data_dir", icon="FILE_FOLDER", text="")

        row = layout.row()
        row.operator("bim.configure_visibility")


def ifc_units(self, context):
    scene = context.scene
    props = scene.BIMProperties
    layout = self.layout
    layout.use_property_decorate = False
    layout.use_property_split = True
    row = layout.row()
    row.prop(props, "area_unit")
    row = layout.row()
    row.prop(props, "volume_unit")
    row = layout.row()
    if scene.unit_settings.system == "IMPERIAL":
        row.prop(props, "imperial_precision")
    else:
        row.prop(props, "metric_precision")


# Scene panel groups
class BIM_PT_project_info(Panel):
    bl_label = "IFC Project Info"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"

    def draw(self, context):
        pass


class BIM_PT_project_setup(Panel):
    bl_label = "IFC Project Setup"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        pass


class BIM_PT_collaboration(Panel):
    bl_label = "IFC Collaboration"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        pass


class BIM_PT_geometry(Panel):
    bl_label = "IFC Geometry"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context):
        return tool.Ifc.get()

    def draw(self, context):
        pass


class BIM_PT_4D5D(Panel):
    bl_label = "IFC Costing and Scheduling"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context):
        return tool.Ifc.get()

    def draw(self, context):
        pass


class BIM_PT_structural(Panel):
    bl_label = "IFC Structural"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context):
        return tool.Ifc.get()

    def draw(self, context):
        pass


class BIM_PT_services(Panel):
    bl_label = "IFC Services"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context):
        return tool.Ifc.get()

    def draw(self, context):
        pass


class BIM_PT_quality_control(Panel):
    bl_label = "IFC Quality Control"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        pass


class BIM_PT_integrations(Panel):
    bl_label = "BIM Integrations"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        pass


# Object panel groups
class BIM_PT_object_metadata(Panel):
    bl_label = "IFC Object Metadata"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        return tool.Ifc.get()

    def draw(self, context):
        pass


class BIM_PT_geometry_object(Panel):
    bl_label = "IFC Geometry"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context):
        return tool.Ifc.get()

    def draw(self, context):
        pass


class BIM_PT_services_object(Panel):
    bl_label = "IFC Services"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context):
        return tool.Ifc.get()

    def draw(self, context):
        pass


class BIM_PT_utilities_object(Panel):
    bl_label = "IFC Utilities"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context):
        return tool.Ifc.get()

    def draw(self, context):
        pass


class BIM_PT_misc_object(Panel):
    bl_label = "IFC Misc."
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context):
        return tool.Ifc.get()

    def draw(self, context):
        pass
