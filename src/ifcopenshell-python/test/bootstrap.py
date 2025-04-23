# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2021 Thomas Krijnen <thomas@aecgeeks.com>
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
import sys

if os.path.abspath(os.path.join(os.path.dirname(__file__), "..")) == sys.path[0]:
    # Don't import ifcopenshell from local directory, because it most likely
    # does not contain the built binary
    sys.path[0:1] = []


import pytest
import ifcopenshell
import ifcopenshell.api.project
import ifcopenshell.api.owner.settings


class IFC4X3:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.file: ifcopenshell.file = ifcopenshell.api.project.create_file(version="IFC4X3")
        ifcopenshell.api.owner.settings.get_user = lambda ifc: (ifc.by_type("IfcPersonAndOrganization") or [None])[0]
        ifcopenshell.api.owner.settings.get_application = lambda ifc: (ifc.by_type("IfcApplication") or [None])[0]
        ifcopenshell.api.pre_listeners = {}
        ifcopenshell.api.post_listeners = {}


class IFC4:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.file: ifcopenshell.file = ifcopenshell.api.project.create_file()
        ifcopenshell.api.owner.settings.get_user = lambda ifc: (ifc.by_type("IfcPersonAndOrganization") or [None])[0]
        ifcopenshell.api.owner.settings.get_application = lambda ifc: (ifc.by_type("IfcApplication") or [None])[0]
        ifcopenshell.api.pre_listeners = {}
        ifcopenshell.api.post_listeners = {}


class IFC2X3:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.file: ifcopenshell.file = ifcopenshell.api.project.create_file(version="IFC2X3")

        def get_user(ifc: ifcopenshell.file) -> ifcopenshell.entity_instance:
            user = next(iter(ifc.by_type("IfcPersonAndOrganization")), None)
            if user:
                return user
            person = ifc.create_entity("IfcPerson")
            organization = ifc.create_entity("IfcOrganization")
            return ifc.create_entity("IfcPersonAndOrganization", ThePerson=person, TheOrganization=organization)

        ifcopenshell.api.owner.settings.get_user = get_user

        def get_application(ifc: ifcopenshell.file) -> ifcopenshell.entity_instance:
            application = next(iter(ifc.by_type("IfcApplication")), None)
            if application:
                return application
            return ifc.create_entity("IfcApplication")

        ifcopenshell.api.owner.settings.get_application = get_application

        ifcopenshell.api.pre_listeners = {}
        ifcopenshell.api.post_listeners = {}


@pytest.fixture(autouse=True)
def file(request):
    return ifcopenshell.open(os.path.join("test/fixtures", request.param))
