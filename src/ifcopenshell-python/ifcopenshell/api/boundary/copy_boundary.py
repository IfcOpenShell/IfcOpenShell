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


def copy_boundary(file: ifcopenshell.file, boundary: ifcopenshell.entity_instance) -> ifcopenshell.entity_instance:
    """Copies a space boundary

    :param boundary: The IfcRelSpaceBoundary you want to copy.
    :return: Duplicate of the IfcRelSpaceBoundary

    Example:

        # A boring boundary with no geometry. Note that this boundary is
        # invalid and does not relate to any space or building element.
        boundary = ifcopenshell.api.root.create_entity(model, ifc_class="IfcRelSpaceBoundary")

        # And now we have two
        boundary_copy = ifcopenshell.api.boundary.copy_boundary(model, boundary=boundary)
    """
    result = ifcopenshell.util.element.copy(file, boundary)
    if result.ConnectionGeometry:
        result.ConnectionGeometry = ifcopenshell.util.element.copy_deep(file, result.ConnectionGeometry)
    return result
