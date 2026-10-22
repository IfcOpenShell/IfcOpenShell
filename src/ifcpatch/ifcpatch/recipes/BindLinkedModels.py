# IfcPatch - IFC patching utiliy
# Copyright (C) 2026 Petru Conduraru <petru@bimvoice.com>
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

# This file was generated with the assistance of an AI coding tool.

from logging import Logger
from pathlib import Path

import ifcopenshell
import ifcopenshell.api.document
import ifcopenshell.api.geometry
import ifcopenshell.util.placement
import ifcopenshell.util.unit
import numpy as np

import ifcpatch
from ifcpatch.recipes.MergeProjects import Patcher as MergeProjects


class Patcher(ifcpatch.BasePatcher):
    def __init__(self, file: ifcopenshell.file, logger: Logger | None = None, base_directory: str = ""):
        """Bind linked models into the model and remove the links

        Each linked model (an IfcDocumentInformation with the scope
        LINKED_MODEL, as created by the Bonsai link tool) is merged into the
        model with the MergeProjects recipe. The link transformation stored in
        the link reference is then applied to the merged elements, and the link
        is removed. Note that the merged elements keep their GlobalIds, so
        linking the same file twice results in duplicated GlobalIds.

        :param base_directory: The directory that relative link locations are
            resolved against. Usually the directory of the input model.

        Example:

        .. code:: python

            ifcpatch.execute({"input": "input.ifc", "file": model, "recipe": "BindLinkedModels", "arguments": ["/path/to/project"]})
        """
        super().__init__(file, logger)
        self.base_directory = base_directory

    def patch(self):
        for document in self.file.by_type("IfcDocumentInformation"):
            if document.Scope != "LINKED_MODEL":
                continue
            references = document.DocumentReferences if self.file.schema == "IFC2X3" else document.HasDocumentReferences
            for reference in references or []:
                self.bind(reference)
                ifcopenshell.api.document.remove_reference(self.file, reference)
            ifcopenshell.api.document.remove_information(self.file, document)

    def bind(self, reference: ifcopenshell.entity_instance) -> None:
        other = ifcopenshell.open(str(Path(self.base_directory) / reference.Location))
        existing = {p.id() for p in self.file.by_type("IfcProduct")}
        MergeProjects(self.file, self.logger).merge(other)
        if not reference[1]:
            return
        matrix = np.fromstring(reference[1], sep=",", dtype=np.float64).reshape(4, 4)
        if np.allclose(matrix, np.eye(4)):
            return
        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(self.file)
        for product in self.file.by_type("IfcProduct"):
            if product.id() in existing or not (placement := product.ObjectPlacement):
                continue
            if not placement.is_a("IfcLocalPlacement") or placement.PlacementRelTo:
                continue
            current = ifcopenshell.util.placement.get_local_placement(placement)
            current[:3, 3] *= unit_scale
            ifcopenshell.api.geometry.edit_object_placement(
                self.file, product, matrix @ current, is_si=True, should_transform_children=True
            )
