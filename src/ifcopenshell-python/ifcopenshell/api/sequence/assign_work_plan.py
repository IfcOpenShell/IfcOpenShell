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
import ifcopenshell.api.project
import ifcopenshell.api.aggregate
from typing import Union


def assign_work_plan(
    file: ifcopenshell.file, work_schedule: ifcopenshell.entity_instance, work_plan: ifcopenshell.entity_instance
) -> Union[ifcopenshell.entity_instance, None]:
    """Assigns a work schedule to a work plan

    Typically, work schedules would be assigned to a work plan at creation.
    However you may also delay this and do it manually afterwards.

    :param work_schedule: The IfcWorkSchedule that will be assigned to the
        work plan.
    :param work_plan: The IfcWorkPlan for the schedule to be assigned to.
    :return: The IfcRelAggregates relationship

    Example:

    .. code:: python

        # This will hold all our construction schedules
        work_plan = ifcopenshell.api.sequence.add_work_plan(model, name="Construction")

        # Alternatively, if you create a schedule without a work plan ...
        schedule = ifcopenshell.api.sequence.add_work_schedule(model, name="Construction Schedule A")

        # ... you can assign the work plan afterwards.
        ifcopenshell.api.sequence.assign_work_plan(work_schedule=schedule, work_plan=work_plan)
    """
    # TODO: this is an ambiguity by buildingSMART
    # See https://forums.buildingsmart.org/t/is-the-ifcworkschedule-project-declaration-mutually-exclusive-to-aggregation-within-a-relating-ifcworkplan/3510
    ifcopenshell.api.project.unassign_declaration(
        file,
        definitions=[work_schedule],
        relating_context=file.by_type("IfcContext")[0],
    )
    rel_aggregates = ifcopenshell.api.aggregate.assign_object(
        file,
        products=[work_schedule],
        relating_object=work_plan,
    )
    return rel_aggregates
