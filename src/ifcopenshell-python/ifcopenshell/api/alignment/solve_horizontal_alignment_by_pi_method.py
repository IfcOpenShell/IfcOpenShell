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


def _pi_join_closure_excess(previous_tangent_out: float, tangent_in: float, pi_to_pi_distance: float) -> float:
    """
    The signed gap between what a join_next junction's two curves claim on their shared leg and
    the actual PI-to-PI distance: positive means the tangent claims overshoot the leg (curves too
    big for the gap), negative means they fall short (curves too small). Zero is exact closure.

    Split out from _check_pi_join_closure as a small, reusable, numeric alternative to only being
    able to detect success/failure by catching-and-parsing that function's exception text.
    solve_join_next_radius takes the already-combined target (pi_to_pi_distance minus the joining
    curve's own tangent-out claim) rather than the three separate values here, so its own root
    residual is one line simpler than calling this directly -- but the two describe the same
    quantity, and this is what _check_pi_join_closure itself now computes and raises on.
    """
    return (previous_tangent_out + tangent_in) - pi_to_pi_distance


def _check_pi_join_closure(
    previous_tangent_out: float, tangent_in: float, pi_to_pi_distance: float, pi_number: int
) -> None:
    """
    Validates that the tangent length claimed by a join_next curve on its shared leg, plus the
    tangent length claimed by the curve at the next PI, sum to exactly the PI-to-PI distance so the
    two curves meet at a single shared tangency point (a PCC or PRC) with no intermediate tangent
    run. Raises ValueError, naming the excess or shortfall and the PIs involved, when the curves
    cannot close this way.

    Tolerance is 1e-4 relative, not the tighter 1e-9 a pure-float64 solver could get away with:
    hpoints reaching this solver from the Bonsai UI have typically round-tripped through at least
    one Blender Object.location, which is float32 (~1e-7 relative precision) -- 1e-9 would reject
    a PI pair the user positioned exactly right, just because a marker was dragged through single
    precision along the way. 1e-4 (0.01%) still catches a genuinely too-tight/too-loose PI pair
    (real user error, typically off by a meaningful percentage) while comfortably absorbing that
    round-trip noise.

    :param previous_tangent_out: tangent length the join_next curve claims on the shared leg
    :param tangent_in: tangent length the curve at the next PI claims on the shared leg
    :param pi_to_pi_distance: distance between the two PIs
    :param pi_number: 1-based number of the PI whose curve is the join target (the second of the pair)
    """
    total_tangent = previous_tangent_out + tangent_in
    tolerance = 1.0e-4 * pi_to_pi_distance
    excess = _pi_join_closure_excess(previous_tangent_out, tangent_in, pi_to_pi_distance)
    if abs(excess) <= tolerance:
        return
    if excess > 0.0:
        raise ValueError(
            f"compound/reverse curves at PI {pi_number - 1}-{pi_number} cannot close: tangent runs "
            f"T1+T2 = {total_tangent:.6g} exceed the {pi_to_pi_distance:.6g} PI-to-PI distance by "
            f"{excess:.6g}; reduce the radius or spiral lengths at PI {pi_number - 1} or PI {pi_number}"
        )
    raise ValueError(
        f"compound/reverse curves at PI {pi_number - 1}-{pi_number} cannot close: tangent runs "
        f"T1+T2 = {total_tangent:.6g} fall short of the {pi_to_pi_distance:.6g} PI-to-PI distance "
        f"by {-excess:.6g}; increase the radius or spiral lengths at PI {pi_number - 1} or PI {pi_number}"
    )


class _SpiralCurveSolution(NamedTuple):
    """Geometric pieces of one PI's spiral-circular-spiral curve (or spiral-circular /
    circular-spiral, when one length is 0.0) -- everything solve_horizontal_alignment_by_pi_method's
    main loop needs to both validate closure and build the actual segments, factored out so
    solve_join_next_radius can reuse the exact same math (never an independent re-derivation)."""

    R: float
    s: float
    signed_radius: float
    theta_c: float
    lc: float
    ts_to_pi: float
    """distance from TS (or PC, if there's no entry spiral) to the PI, along the back tangent"""
    pi_to_st: float
    """distance from the PI to ST (or PT, if there's no exit spiral), along the forward tangent"""
    entry_end: Optional[tuple[float, float, float]]
    exit_end: Optional[tuple[float, float, float]]
    gravity_centerline_height: float


