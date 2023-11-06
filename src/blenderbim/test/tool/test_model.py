# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
#
# This file is part of BlenderBIM Add-on.
#
# BlenderBIM Add-on is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BlenderBIM Add-on is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with BlenderBIM Add-on.  If not, see <http://www.gnu.org/licenses/>.

import bpy
import ifcopenshell
import blenderbim.core.tool
import blenderbim.tool as tool
import numpy as np
from test.bim.bootstrap import NewFile
from blenderbim.tool.model import Model as subject
from ifcopenshell.util.shape_builder import V


class TestImplementsTool(NewFile):
    def test_run(self):
        assert isinstance(subject(), blenderbim.core.tool.Model)


class TestGenerateOccurrenceName(NewFile):
    def test_generating_based_on_class(self):
        ifc = ifcopenshell.file()
        element_type = ifc.createIfcWallType(Name="Foobar")
        bpy.context.scene.BIMModelProperties.occurrence_name_style = "CLASS"
        assert subject.generate_occurrence_name(element_type, "IfcWall") == "Wall"

    def test_generating_based_on_type_name(self):
        ifc = ifcopenshell.file()
        element_type = ifc.createIfcWallType()
        bpy.context.scene.BIMModelProperties.occurrence_name_style = "TYPE"
        assert subject.generate_occurrence_name(element_type, "IfcWall") == "Unnamed"
        element_type.Name = "Foobar"
        assert subject.generate_occurrence_name(element_type, "IfcWall") == "Foobar"

    def test_generating_based_on_a_custom_function(self):
        ifc = ifcopenshell.file()
        element_type = ifc.createIfcWallType()
        bpy.context.scene.BIMModelProperties.occurrence_name_style = "CUSTOM"
        bpy.context.scene.BIMModelProperties.occurrence_name_function = '"Foobar"'
        assert subject.generate_occurrence_name(element_type, "IfcWall") == "Foobar"


class TestGetManualBooleans(NewFile):
    def test_get_manual_booleans(self):
        clippings = [
            {
                "type": "IfcBooleanClippingResult",
                "operand_type": "IfcHalfSpaceSolid",
                "matrix": np.eye(4).tolist(),
            },
            {
                "type": "IfcBooleanResult",
                "operand_type": "IfcHalfSpaceSolid",
                "matrix": np.eye(4).tolist(),
            },
        ]

        ifc = ifcopenshell.file()
        self.ifc = ifc
        tool.Ifc.set(ifc)
        ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcProject")
        length = ifcopenshell.api.run("unit.add_si_unit", ifc, unit_type="LENGTHUNIT")
        ifcopenshell.api.run("unit.assign_unit", ifc, units=[length])
        ifcopenshell.api.run("unit.assign_unit", ifc)
        element = ifc.createIfcColumn()
        hea100 = ifc.create_entity(
            "IfcIShapeProfileDef",
            ProfileName="HEA100",
            ProfileType="AREA",
            OverallWidth=100,
            OverallDepth=96,
            WebThickness=5,
            FlangeThickness=8,
            FilletRadius=12,
        )
        model3d = ifcopenshell.api.run("context.add_context", ifc, context_type="Model")
        body = ifcopenshell.api.run(
            "context.add_context",
            ifc,
            context_type="Model",
            context_identifier="Body",
            target_view="MODEL_VIEW",
            parent=model3d,
        )
        representation = ifcopenshell.api.run(
            "geometry.add_profile_representation", ifc, context=body, profile=hea100, depth=5, clippings=clippings
        )
        ifcopenshell.api.run("geometry.assign_representation", ifc, product=element, representation=representation)

        booleans = subject.get_booleans(element)
        assert len(booleans) == 2
        assert len(subject.get_manual_booleans(element)) == 0
        subject.mark_manual_booleans(element, booleans)
        assert len(subject.get_manual_booleans(element)) == 2


