# This file was generated with the assistance of an AI coding tool.

from types import SimpleNamespace
from unittest import mock
from unittest.mock import MagicMock

import bpy
import ifcopenshell
import ifcopenshell.api.context
import ifcopenshell.api.geometry
import ifcopenshell.api.group
import ifcopenshell.api.material
import ifcopenshell.api.profile
import ifcopenshell.api.pset
import ifcopenshell.api.root
import ifcopenshell.api.structural
import ifcopenshell.util.element
import ifcopenshell.util.representation
import ifcopenshell.util.structural
import ifcopenshell.util.unit
import numpy as np
import pytest
from mathutils import Vector

import bonsai.tool as tool
from bonsai.bim.ifc import IfcStore
from bonsai.bim.module.structural.data import LoadGroupDecorationData
from bonsai.bim.module.structural.decorator import LoadsDecorator
from bonsai.bim.module.structural.operator import PickStructuralLoads
from bonsai.bim.module.structural.ui import BIM_PT_generate_structural_model
from test.bim.bootstrap import NewFile, NewIfc


class TestLoadBoundaryConditions(NewFile):
    def test_filtering_duplicate_names(self):
        ifc = ifcopenshell.file(schema="IFC4")
        tool.Ifc.set(ifc)
        ifc.createIfcBoundaryNodeCondition(Name="Fixed")
        ifc.createIfcBoundaryNodeCondition(Name="Fixed")
        ifc.createIfcBoundaryNodeCondition(Name="Pinned")
        props = tool.Structural.get_structural_props()
        props.filtered_boundary_conditions = True
        bpy.ops.bim.load_boundary_conditions()
        assert sorted(c.name for c in props.boundary_conditions) == ["Pinned"]


class TestLoadStructuralLoads(NewFile):
    def test_unused_only(self):
        ifc = ifcopenshell.file(schema="IFC4")
        tool.Ifc.set(ifc)
        point = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcStructuralPointConnection")
        used = ifcopenshell.api.structural.add_structural_load(
            ifc, name="Used", ifc_class="IfcStructuralLoadSingleForce"
        )
        ifcopenshell.api.structural.add_structural_load(ifc, name="Unused", ifc_class="IfcStructuralLoadSingleForce")
        activity = ifcopenshell.api.structural.add_structural_activity(
            ifc, applied_load=used, structural_member=point, ifc_class="IfcStructuralPointAction"
        )
        case = ifcopenshell.api.structural.add_structural_load_case(ifc, name="Case")
        ifcopenshell.api.group.assign_group(ifc, products=[activity], group=case)
        props = tool.Structural.get_structural_props()
        props.show_unused_loads_only = True  # Which lists the loads again.
        assert [load.name for load in props.structural_loads] == ["Unused"]
        props.show_unused_loads_only = False
        assert sorted(load.name for load in props.structural_loads) == ["Unused", "Used"]


class TestShowStructuralLoadCase(NewFile):
    def test_showing_and_hiding_a_load_case(self):
        ifc = ifcopenshell.file(schema="IFC4")
        tool.Ifc.set(ifc)
        model = ifcopenshell.api.structural.add_structural_analysis_model(ifc)
        case = ifcopenshell.api.structural.add_structural_load_case(ifc, name="Case")
        model.LoadedBy = [case]
        LoadGroupDecorationData.is_loaded = False
        props = tool.Structural.get_structural_props()
        props.activity_type = "Action"
        bpy.ops.bim.show_structural_load_case(load_case=case.id())
        assert props.show_loads and props.load_group_to_show == str(case.id())
        # Clicking the open eye of the case shown hides the loads.
        bpy.ops.bim.show_structural_load_case(load_case=case.id())
        assert not props.show_loads


def region(type, x, y, width, height, data=None):
    return SimpleNamespace(type=type, x=x, y=y, width=width, height=height, data=data)


class TestGetViewUnderMouse:
    def get(self, regions, x, y):
        area = SimpleNamespace(type="VIEW_3D", regions=regions)
        context = SimpleNamespace(window=SimpleNamespace(screen=SimpleNamespace(areas=[area])))
        return PickStructuralLoads.get_view_under_mouse(None, context, SimpleNamespace(mouse_x=x, mouse_y=y))

    def test_the_view_of_the_quarter_of_a_quad_view_under_the_mouse(self):
        left, right = region("WINDOW", 0, 0, 100, 100, "left"), region("WINDOW", 100, 0, 100, 100, "right")
        assert self.get([left, right], 150, 50)[1:] == (right, "right")

    def test_not_under_a_sidebar_lying_over_the_view(self):
        view = region("WINDOW", 0, 0, 200, 100, "view")
        sidebar = region("UI", 150, 0, 50, 100)
        assert self.get([view, sidebar], 175, 50) is None
        assert self.get([view, sidebar], 75, 50)[1] is view

    def test_a_hidden_sidebar_takes_nothing(self):
        view = region("WINDOW", 0, 0, 200, 100, "view")
        assert self.get([view, region("UI", 199, 0, 1, 100)], 199, 50)[1] is view


