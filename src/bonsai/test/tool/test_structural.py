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
        props = SimpleNamespace(x=3.0, y=0.0, z=-10.0, moment_x=0.0, moment_y=0.0, moment_z=0.0)
        attributes = get_load_attributes(props, "IfcStructuralPointConnection", load)
        # Down in Blender is +Z in a model pointing Z down.
        assert np.allclose([attributes["ForceX"], attributes["ForceZ"]], (3.0, 10.0))

    def test_line_and_area_loads_are_turned_too(self):
        self.make_load(z_down=True)
        load = ifcopenshell.api.structural.add_structural_load(tool.Ifc.get(), ifc_class="IfcStructuralLoadPlanarForce")
        surface = ifcopenshell.api.root.create_entity(tool.Ifc.get(), ifc_class="IfcStructuralSurfaceMember")
        model = tool.Ifc.get().by_type("IfcStructuralAnalysisModel")[0]
        ifcopenshell.api.structural.assign_structural_analysis_model(
            tool.Ifc.get(), products=[surface], structural_analysis_model=model
        )
        ifcopenshell.api.structural.add_structural_activity(
            tool.Ifc.get(), applied_load=load, structural_member=surface, ifc_class="IfcStructuralPlanarAction"
        )
        assert subject.to_model_axes(load, {"PlanarForceZ": -2.0})["PlanarForceZ"] == 2.0
        turned = subject.to_model_axes(load, {"LinearForceZ": -2.0, "LinearMomentY": 1.0})
        assert (turned["LinearForceZ"], turned["LinearMomentY"]) == (2.0, -1.0)
