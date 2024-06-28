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

import test.bootstrap
import ifcopenshell.api.owner


class TestEditActor(test.bootstrap.IFC4):
    def test_editing_an_actor(self):
        person = self.file.createIfcPerson()
        actor = ifcopenshell.api.owner.add_actor(self.file, ifc_class="IfcActor", actor=person)
        ifcopenshell.api.owner.edit_actor(
            self.file,
            actor=actor,
            attributes={"Name": "Name", "Description": "Description", "ObjectType": "ObjectType"},
        )
        assert actor.Name == "Name"
        assert actor.Description == "Description"
        assert actor.ObjectType == "ObjectType"

    def test_editing_an_occupant(self):
        person = self.file.createIfcPerson()
        actor = ifcopenshell.api.owner.add_actor(self.file, ifc_class="IfcOccupant", actor=person)
        ifcopenshell.api.owner.edit_actor(
            self.file,
            actor=actor,
            attributes={
                "Name": "Name",
                "Description": "Description",
                "ObjectType": "ObjectType",
                "PredefinedType": "TENANT",
            },
        )
        assert actor.Name == "Name"
        assert actor.Description == "Description"
        assert actor.ObjectType == "ObjectType"
        assert actor.PredefinedType == "TENANT"


class TestEditActorIFC2X3(test.bootstrap.IFC2X3, TestEditActor):
    pass
