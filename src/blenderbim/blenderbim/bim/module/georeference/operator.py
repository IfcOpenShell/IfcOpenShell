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
import json
import ifcopenshell
import ifcopenshell.util.unit
import ifcopenshell.util.attribute
import ifcopenshell.api
import blenderbim.bim.helper
from blenderbim.bim.ifc import IfcStore
from ifcopenshell.api.georeference.data import Data
from ifcopenshell.api.unit.data import Data as UnitData
from math import radians, degrees, atan, tan, cos, sin


class EnableEditingGeoreferencing(bpy.types.Operator):
    bl_idname = "bim.enable_editing_georeferencing"
    bl_label = "Enable Editing Georeferencing"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        self.file = IfcStore.get_file()
        props = context.scene.BIMGeoreferenceProperties
        self.props = props

        props.projected_crs.clear()

        blenderbim.bim.helper.import_attributes(
            "IfcProjectedCRS", props.projected_crs, Data.projected_crs, self.import_projected_crs_attributes
        )

        props.map_conversion.clear()
        blenderbim.bim.helper.import_attributes(
            "IfcMapConversion", props.map_conversion, Data.map_conversion, self.import_map_conversion_attributes
        )

        props.has_true_north = bool(Data.true_north)
        if Data.true_north:
            props.true_north_abscissa = str(Data.true_north[0])
            props.true_north_ordinate = str(Data.true_north[1])

        props.is_editing = True
        return {"FINISHED"}

    def import_projected_crs_attributes(self, name, prop, data):
        if name == "MapUnit":
            new = self.props.projected_crs.add()
            new.name = name
            new.data_type = "enum"
            new.is_null = data[name] is None
            new.is_optional = True
            new.enum_items = json.dumps(
                {u["id"]: u["Name"] for u in UnitData.units.values() if u["UnitType"] == "LENGTHUNIT"}
            )
            if data["MapUnit"]:
                new.enum_value = str(data["MapUnit"]["id"])
            return True

    def import_map_conversion_attributes(self, name, prop, data):
        if name not in ["SourceCRS", "TargetCRS"]:
            # Enforce a string data type to prevent data loss in single-precision Blender props
            prop.data_type = "string"
            prop.string_value = "" if prop.is_null else str(data[name])
            return True


class DisableEditingGeoreferencing(bpy.types.Operator):
    bl_idname = "bim.disable_editing_georeferencing"
    bl_label = "Disable Editing Georeferencing"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = context.scene.BIMGeoreferenceProperties
        props.is_editing = False
        return {"FINISHED"}


class EditGeoreferencing(bpy.types.Operator):
    bl_idname = "bim.edit_georeferencing"
    bl_label = "Edit Georeferencing"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        self.file = IfcStore.get_file()
        props = context.scene.BIMGeoreferenceProperties

        projected_crs = blenderbim.bim.helper.export_attributes(props.projected_crs, self.export_crs_attributes)
        map_conversion = blenderbim.bim.helper.export_attributes(props.map_conversion, self.export_map_attributes)

        true_north = None
        if props.has_true_north:
            try:
                true_north = [float(props.true_north_abscissa), float(props.true_north_ordinate)]
            except ValueError:
                self.report({"ERROR"}, "True North Abscissa and Ordinate expect a number")

        ifcopenshell.api.run(
            "georeference.edit_georeferencing",
            self.file,
            **{
                "map_conversion": map_conversion,
                "projected_crs": projected_crs,
                "true_north": true_north,
            }
        )
        Data.load(self.file)
        bpy.ops.bim.disable_editing_georeferencing()
        return {"FINISHED"}

    def export_map_attributes(self, attributes, prop):
        if not prop.is_null and prop.data_type == "string":
            # We store our floats as string to prevent single precision data loss
            attributes[prop.name] = float(prop.string_value)
            return True

    def export_crs_attributes(self, attributes, prop):
        if not prop.is_null and prop.name == "MapUnit":
            attributes[prop.name] = self.file.by_id(int(prop.enum_value))
            return True


class SetBlenderGridNorth(bpy.types.Operator):
    bl_idname = "bim.set_blender_grid_north"
    bl_label = "Set Blender Grid North"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        context.scene.sun_pos_properties.north_offset = -radians(
            ifcopenshell.util.geolocation.xaxis2angle(
                float(context.scene.BIMGeoreferenceProperties.map_conversion.get("XAxisAbscissa").string_value),
                float(context.scene.BIMGeoreferenceProperties.map_conversion.get("XAxisOrdinate").string_value),
            )
        )
        return {"FINISHED"}


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


class RemoveGeoreferencing(bpy.types.Operator):
    bl_idname = "bim.remove_georeferencing"
    bl_label = "Remove Georeferencing"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        ifcopenshell.api.run("georeference.remove_georeferencing", IfcStore.get_file())
        Data.load(IfcStore.get_file())
        return {"FINISHED"}


class AddGeoreferencing(bpy.types.Operator):
    bl_idname = "bim.add_georeferencing"
    bl_label = "Add Georeferencing"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        ifcopenshell.api.run("georeference.add_georeferencing", IfcStore.get_file())
        Data.load(IfcStore.get_file())
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
        if not Data.is_loaded:
            Data.load(IfcStore.get_file())
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

        if Data.map_conversion:
            results = ifcopenshell.util.geolocation.xyz2enh(
                x,
                y,
                z,
                Data.map_conversion["Eastings"],
                Data.map_conversion["Northings"],
                Data.map_conversion["OrthogonalHeight"],
                Data.map_conversion.get("XAxisAbscissa", 1.0),
                Data.map_conversion.get("XAxisOrdinate", 0.0),
                Data.map_conversion.get("Scale", 1.0),
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
        if not Data.is_loaded:
            Data.load(IfcStore.get_file())
        props = context.scene.BIMGeoreferenceProperties
        x, y, z = [float(co) for co in props.coordinate_input.split(",")]

        if Data.map_conversion:
            results = ifcopenshell.util.geolocation.enh2xyz(
                x,
                y,
                z,
                Data.map_conversion["Eastings"],
                Data.map_conversion["Northings"],
                Data.map_conversion["OrthogonalHeight"],
                Data.map_conversion.get("XAxisAbscissa", 1.0),
                Data.map_conversion.get("XAxisOrdinate", 0.0),
                Data.map_conversion.get("Scale", 1.0),
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
