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
import ifcopenshell.api.pset
import ifcopenshell.api.root
import pytest

import bonsai.core.tool
import bonsai.tool as tool
from bonsai.tool.sequence import Sequence as subject
from test.bim.bootstrap import NewFile


class TestImplementsTool(NewFile):
    def test_run(self):
        assert isinstance(subject(), bonsai.core.tool.Sequence)


class TestApplyVisibilityToVoids(NewFile):
    def create_wall_with_opening(self):
        bpy.ops.bim.create_project()
        bpy.ops.mesh.primitive_cube_add(size=2)
        bpy.ops.bim.assign_class(ifc_class="IfcWall")
        wall_obj = bpy.data.objects["IfcWall/Cube"]
        bpy.ops.mesh.primitive_cube_add(size=1)
        opening_obj = bpy.context.active_object
        wall_obj.select_set(True)
        opening_obj.select_set(True)
        bpy.context.view_layer.objects.active = wall_obj
        bpy.ops.bim.add_opening()
        wall = tool.Ifc.get_entity(wall_obj)
        opening = wall.HasOpenings[0].RelatedOpeningElement
        return wall_obj, wall, opening

    def test_hiding_an_opening_recuts_the_host_without_modifying_the_model(self):
        wall_obj, wall, opening = self.create_wall_with_opening()
        ifc = tool.Ifc.get()
        cut_vertices = len(wall_obj.data.vertices)
        ifc_before = ifc.to_string()

        subject.apply_visibility_to_voids({wall})
        assert len(wall_obj.data.vertices) < cut_vertices
        assert opening.Representation
        assert ifc.to_string() == ifc_before

        subject.apply_visibility_to_voids({wall, opening})
        assert len(wall_obj.data.vertices) == cut_vertices
        assert ifc.to_string() == ifc_before

    def test_a_hidden_opening_has_no_representation_only_while_the_kernel_runs(self):
        _, wall, opening = self.create_wall_with_opening()
        ifc = tool.Ifc.get()
        representation = opening.Representation
        with subject.status_hidden_openings_uncut(ifc, [wall]):
            assert opening.Representation == representation

        subject.apply_visibility_to_voids({wall})
        with subject.status_hidden_openings_uncut(ifc, [wall]):
            assert opening.Representation is None
        assert opening.Representation == representation

    def test_a_filter_round_trip_keeps_every_entity_and_inverse(self):
        _, wall, opening = self.create_wall_with_opening()
        ifc = tool.Ifc.get()

        def dump():
            return {e.id(): (str(e), sorted(i.id() for i in ifc.get_inverse(e))) for e in ifc}

        before = dump()
        subject.apply_visibility_to_voids({wall})
        assert dump() == before
        subject.apply_visibility_to_voids({wall, opening})
        assert dump() == before

    def test_an_error_during_the_recut_restores_the_representation(self, monkeypatch):
        _, wall, opening = self.create_wall_with_opening()
        ifc = tool.Ifc.get()
        ifc_before = ifc.to_string()
        seen = []

        def fail(iterator):
            seen.append(opening.Representation)
            raise RuntimeError

        monkeypatch.setattr("ifcopenshell.geom.iterator.initialize", fail)
        try:
            subject.apply_visibility_to_voids({wall})
        except RuntimeError:
            seen.append("raised")
        assert seen == [None, "raised"]
        assert opening.Representation
        assert ifc.to_string() == ifc_before

    def test_the_temporary_edit_is_not_recorded_for_undo(self):
        _, wall, opening = self.create_wall_with_opening()
        ifc = tool.Ifc.get()
        subject.apply_visibility_to_voids({wall})
        ifc.begin_transaction()
        with subject.status_hidden_openings_uncut(ifc, [wall]):
            assert opening.Representation is None
        transaction = ifc.transaction
        ifc.discard_transaction()
        assert transaction.operations == []

    def test_hiding_one_of_two_openings_sharing_a_representation_keeps_the_other_cut(self):
        wall_obj, wall, opening = self.create_wall_with_opening()
        ifc = tool.Ifc.get()
        bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 1.2))
        other_obj = bpy.context.active_object
        wall_obj.select_set(True)
        other_obj.select_set(True)
        bpy.context.view_layer.objects.active = wall_obj
        bpy.ops.bim.add_opening()
        other = next(r.RelatedOpeningElement for r in wall.HasOpenings if r.RelatedOpeningElement != opening)
        other.Representation = shared = opening.Representation
        subject.apply_visibility_to_voids({wall})
        uncut_vertices = len(wall_obj.data.vertices)
        subject.apply_visibility_to_voids({wall, opening, other})
        cut_vertices = len(wall_obj.data.vertices)

        subject.apply_visibility_to_voids({wall, other})
        assert uncut_vertices < len(wall_obj.data.vertices) < cut_vertices
        assert opening.Representation == other.Representation == shared
        with subject.status_hidden_openings_uncut(ifc, [wall]):
            assert opening.Representation is None
            assert other.Representation == shared


