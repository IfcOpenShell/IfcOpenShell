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
import ifcopenshell.util.alignment
import ifcpatch
from logging import Logger

import typing
from typing import Union


class Patcher(ifcpatch.BasePatcher):
    def __init__(self, file: ifcopenshell.file, logger: Union[Logger, None] = None):
        """Adds the IfcLinearPlacement.CartesianPosition fallback position to all of the IfcLinearPlacement objects in the file

        Example:

        .. code:: python

            model = ifcpatch.execute({"input": "input.ifc", "file": model, "recipe": "AddLinearPlacementFallbackPosition"})
        """
        super().__init__(file, logger)
        self.file_patched: ifcopenshell.file

    def patch(self):
        self.file_patched = ifcopenshell.util.alignment.add_linear_placement_fallback_position(self.file)
