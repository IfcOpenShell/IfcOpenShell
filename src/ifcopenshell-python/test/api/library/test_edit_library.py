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
import datetime
import ifcopenshell.api.library
import ifcopenshell.util.date


class TestEditLibrary(test.bootstrap.IFC4):
    def test_editing_a_library(self):
        library = self.file.createIfcLibraryInformation()
        dt = datetime.datetime.now()
        attributes = {
            "Name": "Name",
            "Version": "Version",
            "VersionDate": dt,
        }
        if self.file.schema != "IFC2X3":
            attributes["Location"] = "Location"
            attributes["Description"] = "Description"

        ifcopenshell.api.library.edit_library(
            self.file,
            library=library,
            attributes=attributes,
        )
        assert library.Name == "Name"
        assert library.Version == "Version"
        if self.file.schema != "IFC2X3":
            assert library.VersionDate == ifcopenshell.util.date.datetime2ifc(dt, "IfcDateTime")
            assert library.Location == "Location"
            assert library.Description == "Description"
        else:
            info = library.VersionDate.get_info()
            del info["id"], info["type"]
            assert info == ifcopenshell.util.date.datetime2ifc(dt, "IfcCalendarDate")


class TestEditLibraryIFC2X3(test.bootstrap.IFC2X3, TestEditLibrary):
    pass
