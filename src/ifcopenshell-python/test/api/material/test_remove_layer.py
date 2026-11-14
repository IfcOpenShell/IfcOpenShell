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


class TestRemoveLayerIFC2X3(test.bootstrap.IFC2X3):
    def test_removing_a_non_last_layer(self):
        material_set = ifcopenshell.api.material.add_material_set(self.file, set_type="IfcMaterialLayerSet")
        material = ifcopenshell.api.material.add_material(self.file)
        layer1 = ifcopenshell.api.material.add_layer(self.file, layer_set=material_set, material=material)
        layer2 = ifcopenshell.api.material.add_layer(self.file, layer_set=material_set, material=material)
        ifcopenshell.api.material.remove_layer(self.file, layer=layer2)
        assert material_set.MaterialLayers == (layer1,)

    def test_removing_the_last_layer_removes_the_whole_set(self):
        material_set = ifcopenshell.api.material.add_material_set(self.file, set_type="IfcMaterialLayerSet")
        material = ifcopenshell.api.material.add_material(self.file)
        layer = ifcopenshell.api.material.add_layer(self.file, layer_set=material_set, material=material)
        ifcopenshell.api.material.remove_layer(self.file, layer=layer)
        assert len(self.file.by_type("IfcMaterialLayerSet")) == 0
        assert len(self.file.by_type("IfcMaterialLayer")) == 0
        assert len(self.file.by_type("IfcMaterial")) == 1


class TestRemoveLayerIFC4(test.bootstrap.IFC4, TestRemoveLayerIFC2X3):
    pass
