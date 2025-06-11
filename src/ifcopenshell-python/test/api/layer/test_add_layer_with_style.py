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


class TestAddLayerWithStyle(test.bootstrap.IFC4):
    def test_add_layer_no_arguments(self):
        layer = ifcopenshell.api.layer.add_layer_with_style(self.file)
        assert layer.Name == "Unnamed"
        assert layer.LayerOn == "UNKNOWN"
        assert layer.LayerFrozen == "UNKNOWN"
        assert layer.LayerBlocked == "UNKNOWN"
        assert layer.LayerStyles == ()

    def test_assign_all_arguments(self):
        curve_style = self.file.create_entity("IfcCurveStyle")
        layer = ifcopenshell.api.layer.add_layer_with_style(
            self.file, name="Name", on=True, frozen=True, blocked=True, styles=(curve_style,)
        )
        assert layer.Name == "Name"
        assert layer.LayerOn == True
        assert layer.LayerFrozen == True
        assert layer.LayerBlocked == True
        assert layer.LayerStyles == (curve_style,)


class TestAddLayerWithStyleIFC2X3(test.bootstrap.IFC2X3, TestAddLayerWithStyle):
    pass
