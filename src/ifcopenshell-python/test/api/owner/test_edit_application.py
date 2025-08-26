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
import ifcopenshell.api.owner


class TestEditApplication(test.bootstrap.IFC4):
    def test_editing_a_application(self):
        application = self.file.create_entity("IfcApplication")
        organization = self.file.create_entity("IfcOrganization")
        attributes = {
            "ApplicationDeveloper": organization,
            "Version": "v001",
            "ApplicationFullName": "App Name",
            "ApplicationIdentifier": "App Name",
        }
        ifcopenshell.api.owner.edit_application(
            self.file,
            application=application,
            attributes=attributes,
        )
        for attr, value in attributes.items():
            assert getattr(application, attr) == value


class TestEditApplicationIFC2X3(test.bootstrap.IFC2X3, TestEditApplication):
    pass


class TestEditApplicationIFC4X3(test.bootstrap.IFC4X3, TestEditApplication):
    pass
