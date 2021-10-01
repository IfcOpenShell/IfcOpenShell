import test.bootstrap
import ifcopenshell.api


class TestEditPerson(test.bootstrap.IFC4):
    def test_editing_a_person(self):
        person = self.file.createIfcPerson()
        ifcopenshell.api.run("owner.edit_person", self.file, person=person, attributes={
            "Identification": "Identification",
            "FamilyName": "FamilyName",
            "GivenName": "GivenName",
            "MiddleNames": ["Middle", "Names"],
            "PrefixTitles": ["Prefix", "Titles"],
            "SuffixTitles": ["Suffix", "Titles"],
        })
        assert person.Identification == "Identification"
        assert person.FamilyName == "FamilyName"
        assert person.GivenName == "GivenName"
        assert person.MiddleNames == ("Middle", "Names")
        assert person.PrefixTitles == ("Prefix", "Titles")
        assert person.SuffixTitles == ("Suffix", "Titles")
