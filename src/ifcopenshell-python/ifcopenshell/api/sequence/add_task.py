import ifcopenshell.api


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {
            "name": None,
            "predefined_type": "NOTDEFINED",
            "is_milestone": False,
            "identification": "none",
            "predecessor_to": None,
            "successor_from": None,
        }
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        task = ifcopenshell.api.run(
            "root.create_entity",
            self.file,
            ifc_class="IfcTask",
            predefined_type=self.settings["predefined_type"],
            name=self.settings["name"],
        )
        task.IsMilestone = self.settings["is_milestone"]
        return task
