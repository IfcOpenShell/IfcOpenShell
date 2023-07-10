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
import math
import os
import pathlib
from typing import List

import numpy as np

import ifcopenshell.geom
import ifcopenshell.express
from ifcopenshell.alignment_enums import TransitionCode

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


def synthetic_test(transition_type: str, case: int = 1) -> None:
    from .ifcgeom import Alignment

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
    from .ifcgeom import Alignment

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
    cant: float


def point_on_LINE(segment, u: float) -> np.ndarray:
    """
    2D point at distance u along a LINE segment

    @param segment: IfcAlignmentHorizontalSegment containing the point
    @type segment: ifcopenshell.ifcgeom.AlignmentHorizontalSegment
    """
    raise NameError("We shouldn't be using this implementation!?!?")


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
