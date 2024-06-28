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

import test.bootstrap
import ifcopenshell.api.root
import ifcopenshell.api.aggregate
import ifcopenshell.util.element


class TestUnassignObject(test.bootstrap.IFC4):
    def test_unassigning_an_object(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcSite")
        subelement1 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcBuilding")
        subelement2 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcBuilding")
        ifcopenshell.api.aggregate.assign_object(
            self.file, products=[subelement1, subelement2], relating_object=element
        )
        ifcopenshell.api.aggregate.unassign_object(self.file, products=[subelement1, subelement2])
        assert ifcopenshell.util.element.get_aggregate(subelement1) is None
        assert ifcopenshell.util.element.get_aggregate(subelement2) is None

    def test_the_rel_is_kept_if_there_are_more_decomposed_elements(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcSite")
        subelement2 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcBuilding")
        subelement1 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcBuilding")
        ifcopenshell.api.aggregate.assign_object(self.file, products=[subelement1], relating_object=element)
        ifcopenshell.api.aggregate.assign_object(self.file, products=[subelement2], relating_object=element)
        ifcopenshell.api.aggregate.unassign_object(self.file, products=[subelement1])
        assert len(self.file.by_type("IfcRelAggregates")) == 1

    def test_the_rel_is_purged_if_there_are_no_more_decomposed_elements(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcSite")
        subelement = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcBuilding")
        ifcopenshell.api.aggregate.assign_object(self.file, products=[subelement], relating_object=element)
        ifcopenshell.api.aggregate.unassign_object(self.file, products=[subelement])
        assert len(self.file.by_type("IfcRelAggregates")) == 0


class TestUnassignObjectIFC2X3(test.bootstrap.IFC2X3, TestUnassignObject):
    pass
