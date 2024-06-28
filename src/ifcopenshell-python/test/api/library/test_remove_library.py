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


class TestRemoveLibrary(test.bootstrap.IFC4):
    def test_removing_a_library(self):
        library = self.file.createIfcLibraryInformation()
        ifcopenshell.api.library.remove_library(self.file, library=library)
        assert len(self.file.by_type("IfcLibraryInformation")) == 0

    def test_removing_a_library_and_all_references(self):
        if self.file.schema != "IFC2X3":
            library = self.file.createIfcLibraryInformation()
            reference1 = self.file.createIfcLibraryReference(ReferencedLibrary=library)
            reference2 = self.file.createIfcLibraryReference(ReferencedLibrary=library)
        else:
            reference1 = self.file.createIfcLibraryReference()
            reference2 = self.file.createIfcLibraryReference()
            library = self.file.createIfcLibraryInformation(LibraryReference=[reference1, reference2])

        self.file.createIfcRelAssociatesLibrary(GlobalId="foo", RelatingLibrary=library)
        self.file.createIfcRelAssociatesLibrary(GlobalId="bar", RelatingLibrary=reference1)
        ifcopenshell.api.library.remove_library(self.file, library=library)
        assert len(self.file.by_type("IfcLibraryReference")) == 0
        assert len(self.file.by_type("IfcRelAssociatesLibrary")) == 0


class TestRemoveLibraryIFC2X3(test.bootstrap.IFC2X3, TestRemoveLibrary):
    pass
