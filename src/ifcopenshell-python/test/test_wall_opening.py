# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2021 Thomas Krijnen <thomas@aecgeeks.com>
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

import glob
import json
import math
import os
import re
import shutil
import subprocess
import typing
from dataclasses import dataclass, field

import pytest

import ifcopenshell.api.context
import ifcopenshell.api.feature
import ifcopenshell.api.geometry
import ifcopenshell.api.project
import ifcopenshell.api.root
import ifcopenshell.api.unit
import ifcopenshell.geom
import ifcopenshell.guid
import ifcopenshell.template
import ifcopenshell.util.shape

PERF = False


@dataclass
class rect:
    width: float
    height: float

    def build(self, f):
        return f.createIfcRectangleProfileDef("AREA", None, None, self.width, self.height)


@dataclass
class circle:
    radius: float

    def build(self, f):
        return f.createIfcCircleProfileDef("AREA", None, None, self.radius)


@dataclass
class opening:
    x: float
    z: float
    shape: typing.Any
    depth: float
    direc: tuple = field(default_factory=lambda: (0.0, 0.0, -1.0))


O = 0.0, 0.0, 0.0
X = 1.0, 0.0, 0.0
Y = 0.0, 1.0, 0.0
Z = 0.0, 0.0, 1.0


# Creates an IfcAxis2Placement3D from Location, Axis and RefDirection specified as Python tuples
def create_ifcaxis2placement(f, point=O, dir1=Z, dir2=X):
    point = f.createIfcCartesianPoint(point)
    dir1 = f.createIfcDirection(dir1)
    dir2 = f.createIfcDirection(dir2)
    axis2placement = f.createIfcAxis2Placement3D(point, dir1, dir2)
    return axis2placement


# Creates an IfcLocalPlacement from Location, Axis and RefDirection, specified as Python tuples, and relative placement
def create_ifclocalplacement(f, point=O, dir1=Z, dir2=X, relative_to=None):
    axis2placement = create_ifcaxis2placement(f, point, dir1, dir2)
    ifclocalplacement2 = f.createIfcLocalPlacement(relative_to, axis2placement)
    return ifclocalplacement2


# Creates an IfcPolyLine from a list of points, specified as Python tuples
def create_ifcpolyline(f, point_list):
    ifcpts = []
    for point in point_list:
        point = f.createIfcCartesianPoint(point)
        ifcpts.append(point)
    polyline = f.createIfcPolyLine(ifcpts)
    return polyline


# Creates an IfcExtrudedAreaSolid from a list of points, specified as Python tuples
def create_ifcextrudedareasolid(f, point_list, ifcaxis2placement, extrude_dir, extrusion):
    polyline = create_ifcpolyline(f, point_list)
    ifcclosedprofile = f.createIfcArbitraryClosedProfileDef("AREA", None, polyline)
    ifcdir = f.createIfcDirection(extrude_dir)
    ifcextrudedareasolid = f.createIfcExtrudedAreaSolid(ifcclosedprofile, ifcaxis2placement, ifcdir, extrusion)
    return ifcextrudedareasolid


