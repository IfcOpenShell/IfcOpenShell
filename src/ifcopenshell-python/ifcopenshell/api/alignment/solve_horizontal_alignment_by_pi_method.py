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

# Ported from IfcOpenShell/IfcOpenShell#8833 by Petru Conduraru (BIMvoice), onto this
# repository's PI-method API surface.

import math
from collections.abc import Sequence
from typing import Callable, NamedTuple, Optional, Union

import numpy as np

from ifcopenshell.api.alignment import _spiral_curvature

# Gauss-Legendre quadrature nodes and weights used to integrate the spiral position functions
_gauss_legendre_points = np.polynomial.legendre.leggauss(32)

# Spiral families the PI method can produce, besides CLOTHOID (see compute_spiral_end).
# VIENNESEBEND's true shape also depends on the CANT segment at the same station (gravity
# centerline height, cant angle change) -- nothing in this codebase exposes GravityCenterLineHeight
# yet (it's always written as None/0.0, here and in the raw segment table), so compute_spiral_end
# always solves it with zero cant contribution, same as every other VIENNESEBEND this project
# creates today. It's still gated on an alignment actually having a cant layout at the Bonsai UI
# layer (see prop.SPIRAL_FAMILY_ITEMS / operator._pi_curve_radii_entry) -- a real cant segment
# needs to exist there for the geometry kernel to resolve VIENNESEBEND's representation against.
SPIRAL_FAMILIES = ("CLOTHOID", "BLOSSCURVE", "COSINECURVE", "SINECURVE", "HELMERTCURVE", "CUBIC", "VIENNESEBEND")


class HorizontalSegmentDefinition(NamedTuple):
    """
    Parameters of one horizontal alignment segment produced by the PI method solver.

    The fields mirror IfcAlignmentHorizontalSegment so a definition can be written to a file
    without further computation, but the definition itself is independent of any file. Directions
    are in radians, lengths and coordinates in the caller's length unit.
    """

    start_point: tuple[float, float]
    """(X, Y) of the segment start"""

    start_direction: float
    """direction of the tangent at the segment start, in radians"""

    start_radius_of_curvature: float
    """radius at the segment start; 0.0 for straight, positive curving left, negative curving right"""

    end_radius_of_curvature: float
    """radius at the segment end, with the same sign convention as start_radius_of_curvature"""

    segment_length: float
    """length of the segment along the curve"""

    predefined_type: str
    """IfcAlignmentHorizontalSegmentTypeEnum value: LINE, CIRCULARARC, or one of SPIRAL_FAMILIES"""

    start_dist_along: float = 0.0
    """distance along the alignment at the segment start"""

    start_cant: float = 0.0
    """cant at the segment start, applied to the rail on the outside of the curve"""

    end_cant: float = 0.0
    """cant at the segment end, applied to the rail on the outside of the curve"""

    raise_left_rail: bool = False
    """True when the outside of the curve is the left rail (a curve to the right)"""

    gravity_centerline_height: float = 0.0
    """VIENNESEBEND only (0.0/unused for every other predefined_type): IfcAlignmentHorizontalSegment.
    GravityCenterLineHeight, the value _map_alignment_horizontal_segment will read back when
    rendering this segment's representation -- carried on the definition so the family's
    cant-derived curvature term stays consistent between what this solver assumed and what gets
    written and later rendered."""


def compute_clothoid_end(length: float, start_curvature: float, end_curvature: float) -> tuple[float, float, float]:
    """
    Computes the end point of a clothoid transition whose curvature varies linearly from
    start_curvature to end_curvature over length.

    The result (dx, dy, dtheta) is relative to the start of the transition, with the x-axis in the
    direction of the tangent at the start. Curvatures are signed: positive curving left, negative
    curving right. The position is computed with 32 point Gauss-Legendre quadrature of the clothoid
    integrals.

    :param length: length of the transition, measured along the curve
    :param start_curvature: curvature at the start (1/R, 0.0 for a straight)
    :param end_curvature: curvature at the end (1/R, 0.0 for a straight)
    :return: (dx, dy, dtheta) displacement and change in tangent direction over the transition
    """
    u, w = _gauss_legendre_points
    l = 0.5 * length * (u + 1.0)  # map quadrature points from (-1,1) onto (0,length)
    theta = start_curvature * l + (end_curvature - start_curvature) * l * l / (2.0 * length)
    dx = 0.5 * length * float(np.sum(w * np.cos(theta)))
    dy = 0.5 * length * float(np.sum(w * np.sin(theta)))
    dtheta = 0.5 * (start_curvature + end_curvature) * length
    return dx, dy, dtheta


