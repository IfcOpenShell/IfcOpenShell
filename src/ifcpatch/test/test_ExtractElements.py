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
import pytest
import ifcpatch
import ifcopenshell
import ifcopenshell.api
import ifcopenshell.util.element


class TestExtractElements:
    def test_basic(self):
        ifc_file = ifcopenshell.file()
        project = ifcopenshell.api.run("root.create_entity", ifc_file, ifc_class="IfcProject")
        wall = ifcopenshell.api.run("root.create_entity", ifc_file, ifc_class="IfcWall")
        output = ifcpatch.execute({"file": ifc_file, "recipe": "ExtractElements", "arguments": ["IfcWall"]})

        assert output.by_type("IfcProject")[0].GlobalId == project.GlobalId
        assert output.by_type("IfcWall")[0].GlobalId == wall.GlobalId

    def test_keep_spatial_structure(self):
        ifc_file = ifcopenshell.file()
        project = ifcopenshell.api.run("root.create_entity", ifc_file, ifc_class="IfcProject")

        site = ifcopenshell.api.run("root.create_entity", ifc_file, ifc_class="IfcSite")
        building = ifcopenshell.api.run("root.create_entity", ifc_file, ifc_class="IfcBuilding")
        storey = ifcopenshell.api.run("root.create_entity", ifc_file, ifc_class="IfcBuildingStorey")
        wall = ifcopenshell.api.run("root.create_entity", ifc_file, ifc_class="IfcWall")
        ifcopenshell.api.run("aggregate.assign_object", ifc_file, product=building, relating_object=site)
        ifcopenshell.api.run("aggregate.assign_object", ifc_file, product=storey, relating_object=building)
        ifcopenshell.api.run("spatial.assign_container", ifc_file, products=[wall], relating_structure=storey)

        output = ifcpatch.execute({"file": ifc_file, "recipe": "ExtractElements", "arguments": ["IfcWall"]})

        wall_new = output.by_type("IfcWall")[0]
        assert (storey_new := ifcopenshell.util.element.get_container(wall_new)).GlobalId == storey.GlobalId
        assert (building_new := ifcopenshell.util.element.get_aggregate(storey_new)).GlobalId == building.GlobalId
        assert (site_new := ifcopenshell.util.element.get_aggregate(building_new)).GlobalId == site.GlobalId

    def test_keep_aggregate_in_spatial_structure(self):
        ifc_file = ifcopenshell.file()
        project = ifcopenshell.api.run("root.create_entity", ifc_file, ifc_class="IfcProject")

        element = ifcopenshell.api.run("root.create_entity", ifc_file, ifc_class="IfcElementAssembly")
        container = ifcopenshell.api.run("root.create_entity", ifc_file, ifc_class="IfcBuildingStorey")
        subelement = ifcopenshell.api.run("root.create_entity", ifc_file, ifc_class="IfcWall")
        ifcopenshell.api.run("spatial.assign_container", ifc_file, products=[element], relating_structure=container)
        ifcopenshell.api.run("aggregate.assign_object", ifc_file, product=subelement, relating_object=element)

        output = ifcpatch.execute({"file": ifc_file, "recipe": "ExtractElements", "arguments": ["IfcWall"]})

        wall_new = output.by_type("IfcWall")[0]
        assembly = output.by_type("IfcElementAssembly")[0]

        assert ifcopenshell.util.element.get_aggregate(wall_new).GlobalId == element.GlobalId
        assert ifcopenshell.util.element.get_container(assembly).GlobalId == container.GlobalId

    def test_getting_the_psets_of_a_product_as_a_dictionary(self):
        ifc = ifcopenshell.open(os.path.join(os.getcwd(), "test", "files", "basic.ifc"))
        output = ifcpatch.execute({"file": ifc, "recipe": "ExtractElements", "arguments": ["IfcWall"]})
        assert output.by_type("IfcWall")
        assert not output.by_type("IfcSlab")
