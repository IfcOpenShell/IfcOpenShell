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
import ifcopenshell
import ifcopenshell.util.unit
import ifcopenshell.util.attribute
import ifcopenshell.api
import blenderbim.bim.helper
import blenderbim.bim.handler
import blenderbim.core.georeference as core
import blenderbim.tool as tool
from blenderbim.bim.ifc import IfcStore
from blenderbim.bim.module.georeference.data import GeoreferenceData
from ifcopenshell.api.unit.data import Data as UnitData #TODO Connect new module data
from math import radians, degrees, atan, tan, cos, sin

class Operator:
    def execute(self, context):
        IfcStore.execute_ifc_operator(self, context)
        blenderbim.bim.handler.refresh_ui_data()
        return {"FINISHED"}

class EnableEditingGeoreferencing(bpy.types.Operator, Operator):
    bl_idname = "bim.enable_editing_georeferencing"
    bl_label = "Enable Editing Georeferencing"
    bl_options = {"REGISTER", "UNDO"}
    georeferencing: bpy.props.IntProperty()

    def _execute(self, context):
        core.enable_editing_georeferencing(tool.Georeference, georeferencing = tool.Ifc.get().by_id(self.georeferencing))

class DisableEditingGeoreferencing(bpy.types.Operator, Operator):
    bl_idname = "bim.disable_editing_georeferencing"
    bl_label = "Disable Editing Georeferencing"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.disable_editing_georeferencing(tool.Georeference)


class EditGeoreferencing(bpy.types.Operator, Operator):
    bl_idname = "bim.edit_georeferencing"
    bl_label = "Edit Georeferencing"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.edit_georeferencing(tool.Ifc, tool.Georeference)


class AddGeoreferencing(bpy.types.Operator, Operator):
    bl_idname = "bim.add_georeferencing"
    bl_label = "Add Georeferencing"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.add_georeferencing(tool.Georeference)


class RemoveGeoreferencing(bpy.types.Operator):
    bl_idname = "bim.remove_georeferencing"
    bl_label = "Remove Georeferencing"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        ifcopenshell.api.run("georeference.remove_georeferencing", IfcStore.get_file())
        GeoreferenceData.load()
        return {"FINISHED"}


class SetBlenderGridNorth(bpy.types.Operator, Operator):
    bl_idname = "bim.set_blender_grid_north"
    bl_label = "Set Blender Grid North"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.set_blender_grid_north(tool.Georeference)


class SetIfcGridNorth(bpy.types.Operator):
    bl_idname = "bim.set_ifc_grid_north"
    bl_label = "Set IFC Grid North"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        x_angle = -context.scene.sun_pos_properties.north_offset
        context.scene.BIMGeoreferenceProperties.map_conversion.get("XAxisAbscissa").string_value = str(cos(x_angle))
        context.scene.BIMGeoreferenceProperties.map_conversion.get("XAxisOrdinate").string_value = str(sin(x_angle))
        return {"FINISHED"}


class SetBlenderTrueNorth(bpy.types.Operator):
    bl_idname = "bim.set_blender_true_north"
    bl_label = "Set Blender True North"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        context.scene.sun_pos_properties.north_offset = -radians(
            ifcopenshell.util.geolocation.yaxis2angle(
                float(context.scene.BIMGeoreferenceProperties.true_north_abscissa),
                float(context.scene.BIMGeoreferenceProperties.true_north_ordinate),
            )
        )
        return {"FINISHED"}


class SetIfcTrueNorth(bpy.types.Operator):
    bl_idname = "bim.set_ifc_true_north"
    bl_label = "Set IFC True North"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        y_angle = -context.scene.sun_pos_properties.north_offset + radians(90)
        context.scene.BIMGeoreferenceProperties.true_north_abscissa = str(cos(y_angle))
        context.scene.BIMGeoreferenceProperties.true_north_ordinate = str(sin(y_angle))
        return {"FINISHED"}


