# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026
#
# This file is part of Bonsai.
#
# Bonsai is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Bonsai is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Bonsai.  If not, see <http://www.gnu.org/licenses/>.
#
# This file was generated with the assistance of an AI coding tool.

"""Host resolution for door and window fillings.

A pick can land on something the wall decomposes into rather than on the wall,
which is common in models exported from other tools where a wall aggregates its
course lines. The filling belongs in the wall either way."""

import ifcopenshell
import ifcopenshell.api.aggregate
import ifcopenshell.api.root
import pytest

from bonsai.bim.module.model.opening import get_filling_host
from test.bim.bootstrap import NewFile


class TestGetFillingHost(NewFile):
    def create_file(self) -> ifcopenshell.file:
        ifc = ifcopenshell.file()
        ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcProject")
        return ifc

    def test_a_wall_hosts_itself(self):
        ifc = self.create_file()
        wall = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcWall")
        assert get_filling_host(wall) == wall

    def test_the_other_host_classes_resolve_to_themselves(self):
        ifc = self.create_file()
        for ifc_class in ("IfcWallStandardCase", "IfcCovering", "IfcElementAssembly"):
            element = ifcopenshell.api.root.create_entity(ifc, ifc_class=ifc_class)
            assert get_filling_host(element) == element

    def test_a_part_the_wall_aggregates_resolves_to_the_wall(self):
        ifc = self.create_file()
        wall = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcWall")
        annotation = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcAnnotation")
        ifcopenshell.api.aggregate.assign_object(ifc, products=[annotation], relating_object=wall)
        assert get_filling_host(annotation) == wall

    def test_resolution_walks_more_than_one_level(self):
        ifc = self.create_file()
        wall = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcWall")
        part = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcBuildingElementPart")
        annotation = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcAnnotation")
        ifcopenshell.api.aggregate.assign_object(ifc, products=[part], relating_object=wall)
        ifcopenshell.api.aggregate.assign_object(ifc, products=[annotation], relating_object=part)
        assert get_filling_host(annotation) == wall

    def test_an_element_that_is_not_part_of_a_host_resolves_to_nothing(self):
        ifc = self.create_file()
        # A beam sitting against a wall is not part of it, so it cannot stand in for one.
        beam = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcBeam")
        assert get_filling_host(beam) is None

    def test_nothing_resolves_to_nothing(self):
        assert get_filling_host(None) is None
