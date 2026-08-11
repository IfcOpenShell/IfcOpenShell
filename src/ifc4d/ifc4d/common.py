from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any, TypedDict, Union

import ifcopenshell
import ifcopenshell.api.control
import ifcopenshell.api.owner
import ifcopenshell.api.pset
import ifcopenshell.api.resource
import ifcopenshell.api.root
import ifcopenshell.api.sequence
import ifcopenshell.guid
import ifcopenshell.util.date
from typing_extensions import NotRequired


class WorkSlot(TypedDict):
    DayOfWeek: str
    WorkTimes: list[dict[str, Any]]
    ifc: Union[ifcopenshell.entity_instance, None]


class ExceptionDict(TypedDict):
    WorkTime: list[int]
    FullDay: list[int]


ExceptionsDict = dict[int, dict[int, ExceptionDict]]


class Calendar(TypedDict):
    Name: str
    Type: str
    HoursPerDay: int
    StandardWorkWeek: list[WorkSlot]
    HolidayOrExceptions: NotRequired[ExceptionsDict]
    ifc: NotRequired[ifcopenshell.entity_instance]


class Activity(TypedDict):
    Name: str
    Identification: int
    StartDate: datetime
    FinishDate: datetime
    PlannedDuration: float
    Status: str
    CalendarObjectId: str
    Type: NotRequired[str]
    # {Title: (ifc_type, value)} — the IFC type comes from the P6 UDFType
    # declaration, not from the value, so it is resolved at parse time.
    UDFs: NotRequired[dict[str, tuple[str, str]]]
    Codes: NotRequired[dict[str, str]]
    ActualStartDate: NotRequired[Union[datetime, None]]
    ActualFinishDate: NotRequired[Union[datetime, None]]
    EarlyStartDate: NotRequired[Union[datetime, None]]
    EarlyFinishDate: NotRequired[Union[datetime, None]]
    LateStartDate: NotRequired[Union[datetime, None]]
    LateFinishDate: NotRequired[Union[datetime, None]]
    TotalFloat: NotRequired[Union[float, None]]
    FreeFloat: NotRequired[Union[float, None]]
    PercentComplete: NotRequired[Union[float, None]]
    ifc: Union[ifcopenshell.entity_instance, None]


class WBSEntry(TypedDict):
    """Work Breakdown Strcture Entry"""

    Name: str
    Code: int
    ParentObjectId: Union[int, None]
    ifc: Union[ifcopenshell.entity_instance, None]
    rel: Union[ifcopenshell.entity_instance, None]
    activities: list[int]


