import time
import ifcopenshell
import ifcopenshell.api


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        self.settings["person"] = ifcopenshell.api.owner.settings.get_person(self.file)
        self.settings["organisation"] = ifcopenshell.api.owner.settings.get_organisation(self.file)
        if not self.settings["element"].OwnerHistory:
            self.settings["element"].OwnerHistory = ifcopenshell.api.run(
                "owner.create_owner_history", self.file, **self.settings
            )
            return self.settings["element"].OwnerHistory
        if len(self.file.get_inverse(self.settings["element"].OwnerHistory)) > 1:
            old_history = self.settings["element"].OwnerHistory
            self.settings["element"].OwnerHistory = self.file.create_entity("IfcOwnerHistory")
            for i, attribute in enumerate(old_history):
                self.settings["element"].OwnerHistory[i] = attribute
        user = self.get_user()
        application = ifcopenshell.api.owner.settings.get_application(self.file)
        self.settings["element"].OwnerHistory.ChangeAction = "MODIFIED"
        self.settings["element"].OwnerHistory.LastModifiedDate = int(time.time())
        self.settings["element"].OwnerHistory.LastModifyingUser = user
        self.settings["element"].OwnerHistory.LastModifyingApplication = application
        return self.settings["element"].OwnerHistory

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
