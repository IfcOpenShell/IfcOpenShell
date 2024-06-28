# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of IfcOpenShell.
#
# IfcOpenShell is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcOpenShell is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcOpenShell.  If not, see <http://www.gnu.org/licenses/>.

import test.bootstrap
import ifcopenshell.api.owner


class TestEditPerson(test.bootstrap.IFC4):
    def test_editing_a_person(self):
        person = self.file.createIfcPerson()
        ifcopenshell.api.owner.edit_person(
            self.file,
            person=person,
            attributes={
                "Identification" if self.file.schema != "IFC2X3" else "Id": "Identification",
                "FamilyName": "FamilyName",
                "GivenName": "GivenName",
                "MiddleNames": ["Middle", "Names"],
                "PrefixTitles": ["Prefix", "Titles"],
                "SuffixTitles": ["Suffix", "Titles"],
            },
        )
        # 0 IfcPerson Identification(>IFC2X3) / Id (IFC2X3)
        assert person[0] == "Identification"
        assert person.FamilyName == "FamilyName"
        assert person.GivenName == "GivenName"
        assert person.MiddleNames == ("Middle", "Names")
        assert person.PrefixTitles == ("Prefix", "Titles")
        assert person.SuffixTitles == ("Suffix", "Titles")


class TestEditPersonIFC2X3(test.bootstrap.IFC2X3, TestEditPerson):
    pass
