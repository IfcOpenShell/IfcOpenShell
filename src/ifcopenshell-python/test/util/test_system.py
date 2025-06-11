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
import ifcopenshell.api.root
import ifcopenshell.api.system
import ifcopenshell.util.schema
import ifcopenshell.util.system as subject
from typing import get_args


class TestValidateGroupTypes:
    def test_run(self):
        ifcsystem_classes = set()
        for schema_name in get_args(ifcopenshell.util.schema.IFC_SCHEMA):
            schema = ifcopenshell.schema_by_name(schema_name)
            declaration = schema.declaration_by_name("IfcSystem")
            declarations = ifcopenshell.util.schema.get_subtypes(declaration)
            ifcsystem_classes.update(d.name() for d in declarations)

        used_classes = set(subject.group_types)
        unused_classes = ifcsystem_classes - used_classes
        assert not unused_classes


class TestIsAssignable(test.bootstrap.IFC4):
    def test_run(self):
        project = self.file.createIfcProject()
        system = self.file.createIfcSystem()
        pump = self.file.createIfcPump()
        assert subject.is_assignable(pump, system)
        assert not subject.is_assignable(project, system)
        assert not subject.is_assignable(pump, project)


class TestGetSystemElements(test.bootstrap.IFC4):
    def test_run(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcPump")
        system = ifcopenshell.api.system.add_system(self.file, ifc_class="IfcSystem")
        ifcopenshell.api.system.assign_system(self.file, products=[element], system=system)
        assert subject.get_system_elements(system) == [element]


class TestGetElementSystems(test.bootstrap.IFC4):
    def test_run(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcPump")
        system = ifcopenshell.api.system.add_system(self.file, ifc_class="IfcSystem")
        ifcopenshell.api.system.assign_system(self.file, products=[element], system=system)
        assert subject.get_element_systems(element) == [system]

    def test_do_not_get_non_services_groups(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcPump")
        ifcopenshell.api.system.assign_system(
            self.file,
            products=[element],
            system=self.file.createIfcGroup(),
        )
        for not_assignable_system_class in ("IfcZone", "IfcStructuralAnalysisModel"):
            with pytest.raises(TypeError):
                ifcopenshell.api.system.assign_system(
                    self.file,
                    products=[element],
                    system=self.file.create_entity(not_assignable_system_class),
                )
        assert not subject.get_element_systems(element)


class TestGetPorts(test.bootstrap.IFC4):
    def test_run(self):
        port = self.file.createIfcDistributionPort()
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcFlowSegment")
        ifcopenshell.api.system.assign_port(self.file, element=element, port=port)
        assert subject.get_ports(element) == [port]


class TestGetPortsIFC2X3(test.bootstrap.IFC2X3, TestGetPorts):
    pass


class TestGetConnectedPort(test.bootstrap.IFC4):
    def test_run(self):
        port1 = ifcopenshell.api.system.add_port(self.file)
        port2 = ifcopenshell.api.system.add_port(self.file)
        ifcopenshell.api.system.connect_port(self.file, port1=port1, port2=port2)
        assert subject.get_connected_port(port1) == port2
        assert subject.get_connected_port(port2) == port1


class TestGetConnectedToFrom(test.bootstrap.IFC4):
    def test_run(self):
        port1 = ifcopenshell.api.system.add_port(self.file)
        element1 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcFlowSegment")
        ifcopenshell.api.system.assign_port(self.file, element=element1, port=port1)

        port2 = ifcopenshell.api.system.add_port(self.file)
        element2 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcFlowSegment")
        ifcopenshell.api.system.assign_port(self.file, element=element2, port=port2)

        ifcopenshell.api.system.connect_port(self.file, port1=port1, port2=port2, direction="SOURCE")
        assert subject.get_connected_to(element1) == [element2]
        assert subject.get_connected_from(element1) == []
        assert subject.get_connected_to(element2) == []
        assert subject.get_connected_from(element2) == [element1]

        ifcopenshell.api.system.connect_port(self.file, port1=port1, port2=port2, direction="SINK")
        assert subject.get_connected_to(element1) == []
        assert subject.get_connected_from(element1) == [element2]
        assert subject.get_connected_to(element2) == [element1]
        assert subject.get_connected_from(element2) == []


class TestGetConnectedToFromIFC2X3(test.bootstrap.IFC2X3, TestGetConnectedToFrom):
    pass
