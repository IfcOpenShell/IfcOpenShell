import ifcopenshell


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"opening": None, "element": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        fills_voids = self.settings["element"].FillsVoids

        if fills_voids:
            if fills_voids[0].RelatingOpeningElement == self.settings["opening"]:
                return
            self.file.remove(fills_voids[0])

        self.file.create_entity(
            "IfcRelFillsElement",
            **{
                "GlobalId": ifcopenshell.guid.new(),
                "RelatingOpeningElement": self.settings["opening"],
                "RelatedBuildingElement": self.settings["element"],
            }
        )
