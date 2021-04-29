import ifcopenshell.api


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"work_time": None, "recurrence_type": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        recurrence_pattern = self.file.create_entity("IfcRecurrencePattern")
        recurrence_pattern.RecurrenceType = self.settings["recurrence_type"]
        self.settings["work_time"].RecurrencePattern = recurrence_pattern
        return recurrence_pattern
