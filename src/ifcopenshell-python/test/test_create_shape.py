import functools
import itertools
import math
import multiprocessing
import operator
import os
from typing import get_args

import numpy as np
import pytest

import ifcopenshell
import ifcopenshell.api.context
import ifcopenshell.api.owner.settings
import ifcopenshell.api.project
import ifcopenshell.api.root
import ifcopenshell.api.unit
import ifcopenshell.geom
import ifcopenshell.ifcopenshell_wrapper as W
import ifcopenshell.util.shape
import test.bootstrap
from ifcopenshell.util.shape_builder import ShapeBuilder

fn = os.path.join(os.path.dirname(__file__), "fixtures/ColumnPSetsOfSets.ifc")


class TestGeomSettings:
    def test_settings(self):
        settings = ifcopenshell.geom.settings()
        assert set(get_args(ifcopenshell.geom.SETTING)) == set(
            settings.setting_names()
        ), "Also need to update IfcPython.i, if new settings were added/removed."

        assert "use-python-opencascade" in settings.setting_names()
        assert settings.get(settings.USE_PYTHON_OPENCASCADE) is False
        assert settings.get("use-python-opencascade") is False
        assert "USE_PYTHON_OPENCASCADE = False" in repr(settings)

        # Testing both new and old ways of setting geometry settings.
        if ifcopenshell.geom.has_occ:
            settings.set("use-python-opencascade", True)
            settings.set(settings.USE_PYTHON_OPENCASCADE, True)
            assert settings.get(settings.USE_PYTHON_OPENCASCADE) is True
            assert "USE_PYTHON_OPENCASCADE = True" in repr(settings)
        else:
            with pytest.raises(AttributeError):
                settings.set("use-python-opencascade", True)
            with pytest.raises(AttributeError):
                settings.set(settings.USE_PYTHON_OPENCASCADE, True)
            assert "USE_PYTHON_OPENCASCADE = False" in repr(settings)

        settings.set("base-uri", "https://example.test/")
        assert settings.get("base-uri") == "https://example.test/"


class TestTriangulationAttributes(test.bootstrap.IFC4):
    def test_faces_representation_item_ids(self):
        ifc_file = ifcopenshell.file()
        ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcProject", name="Test")
        context = ifcopenshell.api.context.add_context(ifc_file, context_type="Model")

        builder = ShapeBuilder(ifc_file)
        extrusion = builder.extrude(builder.rectangle(), magnitude=1.0)
        representation = builder.get_representation(context, extrusion)
        settings = ifcopenshell.geom.settings()
        shape = ifcopenshell.geom.create_shape(settings, representation)
        faces_item_ids = ifcopenshell.util.shape.get_faces_representation_item_ids(shape)
        faces = ifcopenshell.util.shape.get_faces(shape)
        assert set(faces_item_ids) == {extrusion.id()}
        assert len(faces) == 12  # Cube has 12 tris.
        assert len(faces_item_ids) == len(faces)

        edges_item_ids = ifcopenshell.util.shape.get_edges_representation_item_ids(shape)
        edges = ifcopenshell.util.shape.get_edges(shape)
        assert set(edges_item_ids) == {extrusion.id()}
        assert len(edges) == 12  # Cube has 12 edges.
        assert len(edges_item_ids) == len(edges)

    def test_curve_representation_item_ids(self):
        ifc_file = ifcopenshell.file()
        ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcProject", name="Test")
        context = ifcopenshell.api.context.add_context(ifc_file, context_type="Model")

        builder = ShapeBuilder(ifc_file)
        curve = builder.rectangle()
        representation = builder.get_representation(context, curve)
        settings = ifcopenshell.geom.settings()
        settings.set("dimensionality", W.CURVES_SURFACES_AND_SOLIDS)
        shape = ifcopenshell.geom.create_shape(settings, representation)

        faces_item_ids = ifcopenshell.util.shape.get_faces_representation_item_ids(shape)
        assert len(faces_item_ids) == 0

        edges_item_ids = ifcopenshell.util.shape.get_edges_representation_item_ids(shape)
        edges = ifcopenshell.util.shape.get_edges(shape)
        assert set(edges_item_ids) == {curve.id()}
        assert len(edges) == 4
        assert len(edges_item_ids) == len(edges)

    def test_mixed_representation_item_ids(self):
        ifc_file = ifcopenshell.file()
        ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcProject", name="Test")
        context = ifcopenshell.api.context.add_context(ifc_file, context_type="Model")

        builder = ShapeBuilder(ifc_file)
        curve = builder.rectangle()

        fill = ifc_file.create_entity("IfcAnnotationFillArea", builder.rectangle())
        representation = builder.get_representation(context, (curve, fill))
        settings = ifcopenshell.geom.settings()
        settings.set("dimensionality", W.CURVES_SURFACES_AND_SOLIDS)
        shape = ifcopenshell.geom.create_shape(settings, representation)

        faces_item_ids = ifcopenshell.util.shape.get_faces_representation_item_ids(shape)
        faces = ifcopenshell.util.shape.get_faces(shape)
        assert len(faces) == 2  # Fill area will produce a triangulated face.
        assert set(faces_item_ids) == {fill.id()}
        assert len(faces_item_ids) == len(faces)

        edges_item_ids = ifcopenshell.util.shape.get_edges_representation_item_ids(shape)
        edges = ifcopenshell.util.shape.get_edges(shape)
        assert set(edges_item_ids) == {fill.id(), curve.id()}
        assert len(edges) == 8  # 4 edges rectangle curve + 4 edges fill area
        assert len(edges_item_ids) == len(edges)


