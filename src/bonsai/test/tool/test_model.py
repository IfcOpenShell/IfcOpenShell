# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
#
# This file is part of Bonsai.
#
# Bonsai is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Bonsai is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Bonsai.  If not, see <http://www.gnu.org/licenses/>.

import json
from typing import Any

import bpy
import ifcopenshell
import ifcopenshell.api.geometry
import ifcopenshell.api.material
import ifcopenshell.api.pset
import ifcopenshell.api.root
import ifcopenshell.api.style
import ifcopenshell.api.type
import ifcopenshell.util.element
import ifcopenshell.util.representation
import ifcopenshell.util.shape_builder
import numpy as np
from ifcopenshell.util.shape_builder import ShapeBuilder, V

import bonsai.core.tool
import bonsai.tool as tool
from bonsai.tool.model import Model as subject
from test.bim.bootstrap import NewFile


class TestImplementsTool(NewFile):
    def test_run(self):
        assert isinstance(subject(), bonsai.core.tool.Model)


class TestGenerateOccurrenceName(NewFile):
    def test_generating_based_on_class(self):
        ifc = ifcopenshell.file()
        element_type = ifc.createIfcWallType(Name="Foobar")
        prefs = tool.Blender.get_addon_preferences()
        with tool.Blender.preserve_prop_value(prefs, "occurrence_name_style"):
            prefs.occurrence_name_style = "CLASS"
            assert subject.generate_occurrence_name(element_type, "IfcWall") == "Wall"

    def test_generating_based_on_type_name(self):
        ifc = ifcopenshell.file()
        element_type = ifc.createIfcWallType()
        prefs = tool.Blender.get_addon_preferences()
        with tool.Blender.preserve_prop_value(prefs, "occurrence_name_style"):
            prefs.occurrence_name_style = "TYPE"
            assert subject.generate_occurrence_name(element_type, "IfcWall") == "Unnamed"
            element_type.Name = "Foobar"
            assert subject.generate_occurrence_name(element_type, "IfcWall") == "Foobar"

    def test_generating_based_on_a_custom_function(self):
        ifc = ifcopenshell.file()
        element_type = ifc.createIfcWallType()
        prefs = tool.Blender.get_addon_preferences()
        with tool.Blender.preserve_prop_value(prefs, "occurrence_name_style"):
            prefs.occurrence_name_style = "CUSTOM"
            prefs.occurrence_name_function = '"Foobar"'
            assert subject.generate_occurrence_name(element_type, "IfcWall") == "Foobar"


class TestGetBooleans(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)

        context = ifc.createIfcGeometricRepresentationContext()
        element = ifc.createIfcWall()

        items = [ifc.createIfcExtrudedAreaSolid()]
        representation = ifc.createIfcShapeRepresentation(Items=items, ContextOfItems=context)
        ifcopenshell.api.geometry.assign_representation(ifc, product=element, representation=representation)

        builder = ifcopenshell.util.shape_builder.ShapeBuilder(ifc)
        cut1 = builder.half_space_solid(builder.plane())
        cut2 = builder.half_space_solid(builder.plane())
        bools = ifcopenshell.api.geometry.add_boolean(ifc, first_item=items[0], second_items=[cut1, cut2])

        assert set(subject.get_booleans(element, representation)) == set(bools)


