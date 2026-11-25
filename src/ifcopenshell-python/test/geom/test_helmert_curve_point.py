"""helmert_curve_point, which _map_helmert_curve uses to place the second half of a helmert curve.

The heading it returns must be the polynomial spiral's theta at arc length s, or the second half is
placed at an angle to the end of the first and the curve has a kink at its midpoint.
"""

import math

import pytest

from ifcopenshell import ifcopenshell_wrapper


def theta(a0, a1, a2, t):
    """IfcSecondOrderPolynomialSpiral's heading at arc length t, the integral of its curvature"""
    return (t / a0 if a0 else 0.0) + (a1 * t**2 / (2 * abs(a1**3)) if a1 else 0.0) + (t**3 / (3 * a2**3) if a2 else 0.0)


# the first half of 100 long helmert curves: straight to R300, R300 to straight, R300 to R1000
TERMS = [(0.0, 0.0, 114.47142425533319), (300.0, 0.0, -114.47142425533319), (300.0, 0.0, -128.9231989389298)]


@pytest.mark.parametrize("a0,a1,a2", TERMS)
def test_heading_is_theta_at_s(a0, a1, a2):
    s = 50.0
    assert ifcopenshell_wrapper.helmert_curve_point(a0, a1, a2, s)[2] == pytest.approx(theta(a0, a1, a2, s), abs=1e-12)


@pytest.mark.parametrize("a0,a1,a2", TERMS)
def test_position_is_the_integral_of_the_heading(a0, a1, a2):
    s = 50.0
    n = 2000  # composite Simpson's rule
    h = s / n
    weights = [1 if i in (0, n) else 4 if i % 2 else 2 for i in range(n + 1)]
    x = h / 3 * sum(w * math.cos(theta(a0, a1, a2, i * h)) for i, w in enumerate(weights))
    y = h / 3 * sum(w * math.sin(theta(a0, a1, a2, i * h)) for i, w in enumerate(weights))
    point = ifcopenshell_wrapper.helmert_curve_point(a0, a1, a2, s)
    assert point[0] == pytest.approx(x, abs=1e-9)
    assert point[1] == pytest.approx(y, abs=1e-9)
