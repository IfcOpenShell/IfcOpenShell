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


from dataclasses import dataclass
from enum import Enum
import os
import pathlib
from typing import List

import numpy as np

import ifcopenshell.geom
import ifcopenshell.express
from ifcopenshell.transition_curve import point_on_LINE
from ifcopenshell.transition_curve import point_on_CIRCULARARC
from ifcopenshell.transition_curve import point_on_BLOSSCURVE
from ifcopenshell.transition_curve import point_on_CLOTHOID
from ifcopenshell.transition_curve import point_on_COSINECURVE

"""
Test cases are loaded from https://github.com/bSI-RailwayRoom/IFC-Rail-Sample-Files
"""


def print_structure(alignment, indent=0):
    """
    Debugging function to print alignment decomposition
    """
    print(" " * indent, str(alignment)[0:100])
    for rel in alignment.IsNestedBy:
        for child in rel.RelatedObjects:
            print_structure(child, indent + 2)


class TransitionCode(Enum):
    CONTINUOUS = "CONTINUOUS"
    CONTSAMEGRADIENT = "CONTSAMEGRADIENT"
    CONTSAMEGRADIENTSAMECURVATURE = "CONTSAMEGRADIENTSAMECURVATURE"
    DISCONTINUOUS = "DISCONTINUOUS"


class Root:
    """
    IfcRoot

    Ref: 5.4.3.443
    https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcRoot.htm
    """

    def __init__(self):
        self._elem = None

    def from_entity(self, elem: ifcopenshell.entity_instance):
        self._elem = elem

    @property
    def wrapped_entity(self):
        return self._elem

    @property
    def GlobalId(self):
        return self._elem.GlobalId

    @property
    def OwnerHistory(self):
        return self._elem.OwnerHistory

    @property
    def Name(self):
        return self._elem.Name

    @property
    def Description(self):
        return self._elem.Description

    def print_attributes(self):
        print(f"{self.wrapped_entity=}")
        print("-----------------------------------------")
        print(f"{self.OwnerHistory=}")
        print(f"{self.OwnerHistory.CreationDate=}")
        print(f"{self.OwnerHistory.State=}")
        print(f"{self.GlobalId=}")
        print(f"{self.Name=}")
        print(f"{self.Description=}")


class ObjectDefinition(Root):
    """
    IfcObjectDefintion

    5.1.3.7
    https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcObjectDefinition.htm
    """

    def __init__(self):
        super().__init__()

    @property
    def HasAssignments(self):
        return self._elem.HasAssignments

    @property
    def Nests(self):
        return self._elem.Nests

    @property
    def IsNestedBy(self):
        return self._elem.IsNestedBy

    @property
    def HasContext(self):
        return self._elem.HasContext

    @property
    def IsDecomposedBy(self):
        return self._elem.IsDecomposedBy

    @property
    def Decomposes(self):
        return self._elem.Decomposes

    @property
    def HasAssociations(self):
        return self._elem.HasAssociations

    def print_attributes(self):
        super().print_attributes()
        print("-----------------------------------------")
        print(f"{self.HasAssignments=}")
        print(f"{self.Nests=}")
        print(f"{self.IsNestedBy=}")
        print(f"{self.HasContext=}")
        print(f"{self.IsDecomposedBy=}")
        print(f"{self.Decomposes=}")
        print(f"{self.HasAssociations=}")


class Object(ObjectDefinition):
    """
    IfcObjectDefinition

    5.1.3.6
    https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcObject.htm
    """

    def __init__(self):
        super().__init__()

    @property
    def ObjectType(self):
        return self._elem.ObjectType

    @property
    def IsDeclaredBy(self):
        return self._elem.IsDeclaredBy

    @property
    def Declares(self):
        return self._elem.Declares

    @property
    def IsTypedBy(self):
        return self._elem.IsTypedBy

    @property
    def IsDefinedBy(self):
        return self._elem.IsDefinedBy

    def print_attributes(self):
        super().print_attributes()
        print("-----------------------------------------")
        print(f"{self.ObjectType=}")
        print(f"{self.IsDeclaredBy=}")
        print(f"{self.Declares=}")
        print(f"{self.IsTypedBy=}")
        print(f"{self.IsDefinedBy=}")


