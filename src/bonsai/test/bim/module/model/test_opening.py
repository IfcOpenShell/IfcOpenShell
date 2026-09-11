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

"""Regression test for FilledOpeningGenerator's void-profile shapely guard.

A filling type's ELEVATION_VIEW profile that doesn't tessellate into a
closed 2D outline (eg. precision loss on a re-triangulated curve) used to
crash deep inside shapely's polygonize/max(). generate_opening_from_filling
now falls through to the bounding-box opening shape instead."""

from unittest import mock

import bpy
import ifcopenshell
import ifcopenshell.api.root
import ifcopenshell.api.type
import numpy as np
import pytest

import bonsai.tool as tool
from bonsai.bim.module.model.opening import FilledOpeningGenerator

pytestmark = pytest.mark.model


def test_non_closing_profile_falls_back_to_bounding_box():
    ifc = ifcopenshell.file()
    tool.Ifc.set(ifc)

    model_context = ifc.createIfcGeometricRepresentationContext(ContextType="Model")
    profile_context = ifc.createIfcGeometricRepresentationSubContext(
        ContextIdentifier="Profile",
        ContextType="Model",
        ParentContext=model_context,
        TargetView="ELEVATION_VIEW",
    )
    ifc.createIfcGeometricRepresentationSubContext(
        ContextIdentifier="Body",
        ContextType="Model",
        ParentContext=model_context,
        TargetView="MODEL_VIEW",
    )

    door_type = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcDoorType")
    # A multi-item profile is required to reach the shapely tessellation
    # path (a single-item profile takes a direct, shapely-free shortcut).
    profile_rep = ifc.createIfcShapeRepresentation(
        ContextOfItems=profile_context,
        RepresentationIdentifier="Profile",
        RepresentationType="Curve2D",
        Items=[ifc.createIfcPolyline(Points=[]), ifc.createIfcPolyline(Points=[])],
    )
    door_type.RepresentationMaps = [
        ifc.createIfcRepresentationMap(
            MappingOrigin=ifc.createIfcAxis2Placement3D(Location=ifc.createIfcCartesianPoint((0.0, 0.0, 0.0))),
            MappedRepresentation=profile_rep,
        )
    ]
    door_type_obj = bpy.data.objects.new("DoorType", bpy.data.meshes.new("DoorType"))
    bpy.context.collection.objects.link(door_type_obj)
    tool.Ifc.link(door_type, door_type_obj)

    door = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcDoor")
    ifcopenshell.api.type.assign_type(ifc, related_objects=[door], relating_type=door_type)
    door_obj = bpy.data.objects.new("Door", bpy.data.meshes.new("Door"))
    bpy.context.collection.objects.link(door_obj)
    tool.Ifc.link(door, door_obj)

    # A single edge (0,1) never closes a loop, so shapely.polygonize finds
    # no polygon regardless of which of the two calls below it services.
    # The box corners (1.0m x 0.2m x 2.0m) let the fallback path compute a
    # distinctive, checkable opening size.
    fake_verts = np.array(
        [
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [1.0, 0.2, 0.0],
            [0.0, 0.2, 0.0],
            [0.0, 0.0, 2.0],
            [1.0, 0.0, 2.0],
            [1.0, 0.2, 2.0],
            [0.0, 0.2, 2.0],
        ]
    )
    with (
        mock.patch("ifcopenshell.geom.create_shape", return_value=object()),
        mock.patch("ifcopenshell.util.shape.get_vertices", return_value=fake_verts),
        mock.patch("ifcopenshell.util.shape.get_edges", return_value=[(0, 1)]),
    ):
        representation = FilledOpeningGenerator().generate_opening_from_filling(door, door_obj)

    assert representation is not None
    solid = representation.Items[0]
    assert solid.is_a("IfcExtrudedAreaSolid")
    outer_curve = solid.SweptArea.OuterCurve
    # Only shape_builder.rectangle(size=(x, z)) produces this exact 1x2
    # rectangle; the (unreachable, guarded-off) profile-curve path would
    # have produced a different, non-rectangular polyline.
    assert outer_curve.Points.CoordList == ((0.0, 0.0), (1.0, 0.0), (1.0, 2.0), (0.0, 2.0))
