from dataclasses import dataclass
from typing import List

import ifcopenshell
import numpy as np

from ..alignment import AlignmentParameterSegment
from ..alignment import LinearElement
from ..alignment_enums import AlignmentCantSide


def c_on_CONSTANTCANT(segment, u: float, side: AlignmentCantSide):
    if side == AlignmentCantSide.LEFT:
        return segment.StartCantLeft
    elif side == AlignmentCantSide.RIGHT:
        return segment.StartCantRight
    else:
        msg = "Cannot determine which side to calculate cant."
        raise ValueError(msg)


def c_on_LINEARTRANSITION(segment, u: float, side: AlignmentCantSide):
    if side == AlignmentCantSide.LEFT:
        start = segment.StartCantLeft
        end = segment.EndCantLeft
    elif side == AlignmentCantSide.RIGHT:
        start = segment.StartCantRight
        end = segment.EndCantRight
    else:
        msg = "Cannot determine which side to calculate cant."
        raise ValueError(msg)

    slope = (end - start) / segment.HorizontalLength
    return (slope * u) + start


def c_on_COSINECURVE(
    segment,
    u: float,
):
    raise NotImplementedError("Cant calculation on COSINECURVE not implemented yet.")


def c_on_HELMERTCURVE(
    segment,
    u: float,
):
    raise NotImplementedError("Cant calculation on HELMERTCURVE not implemented yet.")


def c_on_SINECURVE(
    segment,
    d: float,
):
    raise NotImplementedError("Cant calculation on SINECURVE not implemented yet.")


def c_on_VIENNESEBEND(
    segment,
    d: float,
):
    raise NotImplementedError("Cant calculation on VIENNESEBEND not implemented yet.")


@dataclass
class AlignmentCantSegment(AlignmentParameterSegment):
    """
    IfcAlignmentCantSegment

    8.7.3.1
    https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcAlignmentCantSegment.htm
    """

    StartDistAlong: float
    HorizontalLength: float
    StartCantLeft: float
    EndCantLeft: float
    StartCantRight: float
    EndCantRight: float
    PredefinedType: str

    @property
    def end_distance(self):
        """
        Distance along the alignment at the end of this segment
        """
        return self.StartDistAlong + self.HorizontalLength

    def c_at_distance(self, d: float):
        """
        amount of cant at distance d along an IfcAlignment (entire alignment)

        @param segment: IfcAlignmentCantSegment containing the location
        @type segment: ifcopenshell.alignment.AlignmentCantSegment
        """
        side = AlignmentCantSide.LEFT
        u = d - self.StartDistAlong

        if self.PredefinedType == "CONSTANTCANT":
            return c_on_CONSTANTCANT(self, u, side)
        elif self.PredefinedType == "LINEARTRANSITION":
            return c_on_LINEARTRANSITION(self, u, side)
        elif self.PredefinedType == "COSINECURVE":
            return c_on_COSINECURVE(self, u, side)
        elif self.PredefinedType == "HELMERTCURVE":
            return c_on_HELMERTCURVE(self, u, side)
        elif self.PredefinedType == "SINECURVE":
            return c_on_SINECURVE(self, u, side)
        elif self.PredefinedType == "VIENNESEBEND":
            return c_on_VIENNESEBEND(self, u, side)


class AlignmentCant(LinearElement):
    """
    IfcAlignmentCant

    5.4.3.2
    https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcAlignmentCant.htm
    """

    def __init__(self, RailHeadDistance: float = None):
        super().__init__()
        self._segments = list()
        if RailHeadDistance is None:
            self._rail_head_distance = 0.0
        else:
            self._rail_head_distance = RailHeadDistance

    def from_entity(self, elem: ifcopenshell.entity_instance):
        self._elem = elem
        self._length = 0
        self._rail_head_distance = elem.RailHeadDistance

        for rel in elem.IsNestedBy:
            for child in rel.RelatedObjects:
                dp = child.DesignParameters
                if not dp.is_a("IfcAlignmentCantSegment"):
                    msg = f"""Alignment segment is a {dp.is_a()}. \n 
                        IfcAlignmentCant can only be nested by IfcAlignmentCantSegment entities.
                        """
                    raise ValueError(msg)

                cs = AlignmentCantSegment(
                    StartDistAlong=dp.StartDistAlong,
                    HorizontalLength=dp.HorizontalLength,
                    StartCantLeft=dp.StartCantLeft,
                    EndCantLeft=dp.EndCantLeft,
                    StartCantRight=dp.StartCantRight,
                    EndCantRight=dp.EndCantRight,
                    PredefinedType=dp.PredefinedType,
                )
                self._segments.append(cs)

        return self

    @property
    def segments(self) -> List[AlignmentCantSegment]:
        return self._segments

    @property
    def RailHeadDistance(self) -> float:
        return self._rail_head_distance

    def calc_cant_amounts(self, d: np.ndarray) -> np.ndarray:
        """
        Calculate amount of cant at each location specified by the
        distances array supplied by the alignment that contains this cant alignment.

        @param d: Array of distances along the horizontal alignment at which to calculate values.
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
        functions.append(s0.c_at_distance)

        for seg in segs[1:]:
            lower = seg.StartDistAlong
            upper = seg.end_distance
            # other segments will be inclusive of upper bound only
            conditions.append((d > lower) & (d <= upper))
            functions.append(seg.c_at_distance)

        # append another function to serve as default where the conditions are not met
        # this would apply in the instance where a vertical alignment does not cover the entire
        # limit of the associated horizontal alignment
        functions.append(np.nan)

        heights = np.piecewise(
            x=d,
            condlist=conditions,
            funclist=functions,
        )

        return heights
