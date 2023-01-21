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

import ifcopenshell.api


class Usecase:
    def __init__(self, file, relation=None):
        """Removes a relationship between a connection and a condition

        The condition and the member itself is preserved.

        :param relation: The IfcRelConnectsStructuralMember to remove.
        :type relation: ifcopenshell.entity_instance.entity_instance
        :return: None
        :rtype: None
        """
        self.file = file
        self.settings = {"relation": relation}

    def execute(self):
        if self.settings["relation"].AppliedCondition:
            ifcopenshell.api.run(
                "structural.remove_structural_boundary_condition",
                self.file,
                **{"connection": self.settings["relation"].RelatedStructuralConnection}
            )
        self.file.remove(self.settings["relation"])
