# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
#
# This file is part of IfcOpenShell.
#
# IfcOpenShell is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcOpenShell is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcOpenShell.  If not, see <http://www.gnu.org/licenses/>.


import pytest

import ifcopenshell.api.project
import ifcpatch
import test.bootstrap


class TestMigrate(test.bootstrap.IFC4):
    def test_migrate_header(self):
        old_file = self.file
        old_file.header.file_name.name = "test"
        new_file = ifcpatch.execute({"file": old_file, "recipe": "Migrate", "arguments": ["IFC4"]})
        assert new_file.header.file_name.name == "test"

    def test_migrate_ifc4_to_ifc2x3_flattens_indexed_polycurve(self):
        """Downgrade IFC4 → IFC2X3 should auto-run DowngradeIndexedPolyCurve on
        IfcIndexedPolyCurve carriers, so the migrated file uses IfcPolyline (which
        exists in IFC2X3) instead of crashing on the IFC4-only curve class."""
        ifc4_file = self.file
        point_list = ifc4_file.create_entity(
            "IfcCartesianPointList2D",
            CoordList=((0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)),
        )
        segments = [
            ifc4_file.create_entity("IfcLineIndex", (1, 2)),
            ifc4_file.create_entity("IfcLineIndex", (2, 3)),
            ifc4_file.create_entity("IfcLineIndex", (3, 4)),
            ifc4_file.create_entity("IfcLineIndex", (4, 1)),
        ]
        curve = ifc4_file.create_entity(
            "IfcIndexedPolyCurve", Points=point_list, Segments=segments, SelfIntersect=False
        )
        ifc4_file.create_entity("IfcArbitraryClosedProfileDef", ProfileType="AREA", OuterCurve=curve)

        new_file = ifcpatch.execute({"file": ifc4_file, "recipe": "Migrate", "arguments": ["IFC2X3"]})

        assert new_file.schema == "IFC2X3"
        new_profile = new_file.by_type("IfcArbitraryClosedProfileDef")[0]
        assert new_profile.OuterCurve.is_a("IfcPolyline")
        # The preprocessing step should have purged orphaned IFC4-only entities
        # from the source before the migration loop reached them.
        assert not ifc4_file.by_type("IfcIndexedPolyCurve")
        assert not ifc4_file.by_type("IfcCartesianPointList2D")

    def test_migrate_ifc4_to_ifc2x3_encodes_fallback_class_in_object_type(self):
        """IfcLamp / IfcPipeSegment / IfcGeographicElement fall back to
        IfcBuildingElementProxy on downgrade. The original class and
        PredefinedType are encoded into ObjectType so the type info survives
        — but only when ObjectType is empty (author-supplied values stay)."""
        ifc4_file = self.file
        ifc4_file.create_entity("IfcLamp", GlobalId="2K6Z3DR8X37AS9XFvX8GcW", PredefinedType="COMPACTFLUORESCENT")
        ifc4_file.create_entity("IfcPipeSegment", GlobalId="0_bkftCTnBCOOZeUxtJngE")
        ifc4_file.create_entity(
            "IfcGeographicElement",
            GlobalId="3_b4gD1aP3ARmIm2ePijXi",
            ObjectType="Terrain Mesh",  # author-supplied, must not be overwritten
            PredefinedType="TERRAIN",
        )

        new_file = ifcpatch.execute({"file": ifc4_file, "recipe": "Migrate", "arguments": ["IFC2X3"]})

        proxies = {p.GlobalId: p for p in new_file.by_type("IfcBuildingElementProxy")}
        # IfcLamp with no author ObjectType: encoded as IfcLamp/COMPACTFLUORESCENT.
        assert proxies["2K6Z3DR8X37AS9XFvX8GcW"].ObjectType == "IfcLamp/COMPACTFLUORESCENT"
        # IfcPipeSegment with no PredefinedType set: just the class name.
        assert proxies["0_bkftCTnBCOOZeUxtJngE"].ObjectType == "IfcPipeSegment"
        # IfcGeographicElement with author ObjectType: preserved as-is.
        assert proxies["3_b4gD1aP3ARmIm2ePijXi"].ObjectType == "Terrain Mesh"

    def test_migrate_ifc4_to_ifc2x3_converts_polygonal_face_set_to_faceted_brep(self):
        """IfcPolygonalFaceSet has no IFC2X3 equivalent. Direct entity-level
        conversion produces an IfcFacetedBrep with the same topology, regardless
        of which representation context the source lived in."""
        ifc4_file = self.file
        coords = ifc4_file.create_entity(
            "IfcCartesianPointList3D",
            CoordList=(
                (0.0, 0.0, 0.0),
                (1.0, 0.0, 0.0),
                (1.0, 1.0, 0.0),
                (0.0, 1.0, 0.0),
                (0.5, 0.5, 1.0),
            ),
        )
        # Square base + 4 triangle sides — a simple pyramid.
        faces = [
            ifc4_file.create_entity("IfcIndexedPolygonalFace", CoordIndex=(1, 2, 3, 4)),
            ifc4_file.create_entity("IfcIndexedPolygonalFace", CoordIndex=(1, 2, 5)),
            ifc4_file.create_entity("IfcIndexedPolygonalFace", CoordIndex=(2, 3, 5)),
            ifc4_file.create_entity("IfcIndexedPolygonalFace", CoordIndex=(3, 4, 5)),
            ifc4_file.create_entity("IfcIndexedPolygonalFace", CoordIndex=(4, 1, 5)),
        ]
        face_set = ifc4_file.create_entity("IfcPolygonalFaceSet", Coordinates=coords, Faces=faces)
        context = ifc4_file.create_entity(
            "IfcGeometricRepresentationContext",
            ContextType="Model",
            CoordinateSpaceDimension=3,
            Precision=0.01,
            WorldCoordinateSystem=ifc4_file.createIfcAxis2Placement3D(
                Location=ifc4_file.createIfcCartesianPoint((0.0, 0.0, 0.0))
            ),
        )
        ifc4_file.create_entity(
            "IfcShapeRepresentation",
            ContextOfItems=context,
            RepresentationIdentifier="Body",
            RepresentationType="Tessellation",
            Items=[face_set],
        )

        new_file = ifcpatch.execute({"file": ifc4_file, "recipe": "Migrate", "arguments": ["IFC2X3"]})

        assert new_file.schema == "IFC2X3"
        breps = new_file.by_type("IfcFacetedBrep")
        assert len(breps) == 1
        brep = breps[0]
        assert len(brep.Outer.CfsFaces) == 5
        # Coordinates from the source CartesianPointList3D must appear in the
        # resulting brep's loop points — otherwise the conversion silently
        # corrupted geometry.
        brep_coords = {tuple(p.Coordinates) for face in brep.Outer.CfsFaces for p in face.Bounds[0].Bound.Polygon}
        for expected in ((0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (1.0, 1.0, 0.0), (0.0, 1.0, 0.0), (0.5, 0.5, 1.0)):
            assert expected in brep_coords, f"vertex {expected} missing from converted brep"
        rep = new_file.by_type("IfcShapeRepresentation")[0]
        assert rep.RepresentationType == "Brep"
        assert rep.Items[0].is_a("IfcFacetedBrep")

    def test_migrate_ifc4_to_ifc2x3_summarises_unmappable_entities(self):
        """When an IFC4-only entity that cannot be auto-substituted survives
        preprocessing, the recipe must surface a summary RuntimeError naming
        the failing class — not the cryptic ``RuntimeError: Entity with name
        '' not found``.

        Uses ``IfcWorkCalendar`` as the fixture — an IFC4 entity that
        (a) is not an IfcRepresentationItem (skips the geometry purge),
        (b) is not an IfcElement (skips the proxy fallback),
        (c) has no IFC2X3 equivalent in ``class_4_to_2x3.json`` (mapped to ``""``).
        These three conditions together guarantee it always reaches the
        unmappable error path, independent of future schema additions."""
        ifc4_file = self.file
        ifc4_file.create_entity("IfcWorkCalendar", GlobalId="2K6Z3DR8X37AS9XFvX8GcW")

        with pytest.raises(RuntimeError) as exc_info:
            ifcpatch.execute({"file": ifc4_file, "recipe": "Migrate", "arguments": ["IFC2X3"]})

        message = str(exc_info.value)
        assert "IfcWorkCalendar" in message

    def test_migrate_ifc4x3_to_ifc2x3_runs_downgrade_preprocessing(self):
        """IFC4X3 → IFC2X3 must trigger the same downgrade preprocessing as
        IFC4 → IFC2X3: curve flatten, face-set → brep, IfcBuildingElementProxy
        fallback, ObjectType encoding. Pins the gate at
        ``self.file.schema in ('IFC4', 'IFC4X3')`` — a narrower check would
        silently leave IFC4X3 sources crashing on IFC4-only geometry."""
        ifc4x3_file = ifcopenshell.api.project.create_file(version="IFC4X3")
        ifc4x3_file.create_entity("IfcLamp", GlobalId="2K6Z3DR8X37AS9XFvX8GcW", PredefinedType="COMPACTFLUORESCENT")

        new_file = ifcpatch.execute({"file": ifc4x3_file, "recipe": "Migrate", "arguments": ["IFC2X3"]})

        assert new_file.schema == "IFC2X3"
        proxies = new_file.by_type("IfcBuildingElementProxy")
        assert len(proxies) == 1
        # ObjectType encoding ran — same as the IFC4 → IFC2X3 case.
        assert proxies[0].ObjectType == "IfcLamp/COMPACTFLUORESCENT"

    def test_migrate_ifc4_to_ifc2x3_flattens_arc_bearing_indexed_polycurve(self):
        """An IfcIndexedPolyCurve with IfcArcIndex segments is approximated
        with a chord polyline rather than skipped, so the parent profile def
        and its representations stay parametric (no fallback to tessellation)."""
        ifc4_file = self.file
        point_list = ifc4_file.create_entity(
            "IfcCartesianPointList2D",
            CoordList=((1.0, 0.0), (0.0, 1.0), (-1.0, 0.0), (0.0, -1.0)),
        )
        # Two half-arcs forming a circle: (1,0)→(0,1)→(-1,0)→(0,-1)→(1,0).
        segments = [
            ifc4_file.create_entity("IfcArcIndex", (1, 2, 3)),
            ifc4_file.create_entity("IfcArcIndex", (3, 4, 1)),
        ]
        curve = ifc4_file.create_entity(
            "IfcIndexedPolyCurve", Points=point_list, Segments=segments, SelfIntersect=False
        )
        ifc4_file.create_entity("IfcArbitraryClosedProfileDef", ProfileType="AREA", OuterCurve=curve)

        new_file = ifcpatch.execute({"file": ifc4_file, "recipe": "Migrate", "arguments": ["IFC2X3"]})

        assert new_file.schema == "IFC2X3"
        new_profile = new_file.by_type("IfcArbitraryClosedProfileDef")[0]
        assert new_profile.OuterCurve.is_a("IfcPolyline")
        # Arc subdivision should produce many more points than the 4 input coords.
        assert len(new_profile.OuterCurve.Points) > 4