class TestPickLoads:
    def pick(self, x, y):
        LoadsDecorator.shader_info = [{}]
        LoadsDecorator.pickables = [{"tail": (0.0, 0.0, 0.0), "tip": (100.0, 0.0, 0.0), "activity": 7, "info": 0}]
        # Viewed from the front, as if X and Z were the region's x and y.
        project = lambda region, rv3d, point: Vector((point.x, point.z))
        with mock.patch("bonsai.bim.module.structural.decorator.location_3d_to_region_2d", project):
            try:
                return LoadsDecorator.pick(None, None, x, y)
            finally:
                LoadsDecorator.pickables, LoadsDecorator.shader_info = [], []

    def test_an_arrow_within_a_few_pixels(self):
        assert self.pick(60, 5)["activity"] == 7
        assert self.pick(60, 15) is None

    def test_not_at_its_tail_where_its_point_is_selected(self):
        assert self.pick(5, 0) is None


class TestGenerationSchemas(NewFile):
    def test_ifc2x3_is_rejected_without_writing(self, capsys):
        tool.Project.get_project_props().export_schema = "IFC2X3"
        bpy.ops.bim.create_project()
        ifc = tool.Ifc.get()
        ifcopenshell.api.structural.add_structural_analysis_model(ifc)
        before = ifc.to_string()
        bpy.ops.bim.generate_structural_model()
        assert "not supported for IFC2X3" in capsys.readouterr().out
        assert ifc.to_string() == before

    def test_ifc4x3_member_has_section_and_material(self):
        tool.Project.get_project_props().export_schema = "IFC4X3_ADD2"
        bpy.ops.bim.create_project()
        ifc = tool.Ifc.get()
        model_context = ifcopenshell.util.representation.get_context(ifc, "Model")
        body = ifcopenshell.api.context.add_context(
            ifc, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=model_context
        )
        profile = ifcopenshell.api.profile.add_parameterized_profile(ifc, ifc_class="IfcRectangleProfileDef")
        profile.XDim, profile.YDim = 0.2, 0.3
        material = ifcopenshell.api.material.add_material(ifc, name="Steel")
        ifcopenshell.api.structural.add_structural_analysis_model(ifc)
        source = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcColumn")
        representation = ifcopenshell.api.geometry.add_profile_representation(
            ifc, context=body, profile=profile, depth=3
        )
        ifcopenshell.api.geometry.assign_representation(ifc, product=source, representation=representation)
        ifcopenshell.api.material.assign_material(ifc, products=[source], material=material)
        obj = bpy.data.objects.new("Column", bpy.data.meshes.new("Column"))
        bpy.context.scene.collection.objects.link(obj)
        tool.Ifc.link(source, obj)
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.context.view_layer.update()
        bpy.ops.bim.generate_structural_model()
        member = ifcopenshell.util.structural.get_structural_members(source)[0]
        member_profile = ifcopenshell.util.element.get_material(member, should_skip_usage=True).MaterialProfiles[0]
        assert member_profile.Profile == profile and member_profile.Material == material