class TestAssignObject:
    def test_no_welding_on_distinct_items(self):
        self.file = ifcopenshell.api.project.create_file()
        ifcopenshell.api.owner.settings.get_user = lambda ifc: (ifc.by_type("IfcPersonAndOrganization") or [None])[0]
        ifcopenshell.api.owner.settings.get_application = lambda ifc: (ifc.by_type("IfcApplication") or [None])[0]

        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject", name="Test")
        unit = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="LENGTHUNIT")
        ifcopenshell.api.unit.assign_unit(self.file, units=[unit])
        context = ifcopenshell.api.context.add_context(self.file, context_type="Model")
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")

        def create_extrusion(x, y):
            points = (
                (x + 0.0, y + 0.0),
                (x + 0.0, y + 1.0),
                (x + 1.0, y + 1.0),
                (x + 1.0, y + 0.0),
                (x + 0.0, y + 0.0),
            )
            curve = self.file.createIfcPolyline([self.file.createIfcCartesianPoint(p) for p in points])
            extrusion_direction = self.file.createIfcDirection((0.0, 0.0, 1.0))
            return self.file.createIfcExtrudedAreaSolid(
                self.file.createIfcArbitraryClosedProfileDef("AREA", None, curve),
                self.file.createIfcAxis2Placement3D(
                    self.file.createIfcCartesianPoint((0.0, 0.0, 0.0)),
                ),
                extrusion_direction,
                1.0,
            )

        extrusions = [create_extrusion(x, 0.0) for x in [0.0, 1.0]]
        element.Representation = self.file.createIfcProductDefinitionShape(
            Representations=[
                self.file.createIfcShapeRepresentation(
                    context,
                    context.ContextIdentifier,
                    "SweptSolid",
                    extrusions,
                )
            ]
        )

        obj = ifcopenshell.geom.create_shape(ifcopenshell.geom.settings(WELD_VERTICES=True), element)

        # item_ids is a per-triangle array, so we have 12 triangles per cube
        # even though not documented, the order in representation items should match
        assert obj.geometry.item_ids == (extrusions[0].id(),) * 12 + (extrusions[1].id(),) * 12

        # group the vertices
        vs = [obj.geometry.verts[i : i + 3] for i in range(0, len(obj.geometry.verts), 3)]

        # welding should not happen between distinct items so the total number of verts should be 2 times 8
        assert len(vs) == 16

        # even though there are only 12 unique vertices as the cubes are touching
        assert len(set(vs)) == 12


