# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of Bonsai.
#
# Bonsai is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Bonsai is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Bonsai.  If not, see <http://www.gnu.org/licenses/>.

import bonsai.core.library as subject
from test.core.bootstrap import ifc, library


class TestAddLibrary:
    def test_run(self, ifc):
        ifc.run("library.add_library", name="Unnamed").should_be_called().will_return("library")
        assert subject.add_library(ifc) == "library"


class TestRemoveLibrary:
    def test_run(self, ifc):
        ifc.run("library.remove_library", library="library").should_be_called()
        subject.remove_library(ifc, library="library")


class TestEnableEditingLibraryReferences:
    def test_run(self, library):
        library.set_editing_mode("REFERENCES").should_be_called()
        library.set_active_library("library").should_be_called()
        library.import_references("library").should_be_called()
        subject.enable_editing_library_references(library, library="library")


class TestDisableEditingLibraryReferences:
    def test_run(self, library):
        library.clear_editing_mode().should_be_called()
        subject.disable_editing_library_references(library)


class TestEnableEditingLibrary:
    def test_run(self, library):
        library.set_editing_mode("LIBRARY").should_be_called()
        library.get_active_library().should_be_called().will_return("library")
        library.import_library_attributes("library").should_be_called()
        subject.enable_editing_library(library)


class TestDisableEditingLibrary:
    def test_run(self, library):
        library.set_editing_mode("REFERENCES").should_be_called()
        subject.disable_editing_library(library)


class TestEditLibrary:
    def test_run(self, ifc, library):
        library.set_editing_mode("REFERENCES").should_be_called()
        library.get_active_library().should_be_called().will_return("library")
        library.export_library_attributes().should_be_called().will_return("attributes")
        ifc.run("library.edit_library", library="library", attributes="attributes").should_be_called()
        library.import_references("library").should_be_called()
        subject.edit_library(ifc, library)


class TestAddLibraryReference:
    def test_run(self, ifc, library):
        library.get_active_library().should_be_called().will_return("library")
        ifc.run("library.add_reference", library="library").should_be_called()
        library.import_references("library").should_be_called()
        subject.add_library_reference(ifc, library)


class TestRemoveLibraryReference:
    def test_run(self, ifc, library):
        ifc.run("library.remove_reference", reference="reference").should_be_called()
        library.get_active_library().should_be_called().will_return("library")
        library.import_references("library").should_be_called()
        subject.remove_library_reference(ifc, library, reference="reference")


class TestEnableEditingLibraryReference:
    def test_run(self, library):
        library.set_editing_mode("REFERENCE").should_be_called()
        library.set_active_reference("reference").should_be_called()
        library.import_reference_attributes("reference").should_be_called()
        subject.enable_editing_library_reference(library, reference="reference")


class TestDisableEditingLibraryReference:
    def test_run(self, library):
        library.set_editing_mode("REFERENCES").should_be_called()
        subject.disable_editing_library_reference(library)


class TestEditLibraryReference:
    def test_run(self, ifc, library):
        library.set_editing_mode("REFERENCES").should_be_called()
        library.get_active_reference().should_be_called().will_return("reference")
        library.export_reference_attributes().should_be_called().will_return("attributes")
        ifc.run("library.edit_reference", reference="reference", attributes="attributes").should_be_called()
        library.get_active_library().should_be_called().will_return("library")
        library.import_references("library").should_be_called()
        subject.edit_library_reference(ifc, library)


class TestAssignLibraryReference:
    def test_run(self, ifc):
        ifc.get_entity("obj").should_be_called().will_return("product")
        ifc.run("library.assign_reference", products=["product"], reference="reference").should_be_called()
        subject.assign_library_reference(ifc, obj="obj", reference="reference")


class TestUnassignLibraryReference:
    def test_run(self, ifc):
        ifc.get_entity("obj").should_be_called().will_return("product")
        ifc.run("library.unassign_reference", products=["product"], reference="reference").should_be_called()
        subject.unassign_library_reference(ifc, obj="obj", reference="reference")