def create_case(fn, openings):
    f = ifcopenshell.template.create()

    owner_history = f.by_type("IfcOwnerHistory")[0]
    project = f.by_type("IfcProject")[0]
    context = f.by_type("IfcGeometricRepresentationContext")[0]

    wall_placement = create_ifclocalplacement(f, relative_to=None)

    extrusion_placement = create_ifcaxis2placement(f, (0.0, 0.0, 0.0), (0.0, 0.0, 1.0), (1.0, 0.0, 0.0))
    point_list_extrusion_area = [
        (0.0, -0.2, 0.0),
        (15.0, -0.2, 0.0),
        (15.0, 0.0, 0.0),
        (0.0, 0.0, 0.0),
        (0.0, -0.2, 0.0),
    ]
    solid = create_ifcextrudedareasolid(f, point_list_extrusion_area, extrusion_placement, (0.0, 0.0, 1.0), 4.0)
    body_representation = f.createIfcShapeRepresentation(context, "Body", "SweptSolid", [solid])

    product_shape = f.createIfcProductDefinitionShape(None, None, [body_representation])

    wall = f.createIfcWallStandardCase(
        ifcopenshell.guid.new(), owner_history, "Wall", None, None, wall_placement, product_shape, None
    )

    for opening in openings:
        opening_placement = create_ifclocalplacement(
            f, (opening.x, 0.0, opening.z), (0.0, 1.0, 0.0), (1.0, 0.0, 0.0), wall_placement
        )
        opening_solid = f.createIfcExtrudedAreaSolid(
            opening.shape.build(f), None, f.createIfcDirection(opening.direc), opening.depth
        )
        opening_representation = f.createIfcShapeRepresentation(context, "Body", "SweptSolid", [opening_solid])
        opening_shape = f.createIfcProductDefinitionShape(None, None, [opening_representation])
        opening_element = f.createIfcOpeningElement(
            ifcopenshell.guid.new(), owner_history, "Opening", None, None, opening_placement, opening_shape, None
        )
        f.createIfcRelVoidsElement(ifcopenshell.guid.new(), owner_history, None, None, wall, opening_element)

    f.write(fn)


def kernel_available(library):
    f = ifcopenshell.api.project.create_file(version="IFC4")
    try:
        ifcopenshell.geom.iterator(ifcopenshell.geom.settings(), f, 1, geometry_library=library)
    except RuntimeError:
        return False
    return True


KERNELS = ("cgal-simple", "manifold", "hybrid-cgal-simple-opencascade", "hybrid-manifold-opencascade")
AVAILABLE_KERNELS = {library for library in KERNELS if kernel_available(library)}

WALL_VOLUME = 5.0 * 0.2 * 2.8
SLAB_VOLUME = 6.0 * 4.0 * 0.25
CIRCLE_CUT = math.pi * 0.3**2 * 0.2


def build_voided_element(entity, host, opening_body):
    f = ifcopenshell.api.project.create_file(version="IFC4")
    ifcopenshell.api.root.create_entity(f, ifc_class="IfcProject")
    ifcopenshell.api.unit.assign_unit(f, length={"is_metric": True, "raw": "METERS"})
    model = ifcopenshell.api.context.add_context(f, context_type="Model")
    body = ifcopenshell.api.context.add_context(
        f, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=model
    )

    def axis(location=O, z=None, x=None):
        return f.createIfcAxis2Placement3D(
            f.createIfcCartesianPoint(location),
            f.createIfcDirection(z) if z else None,
            f.createIfcDirection(x) if x else None,
        )

    def extrusion(profile, depth, position=None):
        return f.createIfcExtrudedAreaSolid(profile, position or axis(), f.createIfcDirection(Z), depth)

    def box(x_dim, y_dim, depth, centre=(0.0, 0.0), position=None):
        location = f.createIfcAxis2Placement2D(f.createIfcCartesianPoint(centre), None)
        return extrusion(f.createIfcRectangleProfileDef("AREA", None, location, x_dim, y_dim), depth, position)

    def circle_body(radius, depth, position):
        location = f.createIfcAxis2Placement2D(f.createIfcCartesianPoint((0.0, 0.0)), None)
        return extrusion(f.createIfcCircleProfileDef("AREA", None, location, radius), depth, position)

    def assign(product, item):
        representation = f.createIfcShapeRepresentation(body, "Body", "SweptSolid", [item])
        ifcopenshell.api.geometry.assign_representation(f, product=product, representation=representation)

    through_wall = axis((2.5, -0.15, 1.5), Y, X)
    hosts = {
        "wall": box(5.0, 0.2, 2.8, (2.5, 0.0)),
        "slab": box(6.0, 4.0, 0.25, (3.0, 2.0)),
    }
    openings = {
        "through": lambda: box(1.0, 2.0, 0.3, position=through_wall),
        "slot": lambda: box(1.0, 0.1, 3.0, position=axis((2.5, 0.0, -0.1))),
        "hole": lambda: box(1.0, 1.0, 0.35, position=axis((2.0, 2.0, -0.05))),
        "recess": lambda: box(1.0, 1.0, 0.15, position=axis((2.0, 2.0, 0.15))),
        "circle": lambda: circle_body(0.3, 0.3, through_wall),
    }

    element = ifcopenshell.api.root.create_entity(f, ifc_class=entity)
    assign(element, hosts[host])
    opening = ifcopenshell.api.root.create_entity(f, ifc_class="IfcOpeningElement")
    assign(opening, openings[opening_body]())
    ifcopenshell.api.feature.add_feature(f, feature=opening, element=element)
    return f, element


