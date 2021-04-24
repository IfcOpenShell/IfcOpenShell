import ifcopenshell.api
import ifcopenshell.util.date
from datetime import datetime


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {
            "parent_resource": None,
            "name": "Unnamed",
            "predefined_type": "NOTDEFINED",
        }
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        subcontract_resource = ifcopenshell.api.run(
            "root.create_entity",
            self.file,
            ifc_class="IfcSubContractResource",
            predefined_type=self.settings["predefined_type"],
            name=self.settings["name"],
        )
        # TODO: this is an ambiguity by buildingSMART: Can we nest and IfcCrewResource under an ifcCrewResource ?
        # See https://forums.buildingsmart.org/t/is-the-ifcCrewResource-project-declaration-mutually-exclusive-to-aggregation-within-a-relating-ifcworkplan/3510
        if self.settings["parent_resource"]:
            ifcopenshell.api.run(
                "nest.assign_object", self.file, related_object=resource, relating_object=self.settings["parent_resource"]
            )
        else:
            context = self.file.by_type("IfcContext")[0]
            ifcopenshell.api.run(
                "project.assign_declaration", self.file, definition=subcontract_resource, relating_context=context
            )
        return subcontract_resource