def _quadrature_range(theta: Callable[[float], float], t0: float, t1: float) -> tuple[float, float, float]:
    """
    Computes (dx, dy, dtheta) for the piece of a curve from t0 to t1 of a heading-angle function
    theta(t), normalized into the frame of the tangent at t0 (i.e. as if t0 were 0), with the same
    32-point Gauss-Legendre quadrature compute_clothoid_end uses for the clothoid's closed-form
    theta. t0 need not be 0 -- this is what a family like HELMERTCURVE needs, whose second half is
    a curve trimmed starting partway through its own parametrization (see
    _spiral_curvature.helmert_theta_halves).
    """
    length = t1 - t0
    u, w = _gauss_legendre_points
    t = t0 + 0.5 * length * (u + 1.0)  # map quadrature points from (-1,1) onto (t0,t1)
    angles = np.array([theta(float(ti)) for ti in t])
    theta0 = theta(t0)
    dx_raw = 0.5 * length * float(np.sum(w * np.cos(angles)))
    dy_raw = 0.5 * length * float(np.sum(w * np.sin(angles)))
    dtheta = theta(t1) - theta0
    # rotate the raw (t0-anchored) displacement into the frame of the tangent at t0
    dx = dx_raw * math.cos(theta0) + dy_raw * math.sin(theta0)
    dy = -dx_raw * math.sin(theta0) + dy_raw * math.cos(theta0)
    return dx, dy, dtheta


def _quadrature_end(theta: Callable[[float], float], length: float) -> tuple[float, float, float]:
    """
    Computes (dx, dy, dtheta) for a spiral transition given its heading-angle function theta(l)
    (arc length l in [0, length], heading measured from the tangent at l=0). The t0=0 case of
    _quadrature_range, kept separate since it's what most families use and needs no normalization
    (theta(0) is always 0 for them).
    """
    return _quadrature_range(theta, 0.0, length)


def _cubic_arc_length(A1: float, A2: float, A3: float, x: float) -> float:
    """Signed arc length of y = A0 + A1*t + A2*t^2 + A3*t^3 from 0 to x (A0 doesn't affect arc
    length), via the same 32-point Gauss-Legendre quadrature used elsewhere in this module."""
    u, w = _gauss_legendre_points
    t = 0.5 * x * (u + 1.0)
    slope = A1 + 2.0 * A2 * t + 3.0 * A3 * t * t
    return 0.5 * x * float(np.sum(w * np.sqrt(1.0 + slope * slope)))


def _cubic_x_at_arc_length(A1: float, A2: float, A3: float, s: float) -> float:
    """Inverts _cubic_arc_length by Newton's method, matching the geometry kernel's own
    x_at_dist_along (IfcCurveSegment.cpp) so a CUBIC endpoint predicted here matches what the
    kernel will later render for the same IfcPolynomialCurve."""
    x = s  # s = x is a very close starting guess for a curve this gentle
    for _ in range(50):
        slope = A1 + 2.0 * A2 * x + 3.0 * A3 * x * x
        step = (_cubic_arc_length(A1, A2, A3, x) - s) / math.sqrt(1.0 + slope * slope)
        x -= step
        if abs(step) < 1.0e-12 * max(1.0, abs(x)):
            break
    return x


