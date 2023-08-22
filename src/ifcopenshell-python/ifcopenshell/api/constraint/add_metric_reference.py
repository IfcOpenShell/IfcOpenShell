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

import ifcopenshell

class Usecase:
    def __init__(self, file, metric=None, reference_path=None):
        """
        Adds a chain of references to a metric. The reference path is a string of the form "attribute.attribute.attribute" 
        Used to reference a value of an attribute of an instance through a metric objective entity.
        """
        self.file = file
        self.settings = {"metric": metric, "reference_path": reference_path}

    def execute(self):
        if self.settings["reference_path"]:
            attributes = self.settings["reference_path"].split(".")
            references_created = []
            for i in range(len(attributes)):
                if i == 0:
                    reference = self.file.create_entity("IfcReference")
                    reference.AttributeIdentifier = attributes[i]
                    self.settings["metric"].ReferencePath = reference
                    references_created.append(reference)
                else:
                    reference = self.file.create_entity("IfcReference")
                    reference.AttributeIdentifier = attributes[i]
                    references_created[i-1].InnerReference = reference
                    references_created.append(reference)
            return references_created