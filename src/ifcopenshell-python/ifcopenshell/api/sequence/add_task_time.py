import ifcopenshell.util.date


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {
            "task": None,
        }
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        task_time = self.file.create_entity("IfcTaskTime")
        self.settings["task"].TaskTime = task_time
        return task_time
