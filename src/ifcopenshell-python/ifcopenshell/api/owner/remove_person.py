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

import ifcopenshell.api


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"person": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        for role in self.settings["person"].Roles or []:
            if len(self.file.get_inverse(role)) == 1:
                ifcopenshell.api.run("owner.remove_role", self.file, role=role)
        for address in self.settings["person"].Addresses or []:
            if len(self.file.get_inverse(address)) == 1:
                ifcopenshell.api.run("owner.remove_address", self.file, address=address)
        for inverse in self.file.get_inverse(self.settings["person"]):
            if inverse.is_a("IfcWorkControl"):
                if inverse.Creators == (self.settings["person"],):
                    inverse.Creators = None
            elif inverse.is_a("IfcInventory"):
                if inverse.ResponsiblePersons == (self.settings["person"],):
                    inverse.ResponsiblePersons = None
            elif inverse.is_a("IfcDocumentInformation"):
                if inverse.Editors == (self.settings["person"],):
                    inverse.Editors = None
            elif inverse.is_a("IfcPersonAndOrganization"):
                ifcopenshell.api.run("owner.remove_person_and_organisation", self.file, person_and_organisation=inverse)
            elif inverse.is_a("IfcActor"):
                ifcopenshell.api.run("root.remove_product", self.file, product=inverse)
            elif inverse.is_a("IfcResourceLevelRelationship"):
                if inverse.RelatedResourceObjects == (self.settings["person"],):
                    self.file.remove(inverse)
        self.file.remove(self.settings["person"])
