# IfcPatch - IFC patching utiliy
# Copyright (C) 2023 Dion Moult <dion@thinkmoult.com>
#
# This file is part of IfcPatch.
#
# IfcPatch is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcPatch is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcPatch.  If not, see <http://www.gnu.org/licenses/>.

import datetime


class Patcher:
    def __init__(self, src, file, logger):
        """Purge IFC properties, relationships, and other data

        In some rare cases (i.e. "resetting" a model or for security purposes)
        you may need to purge all relationships and data within a model but
        retain the ability to view the geometry in a model. This patch purges
        the following relationships:

        - STEP comments, which may include software export metadata
        - Header data, which may include filenames
        - Owner, person, organisation, and application data
        - Addresses
        - Rooted names
        - Tags (that reference original software)
        - Properties and quantities
        - Materials
        - Styles (e.g. colours)
        - External references like classifications, documents, libraries
        - Types
        - Groups (such as model groups or search groups) and systems
        - Profile names

        Example:

        .. code:: python

            # Watch the world burn
            ifcpatch.execute({"input": model, "recipe": "PurgeData", "arguments": []})
        """
        self.src = src
        self.file = file
        self.logger = logger

    def patch(self):
        self.file.wrapped_data.header.file_name.name = "Rabbit"
        self.file.wrapped_data.header.file_name.time_stamp = (
            datetime.datetime.utcnow()
            .replace(tzinfo=datetime.timezone.utc)
            .astimezone()
            .replace(microsecond=0)
            .isoformat()
        )
        self.file.wrapped_data.header.file_name.preprocessor_version = "Rabbit"
        self.file.wrapped_data.header.file_name.originating_system = "Rabbit"

        for element in self.file.by_type("IfcApplication"):
            element.Version = "Rabbit"
            element.ApplicationFullName = "Rabbit"
            element.ApplicationIdentifier = "Rabbit"

        for element in self.file.by_type("IfcOrganization"):
            element[0] = None  # Id
            element.Name = "Rabbit"
            element.Description = None
            element.Roles = []
            element.Addresses = []

        for element in self.file.by_type("IfcPerson"):
            for i in range(0, len(element)):
                element[i] = None

        for element in self.file.by_type("IfcPersonAndOrganization"):
            element.Roles = []

        for element in self.file.by_type("IfcActorRole"):
            self.file.remove(element)

        for element in self.file.by_type("IfcAddress"):
            self.file.remove(element)

        for element in self.file.by_type("IfcRoot"):
            element.Name = "Rabbit"
            element.Description = "Rabbit"

        for element in self.file.by_type("IfcContext"):
            element.ObjectType = None
            element.LongName = None
            element.Phase = None

        for element in self.file.by_type("IfcSpatialElement"):
            element.LongName = None

        for element in self.file.by_type("IfcOwnerHistory"):
            element.State = None
            element.ChangeAction = None
            element.LastModifiedDate = None
            element.LastModifyingUser = None
            element.LastModifyingApplication = None
            element.CreationDate = 0

        for element in self.file.by_type("IfcRelDefines"):
            self.file.remove(element)

        for element in self.file.by_type("IfcTypeProduct"):
            self.file.remove(element)

        for element in self.file.by_type("IfcElement"):
            element.Tag = None
            element.ObjectType = None

        for element in self.file.by_type("IfcPropertyDefinition"):
            self.file.remove(element)

        for element in self.file.by_type("IfcPropertyAbstraction"):
            self.file.remove(element)

        for element in self.file.by_type("IfcPhysicalQuantity"):
            self.file.remove(element)

        for element in self.file.by_type("IfcRelAssociates"):
            self.file.remove(element)

        for element in self.file.by_type("IfcMaterialDefinition"):
            self.file.remove(element)

        for element in self.file.by_type("IfcMaterialDefinitionRepresentation"):
            self.file.remove(element)

        for element in self.file.by_type("IfcMaterialUsageDefinition"):
            self.file.remove(element)

        for element in self.file.by_type("IfcMaterialList"):
            self.file.remove(element)

        for element in self.file.by_type("IfcStyledItem"):
            self.file.remove(element)

        for element in self.file.by_type("IfcStyledRepresentation"):
            self.file.remove(element)

        for element in self.file.by_type("IfcPresentationStyle"):
            self.file.remove(element)

        for element in self.file.by_type("IfcPresentationItem"):
            self.file.remove(element)

        for element in self.file.by_type("IfcExternalInformation"):
            self.file.remove(element)

        for element in self.file.by_type("IfcExternalReference"):
            self.file.remove(element)

        for element in self.file.by_type("IfcTypeObject"):
            self.file.remove(element)

        for element in self.file.by_type("IfcGroup"):
            self.file.remove(element)

        for element in self.file.by_type("IfcRelAssigns"):
            self.file.remove(element)

        for element in self.file.by_type("IfcProfileDef"):
            element.ProfileName = None
