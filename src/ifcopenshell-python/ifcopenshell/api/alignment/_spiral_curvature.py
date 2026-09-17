# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2025 Thomas Krijnen <thomas@aecgeeks.com>
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

"""
Curvature-law math shared between _map_alignment_horizontal_segment (which builds the IFC
representation entities for a horizontal segment whose business-logic start/end radius and length
are already known) and solve_horizontal_alignment_by_pi_method (which needs the same curvature law
in the opposite direction: given start/end radius and length, what (dx, dy, dtheta) displacement
does the segment produce).

Every formula here is a direct translation of the corresponding case in the geometry kernel's
IfcCurveSegment evaluator (src/ifcgeom/mapping/IfcCurveSegment.cpp), so a value computed here and
later re-evaluated by the kernel always agree. Keeping this math in one place (rather than letting
_map_alignment_horizontal_segment and the PI-method solver each carry their own copy) is what makes
that guarantee cheap to keep true.
"""

import math
from collections.abc import Sequence
from typing import Callable, Optional


def curve_factor(length: float, start_radius: float, end_radius: float) -> float:
    """The "f" curvature-change factor used throughout the polynomial spiral families."""
    return (0.0 if end_radius == 0.0 else length / end_radius) - (0.0 if start_radius == 0.0 else length / start_radius)


def _scale_term(a: float, length: float, power: int) -> float:
    """A_i = length * |a_i|^(-1/power) * sign(a_i), the scaling every polynomial spiral term uses
    to go from its raw curvature-law coefficient to the IFC-attribute value (ConstantTerm,
    LinearTerm, QuadraticTerm, ...)."""
    if a == 0.0:
        return 0.0
    return length * math.pow(math.fabs(a), -1.0 / power) * (a / math.fabs(a))


def polynomial_spiral_theta(terms: Sequence[Optional[float]]) -> Callable[[float], float]:
    """theta(t) for a polynomial spiral (IfcSecondOrderPolynomialSpiral, IfcThirdOrderPolynomial-
    Spiral, IfcSeventhOrderPolynomialSpiral) given its A0..A7 terms (any may be 0.0/None for an
    unused term), matching polynomial_spiral()'s theta lambda and helmert_curve_point() in
    IfcCurveSegment.cpp / function_item_evaluator.cpp exactly (both are the same formula, the
    latter just fixed to 3 terms)."""

    def theta(t: float) -> float:
        total = 0.0
        for i, a_i in enumerate(terms):
            if not a_i:
                continue
            power = i + 1
            if i % 2 == 0:
                total += t**power / (power * a_i**power)
            else:
                total += a_i * t**power / (power * abs(a_i ** (power + 1)))
        return total

    return theta


def bloss_coefficients(length: float, start_radius: float, end_radius: float) -> tuple[float, float, float, float]:
    """(A0, A1, A2, A3) for IfcThirdOrderPolynomialSpiral, matching _map_bloss_curve."""
    f = curve_factor(length, start_radius, end_radius)
    a0 = length / start_radius if start_radius != 0.0 else 0.0
    a2 = 3.0 * f
    a3 = -2.0 * f
    return (
        _scale_term(a0, length, 1),
        0.0,
        _scale_term(a2, length, 3),
        _scale_term(a3, length, 4),
    )


def bloss_theta(length: float, start_radius: float, end_radius: float) -> Callable[[float], float]:
    return polynomial_spiral_theta(bloss_coefficients(length, start_radius, end_radius))


def helmert_coefficients(
    length: float, start_radius: float, end_radius: float
) -> tuple[tuple[float, float, float], tuple[float, float, float]]:
    """((A0_1, A1_1, A2_1), (A0_2, A1_2, A2_2)) for the two IfcSecondOrderPolynomialSpiral halves,
    matching _map_helmert_curve. Each half is valid over its own local [0, length/2]."""
    f = curve_factor(length, start_radius, end_radius)

    a0_1 = length / start_radius if start_radius != 0.0 else 0.0
    a2_1 = 2.0 * f
    half1 = (
        _scale_term(a0_1, length, 1),
        0.0,
        _scale_term(a2_1, length, 3),
    )

    a0_2 = -1.0 * f + (length / start_radius if start_radius != 0.0 else 0.0)
    a1_2 = 4.0 * f
    a2_2 = -2.0 * f
    half2 = (
        _scale_term(a0_2, length, 1),
        _scale_term(a1_2, length, 2),
        _scale_term(a2_2, length, 3),
    )

    return half1, half2


def helmert_theta_halves(
    length: float, start_radius: float, end_radius: float
) -> tuple[Callable[[float], float], Callable[[float], float]]:
    """theta(t) for each of the two IfcSecondOrderPolynomialSpiral halves, each defined (and only
    valid) over its own local [0, length/2] -- matching how _map_helmert_curve builds them, with
    the *second* half's underlying curve trimmed starting at parameter length/2 (its SegmentStart),
    not 0. A caller composing the whole HELMERTCURVE segment's endpoint must integrate the second
    half's theta over [length/2, length], not [0, length/2] -- see compute_spiral_end."""
    half1, half2 = helmert_coefficients(length, start_radius, end_radius)
    return polynomial_spiral_theta(half1), polynomial_spiral_theta(half2)


