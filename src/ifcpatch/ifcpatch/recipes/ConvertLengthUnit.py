# IfcPatch - IFC patching utiliy
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of IfcPatch.
#
# IfcPatch is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcPatch is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcPatch.  If not, see <http://www.gnu.org/licenses/>.

import ifcopenshell
import ifcopenshell.api
import ifcopenshell.api.owner.settings
import ifcopenshell.util.pset
import ifcopenshell.util.element
import ifcopenshell.util.unit
import ifcpatch
from logging import Logger

import typing
from typing import Union

LengthUnit = typing.Literal[
    "ATTOMETER",
    "FEMTOMETER",
    "PICOMETER",
    "NANOMETER",
    "MICROMETER",
    "MILLIMETER",
    "CENTIMETER",
    "DECIMETER",
    "METER",
    "DECAMETER",
    "HECTOMETER",
    "KILOMETER",
    "MEGAMETER",
    "GIGAMETER",
    "TERAMETER",
    "PETAMETER",
    "EXAMETER",
    "INCH",
    "FOOT",
    "MILE",
]


class Patcher(ifcpatch.BasePatcher):
    def __init__(
        self,
        file: ifcopenshell.file,
        logger: Union[Logger, None] = None,
        unit: LengthUnit = "METER",
    ):
        """Converts the length unit of a model to the specified unit

        Allowed metric units include METER, MILLIMETER, CENTIMETER, etc.
        Allowed imperial units include INCH, FOOT, MILE.

        :param unit: The name of the desired unit, defaults to "METER"

        Example:

        .. code:: python

            # Convert to millimeters
            model = ifcpatch.execute({"input": "input.ifc", "file": model, "recipe": "ConvertLengthUnit", "arguments": ["MILLIMETER"]})

            # Convert to feet
            model = ifcpatch.execute({"input": "input.ifc", "file": model, "recipe": "ConvertLengthUnit", "arguments": ["FOOT"]})
        """
        super().__init__(file, logger)
        self.unit = unit
        self.file_patched: ifcopenshell.file

    def patch(self):
        self.file_patched = ifcopenshell.util.unit.convert_file_length_units(self.file, self.unit)
