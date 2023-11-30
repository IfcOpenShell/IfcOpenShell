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
import blenderbim.core.tool
import blenderbim.tool as tool
import ifcopenshell
import blenderbim.bim.helper
from math import radians, degrees, atan, tan, cos, sin


class Georeference(blenderbim.core.tool.Georeference):
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
    def import_map_conversion(cls):
        def callback(name, prop, data):
            if name not in ["SourceCRS", "TargetCRS"]:
                # Enforce a string data type to prevent data loss in single-precision Blender props
                prop.data_type = "string"
                prop.string_value = "" if prop.is_null else str(data[name])
                return True

        props = bpy.context.scene.BIMGeoreferenceProperties
        props.map_conversion.clear()

        if tool.Ifc.get_schema() == "IFC2X3":
            return

        for context in tool.Ifc.get().by_type("IfcGeometricRepresentationContext", include_subtypes=False):
            if context.HasCoordinateOperation:
                map_conversion = context.HasCoordinateOperation[0]
                blenderbim.bim.helper.import_attributes2(map_conversion, props.map_conversion, callback=callback)
                return

    @classmethod
    def import_true_north(cls):
        if tool.Ifc.get_schema() == "IFC2X3":
            return

        props = bpy.context.scene.BIMGeoreferenceProperties
        props.has_true_north = False
        for context in tool.Ifc.get().by_type("IfcGeometricRepresentationContext", include_subtypes=False):
            if context.TrueNorth:
                true_north = context.TrueNorth.DirectionRatios
                props.true_north_abscissa = str(true_north[0])
                props.true_north_ordinate = str(true_north[1])
                props.has_true_north = True
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
    def get_map_conversion_attributes(cls):
        def callback(attributes, prop):
            if not prop.is_null and prop.data_type == "string":
                # We store our floats as string to prevent single precision data loss
                attributes[prop.name] = float(prop.string_value)
                return True

        props = bpy.context.scene.BIMGeoreferenceProperties
        return blenderbim.bim.helper.export_attributes(props.map_conversion, callback=callback)

    @classmethod
    def get_true_north_attributes(cls):
        props = bpy.context.scene.BIMGeoreferenceProperties
        if props.has_true_north:
            try:
                return [float(props.true_north_abscissa), float(props.true_north_ordinate)]
            except ValueError:
                print("ERROR, True North Abscissa and Ordinate expect a number")
                # self.report({"ERROR"}, "True North Abscissa and Ordinate expect a number")

    @classmethod
    def enable_editing(cls):
        bpy.context.scene.BIMGeoreferenceProperties.is_editing = True

    @classmethod
    def disable_editing(cls):
        bpy.context.scene.BIMGeoreferenceProperties.is_editing = False

    @classmethod
    def set_coordinates(cls, io, coordinates):
        if io == "input":
            bpy.context.scene.BIMGeoreferenceProperties.coordinate_input = ",".join([str(o) for o in coordinates])
        elif io == "output":
            bpy.context.scene.BIMGeoreferenceProperties.coordinate_output = ",".join([str(o) for o in coordinates])

    @classmethod
    def get_coordinates(cls, io):
        if io == "input":
            return [float(co) for co in bpy.context.scene.BIMGeoreferenceProperties.coordinate_input.split(",")]
        elif io == "output":
            return [float(co) for co in bpy.context.scene.BIMGeoreferenceProperties.coordinate_output.split(",")]

    @classmethod
    def get_cursor_location(cls):
        props = bpy.context.scene.BIMGeoreferenceProperties
        scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        return [o / scale for o in bpy.context.scene.cursor.location]

    @classmethod
    def set_cursor_location(cls, coordinates):
        scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        bpy.context.scene.cursor.location = [co * scale for co in coordinates]

    @classmethod
    def set_ifc_true_north(cls):
        y_angle = -bpy.context.scene.sun_pos_properties.north_offset + radians(90)
        bpy.context.scene.BIMGeoreferenceProperties.true_north_abscissa = str(cos(y_angle))
        bpy.context.scene.BIMGeoreferenceProperties.true_north_ordinate = str(sin(y_angle))

    @classmethod
    def set_blender_true_north(cls):
        bpy.context.scene.sun_pos_properties.north_offset = -radians(
            ifcopenshell.util.geolocation.yaxis2angle(
                float(bpy.context.scene.BIMGeoreferenceProperties.true_north_abscissa),
                float(bpy.context.scene.BIMGeoreferenceProperties.true_north_ordinate),
            )
        )

    @classmethod
    def xyz2enh(cls, coordinates):
        props = bpy.context.scene.BIMGeoreferenceProperties
        if props.has_blender_offset:
            coordinates = ifcopenshell.util.geolocation.xyz2enh(
                coordinates[0],
                coordinates[1],
                coordinates[2],
                float(props.blender_eastings),
                float(props.blender_northings),
                float(props.blender_orthogonal_height),
                float(props.blender_x_axis_abscissa),
                float(props.blender_x_axis_ordinate),
                1.0,
            )
        return ifcopenshell.util.geolocation.auto_xyz2enh(tool.Ifc.get(), *coordinates)

    @classmethod
    def enh2xyz(cls, coordinates):
        coordinates = ifcopenshell.util.geolocation.auto_enh2xyz(tool.Ifc.get(), *coordinates)
        props = bpy.context.scene.BIMGeoreferenceProperties
        if props.has_blender_offset:
            coordinates = ifcopenshell.util.geolocation.enh2xyz(
                coordinates[0],
                coordinates[1],
                coordinates[2],
                float(props.blender_eastings),
                float(props.blender_northings),
                float(props.blender_orthogonal_height),
                float(props.blender_x_axis_abscissa),
                float(props.blender_x_axis_ordinate),
                1.0,
            )
        return coordinates

    @classmethod
    def set_ifc_grid_north(cls):
        x_angle = bpy.context.scene.sun_pos_properties.north_offset
        props = bpy.context.scene.BIMGeoreferenceProperties
        props.map_conversion.get("XAxisAbscissa").string_value = str(cos(x_angle))
        props.map_conversion.get("XAxisOrdinate").string_value = str(sin(x_angle))

    @classmethod
    def set_blender_grid_north(cls):
        props = bpy.context.scene.BIMGeoreferenceProperties
        angle = ifcopenshell.util.geolocation.xaxis2angle(
            float(props.map_conversion.get("XAxisAbscissa").string_value),
            float(props.map_conversion.get("XAxisOrdinate").string_value),
        )
        bpy.context.scene.sun_pos_properties.north_offset = -radians(angle)

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
    def import_plot(cls, filepath, map_conversion):
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
