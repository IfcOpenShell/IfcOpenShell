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


class Patcher:
    def __init__(self, src, file, logger, unit="METERS"):
        """Converts the length unit of a model to the specified unit

        Allowed metric units include METERS, MILLIMETERS, CENTIMETERS, etc.
        Allowed imperial units include INCHES, FEET, MILES.

        :param unit: The name of the desired unit.
        :type unit: str

        Example:

        .. code:: python

            # Convert to millimeters
            ifcpatch.execute({"input": model, "recipe": "ConvertLengthUnit", "arguments": ["MILLIMETERS"]})

            # Convert to feet
            ifcpatch.execute({"input": model, "recipe": "ConvertLengthUnit", "arguments": ["FEET"]})
        """
        self.src = src
        self.file = file
        self.logger = logger
        self.unit = unit

    def patch(self):
        unit = {"is_metric": "METERS" in self.unit, "raw": self.unit}
        self.file_patched = ifcopenshell.api.run("project.create_file", version=self.file.schema)
        if self.file.schema == "IFC2X3":
            user = self.file_patched.add(self.file.by_type("IfcProject")[0].OwnerHistory.OwningUser)
            application = self.file_patched.add(self.file.by_type("IfcProject")[0].OwnerHistory.OwningApplication)
            old_get_user = ifcopenshell.api.owner.settings.get_user
            old_get_application = ifcopenshell.api.owner.settings.get_application
            ifcopenshell.api.owner.settings.get_user = lambda ifc: user
            ifcopenshell.api.owner.settings.get_application = lambda ifc: application
        project = ifcopenshell.api.run("root.create_entity", self.file_patched, ifc_class="IfcProject")
        unit_assignment = ifcopenshell.api.run("unit.assign_unit", self.file_patched, **{"length": unit})

        # Is there a better way?
        for element in self.file.by_type("IfcGeometricRepresentationContext", include_subtypes=False):
            element.Precision = 1e-8

        # If we don't add openings first, they don't get converted
        for element in self.file.by_type("IfcOpeningElement"):
            self.file_patched.add(element)

        for element in self.file:
            self.file_patched.add(element)

        new_length = [u for u in unit_assignment.Units if getattr(u, "UnitType", None) == "LENGTHUNIT"][0]
        old_length = [
            u
            for u in self.file_patched.by_type("IfcProject")[1].UnitsInContext.Units
            if getattr(u, "UnitType", None) == "LENGTHUNIT"
        ][0]

        for inverse in self.file_patched.get_inverse(old_length):
            ifcopenshell.util.element.replace_attribute(inverse, old_length, new_length)

        self.file_patched.remove(old_length)
        self.file_patched.remove(project)

        if self.file.schema == "IFC2X3":
            ifcopenshell.api.owner.settings.get_user = old_get_user
            ifcopenshell.api.owner.settings.get_application = old_get_application