def cosine_coefficients(length: float, start_radius: float, end_radius: float) -> tuple[float, float]:
    """(ConstantTerm, CosineTerm) for IfcCosineSpiral, matching _map_cosine_curve."""
    f = curve_factor(length, start_radius, end_radius)
    a0 = 0.5 * f + (length / start_radius if start_radius != 0.0 else 0.0)
    a1 = -0.5 * f
    return _scale_term(a0, length, 1), _scale_term(a1, length, 1)


def cosine_theta(length: float, start_radius: float, end_radius: float) -> Callable[[float], float]:
    """theta(t) for IfcCosineSpiral, matching its IfcCurveSegment.cpp operator()."""
    constant_term, cosine_term = cosine_coefficients(length, start_radius, end_radius)

    def theta(t: float) -> float:
        a0 = t / constant_term if constant_term != 0.0 else 0.0
        a1 = (length / math.pi) * (1.0 / cosine_term) * math.sin((math.pi / length) * t) if cosine_term != 0.0 else 0.0
        return a0 + a1

    return theta


def sine_coefficients(length: float, start_radius: float, end_radius: float) -> tuple[float, float, float]:
    """(ConstantTerm, LinearTerm, SineTerm) for IfcSineSpiral, matching _map_sine_curve."""
    f = curve_factor(length, start_radius, end_radius)
    a0 = length / start_radius if start_radius != 0.0 else 0.0
    a1 = f
    a2 = -f / (2.0 * math.pi)
    return (
        _scale_term(a0, length, 1),
        _scale_term(a1, length, 2),
        _scale_term(a2, length, 1),
    )


def cubic_coefficients(
    length: float, start_radius: float, end_radius: float
) -> tuple[float, float, float, float, float]:
    """(A0, A1, A2, A3, offset) for the IfcPolynomialCurve (CoefficientsY) backing CUBIC, matching
    _map_cubic. Unlike the other families, this is a Cartesian small-angle approximation
    (y = A0 + A1*x + A2*x^2 + A3*x^3, x taken directly as the arc-length domain) rather than a
    curvature-vs-arclength law, and the polynomial's own x=0 is wherever curvature is zero -- offset
    locates the segment's actual start relative to that point."""
    offset = 0.0
    A0 = 0.0
    A1 = 0.0
    A2 = 0.0
    A3 = 0.0

    if end_radius != 0.0 and start_radius != 0.0 and end_radius != start_radius:
        f = (start_radius - end_radius) / end_radius
        A3 = f / (6.0 * start_radius * length)
        offset = length / f
    elif end_radius != 0.0:
        A3 = 1.0 / (6.0 * end_radius * length)
        offset = 0.0
    elif start_radius != 0.0:
        A3 = -1.0 / (6.0 * start_radius * length)
        offset = -length

    return A0, A1, A2, A3, offset


def viennese_bend_coefficients(
    length: float, start_radius: float, end_radius: float, cant_factor: float = 0.0
) -> tuple[float, float, float, float, float, float, float, float]:
    """(A0..A7) for IfcSeventhOrderPolynomialSpiral, matching _map_viennese_bend.

    cant_factor folds in the cant-derived terms (-420 * (gravity_centerline_height / length) *
    (cant_angle_end - cant_angle_start) in _map_viennese_bend) -- callers with no cant angle change
    to give it (or no GravityCenterLineHeight at all, which is every caller in this codebase today;
    nothing yet exposes that field) pass 0.0, which is also the default: a Viennese bend with no
    cant contribution is just a plain degree-7 curvature-integral spiral driven by the radius
    change alone (a0/a4/a5/a6/a7 from f only, matching Bloss/Cosine/Sine/Helmert's own pattern, just
    a higher polynomial order).
    """
    f = curve_factor(length, start_radius, end_radius)
    a0 = length / start_radius if start_radius != 0.0 else 0.0
    a2 = 1.0 * cant_factor
    a3 = -4.0 * cant_factor
    a4 = 5.0 * cant_factor + 35.0 * f
    a5 = -2.0 * cant_factor - 84.0 * f
    a6 = 70.0 * f
    a7 = -20.0 * f
    return (
        _scale_term(a0, length, 1),
        0.0,
        _scale_term(a2, length, 3),
        _scale_term(a3, length, 4),
        _scale_term(a4, length, 5),
        _scale_term(a5, length, 6),
        _scale_term(a6, length, 7),
        _scale_term(a7, length, 8),
    )


def viennese_bend_theta(
    length: float, start_radius: float, end_radius: float, cant_factor: float = 0.0
) -> Callable[[float], float]:
    return polynomial_spiral_theta(viennese_bend_coefficients(length, start_radius, end_radius, cant_factor))


def sine_theta(length: float, start_radius: float, end_radius: float) -> Callable[[float], float]:
    """theta(t) for IfcSineSpiral, matching its IfcCurveSegment.cpp operator()."""
    constant_term, linear_term, sine_term = sine_coefficients(length, start_radius, end_radius)

    def theta(t: float) -> float:
        a0 = t / constant_term if constant_term != 0.0 else 0.0
        a1 = (linear_term / abs(linear_term)) * (t / linear_term) ** 2 / 2.0 if linear_term != 0.0 else 0.0
        a2 = (
            -1.0 * (length / (2.0 * math.pi * sine_term)) * (math.cos(2.0 * math.pi * t / length) - 1.0)
            if sine_term != 0.0
            else 0.0
        )
        return a0 + a1 + a2

    return theta
