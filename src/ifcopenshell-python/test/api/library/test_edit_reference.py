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
import ifcopenshell.api.library


class TestEditReference(test.bootstrap.IFC4):
    def test_editing_a_reference(self):
        reference = self.file.createIfcLibraryReference()
        attributes = {
            "Location": "Location",
            "Identification" if self.file.schema != "IFC2X3" else "ItemReference": "Identification",
            "Name": "Name",
        }
        if self.file.schema != "IFC2X3":
            attributes["Description"] = "Description"
            attributes["Language"] = "Language"
        ifcopenshell.api.library.edit_reference(
            self.file,
            reference=reference,
            attributes=attributes,
        )
        assert reference.Location == "Location"
        # 1 IfcExternalReference Identification(>IFC2X3) / ItemReference  (IFC2X3)
        assert reference[1] == "Identification"
        assert reference.Name == "Name"
        if self.file.schema != "IFC2X3":
            assert reference.Description == "Description"
            assert reference.Language == "Language"


class TestEditReferenceIFC2X3(test.bootstrap.IFC2X3, TestEditReference):
    pass
