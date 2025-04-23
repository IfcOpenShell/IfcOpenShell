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

import ifcopenshell.api.sequence


def unassign_lag_time(file: ifcopenshell.file, rel_sequence: ifcopenshell.entity_instance) -> None:
    """Removes any lag time in a sequence

    The schedule is cascaded afterwards.

    :param rel_sequence: The sequence to remove the lag time from.
    :return: None

    Example:

    .. code:: python

        # Let's imagine we are creating a construction schedule. All tasks
        # need to be part of a work schedule.
        schedule = ifcopenshell.api.sequence.add_work_schedule(model, name="Construction Schedule A")

        # Let's imagine a root construction task
        construction = ifcopenshell.api.sequence.add_task(model,
            work_schedule=schedule, name="Construction", identification="C")

        # Let's imagine we're building 2 zones, one after another.
        zone1 = ifcopenshell.api.sequence.add_task(model,
            parent_task=construction, name="Zone 1", identification="C.1")
        zone2 = ifcopenshell.api.sequence.add_task(model,
            parent_task=construction, name="Zone 2", identification="C.2")

        # Zone 1 finishes, then zone 2 starts.
        sequence = ifcopenshell.api.sequence.assign_sequence(model,
            relating_process=zone1, related_process=zone2)

        # What if you had to wait 1 week before you could start zone 2?
        ifcopenshell.api.sequence.assign_lag_time(model, rel_sequence=sequence, lag_value="P1W")

        # What if you didn't?
        ifcopenshell.api.sequence.unassign_lag_time(model, rel_sequence=sequence)
    """
    if file.get_total_inverses((current_lag_time := rel_sequence.TimeLag)) == 1:
        file.remove(current_lag_time)
    else:
        rel_sequence.TimeLag = None
    ifcopenshell.api.sequence.cascade_schedule(file, task=rel_sequence.RelatedProcess)
