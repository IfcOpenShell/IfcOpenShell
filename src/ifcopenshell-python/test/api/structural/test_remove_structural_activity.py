# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2026 Ryan Schultz
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

import ifcopenshell.api.group
import ifcopenshell.api.root
import ifcopenshell.api.structural
import test.bootstrap


class TestRemoveStructuralActivity(test.bootstrap.IFC4):
    def test_removing_an_activity_keeps_its_load(self):
        point = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcStructuralPointConnection")
        load = ifcopenshell.api.structural.add_structural_load(self.file, ifc_class="IfcStructuralLoadSingleForce")
        group = ifcopenshell.api.structural.add_structural_load_group(self.file)
        activity = ifcopenshell.api.structural.add_structural_activity(
            self.file, ifc_class="IfcStructuralPointAction", applied_load=load, structural_member=point
        )
        other = ifcopenshell.api.structural.add_structural_activity(
            self.file, ifc_class="IfcStructuralPointAction", applied_load=load, structural_member=point
        )
        ifcopenshell.api.group.assign_group(self.file, products=[activity, other], group=group)
        ifcopenshell.api.structural.remove_structural_activity(self.file, activity=activity)
        assert self.file.by_type("IfcStructuralActivity") == (other,)
        rels = self.file.by_type("IfcRelConnectsStructuralActivity")
        assert [r.RelatedStructuralActivity for r in rels] == [other]
        assert group.IsGroupedBy[0].RelatedObjects == (other,)
        assert self.file.by_type("IfcStructuralLoad") == (load,)


class TestRemoveStructuralActivityIFC2X3(test.bootstrap.IFC2X3, TestRemoveStructuralActivity):
    pass