def test_iterator():
    # just test some permutations of invocation
    settings = ifcopenshell.geom.settings()
    file_or_filename = [fn, ifcopenshell.open(fn)]
    with_or_without_threads = [[], [multiprocessing.cpu_count()]]
    includes = [
        {},
        {"include": ["IfcColumn"]},
        {"include": [file_or_filename[1].by_type("IfcColumn")[0]]},
    ]
    for args in itertools.product(file_or_filename, with_or_without_threads, includes):
        kwargs = functools.reduce(operator.or_, (a for a in args if isinstance(a, dict)))
        pargs = []
        for a in (_ for _ in args if not isinstance(_, dict)):
            if isinstance(a, list):
                pargs.extend(a)
            else:
                pargs.append(a)
        iterator = ifcopenshell.geom.iterator(settings, *pargs, **kwargs)
        assert iterator.initialize()


@pytest.mark.parametrize("num_threads", [1, 2])
def test_iterator_get_transfers_ownership(num_threads):
    settings = ifcopenshell.geom.settings()
    iterator = ifcopenshell.geom.iterator(settings, fn, num_threads)
    assert iterator.initialize()

    element = iterator.get()
    element_id = element.id
    with pytest.raises(RuntimeError, match="already been retrieved"):
        iterator.get()

    iterator.next()
    assert element.id == element_id


@pytest.mark.parametrize("num_threads", [1, 2])
def test_iterator_get_native_transfers_ownership(num_threads):
    settings = ifcopenshell.geom.settings()
    iterator = ifcopenshell.geom.iterator(settings, fn, num_threads)
    assert iterator.initialize()

    element = iterator.get_native()
    element_id = element.id
    with pytest.raises(RuntimeError, match="already been retrieved"):
        iterator.get_native()

    iterator.next()
    assert element.id == element_id


@pytest.mark.parametrize("num_threads", [1, 2])
def test_iterator_native_output_is_retrieved_with_get(num_threads):
    settings = ifcopenshell.geom.settings()
    settings.set("iterator-output", W.NATIVE)
    iterator = ifcopenshell.geom.iterator(settings, fn, num_threads)
    assert iterator.initialize()

    with pytest.raises(RuntimeError, match=r"use get\(\) instead"):
        iterator.get_native()

    element = iterator.get()
    element_id = element.id
    iterator.next()
    assert element.id == element_id


def test_logging():
    assert ifcopenshell.logger
    logger = ifcopenshell.logger()
    logger.output_format(logger.FMT_INMEMORY)
    settings = ifcopenshell.geom.settings()
    f = ifcopenshell.open(fn)
    col = f.by_type("IfcColumn")[0]
    _ = ifcopenshell.geom.create_shape(settings, col, logger=logger)

    num_log_items = len(list(logger))
    col.Representation.Representations[0].Items[0].MappingSource.MappedRepresentation.Items[0].Depth *= -1.0

    with pytest.raises(RuntimeError):
        _ = ifcopenshell.geom.create_shape(settings, col, logger=logger)
    new_items = list(logger)[num_log_items:]

    assert ("GEO089", "Non-positive extrusion height encountered for:") in [
        (msg.code, msg.message) for msg in new_items
    ]


