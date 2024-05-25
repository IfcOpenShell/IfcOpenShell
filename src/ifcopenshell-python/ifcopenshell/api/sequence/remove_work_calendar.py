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
import ifcopenshell.api
import ifcopenshell.util.element


def remove_work_calendar(file: ifcopenshell.file, work_calendar: ifcopenshell.entity_instance) -> None:
    """Removes a work calendar

    All relationships are also removed, such as if a task is set to use that
    calendar.

    :param work_calendar: The IfcWorkCalendar to remove
    :type work_calendar: ifcopenshell.entity_instance
    :return: None
    :rtype: None

    Example:

    .. code:: python

        # Let's create a new calendar.
        calendar = ifcopenshell.api.run("sequence.add_work_calendar", model, name="5 Day Week")

        # And remove it immediately
        ifcopenshell.api.run("sequence.remove_work_calendar", model, work_calendar=calendar)
    """
    settings = {"work_calendar": work_calendar}

    # TODO: do a deep purge
    ifcopenshell.api.run(
        "project.unassign_declaration",
        file,
        definitions=[settings["work_calendar"]],
        relating_context=file.by_type("IfcContext")[0],
    )
    if settings["work_calendar"].Controls:
        for rel in settings["work_calendar"].Controls:
            for related_object in rel.RelatedObjects:
                ifcopenshell.api.run(
                    "control.unassign_control",
                    file,
                    relating_control=settings["work_calendar"],
                    related_object=related_object,
                )
    history = settings["work_calendar"].OwnerHistory
    file.remove(settings["work_calendar"])
    if history:
        ifcopenshell.util.element.remove_deep2(file, history)
