# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026 Ryan Schultz
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

# This file was generated with the assistance of an AI coding tool.

import math
from types import SimpleNamespace

import ifcopenshell
import ifcopenshell.api.group
import ifcopenshell.api.root
import ifcopenshell.api.structural
import numpy as np

import bonsai.core.tool
import bonsai.tool as tool
from bonsai.bim.module.structural.operator import get_load_attributes
from bonsai.tool.structural import Structural as subject
from test.bim.bootstrap import NewFile


class TestImplementsTool(NewFile):
    def test_run(self):
        assert isinstance(subject(), bonsai.core.tool.Structural)


class TestGetInPlaneComponents(NewFile):
    def test_an_angle_above_the_horizontal(self):
        x, z = subject.get_in_plane_components("ANGLE", magnitude=10, angle=30)
        assert math.isclose(x, 10 * math.cos(math.radians(30)))
        assert math.isclose(z, 5)

    def test_a_slope(self):
        x, z = subject.get_in_plane_components("SLOPE", magnitude=10, rise=5, run=12)
        assert math.isclose(x, 120 / 13)
        assert math.isclose(z, 50 / 13)

    def test_directions_measure_from_the_nearest_horizontal(self):
        x, z = subject.get_in_plane_components("ANGLE", magnitude=100, angle=40, direction="UP_LEFT")
        assert math.isclose(x, -100 * math.cos(math.radians(40)))
        assert math.isclose(z, 100 * math.sin(math.radians(40)))
        x, z = subject.get_in_plane_components("SLOPE", magnitude=200, rise=3, run=4, direction="DOWN_LEFT")
        assert math.isclose(x, -160)
        assert math.isclose(z, -120)
        x, z = subject.get_in_plane_components("ANGLE", magnitude=1, angle=60, direction="DOWN_RIGHT")
        assert x > 0 and z < 0

    def test_a_zero_slope_gives_no_force(self):
        assert subject.get_in_plane_components("SLOPE", magnitude=10, rise=0, run=0) == (0.0, 0.0)


class TestGetSimpleSlope(NewFile):
    def test_reducing_to_small_whole_numbers(self):
        assert subject.get_simple_slope(-160, -120) == (-3, -4)
        assert subject.get_simple_slope(134.16407864998737, -268.3281572999747) == (-2, 1)

    def test_axis_aligned_components(self):
        assert subject.get_simple_slope(5, 0) == (0.0, 1.0)
        assert subject.get_simple_slope(0, -5) == (-1.0, 0.0)

    def test_no_force_gives_a_unit_slope(self):
        assert subject.get_simple_slope(0, 0) == (1.0, 1.0)

    def test_falling_back_to_a_unit_slope(self):
        rise, run = subject.get_simple_slope(3, 7.1)
        assert math.isclose(math.hypot(rise, run), 1)
        assert math.isclose(rise / run, 7.1 / 3)


