# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
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

# This file was generated with the assistance of an AI coding tool.

import ifcopenshell

import bonsai.tool as tool
from bonsai.bim.ifc import IfcStore
from test.bim.bootstrap import NewFile


def new_wall():
    ifc = ifcopenshell.file()
    tool.Ifc.set(ifc)
    return ifc, ifc.createIfcWall(ifcopenshell.guid.new(), Name="Before")


class TestTrackTransactionOutsideOperator(NewFile):
    def test_undo_reverts_a_rename_made_outside_an_operator(self):
        ifc, wall = new_wall()
        key_before = IfcStore.last_transaction
        with IfcStore.track_transaction_outside_operator("Rename"):
            wall.Name = "After"
        assert wall.Name == "After"
        assert IfcStore.last_transaction != key_before
        IfcStore.undo(until_key=key_before)
        assert wall.Name == "Before"

    def test_redo_reapplies_the_rename(self):
        ifc, wall = new_wall()
        key_before = IfcStore.last_transaction
        with IfcStore.track_transaction_outside_operator("Rename"):
            wall.Name = "After"
        key = IfcStore.last_transaction
        IfcStore.undo(until_key=key_before)
        IfcStore.redo(until_key=key)
        assert wall.Name == "After"

    def test_an_edit_inside_an_ongoing_transaction_joins_it(self):
        ifc, wall = new_wall()
        key_before = IfcStore.last_transaction
        ifc.begin_transaction()
        with IfcStore.track_transaction_outside_operator("Rename"):
            wall.Name = "After"
        ifc.end_transaction()
        assert IfcStore.last_transaction == key_before
