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
import ifcopenshell.api.layer


class TestAssignLayer(test.bootstrap.IFC4):
    def test_assign_layer_to_items(self):
        items = [self.file.createIfcExtrudedAreaSolid() for i in range(2)]
        layer = self.file.createIfcPresentationLayerAssignment()

        ifcopenshell.api.layer.assign_layer(self.file, items=items, layer=layer)
        assert len(layer.AssignedItems) == 2
        assert set(layer.AssignedItems) == set(items)

    def test_assign_additional_items(self):
        items = [self.file.createIfcExtrudedAreaSolid() for i in range(4)]
        layer = self.file.createIfcPresentationLayerAssignment()

        ifcopenshell.api.layer.assign_layer(self.file, items=items[:2], layer=layer)
        ifcopenshell.api.layer.assign_layer(self.file, items=items[2:], layer=layer)
        assert len(layer.AssignedItems) == 4
        assert set(layer.AssignedItems) == set(items)


class TestAssignLayerIFC2X3(test.bootstrap.IFC2X3, TestAssignLayer):
    pass
