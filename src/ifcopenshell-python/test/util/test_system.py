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

import pytest
import test.bootstrap
import ifcopenshell.api
import ifcopenshell.util.system as subject


class TestGetSystemElements(test.bootstrap.IFC4):
    def test_run(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcPump")
        system = ifcopenshell.api.run("system.add_system", self.file, ifc_class="IfcSystem")
        ifcopenshell.api.run("system.assign_system", self.file, product=element, system=system)
        assert subject.get_system_elements(system) == [element]


class TestGetElementSystems(test.bootstrap.IFC4):
    def test_run(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcPump")
        system = ifcopenshell.api.run("system.add_system", self.file, ifc_class="IfcSystem")
        ifcopenshell.api.run("system.assign_system", self.file, product=element, system=system)
        assert subject.get_element_systems(element) == [system]

    def test_do_not_get_non_services_groups(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcPump")
        ifcopenshell.api.run("system.assign_system", self.file, product=element, system=self.file.createIfcGroup())
        ifcopenshell.api.run("system.assign_system", self.file, product=element, system=self.file.createIfcZone())
        ifcopenshell.api.run(
            "system.assign_system", self.file, product=element, system=self.file.createIfcStructuralAnalysisModel()
        )
        assert not subject.get_element_systems(element)
