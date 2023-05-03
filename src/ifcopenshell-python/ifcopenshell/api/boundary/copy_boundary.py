# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2023 Dion Moult <dion@thinkmoult.com>
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

import ifcopenshell.util.element


class Usecase:
    def __init__(self, file, boundary=None):
        """Copies a space boundary

        :param boundary: The IfcRelSpaceBoundary you want to copy.
        :type boundary: ifcopenshell.entity_instance.entity_instance
        :return: None
        :rtype: None

        Example:

            # A boring boundary with no geometry. Note that this boundary is
            # invalid and does not relate to any space or building element.
            boundary = ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcRelSpaceBoundary")

            # And now we have two
            boundary_copy = ifcopenshell.api.run("boundary.copy_boundary", model, boundary=boundary)
        """
        self.file = file
        self.settings = {"boundary": boundary}

    def execute(self):
        result = ifcopenshell.util.element.copy(self.file, self.settings["boundary"])
        if result.ConnectionGeometry:
            result.ConnectionGeometry = ifcopenshell.util.element.copy_deep(self.file, result.ConnectionGeometry)
        return result
