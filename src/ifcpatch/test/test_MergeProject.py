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

import ifcpatch
import ifcopenshell
import ifcopenshell.api.context
import ifcopenshell.api.geometry
import ifcopenshell.api.georeference
import ifcopenshell.geom
import ifcopenshell.util.geolocation
import ifcopenshell.util.placement
import ifcopenshell.util.representation
import ifcopenshell.util.shape
import ifcopenshell.util.shape_builder
import test.bootstrap
import tempfile
import numpy as np
from pathlib import Path
from typing import Optional


class TestMergeProjects(test.bootstrap.IFC4):
    def setup_project(self, ifc_file: Optional[ifcopenshell.file] = None):
        prefix = None if ifc_file else "MILLI"
        if ifc_file is None:
            ifc_file = ifcopenshell.file(schema=self.file.schema)

        ifcopenshell.api.run("root.create_entity", ifc_file, ifc_class="IfcProject")
        unit = ifcopenshell.api.run("unit.add_si_unit", ifc_file, unit_type="LENGTHUNIT", prefix=prefix)
        ifcopenshell.api.run("unit.assign_unit", ifc_file, units=[unit])
        model = ifcopenshell.api.context.add_context(ifc_file, "Model")
        ifcopenshell.api.context.add_context(ifc_file, "Model", "Body", "MODEL_VIEW", parent=model)

        matrix = np.eye(4)
        matrix[:, 3] = (1, 2, 3, 1)
        wall = ifcopenshell.api.run("root.create_entity", ifc_file, ifc_class="IfcWall")
        ifcopenshell.api.run("geometry.edit_object_placement", ifc_file, product=wall, matrix=matrix, is_si=True)
        return ifc_file

    def test_run(self):
        self.file = self.setup_project(self.file)
        second_file = self.setup_project()
        temp_path = Path(tempfile.gettempdir()) / "second.ifc"
        second_file.write(temp_path)
        output = ifcpatch.execute({"file": self.file, "recipe": "MergeProjects", "arguments": [str(temp_path)]})

        assert self.file == output
        assert len(output.by_type("IfcWall")) == 2
        wall1, wall2 = output.by_type("IfcWall")

        # test that units are converted
        placement1 = ifcopenshell.util.placement.get_local_placement(wall1.ObjectPlacement)
        placement2 = ifcopenshell.util.placement.get_local_placement(wall2.ObjectPlacement)
        to_tuple = lambda arr: tuple(map(tuple, arr))
        matrix = np.eye(4)
        matrix[:, 3] = (1, 2, 3, 1)
        assert to_tuple(placement1) == to_tuple(placement2) == to_tuple(matrix)

    def test_reusing_geometric_contexts(self):
        self.file = self.setup_project(self.file)
        second_file = self.setup_project()
        output = ifcpatch.execute({"file": self.file, "recipe": "MergeProjects", "arguments": [second_file]})
        assert len(output.by_type("IfcGeometricRepresentationContext")) == 2

    def test_using_the_georeferencing_of_the_original_project(self):
        if self.file.schema == "IFC2X3":
            return
        self.file = self.setup_project(self.file)
        second_file = self.setup_project()
        ifcopenshell.api.georeference.add_georeferencing(self.file)
        ifcopenshell.api.georeference.add_georeferencing(second_file)
        output = ifcpatch.execute({"file": self.file, "recipe": "MergeProjects", "arguments": [second_file]})
        assert len(output.by_type("IfcProjectedCRS")) == 1
        assert len(output.by_type("IfcMapConversion")) == 1

    def test_shifting_the_other_project_to_match_the_original_project_origin(self):
        self.file = self.setup_project(self.file)
        second_file = self.setup_project()
        ifcopenshell.api.georeference.add_georeferencing(self.file)
        xaa1, xao1 = ifcopenshell.util.geolocation.angle2xaxis(10)
        ifcopenshell.api.georeference.edit_georeferencing(
            self.file,
            coordinate_operation={"Eastings": 10, "Northings": 20, "XAxisAbscissa": xaa1, "XAxisOrdinate": xao1},
            projected_crs={"Name": "EPSG:1234"},
        )
        ifcopenshell.api.georeference.add_georeferencing(second_file)
        xaa, xao = ifcopenshell.util.geolocation.angle2xaxis(30)
        ifcopenshell.api.georeference.edit_georeferencing(
            second_file,
            coordinate_operation={"Eastings": 30000, "Northings": 40000, "XAxisAbscissa": xaa, "XAxisOrdinate": xao},
            projected_crs={"Name": "EPSG:0"},
        )

        builder1 = ifcopenshell.util.shape_builder.ShapeBuilder(self.file)
        builder2 = ifcopenshell.util.shape_builder.ShapeBuilder(second_file)
        o1 = builder1.create_axis2_placement_3d()
        o2 = builder2.create_axis2_placement_3d()
        body1 = ifcopenshell.util.representation.get_context(self.file, "Model", "Body", "MODEL_VIEW")
        body2 = ifcopenshell.util.representation.get_context(second_file, "Model", "Body", "MODEL_VIEW")

        # Original file is in meters
        wall1 = self.file.by_type("IfcWall")[0]
        m1 = ifcopenshell.util.placement.get_local_placement(wall1.ObjectPlacement)
        assert np.allclose(m1[:, 3], (1, 2, 3, 1))
        global_m1 = ifcopenshell.util.geolocation.auto_local2global(self.file, m1, should_return_in_map_units=False)
        assert np.allclose(global_m1[:, 3], (11.332, 21.796, 3, 1))

        block = self.file.createIfcCsgSolid(self.file.createIfcBlock(o1, 2, 2, 2))
        rep = builder1.get_representation(context=body1, items=[block])
        ifcopenshell.api.geometry.assign_representation(self.file, product=wall1, representation=rep)
        shape = ifcopenshell.geom.create_shape(ifcopenshell.geom.settings(), wall1)
        verts = ifcopenshell.util.shape.get_shape_vertices(shape, shape.geometry)
        assert np.any(np.all(np.isclose(np.array((1.0, 2.0, 3.0)), verts), axis=1))
        assert np.any(np.all(np.isclose(np.array((3.0, 4.0, 5.0)), verts), axis=1))

        # Second file is in millimeters with a different false origin
        wall1 = second_file.by_type("IfcWall")[0]
        m1 = ifcopenshell.util.placement.get_local_placement(wall1.ObjectPlacement)
        assert np.allclose(m1[:, 3], (1000, 2000, 3000, 1))
        global_m1 = ifcopenshell.util.geolocation.auto_local2global(second_file, m1, should_return_in_map_units=False)
        assert np.allclose(global_m1[:, 3], (31866, 41232, 3000, 1))

        block = second_file.createIfcCsgSolid(second_file.createIfcBlock(o2, 2000, 2000, 2000))
        rep = builder2.get_representation(context=body2, items=[block])
        ifcopenshell.api.geometry.assign_representation(second_file, product=wall1, representation=rep)
        shape = ifcopenshell.geom.create_shape(ifcopenshell.geom.settings(), wall1)
        verts = ifcopenshell.util.shape.get_shape_vertices(shape, shape.geometry)
        assert np.any(np.all(np.isclose(np.array((1.0, 2.0, 3.0)), verts), axis=1))
        assert np.any(np.all(np.isclose(np.array((3.0, 4.0, 5.0)), verts), axis=1))

        output = ifcpatch.execute({"file": self.file, "recipe": "MergeProjects", "arguments": [second_file]})

        # In the future we may use proj to support reprojection from different CRSes. For now... nope!
        if self.file.schema != "IFC2X3":
            assert output.by_type("IfcProjectedCRS")[0].Name == "EPSG:1234"

        # The results should be in meters with the false origin of the original file
        params = ifcopenshell.util.geolocation.get_helmert_transformation_parameters(output)
        assert params.e == 10
        assert params.n == 20
        assert params.xaa == xaa1
        assert params.xao == xao1

        wall1, wall2 = output.by_type("IfcWall")
        m1 = ifcopenshell.util.placement.get_local_placement(wall1.ObjectPlacement)
        m2 = ifcopenshell.util.placement.get_local_placement(wall2.ObjectPlacement)
        assert np.allclose(m1[:, 3], (1, 2, 3, 1))
        # assert np.allclose(m2[:, 3], (8.321, 29.321, 3, 1), atol=1e-3)
        assert np.allclose(m2[:, 3], (17.847, 24.707, 3.0, 1.0), atol=1e-3)

        shape = ifcopenshell.geom.create_shape(ifcopenshell.geom.settings(), wall1)
        verts = ifcopenshell.util.shape.get_shape_vertices(shape, shape.geometry)
        assert np.any(np.all(np.isclose(np.array((1.0, 2.0, 3.0)), verts), axis=1))
        assert np.any(np.all(np.isclose(np.array((3.0, 4.0, 5.0)), verts), axis=1))

        shape = ifcopenshell.geom.create_shape(ifcopenshell.geom.settings(), wall2)
        verts = ifcopenshell.util.shape.get_shape_vertices(shape, shape.geometry)
        assert np.any(np.all(np.isclose(np.array((17.847, 24.707, 3.0)), verts, atol=1e-3), axis=1))
        assert np.any(np.all(np.isclose(np.array((20.410, 25.902, 5.0)), verts, atol=1e-3), axis=1))


class TestMergeProjectsIFC2X3(test.bootstrap.IFC2X3, TestMergeProjects):
    pass
