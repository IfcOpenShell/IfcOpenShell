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

import ifcopenshell.api.layer
import test.bootstrap


class TestRemoveEmptyLayers(test.bootstrap.IFC4):
    def test_remove_layer_with_no_assigned_items(self):
        layer = self.file.createIfcPresentationLayerAssignment()
        removed = ifcopenshell.api.layer.remove_empty_layers(self.file)
        assert removed == [layer]
        assert not self.file.by_type("IfcPresentationLayerAssignment")

    def test_keep_layer_with_assigned_items(self):
        items = [self.file.createIfcExtrudedAreaSolid() for i in range(2)]
        layer = self.file.createIfcPresentationLayerAssignment()
        ifcopenshell.api.layer.assign_layer(self.file, items=items, layer=layer)

        removed = ifcopenshell.api.layer.remove_empty_layers(self.file)
        assert removed == []
        assert self.file.by_type("IfcPresentationLayerAssignment") == [layer]
        assert set(layer.AssignedItems) == set(items)

    def test_only_empty_layers_are_removed(self):
        items = [self.file.createIfcExtrudedAreaSolid()]
        populated = self.file.createIfcPresentationLayerAssignment(Name="Good")
        ifcopenshell.api.layer.assign_layer(self.file, items=items, layer=populated)
        self.file.createIfcPresentationLayerAssignment(Name="Empty")

        removed = ifcopenshell.api.layer.remove_empty_layers(self.file)
        assert len(removed) == 1
        assert self.file.by_type("IfcPresentationLayerAssignment") == [populated]


class TestRemoveEmptyLayersIFC2X3(test.bootstrap.IFC2X3, TestRemoveEmptyLayers):
    pass
