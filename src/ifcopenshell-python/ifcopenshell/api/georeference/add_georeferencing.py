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


def add_georeferencing(file: ifcopenshell.file, ifc_class: str = "IfcMapConversion", name: str = "EPSG:3857") -> None:
    """Add empty georeferencing entities to a model

    By default, models are not georeferenced. Georeferencing requires two
    entities: a definition of the projected coordinated reference system
    (CRS) used, and the transformation parameters between any local coordinate
    system and that projected CRS if any.

    This function will create the entities to store the projected CRS and
    map conversion transformation, but will leave all the parameters blank.
    It is this the users responsibility to specify the correct
    georeferencing parameters. See
    ifcopenshell.api.georeference.edit_georeferencing.

    :param ifc_class: A type of IfcCoordinateOperation. For IFC2X3, this has no
        impact and only uses ePSet_MapConversion.

    Example:

    .. code:: python

        ifcopenshell.api.georeference.add_georeferencing(model)
    """
    if file.schema == "IFC2X3":
        if not (project := file.by_type("IfcProject")):
            return
        project = project[0]
        if ifcopenshell.util.element.get_pset(project, "ePSet_ProjectedCRS"):
            return
        conversion = ifcopenshell.api.pset.add_pset(file, project, "ePSet_MapConversion")
        crs = ifcopenshell.api.pset.add_pset(file, project, "ePSet_ProjectedCRS")
        ifcopenshell.api.pset.edit_pset(file, crs, properties={"Name": name})
        ifcopenshell.api.pset.edit_pset(
            file,
            conversion,
            properties={
                "Eastings": file.createIfcLengthMeasure(0),
                "Northings": file.createIfcLengthMeasure(0),
                "OrthogonalHeight": file.createIfcLengthMeasure(0),
            },
        )
        return
    if file.by_type("IfcProjectedCRS"):
        return
    source_crs = None
    for context in file.by_type("IfcGeometricRepresentationContext", include_subtypes=False):
        if context.ContextType == "Model":
            source_crs = context
            break
    if not source_crs:
        return
    projected_crs = file.create_entity("IfcProjectedCRS", Name=name)
    if ifc_class == "IfcMapConversion":
        file.create_entity(
            ifc_class, SourceCRS=source_crs, TargetCRS=projected_crs, Eastings=0, Northings=0, OrthogonalHeight=0
        )
    elif ifc_class == "IfcMapConversionScaled":
        file.create_entity(
            ifc_class,
            SourceCRS=source_crs,
            TargetCRS=projected_crs,
            Eastings=0,
            Northings=0,
            OrthogonalHeight=0,
            FactorX=1,
            FactorY=1,
            FactorZ=1,
        )
    elif ifc_class == "IfcRigidOperation":
        file.create_entity(
            ifc_class,
            SourceCRS=source_crs,
            TargetCRS=projected_crs,
            FirstCoordinate=file.createIfcLengthMeasure(0),
            SecondCoordinate=file.createIfcLengthMeasure(0),
        )
