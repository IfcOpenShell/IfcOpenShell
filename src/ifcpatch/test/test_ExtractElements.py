# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
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

import os

import ifcopenshell
import ifcopenshell.api.aggregate
import ifcopenshell.api.context
import ifcopenshell.api.geometry
import ifcopenshell.api.georeference
import ifcopenshell.api.root
import ifcopenshell.api.spatial
import ifcopenshell.util.element
import numpy
import pytest

import ifcpatch
import test.bootstrap


class TestExtractElements(test.bootstrap.IFC4):
    def test_basic(self):
        project = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        wall = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        output = ifcpatch.execute({"file": self.file, "recipe": "ExtractElements", "arguments": ["IfcWall"]})

        assert output.by_type("IfcProject")[0].GlobalId == project.GlobalId
        assert output.by_type("IfcWall")[0].GlobalId == wall.GlobalId

    def test_keep_spatial_structure(self):
        project = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")

        site = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcSite")
        building = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcBuilding")
        storey = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcBuildingStorey")
        wall = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        ifcopenshell.api.aggregate.assign_object(self.file, products=[building], relating_object=site)
        ifcopenshell.api.aggregate.assign_object(self.file, products=[storey], relating_object=building)
        ifcopenshell.api.spatial.assign_container(self.file, products=[wall], relating_structure=storey)

        output = ifcpatch.execute({"file": self.file, "recipe": "ExtractElements", "arguments": ["IfcWall"]})

        wall_new = output.by_type("IfcWall")[0]
        assert (storey_new := ifcopenshell.util.element.get_container(wall_new)).GlobalId == storey.GlobalId
        assert (building_new := ifcopenshell.util.element.get_aggregate(storey_new)).GlobalId == building.GlobalId
        assert (site_new := ifcopenshell.util.element.get_aggregate(building_new)).GlobalId == site.GlobalId

    def test_keep_aggregate_in_spatial_structure(self):
        project = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")

        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcElementAssembly")
        container = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcBuildingStorey")
        subelement = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        ifcopenshell.api.spatial.assign_container(self.file, products=[element], relating_structure=container)
        ifcopenshell.api.aggregate.assign_object(self.file, products=[subelement], relating_object=element)

        output = ifcpatch.execute({"file": self.file, "recipe": "ExtractElements", "arguments": ["IfcWall"]})

        wall_new = output.by_type("IfcWall")[0]
        assembly = output.by_type("IfcElementAssembly")[0]

        assert ifcopenshell.util.element.get_aggregate(wall_new).GlobalId == element.GlobalId
        assert ifcopenshell.util.element.get_container(assembly).GlobalId == container.GlobalId

    def test_getting_the_psets_of_a_product_as_a_dictionary(self):
        ifc = ifcopenshell.open(os.path.join(os.path.dirname(__file__), "files", "basic.ifc"))
        output = ifcpatch.execute({"file": ifc, "recipe": "ExtractElements", "arguments": ["IfcWall"]})
        assert output.by_type("IfcWall")
        assert not output.by_type("IfcSlab")

    def test_preserving_georeferencing(self):
        # Regression test for #8199: ExtractElements must carry IfcMapConversion
        # and IfcProjectedCRS into the output. Without the fix these entities are
        # silently dropped because they reference the IfcGeometricRepresentationContext
        # via an inverse attribute and are therefore not reachable through the
        # IfcProject forward-attribute walk used by self.new.add().
        if self.file.schema == "IFC2X3":
            pytest.skip("IfcMapConversion does not exist in IFC2X3")
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        ifcopenshell.api.context.add_context(self.file, context_type="Model")
        ifcopenshell.api.georeference.add_georeferencing(self.file)
        ifcopenshell.api.georeference.edit_georeferencing(
            self.file,
            coordinate_operation={"Eastings": 100000.0, "Northings": 200000.0},
        )
        wall = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        matrix = numpy.eye(4)
        matrix[:3, 3] = [5.0, 10.0, 2.0]
        ifcopenshell.api.geometry.edit_object_placement(self.file, product=wall, matrix=matrix)

        output = ifcpatch.execute({"file": self.file, "recipe": "ExtractElements", "arguments": ["IfcWall"]})

        assert len(output.by_type("IfcMapConversion")) == 1
        assert len(output.by_type("IfcProjectedCRS")) == 1
        conversion = output.by_type("IfcMapConversion")[0]
        assert conversion.Eastings == 100000.0
        assert conversion.Northings == 200000.0
        # Placements must be copied verbatim: extraction must not bake map
        # coordinates (or any other georeferencing transform) into the local
        # placements of the extracted elements.
        wall_new = output.by_type("IfcWall")[0]
        assert wall_new.ObjectPlacement.RelativePlacement.Location.Coordinates == (5.0, 10.0, 2.0)

    @pytest.mark.skipif(
        "IFC4X3" not in ifcopenshell.ifcopenshell_wrapper.schema_names(),
        reason=(
            "Need some non-standard schema available for this test."
            "IFC4X3 is typically available in the full build, but not in CI."
        ),
    )
    def test_extracting_non_standard_schema_version(self):
        self.file = ifcopenshell.file(schema_version=(4, 3, 0, 0))
        project = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        wall = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        output = ifcpatch.execute({"file": self.file, "recipe": "ExtractElements", "arguments": ["IfcWall"]})
        assert output.by_type("IfcProject")[0].GlobalId == project.GlobalId
        assert output.by_type("IfcWall")[0].GlobalId == wall.GlobalId


class TestExtractElementsIFC2X3(test.bootstrap.IFC2X3, TestExtractElements):
    pass