class TestGenerateStair2DProfile(NewFile):
    def compare_data(self, generated_profile, expected_profile):
        verts_gen, edges_gen, faces_gen = generated_profile
        verts, edges, faces = expected_profile

        assert np.all(edges == np.array(edges_gen))
        assert faces == tuple(tuple(face) for face in faces_gen)
        for vert, vert_gen in zip(verts, verts_gen, strict=True):
            assert tool.Cad.are_vectors_equal(vert, vert_gen, 0.01)

    def test_create_concrete_stair(self):
        kwargs = {
            "base_slab_depth": 0.25,
            "has_top_nib": False,
            "height": 1.0,
            "number_of_treads": 3,
            "stair_type": "CONCRETE",
            "top_slab_depth": 0.25,
            "tread_depth": 0.25,
            "tread_run": 0.3,
            "width": 1.2,
        }
        verts_data = (
            V(0.0, 0, 0.0),
            V(0.0, 0, 0.25),
            V(0.3, 0, 0.25),
            V(0.3, 0, 0.5),
            V(0.6, 0, 0.5),
            V(0.6, 0, 0.75),
            V(0.9, 0, 0.75),
            V(0.9, 0, 1.0),
            V(1.2, 0, 1.0),
            V(1.2, 0, 0.67457),
            V(0.1, 0, -0.25),
            V(0.0, 0, -0.25),
        )
        edges_data = (
            (0, 1),
            (1, 2),
            (2, 3),
            (3, 4),
            (4, 5),
            (5, 6),
            (6, 7),
            (7, 8),
            (8, 9),
            (0, 11),
            (10, 11),
            (10, 9),
        )
        faces_data = ()
        expected_profile = (verts_data, edges_data, faces_data)
        generated_profile = subject.generate_stair_2d_profile(**kwargs)
        self.compare_data(generated_profile, expected_profile)

    def test_create_concrete_stair_nib(self):
        kwargs = {
            "base_slab_depth": 0.25,
            "has_top_nib": True,
            "height": 1.0,
            "number_of_treads": 3,
            "stair_type": "CONCRETE",
            "top_slab_depth": 0.25,
            "tread_depth": 0.25,
            "tread_run": 0.3,
            "width": 1.2,
        }
        verts_data = (
            V(0.0, 0, 0.0),
            V(0.0, 0, 0.25),
            V(0.3, 0, 0.25),
            V(0.3, 0, 0.5),
            V(0.6, 0, 0.5),
            V(0.6, 0, 0.75),
            V(0.9, 0, 0.75),
            V(0.9, 0, 1.0),
            V(1.2, 0, 1.0),
            V(1.2, 0, 0.75),
            V(1.3, 0, 0.75),
            V(0.1, 0, -0.25),
            V(0.0, 0, -0.25),
        )

        edges_data = (
            (0, 1),
            (1, 2),
            (2, 3),
            (3, 4),
            (4, 5),
            (5, 6),
            (6, 7),
            (7, 8),
            (8, 9),
            (9, 10),
            (0, 12),
            (11, 12),
            (11, 10),
        )

        faces_data = ()
        expected_profile = (verts_data, edges_data, faces_data)
        generated_profile = subject.generate_stair_2d_profile(**kwargs)
        self.compare_data(generated_profile, expected_profile)

    def test_create_wood_steel_stair(self):
        kwargs = {
            "height": 1.0,
            "number_of_treads": 3,
            "stair_type": "WOOD/STEEL",
            "tread_depth": 0.25,
            "tread_run": 0.3,
            "width": 1.2,
        }
        verts_data = (
            V(0.0, 0, 0.0),
            V(0.3, 0, 0.0),
            V(0.3, 0, 0.25),
            V(0.0, 0, 0.25),
            V(0.3, 0, 0.25),
            V(0.6, 0, 0.25),
            V(0.6, 0, 0.5),
            V(0.3, 0, 0.5),
            V(0.6, 0, 0.5),
            V(0.9, 0, 0.5),
            V(0.9, 0, 0.75),
            V(0.6, 0, 0.75),
            V(0.9, 0, 0.75),
            V(1.2, 0, 0.75),
            V(1.2, 0, 1.0),
            V(0.9, 0, 1.0),
        )

        edges_data = (
            (0, 1),
            (1, 2),
            (2, 3),
            (3, 0),
            (4, 5),
            (5, 6),
            (6, 7),
            (7, 4),
            (8, 9),
            (9, 10),
            (10, 11),
            (11, 8),
            (12, 13),
            (13, 14),
            (14, 15),
            (15, 12),
        )

        faces_data = ()

        expected_profile = (verts_data, edges_data, faces_data)
        generated_profile = subject.generate_stair_2d_profile(**kwargs)
        self.compare_data(generated_profile, expected_profile)

    def test_create_generic_stair(self):
        kwargs = {"height": 1.0, "number_of_treads": 3, "stair_type": "GENERIC", "tread_run": 0.3, "width": 1.2}
        verts_data = (
            V(0.0, 0, 0.0),
            V(0.0, 0, 0.25),
            V(0.3, 0, 0.25),
            V(0.3, 0, 0.5),
            V(0.6, 0, 0.5),
            V(0.6, 0, 0.75),
            V(0.9, 0, 0.75),
            V(0.9, 0, 1.0),
            V(1.2, 0, 1.0),
            V(1.2, 0, 0.0),
        )

        edges_data = (
            (0, 1),
            (1, 2),
            (2, 3),
            (3, 4),
            (4, 5),
            (5, 6),
            (6, 7),
            (7, 8),
            (8, 9),
            (9, 0),
        )

        faces_data = ()
        expected_profile = (verts_data, edges_data, faces_data)
        generated_profile = subject.generate_stair_2d_profile(**kwargs)
        self.compare_data(generated_profile, expected_profile)
