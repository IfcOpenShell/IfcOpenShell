import datetime
import ifcopenshell


class Usecase:
    def __init__(self, **settings):
        self.settings = {"version": "IFC4"}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        self.file = ifcopenshell.file(schema=self.settings["version"])
        # TODO: add all metadata, pending bug #747
        self.file.wrapped_data.header.file_name.name = "/dev/null"  # Hehehe
        self.file.wrapped_data.header.file_name.time_stamp = (
            datetime.datetime.utcnow()
            .replace(tzinfo=datetime.timezone.utc)
            .astimezone()
            .replace(microsecond=0)
            .isoformat()
        )
        self.file.wrapped_data.header.file_name.preprocessor_version = "IfcOpenShell {}".format(ifcopenshell.version)
        self.file.wrapped_data.header.file_name.originating_system = "IfcOpenShell {}".format(ifcopenshell.version)
        self.file.wrapped_data.header.file_name.authorization = "Nobody"
        return self.file
