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
            action_type=self.settings["action_type"],
            action_source=self.settings["action_source"],
            name=self.settings["name"],
        )
        return load_case