def compute_spiral_end(
    family: str, length: float, start_radius: float, end_radius: float, cant_factor: float = 0.0
) -> tuple[float, float, float]:
    """
    Computes the (dx, dy, dtheta) displacement of a spiral transition of the given family, the same
    way compute_clothoid_end does for CLOTHOID, generalized to every spiral family
    _map_alignment_horizontal_segment can turn into real geometry (see SPIRAL_FAMILIES).

    The curvature law for each family comes from _spiral_curvature, which is also what
    _map_alignment_horizontal_segment uses to build the actual IfcCurveSegment representation --
    so the endpoint this function predicts is the one the geometry kernel will later render.

    :param family: one of SPIRAL_FAMILIES
    :param length: length of the transition, measured along the curve
    :param start_radius: radius at the start (0.0 for a straight), signed as elsewhere in this module
    :param end_radius: radius at the end, same sign convention
    :param cant_factor: VIENNESEBEND only (ignored otherwise) -- see
        _spiral_curvature.viennese_bend_coefficients; the main solve loop derives this per spiral
        leg from a PI's gravity centerline height and cant, see the "extra" element of its radii
        tuple.
    :return: (dx, dy, dtheta) displacement and change in tangent direction over the transition
    """
    if family == "CLOTHOID":
        start_curvature = 1.0 / start_radius if start_radius != 0.0 else 0.0
        end_curvature = 1.0 / end_radius if end_radius != 0.0 else 0.0
        return compute_clothoid_end(length, start_curvature, end_curvature)

    if family == "BLOSSCURVE":
        return _quadrature_end(_spiral_curvature.bloss_theta(length, start_radius, end_radius), length)

    if family == "COSINECURVE":
        return _quadrature_end(_spiral_curvature.cosine_theta(length, start_radius, end_radius), length)

    if family == "SINECURVE":
        return _quadrature_end(_spiral_curvature.sine_theta(length, start_radius, end_radius), length)

    if family == "VIENNESEBEND":
        return _quadrature_end(
            _spiral_curvature.viennese_bend_theta(length, start_radius, end_radius, cant_factor), length
        )

    if family == "HELMERTCURVE":
        # Helmert is inherently two pieces, the second trimmed starting at its own parameter
        # length/2 (see _spiral_curvature.helmert_theta_halves) -- integrate each half over its own
        # true range, then compose them the same way this module's own main loop composes
        # entry-spiral/arc/exit-spiral pieces into one alignment.
        half_length = length / 2.0
        theta1, theta2 = _spiral_curvature.helmert_theta_halves(length, start_radius, end_radius)
        dx1, dy1, dtheta1 = _quadrature_range(theta1, 0.0, half_length)
        dx2, dy2, dtheta2 = _quadrature_range(theta2, half_length, length)
        dx = dx1 + dx2 * math.cos(dtheta1) - dy2 * math.sin(dtheta1)
        dy = dy1 + dx2 * math.sin(dtheta1) + dy2 * math.cos(dtheta1)
        dtheta = dtheta1 + dtheta2
        return dx, dy, dtheta

    if family == "CUBIC":
        # Cartesian curve (y = A3*x^3), not a curvature-vs-arclength law like the other families.
        # The geometry kernel evaluates it by numerically inverting the true arc-length integral to
        # find the x matching each end of the trimmed [offset, offset+length] range (see
        # IfcCurveSegment.cpp's x_at_dist_along) -- _cubic_x_at_arc_length mirrors that inversion so
        # this endpoint matches what the kernel will render.
        A0, A1, A2, A3, offset = _spiral_curvature.cubic_coefficients(length, start_radius, end_radius)

        def y(t: float) -> float:
            return A0 + A1 * t + A2 * t * t + A3 * t**3

        def slope(t: float) -> float:
            return A1 + 2.0 * A2 * t + 3.0 * A3 * t * t

        x0 = _cubic_x_at_arc_length(A1, A2, A3, offset)
        x1 = _cubic_x_at_arc_length(A1, A2, A3, offset + length)
        theta0 = math.atan(slope(x0))
        theta1 = math.atan(slope(x1))
        dx_raw = x1 - x0
        dy_raw = y(x1) - y(x0)
        # rotate the raw (world-frame) displacement into the frame of the tangent at x0
        dx = dx_raw * math.cos(theta0) + dy_raw * math.sin(theta0)
        dy = -dx_raw * math.sin(theta0) + dy_raw * math.cos(theta0)
        return dx, dy, theta1 - theta0

    raise ValueError(f"unsupported spiral family '{family}'; expected one of {SPIRAL_FAMILIES}")


