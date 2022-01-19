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


class Usecase:
    def __init__(self, file, **settings):
        self.file = file

    def execute(self):
        source_crs = None
        for context in self.file.by_type("IfcGeometricRepresentationContext", include_subtypes=False):
            if context.ContextType == "Model":
                source_crs = context
                break
        if not source_crs:
            return
        projected_crs = self.file.create_entity("IfcProjectedCRS", **{"Name": ""})
        self.file.create_entity(
            "IfcMapConversion",
            **{
                "SourceCRS": source_crs,
                "TargetCRS": projected_crs,
                "Eastings": 0,
                "Northings": 0,
                "OrthogonalHeight": 0,
            }
        )