# (IFC class, host body, opening body, volume of the uncut host, volume with the opening subtracted)
VOIDED_CASES = {
    "wall-through-opening": ("IfcWall", "wall", "through", WALL_VOLUME, WALL_VOLUME - 1.0 * 2.0 * 0.2),
    "wall-slot": ("IfcWall", "wall", "slot", WALL_VOLUME, WALL_VOLUME - 1.0 * 0.1 * 2.8),
    "slab-through-hole": ("IfcSlab", "slab", "hole", SLAB_VOLUME, SLAB_VOLUME - 1.0 * 1.0 * 0.25),
    "slab-recess": ("IfcSlab", "slab", "recess", SLAB_VOLUME, SLAB_VOLUME - 1.0 * 1.0 * 0.1),
    "wall-circular-opening": ("IfcWall", "wall", "circle", WALL_VOLUME, WALL_VOLUME - CIRCLE_CUT),
}


# cgal-simple cannot subtract openings, so it keeps the uncut host. manifold cannot convert a circular opening
# at the default circle-segments, so there the host is kept unless that conversion gets fixed.
def expected_volumes(library, case):
    entity, host, opening_body, uncut, cut = VOIDED_CASES[case]
    if library == "cgal-simple":
        return (uncut,)
    if case == "wall-circular-opening" and "manifold" in library:
        return (uncut, cut)
    return (cut,)


def assert_voided_volume(library, case, volume, log):
    uncut = VOIDED_CASES[case][3]
    assert any(volume == pytest.approx(expected, rel=1e-3) for expected in expected_volumes(library, case))
    if volume == pytest.approx(uncut, rel=1e-3):
        assert "GEO034" in log


class TestVoidedElementFallback:
    @pytest.mark.parametrize("case", VOIDED_CASES)
    @pytest.mark.parametrize("library", KERNELS)
    def test_voided_element_is_never_empty(self, library, case):
        if library not in AVAILABLE_KERNELS:
            pytest.skip(f"{library} kernel is not available")
        f, element = build_voided_element(*VOIDED_CASES[case][:3])
        ifcopenshell.get_log()
        shape = ifcopenshell.geom.create_shape(ifcopenshell.geom.settings(), element, geometry_library=library)
        volume = ifcopenshell.util.shape.get_volume(shape.geometry)
        assert_voided_volume(library, case, volume, ifcopenshell.get_log())

    @pytest.mark.parametrize("case", VOIDED_CASES)
    @pytest.mark.parametrize("library", KERNELS)
    def test_iterator_yields_voided_element(self, library, case):
        if library not in AVAILABLE_KERNELS:
            pytest.skip(f"{library} kernel is not available")
        f, element = build_voided_element(*VOIDED_CASES[case][:3])
        ifcopenshell.get_log()
        shapes = list(
            ifcopenshell.geom.iterate(ifcopenshell.geom.settings(), f, 1, include=[element], geometry_library=library)
        )
        assert len(shapes) == 1
        volume = ifcopenshell.util.shape.get_volume(shapes[0].geometry)
        assert_voided_volume(library, case, volume, ifcopenshell.get_log())


