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

import time
import test.bootstrap
import ifcopenshell.api


class TestCreateOwnerHistory(test.bootstrap.IFC4):
    def test_creating_nothing_if_no_user_or_application_is_available(self):
        history = ifcopenshell.api.run("owner.create_owner_history", self.file)
        assert history is None

    def test_creating_a_history_using_a_specified_user_and_application(self):
        old_get_user = ifcopenshell.api.owner.settings.get_user
        old_get_application = ifcopenshell.api.owner.settings.get_application
        user = self.file.createIfcPersonAndOrganization()
        application = self.file.createIfcApplication()
        ifcopenshell.api.owner.settings.get_user = lambda x: user
        ifcopenshell.api.owner.settings.get_application = lambda x: application
        history = ifcopenshell.api.run("owner.create_owner_history", self.file)
        ifcopenshell.api.owner.settings.get_user = old_get_user
        ifcopenshell.api.owner.settings.get_application = old_get_application
        assert history.is_a("IfcOwnerHistory")
        assert history.OwningUser == user
        assert history.OwningApplication == application
        assert history.State == "READWRITE"
        assert history.ChangeAction == "ADDED"
        assert abs(time.time() - history.LastModifiedDate) < 5
        assert history.LastModifyingUser == user
        assert history.LastModifyingApplication == application
        assert abs(time.time() - history.CreationDate) < 5
