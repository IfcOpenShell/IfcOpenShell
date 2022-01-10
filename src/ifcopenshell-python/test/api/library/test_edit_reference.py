import test.bootstrap
import ifcopenshell.api


class TestEditReference(test.bootstrap.IFC4):
    def test_editing_a_reference(self):
        reference = self.file.createIfcLibraryReference()
        ifcopenshell.api.run(
            "library.edit_reference",
            self.file,
            reference=reference,
            attributes={
                "Location": "Location",
                "Identification": "Identification",
                "Name": "Name",
                "Description": "Description",
                "Language": "Language",
            },
        )
        assert reference.Location == "Location"
        assert reference.Identification == "Identification"
        assert reference.Name == "Name"
        assert reference.Description == "Description"
        assert reference.Language == "Language"
