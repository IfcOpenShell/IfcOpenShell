# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
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
import numpy as np
import ifcopenshell
import ifcopenshell.api.georeference
import blenderbim.core.tool
import blenderbim.tool as tool
import blenderbim.bim.helper
from math import radians, cos, sin


class Georeference(blenderbim.core.tool.Georeference):
    @classmethod
    def add_georeferencing(cls):
        tool.Ifc.run(
            "georeference.add_georeferencing",
            ifc_class=bpy.context.scene.BIMGeoreferenceProperties.coordinate_operation_class,
        )

    @classmethod
    def import_projected_crs(cls):
        def callback(name, prop, data):
            if name == "MapUnit":
                new = bpy.context.scene.BIMGeoreferenceProperties.projected_crs.add()
                new.name = name
                new.data_type = "enum"
                new.is_null = data[name] is None
                new.is_optional = True
                new.enum_items = json.dumps(
                    {
                        u.id(): (getattr(u, "Prefix", "") or "") + u.Name
                        for u in tool.Ifc.get().by_type("IfcNamedUnit")
                        if u.UnitType == "LENGTHUNIT"
                    }
                )
                if data["MapUnit"]:
                    new.enum_value = str(data["MapUnit"].id())
                return True

        props = bpy.context.scene.BIMGeoreferenceProperties
        props.projected_crs.clear()

        if tool.Ifc.get_schema() == "IFC2X3":
            return

        for context in tool.Ifc.get().by_type("IfcGeometricRepresentationContext", include_subtypes=False):
            if context.HasCoordinateOperation:
                projected_crs = context.HasCoordinateOperation[0].TargetCRS
                blenderbim.bim.helper.import_attributes2(projected_crs, props.projected_crs, callback=callback)
                return

    @classmethod
    def import_coordinate_operation(cls):
        def callback(name, prop, data):
            if name in ("FirstCoordinate", "SecondCoordinate"):
                props = bpy.context.scene.BIMGeoreferenceProperties
                if name == "FirstCoordinate":
                    new = props.coordinate_operation.add()
                    new.name = "Measure Type"
                    new.data_type = "enum"
                    new.is_optional = False
                    new.is_null = False
                    new.enum_items = json.dumps(["IfcLengthMeasure", "IfcPlaneAngleMeasure"])
                    new.enum_value = data[name].is_a()
                prop = props.coordinate_operation.add()
                prop.name = name
                prop.is_optional = False
                prop.is_null = False
                # Enforce a string data type to prevent data loss in single-precision Blender props
                prop.data_type = "string"
                prop.string_value = "" if prop.is_null else str(data[name].wrappedValue)
                return True
            elif name == "XAxisAbscissa":
                props = bpy.context.scene.BIMGeoreferenceProperties
                props.is_changing_angle = True
                if data["XAxisAbscissa"] is None or data["XAxisOrdinate"] is None:
                    props.x_axis_is_null = True
                else:
                    props.grid_north_angle = str(
                        round(
                            ifcopenshell.util.geolocation.xaxis2angle(data["XAxisAbscissa"], data["XAxisOrdinate"]), 7
                        )
                    )
                    props.x_axis_abscissa = str(data["XAxisAbscissa"])
                    props.x_axis_ordinate = str(data["XAxisOrdinate"])
                props.is_changing_angle = False
                return True
            elif name == "XAxisOrdinate":
                return True
            elif name not in ("SourceCRS", "TargetCRS"):
                # Enforce a string data type to prevent data loss in single-precision Blender props
                prop.data_type = "string"
                prop.string_value = "" if prop.is_null else str(data[name])
                return True

        props = bpy.context.scene.BIMGeoreferenceProperties
        props.coordinate_operation.clear()

        if tool.Ifc.get_schema() == "IFC2X3":
            return

        for context in tool.Ifc.get().by_type("IfcGeometricRepresentationContext", include_subtypes=False):
            if context.HasCoordinateOperation:
                coordinate_operation = context.HasCoordinateOperation[0]
                blenderbim.bim.helper.import_attributes2(
                    coordinate_operation, props.coordinate_operation, callback=callback
                )
                return

    @classmethod
    def import_true_north(cls):
        if tool.Ifc.get_schema() == "IFC2X3":
            return

        props = bpy.context.scene.BIMGeoreferenceProperties
        props.is_changing_angle = True
        props.true_north_abscissa = "0"
        props.true_north_ordinate = "1"
        props.true_north_angle = "0"
        props.is_changing_angle = False

        for context in tool.Ifc.get().by_type("IfcGeometricRepresentationContext", include_subtypes=False):
            if context.TrueNorth:
                true_north = context.TrueNorth.DirectionRatios
                props.is_changing_angle = True
                props.true_north_abscissa = str(true_north[0])
                props.true_north_ordinate = str(true_north[1])
                props.true_north_angle = str(round(ifcopenshell.util.geolocation.yaxis2angle(*true_north[:2]), 7))
                props.is_changing_angle = False
                return

    @classmethod
    def get_projected_crs_attributes(cls):
        def callback(attributes, prop):
            if not prop.is_null and prop.name == "MapUnit":
                attributes[prop.name] = tool.Ifc.get().by_id(int(prop.enum_value))
                return True

        props = bpy.context.scene.BIMGeoreferenceProperties
        return blenderbim.bim.helper.export_attributes(props.projected_crs, callback=callback)

    @classmethod
    def get_coordinate_operation_attributes(cls):
        measure_type = None

        def callback(attributes, prop):
            global measure_type
            if prop.name == "Measure Type":
                measure_type = prop.get_value()
                return True
            elif prop.name in ("FirstCoordinate", "SecondCoordinate"):
                attributes[prop.name] = tool.Ifc.get().create_entity(measure_type, float(prop.string_value))
                return True
            elif prop.name == "XAxisAbscissa":
                props = bpy.context.scene.BIMGeoreferenceProperties
                if props.x_axis_is_null:
                    attributes["XAxisAbscissa"] = None
                    attributes["XAxisOrdinate"] = None
                else:
                    attributes["XAxisAbscissa"] = float(props.x_axis_abscissa)
                    attributes["XAxisOrdinate"] = float(props.x_axis_ordinate)
                return True
            elif prop.name == "XAxisOrdinate":
                return True
            elif not prop.is_null and prop.data_type == "string":
                # We store our floats as string to prevent single precision data loss
                attributes[prop.name] = float(prop.string_value)
                return True

        props = bpy.context.scene.BIMGeoreferenceProperties
        return blenderbim.bim.helper.export_attributes(props.coordinate_operation, callback=callback)

    @classmethod
    def get_true_north_attributes(cls):
        props = bpy.context.scene.BIMGeoreferenceProperties
        try:
            return [float(props.true_north_abscissa), float(props.true_north_ordinate)]
        except ValueError:
            print("ERROR, True North Abscissa and Ordinate expect a number")

    @classmethod
    def enable_editing(cls):
        bpy.context.scene.BIMGeoreferenceProperties.is_editing = True

    @classmethod
    def disable_editing(cls):
        bpy.context.scene.BIMGeoreferenceProperties.is_editing = False

    @classmethod
    def enable_editing_wcs(cls):
        bpy.context.scene.BIMGeoreferenceProperties.is_editing_wcs = True

    @classmethod
    def disable_editing_wcs(cls):
        bpy.context.scene.BIMGeoreferenceProperties.is_editing_wcs = False

    @classmethod
    def enable_editing_true_north(cls):
        bpy.context.scene.BIMGeoreferenceProperties.is_editing_true_north = True

    @classmethod
    def disable_editing_true_north(cls):
        bpy.context.scene.BIMGeoreferenceProperties.is_editing_true_north = False

    @classmethod
    def set_coordinates(cls, io, coordinates):
        if io == "local":
            bpy.context.scene.BIMGeoreferenceProperties.local_coordinates = ",".join([str(o) for o in coordinates])
        elif io == "map":
            bpy.context.scene.BIMGeoreferenceProperties.map_coordinates = ",".join([str(o) for o in coordinates])

    @classmethod
    def get_coordinates(cls, io):
        if io == "local":
            return [float(co) for co in bpy.context.scene.BIMGeoreferenceProperties.local_coordinates.split(",")]
        elif io == "map":
            return [float(co) for co in bpy.context.scene.BIMGeoreferenceProperties.map_coordinates.split(",")]

    @classmethod
    def get_cursor_location(cls):
        scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        return [o / scale for o in bpy.context.scene.cursor.location]

    @classmethod
    def set_cursor_location(cls):
        coordinates = cls.get_coordinates("local")
        scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        bpy.context.scene.cursor.location = [co * scale for co in coordinates]

    @classmethod
    def xyz2enh(cls, coordinates, should_return_in_map_units=True):
        props = bpy.context.scene.BIMGeoreferenceProperties
        if props.has_blender_offset:
            coordinates = ifcopenshell.util.geolocation.xyz2enh(
                coordinates[0],
                coordinates[1],
                coordinates[2],
                float(props.blender_offset_x),
                float(props.blender_offset_y),
                float(props.blender_offset_z),
                float(props.blender_x_axis_abscissa),
                float(props.blender_x_axis_ordinate),
            )
        return ifcopenshell.util.geolocation.auto_xyz2enh(
            tool.Ifc.get(), *coordinates, should_return_in_map_units=should_return_in_map_units
        )

    @classmethod
    def enh2xyz(cls, coordinates):
        coordinates = ifcopenshell.util.geolocation.auto_enh2xyz(tool.Ifc.get(), *coordinates)
        props = bpy.context.scene.BIMGeoreferenceProperties
        if props.has_blender_offset:
            coordinates = ifcopenshell.util.geolocation.enh2xyz(
                coordinates[0],
                coordinates[1],
                coordinates[2],
                float(props.blender_offset_x),
                float(props.blender_offset_y),
                float(props.blender_offset_z),
                float(props.blender_x_axis_abscissa),
                float(props.blender_x_axis_ordinate),
            )
        return coordinates

    @classmethod
    def angle2coords(cls, angle, type):
        if type == "rel_x":
            return ifcopenshell.util.geolocation.angle2xaxis(angle)
        elif type == "rel_y":
            return ifcopenshell.util.geolocation.angle2yaxis(angle)

    @classmethod
    def get_angle(cls, type):
        if type == "rel_x":
            return bpy.context.scene.BIMGeoreferenceProperties.angle_degree_input_x
        elif type == "rel_y":
            return bpy.context.scene.BIMGeoreferenceProperties.angle_degree_input_y

    @classmethod
    def set_vector_coordinates(cls, vector_coordinates, type):
        x, y = vector_coordinates
        if type == "rel_x":
            bpy.context.scene.BIMGeoreferenceProperties.x_axis_abscissa_output = str(x)
            bpy.context.scene.BIMGeoreferenceProperties.x_axis_ordinate_output = str(y)
        elif type == "rel_y":
            bpy.context.scene.BIMGeoreferenceProperties.y_axis_abscissa_output = str(x)
            bpy.context.scene.BIMGeoreferenceProperties.y_axis_ordinate_output = str(y)

    @classmethod
    def import_plot(cls, filepath):
        import bmesh

        def parse_csv(file_path):
            import csv

            with open(file_path, "r") as f:
                reader = csv.reader(f)  # Assuming tab-delimited CSV
                rows = []
                for row in reader:
                    if len(row) == 0:
                        continue
                    rows.append(row)
                return rows

        rows = parse_csv(filepath)
        vertices = []
        for row in rows:
            coordinates = cls.enh2xyz([float(row[0]), float(row[1]), float(row[2])])
            vertices.append(coordinates)

        mesh = bpy.data.meshes.new("mesh")
        obj = bpy.data.objects.new("Plot Line", mesh)
        bpy.context.scene.collection.objects.link(obj)
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        obj.data
        bm = bmesh.new()
        for vertex in vertices:
            bm.verts.new(vertex)
        bm.to_mesh(mesh)
        bm.free()

    @classmethod
    def import_wcs(cls):
        props = bpy.context.scene.BIMGeoreferenceProperties
        wcs = None
        for context in tool.Ifc.get().by_type("IfcGeometricRepresentationContext", include_subtypes=False):
            wcs = context.WorldCoordinateSystem
            if context.ContextType == "Model":
                break
        if not wcs:
            return
        placement = ifcopenshell.util.placement.get_axis2placement(wcs)
        if np.allclose(placement, np.eye(4)):
            props.wcs_x = props.wcs_y = props.wcs_z = props.wcs_rotation = "0"
        else:
            props.wcs_rotation = str(round(ifcopenshell.util.geolocation.yaxis2angle(*placement[:, 1][:2]), 7))
            props.wcs_x, props.wcs_y, props.wcs_z = map(str, placement[:, 3][:3])

    @classmethod
    def export_wcs(cls):
        props = bpy.context.scene.BIMGeoreferenceProperties
        return {
            "x": float(props.wcs_x),
            "y": float(props.wcs_y),
            "z": float(props.wcs_z),
            "rotation": float(props.wcs_rotation),
        }

    @classmethod
    def set_wcs(cls, wcs):
        ifcopenshell.api.georeference.edit_wcs(tool.Ifc.get(), **wcs, is_si=False)

    @classmethod
    def set_model_origin(cls) -> None:
        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        gprops = bpy.context.scene.BIMGeoreferenceProperties
        e, n, h = cls.xyz2enh((0, 0, 0), should_return_in_map_units=False)
        gprops.model_origin = f"{e},{n},{h}"
        gprops.model_origin_si = f"{e * unit_scale},{n * unit_scale},{h * unit_scale}"
        angle = ifcopenshell.util.geolocation.get_grid_north(tool.Ifc.get())
        if gprops.has_blender_offset:
            angle += ifcopenshell.util.geolocation.xaxis2angle(
                float(gprops.blender_x_axis_abscissa), float(gprops.blender_x_axis_ordinate)
            )
            angle = tool.Cad.normalise_angle(angle)
        gprops.model_project_north = str(angle)
