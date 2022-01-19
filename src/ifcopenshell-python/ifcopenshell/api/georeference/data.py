# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of IfcOpenShell.
#
# IfcOpenShell is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcOpenShell is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcOpenShell.  If not, see <http://www.gnu.org/licenses/>.


class Data:
    is_loaded = False
    map_conversion = {}
    projected_crs = {}
    true_north = {}

    @classmethod
    def purge(cls):
        cls.is_loaded = False
        cls.map_conversion = {}
        cls.projected_crs = {}
        cls.true_north = None

    @classmethod
    def load(cls, file):
        if not file:
            return
        cls.map_conversion = {}
        cls.projected_crs = {}
        cls.true_north = {}
        if file.schema == "IFC2X3":
            return
        for context in file.by_type("IfcGeometricRepresentationContext", include_subtypes=False):
            if not context.HasCoordinateOperation:
                continue
            map_conversion = context.HasCoordinateOperation[0]
            cls.map_conversion = map_conversion.get_info()
            cls.map_conversion["SourceCRS"] = cls.map_conversion["SourceCRS"].id()
            cls.map_conversion["TargetCRS"] = cls.map_conversion["TargetCRS"].id()
            cls.projected_crs = map_conversion.TargetCRS.get_info()
            if cls.projected_crs["MapUnit"]:
                cls.projected_crs["MapUnit"] = map_conversion.TargetCRS.MapUnit.get_info()
            break
        for context in file.by_type("IfcGeometricRepresentationContext", include_subtypes=False):
            if not context.TrueNorth:
                continue
            cls.true_north = context.TrueNorth.DirectionRatios
            break
        cls.is_loaded = True
