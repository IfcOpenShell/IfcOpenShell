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

import operator

from dataclasses import dataclass

import numpy

import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.express
import ifcopenshell.transition_curve

# geometric primitives

# @notes
# - not sure if the separation of geometric primitives make sense
#   does it make handling the variety of distance expressions and
#   interpolation harder?


@dataclass
class line:
    start_point: numpy.ndarray
    direction_vector: numpy.ndarray

    def __call__(self, u):
        p = numpy.ndarray((3,))
        p[0:2] = self.start_point + self.direction_vector * u
        p[2] = numpy.nan
        return p


@dataclass
class circle:
    radius: numpy.ndarray

    def __call__(self, u):
        return numpy.array([self.radius * numpy.cos(u), self.radius * numpy.sin(u), numpy.nan])


def place(matrix, func):
    """
    Higher order function for application of a 3x3 matrix
    to a 2D point. Assumes a functor such as line or circle.
    """

    def inner(*args):
        v = func(*args)
        # homogenize
        v = numpy.insert(v[0:2], v[0:2].shape, 1, axis=-1)
        p = numpy.ndarray((3,))
        p[0:2] = (matrix @ v)[0:2]
        p[2] = numpy.nan
        return p

    return inner


# primitives for manipulating and joining curve functor domains


def reparametrized_curve(fn, a, b):
    return lambda u: fn(a * u + b)


def normalized_curve(fn):
    return lambda u: fn(u / fn.length)


class trimmed_curve:
    def __init__(self, fn, length):
        self.fn = fn
        self.length = length

    def __call__(self, u):
        assert u >= 0.0 and u <= self.length
        return self.fn(u)


class piecewise:
    # takes a set of functors and returns a function f(u) that delegates to the correct segment

    def __init__(self, fns):
        self.fns = fns
        self.length = sum(map(operator.attrgetter("length"), fns))

    def __call__(self, u):
        # this is silly, assuming `u` is monotonically increases we should not always start
        # searching from the first segment or at least binary search into the segment
        # lengths
        u0 = 0
        for fn in self.fns:
            u1 = u0 + fn.length
            if u >= u0 and u <= u1:
                return fn(u - u0)
            u0 = u1


# mapping functions from IFC entities


def map_inst(inst):
    """
    Looks up one of the implementation functions below in the global namespace
    """
    return globals()[f"impl_{inst.is_a()}"](inst)


def impl_IfcLine(inst):
    return line(
        numpy.array(inst.Pnt.Coordinates),
        numpy.array(inst.Dir.Orientation.DirectionRatios) * inst.Dir.Magnitude,
    )


def impl_IfcCircle(inst):
    return place(map_inst(inst.Position), circle(inst.Radius))


def impl_IfcClothoid(inst):
    # @todo
    # place = map_inst(inst.Position)
    # ifcopenshell.transition_curve.TransitionCurve(
    #     StartPoint          = place.T[2]
    #     StartDirection      = numpy.arctan2(place.T[0][1], place.T[0][0]),
    #     SegmentLength       =
    #     IsStartRadiusCCW    =
    #     IsEndRadiusCCW      =
    #     TransitionCurveType =
    #     StartRadius         =
    #     EndRadius           =
    # )
    return lambda *args: numpy.array((0.0, 0.0))


def impl_IfcAxis2Placement2D(inst):
    arr = numpy.eye(3)

    if inst is None:
        return arr

    arr.T[2, 0:2] = inst.Location.Coordinates

    if inst.RefDirection is None:
        return arr

    arr.T[0, 0:2] = inst.RefDirection.DirectionRatios
    arr.T[0, 0:2] /= numpy.linalg.norm(arr.T[0, 0:2])
    arr.T[1, 0:2] = -arr.T[0, 1], arr.T[0, 0]

    return arr


# conversion functions for semantic design parameters (not used atm)


def convert(inst):
    """
    Looks up one of the conversion functions below in the global namespace
    """
    yield from globals()[f"convert_{inst.is_a()}_{inst.PredefinedType}"](inst)


def convert_IfcAlignmentHorizontalSegment_LINE(data):
    xy = numpy.array(data.StartPoint.Coordinates)
    yield xy
    di = numpy.array([numpy.cos(data.StartDirection), numpy.sin(data.StartDirection)])
    yield xy + di * data.SegmentLength


# Two approaches, either DesignParameters or Representation


def interpret_linear_element_semantics(settings, crv):
    # traverse decomposition
    for rel in crv.IsNestedBy:
        for obj in rel.RelatedObjects:
            yield from interpret_linear_element_semantics(settings, obj)

    # lookup design parameters and dispatch to conversion function
    if crv.is_a("IfcAlignmentSegment"):
        dp = crv.DesignParameters
        yield from convert(dp)


def evaluate_segment(segment):
    # print(segment)
    # print(segment.ParentCurve)
    # print()

    func = place(map_inst(segment.Placement), map_inst(segment.ParentCurve))

    # reparam so domain starts at zero
    reparam = reparametrized_curve(func, 1.0, -segment.SegmentStart[0])

    # embed curve length (doesn't do much, just make length recoverable)
    trimmed = trimmed_curve(reparam, segment.SegmentLength[0])

    return trimmed


def interpret_linear_element_geometry(settings, crv):
    func = piecewise(
        list(
            map(
                evaluate_segment,
                crv.Representation.Representations[0].Items[0].Segments,
            )
        )
    )

    for u in numpy.linspace(0, func.length, num=int(numpy.ceil(func.length / 0.05))):
        yield func(u)


interpret_linear_element = interpret_linear_element_geometry


def create_shape(settings, elem):
    if elem.is_a("IfcLinearPositioningElement") or elem.is_a("IfcLinearElement"):
        return numpy.row_stack(list(interpret_linear_element(settings, elem)))
    else:
        return ifcopenshell.geom.create_shape(settings, elem)


def print_structure(alignment, indent=0):
    """
    Debugging function to print alignment decomposition
    """
    print(" " * indent, str(alignment)[0:100])
    for rel in alignment.IsNestedBy:
        for child in rel.RelatedObjects:
            print_structure(child, indent + 2)


if __name__ == "__main__":
    import sys
    from matplotlib import pyplot as plt

    s = ifcopenshell.express.parse("IFC4x3_RC3.exp")
    ifcopenshell.register_schema(s)
    f = ifcopenshell.open(sys.argv[1])
    print_structure(f.by_type("IfcAlignment")[0])

    al_hor = f.by_type("IfcAlignmentHorizontal")[0]
    xy = create_shape({}, al_hor)

    plt.plot(xy.T[0], xy.T[1])
    plt.savefig("horizontal_alignment.png")
