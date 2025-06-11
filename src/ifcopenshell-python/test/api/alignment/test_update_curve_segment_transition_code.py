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

import pytest
import ifcopenshell.api.alignment
import ifcopenshell.api.context


def _test1():
    file = ifcopenshell.file(schema="IFC4X3")
    project = file.createIfcProject(Name="Test")
    geometric_representation_context = ifcopenshell.api.context.add_context(file, context_type="Model")
    axis_model_representation_subcontext = ifcopenshell.api.context.add_context(
        file,
        context_type="Model",
        context_identifier="Axis",
        target_view="MODEL_VIEW",
        parent=geometric_representation_context,
    )

    # 26=IFCCARTESIANPOINT((4084.115884,3889.462938));
    # 70=IFCDIRECTION((0.224530986099614,0.974466949814685));
    # 71=IFCAXIS2PLACEMENT2D(#26,#70);
    # 72=IFCCARTESIANPOINT((0.,0.));
    # 73=IFCDIRECTION((1.,0.));
    # 74=IFCAXIS2PLACEMENT2D(#72,#73);
    # 75=IFCCIRCLE(#74,1250.);
    # 76=IFCCURVESEGMENT(.CONTSAMEGRADIENT.,#71,IFCLENGTHMEASURE(0.),IFCLENGTHMEASURE(-1848.115835),#75);
    circular_arc = file.createIfcCurveSegment(
        Placement=file.createIfcAxis2Placement2d(
            file.createIfcCartesianPoint((4084.115884, 3889.462938)),
            file.createIfcDirection((0.224530986099614, 0.974466949814685)),
        ),
        SegmentStart=file.createIfcLengthMeasure(0.0),
        SegmentLength=file.createIfcLengthMeasure(-1848.115835),
        ParentCurve=file.createIfcCircle(
            Position=file.createIfcAxis2Placement2d(
                file.createIfcCartesianPoint((0.0, 0.0)), file.createIfcDirection((1.0, 0.0))
            ),
            Radius=1250.0,
        ),
    )

    # 27=IFCCARTESIANPOINT((5469.395067,4847.56631));
    # 77=IFCDIRECTION((0.991014275066766,-0.133756146078947));
    # 78=IFCAXIS2PLACEMENT2D(#27,#77);
    # 79=IFCCARTESIANPOINT((0.,0.));
    # 80=IFCDIRECTION((1.,0.));
    # 81=IFCVECTOR(#80,1.);
    # 82=IFCLINE(#79,#81);
    # 83=IFCCURVESEGMENT(.CONTSAMEGRADIENT.,#78,IFCLENGTHMEASURE(0.),IFCLENGTHMEASURE(1564.635765),#82);
    line = file.createIfcCurveSegment(
        Placement=file.createIfcAxis2Placement2d(
            file.createIfcCartesianPoint((5469.395067, 4847.56631)),
            file.createIfcDirection((0.991014275066766, -0.133756146078947)),
        ),
        SegmentStart=file.createIfcLengthMeasure(0.0),
        SegmentLength=file.createIfcLengthMeasure(1564.635765),
        ParentCurve=file.createIfcLine(
            Pnt=file.createIfcCartesianPoint((0.0, 0.0)),
            Dir=file.createIfcVector(Orientation=file.createIfcDirection((1.0, 0.0)), Magnitude=1.0),
        ),
    )

    composite_curve = file.createIfcCompositeCurve(Segments=(circular_arc, line), SelfIntersect=False)

    ifcopenshell.api.alignment.update_curve_segment_transition_code(circular_arc, line)
    assert circular_arc.Transition == "CONTSAMEGRADIENT"