class TestGetManualBooleans(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)

        context = ifc.createIfcGeometricRepresentationContext()
        element = ifc.createIfcWall()

        items = [ifc.createIfcExtrudedAreaSolid()]
        representation = ifc.createIfcShapeRepresentation(Items=items, ContextOfItems=context)
        ifcopenshell.api.geometry.assign_representation(ifc, product=element, representation=representation)

        builder = ifcopenshell.util.shape_builder.ShapeBuilder(ifc)
        cut1 = builder.half_space_solid(builder.plane())
        cut2 = builder.half_space_solid(builder.plane())
        bools = ifcopenshell.api.geometry.add_boolean(ifc, first_item=items[0], second_items=[cut1, cut2])

        assert set(subject.get_booleans(element, representation)) == set(bools)
        assert len(subject.get_manual_booleans(element, representation)) == 0

        bool1 = bools[0]

        subject.mark_manual_booleans(element, [bool1])
        assert set(subject.get_manual_booleans(element, representation)) == {bool1}


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
        bpy.ops.mesh.add_stair()
        pset_data_base = {
            "number_of_treads": 3,
            "height": 1.0,
            "tread_run": 0.3,
            "custom_first_last_tread_run": (None, None),
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
        pset_data["custom_tread_lock"] = False
        calculated_data["Length"] += -0.2 + 0.1
        self.compare_data(pset_data, calculated_data)

        # zero-width first tread
        pset_data = pset_data_base.copy()
        calculated_data = calculated_data_base.copy()
        pset_data["custom_first_last_tread_run"] = (0.0, None)
        pset_data["custom_tread_lock"] = False
        calculated_data["Length"] = 0.9  # Only 3 treads at 0.3 each
        self.compare_data(pset_data, calculated_data)

        # zero-width last tread
        pset_data = pset_data_base.copy()
        calculated_data = calculated_data_base.copy()
        pset_data["custom_first_last_tread_run"] = (None, 0.0)
        pset_data["custom_tread_lock"] = False
        calculated_data["Length"] = 0.9  # Only 3 treads at 0.3 each
        self.compare_data(pset_data, calculated_data)

        # both first and last treads zero-width
        pset_data = pset_data_base.copy()
        calculated_data = calculated_data_base.copy()
        pset_data["custom_first_last_tread_run"] = (0.0, 0.0)
        pset_data["custom_tread_lock"] = False
        calculated_data["Length"] = 0.6  # Only 2 middle treads at 0.3 each
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
            assert np.allclose(vert, V(vert_gen), atol=0.01)

    CONCRETE_STAIR_KWARGS: dict[str, Any] = {
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

    def test_create_concrete_stair(self):
        kwargs = self.CONCRETE_STAIR_KWARGS.copy()
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
        kwargs = self.CONCRETE_STAIR_KWARGS.copy()
        kwargs["has_top_nib"] = True
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

    def test_create_concrete_stair_zero_width_first_tread(self):
        kwargs = self.CONCRETE_STAIR_KWARGS.copy()
        kwargs["custom_first_last_tread_run"] = (0.0, None)
        verts_data = (
            V(0.0, 0, 0.0),
            # First tread skipped - goes straight to second tread
            V(0.0, 0, 0.5),
            V(0.3, 0, 0.5),
            V(0.3, 0, 0.75),
            V(0.6, 0, 0.75),
            V(0.6, 0, 1.0),
            V(0.9, 0, 1.0),
            V(0.9, 0, 0.6745729),
            V(0.0, 0, -0.0754271),
        )
        edges_data = (
            (0, 1),
            (1, 2),
            (2, 3),
            (3, 4),
            (4, 5),
            (5, 6),
            (6, 7),
            (8, 0),
            (7, 8),
        )
        edges_data = [e[::-1] for e in edges_data]
        faces_data = ()
        expected_profile = (verts_data, edges_data, faces_data)
        generated_profile = subject.generate_stair_2d_profile(**kwargs)
        self.compare_data(generated_profile, expected_profile)

    def test_create_concrete_stair_zero_width_last_tread(self):
        kwargs = self.CONCRETE_STAIR_KWARGS.copy()
        kwargs["custom_first_last_tread_run"] = (None, 0.0)
        verts_data = (
            V(0.0, 0, 0.0),
            V(0.0, 0, 0.25),
            V(0.3, 0, 0.25),
            V(0.3, 0, 0.5),
            V(0.6, 0, 0.5),
            V(0.6, 0, 0.75),
            V(0.9, 0, 0.75),
            # Last tread skipped
            V(0.9, 0, 0.42457),
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
            (9, 0),
            (8, 9),
            (7, 8),
        )
        edges_data = [e[::-1] for e in edges_data]
        faces_data = ()
        expected_profile = (verts_data, edges_data, faces_data)
        generated_profile = subject.generate_stair_2d_profile(**kwargs)
        self.compare_data(generated_profile, expected_profile)

    WOOD_STEEL_STAIR_KWARGS: dict[str, Any] = {
        "height": 1.0,
        "number_of_treads": 3,
        "stair_type": "WOOD/STEEL",
        "tread_depth": 0.25,
        "tread_run": 0.3,
        "width": 1.2,
    }

    def test_create_wood_steel_stair(self):
        kwargs = self.WOOD_STEEL_STAIR_KWARGS.copy()
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

    def test_create_wood_steel_stair_zero_width_first_tread(self):
        kwargs = self.WOOD_STEEL_STAIR_KWARGS.copy()
        kwargs["custom_first_last_tread_run"] = (0.0, None)
        verts_data = (
            # First tread skipped - start at second tread
            V(0.0, 0, 0.25),
            V(0.3, 0, 0.25),
            V(0.3, 0, 0.5),
            V(0.0, 0, 0.5),
            V(0.3, 0, 0.5),
            V(0.6, 0, 0.5),
            V(0.6, 0, 0.75),
            V(0.3, 0, 0.75),
            V(0.6, 0, 0.75),
            V(0.9, 0, 0.75),
            V(0.9, 0, 1.0),
            V(0.6, 0, 1.0),
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
        )

        faces_data = ()

        expected_profile = (verts_data, edges_data, faces_data)
        generated_profile = subject.generate_stair_2d_profile(**kwargs)
        self.compare_data(generated_profile, expected_profile)

    def test_create_wood_steel_stair_zero_width_last_tread(self):
        """Test wood/steel stair with zero-width last tread"""
        kwargs = self.WOOD_STEEL_STAIR_KWARGS.copy()
        kwargs["custom_first_last_tread_run"] = (None, 0.0)

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
            # Last tread skipped
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
        )

        faces_data = ()

        expected_profile = (verts_data, edges_data, faces_data)
        generated_profile = subject.generate_stair_2d_profile(**kwargs)
        self.compare_data(generated_profile, expected_profile)

    GENERIC_STAIR_KWARGS: dict[str, Any] = {
        "height": 1.0,
        "number_of_treads": 3,
        "stair_type": "GENERIC",
        "tread_run": 0.3,
        "width": 1.2,
    }

    def test_create_generic_stair(self):
        kwargs = self.GENERIC_STAIR_KWARGS.copy()
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

    def test_create_generic_stair_zero_width_treads(self):
        kwargs = self.GENERIC_STAIR_KWARGS.copy()
        kwargs["custom_first_last_tread_run"] = (0.0, 0.0)
        verts_data = (
            V(0.0, 0, 0.0),
            # First tread skipped
            V(0.0, 0, 0.5),
            V(0.3, 0, 0.5),
            V(0.3, 0, 0.75),
            V(0.6, 0, 0.75),
            # Last tread skipped
            V(0.6, 0, 0.0),
        )
        edges_data = (
            (0, 1),
            (1, 2),
            (2, 3),
            (3, 4),
            (4, 5),
            (5, 0),
        )
        edges_data = [e[::-1] for e in edges_data]

        faces_data = ()
        expected_profile = (verts_data, edges_data, faces_data)
        generated_profile = subject.generate_stair_2d_profile(**kwargs)
        self.compare_data(generated_profile, expected_profile)


class TestUsingArrays(NewFile):
    @staticmethod
    def _array_objects() -> list[bpy.types.Object]:
        return [o for o in bpy.data.objects if (e := tool.Ifc.get_entity(o)) and e.is_a("IfcActuator")]

    def setup_array(self, add_second_layer=False, sync_children=False):
        tool.Project.get_project_props().template_file = "0"
        bpy.ops.bim.create_project()

        bpy.ops.mesh.primitive_cube_add()
        obj = bpy.context.active_object
        assert obj
        rprops = tool.Root.get_root_props()
        rprops.ifc_product = "IfcElement"
        bpy.ops.bim.assign_class(ifc_class="IfcActuator", predefined_type="ELECTRICACTUATOR", userdefined_type="")

        bpy.ops.bim.add_array()
        bpy.ops.bim.enable_editing_array(item=0)
        props = tool.Model.get_array_props(obj)
        props.count = 4
        props.x = 4
        props.sync_children = sync_children
        bpy.ops.bim.finish_editing_array()

        if add_second_layer:
            bpy.ops.bim.add_array()
            bpy.ops.bim.enable_editing_array(item=1)
            props = tool.Model.get_array_props(obj)
            props.count = 3
            props.y = 4
            props.sync_children = sync_children
            bpy.ops.bim.finish_editing_array()

    def test_remove_array_last_to_first(self):
        self.setup_array(add_second_layer=True)
        bpy.ops.bim.remove_array(item=1)
        assert len(self._array_objects()) == 4
        bpy.ops.bim.remove_array(item=0)
        assert len(self._array_objects()) == 1

    def test_remove_array_first_to_last(self):
        self.setup_array(add_second_layer=True)
        bpy.ops.bim.remove_array(item=0)
        assert len(self._array_objects()) == 3
        bpy.ops.bim.remove_array(item=0)
        assert len(self._array_objects()) == 1

    def test_apply_array_1_layer(self):
        self.setup_array()
        bpy.ops.bim.apply_array()

        objs = self._array_objects()
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

        objs = self._array_objects()
        assert len(objs) == 12

        # check BBIM_Array psets are removed
        for obj in objs:
            element = tool.Ifc.get_entity(obj)
            pset = ifcopenshell.util.element.get_pset(element, "BBIM_Array")
            assert pset is None, (obj, pset)

    def test_apply_array_with_sync_children(self):
        self.setup_array(sync_children=True)
        bpy.ops.bim.apply_array()

        objs = self._array_objects()
        assert len(objs) == 4
        # check BBIM_Array psets are removed
        for obj in objs:
            element = tool.Ifc.get_entity(obj)
            pset = ifcopenshell.util.element.get_pset(element, "BBIM_Array")
            assert pset is None, (obj, pset)

    def test_remove_array_tolerates_stale_child_guid(self):
        """``bim.remove_array`` and the underlying ``regenerate_array`` must
        survive a child GUID in ``BBIM_Array.Data`` that no longer resolves
        in the file. Real-world IFC files can carry dangling array refs
        from external edits — the remove path is meant to delete those
        children, so an already-missing entity is the desired terminal
        state, not a fatal error."""
        self.setup_array()
        parent_obj = bpy.context.active_object
        parent_element = tool.Ifc.get_entity(parent_obj)
        ifc_file = tool.Ifc.get()

        pset = ifcopenshell.util.element.get_pset(parent_element, "BBIM_Array")
        data = json.loads(pset["Data"])
        data[0]["children"].append("3iyt7r$Hf4_hQYNhBIDJI4")
        ifcopenshell.api.pset.edit_pset(
            ifc_file,
            pset=ifc_file.by_id(pset["id"]),
            properties={"Data": json.dumps(data)},
        )

        bpy.ops.bim.remove_array(item=0)
        assert ifcopenshell.util.element.get_pset(parent_element, "BBIM_Array") is None


class TestApplyIfcMaterialChanges(NewFile):
    def get_used_styles(self, obj: bpy.types.Object) -> set[ifcopenshell.entity_instance]:
        ifc_file = tool.Ifc.get()
        return {
            ifc_file.by_id(tool.Blender.get_ifc_definition_id(s.material)) for s in obj.material_slots if s.material
        }

    def get_mesh(self, obj: bpy.types.Object) -> bpy.types.Mesh:
        mesh = obj.data
        assert isinstance(mesh, bpy.types.Mesh)
        return mesh

    def setup_test(self, and_elements: bool = True) -> None:
        props = tool.Project.get_project_props()
        props.template_file = "0"
        bpy.context.scene.unit_settings.length_unit = "MILLIMETERS"
        bpy.ops.bim.create_project()
        ifc_file = tool.Ifc.get()

        # Setup materials and styles.
        context = ifcopenshell.util.representation.get_context(ifc_file, "Model", "Body", "MODEL_VIEW")
        assert context  # Type checker.

        red_material = ifcopenshell.api.material.add_material(ifc_file, "Red Material")
        bpy.ops.bim.load_styles(style_type="IfcSurfaceStyle")
        bpy.ops.bim.enable_adding_presentation_style()
        sprops = tool.Style.get_style_props()
        sprops.style_name = "Red"
        bpy.ops.bim.add_presentation_style()
        red_style = next(i for i in ifc_file.by_type("IfcSurfaceStyle") if i.Name == "Red")
        ifcopenshell.api.style.assign_material_style(ifc_file, red_material, red_style, context)

        blue_material = ifcopenshell.api.material.add_material(ifc_file, "Blue Material")
        bpy.ops.bim.enable_adding_presentation_style()
        sprops.style_name = "Blue"
        bpy.ops.bim.add_presentation_style()
        blue_style = next(i for i in ifc_file.by_type("IfcSurfaceStyle") if i.Name == "Blue")
        ifcopenshell.api.style.assign_material_style(ifc_file, blue_material, blue_style, context)

        bpy.ops.bim.enable_adding_presentation_style()
        sprops.style_name = "Green"
        bpy.ops.bim.add_presentation_style()

        if and_elements:
            self.setup_elements()

    def setup_elements(self) -> None:
        ifc_file = tool.Ifc.get()
        blue_material = next(i for i in ifc_file.by_type("IfcMaterial") if i.Name == "Blue Material")
        blue_style = tool.Material.get_style(blue_material)

        # Element type.
        bpy.ops.mesh.primitive_cube_add(size=10, location=(0, 0, 4))
        element_type_obj = bpy.data.objects["Cube"]
        bpy.ops.bim.assign_class(ifc_class="IfcActuatorType", predefined_type="ELECTRICACTUATOR", userdefined_type="")
        element_type = tool.Ifc.get_entity(element_type_obj)

        # Setup occurrences.
        relating_type_id = element_type.id()
        bpy.ops.bim.add_occurrence(relating_type_id=relating_type_id)
        simple = bpy.context.active_object
        simple.name = "Simple"

        # Occurrence with an opening.
        bpy.ops.bim.add_occurrence(relating_type_id=relating_type_id)
        with_opening = bpy.context.active_object
        with_opening.name = "With Opening"
        props = tool.Root.get_root_props()
        props.representation_obj = with_opening
        bpy.ops.bim.add_element(ifc_product="IfcFeatureElement", ifc_class="IfcOpeningElement")

        # Occurrence with a material override.
        bpy.ops.bim.add_occurrence(relating_type_id=relating_type_id)
        with_material = bpy.context.active_object
        with_material.name = "With Material"
        tool.Blender.set_objects_selection(bpy.context, active_object=with_material, selected_objects=[with_material])

        ifcopenshell.api.material.assign_material(
            ifc_file, products=[tool.Ifc.get_entity(with_material)], material=blue_material
        )
        tool.Material.ensure_material_assigned([tool.Ifc.get_entity(with_material)], material=blue_material)

        assert self.get_used_styles(element_type_obj) == set()
        for element in ifc_file.by_type("IfcActuator"):
            obj = tool.Ifc.get_object(element)
            expected = {blue_style} if obj.name == "With Material" else set()
            assert self.get_used_styles(obj) == expected

    def test_element_type_and_occurrences(self):
        self.setup_test()
        ifc_file = tool.Ifc.get()
        element_type = next(ifc_file.by_type("IfcActuatorType").__iter__())
        red_material = next(i for i in ifc_file.by_type("IfcMaterial") if i.Name == "Red Material")
        red_style = tool.Material.get_style(red_material)
        blue_style = next(i for i in ifc_file.by_type("IfcSurfaceStyle") if i.Name == "Blue")

        ifcopenshell.api.material.assign_material(ifc_file, material=red_material, products=[element_type])
        tool.Material.ensure_material_assigned([element_type], material=red_material)
        assert self.get_used_styles(tool.Ifc.get_object(element_type)) == {red_style}
        for element in ifc_file.by_type("IfcActuator"):
            obj = tool.Ifc.get_object(element)
            expected = {blue_style} if obj.name == "With Material" else {red_style}
            assert self.get_used_styles(obj) == expected

        ifcopenshell.api.material.unassign_material(ifc_file, products=[element_type])
        tool.Material.ensure_material_unassigned([element_type])
        assert self.get_used_styles(tool.Ifc.get_object(element_type)) == set()
        for element in ifc_file.by_type("IfcActuator"):
            obj = tool.Ifc.get_object(element)
            expected = {blue_style} if obj.name == "With Material" else set()
            assert self.get_used_styles(obj) == expected

    def test_dont_override_exisiting_styles(self):
        self.setup_test()
        ifc_file = tool.Ifc.get()
        element_type = next(ifc_file.by_type("IfcActuatorType").__iter__())
        red_material = next(i for i in ifc_file.by_type("IfcMaterial") if i.Name == "Red Material")
        green_style = next(i for i in ifc_file.by_type("IfcSurfaceStyle") if i.Name == "Green")

        # Occurrence with a style.
        element_type_obj = tool.Ifc.get_object(element_type)
        with bpy.context.temp_override(selected_objects=[element_type_obj]):
            bpy.ops.bim.assign_style_to_selected(style_id=green_style.id())

        ifcopenshell.api.material.assign_material(ifc_file, material=red_material, products=[element_type])
        tool.Material.ensure_material_assigned([element_type], material=red_material)
        assert self.get_used_styles(tool.Ifc.get_object(element_type)) == {green_style}
        for element in ifc_file.by_type("IfcActuator"):
            obj = tool.Ifc.get_object(element)
            assert self.get_used_styles(obj) == {green_style}

        ifcopenshell.api.material.unassign_material(ifc_file, products=[element_type])
        tool.Material.ensure_material_unassigned([element_type])
        assert self.get_used_styles(tool.Ifc.get_object(element_type)) == {green_style}
        for element in ifc_file.by_type("IfcActuator"):
            obj = tool.Ifc.get_object(element)
            assert self.get_used_styles(obj) == {green_style}

    def test_assign_material_to_representation_that_has_2_items_and_1_item_has_a_style(self):
        self.setup_test(and_elements=False)
        ifc_file = tool.Ifc.get()
        red_material = next(i for i in ifc_file.by_type("IfcMaterial") if i.Name == "Red Material")
        red_style = tool.Material.get_style(red_material)
        green_style = next(i for i in ifc_file.by_type("IfcSurfaceStyle") if i.Name == "Green")

        bpy.ops.mesh.primitive_cube_add(size=10, location=(0, 0, 4))
        obj = bpy.data.objects["Cube"]
        bpy.ops.bim.assign_class(ifc_class="IfcActuator", predefined_type="ELECTRICACTUATOR", userdefined_type="")
        element = tool.Ifc.get_entity(obj)
        builder = ShapeBuilder(ifc_file)

        # Change representation that consists of 2 rep items:
        # 1 with style and other without.
        rep = tool.Geometry.get_active_representation(obj)
        assert rep
        cube = rep.Items[0]
        cube2 = builder.deep_copy(cube)
        rep.Items = [cube, cube2]
        tool.Style.assign_style_to_representation_item(cube, green_style)
        tool.Geometry._reload_representation(obj)

        def get_material_indices(mesh: bpy.types.Mesh) -> np.ndarray:
            buffer = np.empty(len(mesh.polygons), dtype="I")
            mesh.polygons.foreach_get("material_index", buffer)
            return buffer

        mesh = self.get_mesh(obj)
        assert len(mesh.materials) == 2
        assert set(mesh.materials) == {bpy.data.materials["Green"], None}

        ifcopenshell.api.material.assign_material(ifc_file, products=[element], material=red_material)
        tool.Material.ensure_material_assigned([element], material=red_material)
        assert self.get_used_styles(obj) == {green_style, red_style}
        ifcopenshell.api.material.unassign_material(ifc_file, products=[element])
        tool.Material.ensure_material_unassigned([element])
        mesh = self.get_mesh(obj)
        assert len(mesh.materials) == 2
        assert set(mesh.materials) == {bpy.data.materials["Green"], None}

        # Test that if style is the same it would just reuse it.
        tool.Style.assign_style_to_representation_item(cube, red_style)
        tool.Geometry._reload_representation(obj)
        mesh = self.get_mesh(obj)
        assert len(mesh.materials) == 2
        assert set(mesh.materials) == {bpy.data.materials["Red"], None}

        ifcopenshell.api.material.assign_material(ifc_file, products=[element], material=red_material)
        tool.Material.ensure_material_assigned([element], material=red_material)
        mesh = self.get_mesh(obj)
        assert mesh.materials[:] == [bpy.data.materials["Red"]]
        # All polygons are just reassigned to the existing material.
        assert set(get_material_indices(mesh)) == {mesh.materials.find("Red")}

        ifcopenshell.api.material.unassign_material(ifc_file, products=[element])
        tool.Material.ensure_material_unassigned([element])
        mesh = self.get_mesh(obj)
        assert len(mesh.materials) == 2
        assert set(mesh.materials) == {bpy.data.materials["Red"], None}
        assert set(get_material_indices(mesh)) == {0, 1}

    def test_assign_unassign_overriding_occurrence_material(self):
        self.setup_test(and_elements=True)
        ifc_file = tool.Ifc.get()
        element_type = next(ifc_file.by_type("IfcActuatorType").__iter__())
        red_material = next(i for i in ifc_file.by_type("IfcMaterial") if i.Name == "Red Material")
        no_style_material = ifcopenshell.api.material.add_material(ifc_file, "No Style")
        obj = bpy.data.objects["Simple"]
        element = tool.Ifc.get_entity(obj)

        ifcopenshell.api.material.assign_material(ifc_file, material=red_material, products=[element_type])
        tool.Material.ensure_material_assigned([element_type], material=red_material)

        # Override type material.
        ifcopenshell.api.material.assign_material(ifc_file, material=no_style_material, products=[element])
        tool.Material.ensure_material_assigned([element], material=no_style_material)
        assert self.get_mesh(obj).materials[:] == []

        ifcopenshell.api.material.unassign_material(ifc_file, products=[element])
        tool.Material.ensure_material_unassigned([element])
        assert self.get_mesh(obj).materials[:] == [bpy.data.materials["Red"]]


class TestOffsetWall(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)

        wall_type = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcWallType", name="WAL01")
        material_set = ifcopenshell.api.material.add_material_set(ifc, set_type="IfcMaterialLayerSet")
        material = ifcopenshell.api.material.add_material(ifc, name="PB01", category="gypsum")
        layer = ifcopenshell.api.material.add_layer(ifc, layer_set=material_set, material=material)
        ifcopenshell.api.material.edit_layer(ifc, layer=layer, attributes={"LayerThickness": 100})
        ifcopenshell.api.material.assign_material(ifc, products=[wall_type], material=material_set)

        wall = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcWall")
        ifcopenshell.api.type.assign_type(ifc, related_objects=[wall], relating_type=wall_type)
        rel = ifcopenshell.api.material.assign_material(ifc, products=[wall], type="IfcMaterialLayerSetUsage")
        usage = rel.RelatingMaterial
        obj = bpy.data.objects.new("Wall", None)
        tool.Ifc.link(wall, obj)

        usage.DirectionSense = "POSITIVE"
        subject.offset_wall(obj, "CENTER")
        assert usage.OffsetFromReferenceLine == -50
        usage.DirectionSense = "NEGATIVE"
        subject.offset_wall(obj, "CENTER")
        assert usage.OffsetFromReferenceLine == 50

        usage.DirectionSense = "POSITIVE"
        subject.offset_wall(obj, "INTERIOR")
        assert usage.OffsetFromReferenceLine == -100
        usage.DirectionSense = "NEGATIVE"
        subject.offset_wall(obj, "INTERIOR")
        assert usage.OffsetFromReferenceLine == 0

        usage.DirectionSense = "POSITIVE"
        subject.offset_wall(obj, "EXTERIOR")
        assert usage.OffsetFromReferenceLine == 0
        usage.DirectionSense = "NEGATIVE"
        subject.offset_wall(obj, "EXTERIOR")
        assert usage.OffsetFromReferenceLine == 100


class TestGetSiblingOccurrenceCount(NewFile):
    """The pen-icon dispatcher's pre-edit warning depends on this count: zero
    means the edit is safe (unique geometry), non-zero means the edit will
    silently mutate other instances sharing the same resolved body rep."""

    def _make_body_subcontext(self, ifc: ifcopenshell.file) -> ifcopenshell.entity_instance:
        import ifcopenshell.api.context

        ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcProject", name="Project")
        parent = ifcopenshell.api.context.add_context(ifc, context_type="Model")
        return ifcopenshell.api.context.add_context(
            ifc,
            context_type="Model",
            context_identifier="Body",
            target_view="MODEL_VIEW",
            parent=parent,
        )

    def _create_wall_with_body_rep(
        self,
        ifc: ifcopenshell.file,
        body_subcontext: ifcopenshell.entity_instance,
        name: str = "Wall",
    ) -> ifcopenshell.entity_instance:
        wall = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcWall", name=name)
        rep = ifc.createIfcShapeRepresentation(
            ContextOfItems=body_subcontext,
            RepresentationIdentifier="Body",
            RepresentationType="SweptSolid",
            Items=[ifc.createIfcExtrudedAreaSolid()],
        )
        ifcopenshell.api.geometry.assign_representation(ifc, product=wall, representation=rep)
        return wall

    def test_returns_zero_when_element_has_no_body_representation(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        wall = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcWall")
        assert subject.get_sibling_occurrence_count(wall) == 0

    def test_returns_zero_when_element_has_unique_body_representation(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        body = self._make_body_subcontext(ifc)
        wall = self._create_wall_with_body_rep(ifc, body)
        assert subject.get_sibling_occurrence_count(wall) == 0

    def test_returns_sibling_count_excluding_self_and_type(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        body = self._make_body_subcontext(ifc)
        wall_type = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcWallType", name="WAL01")
        type_rep = ifc.createIfcShapeRepresentation(
            ContextOfItems=body,
            RepresentationIdentifier="Body",
            RepresentationType="SweptSolid",
            Items=[ifc.createIfcExtrudedAreaSolid()],
        )
        ifcopenshell.api.geometry.assign_representation(ifc, product=wall_type, representation=type_rep)

        occurrences = [ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcWall", name=f"Wall{i}") for i in range(3)]
        ifcopenshell.api.type.assign_type(ifc, related_objects=occurrences, relating_type=wall_type)

        assert subject.get_sibling_occurrence_count(occurrences[0]) == 2
        assert subject.get_sibling_occurrence_count(occurrences[1]) == 2
        assert subject.get_sibling_occurrence_count(occurrences[2]) == 2

    def test_type_with_occurrences_reports_its_occurrence_count(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        body = self._make_body_subcontext(ifc)
        wall_type = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcWallType", name="WAL01")
        type_rep = ifc.createIfcShapeRepresentation(
            ContextOfItems=body,
            RepresentationIdentifier="Body",
            RepresentationType="SweptSolid",
            Items=[ifc.createIfcExtrudedAreaSolid()],
        )
        ifcopenshell.api.geometry.assign_representation(ifc, product=wall_type, representation=type_rep)
        occurrences = [ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcWall", name=f"Wall{i}") for i in range(2)]
        ifcopenshell.api.type.assign_type(ifc, related_objects=occurrences, relating_type=wall_type)

        assert subject.get_sibling_occurrence_count(wall_type) == 2
