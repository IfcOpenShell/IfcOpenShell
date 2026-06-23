# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026
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
#
# This file was generated with the assistance of an AI coding tool.

"""End-to-end integration tests for the unified MEP disconnect path.

Builds a real IFC scene (two pipe segments joined via ports to a bridging
fitting) and exercises the full chain:
    tool.Connection.find_rels(seg_a, seg_b)
    → returns (fitting, "mep-pair-fitting")
    → bonsai.core.connection.disconnect_rel(subject=fitting, kind=...)
    → tool.Geometry.delete_ifc_object(fitting_obj)
    → cascade-on-delete removes the IfcRelConnectsPorts via remove_port

The mock-based dispatch tests in :py:mod:`test_disconnect_elements` pin each
piece in isolation. This module pins that they compose — the surface the
gizmo click hits in production."""

import bpy
import ifcopenshell.api.system
import pytest

import bonsai.core.connection
import bonsai.tool as tool
from test.bim.bootstrap import NewFile

pytestmark = pytest.mark.model


class TestMEPPairDisconnectEndToEnd(NewFile):
    def _make_segment(self, name: str):
        """Create one IfcPipeSegment occurrence with ports at both ends.
        Returns (blender_object, ifc_element)."""
        bpy.ops.mesh.primitive_cube_add(size=1)
        obj = bpy.data.objects["Cube"]
        obj.name = name
        bpy.ops.bim.assign_class(ifc_class="IfcPipeSegment", predefined_type="RIGIDSEGMENT", userdefined_type="")
        element = tool.Ifc.get_entity(obj)
        tool.System.add_ports(obj)
        return obj, element

    def _make_bend_fitting(self, name: str):
        """Create one IfcPipeFitting (PredefinedType=BEND) occurrence with two
        ports. Manual setup — bpy.ops.bim.assign_class doesn't add ports."""
        bpy.ops.mesh.primitive_cube_add(size=0.3)
        obj = bpy.data.objects["Cube"]
        obj.name = name
        bpy.ops.bim.assign_class(ifc_class="IfcPipeFitting", predefined_type="BEND", userdefined_type="")
        element = tool.Ifc.get_entity(obj)
        tool.System.add_ports(obj)
        return obj, element

    def _setup_joined_pair(self):
        bpy.ops.bim.create_project()
        seg_a_obj, seg_a = self._make_segment("SegA")
        seg_b_obj, seg_b = self._make_segment("SegB")
        bend_obj, bend = self._make_bend_fitting("Bend")

        ifc_file = tool.Ifc.get()
        seg_a_ports = tool.System.get_ports(seg_a)
        seg_b_ports = tool.System.get_ports(seg_b)
        bend_ports = tool.System.get_ports(bend)
        ifcopenshell.api.system.connect_port(ifc_file, port1=seg_a_ports[0], port2=bend_ports[0])
        ifcopenshell.api.system.connect_port(ifc_file, port1=seg_b_ports[0], port2=bend_ports[1])

        return seg_a, seg_b, bend, bend_obj

    def test_find_rels_returns_mep_pair_fitting_subject(self):
        seg_a, seg_b, bend, _ = self._setup_joined_pair()
        rels = tool.Connection.find_rels(seg_a, seg_b)
        assert rels == [(bend, "mep-pair-fitting")]

    def test_disconnect_rel_removes_the_bridging_fitting(self):
        """The end-to-end contract: dispatch removes the fitting from the
        IFC file, the Blender object is deleted, and a follow-up find_rels
        on the same pair returns empty — there's nothing left to disconnect."""
        seg_a, seg_b, bend, bend_obj = self._setup_joined_pair()
        bend_id = bend.id()
        bend_obj_name = bend_obj.name
        ifc_file = tool.Ifc.get()

        bonsai.core.connection.disconnect_rel(
            tool.Ifc,
            tool.Geometry,
            tool.Model,
            tool.Connection,
            subject=bend,
            kind="mep-pair-fitting",
            elem=seg_a,
            partner=seg_b,
        )

        # The fitting is gone from the IFC file.
        with pytest.raises(RuntimeError):
            ifc_file.by_id(bend_id)
        # The pair is no longer joined.
        assert tool.Connection.find_rels(seg_a, seg_b) == []
        # The Blender object was removed by delete_ifc_object.
        assert bend_obj_name not in bpy.data.objects

    def test_disconnect_rel_skips_when_subject_is_elem_being_deleted(self):
        """Cascade-side guard: if the fitting is itself the element being
        deleted (subject is elem), skip — the deletion is already in flight
        and re-deleting would crash."""
        seg_a, seg_b, bend, bend_obj = self._setup_joined_pair()
        bend_id = bend.id()
        bend_obj_name = bend_obj.name

        bonsai.core.connection.disconnect_rel(
            tool.Ifc,
            tool.Geometry,
            tool.Model,
            tool.Connection,
            subject=bend,
            kind="mep-pair-fitting",
            elem=bend,
            partner=seg_a,
            skip_elem_recreate=True,
        )

        # Fitting still present — the dispatch correctly skipped.
        assert tool.Ifc.get().by_id(bend_id).id() == bend_id
        assert bend_obj_name in bpy.data.objects