class TestSectionedSolidHorizontalRakedEndCut(test.bootstrap.IFC4X3):
    """An IfcSectionedSolidHorizontal whose two IfcAxis2PlacementLinear cross
    section positions use direction vectors inconsistently -- one raked
    RefDirection + width scale, the other plain -- must still loft a uniform
    prism (raked at one end, square at the other), not a wedge, and must not
    log GEO 42."""

    def _build_wingwall(self, theta):
        f = self.file
        ifcopenshell.api.root.create_entity(f, ifc_class="IfcProject", name="Test")
        ctx = ifcopenshell.api.context.add_context(f, context_type="Model")
        body = ifcopenshell.api.context.add_context(
            f, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=ctx
        )

        self.L, self.w, self.h = 40.0, 20.0 / 12.0, 6.0
        width_scale = 1.0 / math.cos(theta)

        directrix = f.createIfcPolyline(
            Points=[f.createIfcCartesianPoint((0.0, 0.0, 0.0)), f.createIfcCartesianPoint((self.L, 0.0, 0.0))]
        )

        def rect(half_width):
            coords = (
                (-half_width, 0.0),
                (half_width, 0.0),
                (half_width, self.h),
                (-half_width, self.h),
                (-half_width, 0.0),
            )
            return f.createIfcArbitraryClosedProfileDef(
                ProfileType="AREA",
                OuterCurve=f.createIfcIndexedPolyCurve(
                    Points=f.createIfcCartesianPointList2D(coords), Segments=None, SelfIntersect=False
                ),
            )

        axis = f.createIfcDirection((0.0, 0.0, 1.0))
        # Rakes the near end cap about the vertical axis by theta while keeping
        # the section's width axis (Axis x RefDirection) perpendicular extent at w.
        ref_direction = f.createIfcDirection((math.cos(theta), -math.sin(theta), 0.0))

        def location(distance_along):
            return f.createIfcPointByDistanceExpression(
                DistanceAlong=f.createIfcLengthMeasure(distance_along), BasisCurve=directrix
            )

        near = f.createIfcAxis2PlacementLinear(Location=location(0.0), Axis=axis, RefDirection=ref_direction)
        far = f.createIfcAxis2PlacementLinear(Location=location(self.L), Axis=axis)

        solid = f.createIfcSectionedSolidHorizontal(
            Directrix=directrix,
            CrossSections=[rect(0.5 * self.w * width_scale), rect(0.5 * self.w)],
            CrossSectionPositions=[near, far],
        )
        return f.createIfcShapeRepresentation(
            ContextOfItems=body,
            RepresentationIdentifier="Body",
            RepresentationType="AdvancedSweptSolid",
            Items=[solid],
        )

    @pytest.mark.skipif(
        not ifcopenshell.geom.has_geometry_library("opencascade"), reason="requires the OpenCASCADE kernel"
    )
    def test_raked_end_keeps_uniform_perpendicular_thickness(self):
        theta = math.radians(25.0 + 22.0 / 60.0 + 58.0 / 3600.0)
        representation = self._build_wingwall(theta)

        logger = ifcopenshell.logger()
        logger.output_format(logger.FMT_INMEMORY)
        settings = ifcopenshell.geom.settings()
        settings.set("use-world-coords", True)
        geometry = ifcopenshell.geom.create_shape(settings, representation, logger=logger)

        assert "GEO42" not in [msg.code for msg in logger]

        v = ifcopenshell.util.shape.get_vertices(geometry)
        xs = v[:, 0]

        # Uniform thickness perpendicular to the (X aligned) directrix. The whole
        # solid spans exactly w in Y; a wedge (the pre fix behaviour) does not.
        assert np.ptp(v[:, 1]) == pytest.approx(self.w, abs=1e-4)
        for x0 in np.linspace(3.0, self.L - 3.0, 12):
            slab = v[np.abs(xs - x0) < 1.0]
            if len(slab) < 4:
                continue
            assert np.ptp(slab[:, 1]) == pytest.approx(self.w, abs=1e-4), f"thickness at x={x0:.1f}"

        # Far end square to the directrix (all vertices at x == L), near end raked
        # about the vertical axis by exactly theta (its extreme vertex sits at
        # -w/2 * tan(theta) along the directrix).
        assert xs.max() == pytest.approx(self.L, abs=1e-4)
        assert np.ptp(v[xs > xs.max() - 1e-4][:, 0]) < 1e-4
        assert xs.min() == pytest.approx(-0.5 * self.w * math.tan(theta), abs=1e-4)


