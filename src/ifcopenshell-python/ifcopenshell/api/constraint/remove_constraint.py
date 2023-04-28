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
    def __init__(self, file, constraint=None):
        """Remove a constraint (typically an objective)

        Removes a constraint definition and all of its associations to any
        products. Typically this would be an IfcObjective, although technically
        you can associate IfcMetrics ith products too, though the meaning may be
        unclear.

        :param constraint: The IfcObjective you want to remove.
        :type constraint: ifcopenshell.entity_instance.entity_instance
        :return: None
        :rtype: None

        Example:

        .. code:: python

            objective = ifcopenshell.api.run("constraint.add_objective", model)
            ifcopenshell.api.run("constraint.remove_constraint", model,
                constraint=objective)
        """
        self.file = file
        self.settings = {"constraint": constraint}

    def execute(self):
        self.file.remove(self.settings["constraint"])
        for rel in self.file.by_type("IfcRelAssociatesConstraint"):
            if not rel.RelatingConstraint:
                self.file.remove(rel)
