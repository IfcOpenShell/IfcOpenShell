# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
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

import blenderbim.tool as tool

def refresh():
    GeoreferenceData.is_loaded = False

class GeoreferenceData:
    is_loaded = False
    data = {
        "map_conversion" : {},
        "projected_crs" : {},
        "true_north" : {},
    }

    @classmethod
    def load(cls):
        cls.file = tool.Ifc.get()

        if cls.file.schema == "IFC2X3":
            return

        cls.data["map_conversion"] = cls.get_map_conversion()
        cls.data["projected_crs"] = cls.get_projected_crs()
        cls.data["true_north"] = cls.get_true_north()
        cls.is_loaded = True

    @classmethod
    def get_map_conversion(cls):
        results = {}
        for context in cls.file.by_type("IfcGeometricRepresentationContext", include_subtypes=False):
            if not context.HasCoordinateOperation:
                continue
            map_conversion = context.HasCoordinateOperation[0]
            results = map_conversion.get_info()
            results["SourceCRS"] = results["SourceCRS"].id()
            results["TargetCRS"] = results["TargetCRS"].id()
        return results

    @classmethod
    def get_projected_crs(cls):
        results = {}
        for context in cls.file.by_type("IfcGeometricRepresentationContext", include_subtypes=False):
            if not context.HasCoordinateOperation:
                continue
            map_conversion = context.HasCoordinateOperation[0]
            results = map_conversion.TargetCRS.get_info()
            if results["MapUnit"]:
                results["MapUnit"] = map_conversion.TargetCRS.MapUnit.get_info()
        return results
            
    @classmethod
    def get_true_north(cls):
        results = {}
        for context in cls.file.by_type("IfcGeometricRepresentationContext", include_subtypes=False):
            if not context.TrueNorth:
                continue
            results = context.TrueNorth.DirectionRatios
        return results
        
        