class TestLoadCases(NewFile):
    def make_loaded_model(self, ifc_file, case_class, predefined_type):
        model = ifcopenshell.api.structural.add_structural_analysis_model(ifc_file)
        point = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcStructuralPointConnection")
        ifcopenshell.api.structural.assign_structural_analysis_model(
            ifc_file, products=[point], structural_analysis_model=model
        )
        case = ifcopenshell.api.root.create_entity(ifc_file, ifc_class=case_class, predefined_type=predefined_type)
        load = ifcopenshell.api.structural.add_structural_load(ifc_file, ifc_class="IfcStructuralLoadSingleForce")
        activity = ifcopenshell.api.structural.add_structural_activity(
            ifc_file, applied_load=load, structural_member=point, ifc_class="IfcStructuralPointAction"
        )
        ifcopenshell.api.group.assign_group(ifc_file, products=[activity], group=case)
        return model, point, case, activity

    def test_a_load_group_typed_load_case_is_one(self):
        ifc_file = ifcopenshell.file(schema="IFC4")
        tool.Ifc.set(ifc_file)
        group = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcStructuralLoadGroup")
        group.PredefinedType = "LOAD_CASE"
        other = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcStructuralLoadGroup")
        other.PredefinedType = "LOAD_GROUP"
        case = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcStructuralLoadCase")
        assert subject.is_load_case(group) and subject.is_load_case(case) and not subject.is_load_case(other)
        assert set(subject.get_load_cases()) == {group, case}

    def test_cases_loading_a_model_it_does_not_list(self):
        # As RFEM writes them: a load group typed LOAD_CASE, and the model's LoadedBy left empty.
        ifc_file = ifcopenshell.file(schema="IFC4")
        tool.Ifc.set(ifc_file)
        model, point, case, activity = self.make_loaded_model(ifc_file, "IfcStructuralLoadGroup", "LOAD_CASE")
        assert not model.LoadedBy
        assert subject.get_load_cases(model) == [case]

    def test_loads_in_a_load_group_within_the_case_count(self):
        ifc_file = ifcopenshell.file(schema="IFC4")
        tool.Ifc.set(ifc_file)
        model, point, case, activity = self.make_loaded_model(ifc_file, "IfcStructuralLoadGroup", "LOAD_CASE")
        ifcopenshell.api.group.unassign_group(ifc_file, products=[activity], group=case)
        group = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcStructuralLoadGroup")
        group.PredefinedType = "LOAD_GROUP"
        ifcopenshell.api.group.assign_group(ifc_file, products=[activity], group=group)
        ifcopenshell.api.group.assign_group(ifc_file, products=[group], group=case)
        assert subject.get_load_cases(model) == [case]

    def test_a_model_is_loaded_by_what_it_lists_only(self):
        ifc_file = ifcopenshell.file(schema="IFC4")
        tool.Ifc.set(ifc_file)
        model, _, case, _ = self.make_loaded_model(ifc_file, "IfcStructuralLoadCase", "LOAD_CASE")
        combination = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcStructuralLoadGroup")
        combination.PredefinedType = "LOAD_COMBINATION"
        ifcopenshell.api.structural.assign_structural_load_group(
            ifc_file, load_groups=[combination], structural_analysis_model=model
        )
        # The case loads the model's item, but a model that lists its load groups is taken at its word.
        assert subject.get_load_cases(model) == [combination]

    def test_unrelated_cases_are_left_out(self):
        ifc_file = ifcopenshell.file(schema="IFC4")
        tool.Ifc.set(ifc_file)
        model, _, case, _ = self.make_loaded_model(ifc_file, "IfcStructuralLoadCase", "LOAD_CASE")
        ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcStructuralLoadCase")  # Loads nothing.
        assert subject.get_load_cases(model) == [case]

    def test_a_case_another_model_lists_is_not_inferred(self):
        ifc_file = ifcopenshell.file(schema="IFC4")
        tool.Ifc.set(ifc_file)
        model, point, case, _ = self.make_loaded_model(ifc_file, "IfcStructuralLoadCase", "LOAD_CASE")
        other = ifcopenshell.api.structural.add_structural_analysis_model(ifc_file)
        ifcopenshell.api.structural.assign_structural_load_group(
            ifc_file, load_groups=[case], structural_analysis_model=other
        )
        assert subject.get_load_cases(model) == []
        assert subject.get_load_cases(other) == [case]

    def test_a_case_on_items_two_models_share_is_not_inferred(self):
        ifc_file = ifcopenshell.file(schema="IFC4")
        tool.Ifc.set(ifc_file)
        model, point, case, _ = self.make_loaded_model(ifc_file, "IfcStructuralLoadCase", "LOAD_CASE")
        other = ifcopenshell.api.structural.add_structural_analysis_model(ifc_file)
        ifcopenshell.api.structural.assign_structural_analysis_model(
            ifc_file, products=[point], structural_analysis_model=other
        )
        assert subject.get_load_cases(model) == []
        assert subject.get_load_cases(other) == []

    def test_a_case_with_loads_beyond_the_model_is_not_inferred(self):
        ifc_file = ifcopenshell.file(schema="IFC4")
        tool.Ifc.set(ifc_file)
        model, point, case, _ = self.make_loaded_model(ifc_file, "IfcStructuralLoadCase", "LOAD_CASE")
        other = ifcopenshell.api.structural.add_structural_analysis_model(ifc_file)
        elsewhere = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcStructuralPointConnection")
        ifcopenshell.api.structural.assign_structural_analysis_model(
            ifc_file, products=[elsewhere], structural_analysis_model=other
        )
        load = ifcopenshell.api.structural.add_structural_load(ifc_file, ifc_class="IfcStructuralLoadSingleForce")
        activity = ifcopenshell.api.structural.add_structural_activity(
            ifc_file, applied_load=load, structural_member=elsewhere, ifc_class="IfcStructuralPointAction"
        )
        ifcopenshell.api.group.assign_group(ifc_file, products=[activity], group=case)
        # One case loading items of two models belongs to neither, rather than to whichever is current.
        assert subject.get_load_cases(model) == []
        assert subject.get_load_cases(other) == []


