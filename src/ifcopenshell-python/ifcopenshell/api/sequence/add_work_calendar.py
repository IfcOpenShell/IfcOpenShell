import ifcopenshell.api


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"name": "Unnamed", "predefined_type": "NOTDEFINED", "working_times": [], "exception_times": []}
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
        context = self.file.by_type("IfcContext")[0]
        ifcopenshell.api.run(
            "project.assign_declaration", self.file, definition=work_calendar, relating_context=context
        )
        return work_calendar
