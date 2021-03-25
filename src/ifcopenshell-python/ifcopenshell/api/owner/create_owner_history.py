import time
import ifcopenshell
import ifcopenshell.api.owner.settings


class Usecase:
    def __init__(self, file, settings={}):
        self.file = file
        self.settings = ifcopenshell.api.owner.settings.settings
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        if self.file.schema != "IFC2X3":
            if not self.settings["person"] or not self.settings["organisation"]:
                return
        user = self.get_user()
        application = self.get_application()
        return self.file.create_entity(
            "IfcOwnerHistory",
            **{
                "OwningUser": user,
                "OwningApplication": application,
                "State": "READWRITE",
                "ChangeAction": self.settings["ChangeAction"] or "ADDED",
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

    def get_application(self):
        for element in self.file.by_type("IfcApplication"):
            if element.ApplicationIdentifier == self.settings["ApplicationIdentifier"]:
                return element
        return self.file.create_entity(
            "IfcApplication",
            **{
                "ApplicationDeveloper": self.get_application_organisation(),
                "Version": self.settings["Version"],
                "ApplicationFullName": self.settings["ApplicationFullName"],
                "ApplicationIdentifier": self.settings["ApplicationIdentifier"],
            },
        )

    def get_application_organisation(self):
        return self.file.create_entity(
            "IfcOrganization",
            **{
                "Name": "IfcOpenShell",
                "Description": "IfcOpenShell is an open source (LGPL) software library that helps users and software developers to work with the IFC file format.",
                "Roles": [
                    self.file.create_entity("IfcActorRole", **{"Role": "USERDEFINED", "UserDefinedRole": "CONTRIBUTOR"})
                ],
                "Addresses": [
                    self.file.create_entity(
                        "IfcTelecomAddress",
                        **{
                            "Purpose": "USERDEFINED",
                            "UserDefinedPurpose": "WEBPAGE",
                            "Description": "The main webpage of the software collection.",
                            "WWWHomePageURL": "https://ifcopenshell.org",
                        },
                    ),
                    self.file.create_entity(
                        "IfcTelecomAddress",
                        **{
                            "Purpose": "USERDEFINED",
                            "UserDefinedPurpose": "WEBPAGE",
                            "Description": "The BlenderBIM Add-on webpage of the software collection.",
                            "WWWHomePageURL": "https://blenderbim.org",
                        },
                    ),
                    self.file.create_entity(
                        "IfcTelecomAddress",
                        **{
                            "Purpose": "USERDEFINED",
                            "UserDefinedPurpose": "REPOSITORY",
                            "Description": "The source code repository of the software collection.",
                            "WWWHomePageURL": "https://github.com/IfcOpenShell/IfcOpenShell.git",
                        },
                    ),
                ],
            },
        )
