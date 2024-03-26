from dataclasses import dataclass
from enum import Enum
import math
from typing import List

import ifcopenshell
import numpy as np

from ..alignment import AlignmentParameterSegment
from ..alignment import LinearElement
from ..alignment_enums import VerticalCurveDirection
from ..alignment_enums import AlignmentVerticalSegmentType
from .config import GEOM_TOLERANCE


class VerticalCurve:
    """
    Common Parameters of vertical curves

    @param segment: Alignment segment to be calculated
    @type segment: AlignmentVerticalSegment
    """

    def __init__(self, segment):
        self._pvc_station = segment.StartDistAlong
        self._length = segment.HorizontalLength
        self._pvc_elevation = segment.StartHeight
        self._g1 = segment.StartGradient
        self._g2 = segment.EndGradient
        self._R = segment.RadiusOfCurvature

        if abs(self._g2 - self._g1) < GEOM_TOLERANCE:
            msg = "Invalid definition of a vertical curve.  Entrance and exit gradients are the same."
            raise ValueError(msg)

        if self._g2 > self._g1:
            self._direction = VerticalCurveDirection.SAG
        else:
            self._direction = VerticalCurveDirection.CREST

        self._pvi_station = self._pvc_station + 0.5 * self._length
        self._pvi_elevation = self._pvc_elevation + 0.5 * self._length * self._g1
        self._pvt_station = self._pvi_station + 0.5 * self._length
        self._pvt_elevation = self._pvi_elevation + 0.5 * self._length * self._g2

    @property
    def PVC(self) -> tuple:
        """
        The distance and elevation of the point of vertical curvature
        (beginning of the curve)
        """
        return (self._pvc_station, self._pvc_elevation)

    @property
    def PVI(self) -> tuple:
        """
        The distance and elevation of the point of vertical intersection
        """
        return (self._pvi_station, self._pvi_elevation)

    @property
    def PVT(self) -> tuple:
        """
        The distance and elevation of the point of vertical tangency
        (end of the curve)
        """
        return (self._pvt_station, self._pvt_elevation)


class CircularArc(VerticalCurve):
    """
    A circular vertical curve.

    Ref: Exact Solution of Circular Vertical Curves
    Coskun, M. Zeki and Baykal, O.
    https://web.itu.edu.tr/tari/engsurv/vertical-curves.pdf
    Retrieved 2023-07-01

    @param segment: Alignment segment to be calculated
    @type segment: AlignmentVerticalSegment
    """

    def __init__(self, segment):
        super().__init__(segment)

        # extreme point (high / low)
        self._Xt = (
            self._direction.value * (-self._g1 * self._R) / math.sqrt(1 + self._g1**2)
        )
        self._Zt = self.z_at_distance(self._Xt)

    def z_at_distance(self, u: float) -> float:
        """
        The elevation on the curve at a given distance along the curve (from PVC).
        """
        dir_factor = self._direction.value

        # coordinates of circle center
        xm = dir_factor * (-self._g1 * self._R) / math.sqrt(1 + (self._g1) ** 2)
        ym = self._R / math.sqrt(1 + (self._g1) ** 2)

        num = self._g1 * self._R
        denom = (1 + self._g1**2) ** 0.5
        z_term3 = self._R / denom
        r2 = self._R**2

        if self._direction == VerticalCurveDirection.SAG:
            z_term2 = (u + (num / denom)) ** 2
            z = -1 * (r2 - z_term2) ** 0.5 + z_term3

        elif self._direction == VerticalCurveDirection.CREST:
            z_term2 = (u - (num / denom)) ** 2
            z = (r2 - z_term2) ** 0.5 - z_term3

        else:
            msg = f"Unable to determine direction of vertical curve with gradients {self._g1:6f} and {self._g1:6f}."
            raise ValueError(msg)

        return self._pvc_elevation + z

    @property
    def extreme_point(self) -> tuple:
        """
        The distance and elevation of the extreme (high or low) point on the curve
        """
        station = self._pvc_station + self.Xt
        elevation = self.Zt
        return (station, elevation)


class ParabolicArc(VerticalCurve):
    """
    A parabolic vertical curve.

    Ref: Indiana Department of Transportation (INDOT) Design Manual 2013
    Figure 44-3F
    Retrieved 2023-06-25
    https://www.in.gov/dot/div/contracts/design/Part%203/Chapter%2044%20-%20Vertical%20Alignment.pdf

    @param segment: Alignment segment to be calculated
    @type segment: AlignmentVerticalSegment
    """

    def __init__(self, segment):
        super().__init__(segment)
        expected = str(AlignmentVerticalSegmentType.PARABOLICARC.value)

        # setup for variable names to match
        self.L = self._length

        # use slopes in percent
        self.G1 = 100 * self._g1
        self.G2 = 100 * self._g2

        # calculate high / low point
        self.Xt = (self.L * self.G1) / (self.G1 - self.G2)
        self.Zt = self.z_at_distance(self.Xt)

    def z_at_distance(self, u: float) -> float:
        """
        The elevation on the curve at a given distance along the curve (from PVC).
        Ref: https://en.wikibooks.org/wiki/Fundamentals_of_Transportation/Vertical_Curves
        """
        return (
            self._pvc_elevation
            + self._g1 * u
            + (((self._g2 - self._g1) * u**2) / (2 * self._length))
        )

    @property
    def extreme_point(self) -> tuple:
        """
        The distance and elevation of the extreme (high or low) point on the curve
        """
        station = self._pvc_station + self.Xt
        elevation = self.Zt
        return (station, elevation)


