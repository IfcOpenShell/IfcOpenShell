import bpy
import json
import ifcopenshell
import ifcopenshell.util.unit
import ifcopenshell.util.attribute
import ifcopenshell.api
from blenderbim.bim.ifc import IfcStore
from ifcopenshell.api.georeference.data import Data
from math import radians, degrees, atan, tan, cos, sin


class EnableEditingGeoreferencing(bpy.types.Operator):
    bl_idname = "bim.enable_editing_georeferencing"
    bl_label = "Enable Editing Georeferencing"

    def execute(self, context):
        self.file = IfcStore.get_file()
        props = context.scene.BIMGeoreferenceProperties

        while len(props.projected_crs) > 0:
            props.projected_crs.remove(0)

        for attribute in IfcStore.get_schema().declaration_by_name("IfcProjectedCRS").all_attributes():
            data_type = ifcopenshell.util.attribute.get_primitive_type(attribute)
            if data_type == "entity":
                continue
            new = props.projected_crs.add()
            new.name = attribute.name()
            new.is_null = Data.projected_crs[attribute.name()] is None
            new.is_optional = attribute.optional()
            new.data_type = data_type
            if data_type == "string":
                new.string_value = "" if new.is_null else Data.projected_crs[attribute.name()]
            elif data_type == "float":
                new.float_value = 0.0 if new.is_null else Data.projected_crs[attribute.name()]
            elif data_type == "integer":
                new.int_value = 0 if new.is_null else Data.projected_crs[attribute.name()]
            elif data_type == "boolean":
                new.bool_value = False if new.is_null else Data.projected_crs[attribute.name()]

        props.is_map_unit_null = Data.projected_crs["MapUnit"] is None
        if not props.is_map_unit_null:
            props.map_unit_type = Data.projected_crs["MapUnit"]["type"]
            if props.map_unit_type == "IfcSIUnit":
                prefix = ifcopenshell.util.unit.get_prefix(Data.projected_crs["MapUnit"]["Prefix"]) or ""
                name = ifcopenshell.util.unit.get_unit_name(Data.projected_crs["MapUnit"]["Name"])
                props.map_unit_si = prefix + name
            elif props.map_unit_type == "IfcConversionBasedUnit":
                props.map_unit_imperial = Data.projected_crs["MapUnit"]["Name"]

        while len(props.map_conversion) > 0:
            props.map_conversion.remove(0)

        for attribute in IfcStore.get_schema().declaration_by_name("IfcMapConversion").all_attributes():
            data_type = ifcopenshell.util.attribute.get_primitive_type(attribute)
            if data_type == "entity" or data_type == "select":
                continue
            print(attribute.name(), data_type)
            new = props.map_conversion.add()
            new.name = attribute.name()
            new.is_null = Data.map_conversion[attribute.name()] is None
            new.is_optional = attribute.optional()
            # Enforce a string data type to prevent data loss in singpe-precision Blender props
            new.data_type = "string"
            new.string_value = "" if new.is_null else str(Data.map_conversion[attribute.name()])

        props.has_true_north = bool(Data.true_north)
        if Data.true_north:
            props.true_north_abscissa = str(Data.true_north[0])
            props.true_north_ordinate = str(Data.true_north[1])

        props.is_editing = True
        return {"FINISHED"}


class DisableEditingGeoreferencing(bpy.types.Operator):
    bl_idname = "bim.disable_editing_georeferencing"
    bl_label = "Disable Editing Georeferencing"

    def execute(self, context):
        props = context.scene.BIMGeoreferenceProperties
        props.is_editing = False
        return {"FINISHED"}


class EditGeoreferencing(bpy.types.Operator):
    bl_idname = "bim.edit_georeferencing"
    bl_label = "Edit Georeferencing"

    def execute(self, context):
        self.file = IfcStore.get_file()
        props = context.scene.BIMGeoreferenceProperties

        projected_crs = {}
        for attribute in IfcStore.get_schema().declaration_by_name("IfcProjectedCRS").all_attributes():
            data_type = ifcopenshell.util.attribute.get_primitive_type(attribute)
            if data_type == "entity":
                continue
            blender_attribute = props.projected_crs.get(attribute.name())
            if blender_attribute.is_null:
                projected_crs[attribute.name()] = None
            elif blender_attribute.data_type == "string":
                projected_crs[attribute.name()] = blender_attribute.string_value
            elif blender_attribute.data_type == "float":
                projected_crs[attribute.name()] = blender_attribute.float_value
            elif blender_attribute.data_type == "integer":
                projected_crs[attribute.name()] = blender_attribute.int_value
            elif blender_attribute.data_type == "boolean":
                projected_crs[attribute.name()] = blender_attribute.bool_value

        map_unit = ""
        if not props.is_map_unit_null:
            map_unit = props.map_unit_si if props.map_unit_type == "IfcSIUnit" else props.map_unit_imperial

        map_conversion = {}
        for attribute in IfcStore.get_schema().declaration_by_name("IfcMapConversion").all_attributes():
            data_type = ifcopenshell.util.attribute.get_primitive_type(attribute)
            if data_type == "entity" or data_type == "select":
                continue
            blender_attribute = props.map_conversion.get(attribute.name())
            if blender_attribute.is_null:
                map_conversion[attribute.name()] = None
            elif blender_attribute.data_type == "string":
                # We store our floats as string to prevent single precision data loss
                map_conversion[attribute.name()] = float(blender_attribute.string_value)

        true_north = None
        if props.has_true_north:
            try:
                true_north = [float(props.true_north_abscissa), float(props.true_north_ordinate)]
            except:
                pass

        ifcopenshell.api.run(
            "georeference.edit_georeferencing",
            self.file,
            **{
                "map_conversion": map_conversion,
                "projected_crs": projected_crs,
                "map_unit": map_unit,
                "true_north": true_north,
            }
        )
        Data.load(IfcStore.get_file())
        bpy.ops.bim.disable_editing_georeferencing()
        return {"FINISHED"}