class ScheduleIfcGenerator:
    file: Union[ifcopenshell.file, None]
    calendars: dict[int, Calendar]

    # The property sets an activity's user-defined fields and codes land in.
    # Named for P6 because that is where the shape came from; an importer for
    # another tool overrides them rather than filing its own fields under a
    # name that names the wrong tool.
    udf_pset_name = "P6_UDF"
    code_pset_name = "P6_ActivityCodes"

    def __init__(self, file: Union[ifcopenshell.file, None], output, settings):
        self.file = file
        self.work_plan = settings["work_plan"]
        self.project = settings["project"]
        self.calendars = settings["calendars"]
        self.wbs = settings["wbs"]
        self.root_activites = settings["root_activities"]
        self.activities = settings["activities"]
        self.relationships = settings["relationships"]
        self.resources = settings["resources"]
        self.output = output
        self.day_map = {
            "Monday": 1,
            "Tuesday": 2,
            "Wednesday": 3,
            "Thursday": 4,
            "Friday": 5,
            "Saturday": 6,
            "Sunday": 7,
        }

    def create_ifc(self) -> None:
        if not self.file:
            self.create_boilerplate_ifc()
        if not self.work_plan:
            self.work_plan = ifcopenshell.api.sequence.add_work_plan(self.file)
        work_schedule = self.create_work_schedule()
        self.create_calendars()
        self.create_tasks(work_schedule)
        self.create_rel_sequences()
        self.create_resources()
        if self.output:
            self.file.write(self.output)

    def create_work_schedule(self) -> ifcopenshell.entity_instance:
        return ifcopenshell.api.sequence.add_work_schedule(
            self.file, name=self.project["Name"], work_plan=self.work_plan
        )

    def create_calendars(self) -> None:
        for calendar_id, calendar in self.calendars.items():
            calendar["ifc"] = ifcopenshell.api.sequence.add_work_calendar(self.file, name=calendar["Name"])
            calendar["ifc"].Identification = str(calendar_id)
            self.process_working_week(calendar["StandardWorkWeek"], calendar["ifc"])
            self.process_exceptions(calendar.get("HolidayOrExceptions"), calendar["ifc"])

    def process_working_week(self, week: list[WorkSlot], calendar: ifcopenshell.entity_instance) -> None:
        for day in week:
            if day["ifc"] or not day.get("WorkTimes"):
                continue

            day["ifc"] = ifcopenshell.api.sequence.add_work_time(
                self.file, work_calendar=calendar, time_type="WorkingTimes"
            )
            weekday_component = [self.day_map[day["DayOfWeek"]]]
            for day2 in week:
                if day["DayOfWeek"] == day2["DayOfWeek"]:
                    continue
                if day["WorkTimes"] == day2["WorkTimes"]:
                    weekday_component.append(self.day_map[day2["DayOfWeek"]])
                    # Don't process the next day, as we can group it
                    day2["ifc"] = day["ifc"]

            work_time_name = "Weekdays: {}".format(", ".join([str(c) for c in sorted(weekday_component)]))
            ifcopenshell.api.sequence.edit_work_time(
                self.file,
                work_time=day["ifc"],
                attributes={"Name": work_time_name},
            )

            recurrence = ifcopenshell.api.sequence.assign_recurrence_pattern(
                self.file, parent=day["ifc"], recurrence_type="WEEKLY"
            )
            ifcopenshell.api.sequence.edit_recurrence_pattern(
                self.file,
                recurrence_pattern=recurrence,
                attributes={"WeekdayComponent": weekday_component},
            )
            for work_time in day["WorkTimes"]:
                ifcopenshell.api.sequence.add_time_period(
                    self.file,
                    recurrence_pattern=recurrence,
                    start_time=work_time["Start"],
                    end_time=work_time["Finish"],
                )

    def process_exceptions(
        self, exceptions: Union[ExceptionsDict, None], calendar: ifcopenshell.entity_instance
    ) -> None:
        if exceptions:
            for year, year_data in exceptions.items():
                for month, month_data in year_data.items():
                    if month_data["FullDay"]:
                        self.process_full_day_exceptions(year, month, month_data, calendar)
                    if month_data["WorkTime"]:
                        self.process_work_time_exceptions(year, month, month_data, calendar)

    def process_full_day_exceptions(
        self, year: int, month: int, month_data: dict[str, Any], calendar: ifcopenshell.entity_instance
    ):
        work_time = ifcopenshell.api.sequence.add_work_time(
            self.file, work_calendar=calendar, time_type="ExceptionTimes"
        )
        ifcopenshell.api.sequence.edit_work_time(
            self.file,
            work_time=work_time,
            attributes={
                "Name": f"{year}-{month}",
                "Start": date(year, 1, 1),
                "Finish": date(year, 12, 31),
            },
        )
        recurrence = ifcopenshell.api.sequence.assign_recurrence_pattern(
            self.file,
            parent=work_time,
            recurrence_type="YEARLY_BY_DAY_OF_MONTH",
        )
        ifcopenshell.api.sequence.edit_recurrence_pattern(
            self.file,
            recurrence_pattern=recurrence,
            attributes={"DayComponent": month_data["FullDay"], "MonthComponent": [month]},
        )

    def process_work_time_exceptions(
        self, year: int, month: int, month_data: dict[str, Any], calendar: ifcopenshell.entity_instance
    ) -> None:
        for day in month_data["WorkTime"]:
            if day["ifc"]:
                continue

            day["ifc"] = ifcopenshell.api.sequence.add_work_time(
                self.file, work_calendar=calendar, time_type="ExceptionTimes"
            )

            day_component = [day["Day"]]
            for day2 in month_data["WorkTime"]:
                if day["Day"] == day2["Day"]:
                    continue
                if day["WorkTimes"] == day2["WorkTimes"]:
                    day_component.append(day2["Day"])
                    # Don't process the next day, as we can group it
                    day2["ifc"] = day["ifc"]

            ifcopenshell.api.sequence.edit_work_time(
                self.file,
                work_time=day["ifc"],
                attributes={
                    "Name": "{}-{}-{}".format(year, month, ", ".join([str(d) for d in day_component])),
                    "Start": date(year, 1, 1),
                    "Finish": date(year, 12, 31),
                },
            )
            recurrence = ifcopenshell.api.sequence.assign_recurrence_pattern(
                self.file,
                parent=day["ifc"],
                recurrence_type="YEARLY_BY_DAY_OF_MONTH",
            )
            ifcopenshell.api.sequence.edit_recurrence_pattern(
                self.file,
                recurrence_pattern=recurrence,
                attributes={"DayComponent": day_component, "MonthComponent": [month]},
            )
            for work_time in day["WorkTimes"]:
                ifcopenshell.api.sequence.add_time_period(
                    self.file,
                    recurrence_pattern=recurrence,
                    start_time=work_time["Start"],
                    end_time=work_time["Finish"],
                )

    def create_tasks(self, work_schedule: ifcopenshell.entity_instance) -> None:
        # Depth first, siblings in P6's SequenceNumber order rather than the
        # order the export happens to list them in. Parents still come before
        # children, which create_task_from_wbs depends on to find its parent's
        # IFC task.
        siblings: dict[Any, list[tuple[float, Any]]] = {}
        for wbs_id, wbs in self.wbs.items():
            parent = wbs["ParentObjectId"] if self.wbs.get(wbs["ParentObjectId"]) else None
            siblings.setdefault(parent, []).append((wbs.get("SequenceNumber") or 0, wbs_id))

        def emit(parent) -> None:
            for _, wbs_id in sorted(siblings.get(parent, []), key=lambda pair: pair[0]):
                self.create_task_from_wbs(self.wbs[wbs_id], work_schedule)
                emit(wbs_id)

        emit(None)
        for activity_id in self.root_activites:
            self.create_task_from_activity(self.activities[activity_id], None, work_schedule)

    def create_task_from_wbs(self, wbs: WBSEntry, work_schedule: ifcopenshell.entity_instance) -> None:
        if not self.wbs.get(wbs["ParentObjectId"]):
            wbs["ParentObjectId"] = None
        wbs["ifc"] = ifcopenshell.api.sequence.add_task(
            self.file,
            work_schedule=None if wbs["ParentObjectId"] else work_schedule,
            parent_task=self.wbs[wbs["ParentObjectId"]]["ifc"] if wbs["ParentObjectId"] else None,
        )
        identification = wbs["Code"]
        if wbs["ParentObjectId"]:
            if self.wbs[wbs["ParentObjectId"]]["ifc"]:
                identification = str(self.wbs[wbs["ParentObjectId"]]["ifc"].Identification) + "." + str(wbs["Code"])
        ifcopenshell.api.sequence.edit_task(
            self.file,
            task=wbs["ifc"],
            attributes={"Name": wbs["Name"], "Identification": str(identification)},
        )
        for activity_id in wbs["activities"]:
            self.create_task_from_activity(self.activities[activity_id], wbs, None)

    def create_task_from_activity(
        self,
        activity: Activity,
        wbs: Union[WBSEntry, None],
        work_schedule: Union[ifcopenshell.entity_instance, None],
    ) -> None:
        assert self.file
        activity["ifc"] = ifcopenshell.api.sequence.add_task(
            self.file,
            work_schedule=None if wbs else work_schedule,
            parent_task=wbs["ifc"] if wbs else None,
        )
        ifcopenshell.api.sequence.edit_task(
            self.file,
            task=activity["ifc"],
            attributes={
                "Name": activity["Name"],
                "Identification": str(activity["Identification"]),
                "Status": activity["Status"],
                # A zero-length activity is a milestone, which is all P6 gives
                # us to go on. A source that says so outright — Microsoft
                # Project has a Milestone flag — is believed instead, because a
                # tool can mark a task a milestone without zeroing its duration.
                "IsMilestone": activity.get("IsMilestone", activity["StartDate"] == activity["FinishDate"]),
                # A P6 Level of Effort activity has no duration of its own: it
                # stretches to span whatever it hangs off, and its dates are
                # derived from its relationships rather than planned. IFC has no
                # such concept, and ATTENDANCE is the closest thing in
                # IfcTaskTypeEnum — support work that runs alongside the tasks
                # it serves rather than driving them. The derivation itself is
                # not lost: the SS/FS and FF predecessors P6 computes the span
                # from are ordinary relationships, and they are written out as
                # IfcRelSequence like any other, so a scheduler can recompute
                # the span the same way P6 did.
                "PredefinedType": ("ATTENDANCE" if activity.get("Type") == "Level of Effort" else "CONSTRUCTION"),
            },
        )
        self.create_udf_pset(activity)
        self.create_code_pset(activity)
        task_time = ifcopenshell.api.sequence.add_task_time(self.file, task=activity["ifc"])
        calendar = self.calendars[activity["CalendarObjectId"]]
        # Seems intermittently crashy - can we investigate for larger files?
        ifcopenshell.api.control.assign_control(
            self.file,
            relating_control=calendar["ifc"],
            related_objects=[activity["ifc"]],
        )
        self.transcribe_task_time(task_time, activity, calendar)

    def transcribe_task_time(
        self,
        task_time: ifcopenshell.entity_instance,
        activity: Activity,
        calendar: Calendar,
    ) -> None:
        """Write P6's times onto the IfcTaskTime verbatim.

        Intentionally do not recalculate durations or finish times. Match P6
        exactly. Users may recalculate later if needed.
        """
        date = ifcopenshell.util.date.datetime2ifc
        hours_per_day = float(calendar["HoursPerDay"] or 8)

        task_time.ScheduleStart = date(activity["StartDate"], "IfcDateTime")
        task_time.ScheduleFinish = date(activity["FinishDate"], "IfcDateTime")
        task_time.DurationType = "WORKTIME"
        planned = activity["PlannedDuration"]
        if planned is not None and (float(planned) or activity["StartDate"] == activity["FinishDate"]):
            task_time.ScheduleDuration = date(timedelta(days=float(planned) / hours_per_day), "IfcDuration")

        for attribute, value in (
            ("ActualStart", activity.get("ActualStartDate")),
            ("ActualFinish", activity.get("ActualFinishDate")),
            ("EarlyStart", activity.get("EarlyStartDate")),
            ("EarlyFinish", activity.get("EarlyFinishDate")),
            ("LateStart", activity.get("LateStartDate")),
            ("LateFinish", activity.get("LateFinishDate")),
        ):
            if value is not None:
                setattr(task_time, attribute, date(value, "IfcDateTime"))

        # P6 states float in hours against the activity's own calendar, so the
        # calendar is consulted for nothing more than that conversion.
        for attribute, hours in (
            ("TotalFloat", activity.get("TotalFloat")),
            ("FreeFloat", activity.get("FreeFloat")),
        ):
            if hours is not None:
                setattr(task_time, attribute, date(timedelta(days=hours / hours_per_day), "IfcDuration"))
        if activity.get("TotalFloat") is not None:
            task_time.IsCritical = activity["TotalFloat"] <= 0

        # Completion is an IfcPositiveRatioMeasure, so zero is not merely
        # uninteresting, it is invalid. An activity that has not started says
        # nothing rather than saying "0% done".
        if activity.get("PercentComplete"):
            task_time.Completion = activity["PercentComplete"]

    def create_udf_pset(self, activity: Activity) -> None:
        """This activity's P6 user-defined fields, as a P6_UDF property set."""
        assert self.file
        udfs = activity.get("UDFs")
        if not udfs:
            return
        pset = ifcopenshell.api.pset.add_pset(self.file, product=activity["ifc"], name=self.udf_pset_name)
        ifcopenshell.api.pset.edit_pset(
            self.file,
            pset=pset,
            properties={title: self.file.create_entity(ifc_type, value) for title, (ifc_type, value) in udfs.items()},
        )

    def create_code_pset(self, activity: Activity) -> None:
        """This activity's P6 activity codes, as a P6_ActivityCodes set."""
        assert self.file
        codes = activity.get("Codes")
        if not codes:
            return
        pset = ifcopenshell.api.pset.add_pset(self.file, product=activity["ifc"], name=self.code_pset_name)
        ifcopenshell.api.pset.edit_pset(
            self.file,
            pset=pset,
            properties={name: self.file.create_entity("IfcLabel", value) for name, (value, _) in codes.items()},
        )
        # A P6 code carries a short value and a readable description — "SO" and
        # "Start on Site Milestone". Both matter to a reader, and IfcProperty
        # already has the second slot, so the description goes on Description
        # rather than being mangled into the value or dropped.
        for prop in pset.HasProperties:
            description = codes.get(prop.Name, (None, ""))[1]
            if description:
                prop.Description = description

    def create_rel_sequences(self) -> None:
        self.sequence_type_map = {
            "Start to Start": "START_START",
            "Start to Finish": "START_FINISH",
            "Finish to Start": "FINISH_START",
            "Finish to Finish": "FINISH_FINISH",
        }
        for relationship in self.relationships.values():
            predecessor = self.activities[relationship["PredecessorActivity"]]["ifc"]
            successor = self.activities[relationship["SuccessorActivity"]]["ifc"]

            rel_sequence = next(
                (
                    rel
                    for rel in successor.IsSuccessorFrom or []
                    if rel.RelatingProcess == predecessor and rel.SequenceType == relationship["Type"]
                ),
                None,
            )
            if rel_sequence is None:
                attributes = {
                    "GlobalId": ifcopenshell.guid.new(),
                    "RelatingProcess": predecessor,
                    "RelatedProcess": successor,
                    "SequenceType": relationship["Type"],
                }
                owner_history = ifcopenshell.api.owner.create_owner_history(self.file)
                if owner_history is not None:
                    attributes["OwnerHistory"] = owner_history
                rel_sequence = self.file.create_entity("IfcRelSequence", **attributes)
            lag = float(relationship["Lag"])
            if lag:
                calendar = self.calendars[self.activities[relationship["PredecessorActivity"]]["CalendarObjectId"]]
                ifcopenshell.api.sequence.assign_lag_time(
                    self.file,
                    rel_sequence=rel_sequence,
                    lag_value=timedelta(days=lag / float(calendar["HoursPerDay"] or 8)),
                    duration_type="WORKTIME",
                )

    def create_resources(self) -> None:
        if self.resources:
            for id, resource in self.resources.items():

                parent = self.resources.get(resource.get("ParentObjectId"))
                if parent:
                    if not parent.get("ifc"):
                        parent["ifc"] = ifcopenshell.api.resource.add_resource(
                            self.file,
                            ifc_class="IfcCrewResource",
                            name=parent["Name"],
                        )
                if parent:
                    resource["ifc"] = ifcopenshell.api.resource.add_resource(
                        self.file,
                        parent_resource=parent["ifc"] if parent else None,
                        ifc_class="IfcCrewResource",
                        name=resource["Name"],
                    )
                else:
                    resource["ifc"] = ifcopenshell.api.resource.add_resource(
                        self.file, ifc_class="IfcCrewResource", name=resource["Name"]
                    )

    def create_boilerplate_ifc(self) -> None:
        self.file = ifcopenshell.file(schema="IFC4")
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        self.work_plan = self.file.create_entity("IfcWorkPlan")