class TestWallOpenings:
    @pytest.mark.skipif(shutil.which("IfcConvert") is None, reason="Requires IfcConvert in path")
    def test_all(self):
        cases = [
            (
                "wall-openings-non-intersecting-rect-circle.ifc",
                [opening(i * 4.0 + 2.0, 2.0, rect(1.0, 1.0), 0.2) for i in range(3)]
                + [opening(i * 4.0 + 4.0, 2.0, circle(0.5), 0.2) for i in range(3)],
            ),
            (
                "wall-openings-intersecting-inner-bounds.ifc",
                [opening(i * 0.8 + 2.0, i * 0.1 + 1.0, rect(1.0, 1.0), 0.2) for i in range(15)],
            ),
            (
                "wall-openings-intersecting-with-outer.ifc",
                [opening(i * 2.0, 4.0, rect(1.0, 1.0), 0.2) for i in range(15)],
            ),
            (
                "wall-openings-recesses.ifc",
                [opening(i * 4.0 + 2.0, 2.0, rect(1.0, 1.0), 0.1) for i in range(3)]
                + [opening(i * 4.0 + 4.0, 2.0, circle(0.5), 0.1) for i in range(3)],
            ),
            (
                "wall-openings-non-orthogonal.ifc",
                [opening(i * 4.0 + 2.0, 2.0, rect(1.0, 1.0), 0.3, direc=(1.0, 0.0, -1.0)) for i in range(6)],
            ),
            (
                "wall-openings-contained-in-other.ifc",
                [opening(2.0, 2.0, rect(1.0, 1.0), 0.2), opening(2.0, 2.0, rect(0.5, 0.5), 0.2)],
            ),
            (
                "wall-openings-outside-of-outer.ifc",
                [opening(2.0, 2.0, rect(1.0, 1.0), 0.2), opening(2.0, 6.0, rect(1.0, 1.0), 0.2)],
            ),
            ("wall-openings-touching-outer.ifc", [opening(2.0, 3.0, rect(2.0, 2.0), 0.2)]),
        ]

        checks = [
            [(1, "Processed fully in 2D")],
            [(1, "Intersecting boundaries")],
            [(1, "Intersecting boundaries")],
            [(1, "No second operands can be processed as 2D inner bounds"), (0, "Operand B creates a through hole")],
            [(0, "Operand B 1/6 is an extrusion")],
            [(1, "Subtraction operand contained in other"), (0, "Subtraction operand outside of outer bound")],
            [],  # [(1, "Subtraction operand outside of outer bound")],
            [(1, "Intersecting boundaries")],
        ]

        for fn in glob.glob("*.log.json"):
            os.unlink(fn)

        pat = re.compile(r"^([\w :]+?)\s*: (\d+\.\d+)")

        result = []

        for ci, ((fn, ops), cs) in enumerate(zip(cases, checks), start=1):
            create_case(fn, ops)

            result.append([fn])
            for i in range(2 if PERF else 1):
                args = [
                    shutil.which("IfcConvert") or "IfcConvert",
                    "-qyvvv",
                    fn,
                    fn + ".obj",
                    "--log-format",
                    "json",
                    "--log-file",
                    fn + ".log.json",
                ]
                if i:
                    args.append("--no-2d-boolean")

                ts = []
                for j in range(10 if PERF else 1):
                    subprocess.check_call(args, stdout=subprocess.PIPE)

                    log = [json.loads(ln)["message"] for ln in open(fn + ".log.json") if ln]
                    perf = dict(x.groups() for x in [re.match(pat, l) for l in log] if x)

                    ts.append(float(perf["file geometry conversion"]))

                result[-1].append(sum(ts) / len(ts))

                if i == 0 and j == 0:
                    for ln, st in cs:
                        assert len([l for l in log if l.startswith(st)]) == ln, (
                            f"\nOn file:\n - {fn}\nMessages:"
                            + "".join(f'\n - "{l}"' for l in log)
                            + f'\nExpected:\n - "{st}"'
                        )

                # breakpoint()

                temp_files = [fn, f"{fn}.obj", f"{fn}.log.json", f"{fn}.mtl"]
                for temp_fn in temp_files:
                    os.unlink(temp_fn)

        try:
            import tabulate
        except:
            return

        print("\n" + tabulate.tabulate(result, headers=["file", "", "--no-2d-boolean"], tablefmt="github"))


if __name__ == "__main__":
    pytest.main(["-x", __file__])
