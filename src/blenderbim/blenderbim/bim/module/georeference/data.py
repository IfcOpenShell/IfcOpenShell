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
import numpy as np
import blenderbim.tool as tool
import ifcopenshell.util.geolocation
from mathutils import Matrix
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
            wcs[0][3] *= unit_scale
            wcs[1][3] *= unit_scale
            wcs[2][3] *= unit_scale
            result["matrix"] = Matrix(wcs)
        return result
