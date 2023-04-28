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


class Usecase:
    def __init__(self, file, library=None):
        """Removes a library

        All references along with their relationships will also be removed. Any
        products which have relationships to this library will not be removed.

        :param library: The IfcLibraryInformation entity you want to remove
        :type library: ifcopenshell.entity_instance.entity_instance
        :return: None
        :rtype: None

        Example:

        .. code:: python

            library = ifcopenshell.api.run("library.add_library", model, name="Brickschema")
            ifcopenshell.api.run("library.remove_library", model, library=library)
        """
        self.file = file
        self.settings = {"library": library}

    def execute(self):
        for reference in set(self.settings["library"].HasLibraryReferences or []):
            self.file.remove(reference)
        self.file.remove(self.settings["library"])
        for rel in self.file.by_type("IfcRelAssociatesLibrary"):
            if not rel.RelatingLibrary:
                self.file.remove(rel)
