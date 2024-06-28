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

import ifcopenshell
import ifcopenshell.api.pset
import ifcopenshell.util.element


def remove_georeferencing(file: ifcopenshell.file) -> None:
    """Remove georeferencing data

    All georeferencing parameters such as projected CRS and map conversion
    data will be lost.

    In IFC2X3, the psets will be removed from the IfcProject.

    Example:

        ifcopenshell.api.georeference.add_georeferencing(model)
        # Let's change our mind
        ifcopenshell.api.georeference.remove_georeferencing(model)
    """
    if file.schema == "IFC2X3":
        project = file.by_type("IfcProject")[0]
        if pset := ifcopenshell.util.element.get_pset(project, "ePSet_ProjectedCRS"):
            ifcopenshell.api.pset.remove_pset(file, project, file.by_id(pset["id"]))
        if pset := ifcopenshell.util.element.get_pset(project, "ePSet_MapConversion"):
            ifcopenshell.api.pset.remove_pset(file, project, file.by_id(pset["id"]))
        return
    for projected_crs in file.by_type("IfcProjectedCRS"):
        if (unit := projected_crs.MapUnit) and len(file.get_inverse(unit)) == 1:
            projected_crs.MapUnit = None
            ifcopenshell.util.element.remove_deep2(file, unit)
        file.remove(projected_crs)
    for coordinate_operation in file.by_type("IfcCoordinateOperation"):
        file.remove(coordinate_operation)