class Product(Object):
    """
    IfcProduct

    5.1.3.10
    https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcProduct.htm
    """

    def __init__(self):
        super().__init__()

    @property
    def ObjectPlacement(self):
        return self._elem.ObjectPlacement

    @property
    def Representation(self):
        return self._elem.Representation

    @property
    def ReferencedBy(self):
        return self._elem.ReferencedBy

    @property
    def PositionedRelativeTo(self):
        return self._elem.PositionedRelativeTo

    @property
    def ReferencedInStructures(self):
        return self._elem.ReferencedInStructures

    def print_attributes(self):
        super().print_attributes()
        print("-----------------------------------------")
        print(f"{self.ObjectPlacement=}")
        print(f"{self.Representation=}")
        print(f"{self.ReferencedBy=}")
        print(f"{self.PositionedRelativeTo=}")
        print(f"{self.ReferencedInStructures=}")


class PositioningElement(Product):
    """
    IfcPositioningElement

    5.4.3.42
    https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcPositioningElement.htm
    """

    def __init__(self):
        super().__init__()

    @property
    def ContainedInStructure(self):
        return self._elem.ContainedInStructure

    @property
    def Positions(self):
        return self._elem.Positions

    def print_attributes(self):
        super().print_attributes()
        print("-----------------------------------------")
        print(f"{self.ContainedInStructure=}")
        print(f"{self.Positions=}")


class LinearElement(Product):
    """
    IfcLinearElement

    5.4.3.38
    https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcLinearElement.htm
    """

    def __init__(self):
        super().__init__()


@dataclass
class Segment:
    """
    IfcSegment

    Ref: 8.9.3.62
    https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcSegment.htm
    """

    Transition: TransitionCode


@dataclass
class AlignmentHorizontalSegmentTypeEnum(Enum):
    """
    IfcAlignmentHorizontalSegmentTypeEnum

    8.7.2.2
    https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcAlignmentHorizontalSegmentTypeEnum.htm
    """

    BLOSSCURVE = "BLOSSCURVE"
    CIRCULARARC = "CIRCULARARC"
    CLOTHOID = "CLOTHOID"
    COSINECURVE = "COSINECURVE"
    CUBIC = "CUBIC"
    HELMERTCURVE = "HELMERTCURVE"  # also referred to as Schramm curve.
    LINE = "LINE"
    SINECURVE = "SINECURVE"  # also referred to as Klein curve
    VIENNESEBEND = "VIENNESEBEND"


class AlignmentParameterSegment:
    """
    IfcAlignmentParameterSegment

    8.7.3.3
    https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcAlignmentParameterSegment.htm
    """

    StartTag: str = None
    EndTag: str = None


@dataclass
class AlignmentSegment(Product):
    """
    IfcAlignmentSegment

    5.4.3.4
    https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcAlignmentSegment.htm
    """

    DesignParameters: AlignmentParameterSegment


@dataclass
class AlignmentHorizontalSegment(AlignmentParameterSegment):
    """
    IfcAlignmentHorizontalSegment

    8.7.3.2
    https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcAlignmentHorizontalSegment.htm

    @param start_distance: Distance along the alignment at the start of this segment
    """

    StartPoint: np.ndarray
    StartDirection: float
    StartRadiusOfCurvature: float
    EndRadiusOfCurvature: float
    SegmentLength: float
    PredefinedType: AlignmentHorizontalSegmentTypeEnum
    GravityCenterLineHeight: float = None
    start_distance: float = 0

    @property
    def end_distance(self):
        """
        Distance along the alignment at the end of this segment
        """
        return self.start_distance + self.SegmentLength

    @property
    def is_CCW(self) -> bool:
        """
        Whether or not this segment deflects counter clockwise
        """
        if self.PredefinedType.name == "CIRCULARARC":
            if self.StartRadiusOfCurvature >= 0:
                return True
            else:
                return False
        elif self.PredefinedType.name == "CLOTHOID":
            if abs(self.StartRadiusOfCurvature) < abs(self.EndRadiusOfCurvature):
                if self.EndRadiusOfCurvature > 0:
                    return True
                else:
                    return False
            else:
                if self.StartRadiusOfCurvature > 0:
                    return True
                else:
                    return False

    def calc_point(self, u: float) -> np.ndarray:
        """
        Calculate an x, y point at distance u along this segment
        """
        if u < 0:
            msg = f"Invalid distance '{u}' along segment. Distance must be positive."
            raise ValueError(msg)

        if u > self.SegmentLength:
            msg = f"Invalid distance '{u}' along segment. Distance must be <= total length '{self.SegmentLength}'."
            raise ValueError(msg)

        # lookup the appropriate function for point calculation
        segment_pt = globals()[f"point_on_{self.PredefinedType.value}"](self, u)
        return self.StartPoint + segment_pt


