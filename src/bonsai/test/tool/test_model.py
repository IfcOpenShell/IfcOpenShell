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

import bpy
import ifcopenshell
import ifcopenshell.api.material
import ifcopenshell.api.style
import ifcopenshell.util.element
import ifcopenshell.util.representation
import ifcopenshell.util.unit
import bonsai.core.tool
import bonsai.tool as tool
import numpy as np
import json
from test.bim.bootstrap import NewFile
from bonsai.tool.model import Model as subject
from ifcopenshell.util.shape_builder import V, ShapeBuilder


class TestImplementsTool(NewFile):
    def test_run(self):
        assert isinstance(subject(), bonsai.core.tool.Model)


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


class TestGetBooleans(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)

        context = ifc.createIfcGeometricRepresentationContext()
        element = ifc.createIfcWall()

        items = [ifc.createIfcExtrudedAreaSolid(), ifc.createIfcExtrudedAreaSolid()]
        representation = ifc.createIfcShapeRepresentation(Items=items, ContextOfItems=context)
        tool.Ifc.run("geometry.assign_representation", product=element, representation=representation)

        bool1 = set(tool.Ifc.run("geometry.add_boolean", representation=representation, matrix=np.eye(4)))
        bool2 = set(tool.Ifc.run("geometry.add_boolean", representation=representation, matrix=np.eye(4)))

        assert set(subject.get_booleans(element, representation)) == bool1 | bool2


class TestGetManualBooleans(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)

        context = ifc.createIfcGeometricRepresentationContext()
        element = ifc.createIfcWall()

        items = [ifc.createIfcExtrudedAreaSolid(), ifc.createIfcExtrudedAreaSolid()]
        representation = ifc.createIfcShapeRepresentation(Items=items, ContextOfItems=context)
        tool.Ifc.run("geometry.assign_representation", product=element, representation=representation)

        bool1 = set(tool.Ifc.run("geometry.add_boolean", representation=representation, matrix=np.eye(4)))
        bool2 = set(tool.Ifc.run("geometry.add_boolean", representation=representation, matrix=np.eye(4)))

        assert set(subject.get_booleans(element, representation)) == bool1 | bool2
        assert len(subject.get_manual_booleans(element, representation)) == 0

        subject.mark_manual_booleans(element, bool1)
        assert set(subject.get_manual_booleans(element, representation)) == bool1


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


class TestApplyIfcMaterialChanges(NewFile):
    def get_used_styles(self, obj: bpy.types.Object) -> set[ifcopenshell.entity_instance]:
        ifc_file = tool.Ifc.get()
        return {
            ifc_file.by_id(s.material.BIMStyleProperties.ifc_definition_id) for s in obj.material_slots if s.material
        }

    def get_mesh(self, obj: bpy.types.Object) -> bpy.types.Mesh:
        mesh = obj.data
        assert isinstance(mesh, bpy.types.Mesh)
        return mesh

    def setup_test(self, and_elements: bool = True) -> None:
        bpy.context.scene.BIMProjectProperties.template_file = "0"
        bpy.context.scene.unit_settings.length_unit = "MILLIMETERS"
        bpy.ops.bim.create_project()
        ifc_file = tool.Ifc.get()

        # Setup materials and styles.
        context = ifcopenshell.util.representation.get_context(ifc_file, "Model", "Body", "MODEL_VIEW")
        assert context  # Type checker.

        red_material = ifcopenshell.api.material.add_material(ifc_file, "Red Material")
        bpy.ops.bim.load_styles(style_type="IfcSurfaceStyle")
        bpy.ops.bim.enable_adding_presentation_style()
        bpy.data.scenes["Scene"].BIMStylesProperties.style_name = "Red"
        bpy.ops.bim.add_presentation_style()
        red_style = next((i for i in ifc_file.by_type("IfcSurfaceStyle") if i.Name == "Red"))
        ifcopenshell.api.style.assign_material_style(ifc_file, red_material, red_style, context)

        blue_material = ifcopenshell.api.material.add_material(ifc_file, "Blue Material")
        bpy.ops.bim.enable_adding_presentation_style()
        bpy.data.scenes["Scene"].BIMStylesProperties.style_name = "Blue"
        bpy.ops.bim.add_presentation_style()
        blue_style = next((i for i in ifc_file.by_type("IfcSurfaceStyle") if i.Name == "Blue"))
        ifcopenshell.api.style.assign_material_style(ifc_file, blue_material, blue_style, context)

        bpy.ops.bim.enable_adding_presentation_style()
        bpy.data.scenes["Scene"].BIMStylesProperties.style_name = "Green"
        bpy.ops.bim.add_presentation_style()

        if and_elements:
            self.setup_elements()

    def setup_elements(self) -> None:
        ifc_file = tool.Ifc.get()
        blue_material = next((i for i in ifc_file.by_type("IfcMaterial") if i.Name == "Blue Material"))
        blue_style = tool.Material.get_style(blue_material)

        # Element type.
        bpy.ops.mesh.primitive_cube_add(size=10, location=(0, 0, 4))
        element_type_obj = bpy.data.objects["Cube"]
        bpy.ops.bim.assign_class(ifc_class="IfcActuatorType", predefined_type="ELECTRICACTUATOR", userdefined_type="")
        element_type = tool.Ifc.get_entity(element_type_obj)

        # Setup occurrences.
        relating_type_id = element_type.id()
        bpy.ops.bim.add_constr_type_instance(relating_type_id=relating_type_id)
        simple = bpy.context.active_object
        simple.name = "Simple"

        # Occurrence with an opening.
        bpy.ops.bim.add_constr_type_instance(relating_type_id=relating_type_id)
        with_opening = bpy.context.active_object
        with_opening.name = "With Opening"
        bpy.ops.bim.add_potential_opening()
        tool.Blender.set_objects_selection(
            bpy.context, active_object=with_opening, selected_objects=[with_opening, bpy.data.objects["Opening"]]
        )
        bpy.ops.bim.add_opening()

        # Occurrence with a material override.
        bpy.ops.bim.add_constr_type_instance(relating_type_id=relating_type_id)
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
        red_material = next((i for i in ifc_file.by_type("IfcMaterial") if i.Name == "Red Material"))
        red_style = tool.Material.get_style(red_material)
        blue_style = next((i for i in ifc_file.by_type("IfcSurfaceStyle") if i.Name == "Blue"))

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
        red_material = next((i for i in ifc_file.by_type("IfcMaterial") if i.Name == "Red Material"))
        green_style = next((i for i in ifc_file.by_type("IfcSurfaceStyle") if i.Name == "Green"))

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
        red_material = next((i for i in ifc_file.by_type("IfcMaterial") if i.Name == "Red Material"))
        red_style = tool.Material.get_style(red_material)
        green_style = next((i for i in ifc_file.by_type("IfcSurfaceStyle") if i.Name == "Green"))

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
            buffer = np.empty(len(mesh.polygons), dtype=np.int32)
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
        red_material = next((i for i in ifc_file.by_type("IfcMaterial") if i.Name == "Red Material"))
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