class TestSectionedSolidHorizontalHonoursAxis(test.bootstrap.IFC4X3):
    """An IfcSectionedSolidHorizontal whose cross section placements carry an
    explicit Axis = (0,0,1) but no RefDirection must sweep the profile with its
    Y axis on that Axis and its normal on the directrix tangent (buildingSMART
    IFC4.x-IF #147) -- i.e. following the curve. Regression test for the case
    where the directrix does not run along the global X axis: the profile used
    to be placed with a fixed [e_y | e_z | e_x] permutation that ignored the
    directrix, collapsing the swept solid (a road pavement running north-south
    would come out a sliver a few centimetres wide)."""

    def _build(self, theta=0.0):
        f = self.file
        ifcopenshell.api.root.create_entity(f, ifc_class="IfcProject", name="Test")
        ctx = ifcopenshell.api.context.add_context(f, context_type="Model")
        body = ifcopenshell.api.context.add_context(
            f, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=ctx
        )

        self.L, self.width, self.height = 60.0, 12.0, 0.5

        # Directrix runs along +Y, not +X.
        directrix = f.createIfcPolyline(
            Points=[f.createIfcCartesianPoint((0.0, 0.0, 0.0)), f.createIfcCartesianPoint((0.0, self.L, 0.0))]
        )

        def rect(half_width):
            coords = (
                (-half_width, 0.0),
                (half_width, 0.0),
                (half_width, self.height),
                (-half_width, self.height),
                (-half_width, 0.0),
            )
            return f.createIfcArbitraryClosedProfileDef(
                ProfileType="AREA",
                OuterCurve=f.createIfcIndexedPolyCurve(
                    Points=f.createIfcCartesianPointList2D(coords), Segments=None, SelfIntersect=False
                ),
            )

        axis = f.createIfcDirection((0.0, 0.0, 1.0))

        def location(distance_along):
            return f.createIfcPointByDistanceExpression(
                DistanceAlong=f.createIfcLengthMeasure(distance_along), BasisCurve=directrix
            )

        near = f.createIfcAxis2PlacementLinear(Location=location(0.0), Axis=axis)
        if theta:
            # Directrix tangent is +Y; rake the far cap about the vertical Axis.
            ref_direction = f.createIfcDirection((math.sin(theta), math.cos(theta), 0.0))
            far = f.createIfcAxis2PlacementLinear(Location=location(self.L), Axis=axis, RefDirection=ref_direction)
            far_half = 0.5 * self.width / math.cos(theta)
        else:
            far = f.createIfcAxis2PlacementLinear(Location=location(self.L), Axis=axis)
            far_half = 0.5 * self.width

        solid = f.createIfcSectionedSolidHorizontal(
            Directrix=directrix,
            CrossSections=[rect(0.5 * self.width), rect(far_half)],
            CrossSectionPositions=[near, far],
        )
        return f.createIfcShapeRepresentation(
            ContextOfItems=body,
            RepresentationIdentifier="Body",
            RepresentationType="AdvancedSweptSolid",
            Items=[solid],
        )

    def _shape(self, representation):
        logger = ifcopenshell.logger()
        logger.output_format(logger.FMT_INMEMORY)
        settings = ifcopenshell.geom.settings()
        settings.set("use-world-coords", True)
        geometry = ifcopenshell.geom.create_shape(settings, representation, logger=logger)
        assert "GEO42" not in [msg.code for msg in logger]
        return ifcopenshell.util.shape.get_vertices(geometry)

    @pytest.mark.skipif(
        not ifcopenshell.geom.has_geometry_library("opencascade"), reason="requires the OpenCASCADE kernel"
    )
    def test_square_run_follows_the_directrix(self):
        v = self._shape(self._build())
        # width across the road -> world X, crown -> world Z, length -> world Y.
        assert np.ptp(v[:, 0]) == pytest.approx(self.width, abs=1e-4)
        assert np.ptp(v[:, 1]) == pytest.approx(self.L, abs=1e-4)
        assert np.ptp(v[:, 2]) == pytest.approx(self.height, abs=1e-4)

    @pytest.mark.skipif(
        not ifcopenshell.geom.has_geometry_library("opencascade"), reason="requires the OpenCASCADE kernel"
    )
    def test_raked_far_end_on_a_non_axis_aligned_directrix(self):
        theta = math.radians(25.0 + 22.0 / 60.0 + 58.0 / 3600.0)
        v = self._shape(self._build(theta))
        ys = v[:, 1]
        # Uniform width perpendicular to the directrix, square near end, raked far end.
        assert np.ptp(v[:, 0]) == pytest.approx(self.width, abs=1e-4)
        for y0 in np.linspace(5.0, self.L - 5.0, 10):
            slab = v[np.abs(ys - y0) < 1.0]
            if len(slab) >= 4:
                assert np.ptp(slab[:, 0]) == pytest.approx(self.width, abs=1e-4), f"width at y={y0:.1f}"
        assert ys.min() == pytest.approx(0.0, abs=1e-4)
        assert np.ptp(v[ys < ys.min() + 1e-4][:, 1]) < 1e-4
        assert ys.max() == pytest.approx(self.L + 0.5 * self.width * math.tan(theta), abs=1e-4)