def _test2():
    file = ifcopenshell.file(schema="IFC4X3")
    project = file.createIfcProject(Name="Test")
    geometric_representation_context = ifcopenshell.api.context.add_context(file, context_type="Model")
    axis_model_representation_subcontext = ifcopenshell.api.context.add_context(
        file,
        context_type="Model",
        context_identifier="Axis",
        target_view="MODEL_VIEW",
        parent=geometric_representation_context,
    )
    # 30=IFCCARTESIANPOINT((0.,0.));
    # 31=IFCALIGNMENTHORIZONTALSEGMENT($,$,#30,0.523598775598299,0.,0.,27.8843513637174,$,.LINE.);
    # 32=IFCALIGNMENTSEGMENT('3$jiMaOgfAoujgvRyMLw0X',$,'H1',$,$,#111,#113,#31);
    # 33=IFCDIRECTION((0.866025403784439,0.5));
    # 34=IFCAXIS2PLACEMENT2D(#30,#33);
    # 35=IFCCARTESIANPOINT((0.,0.));
    # 36=IFCDIRECTION((1.,0.));
    # 37=IFCVECTOR(#36,1.);
    # 38=IFCLINE(#35,#37);
    # 39=IFCCURVESEGMENT(.CONTSAMEGRADIENT.,#34,IFCLENGTHMEASURE(0.),IFCLENGTHMEASURE(27.8843513637174),#38);

    line1 = file.createIfcCurveSegment(
        Placement=file.createIfcAxis2Placement2d(
            file.createIfcCartesianPoint((0.0, 0.0)),
            file.createIfcDirection((0.866025403784439, 0.5)),
        ),
        SegmentStart=file.createIfcLengthMeasure(0.0),
        SegmentLength=file.createIfcLengthMeasure(27.8843513637174),
        ParentCurve=file.createIfcLine(
            Pnt=file.createIfcCartesianPoint((0.0, 0.0)),
            Dir=file.createIfcVector(Orientation=file.createIfcDirection((1.0, 0.0)), Magnitude=1.0),
        ),
    )

    # 40=IFCCARTESIANPOINT((24.1485566490305,13.9421756818587));
    # 41=IFCALIGNMENTHORIZONTALSEGMENT($,$,#40,0.523598775598299,0.,1524.,152.4,$,.CLOTHOID.);
    # 42=IFCALIGNMENTSEGMENT('0Rd38fCkHF1Q11ppiqdMP6',$,'H2',$,$,#111,#115,#41);
    # 43=IFCDIRECTION((0.866025403784439,0.5));
    # 44=IFCAXIS2PLACEMENT2D(#40,#43);
    # 45=IFCCARTESIANPOINT((0.,0.));
    # 46=IFCDIRECTION((1.,0.));
    # 47=IFCAXIS2PLACEMENT2D(#45,#46);
    # 48=IFCCLOTHOID(#47,481.931115409661);
    # 49=IFCCURVESEGMENT(.CONTSAMEGRADIENT.,#44,IFCLENGTHMEASURE(0.),IFCLENGTHMEASURE(152.4),#48);

    clothoid1 = file.createIfcCurveSegment(
        Placement=file.createIfcAxis2Placement2d(
            file.createIfcCartesianPoint((24.1485566490305, 13.9421756818587)),
            file.createIfcDirection((0.866025403784439, 0.5)),
        ),
        SegmentStart=file.createIfcLengthMeasure(0.0),
        SegmentLength=file.createIfcLengthMeasure(152.4),
        ParentCurve=file.createIfcClothoid(
            Position=file.createIfcAxis2Placement2d(
                file.createIfcCartesianPoint((0.0, 0.0)), RefDirection=file.createIfcDirection((1.0, 0.0))
            ),
            ClothoidConstant=481.931115409661,
        ),
    )

    # 50=IFCCARTESIANPOINT((154.828063204281,92.32243963907));
    # 51=IFCALIGNMENTHORIZONTALSEGMENT($,$,#50,0.573598775598299,1524.,1524.,246.582267005904,$,.CIRCULARARC.);
    # 52=IFCALIGNMENTSEGMENT('2OGYY2lQjCnRlzxKU9vtdu',$,'H3',$,$,#111,#117,#51);
    # 53=IFCDIRECTION((0.839953512903025,0.542658360445933));
    # 54=IFCAXIS2PLACEMENT2D(#50,#53);
    # 55=IFCCARTESIANPOINT((0.,0.));
    # 56=IFCDIRECTION((1.,0.));
    # 57=IFCAXIS2PLACEMENT2D(#55,#56);
    # 58=IFCCIRCLE(#57,1524.);
    # 59=IFCCURVESEGMENT(.CONTSAMEGRADIENT.,#54,IFCLENGTHMEASURE(0.),IFCLENGTHMEASURE(246.582267005904),#58);

    circular_arc = file.createIfcCurveSegment(
        Placement=file.createIfcAxis2Placement2d(
            file.createIfcCartesianPoint((154.828063204281, 92.32243963907)),
            file.createIfcDirection((0.839953512903025, 0.542658360445933)),
        ),
        SegmentStart=file.createIfcLengthMeasure(0.0),
        SegmentLength=file.createIfcLengthMeasure(246.582267005904),
        ParentCurve=file.createIfcCircle(
            Position=file.createIfcAxis2Placement2d(
                file.createIfcCartesianPoint((0.0, 0.0)), file.createIfcDirection((1.0, 0.0))
            ),
            Radius=1524.0,
        ),
    )

    # 60=IFCCARTESIANPOINT((350.24160971216,242.268527691248));
    # 61=IFCALIGNMENTHORIZONTALSEGMENT($,$,#60,0.735398163397447,1524.,0.,152.4,$,.CLOTHOID.);
    # 62=IFCALIGNMENTSEGMENT('13CGRzUN9CAfNVKnf0Pxza',$,'H4',$,$,#111,#119,#61);
    # 63=IFCDIRECTION((0.741563691346478,0.670882472327743));
    # 64=IFCAXIS2PLACEMENT2D(#60,#63);
    # 65=IFCCARTESIANPOINT((0.,0.));
    # 66=IFCDIRECTION((1.,0.));
    # 67=IFCAXIS2PLACEMENT2D(#65,#66);
    # 68=IFCCLOTHOID(#67,-481.931115409661);
    # 69=IFCCURVESEGMENT(.CONTSAMEGRADIENT.,#64,IFCLENGTHMEASURE(-152.4),IFCLENGTHMEASURE(152.4),#68);

    clothoid2 = file.createIfcCurveSegment(
        Placement=file.createIfcAxis2Placement2d(
            file.createIfcCartesianPoint((350.24160971216, 242.268527691248)),
            file.createIfcDirection((0.741563691346478, 0.670882472327743)),
        ),
        SegmentStart=file.createIfcLengthMeasure(-152.4),
        SegmentLength=file.createIfcLengthMeasure(152.4),
        ParentCurve=file.createIfcClothoid(
            Position=file.createIfcAxis2Placement2d(
                file.createIfcCartesianPoint((0.0, 0.0)), RefDirection=file.createIfcDirection((1.0, 0.0))
            ),
            ClothoidConstant=-481.931115409661,
        ),
    )

    # 70=IFCCARTESIANPOINT((459.773476040884,348.208932967387));
    # 71=IFCALIGNMENTHORIZONTALSEGMENT($,$,#70,0.785398163397448,0.,0.,0.,$,.LINE.);
    # 72=IFCALIGNMENTSEGMENT('0FlcTrOfT5YBi0fqVhTMyc',$,'H5',$,$,#111,#121,#71);
    # 73=IFCDIRECTION((0.707106781186548,0.707106781186548));
    # 74=IFCAXIS2PLACEMENT2D(#70,#73);
    # 75=IFCCARTESIANPOINT((0.,0.));
    # 76=IFCDIRECTION((1.,0.));
    # 77=IFCVECTOR(#76,1.);
    # 78=IFCLINE(#75,#77);
    # 79=IFCCURVESEGMENT(.DISCONTINUOUS.,#74,IFCLENGTHMEASURE(0.),IFCLENGTHMEASURE(0.),#78);

    line2 = file.createIfcCurveSegment(
        Placement=file.createIfcAxis2Placement2d(
            file.createIfcCartesianPoint((459.773476040884, 348.208932967387)),
            file.createIfcDirection((0.707106781186548, 0.707106781186548)),
        ),
        SegmentStart=file.createIfcLengthMeasure(0.0),
        SegmentLength=file.createIfcLengthMeasure(0.0),
        ParentCurve=file.createIfcLine(
            Pnt=file.createIfcCartesianPoint((0.0, 0.0)),
            Dir=file.createIfcVector(Orientation=file.createIfcDirection((1.0, 0.0)), Magnitude=1.0),
        ),
    )

    composite_curve = file.createIfcCompositeCurve(Segments=[], SelfIntersect=False)

    # add_segment_to_curve calls update_curve_segment_transition_code
    ifcopenshell.api.alignment.add_segment_to_curve(file, line1, composite_curve)
    assert line1.Transition == "DISCONTINUOUS"

    ifcopenshell.api.alignment.add_segment_to_curve(file, clothoid1, composite_curve)
    assert line1.Transition == "CONTSAMEGRADIENTSAMECURVATURE"
    assert clothoid1.Transition == "DISCONTINUOUS"

    ifcopenshell.api.alignment.add_segment_to_curve(file, circular_arc, composite_curve)
    assert clothoid1.Transition == "CONTSAMEGRADIENTSAMECURVATURE"
    assert circular_arc.Transition == "DISCONTINUOUS"

    ifcopenshell.api.alignment.add_segment_to_curve(file, clothoid2, composite_curve)
    assert circular_arc.Transition == "CONTSAMEGRADIENTSAMECURVATURE"
    assert clothoid2.Transition == "DISCONTINUOUS"

    ifcopenshell.api.alignment.add_segment_to_curve(file, line2, composite_curve)
    assert clothoid2.Transition == "CONTSAMEGRADIENTSAMECURVATURE"
    assert line2.Transition == "DISCONTINUOUS"


def test_update_curve_segment_transition_code():
    _test1()
    _test2()
