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
import json
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


class TestMarkManualBooleans(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)

        element = ifc.createIfcWall()
        boolean = ifc.createIfcBooleanClippingResult()
        subject.mark_manual_booleans(element, [boolean])
        pset = ifcopenshell.util.element.get_pset(element, "BBIM_Boolean")
        assert pset
        value = json.loads(pset["Data"])
        assert set(value) == {boolean.id()}


class TestUnmarkManualBooleans(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)

        element = ifc.createIfcWall()
        boolean = ifc.createIfcBooleanClippingResult()
        boolean2 = ifc.createIfcBooleanClippingResult()
        subject.mark_manual_booleans(element, [boolean, boolean2])
        subject.unmark_manual_booleans(element, [boolean.id()])

        pset = ifcopenshell.util.element.get_pset(element, "BBIM_Boolean")
        assert pset
        value = json.loads(pset["Data"])
        assert set(value) == {boolean2.id()}


class TestStairCalculatedParams(NewFile):
    def compare_data(self, pset_data, expected_calculated_data):
        calculated_data = subject.get_active_stair_calculated_params(pset_data)
        for key, value in expected_calculated_data.items():
            assert tool.Cad.is_x(calculated_data[key], value)

    def test_run(self):
        bpy.ops.bim.create_project()
        bpy.ops.mesh.add_clever_stair()
        pset_data_base = {
            "number_of_treads": 3,
            "height": 1.0,
            "tread_run": 0.3,
            "custom_first_last_tread_run": (0.0, 0.0),
            "nosing_length": 0.0,
        }
        calculated_data_base = {
            "Number of Risers": 4,
            "Tread Rise": 0.25,
            "Length": 1.2,
        }
        self.compare_data(pset_data_base, calculated_data_base)

        # custom first and last treads run
        pset_data = pset_data_base.copy()
        calculated_data = calculated_data_base.copy()
        pset_data["custom_first_last_tread_run"] = (0.1, 0.4)
        calculated_data["Length"] += -0.2 + 0.1
        self.compare_data(pset_data, calculated_data)

        # overlap affects stair length only by first tread
        pset_data = pset_data_base.copy()
        calculated_data = calculated_data_base.copy()
        pset_data["nosing_length"] = 0.1
        calculated_data["Length"] += 0.1
        self.compare_data(pset_data, calculated_data)

        # tread gap
        pset_data = pset_data_base.copy()
        calculated_data = calculated_data_base.copy()
        pset_data["nosing_length"] = -0.1
        calculated_data["Length"] += 0.1 * pset_data["number_of_treads"]
        self.compare_data(pset_data, calculated_data)


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
            (11, 0),
            (10, 11),
            (9, 10),
        )
        edges_data = [e[::-1] for e in edges_data]
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
            (12, 0),
            (11, 12),
            (10, 11),
        )
        edges_data = [e[::-1] for e in edges_data]

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
        edges_data = [e[::-1] for e in edges_data]

        faces_data = ()
        expected_profile = (verts_data, edges_data, faces_data)
        generated_profile = subject.generate_stair_2d_profile(**kwargs)
        self.compare_data(generated_profile, expected_profile)


class TestUsingArrays(NewFile):
    def setup_array(self, add_second_layer=False, sync_children=False):
        bpy.context.scene.BIMProjectProperties.template_file = "0"
        bpy.ops.bim.create_project()

        bpy.ops.mesh.primitive_cube_add()
        obj = bpy.context.active_object
        bpy.context.scene.BIMRootProperties.ifc_product = "IfcElement"
        bpy.ops.bim.assign_class(ifc_class="IfcActuator", predefined_type="ELECTRICACTUATOR", userdefined_type="")

        bpy.ops.bim.add_array()
        bpy.ops.bim.enable_editing_array(item=0)
        obj.BIMArrayProperties.count = 4
        obj.BIMArrayProperties.x = 4
        obj.BIMArrayProperties.sync_children = sync_children
        bpy.ops.bim.edit_array(item=0)

        if add_second_layer:
            bpy.ops.bim.add_array()
            bpy.ops.bim.enable_editing_array(item=1)
            obj.BIMArrayProperties.count = 3
            obj.BIMArrayProperties.y = 4
            obj.BIMArrayProperties.sync_children = sync_children
            bpy.ops.bim.edit_array(item=1)

    def test_remove_array_last_to_first(self):
        self.setup_array(add_second_layer=True)
        bpy.ops.bim.remove_array(item=1)
        assert len(bpy.context.selected_objects) == 4
        bpy.ops.bim.remove_array(item=0)
        assert len(bpy.context.selected_objects) == 1

    def test_remove_array_first_to_last(self):
        self.setup_array(add_second_layer=True)
        bpy.ops.bim.remove_array(item=0)
        assert len(bpy.context.selected_objects) == 3
        bpy.ops.bim.remove_array(item=0)
        assert len(bpy.context.selected_objects) == 1

    def test_apply_array_1_layer(self):
        self.setup_array()
        bpy.ops.bim.apply_array()

        objs = bpy.context.selected_objects
        assert len(objs) == 4
        # check BBIM_Array psets are removed
        for obj in objs:
            element = tool.Ifc.get_entity(obj)
            pset = ifcopenshell.util.element.get_pset(element, "BBIM_Array")
            assert pset is None, (obj, pset)

    def test_apply_array_multiple_layers(self):
        self.setup_array(add_second_layer=True)
        bpy.ops.bim.apply_array()  # apply second layer
        bpy.ops.bim.apply_array()  # apply first layer

        objs = bpy.context.selected_objects
        assert len(objs) == 12

        # check BBIM_Array psets are removed
        for obj in objs:
            element = tool.Ifc.get_entity(obj)
            pset = ifcopenshell.util.element.get_pset(element, "BBIM_Array")
            assert pset is None, (obj, pset)

    def test_apply_array_with_sync_children(self):
        self.setup_array(sync_children=True)
        bpy.ops.bim.apply_array()

        objs = bpy.context.selected_objects
        assert len(objs) == 4
        # check BBIM_Array psets are removed
        for obj in objs:
            element = tool.Ifc.get_entity(obj)
            pset = ifcopenshell.util.element.get_pset(element, "BBIM_Array")
            assert pset is None, (obj, pset)
