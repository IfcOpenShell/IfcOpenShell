class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {
            "condition": None,
            "attributes": {}
        }
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        for name, data in self.settings["attributes"].items():
            if data["type"] == "string" or data["type"] == "null":
                value = data["value"]
            elif data["type"] == "IfcBoolean":
                value = self.file.createIfcBoolean(data["value"])
            else:
                value = self.file.create_entity(data["type"], data["value"])
            setattr(self.settings["condition"], name, value)
