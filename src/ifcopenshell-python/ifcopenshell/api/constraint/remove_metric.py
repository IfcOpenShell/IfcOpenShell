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
    def __init__(self, file, metric=None):
        """Remove a metric benchmark

        Removes a metric benchmark and all of its associations to any products
        and objectives.

        :param metric: The IfcMetric you want to remove.
        :type metric: ifcopenshell.entity_instance.entity_instance
        :return: None
        :rtype: None

        Example:

        .. code:: python

            objective = ifcopenshell.api.run("constraint.add_objective", model)
            metric = ifcopenshell.api.run("constraint.add_metric", model,
                objective=objective)
            ifcopenshell.api.run("constraint.remove_metric", model,
                metric=metric)
        """
        self.file = file
        self.settings = {"metric": metric}

    def execute(self):
        if self.settings["metric"].ReferencePath:
            reference = self.settings["metric"].ReferencePath
            self.delete_reference(reference)

        self.file.remove(self.settings["metric"])
        for rel in self.file.by_type("IfcRelAssociatesConstraint"):
            if not rel.RelatingConstraint:
                self.file.remove(rel)
        for resource_rel in self.file.by_type("IfcResourceConstraintRelationship"):
            if not resource_rel.RelatingConstraint:
                self.file.remove(resource_rel)

    def delete_reference(self, reference):
        if reference.InnerReference:
            self.delete_reference(reference.InnerReference)
        self.file.remove(reference)