@dataclass
class AlignmentPoint:
    """
    Not sure if this will be useful.
    Might serve as syntatic sugar over the numpy array

    Reference: https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcSegmentedReferenceCurve.htm#Figure-8.9.3.63.A-use-of-a-segmented-reference-curve-on-a-cant-segment-based-on-a-gradient-curve
    """

    x: float
    y: float
    z: float  # elevation of base curve (IfcGradientCurve)
    station: float  # distance along alignment
    bearing: float  # horizontal bearing as angle CCW from positive x-axis in radians
    grade: float  # vertical slope as unitless rise over run
    radius: float  # radius at this point (inverse of curvature)
    cant: float  # height distance between rails
    z_reference: float  # elevation of reference curve (IfcSegmentedReferenceCurve) calculated as z + cant


class AlignmentHorizontal(LinearElement):
    """
    IfcAlignmentHorizontal

    5.4.3.3
    https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcAlignmentHorizontal.htm
    """

    def __init__(self):
        super().__init__()
        self._segments = list()

    def from_entity(self, elem: ifcopenshell.entity_instance):
        self._elem = elem
        self._length = 0
        for rel in elem.IsNestedBy:
            for child in rel.RelatedObjects:
                dp = child.DesignParameters
                if not dp.is_a("IfcAlignmentHorizontalSegment"):
                    msg = f"""Alignment segment is a {dp.is_a()}. \n 
                        IfcHorizontal can only be nested by IfcAlignmentHorizontalSegment entities.
                        """
                    raise ValueError(msg)
                x, y = dp.StartPoint.Coordinates

                hs = AlignmentHorizontalSegment(
                    StartPoint=np.array([x, y, np.nan], dtype=np.float64),
                    StartDirection=dp.StartDirection,
                    StartRadiusOfCurvature=dp.StartRadiusOfCurvature,
                    EndRadiusOfCurvature=dp.EndRadiusOfCurvature,
                    SegmentLength=dp.SegmentLength,
                    PredefinedType=AlignmentHorizontalSegmentTypeEnum(
                        dp.PredefinedType,
                    ),
                    GravityCenterLineHeight=dp.GravityCenterLineHeight,
                )
                # set start and end distances of this segment based on
                # how far we have traversed along the alignment
                hs.start_distance = self._length
                self._length += hs.SegmentLength
                self._segments.append(hs)

        return self

    @property
    def segments(self) -> List[AlignmentHorizontalSegment]:
        return self._segments

    @property
    def length(self) -> float:
        return self._length


class AlignmentVertical(LinearElement):
    """
    IfcAlignmentVertical

    5.4.3.5
    https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcAlignmentVertical.htm
    """

    def __init__(self):
        super().__init__()
        self._segments = list()

    def from_entity(self, elem: ifcopenshell.entity_instance):
        self._elem = elem
        for rel in elem.IsNestedBy:
            for child in rel.RelatedObjects:
                dp = child.DesignParameters
                if not dp.is_a("IfcAlignmentVerticalSegment"):
                    msg = f"""Alignment segment is a {dp.is_a()}. \n 
                        IfcVertical can only be nested by IfcAlignmentVerticalSegment entities.
                        """
                    raise ValueError(msg)


