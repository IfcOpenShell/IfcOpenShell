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

import numpy as np
import test.bootstrap
import ifcopenshell.api.root
import ifcopenshell.api.context
import ifcopenshell.api.georeference
import ifcopenshell.util.geolocation


class TestEditTrueNorth(test.bootstrap.IFC4):
    def test_editing_true_north(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        model = ifcopenshell.api.context.add_context(self.file, "Model")
        plan = ifcopenshell.api.context.add_context(self.file, "Plan")
        ifcopenshell.api.georeference.edit_true_north(self.file, true_north=[0.0, 1.0])
        assert model.TrueNorth[0] == (0.0, 1.0)
        assert plan.TrueNorth[0] == (0.0, 1.0)
        ifcopenshell.api.georeference.edit_true_north(self.file, true_north=[-0.5, 0.8660254])
        assert np.isclose(ifcopenshell.util.geolocation.get_true_north(self.file), 30)
        ifcopenshell.api.georeference.edit_true_north(self.file, true_north=30)
        assert np.isclose(ifcopenshell.util.geolocation.get_true_north(self.file), 30)