class TestModelAxes(NewFile):
    def make_load(self, z_down):
        ifc_file = ifcopenshell.file(schema="IFC4")
        tool.Ifc.set(ifc_file)
        model = ifcopenshell.api.structural.add_structural_analysis_model(ifc_file)
        if z_down:
            # As RFEM places its models: Z down, X along X, so Y points the other way too.
            axes = ifc_file.createIfcAxis2Placement3D(
                ifc_file.createIfcCartesianPoint((0.0, 0.0, 0.0)),
                ifc_file.createIfcDirection((0.0, 0.0, -1.0)),
                ifc_file.createIfcDirection((1.0, 0.0, 0.0)),
            )
            model.SharedPlacement = ifc_file.createIfcLocalPlacement(None, axes)
        point = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcStructuralPointConnection")
        ifcopenshell.api.structural.assign_structural_analysis_model(
            ifc_file, products=[point], structural_analysis_model=model
        )
        load = ifcopenshell.api.structural.add_structural_load(ifc_file, ifc_class="IfcStructuralLoadSingleForce")
        load.ForceX, load.ForceZ, load.MomentY = 3.0, 25000.0, 7.0
        ifcopenshell.api.structural.add_structural_activity(
            ifc_file, applied_load=load, structural_member=point, ifc_class="IfcStructuralPointAction"
        )
        return load

    def test_a_model_pointing_z_down(self):
        load = self.make_load(z_down=True)
        # +25000 in the model's Z acts downwards.
        assert np.allclose(subject.get_force(load), (3.0, 0.0, -25000.0))
        turned = subject.to_blender_axes(load, {"MomentY": 7.0})
        assert np.isclose(turned["MomentY"], -7.0)
        written = subject.to_model_axes(load, {"ForceX": 3.0, "ForceY": None, "ForceZ": -10.0})
        assert np.allclose([written["ForceX"], written["ForceZ"]], (3.0, 10.0)) and not written["ForceY"]

    def test_models_bonsai_writes_are_left_alone(self):
        load = self.make_load(z_down=False)
        assert subject.get_model_rotation(load) is None
        assert subject.get_force(load) == (3.0, 0.0, 25000.0)
        assert subject.to_model_axes(load, {"ForceZ": 5.0}) == {"ForceZ": 5.0}

    def test_dialog_values_are_written_in_the_model_axes(self):
        load = self.make_load(z_down=True)
        props = SimpleNamespace(
            input_mode="COMPONENTS", x=3.0, y=0.0, z=-10.0, moment_x=0.0, moment_y=0.0, moment_z=0.0
        )
        attributes = get_load_attributes(props, "IfcStructuralPointConnection", load)
        # Down in Blender is +Z in a model pointing Z down.
        assert np.allclose([attributes["ForceX"], attributes["ForceZ"]], (3.0, 10.0))
