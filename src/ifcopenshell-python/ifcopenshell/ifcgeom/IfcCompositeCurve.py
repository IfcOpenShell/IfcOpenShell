from dataclasses import dataclass
from typing import List

import numpy as np
from OCC.Core.TopTools import TopTools_ListOfShape

from ..alignment_enums import TransitionCode


@dataclass
class Segment:
    """
    IfcSegment

    Ref: 8.9.3.62
    https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcSegment.htm
    """

    Transition: TransitionCode


@dataclass
class CompositeCurve:
    """
    IfcCompositeCurve

    Defines the representation of an alignment with IfcHorizontal only

    Ref: 8.9.3.20
    https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcCompositeCurve.htm
    """

    Segments: List[Segment]
    SelfIntersect: bool

    def create_shape(self) -> np.ndarray:
        raise NotImplementedError


class CompositeCurveShadowCpp:
    """
    A re-implementation of `IfcCompositeCurve.cpp` from C++ namespace `ifcgeom`

    @param entity: the IFC entity
    """

    def __init__(self, entity):
        self._entity = entity

    def convert(self) -> bool:
        """
        @param l: The entity to process
        @type l: IfcCompositeCurve
        """

        # skip radians vs. degrees...

        l = self._entity
        segments = l.Segments
        converted_segments = TopTools_ListOfShape()

        for it in segments:
            curve = it.ParentCurve

            if curve.is_a("IfcLine"):
                pass
