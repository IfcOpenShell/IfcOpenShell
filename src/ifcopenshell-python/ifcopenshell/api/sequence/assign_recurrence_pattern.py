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
    def __init__(self, file, parent=None, recurrence_type="WEEKLY"):
        """Define a time to recur at a particular interval

        There are two scenarios where you might want to define a recurring time
        pattern.

        You might want a task to be scheduled at a recurring interval,
        this is common for maintenance tasks which need to be performed monthly,
        every 6 months, every year, etc.

        Alternatively, you might be defining a work calendar, which defines
        working days or holidays. The working days might be every week from
        monday to friday ("every" week means it recurs every week), or the
        holidays might be the same every year.

        The types of recurrence are:

        - DAILY: every Nth (interval) day for up to X (Occurrences) occurrences.
            e.g. Every day, every 2 days, every day up to 5 times, etc
        - WEEKLY: every Nth (interval) MTWTFSS (WeekdayComponent) for up to X
            (Occurrences) occurrences. e.g. Every Monday, every weekday, every
            other saturday, etc
        - MONTHLY_BY_DAY_OF_MONTH: every Nth (DayComponent) of every Xth
            (Interval) Month up to Y (Occurrences) occurrences. e.g. Every 15th of
            the Month.
        - MONTHLY_BY_POSITION: Every Nth (Position) MTWTFSS (WeekdayComponent)
            of every Xth (Interval) Month up to Y (Occurrences) occurrences. e.g.
            Every second Tuesday of the Month.
        - YEARLY_BY_DAY_OF_MONTH: every Nth (DayComponent) of every JFMAMJJASOND
            (MonthComponent) month of every Yth (Interval) Year up to Z
            (Occurrences) occurrences. e.g. every 25th of December.
        - YEARLY_BY_POSITION: every Nth (Position) MTWTFSS (WeekdayComponent) of
            every JFMAMJJASOND (MonthComponent) month of every Yth (Interval)
            Year up to Z (Occurrences) occurrences. e.g. every third Wednesday
            of January.

        These recurrence patterns are fairly standard in all calendar and
        scheduling applications.

        :param parent: Either an IfcTaskTimeRecurring if you are defining a
            recurring schedule for a task, or IfcWorkTime if you are defining a
            recurring pattern for a workdays or holidays in a calendar.
        :type parent: ifcopenshell.entity_instance.entity_instance
        :param recurrence_type: One of the types of recurrences.
        :type recurrence_type: str
        :return: The newly created IfcRecurrencePattern
        :rtype: ifcopenshell.entity_instance.entity_instance

        Example:

        .. code:: python

            # Let's create a new calendar.
            calendar = ifcopenshell.api.run("sequence.add_work_calendar", model)

            # Let's start defining the times that we work during the week.
            work_time = ifcopenshell.api.run("sequence.add_work_time", model,
                work_calendar=calendar, time_type="WorkingTimes")

            # We create a weekly recurrence
            pattern = ifcopenshell.api.run("sequence.assign_recurrence_pattern", model,
                parent=work_time, recurrence_type="WEEKLY")

            # State that we work from weekdays 1 to 5 (i.e. Monday to Friday)
            ifcopenshell.api.run("sequence.edit_recurrence_pattern", model,
                recurrence_pattern=pattern, attributes={"WeekdayComponent": [1, 2, 3, 4, 5]})

            # Let's imagine we are creating a maintenance schedule.
            schedule = ifcopenshell.api.run("sequence.add_work_schedule", model, name="Equipment Maintenance")

            # Now let's imagine we have a task to maintain the chillers
            task = ifcopenshell.api.run("sequence.add_task", model,
                work_schedule=schedule, name="Chiller maintenance")

            # Because it is a maintenance task, we must schedule a recurring time
            time = ifcopenshell.api.run("sequence.add_task_time", model, task=task, is_recurring=True)

            # We create a monthly recurrence
            pattern = ifcopenshell.api.run("sequence.assign_recurrence_pattern", model,
                parent=work_time, recurrence_type="MONTHLY_BY_DAY_OF_MONTH")

            # Specifically, the maintenance task must occur every 6 months
            ifcopenshell.api.run("sequence.edit_recurrence_pattern", model,
                recurrence_pattern=pattern, attributes={"DayComponent": [1], "Interval": 6})
        """
        self.file = file
        self.settings = {"parent": parent, "recurrence_type": recurrence_type}

    def execute(self):
        recurrence = self.file.createIfcRecurrencePattern(
            self.settings["recurrence_type"]
        )

        if self.settings["parent"].is_a("IfcWorkTime"):
            if (
                self.settings["parent"].RecurrencePattern
                and len(
                    self.file.get_inverse(self.settings["parent"].RecurrencePattern)
                )
                == 1
            ):
                self.file.remove(self.settings["parent"].RecurrencePattern)
            self.settings["parent"].RecurrencePattern = recurrence
        elif self.settings["parent"].is_a("IfcTaskTimeRecurring"):
            if len(self.file.get_inverse(self.settings["parent"].Recurrence)) == 1:
                self.file.remove(self.settings["parent"].Recurrence)
            self.settings["parent"].Recurrence = recurrence
        return recurrence