class TestSectionedSolidHorizontalOffsetUnits(test.bootstrap.IFC4X3):
    """IfcPointByDistanceExpression.OffsetLateral / OffsetVertical are
    IfcLengthMeasure and must be scaled by the model length unit, exactly like
    DistanceAlong. Regression test: in a millimetre model a 3000 mm lateral
    offset must move the swept solid 3 m, not 3000 m."""

    @pytest.mark.skipif(
        not ifcopenshell.geom.has_geometry_library("opencascade"), reason="requires the OpenCASCADE kernel"
    )
    def test_lateral_offset_is_scaled_by_the_length_unit(self):
        f = self.file
        ifcopenshell.api.root.create_entity(f, ifc_class="IfcProject", name="Test")
        unit = ifcopenshell.api.unit.add_si_unit(f, unit_type="LENGTHUNIT", prefix="MILLI")
        ifcopenshell.api.unit.assign_unit(f, units=[unit])
        ctx = ifcopenshell.api.context.add_context(f, context_type="Model")
        body = ifcopenshell.api.context.add_context(
            f, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=ctx
        )

        length_mm, width_mm, offset_mm = 20000.0, 4000.0, 3000.0
        directrix = f.createIfcPolyline(
            Points=[f.createIfcCartesianPoint((0.0, 0.0, 0.0)), f.createIfcCartesianPoint((length_mm, 0.0, 0.0))]
        )
        hw = 0.5 * width_mm
        profile = f.createIfcArbitraryClosedProfileDef(
            ProfileType="AREA",
            OuterCurve=f.createIfcIndexedPolyCurve(
                Points=f.createIfcCartesianPointList2D(((-hw, 0.0), (hw, 0.0), (hw, 500.0), (-hw, 500.0), (-hw, 0.0))),
                Segments=None,
                SelfIntersect=False,
            ),
        )
        axis = f.createIfcDirection((0.0, 0.0, 1.0))

        def position(distance_along):
            return f.createIfcAxis2PlacementLinear(
                Location=f.createIfcPointByDistanceExpression(
                    DistanceAlong=f.createIfcLengthMeasure(distance_along),
                    OffsetLateral=offset_mm,
                    BasisCurve=directrix,
                ),
                Axis=axis,
            )

        solid = f.createIfcSectionedSolidHorizontal(
            Directrix=directrix,
            CrossSections=[profile, profile],
            CrossSectionPositions=[position(0.0), position(length_mm)],
        )
        representation = f.createIfcShapeRepresentation(
            ContextOfItems=body,
            RepresentationIdentifier="Body",
            RepresentationType="AdvancedSweptSolid",
            Items=[solid],
        )

        settings = ifcopenshell.geom.settings()
        settings.set("use-world-coords", True)
        geometry = ifcopenshell.geom.create_shape(settings, representation)
        v = ifcopenshell.util.shape.get_vertices(geometry)  # metres

        # Directrix +X, Axis +Z -> profile local x is world +Y; +OffsetLateral shifts there.
        assert np.ptp(v[:, 0]) == pytest.approx(length_mm / 1000.0, abs=1e-4)
        assert np.ptp(v[:, 1]) == pytest.approx(width_mm / 1000.0, abs=1e-4)
        assert v[:, 1].mean() == pytest.approx(offset_mm / 1000.0, abs=1e-3)


if __name__ == "__main__":
    import pytest

    pytest.main(["-vvsx", __file__])
