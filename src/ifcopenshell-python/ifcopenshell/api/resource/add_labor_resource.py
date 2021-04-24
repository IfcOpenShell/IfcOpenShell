import ifcopenshell.api
import ifcopenshell


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {
            "parent_resource": None,
        }
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        labor_resource = ifcopenshell.api.run(
            "root.create_entity",
            self.file,
            ifc_class="IfcLaborResource",
            name=None,
            predefined_type="NOTDEFINED",
            identification="none",
        )
        if self.settings["parent_resource"]:
            ifcopenshell.api.run(
                "nest.assign_object", self.file, related_object=labor_resource, relating_object=self.settings["parent_resource"]
            )
        return labor_resource
