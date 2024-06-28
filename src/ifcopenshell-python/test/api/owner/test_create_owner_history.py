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
import pytest
import test.bootstrap
import ifcopenshell.api
import ifcopenshell.api.owner.settings


class TestCreateOwnerHistory(test.bootstrap.IFC4):
    def test_creating_nothing_if_no_user_or_application_is_available(self):
        if self.file.schema != "IFC2X3":
            history = ifcopenshell.api.owner.create_owner_history(self.file)
            assert history is None
        else:
            ifcopenshell.api.owner.settings.factory_reset()
            # create new file as bootstrap is creating users in ifc2x3 by default
            file = ifcopenshell.file(schema="IFC2X3")
            with pytest.raises(Exception) as e:
                ifcopenshell.api.owner.create_owner_history(file)
            assert "Please create a user to continue" in str(e.value)
            ifcopenshell.api.owner.settings.restore()

    def test_creating_a_history_using_a_specified_user_and_application(self):
        ifcopenshell.api.owner.settings.factory_reset()

        user = self.file.createIfcPersonAndOrganization()
        application = self.file.createIfcApplication()
        ifcopenshell.api.owner.settings.get_user = lambda x: user
        ifcopenshell.api.owner.settings.get_application = lambda x: application
        history = ifcopenshell.api.owner.create_owner_history(self.file)
        ifcopenshell.api.owner.settings.restore()

        assert history.is_a("IfcOwnerHistory")
        assert history.OwningUser == user
        assert history.OwningApplication == application
        assert history.State == "READWRITE"
        assert history.ChangeAction == "ADDED"
        assert abs(time.time() - history.LastModifiedDate) < 5
        assert history.LastModifyingUser == user
        assert history.LastModifyingApplication == application
        assert abs(time.time() - history.CreationDate) < 5


class TestCreateOwnerHistoryIFC2X3(test.bootstrap.IFC2X3, TestCreateOwnerHistory):
    pass
