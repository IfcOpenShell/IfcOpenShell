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

# This file was generated with the assistance of an AI coding tool.

import ifcopenshell.api.material
import test.bootstrap


class TestRemoveListItemIFC2X3(test.bootstrap.IFC2X3):
    def test_removing_a_non_last_item(self):
        material_list = ifcopenshell.api.material.add_material_set(self.file, set_type="IfcMaterialList")
        material1 = ifcopenshell.api.material.add_material(self.file)
        material2 = ifcopenshell.api.material.add_material(self.file)
        ifcopenshell.api.material.add_list_item(self.file, material_list=material_list, material=material1)
        ifcopenshell.api.material.add_list_item(self.file, material_list=material_list, material=material2)
        ifcopenshell.api.material.remove_list_item(self.file, material_list=material_list, material_index=1)
        assert material_list.Materials == (material1,)

    def test_removing_the_last_item_removes_the_whole_list(self):
        material_list = ifcopenshell.api.material.add_material_set(self.file, set_type="IfcMaterialList")
        material = ifcopenshell.api.material.add_material(self.file)
        ifcopenshell.api.material.add_list_item(self.file, material_list=material_list, material=material)
        ifcopenshell.api.material.remove_list_item(self.file, material_list=material_list, material_index=0)
        assert len(self.file.by_type("IfcMaterialList")) == 0
        assert len(self.file.by_type("IfcMaterial")) == 1


class TestRemoveListItemIFC4(test.bootstrap.IFC4, TestRemoveListItemIFC2X3):
    pass
