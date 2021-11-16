import test.bootstrap
import ifcopenshell.api


class TestEditLibrary(test.bootstrap.IFC4):
    def test_editing_a_library(self):
        library = self.file.createIfcLibraryInformation()
        ifcopenshell.api.run("library.edit_library", self.file, library=library, attributes={
            "Name": "Name",
            "Version": "Version",
            "VersionDate": "VersionDate",
            "Location": "Location",
            "Description": "Description",
        })
        assert library.Name == "Name"
        assert library.Version == "Version"
        assert library.VersionDate == "VersionDate"
        assert library.Location == "Location"
        assert library.Description == "Description"