class Alignment(PositioningElement):
    """
    IfcAlignment

    Ref: 5.4.3.1
    https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcAlignment.htm
    """

    def __init__(self):
        super().__init__()
        self._horizontal = None
        self._vertical = None
        self._cant = None

    @property
    def PredefinedType(self):
        return self._elem.PredefinedType

    @property
    def horizontal(self) -> AlignmentHorizontal:
        return self._horizontal

    @property
    def vertical(self) -> AlignmentVertical:
        return self._vertical

    """
    @property
    def cant(self) -> AlignmentCant:
        return self._cant
    """

    def from_entity(self, elem: ifcopenshell.entity_instance):
        self._elem = elem

        # extract horizontal, vertical, and cant if they exist
        for rel in self.IsNestedBy:
            for child in rel.RelatedObjects:
                if child.is_a("IfcAlignmentHorizontal"):
                    self._horizontal = AlignmentHorizontal().from_entity(child)

                # TODO
                """
                elif child.is_a("IfcAlignmentVertical"):
                    self._vertical = AlignmentVertical().from_entity(child)
                elif child.is_a("IfcAlignmentCant"):
                    self._vertical = AlignmentCant().from_entity(child)
                """
        return self

    @property
    def length(self) -> float:
        """
        Total length of the alignment.
        """
        return self._horizontal.length

    def _calc_points(self, interval: float = 5.0):
        """
        Calculate all of the points on the alignment at a specific distance (interval)
        between points
        """
        pts = list()
        segs = self._horizontal.segments
        distances = np.arange(0, self.length, interval)
        # TODO: add ends of each segment to the array of distances

        idx = 0  # index of the segments
        for d in distances:
            if d >= segs[idx].end_distance:
                idx += 1
            pts.append(segs[idx].calc_point(u=(d - segs[idx].start_distance)))

        self._points = np.array(pts)

    def create_shape(
        self,
        settings: ifcopenshell.geom.settings = ifcopenshell.geom.settings(),
        use_representation: bool = True,
        point_interval: float = 5.0,
    ) -> np.ndarray:
        """
        There are two approaches to modeling IfcAlignment entities: business aspects and representation with
        IFC geometry resources.
        If a representation exists, it may be utilized.  Otherwise it will be calculated from the parameters
        of each individual segment.

        @param use_representation: Use the geometry from the IFC geometry entities, if it exists
        @param point_interval: The distance between points that will be calculated along the alignment.
        """
        if use_representation:
            try:
                if len(self.Representation) > 0:
                    return ifcopenshell.geom.create_shape(settings, self.wrapped_entity)
            except RuntimeError:
                msg = ifcopenshell.get_log()
                raise RuntimeError(msg)
            except TypeError:
                msg = (
                    f"{str(self.wrapped_entity)} does not have a representation shape."
                )
                raise LookupError(msg)
        else:
            self._calc_points(interval=point_interval)
            return self._points

    def print_structure(self, indent: int = 0):
        """
        Print alignment decomposition for debugging purposes.
        """
        print(" " * indent, str(self)[0:100])
        for rel in self.IsNestedBy:
            for child in rel.RelatedObjects:
                print_structure(child, indent + 2)

    def print_attributes(self):
        """
        Print all attributes of the IFC Entity for debugging puposes.
        """
        super().print_attributes()
        print("-----------------------------------------")
        print(f"{self.PredefinedType=}")


@dataclass
class BoundedCurve:
    """
    IfcBoundedCurve

    Ref: 8.9.3.10
    https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcBoundedCurve.htm
    """

    Dim: int = None


@dataclass
class CompositeCurve:
    """
    IfcCompositeCurve

    Ref: 8.9.3.20
    https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcCompositeCurve.htm
    """

    Segments: List[Segment]
    SelfIntersect: bool

    def create_shape(self) -> np.ndarray:
        raise NotImplementedError


@dataclass
class GradientCurve(CompositeCurve):
    """
    IfcGradientCurve

    Ref: 8.9.3.35
    https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcGradientCurve.htm
    """

    BaseCurve: BoundedCurve
    EndPoint: np.ndarray = None

    def create_shape(self) -> np.ndarray:
        raise NotImplementedError


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


def generic_test() -> None:
    test_file = "UT_AWC_1.ifc"
    # test_file = "UT_AWC_1_no_geometry.ifc"
    # test_file = "C3D-UT01.ifc"
    # test_file = "C3D-UT02.ifc"
    # test_file = "C3D-UT03.ifc"
    in_file = os.path.join(
        pathlib.Path(__file__).parent.absolute(), "..", "test", "fixtures", test_file
    )
    model = ifcopenshell.open(in_file)

    align_entity = model.by_type("IfcAlignment")[0]
    align = Alignment().from_entity(align_entity)

    s = ifcopenshell.geom.settings()
    s.set(s.INCLUDE_CURVES, True)
    xy = align.create_shape(settings=s, use_representation=False, point_interval=2)

    fg, ax = plt.subplots()
    ax.plot(xy.T[0], xy.T[1], marker=".", label="IfcOpenShell")
    ax.legend()
    ax.set_title(test_file)
    ax.grid(True, linestyle="-.")

    out_file = f"{test_file}.png"
    print(f"[INFO] writing output to {out_file}...")
    plt.savefig(out_file)
    print(f"[INFO] done.")


