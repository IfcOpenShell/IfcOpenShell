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

import pytest
import numpy as np
import test.bootstrap
import ifcopenshell.util.geolocation as subject


class TestXYZ2ENH(test.bootstrap.IFC4):
    def test_converting_from_a_local_xyz_point_to_a_global_easting_northing_height(self):
        assert subject.xyz2enh(0, 0, 0, 0, 0, 0, 1, 0) == (0, 0, 0)
        assert subject.xyz2enh(0, 0, 0, 1, 2, 3, 1, 0) == (1, 2, 3)
        assert subject.xyz2enh(0, 0, 0, 1, 2, 3, 0, 1) == (1, 2, 3)
        assert np.allclose(subject.xyz2enh(1, 1, 0, 1, 2, 3, 1, 0), (2, 3, 3))
        assert np.allclose(subject.xyz2enh(1, 1, 0, 1, 2, 3, 1, 0, 2), (3, 4, 3))
        assert np.allclose(subject.xyz2enh(1, 1, 0, 1, 2, 3, 0, 1), (0, 3, 3))


class TestXYZ2ENHIfc4X3(test.bootstrap.IFC4):
    def test_converting_from_a_local_xyz_point_to_a_global_easting_northing_height(self):
        assert subject.xyz2enh_ifc4x3(0, 0, 0, 0, 0, 0, 1, 0) == (0, 0, 0)
        assert subject.xyz2enh_ifc4x3(0, 0, 0, 1, 2, 3, 1, 0) == (1, 2, 3)
        assert subject.xyz2enh_ifc4x3(0, 0, 0, 1, 2, 3, 0, 1) == (1, 2, 3)
        assert np.allclose(subject.xyz2enh_ifc4x3(1, 1, 0, 1, 2, 3, 1, 0), (2, 3, 3))
        assert np.allclose(subject.xyz2enh_ifc4x3(1, 1, 0, 1, 2, 3, 1, 0, 2), (3, 4, 3))
        assert np.allclose(subject.xyz2enh_ifc4x3(1, 1, 1, 1, 2, 3, 1, 0, 2, 2, 3, 4), (5, 8, 11))
        assert np.allclose(subject.xyz2enh_ifc4x3(1, 1, 0, 1, 2, 3, 0, 1), (0, 3, 3))


class TestLocal2Global(test.bootstrap.IFC4):
    def test_converting_from_a_local_matrix_to_a_global_matrix(self):
        m = np.eye(4)
        m2 = np.eye(4)
        assert np.allclose(subject.local2global(m, 0, 0, 0, 1.0, 0.0), m2)

        m2[:, 3][0:3] = [1, 2, 3]
        assert np.allclose(subject.local2global(m, 1, 2, 3, 1.0, 0.0), m2)

        m2[:, 0][0:3] = [0, 1, 0]
        m2[:, 1][0:3] = [-1, 0, 0]
        assert np.allclose(subject.local2global(m, 1, 2, 3, 0.0, 1.0), m2)

        m[:, 3][0:3] = [1, 1, 0]
        m2 = np.eye(4)
        m2[:, 3][0:3] = [2, 3, 3]
        assert np.allclose(subject.local2global(m, 1, 2, 3, 1.0, 0.0), m2)

        m2[:, 3][0:3] = [3, 4, 3]
        assert np.allclose(subject.local2global(m, 1, 2, 3, 1.0, 0.0, 2), m2)

        m2[:, 0][0:3] = [0, 1, 0]
        m2[:, 1][0:3] = [-1, 0, 0]
        m2[:, 3][0:3] = [0, 3, 3]
        assert np.allclose(subject.local2global(m, 1, 2, 3, 0.0, 1.0), m2)


class TestLocal2GlobalIfc4X3(test.bootstrap.IFC4):
    def test_converting_from_a_local_matrix_to_a_global_matrix(self):
        m = np.eye(4)
        m2 = np.eye(4)
        assert np.allclose(subject.local2global_ifc4x3(m, 0, 0, 0, 1.0, 0.0), m2)

        m2[:, 3][0:3] = [1, 2, 3]
        assert np.allclose(subject.local2global_ifc4x3(m, 1, 2, 3, 1.0, 0.0), m2)

        m2[:, 0][0:3] = [0, 1, 0]
        m2[:, 1][0:3] = [-1, 0, 0]
        assert np.allclose(subject.local2global_ifc4x3(m, 1, 2, 3, 0.0, 1.0), m2)

        m[:, 3][0:3] = [1, 1, 0]
        m2 = np.eye(4)
        m2[:, 3][0:3] = [2, 3, 3]
        assert np.allclose(subject.local2global_ifc4x3(m, 1, 2, 3, 1.0, 0.0), m2)

        m2[:, 3][0:3] = [3, 4, 3]
        assert np.allclose(subject.local2global_ifc4x3(m, 1, 2, 3, 1.0, 0.0, 2), m2)

        m2[:, 0][0:3] = [0, 1, 0]
        m2[:, 1][0:3] = [-1, 0, 0]
        m2[:, 3][0:3] = [0, 3, 3]
        assert np.allclose(subject.local2global_ifc4x3(m, 1, 2, 3, 0.0, 1.0), m2)

        m[:, 3][0:3] = [1, 1, 1]
        m2 = np.eye(4)
        m2[:, 3][0:3] = [5, 8, 11]
        assert np.allclose(subject.local2global_ifc4x3(m, 1, 2, 3, 1.0, 0.0, 2, 2, 3, 4), m2)
