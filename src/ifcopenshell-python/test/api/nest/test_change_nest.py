# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2026 IfcOpenShell contributors
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

# This file was generated with the assistance of an AI coding tool.

import ifcopenshell.api.nest
import ifcopenshell.api.root
import ifcopenshell.util.element
import test.bootstrap


class TestChangeNest(test.bootstrap.IFC4):
    def test_nesting_an_item_that_had_no_previous_parent(self):
        # A root item, one that isn't nested under anything yet, must still
        # be assignable to a new parent.
        item = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcTask")
        new_parent = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcTask")
        ifcopenshell.api.nest.change_nest(self.file, item=item, new_parent=new_parent)
        assert ifcopenshell.util.element.get_nest(item) == new_parent

    def test_moving_an_item_to_a_new_parent(self):
        old_parent = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcTask")
        new_parent = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcTask")
        item = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcTask")
        ifcopenshell.api.nest.assign_object(self.file, related_objects=[item], relating_object=old_parent)
        ifcopenshell.api.nest.change_nest(self.file, item=item, new_parent=new_parent)
        assert ifcopenshell.util.element.get_nest(item) == new_parent
        assert not old_parent.IsNestedBy
