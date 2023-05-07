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
        """Removes a space boundary

        The relating space or related building element is untouched. Only the
        boundary and its connection geometry is removed.

        :param boundary: The IfcRelSpaceBoundary you want to remove.
        :type boundary: ifcopenshell.entity_instance.entity_instance
        :return: None
        :rtype: None

        Example:

            # A boring boundary with no geometry. Note that this boundary is
            # invalid and does not relate to any space or building element.
            boundary = ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcRelSpaceBoundary")

            # Let's remove it!
            ifcopenshell.api.run("boundary.remove_boundary", model, boundary=boundary)
        """
        self.file = file
        self.settings = {"boundary": boundary}

    def execute(self):
        geometry = self.settings["boundary"].ConnectionGeometry
        if geometry:
            self.settings["boundary"].ConnectionGeometry = None
            ifcopenshell.util.element.remove_deep2(self.file, geometry)
        self.file.remove(self.settings["boundary"])
