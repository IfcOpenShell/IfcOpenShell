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


def remove_georeferencing(file: ifcopenshell.file) -> None:
    """Remove georeferencing data

    All georeferencing parameters such as projected CRS and map conversion
    data will be lost.

    :return: None
    :rtype: None

    Example:

        ifcopenshell.api.run("georeference.add_georeferencing", model)
        # Let's change our mind
        ifcopenshell.api.run("georeference.remove_georeferencing", model)
    """

    map_conversion = file.by_type("IfcMapConversion")[0]
    projected_crs = file.by_type("IfcProjectedCRS")[0]
    if projected_crs.MapUnit and len(file.get_inverse(projected_crs.MapUnit)) == 1:
        # TODO: go deeper for conversion units
        file.remove(projected_crs.MapUnit)
    file.remove(projected_crs)
    file.remove(map_conversion)