class ConvertLocalToGlobal(bpy.types.Operator):
    bl_idname = "bim.convert_local_to_global"
    bl_label = "Convert Local To Global"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        file = IfcStore.get_file()
        props = context.scene.BIMGeoreferenceProperties
        return file and props.coordinate_input.count(",") == 2

    def execute(self, context):
        if not GeoreferenceData.is_loaded:
            GeoreferenceData.load()
        props = context.scene.BIMGeoreferenceProperties
        x, y, z = [float(co) for co in props.coordinate_input.split(",")]

        if props.has_blender_offset:
            results = ifcopenshell.util.geolocation.xyz2enh(
                x,
                y,
                z,
                float(props.blender_eastings),
                float(props.blender_northings),
                float(props.blender_orthogonal_height),
                float(props.blender_x_axis_abscissa),
                float(props.blender_x_axis_ordinate),
                1.0,
            )
            x, y, z = results

        # TODO: what if the project CRS units and the project units are different?

        if GeoreferenceData.data["map_conversion"]:
            results = ifcopenshell.util.geolocation.xyz2enh(
                x,
                y,
                z,
                GeoreferenceData.data["map_conversion"]["Eastings"],
                GeoreferenceData.data["map_conversion"]["Northings"],
                GeoreferenceData.data["map_conversion"]["OrthogonalHeight"],
                GeoreferenceData.data["map_conversion"].get("XAxisAbscissa", 1.0),
                GeoreferenceData.data["map_conversion"].get("XAxisOrdinate", 0.0),
                GeoreferenceData.data["map_conversion"].get("Scale", 1.0),
            )
        else:
            results = (x, y, z)

        props.coordinate_output = ",".join([str(r) for r in results])
        context.scene.cursor.location = results
        return {"FINISHED"}


class ConvertGlobalToLocal(bpy.types.Operator):
    bl_idname = "bim.convert_global_to_local"
    bl_label = "Convert Global To Local"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        file = IfcStore.get_file()
        props = context.scene.BIMGeoreferenceProperties
        return file and file.by_type("IfcUnitAssignment") and props.coordinate_input.count(",") == 2

    def execute(self, context):
        if not GeoreferenceData.is_loaded:
            GeoreferenceData.load()
        props = context.scene.BIMGeoreferenceProperties
        x, y, z = [float(co) for co in props.coordinate_input.split(",")]

        if GeoreferenceData.data["map_conversion"]:
            results = ifcopenshell.util.geolocation.enh2xyz(
                x,
                y,
                z,
                GeoreferenceData.data["map_conversion"]["Eastings"],
                GeoreferenceData.data["map_conversion"]["Northings"],
                GeoreferenceData.data["map_conversion"]["OrthogonalHeight"],
                GeoreferenceData.data["map_conversion"].get("XAxisAbscissa", 1.0),
                GeoreferenceData.data["map_conversion"].get("XAxisOrdinate", 0.0),
                GeoreferenceData.data["map_conversion"].get("Scale", 1.0),
            )
        else:
            results = (x, y, z)

        if props.has_blender_offset:
            results = ifcopenshell.util.geolocation.enh2xyz(
                results[0],
                results[1],
                results[2],
                float(props.blender_eastings),
                float(props.blender_northings),
                float(props.blender_orthogonal_height),
                float(props.blender_x_axis_abscissa),
                float(props.blender_x_axis_ordinate),
                1.0,
            )

        props.coordinate_output = ",".join([str(r) for r in results])

        scale = ifcopenshell.util.unit.calculate_unit_scale(IfcStore.get_file())
        context.scene.cursor.location = [o * scale for o in results]
        return {"FINISHED"}


class GetCursorLocation(bpy.types.Operator):
    bl_idname = "bim.get_cursor_location"
    bl_label = "Get Cursor Location"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        file = IfcStore.get_file()
        return file and file.by_type("IfcUnitAssignment")

    def execute(self, context):
        props = context.scene.BIMGeoreferenceProperties
        scale = ifcopenshell.util.unit.calculate_unit_scale(IfcStore.get_file())
        project_coordinates = [o / scale for o in context.scene.cursor.location]
        props.coordinate_input = ",".join([str(o) for o in project_coordinates])
        return {"FINISHED"}


class SetCursorLocation(bpy.types.Operator):
    bl_idname = "bim.set_cursor_location"
    bl_label = "Set Cursor Location"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        file = IfcStore.get_file()
        props = context.scene.BIMGeoreferenceProperties
        return file and file.by_type("IfcUnitAssignment") and props.coordinate_output.count(",") == 2

    def execute(self, context):
        props = context.scene.BIMGeoreferenceProperties
        scale = ifcopenshell.util.unit.calculate_unit_scale(IfcStore.get_file())
        context.scene.cursor.location = [float(co) * scale for co in props.coordinate_output.split(",")]
        return {"FINISHED"}