def _solve_spiral_curve(
    delta: float,
    radius: float,
    entry_length: float,
    exit_length: float,
    family: str,
    vb_params: Optional[Sequence[float]],
    pi_number: int,
) -> _SpiralCurveSolution:
    """
    Computes one PI's spiral-transitioned curve geometry: entry spiral (optional) + circular arc +
    exit spiral (optional), given the PI's own deflection. Used both by
    solve_horizontal_alignment_by_pi_method's main loop (to build the actual segments) and by
    solve_join_next_radius (to evaluate a candidate radius's tangent claim during root-finding) --
    kept as the single place this math is written, so both always agree exactly.

    :param delta: PI deflection angle, radians, already normalized to (-pi, pi)
    :param radius: radius magnitude (sign, if any, is ignored -- direction comes from delta)
    :param entry_length: entry spiral length, 0.0 for none
    :param exit_length: exit spiral length, 0.0 for none
    :param family: one of SPIRAL_FAMILIES
    :param vb_params: VIENNESEBEND-only (gravity_centerline_height, cant, rail_head_distance), or
        None for every other family or a VIENNESEBEND PI with no cant contribution
    :param pi_number: 1-based PI number, used only in the "spirals too long" error message
    :raises ValueError: if the entry+exit spiral deflection exceeds the PI's own deflection
    """
    R = abs(radius)
    s = 1.0 if 0.0 < delta else -1.0  # +1 curve to the left, -1 curve to the right

    # VIENNESEBEND's cant-derived curvature correction (ignored for every other family -- see
    # compute_spiral_end/_spiral_curvature.viennese_bend_coefficients). The cant angle ramps 0 ->
    # full at the arc over the entry spiral and full -> 0 over the exit spiral, mirroring how
    # start_radius_of_curvature/end_radius_of_curvature ramp over the same two spirals; its sign
    # follows which rail is raised, exactly as _map_viennese_bend derives cant_angle_start/end from
    # StartCantLeft/Right (raise_left_rail=True, i.e. a curve to the right, puts the raised rail on
    # the left, giving a negative angle by that formula).
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

    # deflection of the entry/exit spiral, taken from the family's own actual (dx, dy, dtheta)
    # rather than assumed to be entry_length / (2*R) -- that closed form is exact for CLOTHOID and
    # happens to also hold for the other curvature-integral families (Bloss, Cosine, Sine, Helmert
    # are all normalized to the same total deflection as clothoid for a given length and radius),
    # but CUBIC's Cartesian small-angle approximation doesn't hit it exactly, and using the real
    # dtheta keeps every family geometrically exact here regardless.
    entry_end = compute_spiral_end(family, entry_length, 0.0, R, entry_cant_factor) if 0.0 < entry_length else None
    exit_end = compute_spiral_end(family, exit_length, R, 0.0, exit_cant_factor) if 0.0 < exit_length else None
    theta1 = entry_end[2] if entry_end is not None else 0.0
    theta2 = exit_end[2] if exit_end is not None else 0.0
    theta_c = abs(delta) - theta1 - theta2  # deflection of the circular curve
    if theta_c < 0.0:
        raise ValueError(
            f"PI {pi_number}: spiral transition curves are too long; their combined deflection "
            "exceeds the PI deflection angle"
        )
    lc = R * theta_c

    # compose the displacement from the start of the entry spiral (TS) to the end of the exit
    # spiral (ST), in a frame with the x-axis along the back tangent. pieces are computed for a
    # curve to the left and mirrored by s.
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

    # locate TS on the back tangent and ST on the forward tangent so that the curve ends on the
    # forward tangent. this accounts for the inward shift of the circular curve.
    ts_to_pi = x - y / math.tan(delta)
    pi_to_st = y / math.sin(delta)

    return _SpiralCurveSolution(
        R=R,
        s=s,
        signed_radius=s * R,
        theta_c=theta_c,
        lc=lc,
        ts_to_pi=ts_to_pi,
        pi_to_st=pi_to_st,
        entry_end=entry_end,
        exit_end=exit_end,
        gravity_centerline_height=gravity_centerline_height,
    )


