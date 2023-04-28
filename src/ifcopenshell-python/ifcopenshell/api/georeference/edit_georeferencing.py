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
    def __init__(self, file, map_conversion=None, projected_crs=None, true_north=None):
        """Edits the attributes of a map conversion, projected CRS, and true north

        Setting the correct georeferencing parameters is a complex topic and
        should ideally be done with three parties present: the lead architect,
        surveyor, and a third-party digital engineer with expertise in IFC to
        moderate. For more information, read the BlenderBIM Add-on documentation
        for Georeferencing:
        https://blenderbim.org/docs/users/georeferencing.html

        For more information about the attributes and data types of an
        IfcMapConversion, consult the IFC documentation.

        For more information about the attributes and data types of an
        IfcProjectedCRS, consult the IFC documentation.

        True north is defined as a unitised 2D vector pointing to true north.
        Note that true north is not part of georeferencing, and is only
        optionally provided as a reference value, typically for solar analysis.

        See ifcopenshell.util.geolocation for more utilities to convert to and
        from local and map coordinates to check your results.

        :param map_conversion: The IfcMapConversion dictionary of attribute
            names and values you want to edit.
        :type map_conversion: dict, optional
        :param projected_crs: The IfcProjectedCRS dictionary of attribute
            names and values you want to edit.
        :type projected_crs: dict, optional
        :param true_north: A unitised 2D vector, where each ordinate is a float
        :type true_north: list[float]
        :return: None
        :rtype: None

        Example:

        .. code:: python

            ifcopenshell.api.run("georeference.add_georeferencing", model)
            # This is the simplest scenario, a defined CRS (GDA2020 / MGA Zone
            # 56, typically used in Sydney, Australia) but with no local
            # coordinates. This is only recommended for horizontal construction
            # projects, not for vertical construction (such as buildings).
            ifcopenshell.api.run("georeference.edit_georeferencing", model,
                projected_crs={"Name": "EPSG:7856"})

            # For buildings, it is almost always recommended to specify map
            # conversion parameters to a false origin and orientation to project
            # north. See the diagram in the BlenderBIM Add-on Georeferencing
            # documentation for correct calculation of the X Axis Abcissa and
            # Ordinate.
            ifcopenshell.api.run("georeference.edit_georeferencing", model,
                projected_crs={"Name": "EPSG:7856"},
                map_conversion={
                    "Eastings": 335087.17, # The architect nominates a false origin
                    "Northings": 6251635.41, # The architect nominates a false origin
                    # Note: this is the angle difference between Project North
                    # and Grid North. Remember: True North should never be used!
                    "XAxisAbscissa": cos(radians(-30)), # The architect nominates a project north
                    "XAxisOrdinate": sin(radians(-30)), # The architect nominates a project north
                    "Scale": 0.99956, # Ask your surveyor for your site's average combined scale factor!
                })
        """
        self.file = file
        self.settings = {
            "map_conversion": map_conversion or {},
            "projected_crs": projected_crs or {},
            "true_north": true_north or [],
        }

    def execute(self):
        map_conversion = self.file.by_type("IfcMapConversion")[0]
        projected_crs = self.file.by_type("IfcProjectedCRS")[0]
        for name, value in self.settings["map_conversion"].items():
            setattr(map_conversion, name, value)
        for name, value in self.settings["projected_crs"].items():
            setattr(projected_crs, name, value)
        self.set_true_north()

    def set_true_north(self):
        if self.settings["true_north"] == []:
            return
        for context in self.file.by_type("IfcGeometricRepresentationContext", include_subtypes=False):
            if context.TrueNorth:
                if len(self.file.get_inverse(context.TrueNorth)) != 1:
                    context.TrueNorth = self.file.create_entity("IfcDirection")
            else:
                context.TrueNorth = self.file.create_entity("IfcDirection")
            direction = context.TrueNorth
            if self.settings["true_north"] is None:
                context.TrueNorth = self.settings["true_north"]
            elif context.CoordinateSpaceDimension == 2:
                direction.DirectionRatios = self.settings["true_north"][0:2]
            else:
                direction.DirectionRatios = self.settings["true_north"][0:2] + [0.0]
