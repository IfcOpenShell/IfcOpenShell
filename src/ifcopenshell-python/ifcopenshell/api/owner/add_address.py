class Usecase:
    def __init__(self, file, settings=None):
        self.file = file
        self.settings = {"assigned_object": None, "ifc_class": "IfcPostalAddress"}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        addresses = list(self.settings["assigned_object"].Addresses) if self.settings["assigned_object"].Addresses else []
        addresses.append(self.file.create_entity(self.settings["ifc_class"], "OFFICE"))
        self.settings["assigned_object"].Addresses = addresses