def curve_tangent_out(
    delta: float,
    radius: float,
    entry_length: float = 0.0,
    exit_length: float = 0.0,
    family: str = "CLOTHOID",
    vb_params: Optional[Sequence[float]] = None,
    pi_number: int = 0,
) -> float:
    """
    The tangent length a fully-specified curve claims on its forward (outgoing) side -- the
    "tangent_out" quantity a join_next junction's closure check compares against the next PI's own
    tangent_in claim (see solve_join_next_radius, which solves the inverse problem: given a target
    tangent_out/tangent_in, what radius produces it). Reuses the exact plain-circular formula or
    _solve_spiral_curve's pi_to_st the main solver loop itself uses, so this always agrees with
    what a real Apply would build for the same curve.

    :param delta: this curve's own PI deflection angle, radians (normalized internally)
    :param radius: radius magnitude
    :param entry_length: entry spiral length, 0.0 for none
    :param exit_length: exit spiral length, 0.0 for none
    :param family: spiral family (ignored when entry_length and exit_length are both 0.0)
    :param vb_params: VIENNESEBEND cant params (ignored otherwise)
    :param pi_number: 1-based PI number, used only in a "spirals too long" error message
    :return: tangent length from the PI to this curve's own forward tangent point (PT, or ST if it
        has an exit spiral)
    """
    delta = math.atan2(math.sin(delta), math.cos(delta))
    if entry_length <= 0.0 and exit_length <= 0.0:
        return abs(radius * math.tan(delta / 2.0))
    return _solve_spiral_curve(delta, radius, entry_length, exit_length, family, vb_params, pi_number).pi_to_st


def solve_join_next_radius(
    delta: float,
    target_tangent_in: float,
    exit_length: float = 0.0,
    family: str = "CLOTHOID",
    vb_params: Optional[Sequence[float]] = None,
    tolerance: float = 1.0e-9,
    max_iterations: int = 100,
) -> float:
    """
    Solves for the radius of the curve at the "joined-into" PI of a compound (PCC) / reverse (PRC)
    curve junction, given the tangent length it must claim on its joined (entry) side to close the
    junction -- see join_next in solve_horizontal_alignment_by_pi_method. The joined side is always
    spiral-free (a v1 limitation join_next already enforces), so the curve here is either plain
    CIRCULAR (exit_length == 0.0) or CIRCULAR_SPIRAL (exit_length > 0.0, an outer/non-joined exit
    spiral only).

    For CIRCULAR this has an exact closed form (tangent = R * tan(delta / 2)) and is solved
    directly. For CIRCULAR_SPIRAL, the exit spiral's own length still shifts how much of the PI's
    deflection is left for the circular arc, which in turn changes the entry-side (ts_to_pi) tangent
    claim even though the spiral itself sits on the far side -- there is no closed form for that, so
    this bisects against _solve_spiral_curve's own ts_to_pi, the exact same function
    solve_horizontal_alignment_by_pi_method's main loop uses to build the real segments. Tangent
    length is monotonically increasing in radius for a fixed deflection/spiral length, so a bracket
    search followed by bisection is guaranteed to converge whenever a solution exists.

    :param delta: PI deflection angle at the joined-into PI, radians (not yet normalized to
        (-pi, pi) -- this function normalizes it itself, matching the main solver)
    :param target_tangent_in: the tangent length this curve's joined (entry) side must claim to
        close the junction -- typically (pi_to_pi_distance - the joining curve's own tangent-out
        claim)
    :param exit_length: this curve's own exit spiral length (0.0 for plain CIRCULAR)
    :param family: spiral family for the exit spiral (ignored when exit_length is 0.0)
    :param vb_params: VIENNESEBEND cant params for the exit spiral (ignored otherwise)
    :param tolerance: relative closure tolerance to solve to; default is far tighter than
        _check_pi_join_closure's own 1e-4 (which absorbs float32 round-trip noise from the Bonsai
        UI), so a caller re-validating the result through the real solver comfortably passes
    :param max_iterations: bisection iteration cap, after the initial bracket search
    :return: the radius (unsigned magnitude) that closes the join
    :raises ValueError: if target_tangent_in is not positive, or no radius closes the join for this
        curve type/spiral length/deflection combination (a genuinely unsatisfiable geometry, not a
        root-finding failure)
    """
    return _solve_radius_for_tangent(
        delta, target_tangent_in, 0.0, exit_length, family, vb_params, tolerance, max_iterations
    )


