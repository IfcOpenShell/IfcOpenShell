import ifcopenshell.api


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {
            "parent_resource": None,
            "ifc_class": "IfcCrewResource",
            "name": None,
            "predefined_type": "NOTDEFINED",
        }
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        resource = ifcopenshell.api.run(
            "root.create_entity",
            self.file,
            ifc_class=self.settings["ifc_class"],
            predefined_type=self.settings["predefined_type"],
            name=self.settings["name"],
        )
        # TODO: this is an ambiguity by buildingSMART: Can we nest an IfcCrewResource under an IfcCrewResource ?
        # https://forums.buildingsmart.org/t/what-are-allowed-to-be-root-level-construction-resources/3550
        if self.settings["parent_resource"]:
            ifcopenshell.api.run(
                "nest.assign_object", self.file, related_object=resource, relating_object=self.settings["parent_resource"]
            )
        else:
            context = self.file.by_type("IfcContext")[0]
            ifcopenshell.api.run(
                "project.assign_declaration", self.file, definition=resource, relating_context=context
            )
        return resource
