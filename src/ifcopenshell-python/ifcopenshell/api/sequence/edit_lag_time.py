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
import ifcopenshell.util.date


class Usecase:
    def __init__(self, file, lag_time=None, attributes=None):
        """Edits the attributes of an IfcLagTime

        For more information about the attributes and data types of an
        IfcLagTime, consult the IFC documentation.

        :param lag_time: The IfcLagTime entity you want to edit
        :type lag_time: ifcopenshell.entity_instance.entity_instance
        :param attributes: a dictionary of attribute names and values.
        :type attributes: dict, optional
        :return: None
        :rtype: None

        Example:

        .. code:: python

            # Let's imagine we are creating a construction schedule. All tasks
            # need to be part of a work schedule.
            schedule = ifcopenshell.api.run("sequence.add_work_schedule", model, name="Construction Schedule A")

            # Let's imagine a root construction task
            construction = ifcopenshell.api.run("sequence.add_task", model,
                work_schedule=schedule, name="Construction", identification="C")

            # Let's imagine we're doing a typically formwork, reinforcement,
            # pour sequence. Let's start with the formwork. It'll take us 2
            # days.
            formwork = ifcopenshell.api.run("sequence.add_task", model,
                parent_task=construction, name="Formwork", identification="C.1")
            time = ifcopenshell.api.run("sequence.add_task_time", model, task=formwork)
            ifcopenshell.api.run("sequence.edit_task_time", model,
                task_time=time, attributes={"ScheduleStart": "2000-01-01", "ScheduleDuration": "P2D"})

            # Now let's do the reinforcement. It'll take us another 2 days.
            reinforcement = ifcopenshell.api.run("sequence.add_task", model,
                parent_task=construction, name="Reinforcement", identification="C.2")
            time = ifcopenshell.api.run("sequence.add_task_time", model, task=reinforcement)
            ifcopenshell.api.run("sequence.edit_task_time", model,
                task_time=time, attributes={"ScheduleStart": "2000-01-01", "ScheduleDuration": "P2D"})

            # Now let's say the formwork must finish before the reinforcement
            # can start. This is a typical finish to start relationship (FS).
            sequence = ifcopenshell.api.run("sequence.assign_sequence", model,
                relating_process=formwork, related_process=reinforcement)

            # Now typically there would be no lag time between formwork and
            # reinforcement, but let's pretend that we had to allow 1 day gap
            # for whatever reason.
            lag = ifcopenshell.api.run("sequence.assign_lag_time", model, rel_sequence=sequence, lag_value="P1D")

            # Or, let's make it 2 days instead.
            ifcopenshell.api.run("sequence.edit_lag_time", model, lag_time=lag, attributes={"LagValue": "P2D"})
        """
        self.file = file
        self.settings = {"lag_time": lag_time, "attributes": attributes or {}}

    def execute(self):
        for name, value in self.settings["attributes"].items():
            if name == "LagValue" and value is not None:
                if isinstance(value, float):
                    value = self.file.createIfcRatioMeasure(value)
                else:
                    value = self.file.createIfcDuration(
                        ifcopenshell.util.date.datetime2ifc(value, "IfcDuration")
                    )
            setattr(self.settings["lag_time"], name, value)
        for rel in [
            r
            for r in self.file.get_inverse(self.settings["lag_time"])
            if r.is_a("IfcRelSequence")
        ]:
            ifcopenshell.api.run(
                "sequence.cascade_schedule", self.file, task=rel.RelatedProcess
            )
