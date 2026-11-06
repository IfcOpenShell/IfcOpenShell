# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2026 Petru Conduraru <petru@bimvoice.com>
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

# This file was generated with the assistance of an AI coding tool.

from pathlib import Path

import ifcopenshell
import ifcopenshell.api.context
import ifcopenshell.api.document
import ifcopenshell.api.geometry
import ifcopenshell.api.project
import ifcopenshell.api.root
import ifcopenshell.api.unit
import ifcopenshell.util.placement
import numpy as np

import ifcpatch
import test.bootstrap


class TestBindLinkedModels(test.bootstrap.IFC4):
    def setup_project(self, ifc_file: ifcopenshell.file) -> None:
        ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcProject")
        unit = ifcopenshell.api.unit.add_si_unit(ifc_file, unit_type="LENGTHUNIT")
        ifcopenshell.api.unit.assign_unit(ifc_file, units=[unit])
        ifcopenshell.api.context.add_context(ifc_file, "Model")

    def add_wall(self, ifc_file: ifcopenshell.file, x: float, y: float) -> ifcopenshell.entity_instance:
        wall = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcWall")
        matrix = np.eye(4)
        matrix[:2, 3] = (x, y)
        ifcopenshell.api.geometry.edit_object_placement(ifc_file, product=wall, matrix=matrix)
        return wall

    def add_linked_wall(self, directory: Path, matrix: np.ndarray) -> None:
        linked = ifcopenshell.api.project.create_file()
        self.setup_project(linked)
        self.add_wall(linked, 1, 0)
        linked.write(str(directory / "linked.ifc"))
        document = ifcopenshell.api.document.add_information(self.file)
        document.Name = "linked.ifc"
        document.Scope = "LINKED_MODEL"
        reference = ifcopenshell.api.document.add_reference(self.file, information=document)
        reference[1] = ",".join(str(o) for o in matrix.flatten().tolist())
        reference.Location = "linked.ifc"

    def bind(self, directory: Path) -> ifcopenshell.file:
        return ifcpatch.execute({"file": self.file, "recipe": "BindLinkedModels", "arguments": [str(directory)]})

    def test_translating_the_linked_elements(self, tmp_path: Path):
        self.setup_project(self.file)
        matrix = np.eye(4)
        matrix[:3, 3] = (10, 20, 30)
        self.add_linked_wall(tmp_path, matrix)

        output = self.bind(tmp_path)

        wall = output.by_type("IfcWall")[0]
        placement = ifcopenshell.util.placement.get_local_placement(wall.ObjectPlacement)
        assert np.allclose(placement[:, 3], (11, 20, 30, 1))
        assert len(output.by_type("IfcProject")) == 1

    def test_rotating_the_linked_elements(self, tmp_path: Path):
        self.setup_project(self.file)
        matrix = np.eye(4)
        matrix[:2, :2] = ((0, -1), (1, 0))
        self.add_linked_wall(tmp_path, matrix)

        output = self.bind(tmp_path)

        placement = ifcopenshell.util.placement.get_local_placement(output.by_type("IfcWall")[0].ObjectPlacement)
        assert np.allclose(placement[:, 3], (0, 1, 0, 1))
        assert np.allclose(placement[:3, 0], (0, 1, 0))

    def test_removing_the_link(self, tmp_path: Path):
        self.setup_project(self.file)
        self.add_linked_wall(tmp_path, np.eye(4))

        output = self.bind(tmp_path)

        assert not output.by_type("IfcDocumentInformation")
        assert not output.by_type("IfcDocumentReference")

    def test_leaving_the_host_elements_in_place(self, tmp_path: Path):
        self.setup_project(self.file)
        host_wall = self.add_wall(self.file, 5, 5)
        matrix = np.eye(4)
        matrix[:3, 3] = (10, 0, 0)
        self.add_linked_wall(tmp_path, matrix)

        output = self.bind(tmp_path)

        assert len(output.by_type("IfcWall")) == 2
        placement = ifcopenshell.util.placement.get_local_placement(host_wall.ObjectPlacement)
        assert np.allclose(placement[:, 3], (5, 5, 0, 1))

    def test_a_model_without_links_is_unchanged(self):
        self.setup_project(self.file)
        self.add_wall(self.file, 5, 5)

        output = ifcpatch.execute({"file": self.file, "recipe": "BindLinkedModels", "arguments": []})

        assert len(output.by_type("IfcWall")) == 1
