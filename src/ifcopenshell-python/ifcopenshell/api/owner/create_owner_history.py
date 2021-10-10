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
        user = ifcopenshell.api.owner.settings.get_user(self.file)
        application = ifcopenshell.api.owner.settings.get_application(self.file)
        if self.file.schema != "IFC2X3":
            if not user or not application:
                return
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
