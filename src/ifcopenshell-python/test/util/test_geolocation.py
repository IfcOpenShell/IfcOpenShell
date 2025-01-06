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

import numpy as np
import test.bootstrap
import ifcopenshell.api.root
import ifcopenshell.api.context
import ifcopenshell.api.georeference
import ifcopenshell.util.geolocation as subject


class TestXYZ2ENH(test.bootstrap.IFC4):
    def test_converting_from_a_local_xyz_point_to_a_global_easting_northing_height(self):
        assert subject.xyz2enh(0, 0, 0, 0, 0, 0, 1, 0) == (0, 0, 0)
        assert subject.xyz2enh(0, 0, 0, 1, 2, 3, 1, 0) == (1, 2, 3)
        assert subject.xyz2enh(0, 0, 0, 1, 2, 3, 0, 1) == (1, 2, 3)
        assert np.allclose(subject.xyz2enh(1, 1, 0, 1, 2, 3, 1, 0), (2, 3, 3))
        assert np.allclose(subject.xyz2enh(1, 1, 0, 1, 2, 3, 1, 0, 2), (3, 4, 3))
        assert np.allclose(subject.xyz2enh(1, 1, 1, 1, 2, 3, 1, 0, 2, 2, 3, 4), (5, 8, 11))
        assert np.allclose(subject.xyz2enh(1, 1, 0, 1, 2, 3, 0, 1), (0, 3, 3))


class TestENH2XYZ(test.bootstrap.IFC4):
    def test_converting_from_a_global_easting_northing_height_to_a_local_xyz_point(self):
        assert subject.enh2xyz(0, 0, 0, 0, 0, 0, 1, 0) == (0, 0, 0)
        assert subject.enh2xyz(1, 2, 3, 1, 2, 3, 1, 0) == (0, 0, 0)
        assert subject.enh2xyz(1, 2, 3, 1, 2, 3, 0, 1) == (0, 0, 0)
        assert np.allclose(subject.enh2xyz(2, 3, 3, 1, 2, 3, 1, 0), (1, 1, 0))
        assert np.allclose(subject.enh2xyz(3, 4, 3, 1, 2, 3, 1, 0, 2), (1, 1, 0))
        assert np.allclose(subject.enh2xyz(5, 8, 11, 1, 2, 3, 1, 0, 2, 2, 3, 4), (1, 1, 1))
        assert np.allclose(subject.enh2xyz(0, 3, 3, 1, 2, 3, 0, 1), (1, 1, 0))


class TestZ2E(test.bootstrap.IFC4):
    def test_converting_from_a_local_z_to_a_global_elevation(self):
        assert subject.z2e(0) == 0
        assert subject.z2e(0, 0, 1, 1) == 0
        assert subject.z2e(0, 2) == 2
        assert subject.z2e(1, 2) == 3
        assert subject.z2e(1000, 2, 0.001) == 3
        assert np.isclose(subject.z2e(1000, 2, 0.001, 0.9), 2.9)