class TestGenerateStructuralModel(NewIfc):
    def test_update_section_without_changing_the_building(self):
        ifc = tool.Ifc.get()
        ifcopenshell.api.structural.add_structural_analysis_model(ifc)
        model_context = ifcopenshell.util.representation.get_context(ifc, "Model")
        body = ifcopenshell.api.context.add_context(
            ifc, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=model_context
        )
        sets = []
        for name, size in (("Steel", 0.2), ("Timber", 0.4)):
            profile = ifcopenshell.api.profile.add_parameterized_profile(ifc, ifc_class="IfcRectangleProfileDef")
            profile.XDim, profile.YDim = size, size
            material = ifcopenshell.api.material.add_material(ifc, name=name)
            profile_set = ifcopenshell.api.material.add_material_set(ifc, set_type="IfcMaterialProfileSet")
            ifcopenshell.api.material.add_profile(ifc, profile_set=profile_set, material=material, profile=profile)
            sets.append(profile_set)
        source = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcBeam")
        representation = ifcopenshell.api.geometry.add_profile_representation(
            ifc, context=body, profile=sets[0].MaterialProfiles[0].Profile, depth=3
        )
        ifcopenshell.api.geometry.assign_representation(ifc, product=source, representation=representation)
        ifcopenshell.api.geometry.edit_object_placement(ifc, product=source)
        ifcopenshell.api.material.assign_material(
            ifc, products=[source], type="IfcMaterialProfileSetUsage", material=sets[0]
        )
        obj = bpy.data.objects.new("Physical beam", bpy.data.meshes.new("Physical beam"))
        bpy.context.scene.collection.objects.link(obj)
        tool.Ifc.link(source, obj)
        tool.Geometry.link(representation, obj.data)
        tool.Geometry.reload_representation(obj)
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.context.view_layer.update()

        bpy.ops.bim.generate_structural_model()
        member = ifcopenshell.util.structural.get_structural_members(source)[0]
        assert ifcopenshell.util.element.get_material(member, should_skip_usage=True) == sets[0]
        shared_material = ifcopenshell.api.material.add_material(ifc, name="Updated steel")
        ifcopenshell.api.material.edit_profile(ifc, profile=sets[0].MaterialProfiles[0], material=shared_material)
        assert ifcopenshell.util.element.get_materials(source) == [shared_material]
        assert ifcopenshell.util.element.get_materials(member) == [shared_material]
        assert tool.Structural.get_physical_member_data(obj)
        member_obj = tool.Ifc.get_object(member)
        assert member_obj and member_obj.type == "MESH" and len(member_obj.data.vertices) == 2
        if not bpy.context.scene.collection.objects.get(member_obj.name):
            bpy.context.scene.collection.objects.link(member_obj)
        bpy.context.view_layer.update()
        bpy.ops.object.select_all(action="DESELECT")
        member_obj.select_set(True)
        bpy.context.view_layer.objects.active = member_obj
        bpy.ops.bim.assign_material_to_selected(material=sets[1].id(), should_auto_assign_usage=False)
        assert ifcopenshell.util.element.get_material(member, should_skip_usage=True) == sets[1]
        assert ifcopenshell.util.element.get_material(source, should_skip_usage=True) == sets[0]
        assert representation.Items[0].SweptArea == sets[0].MaterialProfiles[0].Profile
        bpy.ops.object.select_all(action="DESELECT")
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.bim.generate_structural_model()
        assert ifcopenshell.util.element.get_material(member, should_skip_usage=True) == sets[0]
        assert ifcopenshell.util.element.get_material(source, should_skip_usage=True) == sets[0]

        bpy.ops.object.select_all(action="DESELECT")
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.bim.assign_material_to_selected(material=sets[1].id())
        assert ifcopenshell.util.element.get_material(source, should_skip_usage=True) == sets[1]
        assert ifcopenshell.util.element.get_material(member, should_skip_usage=True) == sets[0]
        bpy.ops.bim.generate_structural_model()
        assert ifcopenshell.util.element.get_material(member, should_skip_usage=True) == sets[1]
        beam_type = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcBeamType")
        ifcopenshell.api.material.assign_material(ifc, products=[beam_type], material=sets[0])
        bpy.ops.bim.assign_type(relating_type=beam_type.id(), related_object=obj.name)
        assert ifcopenshell.util.element.get_material(source, should_skip_usage=True) == sets[0]
        assert ifcopenshell.util.element.get_material(member, should_skip_usage=True) == sets[1]
        bpy.ops.bim.generate_structural_model()
        assert ifcopenshell.util.element.get_material(member, should_skip_usage=True) == sets[0]
        bpy.ops.bim.unassign_material(obj=member_obj.name)
        assert not ifcopenshell.util.element.get_material(member)
        assert ifcopenshell.util.element.get_material(source, should_skip_usage=True) == sets[0]
        bpy.ops.bim.generate_structural_model()
        assert ifcopenshell.util.element.get_material(member, should_skip_usage=True) == sets[0]

    def test_generation_only_processes_selected_beams_and_columns(self, capsys):
        ifc = tool.Ifc.get()
        ifcopenshell.api.structural.add_structural_analysis_model(ifc)
        model_context = ifcopenshell.util.representation.get_context(ifc, "Model")
        body = ifcopenshell.api.context.add_context(
            ifc, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=model_context
        )
        profile = ifcopenshell.api.profile.add_parameterized_profile(ifc, ifc_class="IfcRectangleProfileDef")
        profile.XDim, profile.YDim = 0.2, 0.3
        beam = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcBeam")
        wall = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcWall")
        for element, name in ((beam, "Beam"), (wall, "Wall"), (None, "Non-IFC")):
            obj = bpy.data.objects.new(name, bpy.data.meshes.new(name))
            bpy.context.scene.collection.objects.link(obj)
            if element:
                representation = ifcopenshell.api.geometry.add_profile_representation(
                    ifc, context=body, profile=profile, depth=3
                )
                ifcopenshell.api.geometry.assign_representation(ifc, product=element, representation=representation)
                tool.Ifc.link(element, obj)
                tool.Geometry.link(representation, obj.data)
            obj.select_set(True)
        bpy.context.view_layer.update()
        before = ifc.to_string()
        assert bpy.ops.bim.generate_structural_model() == {"CANCELLED"}
        assert "Skipped 1 objects with missing or unsupported materials" in capsys.readouterr().out
        assert ifc.to_string() == before
        assert not ifc.by_type("IfcStructuralCurveMember")
        material = ifcopenshell.api.material.add_material(ifc, name="Steel")
        ifcopenshell.api.material.assign_material(ifc, products=[beam], material=material)
        bpy.ops.bim.generate_structural_model()
        member = ifcopenshell.util.structural.get_structural_members(beam)[0]
        assert not ifcopenshell.util.structural.get_structural_members(wall)
        member_obj = tool.Ifc.get_object(member)
        if not bpy.context.scene.collection.objects.get(member_obj.name):
            bpy.context.scene.collection.objects.link(member_obj)
        bpy.context.view_layer.update()
        bpy.ops.object.select_all(action="DESELECT")
        member_obj.select_set(True)
        tool.Ifc.get_object(beam).location.x = 1
        bpy.context.view_layer.update()
        bpy.ops.bim.generate_structural_model()
        assert "No eligible profile beams or columns selected" in capsys.readouterr().out
        assert member_obj.location.x == pytest.approx(0)
        member_obj.select_set(False)
        tool.Ifc.get_object(beam).select_set(True)
        bpy.ops.bim.generate_structural_model()
        assert member_obj.location.x == pytest.approx(1)
        bpy.ops.bim.unassign_material(obj="Beam")
        assert not ifcopenshell.util.element.get_material(beam)
        assert ifcopenshell.util.element.get_materials(member) == [material]

    @pytest.mark.parametrize(
        "ifc_class,rotation,initial_axis,updated_axis,profile_axis,member_direction",
        [
            ("IfcColumn", (0, 0, np.pi / 2), (0, -1, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1)),
            (
                "IfcColumn",
                (0, 0, np.pi / 4),
                (-(2**-0.5), -(2**-0.5), 0),
                (2**-0.5, -(2**-0.5), 0),
                (2**-0.5, 2**-0.5, 0),
                (0, 0, 1),
            ),
            ("IfcBeam", (0, np.pi / 2, 0), (0, 0, 1), (0, -1, 0), (0, 0, -1), (1, 0, 0)),
        ],
    )
    def test_member_orientation_follows_profile(
        self, ifc_class, rotation, initial_axis, updated_axis, profile_axis, member_direction
    ):
        ifc = tool.Ifc.get()
        model_context = ifcopenshell.util.representation.get_context(ifc, "Model")
        body = ifcopenshell.api.context.add_context(
            ifc, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=model_context
        )
        profile = ifcopenshell.api.profile.add_parameterized_profile(ifc, ifc_class="IfcRectangleProfileDef")
        profile.XDim, profile.YDim = 0.2, 0.3
        ifcopenshell.api.structural.add_structural_analysis_model(ifc)
        source = ifcopenshell.api.root.create_entity(ifc, ifc_class=ifc_class)
        material = ifcopenshell.api.material.add_material(ifc, name="Steel")
        ifcopenshell.api.material.assign_material(ifc, products=[source], material=material)
        representation = ifcopenshell.api.geometry.add_profile_representation(
            ifc, context=body, profile=profile, depth=3, placement_zx_axes=(None, (0.0, 1.0, 0.0))
        )
        ifcopenshell.api.geometry.assign_representation(ifc, product=source, representation=representation)
        obj = bpy.data.objects.new(ifc_class, bpy.data.meshes.new(ifc_class))
        bpy.context.scene.collection.objects.link(obj)
        tool.Ifc.link(source, obj)
        obj.rotation_euler = rotation
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.context.view_layer.update()

        bpy.ops.bim.generate_structural_model()
        member = ifcopenshell.util.structural.get_structural_members(source)[0]
        assert member.Axis.DirectionRatios == pytest.approx(initial_axis, abs=1e-6)
        representation.Items[0].Position.RefDirection.DirectionRatios = (-1.0, 0.0, 0.0)
        bpy.ops.bim.generate_structural_model()
        assert member.Axis.DirectionRatios == pytest.approx(updated_axis, abs=1e-6)

        profile.Position = ifc.createIfcAxis2Placement2D(
            ifc.createIfcCartesianPoint((0.0, 0.0)), ifc.createIfcDirection((0.0, 1.0))
        )
        bpy.ops.bim.generate_structural_model()
        assert member.Axis.DirectionRatios == pytest.approx(profile_axis, abs=1e-6)
        member.Axis.DirectionRatios = tuple(float(value) for value in member_direction)
        bpy.ops.bim.generate_structural_model()
        assert member.Axis.DirectionRatios == pytest.approx(profile_axis, abs=1e-6)

    def test_panel_has_only_generate_button(self):
        ifcopenshell.api.structural.add_structural_analysis_model(tool.Ifc.get())
        layout = MagicMock()
        BIM_PT_generate_structural_model.draw(SimpleNamespace(layout=layout), bpy.context)
        layout.prop.assert_called_once_with(tool.Structural.get_structural_props(), "generation_merge_tolerance")
        layout.operator.assert_any_call("bim.generate_structural_model", icon="MOD_SIMPLIFY")
        layout.box.assert_not_called()
        assert [call.args[0] for call in layout.operator.call_args_list] == ["bim.generate_structural_model"]
        assert "update_structural_model" not in dir(bpy.ops.bim)
        assert "sync_only" not in bpy.ops.bim.generate_structural_model.get_rna_type().properties

    @pytest.mark.parametrize("source_count", [0, 2])
    def test_unlinked_or_ambiguous_source_preserves_member(self, source_count, capsys):
        ifc = tool.Ifc.get()
        model = ifcopenshell.api.structural.add_structural_analysis_model(ifc)
        member = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcStructuralCurveMember")
        ifcopenshell.api.structural.assign_structural_analysis_model(
            ifc, products=[member], structural_analysis_model=model
        )
        for _ in range(source_count):
            source = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcColumn")
            ifcopenshell.api.structural.assign_product(ifc, relating_product=member, related_object=source)
            obj = bpy.data.objects.new("Column", bpy.data.meshes.new("Column"))
            bpy.context.scene.collection.objects.link(obj)
            tool.Ifc.link(source, obj)
            obj.select_set(True)

        assert bpy.ops.bim.generate_structural_model(structural_model=model.id()) == {"CANCELLED"}
        message = "ambiguous source relationships" if source_count else "No eligible profile beams"
        assert message in capsys.readouterr().out
        assert member in ifc.by_type("IfcStructuralCurveMember")

    def test_invalid_snapped_orientation_cancels_without_changes(self, capsys):
        ifc = tool.Ifc.get()
        model_context = ifcopenshell.util.representation.get_context(ifc, "Model")
        body = ifcopenshell.api.context.add_context(
            ifc, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=model_context
        )
        profile = ifcopenshell.api.profile.add_parameterized_profile(ifc, ifc_class="IfcRectangleProfileDef")
        profile.XDim, profile.YDim = 0.2, 0.3
        ifcopenshell.api.structural.add_structural_analysis_model(ifc)
        source = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcColumn")
        material = ifcopenshell.api.material.add_material(ifc, name="Steel")
        ifcopenshell.api.material.assign_material(ifc, products=[source], material=material)
        representation = ifcopenshell.api.geometry.add_profile_representation(
            ifc, context=body, profile=profile, depth=3
        )
        ifcopenshell.api.geometry.assign_representation(ifc, product=source, representation=representation)
        obj = bpy.data.objects.new("Column", bpy.data.meshes.new("Column"))
        bpy.context.scene.collection.objects.link(obj)
        tool.Ifc.link(source, obj)
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        other_source = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcColumn")
        ifcopenshell.api.material.assign_material(ifc, products=[other_source], material=material)
        other_representation = ifcopenshell.api.geometry.add_profile_representation(
            ifc, context=body, profile=profile, depth=3
        )
        ifcopenshell.api.geometry.assign_representation(ifc, product=other_source, representation=other_representation)
        other_obj = bpy.data.objects.new("Other column", bpy.data.meshes.new("Other column"))
        bpy.context.scene.collection.objects.link(other_obj)
        tool.Ifc.link(other_source, other_obj)
        other_obj.location.x = 4
        other_obj.select_set(True)
        bpy.context.view_layer.update()
        assert bpy.ops.bim.generate_structural_model() == {"FINISHED"}
        member = ifcopenshell.util.structural.get_structural_members(source)[0]
        other_member = ifcopenshell.util.structural.get_structural_members(other_source)[0]
        for item in (member, other_member):
            start = min(
                item.ConnectedBy, key=lambda rel: tool.Ifc.get_object(rel.RelatedStructuralConnection).location.z
            )
            external = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcStructuralCurveMember")
            ifcopenshell.api.structural.add_structural_member_connection(
                ifc,
                relating_structural_member=external,
                related_structural_connection=start.RelatedStructuralConnection,
            )
        other_obj.location.x = 5
        bpy.context.view_layer.update()
        tool.Structural.get_structural_props().generation_merge_tolerance = 0.1
        before = ifc.to_string()
        history_before = list(IfcStore.history)
        future_before = list(IfcStore.future)
        objects_before = set(bpy.data.objects)
        positions_before = {obj: obj.location.copy() for obj in objects_before}
        axis = np.array(((0.0, 0.05, 0.05), (0.0, 1.0, 0.0)))
        profile_direction = np.array((0.0, 1.0, 0.0))
        get_member_data = tool.Structural.get_physical_member_data
        with mock.patch.object(
            tool.Structural,
            "get_physical_member_data",
            side_effect=lambda source_obj: (axis, profile_direction)
            if source_obj == obj
            else get_member_data(source_obj),
        ):
            assert bpy.ops.bim.generate_structural_model() == {"CANCELLED"}
        assert "Profile orientation is parallel to the updated structural member" in capsys.readouterr().out
        assert ifc.to_string() == before
        assert IfcStore.history == history_before
        assert IfcStore.future == future_before
        assert set(bpy.data.objects) == objects_before
        assert all(obj.location == position for obj, position in positions_before.items())

    @pytest.mark.parametrize("reverse_link", [False, True])
    @pytest.mark.parametrize("scene_tolerance", [None, 0.2])
    def test_explicit_refresh_of_linked_member(self, reverse_link, scene_tolerance, capsys):
        ifc = tool.Ifc.get()
        model_context = ifcopenshell.util.representation.get_context(ifc, "Model")
        body = ifcopenshell.api.context.add_context(
            ifc, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=model_context
        )
        profile = ifcopenshell.api.profile.add_parameterized_profile(ifc, ifc_class="IfcRectangleProfileDef")
        profile.XDim, profile.YDim = 0.2, 0.3
        model = ifcopenshell.api.structural.add_structural_analysis_model(ifc)
        source = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcColumn", name="Column")
        material = ifcopenshell.api.material.add_material(ifc, name="Steel")
        ifcopenshell.api.material.assign_material(ifc, products=[source], material=material)
        representation = ifcopenshell.api.geometry.add_profile_representation(
            ifc, context=body, profile=profile, depth=3.1
        )
        ifcopenshell.api.geometry.assign_representation(ifc, product=source, representation=representation)
        obj = bpy.data.objects.new("Column", bpy.data.meshes.new("Column"))
        bpy.context.scene.collection.objects.link(obj)
        tool.Ifc.link(source, obj)
        obj.location.z = 0.13
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.context.view_layer.update()
        bpy.ops.bim.generate_structural_model()
        member = ifc.by_type("IfcStructuralCurveMember")[0]
        reopened = ifcopenshell.file.from_string(ifc.to_string())
        assert ifcopenshell.util.structural.get_building_elements(reopened.by_guid(member.GlobalId)) == [
            reopened.by_guid(source.GlobalId)
        ]
        if reverse_link:
            relation = next(rel for rel in source.HasAssignments if rel.is_a("IfcRelAssignsToProduct"))
            relation.RelatingProduct = source
            relation.RelatedObjects = [member]
        nodes = ifc.by_type("IfcStructuralPointConnection")
        assert all(
            not ifcopenshell.util.element.get_pset(item, "BBIM_StructuralGeneration")
            for item in [model, member, *nodes]
        )
        for item, properties in (
            (model, {"MergeTolerance": 0.1}),
            (member, {"Source": source.GlobalId, "SourceAxis": "old", "Keep": "value"}),
            (nodes[0], {"Generated": True}),
        ):
            pset = ifcopenshell.api.pset.add_pset(ifc, product=item, name="BBIM_StructuralGeneration")
            ifcopenshell.api.pset.edit_pset(ifc, pset=pset, properties=properties)
        props = tool.Structural.get_structural_props()
        if scene_tolerance is None:
            props.property_unset("generation_merge_tolerance")
        else:
            props.generation_merge_tolerance = scene_tolerance
        obj.location.x = 2
        bpy.context.view_layer.update()
        assert tool.Ifc.get_object(member).location.x == pytest.approx(0)
        ifc_before_check = ifc.to_string()
        history_before_check = len(IfcStore.history)
        previous_transaction = IfcStore.history[-1]["key"]
        assert bpy.ops.bim.generate_structural_model() == {"FINISHED"}
        assert len(IfcStore.history) == history_before_check + 1
        update_transaction = IfcStore.history[-1]["key"]
        ifc_after_update = ifc.to_string()
        IfcStore.undo(until_key=previous_transaction)
        assert ifc.to_string() == ifc_before_check
        IfcStore.redo(until_key=update_transaction)
        assert ifc.to_string() == ifc_after_update
        assert tool.Ifc.get_object(member).location.x == pytest.approx(2)
        assert props.generation_merge_tolerance == pytest.approx(0.01 if scene_tolerance is None else scene_tolerance)
        assert ifcopenshell.util.element.get_pset(model, "BBIM_StructuralGeneration")["MergeTolerance"] == 0.1
        assert ifcopenshell.util.element.get_pset(nodes[0], "BBIM_StructuralGeneration")["Generated"] is True
        member_pset = ifcopenshell.util.element.get_pset(member, "BBIM_StructuralGeneration")
        assert member_pset["Source"] == source.GlobalId
        assert member_pset["SourceAxis"] == "old"
        assert member_pset["Keep"] == "value"
        member_obj = tool.Ifc.get_object(member)
        tool.Structural.get_structural_props().generation_merge_tolerance = 0.1
        member_obj.data.vertices[1].co.x = 0.3
        bpy.context.view_layer.update()
        member_obj.location.x = 2.15
        bpy.context.view_layer.update()
        assert member_obj.location.x == pytest.approx(2.15)
        bpy.ops.bim.generate_structural_model()
        assert member_obj.location.x == pytest.approx(2)
        assert member_obj.data.vertices[1].co.x == pytest.approx(0)
        tool.Geometry.delete_ifc_object(obj)
        bpy.ops.bim.generate_structural_model()
        assert "No eligible profile beams or columns selected" in capsys.readouterr().out
        assert member in ifc.by_type("IfcStructuralCurveMember")
        assert len(ifc.by_type("IfcStructuralPointConnection")) == 2

    @pytest.mark.parametrize("tolerance,point_count", [(0.0, 4), (0.1, 3)])
    @pytest.mark.parametrize("reverse_link", [False, True])
    def test_selected_columns_are_connected_and_assigned(self, tolerance, point_count, reverse_link):
        ifc = tool.Ifc.get()
        model_context = ifcopenshell.util.representation.get_context(ifc, "Model")
        body = ifcopenshell.api.context.add_context(
            ifc, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=model_context
        )
        profile = ifcopenshell.api.profile.add_parameterized_profile(ifc, ifc_class="IfcRectangleProfileDef")
        profile.XDim, profile.YDim = 0.2, 0.3
        model = ifcopenshell.api.structural.add_structural_analysis_model(ifc)
        material = ifcopenshell.api.material.add_material(ifc, name="Steel")
        tool.Structural.get_structural_props().generation_merge_tolerance = tolerance
        sources = []
        obj = None
        for index, height in enumerate((0.0, 3.05 if tolerance else 3.0)):
            source = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcColumn", name=f"Column {index}")
            ifcopenshell.api.material.assign_material(ifc, products=[source], material=material)
            representation = ifcopenshell.api.geometry.add_profile_representation(
                ifc, context=body, profile=profile, depth=3
            )
            ifcopenshell.api.geometry.assign_representation(ifc, product=source, representation=representation)
            obj = bpy.data.objects.new(source.Name, bpy.data.meshes.new(source.Name))
            bpy.context.scene.collection.objects.link(obj)
            tool.Ifc.link(source, obj)
            obj.location.z = height
            obj.select_set(True)
            sources.append(source)
        assert obj is not None
        bpy.context.view_layer.objects.active = obj
        bpy.context.view_layer.update()

        assert bpy.ops.bim.generate_structural_model() == {"FINISHED"}
        members = ifc.by_type("IfcStructuralCurveMember")
        points = ifc.by_type("IfcStructuralPointConnection")
        assert len(members) == 2
        assert len(points) == point_count
        assert len(ifc.by_type("IfcRelConnectsStructuralMember")) == 4
        assert all(member.Axis for member in members)
        assert all(
            ifcopenshell.util.representation.get_representation(item, "Model", "Reference", "GRAPH_VIEW")
            for item in members + points
        )
        assert all(any(rel.RelatingProduct in members for rel in source.HasAssignments) for source in sources)
        assert all(
            not ifcopenshell.util.element.get_pset(item, "BBIM_StructuralGeneration")
            for item in [model, *members, *points]
        )
        if reverse_link:
            for source in sources:
                relation = next(rel for rel in source.HasAssignments if rel.is_a("IfcRelAssignsToProduct"))
                member = relation.RelatingProduct
                relation.RelatingProduct = source
                relation.RelatedObjects = [member]
        assert set(model.IsGroupedBy[0].RelatedObjects) == set(members + points)
        assert all(tool.Ifc.get_object(item) for item in members + points)
        bpy.ops.bim.generate_structural_model()
        assert len(ifc.by_type("IfcStructuralCurveMember")) == 2
        original_positions = {member.id(): tool.Ifc.get_object(member).location.copy() for member in members}
        for source in sources:
            tool.Ifc.get_object(source).location.x += 2
        bpy.context.view_layer.update()
        bpy.ops.object.select_all(action="DESELECT")
        bpy.ops.bim.generate_structural_model()
        for member in members:
            assert tool.Ifc.get_object(member).location == original_positions[member.id()]
        for source in sources:
            tool.Ifc.get_object(source).select_set(True)
        bpy.ops.bim.generate_structural_model()
        for member in members:
            assert tool.Ifc.get_object(member).location.x == pytest.approx(original_positions[member.id()].x + 2)
        assert len(ifc.by_type("IfcStructuralPointConnection")) == point_count
        source = sources[1]
        extrusion = ifcopenshell.util.representation.get_representation(source, "Model", "Body", "MODEL_VIEW").Items[0]
        extrusion.Depth += 1 / ifcopenshell.util.unit.calculate_unit_scale(ifc)
        bpy.ops.bim.generate_structural_model()
        member = ifcopenshell.util.structural.get_structural_members(source)[0]
        assert tool.Ifc.get_object(member).data.vertices[1].co.length == pytest.approx(4, abs=0.1)
        shared_node = next(
            (node for node in ifc.by_type("IfcStructuralPointConnection") if len(node.ConnectsStructuralMembers) == 2),
            None,
        )
        shared_condition = (
            ifcopenshell.api.structural.add_structural_boundary_condition(ifc, connection=shared_node)
            if shared_node
            else None
        )
        tool.Ifc.get_object(sources[0]).location.x += 1
        tool.Ifc.get_object(sources[0]).rotation_euler.y = 1.5707963267948966
        bpy.context.view_layer.update()
        bpy.ops.bim.generate_structural_model()
        assert len(ifc.by_type("IfcStructuralPointConnection")) == 4
        assert len(ifc.by_type("IfcRelConnectsStructuralMember")) == 4
        if shared_condition:
            assert shared_node.AppliedCondition == shared_condition

        rotated_member = ifcopenshell.util.structural.get_structural_members(sources[0])[0]
        direction = np.array(tool.Ifc.get_object(rotated_member).data.vertices[1].co)
        assert np.dot(direction, rotated_member.Axis.DirectionRatios) == pytest.approx(0, abs=1e-6)
        tool.Ifc.get_object(sources[0]).location.x -= 1
        tool.Ifc.get_object(sources[0]).rotation_euler.y = 0
        bpy.context.view_layer.update()
        bpy.ops.bim.generate_structural_model()
        assert len(ifc.by_type("IfcStructuralPointConnection")) == (3 if tolerance else 4)
        new_source = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcColumn", name="Later Column")
        ifcopenshell.api.material.assign_material(ifc, products=[new_source], material=material)
        representation = ifcopenshell.api.geometry.add_profile_representation(
            ifc, context=body, profile=profile, depth=3
        )
        ifcopenshell.api.geometry.assign_representation(ifc, product=new_source, representation=representation)
        obj = bpy.data.objects.new(new_source.Name, bpy.data.meshes.new(new_source.Name))
        bpy.context.scene.collection.objects.link(obj)
        tool.Ifc.link(new_source, obj)
        obj.location = (2, 0, 7.05 if tolerance else 7.0)
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.context.view_layer.update()
        tool.Structural.get_structural_props().generation_merge_tolerance = tolerance
        bpy.ops.bim.generate_structural_model()
        assert len(ifc.by_type("IfcStructuralCurveMember")) == 3
        assert len(ifc.by_type("IfcStructuralPointConnection")) == (4 if tolerance else 6)
        removed_member = ifcopenshell.util.structural.get_structural_members(sources[0])[0]
        load = ifcopenshell.api.structural.add_structural_load(ifc)
        activity = ifcopenshell.api.structural.add_structural_activity(
            ifc, applied_load=load, structural_member=removed_member, ifc_class="IfcStructuralLinearAction"
        )
        activity_id = activity.id()
        node = next(
            rel.RelatedStructuralConnection
            for rel in removed_member.ConnectedBy
            if len(rel.RelatedStructuralConnection.ConnectsStructuralMembers) == 1
        )
        condition = ifcopenshell.api.structural.add_structural_boundary_condition(ifc, connection=node)
        condition_id = condition.id()
        tool.Geometry.delete_ifc_object(tool.Ifc.get_object(sources[0]))
        bpy.ops.bim.generate_structural_model()
        assert removed_member in ifc.by_type("IfcStructuralCurveMember")
        assert len(ifc.by_type("IfcStructuralPointConnection")) == (4 if tolerance else 6)
        assert len(ifc.by_type("IfcRelConnectsStructuralMember")) == 6
        assert any(item.id() == activity_id for item in ifc.by_type("IfcStructuralActivity"))
        assert any(item.id() == condition_id for item in ifc.by_type("IfcBoundaryCondition"))
        if shared_condition:
            assert shared_node.AppliedCondition == shared_condition
        other_member = ifcopenshell.util.structural.get_structural_members(sources[1])[0]
        selected_member = ifcopenshell.util.structural.get_structural_members(new_source)[0]
        other_position = tool.Ifc.get_object(other_member).location.copy()
        selected_position = tool.Ifc.get_object(selected_member).location.copy()
        for source in (sources[1], new_source):
            tool.Ifc.get_object(source).location.x += 1
        bpy.context.view_layer.update()
        bpy.ops.object.select_all(action="DESELECT")
        tool.Ifc.get_object(new_source).select_set(True)
        bpy.ops.bim.generate_structural_model()
        assert tool.Ifc.get_object(other_member).location == other_position
        assert tool.Ifc.get_object(selected_member).location.x == pytest.approx(selected_position.x + 1)

    def test_generation_scene_state_survives_blend_save(self, tmp_path):
        props = tool.Structural.get_structural_props()
        props.generation_merge_tolerance = 0.25
        path = str(tmp_path / "structural.blend")
        bpy.ops.wm.save_as_mainfile(filepath=path)
        props.generation_merge_tolerance = 0
        bpy.ops.wm.open_mainfile(filepath=path)
        props = tool.Structural.get_structural_props()
        assert props.generation_merge_tolerance == pytest.approx(0.25)
