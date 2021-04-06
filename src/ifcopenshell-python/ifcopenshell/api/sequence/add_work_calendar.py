import ifcopenshell.api
import ifcopenshell.util.date
from datetime import datetime, timedelta


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {
            "name": "Unnamed", 
            "predefined_type": "NOTDEFINED", 
            "working_times":[], 
            "exception_times":[]
        }
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        work_calendar = ifcopenshell.api.run(
            "root.create_entity",
            self.file,
            ifc_class="IfcWorkCalendar",
            predefined_type=self.settings["predefined_type"],
            name=self.settings["name"],
        )
        working_time = self.file.create_entity("IfcWorkTime", **{"Name":"DefaultWorkingTime"})
        self.settings["working_times"].append(working_time)
        work_calendar.WorkingTimes = self.settings["working_times"]

        exception_time = self.file.create_entity("IfcWorkTime", **{"Name":"DefaultExceptionTime"})
        self.settings["exception_times"].append(exception_time)
        work_calendar.ExceptionTimes = self.settings["exception_times"]

        context = self.file.by_type("IfcContext")[0]
        if context.Declares:
            rel_declares = context.Declares[0]
            ifcopenshell.api.run("owner.update_owner_history", self.file, element=rel_declares)
        else:
            rel_declares = self.file.create_entity("IfcRelDeclares", **{
                "GlobalId": ifcopenshell.guid.new(),
                "OwnerHistory": ifcopenshell.api.run("owner.create_owner_history", self.file),
                "RelatingContext": context
            })
        related_definitions = list(rel_declares.RelatedDefinitions or [])
        related_definitions.append(work_calendar)
        rel_declares.RelatedDefinitions = related_definitions

        return work_calendar