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

import ifcopenshell
import ifcopenshell.util.element


def remove_boundary(file: ifcopenshell.file, boundary: ifcopenshell.entity_instance) -> None:
    """Removes a space boundary

    The relating space or related building element is untouched. Only the
    boundary and its connection geometry is removed.

    :param boundary: The IfcRelSpaceBoundary you want to remove.
    :type boundary: ifcopenshell.entity_instance
    :return: None
    :rtype: None

    Example:

        # A boring boundary with no geometry. Note that this boundary is
        # invalid and does not relate to any space or building element.
        boundary = ifcopenshell.api.root.create_entity(model, ifc_class="IfcRelSpaceBoundary")

        # Let's remove it!
        ifcopenshell.api.boundary.remove_boundary(model, boundary=boundary)
    """
    settings = {"boundary": boundary}

    geometry = settings["boundary"].ConnectionGeometry
    if geometry:
        settings["boundary"].ConnectionGeometry = None
        ifcopenshell.util.element.remove_deep2(file, geometry)
    history = settings["boundary"].OwnerHistory
    file.remove(settings["boundary"])
    if history:
        ifcopenshell.util.element.remove_deep2(file, history)
