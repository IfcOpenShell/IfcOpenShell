# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2023 Dion Moult <dion@thinkmoult.com>
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
import ifcopenshell.api


class TestRemoveBoundary(test.bootstrap.IFC4):
    def test_run(self):
        boundary = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcRelSpaceBoundary")
        ifcopenshell.api.run("boundary.remove_boundary", self.file, boundary=boundary)
        assert not self.file.by_type("IfcRelSpaceBoundary")

    def test_removing_connection_geometry(self):
        geometry = self.file.createIfcConnectionSurfaceGeometry()
        boundary = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcRelSpaceBoundary")
        boundary.ConnectionGeometry = geometry
        ifcopenshell.api.run("boundary.remove_boundary", self.file, boundary=boundary)
        assert not self.file.by_type("IfcRelSpaceBoundary")
        assert not self.file.by_type("IfcConnectionSurfaceGeometry")


class TestRemoveBoundaryIFC2X3(test.bootstrap.IFC2X3, TestRemoveBoundary):
    pass
