import time
import ifcopenshell
import ifcopenshell.api.owner.settings


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        self.settings["person"] = ifcopenshell.api.owner.settings.get_person(self.file)
        self.settings["organisation"] = ifcopenshell.api.owner.settings.get_organisation(self.file)
        if self.file.schema != "IFC2X3":
            if not self.settings["person"] or not self.settings["organisation"]:
                return
        user = self.get_user()
        application = ifcopenshell.api.owner.settings.get_application(self.file)
        return self.file.create_entity(
            "IfcOwnerHistory",
            **{
                "OwningUser": user,
                "OwningApplication": application,
                "State": "READWRITE",
                "ChangeAction": "ADDED",
                "LastModifiedDate": int(time.time()),
                "LastModifyingUser": user,
                "LastModifyingApplication": application,
                "CreationDate": int(time.time()),
            },
        )

    def get_user(self):
        for element in self.file.by_type("IfcPersonAndOrganization"):
            if (
                element.ThePerson == self.settings["person"]
                and element.TheOrganization == self.settings["organisation"]
            ):
                return element
        return self.file.create_entity(
            "IfcPersonAndOrganization",
            **{"ThePerson": self.settings["person"], "TheOrganization": self.settings["organisation"]},
        )
