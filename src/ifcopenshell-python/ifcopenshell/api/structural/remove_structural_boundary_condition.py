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
    def __init__(self, file, connection=None, boundary_condition=None):
        """Removes a condition from a connection, or an orphased boundary condition

        :param connection: The IfcStructuralConnection to remove the condition
            from. If omitted, it is assumed to be an orphaned condition.
        :type connection: ifcopenshell.entity_instance.entity_instance,optional
        :param boundary_condition: The IfcBoundaryCondition to remove.
        :type boundary_condition: ifcopenshell.entity_instance.entity_instance
        :return: None
        :rtype: None
        """
        self.file = file
        self.settings = {"connection": connection, "boundary_condition": boundary_condition}

    def execute(self):
        if self.settings["connection"]:
            # remove boundary condition from a connection
            if not self.settings["connection"].AppliedCondition:
                return
            if len(self.file.get_inverse(self.settings["connection"].AppliedCondition)) == 1:
                self.file.remove(self.settings["connection"].AppliedCondition)
            self.settings["connection"].AppliedCondition = None
        else:
            # remove the boundary condition
            for conn in self.file.get_inverse(self.settings["boundary_condition"]):
                conn.AppliedCondition = None
            self.file.remove(self.settings["boundary_condition"])
