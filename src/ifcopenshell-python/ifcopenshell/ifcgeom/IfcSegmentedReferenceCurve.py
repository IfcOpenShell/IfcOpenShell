from dataclasses import dataclass

import numpy as np

from ..alignment import BoundedCurve
from .IfcCompositeCurve import CompositeCurve


@dataclass
class SegmentedReferenceCurve(CompositeCurve):
    """
    IfcSegmentedReferenceCurve

    Ref: 8.9.3.63
    https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcSegmentedReferenceCurve.htm
    """

    BaseCurve: BoundedCurve
    EndPoint: np.ndarray = None

    def create_shape(self) -> np.ndarray:
        raise NotImplementedError
