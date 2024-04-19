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
import ifcopenshell
from logging import Logger


class Patcher:
    def __init__(self, src: str, file: ifcopenshell.file, logger: Logger):
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
            ifcpatch.execute({"input": "input.ifc", "file": model, "recipe": "PurgeData", "arguments": []})
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

        if self.file.schema == "IFC2X3":
            elements = self.file.by_type("IfcProject")
        else:
            elements = self.file.by_type("IfcContext")
        for element in elements:
            element.ObjectType = None
            element.LongName = None
            element.Phase = None

        if self.file.schema == "IFC2X3":
            elements = self.file.by_type("IfcSpatialStructureElement")
        else:
            elements = self.file.by_type("IfcSpatialElement")
        for element in elements:
            element.LongName = None

        for element in self.file.by_type("IfcOwnerHistory"):
            element.State = None
            element.ChangeAction = "NOCHANGE" if self.file.schema == "IFC2X3" else None
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

        if self.file.schema == "IFC2X3":
            elements = self.file.by_type("IfcProperty")
        else:
            elements = self.file.by_type("IfcPropertyAbstraction")
        for element in elements:
            self.file.remove(element)

        for element in self.file.by_type("IfcPhysicalQuantity"):
            self.file.remove(element)

        for element in self.file.by_type("IfcRelAssociates"):
            self.file.remove(element)

        if self.file.schema == "IFC2X3":
            elements = (
                self.file.by_type("IfcMaterial")
                + self.file.by_type("IfcMaterialLayer")
                + self.file.by_type("IfcMaterialLayerSet")
                + self.file.by_type("IfcMaterialLayerSetUsage")
                + self.file.by_type("IfcMaterialList")
            )
        else:
            elements = self.file.by_type("IfcMaterialDefinition")
        for element in elements:
            self.file.remove(element)

        for element in self.file.by_type("IfcMaterialDefinitionRepresentation"):
            self.file.remove(element)

        if self.file.schema == "IFC2X3":
            elements = []
        else:
            elements = self.file.by_type("IfcMaterialUsageDefinition")
        for element in elements:
            self.file.remove(element)

        for element in self.file.by_type("IfcMaterialList"):
            self.file.remove(element)

        for element in self.file.by_type("IfcStyledItem"):
            self.file.remove(element)

        for element in self.file.by_type("IfcStyledRepresentation"):
            self.file.remove(element)

        for element in self.file.by_type("IfcPresentationStyle"):
            self.file.remove(element)

        if self.file.schema == "IFC2X3":
            elements = (
                self.file.by_type("IfcColourSpecification")
                + self.file.by_type("IfcCurveStyleFont")
                + self.file.by_type("IfcCurveStyleFontAndScaling")
                + self.file.by_type("IfcCurveStyleFontPattern")
                + self.file.by_type("IfcPreDefinedItem")
                + self.file.by_type("IfcSurfaceStyleLighting")
                + self.file.by_type("IfcSurfaceStyleRefraction")
                + self.file.by_type("IfcSurfaceStyleShading")
                + self.file.by_type("IfcSurfaceStyleWithTextures")
                + self.file.by_type("IfcSurfaceTexture")
                + self.file.by_type("IfcTextStyleForDefinedFont")
                + self.file.by_type("IfcTextStyleTextModel")
                + self.file.by_type("IfcTextStyleWithBoxCharacteristics")
                + self.file.by_type("IfcTextureCoordinate")
                + self.file.by_type("IfcTextureVertex")
                + self.file.by_type("IfcTextStyleForDefinedFont")
                + self.file.by_type("IfcTextStyleForDefinedFont")
            )
        else:
            elements = self.file.by_type("IfcPresentationItem")
        for element in elements:
            self.file.remove(element)

        if self.file.schema == "IFC2X3":
            elements = (
                self.file.by_type("IfcClassification")
                + self.file.by_type("IfcDocumentInformation")
                + self.file.by_type("IfcLibraryInformation")
            )
        else:
            elements = self.file.by_type("IfcExternalInformation")
        for element in elements:
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

        for element in self.file.by_type("IfcShapeAspect"):
            element.Name = None
            element.Description = None

        for element in self.file.by_type("IfcPresentationLayerAssignment"):
            self.file.remove(element)
