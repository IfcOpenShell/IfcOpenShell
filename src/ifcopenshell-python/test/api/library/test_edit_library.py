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
import ifcopenshell.api


class TestEditLibrary(test.bootstrap.IFC4):
    def test_editing_a_library(self):
        library = self.file.createIfcLibraryInformation()
        ifcopenshell.api.run(
            "library.edit_library",
            self.file,
            library=library,
            attributes={
                "Name": "Name",
                "Version": "Version",
                "VersionDate": "VersionDate",
                "Location": "Location",
                "Description": "Description",
            },
        )
        assert library.Name == "Name"
        assert library.Version == "Version"
        assert library.VersionDate == "VersionDate"
        assert library.Location == "Location"
        assert library.Description == "Description"
