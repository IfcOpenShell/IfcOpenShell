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

import blenderbim.tool as tool
import blenderbim.core.georeference as core
from blenderbim.bim.module.georeference.decorator import GeoreferenceDecorator


class AddGeoreferencing(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_georeferencing"
    bl_label = "Add Georeferencing"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Add a new georeference"

    def _execute(self, context):
        core.add_georeferencing(tool.Georeference)


class EnableEditingGeoreferencing(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.enable_editing_georeferencing"
    bl_label = "Enable Editing Georeferencing"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Enable editing georeferencing"

    def _execute(self, context):
        core.enable_editing_georeferencing(tool.Georeference)


class RemoveGeoreferencing(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_georeferencing"
    bl_label = "Remove Georeferencing"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Remove the georeferencing"

    def _execute(self, context):
        core.remove_georeferencing(tool.Ifc)


class EditGeoreferencing(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.edit_georeferencing"
    bl_label = "Edit Georeferencing"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Edit the georeferencing"

    def _execute(self, context):
        core.edit_georeferencing(tool.Ifc, tool.Georeference)


class DisableEditingGeoreferencing(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.disable_editing_georeferencing"
    bl_label = "Disable Editing Georeferencing"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Close editing panel"

    def _execute(self, context):
        core.disable_editing_georeferencing(tool.Georeference)


class GetCursorLocation(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.get_cursor_location"
    bl_label = "Get Cursor Location"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Insert the current cursor coordinates"

    @classmethod
    def poll(cls, context):
        return tool.Ifc.get()

    def _execute(self, context):
        core.get_cursor_location(tool.Georeference)


class ConvertLocalToGlobal(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.convert_local_to_global"
    bl_label = "Convert Local To Global"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Convert local coordinate to global coordinate"

    @classmethod
    def poll(cls, context):
        file = tool.Ifc.get()
        props = context.scene.BIMGeoreferenceProperties
        return file and props.local_coordinates.count(",") == 2

    def _execute(self, context):
        core.convert_local_to_global(tool.Georeference)


class ConvertGlobalToLocal(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.convert_global_to_local"
    bl_label = "Convert Global To Local"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Convert global coordinate to local coordinate"

    @classmethod
    def poll(cls, context):
        file = tool.Ifc.get()
        props = context.scene.BIMGeoreferenceProperties
        return file and file.by_type("IfcUnitAssignment") and props.local_coordinates.count(",") == 2

    def _execute(self, context):
        core.convert_global_to_local(tool.Georeference)


class ConvertAngleToCoordinates(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.convert_angle_to_coord"
    bl_label = "Convert Angle To Y Axis"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Convert angle to Y axis"
    type: bpy.props.StringProperty()

    @classmethod
    def poll(cls, context):
        file = tool.Ifc.get()
        props = context.scene.BIMGeoreferenceProperties
        return file and (props.angle_degree_input_x or props.angle_degree_input_y)

    def _execute(self, context):
        core.convert_angle_to_coord(tool.Georeference, type=self.type)


class ImportPlot(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.import_plot"
    bl_label = "Import Plot"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Import plot"
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    filter_glob: bpy.props.StringProperty(default="*.csv", options={"HIDDEN"})

    def execute(self, context):
        core.import_plot(tool.Georeference, filepath=self.filepath)
        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}


class EnableEditingWCS(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.enable_editing_wcs"
    bl_label = "Enable Editing WCS"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Enable editing WCS"

    def _execute(self, context):
        core.enable_editing_wcs(tool.Georeference)


class EditWCS(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.edit_wcs"
    bl_label = "Edit WCS"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Edit the WCS"

    def _execute(self, context):
        core.edit_wcs(tool.Ifc, tool.Georeference)


class DisableEditingWCS(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.disable_editing_wcs"
    bl_label = "Disable Editing WCS"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Close editing panel"

    def _execute(self, context):
        core.disable_editing_wcs(tool.Georeference)


class EnableEditingTrueNorth(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.enable_editing_true_north"
    bl_label = "Enable Editing True North"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Enable editing True North"

    def _execute(self, context):
        core.enable_editing_true_north(tool.Georeference)


class EditTrueNorth(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.edit_true_north"
    bl_label = "Edit True North"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Edit the True North"

    def _execute(self, context):
        core.edit_true_north(tool.Ifc, tool.Georeference)


class DisableEditingTrueNorth(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.disable_editing_true_north"
    bl_label = "Disable Editing True North"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Close editing panel"

    def _execute(self, context):
        core.disable_editing_true_north(tool.Georeference)


class RemoveTrueNorth(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_true_north"
    bl_label = "Remove True North"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Remove true north"

    def _execute(self, context):
        core.remove_true_north(tool.Ifc)