def synthetic_test(transition_type: str, case: int = 1) -> None:
    synthetic_path = os.path.join(
        pathlib.Path.home(),
        "src",
        "IFC-Rail-Sample-Files",
        "1_Alignment with Cant (AWC)",
        "UT_AWC_0_(Synthetic_Cases)",
        "Horizontal",
        "SyntheticTestcases",
    )
    type_path = os.path.join(synthetic_path, transition_type)
    test_index = 2
    test_data = {
        1: f"{transition_type}_100.0_inf_300_1_Meter",
        2: f"{transition_type}_100.0_-inf_-300_1_Meter",
        3: f"{transition_type}_100.0_300_inf_1_Meter",
        4: f"{transition_type}_100.0_-300_-inf_1_Meter",
        5: f"{transition_type}_100.0_1000_300_1_Meter",
        6: f"{transition_type}_100.0_-1000_-300_1_Meter",
        7: f"{transition_type}_100.0_300_1000_1_Meter",
        8: f"{transition_type}_100.0_-300_-1000_1_Meter",
    }
    test_case = test_data[test_index]
    test_title = f"TS{test_index}_{test_data[test_index]}"
    test_path = os.path.join(type_path, test_title)
    test_file = f"{test_case}.ifc"
    test_xlsx = f"TS{test_index}_{test_case}.xlsx"
    in_file = os.path.join(test_path, test_file)
    in_xlsx = os.path.join(test_path, test_xlsx)

    df1 = pd.read_excel(in_xlsx, sheet_name="horizontal 2D x,y", skiprows=2)
    df1.rename(
        columns={
            "Station on alignment": "Station",
            "Seg-specific X-coordinate": "X",
            "Seg-specific Y-coordinate": "Y",
        },
        inplace=True,
    )
    model = ifcopenshell.open(in_file)

    align_entity = model.by_type("IfcAlignment")[0]
    align = Alignment().from_entity(align_entity)

    s = ifcopenshell.geom.settings()
    s.set(s.INCLUDE_CURVES, True)
    xy = align.create_shape(settings=s, use_representation=False, point_interval=2)

    fg, ax = plt.subplots()
    ax.plot(xy.T[0], xy.T[1], marker=".", label="IfcOpenShell")
    ax.plot(df1["X"], df1["Y"], label="bSI-RailwayRoom")
    ax.legend()
    ax.set_title(test_file)
    ax.set_title(test_title)
    ax.grid(True, linestyle="-.")

    out_file = f"{test_title}.ifc.png"
    print(f"[INFO] writing output to {out_file}...")
    plt.savefig(out_file)
    print(f"[INFO] done.")


def awc_test(index: int = 1, geometry: bool = True) -> None:
    """
    Run one of the Alignment With Cant (AWC) test cases

    @param index: Index of the AWC test case
    @param geometry: Sets whether the test data should include the
    geometry representation as well as the business logic parameters
    for the alignment data.
    """
    test_name = f"UT_AWC_{index}"
    awc_path = os.path.join(
        pathlib.Path.home(),
        "src",
        "IFC-Rail-Sample-Files",
        "1_Alignment with Cant (AWC)",
        test_name,
        "IFC reference files",
        "RC4",
    )

    if geometry:
        test_file = f"{test_name}.ifc"
    else:
        test_file = f"{test_name}_no_geometry.ifc"
    in_file = os.path.join(awc_path, test_file)

    model = ifcopenshell.open(in_file)

    align_entity = model.by_type("IfcAlignment")[0]
    align = Alignment().from_entity(align_entity)

    s = ifcopenshell.geom.settings()
    s.set(s.INCLUDE_CURVES, True)
    xy = align.create_shape(settings=s, use_representation=False, point_interval=2)

    fg, ax = plt.subplots()
    ax.plot(xy.T[0], xy.T[1], label="IfcOpenShell")
    ax.set_title(test_file)
    ax.grid(True, linestyle="-.")

    out_file = f"{test_name}.ifc.png"
    print(f"[INFO] writing output to {out_file}...")
    plt.savefig(out_file)
    print(f"[INFO] done.")


class Root:
    """
    IfcRoot

    Ref: 5.4.3.443
    https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcRoot.htm
    """

    def __init__(self):
        self._elem = None

    def from_entity(self, elem: ifcopenshell.entity_instance):
        self._elem = elem

    @property
    def wrapped_entity(self):
        return self._elem

    @property
    def GlobalId(self):
        return self._elem.GlobalId

    @property
    def OwnerHistory(self):
        return self._elem.OwnerHistory

    @property
    def Name(self):
        return self._elem.Name

    @property
    def Description(self):
        return self._elem.Description

    def print_attributes(self):
        print(f"{self.wrapped_entity=}")
        print("-----------------------------------------")
        print(f"{self.OwnerHistory=}")
        print(f"{self.OwnerHistory.CreationDate=}")
        print(f"{self.OwnerHistory.State=}")
        print(f"{self.GlobalId=}")
        print(f"{self.Name=}")
        print(f"{self.Description=}")