class SetBlenderGridNorth(bpy.types.Operator):
    bl_idname = "bim.set_blender_grid_north"
    bl_label = "Set Blender Grid North"

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

    def execute(self, context):
        x_angle = -context.scene.sun_pos_properties.north_offset
        context.scene.BIMGeoreferenceProperties.map_conversion.get("XAxisAbscissa").string_value = str(cos(x_angle))
        context.scene.BIMGeoreferenceProperties.map_conversion.get("XAxisOrdinate").string_value = str(sin(x_angle))
        return {"FINISHED"}


class SetBlenderTrueNorth(bpy.types.Operator):
    bl_idname = "bim.set_blender_true_north"
    bl_label = "Set Blender True North"

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

    def execute(self, context):
        y_angle = -context.scene.sun_pos_properties.north_offset + radians(90)
        context.scene.BIMGeoreferenceProperties.true_north_abscissa = str(cos(y_angle))
        context.scene.BIMGeoreferenceProperties.true_north_ordinate = str(sin(y_angle))
        return {"FINISHED"}


class RemoveGeoreferencing(bpy.types.Operator):
    bl_idname = "bim.remove_georeferencing"
    bl_label = "Remove Georeferencing"

    def execute(self, context):
        ifcopenshell.api.run("georeference.remove_georeferencing", IfcStore.get_file())
        Data.load(IfcStore.get_file())
        return {"FINISHED"}


class AddGeoreferencing(bpy.types.Operator):
    bl_idname = "bim.add_georeferencing"
    bl_label = "Add Georeferencing"

    def execute(self, context):
        ifcopenshell.api.run("georeference.add_georeferencing", IfcStore.get_file())
        Data.load(IfcStore.get_file())
        return {"FINISHED"}


class ConvertLocalToGlobal(bpy.types.Operator):
    bl_idname = "bim.convert_local_to_global"
    bl_label = "Convert Local To Global"

    def execute(self, context):
        if not Data.is_loaded:
            Data.load(IfcStore.get_file())
        props = context.scene.BIMGeoreferenceProperties
        x, y, z = [float(co) for co in props.coordinate_input.split(",")]

        if props.has_blender_offset and props.blender_offset_type == "CARTESIAN_POINT":
            x -= float(props.blender_eastings)
            y -= float(props.blender_northings)
            z -= float(props.blender_orthogonal_height)
        elif props.has_blender_offset and props.blender_offset_type == "OBJECT_PLACEMENT":
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
        bpy.context.scene.cursor.location = results
        return {"FINISHED"}


class ConvertGlobalToLocal(bpy.types.Operator):
    bl_idname = "bim.convert_global_to_local"
    bl_label = "Convert Global To Local"

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

        if props.has_blender_offset and props.blender_offset_type == "CARTESIAN_POINT":
            results[0] += float(props.blender_eastings)
            results[1] += float(props.blender_northings)
            results[2] += float(props.blender_orthogonal_height)
        elif props.has_blender_offset and props.blender_offset_type == "OBJECT_PLACEMENT":
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
        bpy.context.scene.cursor.location = [o * scale for o in results]
        return {"FINISHED"}


class GetCursorLocation(bpy.types.Operator):
    bl_idname = "bim.get_cursor_location"
    bl_label = "Get Cursor Location"

    def execute(self, context):
        props = context.scene.BIMGeoreferenceProperties
        scale = ifcopenshell.util.unit.calculate_unit_scale(IfcStore.get_file())
        project_coordinates = [o / scale for o in bpy.context.scene.cursor.location]
        props.coordinate_input = ",".join([str(o) for o in project_coordinates])
        return {"FINISHED"}


class SetCursorLocation(bpy.types.Operator):
    bl_idname = "bim.set_cursor_location"
    bl_label = "Set Cursor Location"

    def execute(self, context):
        props = context.scene.BIMGeoreferenceProperties
        scale = ifcopenshell.util.unit.calculate_unit_scale(IfcStore.get_file())
        bpy.context.scene.cursor.location = [float(co) * scale for co in props.coordinate_output.split(",")]
        return {"FINISHED"}
