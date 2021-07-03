import ifcopenshell.api


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {
            "application_developer": None,
            "version": "0.6.0",
            "application_full_name": "IfcOpenShell",
            "application_identifier": "IfcOpenShell",
        }
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        if not self.settings["application_developer"]:
            self.settings["application_developer"] = self.create_application_organisation()
        return self.file.create_entity(
            "IfcApplication",
            **{
                "ApplicationDeveloper": self.settings["application_developer"],
                "Version": self.settings["version"],
                "ApplicationFullName": self.settings["application_full_name"],
                "ApplicationIdentifier": self.settings["application_identifier"],
            },
        )

    def create_application_organisation(self):
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