class ObjectDefinition(Root):
    """
    IfcObjectDefintion

    5.1.3.7
    https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcObjectDefinition.htm
    """

    def __init__(self):
        super().__init__()

    @property
    def HasAssignments(self):
        return self._elem.HasAssignments

    @property
    def Nests(self):
        return self._elem.Nests

    @property
    def IsNestedBy(self):
        return self._elem.IsNestedBy

    @property
    def HasContext(self):
        return self._elem.HasContext

    @property
    def IsDecomposedBy(self):
        return self._elem.IsDecomposedBy

    @property
    def Decomposes(self):
        return self._elem.Decomposes

    @property
    def HasAssociations(self):
        return self._elem.HasAssociations

    def print_attributes(self):
        super().print_attributes()
        print("-----------------------------------------")
        print(f"{self.HasAssignments=}")
        print(f"{self.Nests=}")
        print(f"{self.IsNestedBy=}")
        print(f"{self.HasContext=}")
        print(f"{self.IsDecomposedBy=}")
        print(f"{self.Decomposes=}")
        print(f"{self.HasAssociations=}")


class Object(ObjectDefinition):
    """
    IfcObjectDefinition

    5.1.3.6
    https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcObject.htm
    """

    def __init__(self):
        super().__init__()

    @property
    def ObjectType(self):
        return self._elem.ObjectType

    @property
    def IsDeclaredBy(self):
        return self._elem.IsDeclaredBy

    @property
    def Declares(self):
        return self._elem.Declares

    @property
    def IsTypedBy(self):
        return self._elem.IsTypedBy

    @property
    def IsDefinedBy(self):
        return self._elem.IsDefinedBy

    def print_attributes(self):
        super().print_attributes()
        print("-----------------------------------------")
        print(f"{self.ObjectType=}")
        print(f"{self.IsDeclaredBy=}")
        print(f"{self.Declares=}")
        print(f"{self.IsTypedBy=}")
        print(f"{self.IsDefinedBy=}")


class Product(Object):
    """
    IfcProduct

    5.1.3.10
    https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcProduct.htm
    """

    def __init__(self):
        super().__init__()

    @property
    def ObjectPlacement(self):
        return self._elem.ObjectPlacement

    @property
    def Representation(self):
        return self._elem.Representation

    @property
    def ReferencedBy(self):
        return self._elem.ReferencedBy

    @property
    def PositionedRelativeTo(self):
        return self._elem.PositionedRelativeTo

    @property
    def ReferencedInStructures(self):
        return self._elem.ReferencedInStructures

    def print_attributes(self):
        super().print_attributes()
        print("-----------------------------------------")
        print(f"{self.ObjectPlacement=}")
        print(f"{self.Representation=}")
        print(f"{self.ReferencedBy=}")
        print(f"{self.PositionedRelativeTo=}")
        print(f"{self.ReferencedInStructures=}")


class PositioningElement(Product):
    """
    IfcPositioningElement

    5.4.3.42
    https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcPositioningElement.htm
    """

    def __init__(self):
        super().__init__()

    @property
    def ContainedInStructure(self):
        return self._elem.ContainedInStructure

    @property
    def Positions(self):
        return self._elem.Positions

    def print_attributes(self):
        super().print_attributes()
        print("-----------------------------------------")
        print(f"{self.ContainedInStructure=}")
        print(f"{self.Positions=}")


class LinearElement(Product):
    """
    IfcLinearElement

    5.4.3.38
    https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcLinearElement.htm
    """

    def __init__(self):
        super().__init__()


@dataclass
class AlignmentHorizontalSegmentTypeEnum(Enum):
    """
    IfcAlignmentHorizontalSegmentTypeEnum

    8.7.2.2
    https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcAlignmentHorizontalSegmentTypeEnum.htm
    """

    BLOSSCURVE = "BLOSSCURVE"
    CIRCULARARC = "CIRCULARARC"
    CLOTHOID = "CLOTHOID"
    COSINECURVE = "COSINECURVE"
    CUBIC = "CUBIC"
    HELMERTCURVE = "HELMERTCURVE"  # also referred to as Schramm curve.
    LINE = "LINE"
    SINECURVE = "SINECURVE"  # also referred to as Klein curve
    VIENNESEBEND = "VIENNESEBEND"


class AlignmentParameterSegment:
    """
    IfcAlignmentParameterSegment

    8.7.3.3
    https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcAlignmentParameterSegment.htm
    """

    StartTag: str = None
    EndTag: str = None


@dataclass
class AlignmentSegment(Product):
    """
    IfcAlignmentSegment

    5.4.3.4
    https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcAlignmentSegment.htm
    """

    DesignParameters: AlignmentParameterSegment