def h_on_CONSTANTGRADIENT(
    segment,
    u: float,
):
    return segment.StartHeight + u * segment.StartGradient


def h_on_CIRCULARARC(
    segment,
    u: float,
):
    ca = CircularArc(segment)
    return ca.z_at_distance(u)


def h_on_PARABOLICARC(
    segment,
    u: float,
):
    pa = ParabolicArc(segment)
    return pa.z_at_distance(u)


def h_on_CLOTHOID(
    segment,
    d: float,
):
    raise NotImplementedError(
        "Vertical height calculation on CLOTHOID not implemented yet."
    )


@dataclass
class AlignmentVerticalSegment(AlignmentParameterSegment):
    """
    IfcAlignmentVerticalSegment

    8.7.3.4
    https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcAlignmentVerticalSegment.htm
    """

    StartDistAlong: float
    HorizontalLength: float
    StartHeight: float
    StartGradient: float
    EndGradient: float
    PredefinedType: str
    RadiusOfCurvature: float = None

    @property
    def end_distance(self):
        """
        Distance along the alignment at the end of this segment
        """
        return self.StartDistAlong + self.HorizontalLength

    def h_at_distance(self, d: float) -> float:
        """
        height on an alignment vertical segment
        at distance d along an IfcAlignment (entire alignment)

        @param segment: IfcAlignmentVerticalSegment containing the location
        @type segment: ifcopenshell.alignment.AlignmentVerticalSegment
        """
        u = d - self.StartDistAlong
        """
        if u < 0:
            msg = f"Calculated distance along {self.PredefinedType} is {u}, which cannot be negative."
            # raise ValueError(msg)
            print(msg)
        """

        if self.PredefinedType == "CONSTANTGRADIENT":
            return h_on_CONSTANTGRADIENT(self, u)
        elif self.PredefinedType == "PARABOLICARC":
            return h_on_PARABOLICARC(self, u)
        elif self.PredefinedType == "CIRCULARARC":
            return h_on_CIRCULARARC(self, u)
        elif self.PredefinedType == "CLOTHOID":
            return h_on_CLOTHOID(self, u)


class AlignmentVertical(LinearElement):
    """
    IfcAlignmentVertical

    5.4.3.5
    https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcAlignmentVertical.htm
    """

    def __init__(self):
        super().__init__()
        self._segments = list()
        self._end_distance = 0.0

    def from_entity(self, elem: ifcopenshell.entity_instance):
        self._elem = elem
        for rel in elem.IsNestedBy:
            for child in rel.RelatedObjects:
                dp = child.DesignParameters
                if not dp.is_a("IfcAlignmentVerticalSegment"):
                    msg = f"""Alignment segment is a {dp.is_a()}. \n 
                        IfcAlignmentVertical can only be nested by IfcAlignmentVerticalSegment entities.
                        """
                    raise ValueError(msg)

                vs = AlignmentVerticalSegment(
                    StartDistAlong=dp.StartDistAlong,
                    HorizontalLength=dp.HorizontalLength,
                    StartHeight=dp.StartHeight,
                    StartGradient=dp.StartGradient,
                    EndGradient=dp.EndGradient,
                    PredefinedType=dp.PredefinedType,
                    RadiusOfCurvature=dp.RadiusOfCurvature,
                )
                # set end distance of this segment based on
                # how far we have traversed along the alignment
                self._end_distance = vs.StartDistAlong + vs.HorizontalLength
                self._segments.append(vs)

        return self

    @property
    def end_distance(self) -> float:
        return self._end_distance

    @property
    def segments(self) -> List[AlignmentVerticalSegment]:
        return self._segments

    def calc_heights(self, d: np.ndarray) -> np.ndarray:
        """
        Calculate heights (elevations) at each location specified by the
        distances array supplied by the alignment that contains this vertical

        @param d: Array of distances along the horizontal alignment at which to calculate values
        """
        conditions = list()
        functions = list()

        # conditions will be based on upper and lower bounds of each segment
        # the first segment will be inclusive of the lower and upper bound
        segs = self._segments

        s0 = segs[0]
        lower = s0.StartDistAlong
        upper = s0.end_distance
        conditions.append((d >= lower) & (d <= upper))
        functions.append(s0.h_at_distance)

        for seg in segs[1:]:
            lower = seg.StartDistAlong
            upper = seg.end_distance
            # other segments will be inclusive of upper bound only
            conditions.append((d > lower) & (d <= upper))
            functions.append(seg.h_at_distance)

        # append another function to serve as default where the conditions are not met
        # this would apply in the instance where a cant alignment does not cover the entire
        # limit of the associated horizontal alignment
        functions.append(np.nan)

        heights = np.piecewise(
            x=d,
            condlist=conditions,
            funclist=functions,
        )

        return heights
