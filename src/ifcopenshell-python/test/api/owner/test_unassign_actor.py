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
import ifcopenshell.api


class TestUnassignActor(test.bootstrap.IFC4):
    def test_unassigning_an_actor(self):
        wall = self.file.createIfcWall()
        actor = self.file.createIfcActor()
        ifcopenshell.api.run("owner.assign_actor", self.file, relating_actor=actor, related_object=wall)
        ifcopenshell.api.run("owner.unassign_actor", self.file, relating_actor=actor, related_object=wall)
        assert len(self.file.by_type("IfcRelAssignsToActor")) == 0
