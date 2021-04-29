class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"parent": None, "recurrence_type": "WEEKLY"}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        recurrence = self.file.createIfcRecurrencePattern(self.settings["recurrence_type"])

        if self.settings["parent"].is_a("IfcWorkTime"):
            if (
                self.settings["parent"].RecurrencePattern
                and len(self.file.get_inverse(self.settings["parent"].RecurrencePattern)) == 1
            ):
                self.file.remove(self.settings["parent"].RecurrencePattern)
            self.settings["parent"].RecurrencePattern = recurrence
        elif self.settings["parent"].is_a("IfcTaskTimeRecurring"):
            if len(self.file.get_inverse(self.settings["parent"].Recurrence)) == 1:
                self.file.remove(self.settings["parent"].Recurrence)
            self.settings["parent"].Recurrence = recurrence