class TestGetElementStatus(NewFile):
    def test_common_pset(self):
        ifc = ifcopenshell.file()
        element = ifcopenshell.api.root.create_entity(ifc, "IfcWall")
        pset = ifcopenshell.api.pset.add_pset(ifc, element, "Pset_WallCommon")
        ifcopenshell.api.pset.edit_pset(ifc, pset, properties={"Status": ["EXISTING", "TEMPORARY"]})
        assert subject.get_element_status(element) == {"EXISTING", "TEMPORARY"}

    def test_epset(self):
        bpy.ops.bim.create_project()
        ifc = tool.Ifc.get()
        element = ifcopenshell.api.root.create_entity(ifc, "IfcWall")
        pset = ifcopenshell.api.pset.add_pset(ifc, element, "EPset_Status")
        ifcopenshell.api.pset.edit_pset(ifc, pset, properties={"Status": ["EXISTING", "TEMPORARY"]})
        assert subject.get_element_status(element) == {"EXISTING", "TEMPORARY"}


class TestEnableStatusFiltersOperator(NewFile):
    @pytest.mark.parametrize("schema", ["IFC2X3", "IFC4", "IFC4X3_ADD2"])
    def test_enumerated_status_property(self, schema):
        tool.Project.get_project_props().export_schema = schema
        bpy.ops.bim.create_project()
        ifc = tool.Ifc.get()
        element = ifcopenshell.api.root.create_entity(ifc, "IfcWall")
        pset = ifcopenshell.api.pset.add_pset(ifc, element, "Pset_WallCommon")
        values = [ifc.create_entity("IfcLabel", v) for v in ("EXISTING", "TEMPORARY")]
        pset.HasProperties = [ifc.create_entity("IfcPropertyEnumeratedValue", Name="Status", EnumerationValues=values)]

        assert bpy.ops.bim.enable_status_filters() == {"FINISHED"}

        props = tool.Sequence.get_status_props()
        assert props.is_enabled
        assert {s.name for s in props.statuses} >= {"No Status", "EXISTING", "TEMPORARY"}


class TestAssignStatus(NewFile):
    def test_run(self):
        bpy.ops.bim.create_project()
        ifc = tool.Ifc.get()

        bpy.ops.mesh.primitive_cube_add(size=10, location=(0, 0, 4))
        obj = bpy.data.objects["Cube"]
        bpy.ops.bim.assign_class(ifc_class="IfcActuator", predefined_type="ELECTRICACTUATOR", userdefined_type="")
        element = tool.Ifc.get_entity(obj)
        assert element

        bpy.ops.bim.assign_status(status="NEW")
        assert subject.get_element_status(element) == {"NEW"}

        bpy.ops.bim.assign_status(status="EXISTING")
        assert subject.get_element_status(element) == {"EXISTING"}

        bpy.ops.bim.assign_status(status="EXISTING", should_unassign_status=True)
        assert subject.get_element_status(element) == set()