@dataclass
class AlignmentHorizontalSegment(AlignmentParameterSegment):
    """
    IfcAlignmentHorizontalSegment

    8.7.3.2
    https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcAlignmentHorizontalSegment.htm

    @param start_distance: Distance along the alignment at the start of this segment
    """

    StartPoint: np.ndarray
    StartDirection: float
    StartRadiusOfCurvature: float
    EndRadiusOfCurvature: float
    SegmentLength: float
    PredefinedType: float
    GravityCenterLineHeight: float = None
    start_distance: float = 0

    @property
    def end_distance(self):
        """
        Distance along the alignment at the end of this segment
        """
        return self.start_distance + self.SegmentLength

    @property
    def is_CCW(self) -> bool:
        """
        Whether or not this segment deflects counter clockwise
        """
        if self.StartRadiusOfCurvature >= 0:
            return True
        else:
            return False

    def calc_point(self, u: float) -> np.ndarray:
        """
        Calculate an x, y point at distance u along this segment
        """
        if u < 0:
            msg = f"Invalid distance '{u}' along segment. Distance must be positive."
            raise ValueError(msg)

        if u > self.SegmentLength:
            msg = f"Invalid distance '{u}' along segment. Distance must be <= total length '{self.SegmentLength}'."
            raise ValueError(msg)

        return globals()[f"point_on_{self.PredefinedType.value}"](self, u)


@dataclass
class AlignmentPoint:
    """
    Not sure if this will be useful.
    Might serve as syntatic sugar over the numpy array
    """

    index: int
    x: float
    y: float
    z: float
    station: float
    direction: float
    radius: float


class AlignmentHorizontal(LinearElement):
    """
    IfcAlignmentHorizontal

    5.4.3.3
    https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcAlignmentHorizontal.htm
    """

    def __init__(self):
        super().__init__()
        self._segments = list()

    def from_entity(self, elem: ifcopenshell.entity_instance):
        self._elem = elem
        self._length = 0
        for rel in elem.IsNestedBy:
            for child in rel.RelatedObjects:
                dp = child.DesignParameters
                if not dp.is_a("IfcAlignmentHorizontalSegment"):
                    msg = f"""Alignment segment is a {dp.is_a()}. \n 
                        IfcHorizontal can only be nested by IfcAlignmentHorizontalSegment entities.
                        """
                    raise ValueError(msg)
                x, y = dp.StartPoint.Coordinates

                hs = AlignmentHorizontalSegment(
                    StartPoint=np.array([x, y, np.nan], dtype=np.float64),
                    StartDirection=dp.StartDirection,
                    StartRadiusOfCurvature=dp.StartRadiusOfCurvature,
                    EndRadiusOfCurvature=dp.EndRadiusOfCurvature,
                    SegmentLength=dp.SegmentLength,
                    PredefinedType=AlignmentHorizontalSegmentTypeEnum(
                        dp.PredefinedType,
                    ),
                    GravityCenterLineHeight=dp.GravityCenterLineHeight,
                )
                # set start and end distances of this segment based on
                # how far we have traversed along the alignment
                hs.start_distance = self._length
                self._length += hs.SegmentLength
                self._segments.append(hs)

        return self

    @property
    def segments(self) -> List[AlignmentHorizontalSegment]:
        return self._segments

    @property
    def length(self) -> float:
        return self._length


class AlignmentVertical(LinearElement):
    """
    IfcAlignmentVertical

    5.4.3.5
    https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcAlignmentVertical.htm
    """

    def __init__(self):
        super().__init__()
        self._segments = list()

    def from_entity(self, elem: ifcopenshell.entity_instance):
        self._elem = elem
        for rel in elem.IsNestedBy:
            for child in rel.RelatedObjects:
                dp = child.DesignParameters
                if not dp.is_a("IfcAlignmentVerticalSegment"):
                    msg = f"""Alignment segment is a {dp.is_a()}. \n 
                        IfcVertical can only be nested by IfcAlignmentVerticalSegment entities.
                        """
                    raise ValueError(msg)