def compute_horizontal_segment_end(segment: HorizontalSegmentDefinition) -> tuple[float, float, float]:
    """
    Computes the end point and end direction of a horizontal segment definition.

    Useful for checking position and direction continuity between consecutive segments: the result
    for one segment should match the start_point and start_direction of the next.

    :param segment: the segment definition
    :return: (x, y, direction) at the end of the segment, direction in radians
    """
    x, y = segment.start_point
    direction = segment.start_direction
    length = segment.segment_length

    if segment.predefined_type == "LINE":
        return (x + length * math.cos(direction), y + length * math.sin(direction), direction)

    if segment.predefined_type == "CIRCULARARC":
        start_curvature = 1.0 / segment.start_radius_of_curvature if segment.start_radius_of_curvature != 0.0 else 0.0
        dtheta = start_curvature * length
        dx = math.sin(dtheta) / start_curvature
        dy = (1.0 - math.cos(dtheta)) / start_curvature
    elif segment.predefined_type in SPIRAL_FAMILIES:
        dx, dy, dtheta = compute_spiral_end(
            segment.predefined_type, length, segment.start_radius_of_curvature, segment.end_radius_of_curvature
        )
    else:
        raise NotImplementedError(f"unsupported predefined type '{segment.predefined_type}'")

    return (
        x + dx * math.cos(direction) - dy * math.sin(direction),
        y + dx * math.sin(direction) + dy * math.cos(direction),
        direction + dtheta,
    )


