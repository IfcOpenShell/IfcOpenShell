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


def add_metric_reference(
    file: ifcopenshell.file, metric: ifcopenshell.entity_instance, reference_path: str
) -> list[ifcopenshell.entity_instance]:
    """
    Adds a chain of references to a metric. The reference path is a string of the form "attribute.attribute.attribute"
    Used to reference a value of an attribute of an instance through a metric objective entity.
    """
    settings = {"metric": metric, "reference_path": reference_path}

    references_created = []
    if settings["reference_path"]:
        attributes = settings["reference_path"].split(".")
        for i in range(len(attributes)):
            if i == 0:
                reference = file.create_entity("IfcReference")
                reference.AttributeIdentifier = attributes[i]
                settings["metric"].ReferencePath = reference
                references_created.append(reference)
            else:
                reference = file.create_entity("IfcReference")
                reference.AttributeIdentifier = attributes[i]
                references_created[i - 1].InnerReference = reference
                references_created.append(reference)
    return references_created