class Alignment(PositioningElement):
    """
    IfcAlignment

    Ref: 5.4.3.1
    https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcAlignment.htm
    """

    def __init__(self):
        super().__init__()
        self._horizontal = None
        self._vertical = None
        self._cant = None

    @property
    def PredefinedType(self):
        return self._elem.PredefinedType

    @property
    def horizontal(self) -> AlignmentHorizontal:
        return self._horizontal

    @property
    def vertical(self) -> AlignmentVertical:
        return self._vertical

    """
    @property
    def cant(self) -> AlignmentCant:
        return self._cant
    """

    def from_entity(self, elem: ifcopenshell.entity_instance):
        self._elem = elem

        # extract horizontal, vertical, and cant if they exist
        for rel in self.IsNestedBy:
            for child in rel.RelatedObjects:
                if child.is_a("IfcAlignmentHorizontal"):
                    self._horizontal = AlignmentHorizontal().from_entity(child)

                # TODO
                """
                elif child.is_a("IfcAlignmentVertical"):
                    self._vertical = AlignmentVertical().from_entity(child)
                elif child.is_a("IfcAlignmentCant"):
                    self._vertical = AlignmentCant().from_entity(child)
                """
        return self

    @property
    def length(self) -> float:
        """
        Total length of the alignment.
        """
        return self._horizontal.length

    def _calc_points(self, interval: float = 5.0):
        """
        Calculate all of the points on the alignment at a specific distance (interval)
        between points
        """
        pts = list()
        segs = self._horizontal.segments
        distances = np.arange(0, self.length, interval)
        # TODO: add ends of each segment to the array of distances

        idx = 0  # index of the segments
        for d in distances[0:10]:
            if d >= segs[idx].end_distance:
                idx += 1
            pts.append(segs[idx].calc_point(u=(d - segs[idx].start_distance)))

        self._points = np.array(pts)

    def create_shape(
        self,
        settings: ifcopenshell.geom.settings = ifcopenshell.geom.settings(),
        use_representation: bool = True,
        point_interval: float = 5.0,
    ) -> np.ndarray:
        """
        There are two approaches to modeling IfcAlignment entities: business aspects and representation with
        IFC geometry resources.
        If a representation exists, it may be utilized.  Otherwise it will be calculated from the parameters
        of each individual segment.

        @param use_representation: Use the geometry from the IFC geometry entities, if it exists
        @param point_interval: The distance between points that will be calculated along the alignment.
        """
        if use_representation:
            try:
                if len(self.Representation) > 0:
                    return ifcopenshell.geom.create_shape(settings, self.wrapped_entity)
            except TypeError:
                msg = (
                    f"{str(self.wrapped_entity)} does not have a representation shape."
                )
                raise LookupError(msg)
        else:
            # msg = "Calculation of shape from segment parameters is not implemented yet."
            # raise NotImplementedError(msg)
            self._calc_points(interval=point_interval)
            return self._points

    def print_structure(self, indent: int = 0):
        """
        Print alignment decomposition for debugging purposes.
        """
        print(" " * indent, str(self)[0:100])
        for rel in self.IsNestedBy:
            for child in rel.RelatedObjects:
                print_structure(child, indent + 2)

    def print_attributes(self):
        """
        Print all attributes of the IFC Entity for debugging puposes.
        """
        super().print_attributes()
        print("-----------------------------------------")
        print(f"{self.PredefinedType=}")


def point_on_LINE(segment: AlignmentHorizontalSegment, u: float) -> np.ndarray:
    """
    2D point at distance u along a LINE segment
    """
    return segment.StartPoint + np.array(
        [
            u * math.cos(segment.StartDirection),
            u * math.sin(segment.StartDirection),
            np.nan,
        ]
    )


def point_on_CIRCULARARC(segment: AlignmentHorizontalSegment, u: float) -> np.ndarray:
    """
    Point at distance u along a CIRCULARARC segment

    Ref: https://connect.ncdot.gov/resources/Structures/Structure%20Design%20Manual/Fig08%20Horizontal%20CurveTangent%20Offset.pdf
    """
    # calc local point with forward tangent on positive x-axis

    R = abs(segment.StartRadiusOfCurvature)
    x = u
    y = R - math.sqrt((R**2 - u**2))

    if not segment.is_CCW:
        y = -y

    # rotation matrix
    theta = segment.StartDirection
    rot_mat = np.array(
        [
            [math.cos(theta), -math.sin(theta)],
            [math.sin(theta), math.cos(theta)],
        ]
    )
    rotated = np.array([x, y]) @ rot_mat
    world_pt = segment.StartPoint + np.array([rotated[0], rotated[1], np.nan])
    world_pt = segment.StartPoint + np.array([x, y, np.nan])

    return world_pt


if __name__ == "__main__":
    from matplotlib import pyplot as plt
    import ifcopenshell
    import pandas as pd

    # synthetic test
    transition_types = [
        "Bloss",
        "Clothoid",
        "Cosine",
        "Helmert",
        "Sine",
        "Viennese Bend",
    ]
    transition_type = transition_types[2]
    # synthetic_test(transition_type, 1)

    # AWC test
    awc_test(index=1, geometry=True)
