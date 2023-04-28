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
    def __init__(self, file):
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

        :return: None
        :rtype: None

        Example:

        .. code:: python

            ifcopenshell.api.run("georeference.add_georeferencing", model)
        """
        self.file = file

    def execute(self):
        source_crs = None
        for context in self.file.by_type("IfcGeometricRepresentationContext", include_subtypes=False):
            if context.ContextType == "Model":
                source_crs = context
                break
        if not source_crs:
            return
        projected_crs = self.file.create_entity("IfcProjectedCRS", **{"Name": ""})
        self.file.create_entity(
            "IfcMapConversion",
            **{
                "SourceCRS": source_crs,
                "TargetCRS": projected_crs,
                "Eastings": 0,
                "Northings": 0,
                "OrthogonalHeight": 0,
            }
        )
