import time
import ifcopenshell
import ifcopenshell.api
import ifcopenshell.util.element


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        if not hasattr(self.settings["element"], "OwnerHistory"):
            return
        user = ifcopenshell.api.owner.settings.get_user(self.file)
        application = ifcopenshell.api.owner.settings.get_application(self.file)
        if not user or not application:
            return
        if not self.settings["element"].OwnerHistory:
            self.settings["element"].OwnerHistory = ifcopenshell.api.run(
                "owner.create_owner_history", self.file, **self.settings
            )
            return self.settings["element"].OwnerHistory
        if len(self.file.get_inverse(self.settings["element"].OwnerHistory)) > 1:
            new = ifcopenshell.util.element.copy(self.file, self.settings["element"].OwnerHistory)
            self.settings["element"].OwnerHistory = new
        self.settings["element"].OwnerHistory.ChangeAction = "MODIFIED"
        self.settings["element"].OwnerHistory.LastModifiedDate = int(time.time())
        self.settings["element"].OwnerHistory.LastModifyingUser = user
        self.settings["element"].OwnerHistory.LastModifyingApplication = application
        return self.settings["element"].OwnerHistory
