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


class Usecase:
    def __init__(self, file, objective=None):
        """Add a new metric benchmark

        Qualitative constraints may have a series of quantitative benchmarks
        linked to it known as metrics. Metrics may be parametrically linked to
        computed model properties or quantities. Metrics need to be satisfied
        to meet the objective of the constraint.

        :param objective: The IfcObjective that this metric is a benchmark of.
        :type objective: ifcopenshell.entity_instance.entity_instance
        :return: The newly created IfcMetric entity
        :rtype: ifcopenshell.entity_instance.entity_instance

        Example:

        .. code:: python

            objective = ifcopenshell.api.run("constraint.add_objective", model)
            metric = ifcopenshell.api.run("constraint.add_metric", model,
                objective=objective)
        """
        self.file = file
        self.settings = {
            "objective": objective,
        }

    def execute(self):
        metric = self.file.create_entity(
            "IfcMetric",
            **{
                "Name": "Unnamed",
                "ConstraintGrade": "NOTDEFINED",
                "Benchmark": "EQUALTO",
            }
        )
        if self.settings["objective"]:
            benchmark_values = list(self.settings["objective"].BenchmarkValues or [])
            benchmark_values.append(metric)
        return metric
