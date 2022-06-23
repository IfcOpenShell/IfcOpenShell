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
import ifcopenshell.util.geolocation
import blenderbim.tool as tool


def refresh():
    GeoreferenceData.is_loaded = False


class GeoreferenceData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.data["blender_derived_angle"] = cls.blender_derived_angle()
        cls.data["map_conversion"] = cls.map_conversion()
        cls.data["map_derived_angle"] = cls.map_derived_angle()
        cls.data["projected_crs"] = cls.projected_crs()
        cls.data["true_north"] = cls.true_north()
        cls.data["true_derived_angle"] = cls.true_derived_angle()
        cls.is_loaded = True

    @classmethod
    def blender_derived_angle(cls):
        props = bpy.context.scene.BIMGeoreferenceProperties
        if props.has_blender_offset:
            return str(
                round(
                    ifcopenshell.util.geolocation.xaxis2angle(
                        float(props.blender_x_axis_abscissa), float(props.blender_x_axis_ordinate)
                    ),
                    3,
                )
            )

    @classmethod
    def map_conversion(cls):
        if tool.Ifc.get_schema() == "IFC2X3":
            return {}

        for context in tool.Ifc.get().by_type("IfcGeometricRepresentationContext", include_subtypes=False):
            if context.HasCoordinateOperation:
                map_conversion = context.HasCoordinateOperation[0].get_info()
                del map_conversion["id"]
                del map_conversion["type"]
                del map_conversion["SourceCRS"]
                del map_conversion["TargetCRS"]
                return map_conversion
        return {}

    @classmethod
    def map_derived_angle(cls):
        if (
            cls.data["map_conversion"]
            and cls.data["map_conversion"]["XAxisAbscissa"] is not None
            and cls.data["map_conversion"]["XAxisOrdinate"] is not None
        ):
            return str(
                round(
                    ifcopenshell.util.geolocation.xaxis2angle(
                        cls.data["map_conversion"]["XAxisAbscissa"], cls.data["map_conversion"]["XAxisOrdinate"]
                    ),
                    3,
                )
            )
        return ""

    @classmethod
    def projected_crs(cls):
        if tool.Ifc.get_schema() == "IFC2X3":
            return {}

        for context in tool.Ifc.get().by_type("IfcGeometricRepresentationContext", include_subtypes=False):
            if context.HasCoordinateOperation:
                projected_crs = context.HasCoordinateOperation[0].TargetCRS.get_info()
                del projected_crs["id"]
                del projected_crs["type"]
                if projected_crs["MapUnit"]:
                    unit = projected_crs["MapUnit"]
                    projected_crs["MapUnit"] = (getattr(unit, "Prefix", "") or "") + unit.Name
                return projected_crs
        return {}

    @classmethod
    def true_north(cls):
        ifc = tool.Ifc.get()
        true_north = {}

        if ifc.schema == "IFC2X3":
            return

        for context in ifc.by_type("IfcGeometricRepresentationContext", include_subtypes=False):
            if not context.TrueNorth:
                continue
            true_north = context.TrueNorth.DirectionRatios
            break

        return true_north

    @classmethod
    def true_derived_angle(cls):
        if cls.data["true_north"]:
            return str(round(ifcopenshell.util.geolocation.yaxis2angle(*cls.data["true_north"][0:2]), 3))
