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
from typing import Optional, Any


def edit_georeferencing(
    file: ifcopenshell.file,
    coordinate_operation: Optional[dict[str, Any]] = None,
    projected_crs: Optional[dict[str, Any]] = None,
) -> None:
    """Edits the attributes of a map conversion, projected CRS, and true north

    Setting the correct georeferencing parameters is a complex topic and
    should ideally be done with three parties present: the lead architect,
    surveyor, and a third-party digital engineer with expertise in IFC to
    moderate. For more information, read the Bonsai documentation
    for Georeferencing:
    https://docs.bonsaibim.org/users/advanced/georeferencing.html

    For more information about the attributes and data types of an
    IfcCoordinateOperation, consult the IFC documentation.

    For more information about the attributes and data types of an
    IfcProjectedCRS, consult the IFC documentation.

    See ifcopenshell.util.geolocation for more utilities to convert to and
    from local and map coordinates to check your results.

    :param coordinate_operation: The dictionary of attribute names and values
        you want to edit.
    :param projected_crs: The IfcProjectedCRS dictionary of attribute
        names and values you want to edit.

    Example:

    .. code:: python

        ifcopenshell.api.georeference.add_georeferencing(model)
        # This is the simplest scenario, a defined CRS (GDA2020 / MGA Zone
        # 56, typically used in Sydney, Australia) but with no local
        # coordinates. This is only recommended for horizontal construction
        # projects, not for vertical construction (such as buildings).
        ifcopenshell.api.georeference.edit_georeferencing(model,
            projected_crs={"Name": "EPSG:7856"})

        # For buildings, it is almost always recommended to specify map
        # conversion parameters to a false origin and orientation to project
        # north. See the diagram in the Bonsai Georeferencing
        # documentation for correct calculation of the X Axis Abcissa and
        # Ordinate.
        ifcopenshell.api.georeference.edit_georeferencing(model,
            projected_crs={"Name": "EPSG:7856"},
            coordinate_operation={
                "Eastings": 335087.17, # The architect nominates a false origin
                "Northings": 6251635.41, # The architect nominates a false origin
                # Note: this is the angle difference between Project North
                # and Grid North. Remember: True North should never be used!
                "XAxisAbscissa": cos(radians(-30)), # The architect nominates a project north
                "XAxisOrdinate": sin(radians(-30)), # The architect nominates a project north
                "Scale": 0.99956, # Ask your surveyor for your site's average combined scale factor!
            })
    """
    if file.schema == "IFC2X3":
        if not (project := file.by_type("IfcProject")):
            return
        project = project[0]
        if projected_crs:
            if crs := ifcopenshell.util.element.get_pset(project, "ePSet_ProjectedCRS"):
                crs = file.by_id(crs["id"])
                for k, v in projected_crs.items():
                    if k == "Description":
                        v = file.createIfcText(v)
                    elif k == "Name":
                        v = file.createIfcLabel(v)
                    else:
                        v = file.createIfcIdentifier(v)
                ifcopenshell.api.pset.edit_pset(file, crs, properties=projected_crs)
        if coordinate_operation:
            if conversion := ifcopenshell.util.element.get_pset(project, "ePSet_MapConversion"):
                conversion = file.by_id(conversion["id"])
                for k, v in coordinate_operation.items():
                    if k in ("XAxisAbscissa", "XAxisOrdinate", "Scale"):
                        v = file.createIfcReal(v)
                    else:
                        v = file.createIfcLengthMeasure(v)
                ifcopenshell.api.pset.edit_pset(file, conversion, properties=coordinate_operation)
        return
    if projected_crs:
        crs = file.by_type("IfcProjectedCRS")[0]
        for name, value in projected_crs.items():
            setattr(crs, name, value)
    if coordinate_operation:
        conversion = file.by_type("IfcCoordinateOperation")[0]
        for name, value in coordinate_operation.items():
            setattr(conversion, name, value)