def solve_horizontal_alignment_by_pi_method(
    hpoints: Sequence[Sequence[float]],
    radii: Sequence[Union[float, Sequence[float]]],
    cants: Optional[Sequence[float]] = None,
) -> list[HorizontalSegmentDefinition]:
    """
    Solves a horizontal alignment defined by the PI layout method into a continuous sequence of
    segment definitions.

    This is a pure geometric computation: no file is read or written. Use
    layout_horizontal_alignment_by_pi_method to write the solution to an IfcAlignmentHorizontal
    layout, or consume the returned definitions directly, for example to preview an alignment in
    an interactive editor before committing it to a file.

    Each element of radii defines the transition at the corresponding PI and is either:

        R - radius of a circular curve (tangent runs connect directly to the circular curve), or

        (R, Lin, Lout) - radius of a circular curve with clothoid spiral transition curves of length
        Lin ahead of the curve and Lout following the curve, or

        (R, Lin, Lout, family) - as above, with the entry and exit spirals both built from the
        named family instead of CLOTHOID. family is one of SPIRAL_FAMILIES; entry and exit always
        share the same family at a given PI, or

        (R, Lin, Lout, family, cant_params) - as above, with cant_params supplying the extra data
        VIENNESEBEND's curvature needs (ignored for every other family): a
        (gravity_centerline_height, cant, rail_head_distance) tuple, where cant is the outer rail's
        superelevation magnitude at the arc (same convention as the cants parameter below) and
        rail_head_distance is the alignment's cant layout's own RailHeadDistance. cant_params may be
        None (or the whole 5-tuple omitted) for a VIENNESEBEND PI with no cant contribution -- it
        then solves as a plain degree-7 curvature-integral spiral, same as every other family.
        Unlike cants below, this never creates or modifies any cant segment -- it only feeds
        already-known cant data into the horizontal segment's own geometry.

        When spiral transitions are used the circular curve shifts inward relative to the tangent
        runs so the tangent runs, spirals, and circular curve are continuous in position and
        direction. Lin and Lout can be 0.0 for a spiral-less connection on that end of the curve.

    If cants is provided, each definition also carries the cant at the segment start and end,
    applied to the rail on the outside of the curve: zero cant on tangent runs, linearly varying
    cant over spiral transitions, and constant cant over circular curves. Because every horizontal
    segment carries its own cant values, a cant layout built from the definitions is one-for-one
    with the horizontal layout. Curves with a non-zero cant require entry and exit spiral
    transition curves so the cant profile is continuous.

    :param hpoints: (X, Y) pairs denoting the location of the horizontal PIs, including start (POB) and end (POE).
    :param radii: radius values to use for transition, optionally with spiral transition lengths
    :param cants: cant values, one per PI curve, applied to the outer rail
    :return: list of segment definitions, in order, continuous in position and direction
    """
    if not (len(hpoints) - 2 == len(radii)):
        raise ValueError("radii should have two fewer elements that hpoints")

    if cants is not None and not (len(cants) == len(radii)):
        raise ValueError("cants should have the same number of elements as radii")

    segments: list[HorizontalSegmentDefinition] = []

    xBT, yBT = hpoints[0]
    xPI, yPI = hpoints[1]

    i = 1
    dist_along = 0.0  # distance along the horizontal alignment at the start of the next segment

    for curve_index, curve in enumerate(radii):
        if isinstance(curve, (int, float)):
            radius = float(curve)
            entry_length = 0.0
            exit_length = 0.0
            family = "CLOTHOID"
            vb_params = None
        else:
            if len(curve) not in (3, 4, 5):
                raise ValueError(
                    "each radii element should be a radius R, a (R, Lin, Lout) sequence, a "
                    "(R, Lin, Lout, family) sequence, or a (R, Lin, Lout, family, cant_params) sequence"
                )
            radius, entry_length, exit_length = (float(v) for v in curve[:3])
            family = curve[3] if len(curve) >= 4 else "CLOTHOID"
            vb_params = curve[4] if len(curve) == 5 else None
            if family not in SPIRAL_FAMILIES:
                raise ValueError(f"unsupported spiral family '{family}'; expected one of {SPIRAL_FAMILIES}")
            if radius == 0.0 and (entry_length != 0.0 or exit_length != 0.0):
                raise ValueError("spiral transition lengths require a non-zero radius")

        cant = float(cants[curve_index]) if cants is not None else 0.0
        if cant != 0.0 and (entry_length == 0.0 or exit_length == 0.0):
            raise ValueError(
                "curves with a non-zero cant require entry and exit spiral transition curves; "
                "otherwise the cant profile is discontinuous"
            )

        # back tangent
        dxBT = xPI - xBT
        dyBT = yPI - yBT
        angleBT = math.atan2(dyBT, dxBT)
        lengthBT = math.sqrt(dxBT * dxBT + dyBT * dyBT)

        # forward tangent
        i += 1
        xFT, yFT = hpoints[i]
        dxFT = xFT - xPI
        dyFT = yFT - yPI
        angleFT = math.atan2(dyFT, dxFT)

        delta = angleFT - angleBT

        if entry_length == 0.0 and exit_length == 0.0:
            # tangent runs connect directly to the circular curve
            tangent = abs(radius * math.tan(delta / 2))

            lc = abs(radius * delta)

            radius *= delta / abs(delta)

            xPC = xPI - tangent * math.cos(angleBT)
            yPC = yPI - tangent * math.sin(angleBT)

            xPT = xPI + tangent * math.cos(angleFT)
            yPT = yPI + tangent * math.sin(angleFT)

            tangent_run = lengthBT - tangent

            if tangent_run < -1.0e-03:
                raise ValueError(
                    f"PI {curve_index + 1}: curve radius is too large for the distance between PIs; "
                    "use a smaller radius or move the PIs farther apart"
                )

            # back tangent run
            if 1.0e-03 < tangent_run:
                segments.append(
                    HorizontalSegmentDefinition(
                        start_point=(xBT, yBT),
                        start_direction=angleBT,
                        start_radius_of_curvature=0.0,
                        end_radius_of_curvature=0.0,
                        segment_length=tangent_run,
                        predefined_type="LINE",
                        start_dist_along=dist_along,
                        raise_left_rail=delta < 0.0,
                    )
                )
                dist_along += tangent_run

            # circular curve
            if radius != 0.0:
                segments.append(
                    HorizontalSegmentDefinition(
                        start_point=(xPC, yPC),
                        start_direction=angleBT,
                        start_radius_of_curvature=float(radius),
                        end_radius_of_curvature=float(radius),
                        segment_length=lc,
                        predefined_type="CIRCULARARC",
                        start_dist_along=dist_along,
                        start_cant=cant,
                        end_cant=cant,
                        raise_left_rail=delta < 0.0,
                    )
                )
                dist_along += lc
        else:
            # tangent runs connect to the circular curve with clothoid spiral transition curves.
            # normalize the deflection angle onto (-pi, pi)
            delta = math.atan2(math.sin(delta), math.cos(delta))
            if delta == 0.0:
                raise ValueError(f"PI {curve_index + 1}: deflection angle is zero; spiral transitions cannot be created")

            R = abs(radius)
            s = 1.0 if 0.0 < delta else -1.0  # +1 curve to the left, -1 curve to the right

            # VIENNESEBEND's cant-derived curvature correction (ignored for every other family --
            # see compute_spiral_end/_spiral_curvature.viennese_bend_coefficients). The cant angle
            # ramps 0 -> full at the arc over the entry spiral and full -> 0 over the exit spiral,
            # mirroring how start_radius_of_curvature/end_radius_of_curvature ramp over the same two
            # spirals; its sign follows which rail is raised, exactly as _map_viennese_bend derives
            # cant_angle_start/end from StartCantLeft/Right (raise_left_rail=True, i.e. a curve to
            # the right, puts the raised rail on the left, giving a negative angle by that formula).
            entry_cant_factor = 0.0
            exit_cant_factor = 0.0
            gravity_centerline_height = 0.0
            if family == "VIENNESEBEND" and vb_params is not None:
                gravity_centerline_height, vb_cant, rail_head_distance = (float(v) for v in vb_params)
                cant_angle_full = vb_cant / rail_head_distance if rail_head_distance else 0.0
                if s < 0.0:  # curve to the right -> raised rail is the left one
                    cant_angle_full = -cant_angle_full
                if 0.0 < entry_length:
                    entry_cant_factor = -420.0 * (gravity_centerline_height / entry_length) * cant_angle_full
                if 0.0 < exit_length:
                    exit_cant_factor = -420.0 * (gravity_centerline_height / exit_length) * (-cant_angle_full)

            # deflection of the entry/exit spiral, taken from the family's own actual (dx, dy,
            # dtheta) rather than assumed to be entry_length / (2*R) -- that closed form is exact
            # for CLOTHOID and happens to also hold for the other curvature-integral families
            # (Bloss, Cosine, Sine, Helmert are all normalized to the same total deflection as
            # clothoid for a given length and radius), but CUBIC's Cartesian small-angle
            # approximation doesn't hit it exactly, and using the real dtheta keeps every family
            # geometrically exact here regardless.
            entry_end = (
                compute_spiral_end(family, entry_length, 0.0, R, entry_cant_factor) if 0.0 < entry_length else None
            )
            exit_end = compute_spiral_end(family, exit_length, R, 0.0, exit_cant_factor) if 0.0 < exit_length else None
            theta1 = entry_end[2] if entry_end is not None else 0.0
            theta2 = exit_end[2] if exit_end is not None else 0.0
            theta_c = abs(delta) - theta1 - theta2  # deflection of the circular curve
            if theta_c < 0.0:
                raise ValueError(
                    f"PI {curve_index + 1}: spiral transition curves are too long; their combined deflection "
                    "exceeds the PI deflection angle"
                )
            lc = R * theta_c

            # compose the displacement from the start of the entry spiral (TS) to the end of the
            # exit spiral (ST), in a frame with the x-axis along the back tangent.
            # pieces are computed for a curve to the left and mirrored by s.
            pieces = []
            if entry_end is not None:
                pieces.append(entry_end)
            pieces.append((R * math.sin(theta_c), R * (1.0 - math.cos(theta_c)), theta_c))
            if exit_end is not None:
                pieces.append(exit_end)

            x = 0.0
            y = 0.0
            direction = 0.0
            for dx_, dy_, dtheta_ in pieces:
                x += dx_ * math.cos(direction) - s * dy_ * math.sin(direction)
                y += dx_ * math.sin(direction) + s * dy_ * math.cos(direction)
                direction += s * dtheta_

            # locate TS on the back tangent and ST on the forward tangent so that the curve ends on
            # the forward tangent. this accounts for the inward shift of the circular curve.
            ts_to_pi = x - y / math.tan(delta)  # distance from TS to the PI, along the back tangent
            pi_to_st = y / math.sin(delta)  # distance from the PI to ST, along the forward tangent

            tangent_run = lengthBT - ts_to_pi

            if tangent_run < -1.0e-03:
                raise ValueError(
                    f"PI {curve_index + 1}: spiral transition curves are too long for the distance between PIs; "
                    "use shorter spirals/a smaller radius or move the PIs farther apart"
                )

            # back tangent run
            if 1.0e-03 < tangent_run:
                segments.append(
                    HorizontalSegmentDefinition(
                        start_point=(xBT, yBT),
                        start_direction=angleBT,
                        start_radius_of_curvature=0.0,
                        end_radius_of_curvature=0.0,
                        segment_length=tangent_run,
                        predefined_type="LINE",
                        start_dist_along=dist_along,
                        raise_left_rail=delta < 0.0,
                    )
                )
                dist_along += tangent_run

            signed_radius = s * R
            cur_x = xPI - ts_to_pi * math.cos(angleBT)
            cur_y = yPI - ts_to_pi * math.sin(angleBT)
            cur_direction = angleBT

            # entry spiral
            if 0.0 < entry_length:
                segments.append(
                    HorizontalSegmentDefinition(
                        start_point=(cur_x, cur_y),
                        start_direction=cur_direction,
                        start_radius_of_curvature=0.0,
                        end_radius_of_curvature=signed_radius,
                        segment_length=entry_length,
                        predefined_type=family,
                        start_dist_along=dist_along,
                        start_cant=0.0,
                        end_cant=cant,
                        raise_left_rail=delta < 0.0,
                        gravity_centerline_height=gravity_centerline_height,
                    )
                )
                dist_along += entry_length

                dx_, dy_, dtheta_ = entry_end
                cur_x += dx_ * math.cos(cur_direction) - s * dy_ * math.sin(cur_direction)
                cur_y += dx_ * math.sin(cur_direction) + s * dy_ * math.cos(cur_direction)
                cur_direction += s * dtheta_

            # circular curve
            if 1.0e-03 < lc:
                segments.append(
                    HorizontalSegmentDefinition(
                        start_point=(cur_x, cur_y),
                        start_direction=cur_direction,
                        start_radius_of_curvature=signed_radius,
                        end_radius_of_curvature=signed_radius,
                        segment_length=lc,
                        predefined_type="CIRCULARARC",
                        start_dist_along=dist_along,
                        start_cant=cant,
                        end_cant=cant,
                        raise_left_rail=delta < 0.0,
                    )
                )
                dist_along += lc

            cur_x += R * math.sin(theta_c) * math.cos(cur_direction) - s * R * (1.0 - math.cos(theta_c)) * math.sin(
                cur_direction
            )
            cur_y += R * math.sin(theta_c) * math.sin(cur_direction) + s * R * (1.0 - math.cos(theta_c)) * math.cos(
                cur_direction
            )
            cur_direction += s * theta_c

            # exit spiral
            if 0.0 < exit_length:
                segments.append(
                    HorizontalSegmentDefinition(
                        start_point=(cur_x, cur_y),
                        start_direction=cur_direction,
                        start_radius_of_curvature=signed_radius,
                        end_radius_of_curvature=0.0,
                        segment_length=exit_length,
                        predefined_type=family,
                        start_dist_along=dist_along,
                        start_cant=cant,
                        end_cant=0.0,
                        raise_left_rail=delta < 0.0,
                        gravity_centerline_height=gravity_centerline_height,
                    )
                )
                dist_along += exit_length

            xPT = xPI + pi_to_st * math.cos(angleFT)
            yPT = yPI + pi_to_st * math.sin(angleFT)

        xBT = xPT
        yBT = yPT
        xPI = xFT
        yPI = yFT

    # done processing radii
    # last tangent run
    dx = xPI - xBT
    dy = yPI - yBT
    angleBT = math.atan2(dy, dx)
    tangent_run = math.sqrt(dx * dx + dy * dy)

    if 1.0e-03 < tangent_run:
        segments.append(
            HorizontalSegmentDefinition(
                start_point=(xBT, yBT),
                start_direction=angleBT,
                start_radius_of_curvature=0.0,
                end_radius_of_curvature=0.0,
                segment_length=tangent_run,
                predefined_type="LINE",
                start_dist_along=dist_along,
            )
        )

    return segments
