# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
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
import numpy as np
import bonsai.tool as tool
import ifcopenshell.util.element
import ifcopenshell.util.geolocation
import ifcopenshell.util.schema
import ifcopenshell.util.unit
from mathutils import Matrix, Vector
from ifcopenshell.util.doc import get_entity_doc


def refresh():
    GeoreferenceData.is_loaded = False


class GeoreferenceData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.data["coordinate_operation_class"] = cls.coordinate_operation_class()
        cls.data["coordinate_operation"] = cls.coordinate_operation()
        cls.data["map_derived_angle"] = cls.map_derived_angle()
        cls.data["projected_crs"] = cls.projected_crs()
        cls.data["true_north"] = cls.true_north()
        cls.data["true_derived_angle"] = cls.true_derived_angle()
        cls.data["local_unit_symbol"] = cls.local_unit_symbol()
        cls.data["map_unit_symbol"] = cls.map_unit_symbol()
        cls.data["world_coordinate_system"] = cls.world_coordinate_system()
        cls.data["local_origin"] = cls.local_origin()
        cls.is_loaded = True

    @classmethod
    def coordinate_operation_class(cls):
        if tool.Ifc.get_schema() == "IFC2X3":
            return []
        declaration = tool.Ifc.schema().declaration_by_name("IfcCoordinateOperation")
        declarations = ifcopenshell.util.schema.get_subtypes(declaration)
        names = [d.name() for d in declarations]
        version = tool.Ifc.get_schema()
        return [(c, c, get_entity_doc(version, c).get("description", "")) for c in sorted(names)]

    @classmethod
    def coordinate_operation(cls):
        if tool.Ifc.get_schema() == "IFC2X3":
            project = tool.Ifc.get().by_type("IfcProject")[0]
            coordinate_operation = ifcopenshell.util.element.get_pset(project, "ePSet_MapConversion")
            if not coordinate_operation:
                return {}
            del coordinate_operation["id"]
            coordinate_operation["type"] = "ePSet_MapConversion"
            return coordinate_operation

        for context in tool.Ifc.get().by_type("IfcGeometricRepresentationContext", include_subtypes=False):
            if context.HasCoordinateOperation:
                coordinate_operation = context.HasCoordinateOperation[0].get_info()
                del coordinate_operation["id"]
                del coordinate_operation["SourceCRS"]
                del coordinate_operation["TargetCRS"]
                return coordinate_operation
        return {}

    @classmethod
    def map_derived_angle(cls):
        if (
            cls.data["coordinate_operation"]
            and cls.data["coordinate_operation"].get("XAxisAbscissa", None) is not None
            and cls.data["coordinate_operation"].get("XAxisOrdinate", None) is not None
        ):
            return str(
                round(
                    ifcopenshell.util.geolocation.xaxis2angle(
                        cls.data["coordinate_operation"]["XAxisAbscissa"],
                        cls.data["coordinate_operation"]["XAxisOrdinate"],
                    ),
                    3,
                )
            )
        return ""

    @classmethod
    def projected_crs(cls):
        if tool.Ifc.get_schema() == "IFC2X3":
            project = tool.Ifc.get().by_type("IfcProject")[0]
            projected_crs = ifcopenshell.util.element.get_pset(project, "ePSet_ProjectedCRS")
            if not projected_crs:
                return {}
            del projected_crs["id"]
            return projected_crs

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
        for context in ifc.by_type("IfcGeometricRepresentationContext", include_subtypes=False):
            if not context.TrueNorth:
                continue
            true_north = context.TrueNorth.DirectionRatios
            break
        return true_north

    @classmethod
    def true_derived_angle(cls):
        if cls.data["true_north"]:
            return str(round(ifcopenshell.util.geolocation.yaxis2angle(*cls.data["true_north"][:2]), 3))

    @classmethod
    def local_unit_symbol(cls):
        if not (unit := ifcopenshell.util.unit.get_project_unit(tool.Ifc.get(), "LENGTHUNIT")):
            return "n/a"
        return ifcopenshell.util.unit.get_unit_symbol(unit)

    @classmethod
    def map_unit_symbol(cls):
        if tool.Ifc.get().schema == "IFC2X3":
            return cls.local_unit_symbol()
        if crs := tool.Ifc.get().by_type("IfcProjectedCRS"):
            crs = crs[0]
            if not (unit := crs.MapUnit):
                return cls.local_unit_symbol()
            return ifcopenshell.util.unit.get_unit_symbol(unit)
        return "n/a"

    @classmethod
    def world_coordinate_system(cls):
        wcs = ifcopenshell.util.geolocation.get_wcs(tool.Ifc.get())
        result = {}
        if wcs is None:
            result["has_transformation"] = False
            return result
        if np.allclose(wcs, np.eye(4)):
            result["has_transformation"] = False
        else:
            unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
            result["has_transformation"] = True
            result["rotation"] = str(round(ifcopenshell.util.geolocation.yaxis2angle(*wcs[:, 1][:2]), 3))
            result["x"], result["y"], result["z"] = wcs[:, 3][:3]

            props = bpy.context.scene.BIMGeoreferenceProperties
            if props.has_blender_offset:
                blender_xyz = ifcopenshell.util.geolocation.enh2xyz(
                    result["x"],
                    result["y"],
                    result["z"],
                    float(props.blender_offset_x),
                    float(props.blender_offset_y),
                    float(props.blender_offset_z),
                    float(props.blender_x_axis_abscissa),
                    float(props.blender_x_axis_ordinate),
                )
            else:
                blender_xyz = wcs[:, 3][:3]

            result["blender_x"], result["blender_y"], result["blender_z"] = blender_xyz
            result["blender_location"] = Vector([co * unit_scale for co in blender_xyz])

            wcs[0][3] *= unit_scale
            wcs[1][3] *= unit_scale
            wcs[2][3] *= unit_scale
            result["matrix"] = Matrix(wcs)
        return result

    @classmethod
    def local_origin(cls):
        props = bpy.context.scene.BIMGeoreferenceProperties
        if not props.has_blender_offset:
            return
        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        x = float(props.blender_offset_x) * -1
        y = float(props.blender_offset_y) * -1
        z = float(props.blender_offset_z) * -1
        enh = ifcopenshell.util.geolocation.auto_xyz2enh(tool.Ifc.get(), 0, 0, 0)
        xyz_si = Vector([x * unit_scale, y * unit_scale, z * unit_scale])
        return {"x": x, "y": y, "z": z, "enh": enh, "location": xyz_si}
