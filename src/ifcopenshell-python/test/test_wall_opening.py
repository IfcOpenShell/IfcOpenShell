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

import os
import re
import glob
import json
import typing
import shutil
import subprocess

from dataclasses import dataclass, field

import pytest
import ifcopenshell
import ifcopenshell.template

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
                    subprocess.call(args, stdout=subprocess.PIPE)

                    log = [json.loads(ln)["message"] for ln in open(fn + ".log.json") if ln]
                    perf = dict(x.groups() for x in [re.match(pat, l) for l in log] if x)

                    ts.append(float(perf["file geometry conversion"]))

                result[-1].append(sum(ts) / len(ts))

                if i == 0 and j == 0:
                    for ln, st in cs:
                        assert len([l for l in log if l.startswith(st)]) == ln

                # breakpoint()

        try:
            import tabulate
        except:
            return

        print(tabulate.tabulate(result, headers=["file", "", "--no-2d-boolean"], tablefmt="github"))


if __name__ == "__main__":
    pytest.main(["-x", __file__])
