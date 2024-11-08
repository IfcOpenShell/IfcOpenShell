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
from bpy.types import Panel


class BIM_PT_debug(Panel):
    bl_label = "Debug"
    bl_idname = "BIM_PT_debug"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_tab_quality_control"

    def draw(self, context):
        layout = self.layout

        props = context.scene.BIMDebugProperties

        row = self.layout.row(align=True)
        row.prop(context.scene.BIMProperties, "ifc_file", text="")
        row.operator("bim.validate_ifc_file", icon="CHECKMARK", text="")
        row.operator("bim.select_ifc_file", icon="FILE_FOLDER", text="")

        row = self.layout.row(align=True)
        row.prop(props, "express_file", text="")
        row.operator("bim.parse_express", icon="IMPORT", text="")
        row.operator("bim.select_express_file", icon="FILE_FOLDER", text="")

        row = self.layout.row(align=True)
        row.prop(props, "package_name", text="")
        row.operator("bim.pip_install", icon="EVENT_PAGEDOWN").name = props.package_name

        row = layout.row()
        row.operator("bim.reload_ifc_file", text="Incrementally Reload Changes")

        row = layout.row()
        row.operator("bim.print_ifc_file")

        row = layout.row()
        row.operator("bim.copy_debug_information")

        row = layout.row()
        row.operator("bim.purge_hdf5_cache")

        row = layout.row()
        row.operator("bim.update_representation", text="Manually Save Representation")

        row = layout.row()
        row.operator("bim.convert_to_blender")

        row = layout.row()
        row.operator("bim.create_all_shapes")

        row = layout.row()
        row.operator("bim.profile_import_ifc")

        row = layout.row()
        row.operator("bim.debug_active_drawing")

        row = layout.row()
        row.operator("bim.toggle_detailed_ios_logs")

        row = layout.row()
        row.operator("bim.restart_blender")

        row = layout.split(factor=0.5, align=True)
        row.operator("bim.create_shape_from_step_id").should_include_curves = False
        row.operator("bim.create_shape_from_step_id", text="", icon="IPO_ELASTIC").should_include_curves = True
        row.prop(props, "step_id", text="")

        row = layout.split(factor=0.7, align=True)
        row.operator("bim.select_high_polygon_meshes").threshold = context.scene.BIMDebugProperties.number_of_polygons
        row.prop(props, "number_of_polygons", text="")
        row = layout.split(factor=0.7, align=True)
        row.operator("bim.select_highest_polygon_meshes").percentile = (
            context.scene.BIMDebugProperties.percentile_of_polygons
        )
        row.prop(props, "percentile_of_polygons", text="")

        row = layout.split(factor=0.5, align=True)
        row.prop(props, "display_type", text="")
        row.operator("bim.override_display_type").display = context.scene.BIMDebugProperties.display_type

        layout.operator("bim.purge_unused_representations")

        row = layout.row(align=True)
        row.prop(context.scene.BIMDebugProperties, "ifc_class_purge", text="")
        row.operator("bim.purge_unused_elements_by_class", text="Purge Orphaned", icon="TRASH")
        row.operator("bim.print_unused_elements_stats", text="", icon="INFO")

        if context.active_object and context.active_object.data:
            mprops = context.active_object.data.BIMMeshProperties
            row = layout.row()
            row.operator("bim.get_representation_ifc_parameters")
            for index, ifc_parameter in enumerate(mprops.ifc_parameters):
                row = layout.row(align=True)
                row.prop(ifc_parameter, "name", text="")
                row.prop(ifc_parameter, "value", text="")
                row.operator("bim.update_parametric_representation", icon="FILE_REFRESH", text="").index = index

        layout.label(text="Inspector:")

        row = layout.row(align=True)
        if len(props.step_id_breadcrumb) >= 2:
            row.operator("bim.rewind_inspector", icon="FRAME_PREV", text="")
        row.prop(props, "active_step_id", text="")
        row = layout.row(align=True)
        row.operator("bim.inspect_from_step_id").step_id = context.scene.BIMDebugProperties.active_step_id
        row.operator("bim.inspect_from_object")

        if props.attributes:
            layout.label(text="Direct attributes:")

        for index, attribute in enumerate(props.attributes):
            row = layout.row(align=True)
            row.prop(attribute, "name", text="")
            row.prop(attribute, "string_value", text="")
            if attribute.name == "GlobalId":
                op = row.operator("bim.select_global_id", icon="RESTRICT_SELECT_OFF", text="")
                op.global_id = attribute.string_value
            if attribute.name == "ObjectPlacement":
                op = row.operator("bim.print_object_placement", icon="OBJECT_ORIGIN", text="")
                op.step_id = attribute.int_value
            if attribute.int_value:
                row.operator("bim.inspect_from_step_id", icon="DISCLOSURE_TRI_RIGHT", text="").step_id = (
                    attribute.int_value
                )

        if props.inverse_attributes:
            layout.label(text="Inverse attributes:")

        for index, attribute in enumerate(props.inverse_attributes):
            row = layout.row(align=True)
            row.prop(attribute, "name", text="")
            row.prop(attribute, "string_value", text="")
            if attribute.int_value:
                row.operator("bim.inspect_from_step_id", icon="DISCLOSURE_TRI_RIGHT", text="").step_id = (
                    attribute.int_value
                )

        if props.inverse_references:
            layout.label(text="Inverse references:")

        for index, attribute in enumerate(props.inverse_references):
            row = layout.row(align=True)
            row.prop(attribute, "string_value", text="")
            if attribute.int_value:
                row.operator("bim.inspect_from_step_id", icon="DISCLOSURE_TRI_RIGHT", text="").step_id = (
                    attribute.int_value
                )
