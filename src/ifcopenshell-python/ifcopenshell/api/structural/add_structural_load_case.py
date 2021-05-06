import ifcopenshell.api


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {
            "name": "Unnamed",
            "predefined_type": "LOAD_CASE",
            "action_type": "NOTDEFINED",
            "action_source": "NOTDEFINED",
        }
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        load_case = ifcopenshell.api.run(
            "root.create_entity",
            self.file,
            ifc_class="IfcStructuralLoadCase",
            predefined_type=self.settings["predefined_type"],
            name=self.settings["name"],
        )
        load_case.ActionType = self.settings["action_type"]
        load_case.ActionSource = self.settings["action_source"]
        return load_case
