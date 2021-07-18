import datetime
import ifcopenshell


class Usecase:
    def __init__(self, version: str = "IFC4"):
        """Create File

        Create a new IFC file object

        :param version: The schema version of the IFC file. Choose from "IFC2X3" or "IFC4".
        :return: file: The created IFC file object.
        """
        self.settings = {"version": version}

    def execute(self) -> ifcopenshell.file:
        self.file = ifcopenshell.file(schema=self.settings["version"])
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
        self.file.wrapped_data.header.file_description.description = ("ViewDefinition[DesignTransferView]",)
        return self.file
