from dataclasses import dataclass
from typing import List

import numpy as np

from ..alignment import BoundedCurve
from .IfcCompositeCurve import CompositeCurve


@dataclass
class GradientCurve(CompositeCurve):
    """
    IfcGradientCurve

    Defines the representation of an alignment containing both IfcHorizontal and IfcVertical

    Ref: 8.9.3.35
    https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcGradientCurve.htm
    """

    BaseCurve: BoundedCurve
    EndPoint: np.ndarray = None

    def create_shape(self) -> np.ndarray:
        raise NotImplementedError