class TestAutoXYZ2ENH(test.bootstrap.IFC4X3):
    def test_no_georeferencing(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        assert subject.auto_xyz2enh(self.file, 0, 0, 0) == (0, 0, 0)
        assert subject.auto_xyz2enh(self.file, 1, 2, 3) == (1, 2, 3)

    def test_map_conversion(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        ifcopenshell.api.context.add_context(self.file, "Model")
        ifcopenshell.api.georeference.add_georeferencing(self.file)
        ifcopenshell.api.georeference.edit_georeferencing(
            self.file,
            projected_crs={"Name": "EPSG:7856"},
            coordinate_operation={"Eastings": 1, "Northings": 2, "OrthogonalHeight": 3},
        )
        assert subject.auto_xyz2enh(self.file, 0, 0, 0) == (1, 2, 3)
        assert subject.auto_xyz2enh(self.file, 1, 3, 5) == (2, 5, 8)
        ifcopenshell.api.georeference.edit_georeferencing(self.file, coordinate_operation={"Scale": 0.001})
        assert subject.auto_xyz2enh(self.file, 1000, 1000, 0) == (2, 3, 3)
        assert subject.auto_xyz2enh(self.file, 1000, 1000, 0, should_return_in_map_units=False) == (2000, 3000, 3000)
        ifcopenshell.api.georeference.edit_georeferencing(
            self.file, coordinate_operation={"XAxisAbscissa": 0, "XAxisOrdinate": 1}
        )
        assert np.allclose(subject.auto_xyz2enh(self.file, 1000, 1000, 0), (0, 3, 3))

    def test_map_conversion_with_wcs(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        ifcopenshell.api.context.add_context(self.file, "Model")
        ifcopenshell.api.georeference.add_georeferencing(self.file)
        ifcopenshell.api.georeference.edit_georeferencing(
            self.file,
            projected_crs={"Name": "EPSG:7856"},
            coordinate_operation={"Eastings": 1, "Northings": 2, "OrthogonalHeight": 3},
        )
        ifcopenshell.api.georeference.edit_wcs(self.file, x=1, y=2, z=3)
        assert np.allclose(subject.auto_xyz2enh(self.file, 0, 0, 0), (0, 0, 0))
        assert np.allclose(subject.auto_xyz2enh(self.file, 1, 2, 3), (1, 2, 3))
        ifcopenshell.api.georeference.edit_wcs(self.file, x=1, y=1, z=2)
        assert np.allclose(subject.auto_xyz2enh(self.file, 0, 0, 0), (0, 1, 1))
        assert np.allclose(subject.auto_xyz2enh(self.file, 1, 2, 3), (1, 3, 4))

    def test_map_conversion_scaled(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        ifcopenshell.api.context.add_context(self.file, "Model")
        ifcopenshell.api.georeference.add_georeferencing(self.file, ifc_class="IfcMapConversionScaled")
        ifcopenshell.api.georeference.edit_georeferencing(
            self.file,
            projected_crs={"Name": "EPSG:7856"},
            coordinate_operation={"Eastings": 1, "Northings": 2, "OrthogonalHeight": 3},
        )
        assert subject.auto_xyz2enh(self.file, 0, 0, 0) == (1, 2, 3)
        assert subject.auto_xyz2enh(self.file, 1, 3, 5) == (2, 5, 8)
        ifcopenshell.api.georeference.edit_georeferencing(self.file, coordinate_operation={"Scale": 0.001})
        assert subject.auto_xyz2enh(self.file, 1000, 1000, 0) == (2, 3, 3)
        ifcopenshell.api.georeference.edit_georeferencing(
            self.file, coordinate_operation={"FactorX": 0.9, "FactorY": 0.9}
        )
        assert np.allclose(subject.auto_xyz2enh(self.file, 1000, 1000, 0), (1.9, 2.9, 3))

    def test_rigid_operation(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        ifcopenshell.api.context.add_context(self.file, "Model")
        ifcopenshell.api.georeference.add_georeferencing(self.file, ifc_class="IfcRigidOperation")
        ifcopenshell.api.georeference.edit_georeferencing(
            self.file,
            projected_crs={"Name": "EPSG:4258"},
            coordinate_operation={
                "FirstCoordinate": self.file.createIfcPlaneAngleMeasure(1),
                "SecondCoordinate": self.file.createIfcPlaneAngleMeasure(2),
                "Height": 3,
            },
        )
        assert subject.auto_xyz2enh(self.file, 0, 0, 0) == (1, 2, 3)
        assert subject.auto_xyz2enh(self.file, 1, 3, 5) == (2, 5, 8)
        ifcopenshell.api.georeference.edit_georeferencing(
            self.file,
            coordinate_operation={
                "FirstCoordinate": self.file.createIfcLengthMeasure(1),
                "SecondCoordinate": self.file.createIfcLengthMeasure(2),
            },
        )
        assert subject.auto_xyz2enh(self.file, 0, 0, 0) == (1, 2, 3)
        assert subject.auto_xyz2enh(self.file, 1, 3, 5) == (2, 5, 8)


class TestAutoENH2XYZ(test.bootstrap.IFC4X3):
    def test_no_georeferencing(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        assert subject.auto_enh2xyz(self.file, 0, 0, 0) == (0, 0, 0)
        assert subject.auto_enh2xyz(self.file, 1, 2, 3) == (1, 2, 3)

    def test_map_conversion(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        ifcopenshell.api.context.add_context(self.file, "Model")
        ifcopenshell.api.georeference.add_georeferencing(self.file)
        ifcopenshell.api.georeference.edit_georeferencing(
            self.file,
            projected_crs={"Name": "EPSG:7856"},
            coordinate_operation={"Eastings": 1, "Northings": 2, "OrthogonalHeight": 3},
        )
        assert subject.auto_enh2xyz(self.file, 1, 2, 3) == (0, 0, 0)
        assert subject.auto_enh2xyz(self.file, 2, 5, 8) == (1, 3, 5)
        ifcopenshell.api.georeference.edit_georeferencing(self.file, coordinate_operation={"Scale": 0.001})
        assert np.allclose(subject.auto_enh2xyz(self.file, 2, 3, 3), (1000, 1000, 0))
        assert np.allclose(
            subject.auto_enh2xyz(self.file, 2000, 3000, 3000, is_specified_in_map_units=False), (1000, 1000, 0)
        )
        ifcopenshell.api.georeference.edit_georeferencing(
            self.file, coordinate_operation={"XAxisAbscissa": 0, "XAxisOrdinate": 1}
        )
        assert np.allclose(subject.auto_enh2xyz(self.file, 0, 3, 3), (1000, 1000, 0))

    def test_map_conversion_with_wcs(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        ifcopenshell.api.context.add_context(self.file, "Model")
        ifcopenshell.api.georeference.add_georeferencing(self.file)
        ifcopenshell.api.georeference.edit_georeferencing(
            self.file,
            projected_crs={"Name": "EPSG:7856"},
            coordinate_operation={"Eastings": 1, "Northings": 2, "OrthogonalHeight": 3},
        )
        ifcopenshell.api.georeference.edit_wcs(self.file, x=1, y=2, z=3)
        assert np.allclose(subject.auto_enh2xyz(self.file, 0, 0, 0), (0, 0, 0))
        assert np.allclose(subject.auto_enh2xyz(self.file, 1, 2, 3), (1, 2, 3))
        ifcopenshell.api.georeference.edit_wcs(self.file, x=1, y=1, z=2)
        assert np.allclose(subject.auto_enh2xyz(self.file, 0, 1, 1), (0, 0, 0))
        assert np.allclose(subject.auto_enh2xyz(self.file, 1, 3, 4), (1, 2, 3))

    def test_map_conversion_scaled(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        ifcopenshell.api.context.add_context(self.file, "Model")
        ifcopenshell.api.georeference.add_georeferencing(self.file, ifc_class="IfcMapConversionScaled")
        ifcopenshell.api.georeference.edit_georeferencing(
            self.file,
            projected_crs={"Name": "EPSG:7856"},
            coordinate_operation={"Eastings": 1, "Northings": 2, "OrthogonalHeight": 3},
        )
        assert subject.auto_enh2xyz(self.file, 1, 2, 3) == (0, 0, 0)
        assert subject.auto_enh2xyz(self.file, 2, 5, 8) == (1, 3, 5)
        ifcopenshell.api.georeference.edit_georeferencing(self.file, coordinate_operation={"Scale": 0.001})
        assert subject.auto_enh2xyz(self.file, 2, 3, 3) == (1000, 1000, 0)
        ifcopenshell.api.georeference.edit_georeferencing(
            self.file, coordinate_operation={"FactorX": 0.9, "FactorY": 0.9}
        )
        assert np.allclose(subject.auto_enh2xyz(self.file, 1.9, 2.9, 3), (1000, 1000, 0))

    def test_rigid_operation(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        ifcopenshell.api.context.add_context(self.file, "Model")
        ifcopenshell.api.georeference.add_georeferencing(self.file, ifc_class="IfcRigidOperation")
        ifcopenshell.api.georeference.edit_georeferencing(
            self.file,
            projected_crs={"Name": "EPSG:4258"},
            coordinate_operation={
                "FirstCoordinate": self.file.createIfcPlaneAngleMeasure(1),
                "SecondCoordinate": self.file.createIfcPlaneAngleMeasure(2),
                "Height": 3,
            },
        )
        assert subject.auto_enh2xyz(self.file, 1, 2, 3) == (0, 0, 0)
        assert subject.auto_enh2xyz(self.file, 2, 5, 8) == (1, 3, 5)
        ifcopenshell.api.georeference.edit_georeferencing(
            self.file,
            coordinate_operation={
                "FirstCoordinate": self.file.createIfcLengthMeasure(1),
                "SecondCoordinate": self.file.createIfcLengthMeasure(2),
            },
        )
        assert subject.auto_enh2xyz(self.file, 1, 2, 3) == (0, 0, 0)
        assert subject.auto_enh2xyz(self.file, 2, 5, 8) == (1, 3, 5)


class TestAutoZ2E(test.bootstrap.IFC4):
    def test_no_georeferencing(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        assert subject.auto_z2e(self.file, 0) == 0
        assert subject.auto_z2e(self.file, 1) == 1

    def test_map_conversion(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        ifcopenshell.api.context.add_context(self.file, "Model")
        ifcopenshell.api.georeference.add_georeferencing(self.file)
        ifcopenshell.api.georeference.edit_georeferencing(
            self.file,
            projected_crs={"Name": "EPSG:7856"},
            coordinate_operation={"Eastings": 1, "Northings": 2, "OrthogonalHeight": 3},
        )
        assert subject.auto_z2e(self.file, 0) == 3
        assert subject.auto_z2e(self.file, 5) == 8
        ifcopenshell.api.georeference.edit_georeferencing(self.file, coordinate_operation={"Scale": 0.001})
        assert np.isclose(subject.auto_z2e(self.file, 0), 3)
        assert np.isclose(subject.auto_z2e(self.file, 0, should_return_in_map_units=False), 3000)
        ifcopenshell.api.georeference.edit_georeferencing(
            self.file, coordinate_operation={"XAxisAbscissa": 0, "XAxisOrdinate": 1}
        )
        assert np.isclose(subject.auto_z2e(self.file, 0), 3)


class TestLocal2Global(test.bootstrap.IFC4):
    def test_run(self):
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

        m[:, 3][0:3] = [1000, 1000, 0]
        m2[:, 3][0:3] = [2, 3, 3]
        assert np.allclose(subject.local2global(m, 1, 2, 3, 1.0, 0.0, 0.001), m2)

        m[:, 3][0:3] = [1, 1, 0]
        m2[:, 0][0:3] = [0, 1, 0]
        m2[:, 1][0:3] = [-1, 0, 0]
        m2[:, 3][0:3] = [0, 3, 3]
        assert np.allclose(subject.local2global(m, 1, 2, 3, 0.0, 1.0), m2)

        m[:, 3][0:3] = [1, 1, 1]
        m2 = np.eye(4)
        m2[:, 3][0:3] = [5, 8, 11]
        assert np.allclose(subject.local2global(m, 1, 2, 3, 1.0, 0.0, 2, 2, 3, 4), m2)


class TestGlobal2Local(test.bootstrap.IFC4):
    def test_run(self):
        m = np.eye(4)
        m2 = np.eye(4)
        assert np.allclose(subject.global2local(m2, 0, 0, 0, 1.0, 0.0), m)

        m2[:, 3][0:3] = [1, 2, 3]
        assert np.allclose(subject.global2local(m2, 1, 2, 3, 1.0, 0.0), m)

        m2[:, 0][0:3] = [0, 1, 0]
        m2[:, 1][0:3] = [-1, 0, 0]
        assert np.allclose(subject.global2local(m2, 1, 2, 3, 0.0, 1.0), m)

        m[:, 3][0:3] = [1, 1, 0]
        m2 = np.eye(4)
        m2[:, 3][0:3] = [2, 3, 3]
        assert np.allclose(subject.global2local(m2, 1, 2, 3, 1.0, 0.0), m)

        m[:, 3][0:3] = [1000, 1000, 0]
        m2[:, 3][0:3] = [2, 3, 3]
        assert np.allclose(subject.global2local(m2, 1, 2, 3, 1.0, 0.0, 0.001), m)

        m[:, 3][0:3] = [1, 1, 0]
        m2[:, 0][0:3] = [0, 1, 0]
        m2[:, 1][0:3] = [-1, 0, 0]
        m2[:, 3][0:3] = [0, 3, 3]
        assert np.allclose(subject.global2local(m2, 1, 2, 3, 0.0, 1.0), m)

        m[:, 3][0:3] = [1, 1, 1]
        m2 = np.eye(4)
        m2[:, 3][0:3] = [5, 8, 11]
        assert np.allclose(subject.global2local(m2, 1, 2, 3, 1.0, 0.0, 2, 2, 3, 4), m)


class TestAutoLocal2Global(test.bootstrap.IFC4):
    def test_no_georeferencing(self):
        m = np.eye(4)
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        assert np.allclose(subject.auto_local2global(self.file, m), m)
        m[:, 3][0:3] = [1, 2, 3]
        assert np.allclose(subject.auto_local2global(self.file, m), m)

    def test_map_conversion(self):
        m = np.eye(4)
        m2 = np.eye(4)
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        ifcopenshell.api.context.add_context(self.file, "Model")
        ifcopenshell.api.georeference.add_georeferencing(self.file)
        ifcopenshell.api.georeference.edit_georeferencing(
            self.file,
            projected_crs={"Name": "EPSG:7856"},
            coordinate_operation={"Eastings": 1, "Northings": 2, "OrthogonalHeight": 3},
        )
        m2[:, 3][0:3] = [1, 2, 3]
        assert np.allclose(subject.auto_local2global(self.file, m), m2)
        ifcopenshell.api.georeference.edit_georeferencing(self.file, coordinate_operation={"Scale": 0.001})
        assert np.allclose(subject.auto_local2global(self.file, m), m2)
        m2[:, 3][0:3] = [1000, 2000, 3000]
        assert np.allclose(subject.auto_local2global(self.file, m, should_return_in_map_units=False), m2)
        ifcopenshell.api.georeference.edit_georeferencing(
            self.file, coordinate_operation={"XAxisAbscissa": 0, "XAxisOrdinate": 1}
        )
        m[:, 3][0:3] = [1000, 1000, 0]
        m2[:, 0][0:3] = [0, 1, 0]
        m2[:, 1][0:3] = [-1, 0, 0]
        m2[:, 3][0:3] = [0, 3, 3]
        assert np.allclose(subject.auto_local2global(self.file, m), m2)

    def test_map_conversion_with_wcs(self):
        m = np.eye(4)
        m2 = np.eye(4)
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        ifcopenshell.api.context.add_context(self.file, "Model")
        ifcopenshell.api.georeference.add_georeferencing(self.file)
        ifcopenshell.api.georeference.edit_georeferencing(
            self.file,
            projected_crs={"Name": "EPSG:7856"},
            coordinate_operation={"Eastings": 1, "Northings": 2, "OrthogonalHeight": 3},
        )
        ifcopenshell.api.georeference.edit_wcs(self.file, x=1, y=2, z=3)
        assert np.allclose(subject.auto_local2global(self.file, m), m2)
        ifcopenshell.api.georeference.edit_georeferencing(self.file, coordinate_operation={"Scale": 0.001})
        ifcopenshell.api.georeference.edit_wcs(self.file, x=1000, y=1000, z=2000)
        m[:, 3][0:3] = [1000, 2000, 3000]
        m2[:, 3][0:3] = [1, 3, 4]
        assert np.allclose(subject.auto_local2global(self.file, m), m2)


class TestAutoGlobal2Local(test.bootstrap.IFC4):
    def test_no_georeferencing(self):
        m = np.eye(4)
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        assert np.allclose(subject.auto_global2local(self.file, m), m)
        m[:, 3][0:3] = [1, 2, 3]
        assert np.allclose(subject.auto_global2local(self.file, m), m)

    def test_map_conversion(self):
        m = np.eye(4)
        m2 = np.eye(4)
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        ifcopenshell.api.context.add_context(self.file, "Model")
        ifcopenshell.api.georeference.add_georeferencing(self.file)
        ifcopenshell.api.georeference.edit_georeferencing(
            self.file,
            projected_crs={"Name": "EPSG:7856"},
            coordinate_operation={"Eastings": 1, "Northings": 2, "OrthogonalHeight": 3},
        )
        m2[:, 3][0:3] = [1, 2, 3]
        assert np.allclose(subject.auto_global2local(self.file, m2), m)
        ifcopenshell.api.georeference.edit_georeferencing(self.file, coordinate_operation={"Scale": 0.001})
        assert np.allclose(subject.auto_global2local(self.file, m2), m)
        m2[:, 3][0:3] = [1000, 2000, 3000]
        assert np.allclose(subject.auto_global2local(self.file, m2, is_specified_in_map_units=False), m)
        ifcopenshell.api.georeference.edit_georeferencing(
            self.file, coordinate_operation={"XAxisAbscissa": 0, "XAxisOrdinate": 1}
        )
        m[:, 3][0:3] = [1000, 1000, 0]
        m2[:, 0][0:3] = [0, 1, 0]
        m2[:, 1][0:3] = [-1, 0, 0]
        m2[:, 3][0:3] = [0, 3, 3]
        assert np.allclose(subject.auto_global2local(self.file, m2), m)

    def test_map_conversion_with_wcs(self):
        m = np.eye(4)
        m2 = np.eye(4)
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        ifcopenshell.api.context.add_context(self.file, "Model")
        ifcopenshell.api.georeference.add_georeferencing(self.file)
        ifcopenshell.api.georeference.edit_georeferencing(
            self.file,
            projected_crs={"Name": "EPSG:7856"},
            coordinate_operation={"Eastings": 1, "Northings": 2, "OrthogonalHeight": 3},
        )
        ifcopenshell.api.georeference.edit_wcs(self.file, x=1, y=2, z=3)
        assert np.allclose(subject.auto_global2local(self.file, m2), m)
        ifcopenshell.api.georeference.edit_georeferencing(self.file, coordinate_operation={"Scale": 0.001})
        ifcopenshell.api.georeference.edit_wcs(self.file, x=1000, y=1000, z=2000)
        m[:, 3][0:3] = [1000, 2000, 3000]
        m2[:, 3][0:3] = [1, 3, 4]
        assert np.allclose(subject.auto_global2local(self.file, m2), m)


class TestXAxis2Angle(test.bootstrap.IFC4):
    def test_run(self):
        assert subject.xaxis2angle(1, 0) == 0
        assert subject.xaxis2angle(1, 1) == -45
        assert subject.xaxis2angle(-1, 1) == -135
        assert subject.xaxis2angle(1, -1) == 45
        assert subject.xaxis2angle(-1, -1) == 135
        assert np.isclose(subject.xaxis2angle(0.8660254, -0.5), 30)


class TestAngle2XAxis(test.bootstrap.IFC4):
    def test_run(self):
        a = 0.707106781186
        assert np.allclose(subject.angle2xaxis(0), (1, 0))
        assert np.allclose(subject.angle2xaxis(-45), (a, a))
        assert np.allclose(subject.angle2xaxis(-135), (-a, a))
        assert np.allclose(subject.angle2xaxis(45), (a, -a))
        assert np.allclose(subject.angle2xaxis(135), (-a, -a))


class TestYAxis2Angle(test.bootstrap.IFC4):
    def test_run(self):
        assert subject.yaxis2angle(0, 1) == 0
        assert np.isclose(subject.yaxis2angle(-0.5, 0.8660254), 30)
        assert subject.yaxis2angle(1, 1) == -45
        assert subject.yaxis2angle(-1, 1) == 45
        assert subject.yaxis2angle(1, -1) == -135
        assert subject.yaxis2angle(-1, -1) == 135


class TestAngle2YAxis(test.bootstrap.IFC4):
    def test_run(self):
        a = 0.707106781186
        assert np.allclose(subject.angle2yaxis(0), (0, 1))
        assert np.allclose(subject.angle2yaxis(-45), (a, a))
        assert np.allclose(subject.angle2yaxis(45), (-a, a))
        assert np.allclose(subject.angle2yaxis(-135), (a, -a))
        assert np.allclose(subject.angle2yaxis(135), (-a, -a))