def solve_joining_radius(
    delta: float,
    target_tangent_out: float,
    entry_length: float = 0.0,
    family: str = "CLOTHOID",
    vb_params: Optional[Sequence[float]] = None,
    tolerance: float = 1.0e-9,
    max_iterations: int = 100,
) -> float:
    """
    Solves for the radius of the *joining* curve of a compound (PCC) / reverse (PRC) curve junction
    (the PI with join_next=True), given the tangent length it must claim on its joined (forward)
    side -- i.e. the distance from its PI to the junction point along the PI-to-PI leg. The mirror
    image of solve_join_next_radius, which solves the joined-into curve from its entry-side claim.

    Together the two let a caller place a junction by distance instead of by radius: with the
    junction at distance T1 from the first PI, this solves the first curve's radius from T1, and
    solve_join_next_radius solves the second curve's radius from (PI-to-PI distance - T1).

    The joined side is always spiral-free, so the curve here is either plain CIRCULAR
    (entry_length == 0.0, exact closed form) or SPIRAL_CIRCULAR (entry_length > 0.0, an outer
    entry spiral only, solved by bisection against _solve_spiral_curve's own pi_to_st).

    :param delta: PI deflection angle at the joining PI, radians (normalized internally)
    :param target_tangent_out: the tangent length this curve's forward side must claim
    :param entry_length: this curve's own entry spiral length (0.0 for plain CIRCULAR)
    :param family: spiral family for the entry spiral (ignored when entry_length is 0.0)
    :param vb_params: VIENNESEBEND cant params for the entry spiral (ignored otherwise)
    :param tolerance: relative tolerance to solve to, see solve_join_next_radius
    :param max_iterations: bisection iteration cap, after the initial bracket search
    :return: the radius (unsigned magnitude) that claims exactly target_tangent_out
    :raises ValueError: if target_tangent_out is not positive, or no radius achieves it
    """
    return _solve_radius_for_tangent(
        delta, target_tangent_out, entry_length, 0.0, family, vb_params, tolerance, max_iterations
    )


