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
import ifcopenshell.api.root
import ifcopenshell.api.boundary


class TestCopyBoundary(test.bootstrap.IFC4):
    def test_run(self):
        boundary = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcRelSpaceBoundary")
        boundary2 = ifcopenshell.api.boundary.copy_boundary(self.file, boundary=boundary)
        assert boundary2.is_a("IfcRelSpaceBoundary")
        assert boundary2.GlobalId != boundary.GlobalId

    def test_copying_connection_geometry(self):
        geometry = self.file.createIfcConnectionSurfaceGeometry()
        boundary = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcRelSpaceBoundary")
        boundary.ConnectionGeometry = geometry
        boundary2 = ifcopenshell.api.boundary.copy_boundary(self.file, boundary=boundary)
        assert boundary2.ConnectionGeometry.is_a("IfcConnectionSurfaceGeometry")
        assert boundary2.ConnectionGeometry != boundary.ConnectionGeometry


class TestCopyBoundaryIFC2X3(test.bootstrap.IFC2X3, TestCopyBoundary):
    pass
