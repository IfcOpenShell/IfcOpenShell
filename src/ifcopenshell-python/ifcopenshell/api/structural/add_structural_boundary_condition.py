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
        self.settings = {"name": None, "connection": None, "ifc_class": "IfcBoundaryNodeCondition"}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        if self.settings["connection"]:
            # assign boundary condition to a connection
            if self.settings["connection"].is_a("IfcRelConnectsStructuralMember"):
                related_connection = self.settings["connection"].RelatedStructuralConnection
            else:
                related_connection = self.settings["connection"]

            if related_connection.is_a("IfcStructuralPointConnection"):
                boundary_class = "IfcBoundaryNodeCondition"
            elif related_connection.is_a("IfcStructuralCurveConnection"):
                boundary_class = "IfcBoundaryEdgeCondition"
            elif related_connection.is_a("IfcStructuralSurfaceConnection"):
                boundary_class = "IfcBoundaryFaceCondition"

            self.settings["connection"].AppliedCondition = self.file.create_entity(
                boundary_class, Name=self.settings["name"]
            )
        else:
            # add an orphan boundary condition
            return self.file.create_entity(self.settings["ifc_class"], Name=self.settings["name"])