def _solve_radius_for_tangent(
    delta: float,
    target_tangent: float,
    entry_length: float,
    exit_length: float,
    family: str,
    vb_params: Optional[Sequence[float]],
    tolerance: float,
    max_iterations: int,
) -> float:
    """Shared root-finder behind solve_join_next_radius (exit spiral only, solves the entry-side
    ts_to_pi claim) and solve_joining_radius (entry spiral only, solves the forward-side pi_to_st
    claim). Exactly one of entry_length/exit_length may be non-zero; the spiral always sits on the
    side opposite the tangent being solved for."""
    delta = math.atan2(math.sin(delta), math.cos(delta))
    if delta == 0.0:
        raise ValueError("cannot solve for a joining radius: the PI deflection angle is zero")
    if target_tangent <= 0.0:
        raise ValueError(
            f"cannot solve for a joining radius: the required tangent length ({target_tangent:.6g}) "
            "is not positive -- the two PIs are too close together, or the joining curve's own "
            "tangent claim already exceeds the PI-to-PI distance by itself"
        )

    spiral_length = entry_length if entry_length > 0.0 else exit_length
    if spiral_length <= 0.0:
        # exact closed form -- same expression the plain-circular branch of the main loop uses.
        denom = math.tan(delta / 2.0)
        if denom == 0.0:
            raise ValueError("cannot solve for a joining radius: the PI deflection angle is zero")
        return target_tangent / abs(denom)

    def tangent(R: float) -> float:
        solution = _solve_spiral_curve(delta, R, entry_length, exit_length, family, vb_params, pi_number=0)
        return solution.pi_to_st if entry_length > 0.0 else solution.ts_to_pi

    def residual(R: float) -> float:
        return tangent(R) - target_tangent

    # A fixed-length spiral's own deflection is proportional to curvature, i.e. to 1/R -- so a
    # SMALL radius is where the exit spiral alone can exceed the PI's whole deflection (invalid,
    # _solve_spiral_curve raises), and validity only improves as R grows: once a radius is valid,
    # every larger radius is valid too. So first find the smallest valid radius (the true lower
    # bound of the search, not an arbitrary small constant) by growing from a small starting point
    # until _solve_spiral_curve stops refusing, then bracket/bisect upward from there -- the
    # opposite direction from where a plain "shrink on failure" bracket search would look.
    r = 1.0
    valid_lo = None
    for _ in range(200):
        try:
            residual(r)
            valid_lo = r
            break
        except ValueError:
            r *= 2.0
    if valid_lo is None:
        raise ValueError(
            f"no radius closes this compound/reverse curve junction (required tangent length "
            f"{target_tangent:.6g}); the spiral's own length never fits within this PI's "
            "deflection angle at any radius tried"
        )

    lo = valid_lo
    f_lo = residual(lo)
    if 0.0 <= f_lo:
        # Even the smallest geometrically valid radius already claims at least the target tangent
        # length -- since tangent_in only grows from here, no valid radius claims less. Either this
        # smallest radius happens to close it near-exactly (accept it) or the junction is
        # unsatisfiable for this exit spiral length/deflection (report cleanly).
        if abs(f_lo) <= tolerance * target_tangent:
            return lo
        raise ValueError(
            f"no radius closes this compound/reverse curve junction (required tangent length "
            f"{target_tangent:.6g}); even the smallest radius at which this spiral length "
            "still fits within the PI's deflection already claims more tangent length than "
            "required -- use a shorter spiral, or increase the required tangent length"
        )

    hi = lo * 2.0
    f_hi = residual(hi)
    expand_iterations = 0
    while f_hi < 0.0 and expand_iterations < 80:
        hi *= 2.0
        f_hi = residual(hi)
        expand_iterations += 1
    if f_hi < 0.0:
        raise ValueError(
            f"no radius closes this compound/reverse curve junction (required tangent length "
            f"{target_tangent:.6g}); this curve type/spiral length combination cannot reach that "
            "tangent claim at any radius tried for this PI's deflection angle"
        )

    for _ in range(max_iterations):
        mid = 0.5 * (lo + hi)
        f_mid = residual(mid)
        if abs(f_mid) <= tolerance * target_tangent:
            return mid
        if f_mid < 0.0:
            lo, f_lo = mid, f_mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


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

        (R, Lin, Lout, family, cant_params, join_next) - as above, with an optional 6th field:
        when join_next is True, the curve at this PI connects directly to the curve at the NEXT PI
        at a shared tangency point, with no intermediate tangent run -- a PCC (point of compound
        curvature) when the two curves turn the same direction, a PRC (point of reverse curvature)
        when they turn opposite directions. The shared tangent line is the PI-to-PI leg itself (the
        two PIs' own straight-tangent positions, exactly as hpoints already defines them -- no
        separate input is needed to place the junction); each curve is solved against its own PI
        deflection as usual, and the solver additionally requires that the two curves' tangent
        lengths on the shared leg sum to exactly the PI-to-PI distance (within 1e-9 relative).
        Inputs that cannot close this way are refused with a ValueError stating the excess or
        shortfall and the two PIs involved. Spiral transitions are not supported on the joined side
        of a join_next curve (the exit spiral of the joining curve, and the entry spiral of the
        curve it joins into, must both be 0.0) -- spirals remain allowed on the outer, non-joined
        side of either curve. This is a documented v1 limitation: a true spiral-to-spiral transition
        at a PCC/PRC junction is not supported. join_next on the last radii element is refused (there
        is no next curve to join to).

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

    previous_join_next = False  # True when the previous PI's curve joins directly into this one (PCC/PRC)
    previous_tangent_out = 0.0  # that previous curve's tangent length claim on the shared leg

    for curve_index, curve in enumerate(radii):
        if isinstance(curve, (int, float)):
            radius = float(curve)
            entry_length = 0.0
            exit_length = 0.0
            family = "CLOTHOID"
            vb_params = None
            join_next = False
        else:
            if len(curve) not in (3, 4, 5, 6):
                raise ValueError(
                    "each radii element should be a radius R, a (R, Lin, Lout) sequence, a "
                    "(R, Lin, Lout, family) sequence, a (R, Lin, Lout, family, cant_params) sequence, or a "
                    "(R, Lin, Lout, family, cant_params, join_next) sequence"
                )
            radius, entry_length, exit_length = (float(v) for v in curve[:3])
            family = curve[3] if len(curve) >= 4 else "CLOTHOID"
            vb_params = curve[4] if len(curve) >= 5 else None
            join_next = bool(curve[5]) if len(curve) == 6 else False
            if family not in SPIRAL_FAMILIES:
                raise ValueError(f"unsupported spiral family '{family}'; expected one of {SPIRAL_FAMILIES}")
            if radius == 0.0 and (entry_length != 0.0 or exit_length != 0.0):
                raise ValueError("spiral transition lengths require a non-zero radius")

        pi_number = curve_index + 1  # 1-based PI number, matching this module's "PI n" labels elsewhere

        if join_next and radius == 0.0:
            raise ValueError(f"PI {pi_number} has join_next=True but radius is 0.0; there is no curve to join")
        if join_next and curve_index == len(radii) - 1:
            raise ValueError(
                f"PI {pi_number} has join_next=True but is the last PI curve; there is no next curve to join to"
            )
        if previous_join_next and entry_length != 0.0:
            raise ValueError(
                f"PI {pi_number - 1}-{pi_number} is a compound/reverse curve junction (join_next); spiral "
                f"transitions are not supported on the joined side of the curve at PI {pi_number} (its entry "
                "spiral length must be 0.0); use a spiral only on its outer, non-joined side"
            )
        if join_next and exit_length != 0.0:
            raise ValueError(
                f"PI {pi_number} has join_next=True; spiral transitions are not supported on the joined side "
                "of a compound/reverse curve junction (its exit spiral length must be 0.0); use a spiral only "
                "on its outer, non-joined side"
            )

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

        # true PI-to-PI distance for the leg shared with a join_next curve; distinct from lengthBT,
        # which is measured from the previous curve's end point rather than from the previous PI
        if previous_join_next:
            prev_pi_x, prev_pi_y = hpoints[curve_index]
            cur_pi_x, cur_pi_y = hpoints[curve_index + 1]
            pi_to_pi_distance = math.hypot(cur_pi_x - prev_pi_x, cur_pi_y - prev_pi_y)

        if entry_length == 0.0 and exit_length == 0.0:
            # tangent runs connect directly to the circular curve
            tangent = abs(radius * math.tan(delta / 2))
            tangent_out_this_curve = tangent  # symmetric: PI-to-PC equals PI-to-PT for a plain arc

            lc = abs(radius * delta)

            radius *= delta / abs(delta)

            xPC = xPI - tangent * math.cos(angleBT)
            yPC = yPI - tangent * math.sin(angleBT)

            xPT = xPI + tangent * math.cos(angleFT)
            yPT = yPI + tangent * math.sin(angleFT)

            tangent_run = lengthBT - tangent

            if previous_join_next:
                _check_pi_join_closure(previous_tangent_out, tangent, pi_to_pi_distance, pi_number)
            elif tangent_run < -1.0e-03:
                raise ValueError(
                    f"PI {curve_index + 1}: curve radius is too large for the distance between PIs; "
                    "use a smaller radius or move the PIs farther apart"
                )

            # back tangent run; suppressed at a validated join_next junction, which places this
            # curve's PC exactly at the previous curve's PT with no intermediate tangent run
            if 1.0e-03 < tangent_run and not previous_join_next:
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

            spiral_solution = _solve_spiral_curve(delta, radius, entry_length, exit_length, family, vb_params, pi_number)
            R = spiral_solution.R
            s = spiral_solution.s
            signed_radius = spiral_solution.signed_radius
            theta_c = spiral_solution.theta_c
            lc = spiral_solution.lc
            ts_to_pi = spiral_solution.ts_to_pi
            pi_to_st = spiral_solution.pi_to_st
            entry_end = spiral_solution.entry_end
            exit_end = spiral_solution.exit_end
            gravity_centerline_height = spiral_solution.gravity_centerline_height
            tangent_out_this_curve = pi_to_st

            tangent_run = lengthBT - ts_to_pi

            if previous_join_next:
                _check_pi_join_closure(previous_tangent_out, ts_to_pi, pi_to_pi_distance, pi_number)
            elif tangent_run < -1.0e-03:
                raise ValueError(
                    f"PI {curve_index + 1}: spiral transition curves are too long for the distance between PIs; "
                    "use shorter spirals/a smaller radius or move the PIs farther apart"
                )

            # back tangent run; suppressed at a validated join_next junction, which places this
            # curve's TS/PC exactly at the previous curve's PT with no intermediate tangent run
            if 1.0e-03 < tangent_run and not previous_join_next:
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

        previous_join_next = join_next
        previous_tangent_out = tangent_out_this_curve

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
