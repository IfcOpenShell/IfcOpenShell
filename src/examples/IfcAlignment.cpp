/********************************************************************************
 *                                                                              *
 * This file is part of IfcOpenShell.                                           *
 *                                                                              *
 * IfcOpenShell is free software: you can redistribute it and/or modify         *
 * it under the terms of the Lesser GNU General Public License as published by  *
 * the Free Software Foundation, either version 3.0 of the License, or          *
 * (at your option) any later version.                                          *
 *                                                                              *
 * IfcOpenShell is distributed in the hope that it will be useful,              *
 * but WITHOUT ANY WARRANTY; without even the implied warranty of               *
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the                 *
 * Lesser GNU General Public License for more details.                          *
 *                                                                              *
 * You should have received a copy of the Lesser GNU General Public License     *
 * along with this program. If not, see <http://www.gnu.org/licenses/>.         *
 *                                                                              *
 ********************************************************************************/

// This example illustrates the basic of building an alignment model.
// The alignment is based on "Bridge Geometry Manual", April 2022
// US Department of Transportation, Federal Highway Administration (FHWA)
// https://www.fhwa.dot.gov/bridge/pubs/hif22034.pdf
//
// Sections and page number for this document are cited in the code comments.
//
// This examples differs from IfcSimplifiedAlignment because it builds the
// alignment explicitly

// Disable warnings coming from IfcOpenShell
#pragma warning(disable : 4018 4267 4250 4984 4985)

#include "../ifcparse/Ifc4x3_add2.h"
#include "../ifcparse/IfcHierarchyHelper.h"

#include <boost/math/constants/constants.hpp>
#include <fstream>

const double PI = boost::math::constants::pi<double>();
double to_radian(double deg) { return PI * deg / 180; }

#define Schema Ifc4x3_add2

// performs basic project setup including created the IfcProject object
// and initializing the project units to FEET
Schema::IfcProject setup_project(IfcHierarchyHelper<Schema>& file) {
    std::vector<std::string> file_description;
    file_description.push_back("ViewDefinition[Alignment-basedReferenceView]");
    file.header().file_description().setdescription(file_description);

    auto project = file.addProject();
    project.setName("FHWA Bridge Geometry Manual Example Alignment");
    project.setDescription("C++ Example");

    // set up project units for feet
    // the call to file.addProject() sets up length units as millimeter.
    auto units_in_context = project.UnitsInContext();
    auto units = units_in_context.Units();
    auto begin = units.begin();
    auto iter = begin;
    auto end = units.end();
    for (; iter != end; iter++) {
        auto& unit = *iter;
        if (unit.as<Schema::IfcSIUnit>() && unit.as<Schema::IfcSIUnit>().UnitType() == Schema::IfcUnitEnum::IfcUnit_LENGTHUNIT) {
            auto dimensions = file.create<Schema::IfcDimensionalExponents>();
            dimensions.setLengthExponent(1);
            dimensions.setMassExponent(0);
            dimensions.setTimeExponent(0);
            dimensions.setElectricCurrentExponent(0);
            dimensions.setThermodynamicTemperatureExponent(0);
            dimensions.setAmountOfSubstanceExponent(0);
            dimensions.setLuminousIntensityExponent(0);
            
            auto conversion_factor = file.create<Schema::IfcMeasureWithUnit>();
            auto length = file.create<Schema::IfcLengthMeasure>();
            length.set_attribute_value(0, 304.80);
            conversion_factor.setValueComponent(length);
            conversion_factor.setUnitComponent(unit);

            auto conversion_based_unit = file.create<Schema::IfcConversionBasedUnit>();
            conversion_based_unit.setDimensions(dimensions);
            conversion_based_unit.setUnitType(Schema::IfcUnitEnum::IfcUnit_LENGTHUNIT);
            conversion_based_unit.setName("FEET");
            conversion_based_unit.setConversionFactor(conversion_factor);
            
            units.erase(std::remove(units.begin(), units.end(), unit)); // remove the millimeter unit
            units.push_back(conversion_based_unit); // add the feet unit
            units_in_context.setUnits(units);  // update the UnitsInContext

            break; // Done!, the length unit was found, so break out of the loop
        }
    }

    return project;
}

// creates geometry and business logic segments for horizontal alignment tangent runs
std::pair<typename Schema::IfcCurveSegment, typename Schema::IfcAlignmentSegment> create_tangent(IfcHierarchyHelper<Schema>& file, const typename Schema::IfcCartesianPoint& p, double dir, double length) {
    // geometry
    auto parent_curve = file.create<Schema::IfcLine>();
    parent_curve.setPnt(file.addDoublet<Schema::IfcCartesianPoint>(0.0, 0.0));
    auto vec = file.create<Schema::IfcVector>();
    vec.setOrientation(file.addDoublet<Schema::IfcDirection>(1.0, 0.0));
    vec.setMagnitude(1.0);
    parent_curve.setDir(vec);

    auto place = file.create<Schema::IfcAxis2Placement2D>();
    place.setLocation(p);
    place.setRefDirection(file.addDoublet<Schema::IfcDirection>(cos(dir), sin(dir)));

    auto curve_segment = file.create<Schema::IfcCurveSegment>();
    curve_segment.setTransition(Schema::IfcTransitionCode::IfcTransitionCode_CONTSAMEGRADIENT);
    curve_segment.setPlacement(place);
    curve_segment.setSegmentStart(file.addValue<Schema::IfcLengthMeasure>(0.0));
    curve_segment.setSegmentLength(file.addValue<Schema::IfcLengthMeasure>(length));
    curve_segment.setParentCurve(parent_curve);

    // business logic
    auto design_parameters = file.create<Schema::IfcAlignmentHorizontalSegment>();
    design_parameters.setStartPoint(p);
    design_parameters.setStartDirection(dir);
    design_parameters.setStartRadiusOfCurvature(0.0);
    design_parameters.setEndRadiusOfCurvature(0.0);
    design_parameters.setSegmentLength(length);
    design_parameters.setPredefinedType(Schema::IfcAlignmentHorizontalSegmentTypeEnum::IfcAlignmentHorizontalSegmentType_LINE);

    auto alignment_segment = file.create<Schema::IfcAlignmentSegment>();
    alignment_segment.setGlobalId(IfcParse::IfcGlobalId());
    alignment_segment.setDesignParameters(design_parameters);

    return {curve_segment, alignment_segment};
}

// creates geometry and business logic segments for horizontal alignment horizonal curves
std::pair<typename Schema::IfcCurveSegment, typename Schema::IfcAlignmentSegment> create_hcurve(IfcHierarchyHelper<Schema>& file, const typename Schema::IfcCartesianPoint& pc, double dir, double radius, double lc) {
    // geometry
    double sign = radius / fabs(radius);
    auto place = file.create<Schema::IfcAxis2Placement2D>();
    place.setLocation(file.addDoublet<Schema::IfcCartesianPoint>(0.0, 0.0));
    place.setRefDirection(file.addDoublet<Schema::IfcDirection>(1.0, 0.0));
    auto parent_curve = file.create<Schema::IfcCircle>();
    parent_curve.setPosition(place);
    parent_curve.setRadius(fabs(radius));

    auto place2 = file.create<Schema::IfcAxis2Placement2D>();
    place2.setLocation(pc);
    place2.setRefDirection(file.addDoublet<Schema::IfcDirection>(cos(dir), sin(dir)));

    auto curve_segment = file.create<Schema::IfcCurveSegment>();
    curve_segment.setTransition(Schema::IfcTransitionCode::IfcTransitionCode_CONTSAMEGRADIENT);
    curve_segment.setPlacement(place2);
    curve_segment.setSegmentStart(file.addValue<Schema::IfcLengthMeasure>(0.0));
    curve_segment.setSegmentLength(file.addValue<Schema::IfcLengthMeasure>(sign * lc));
    curve_segment.setParentCurve(parent_curve);

    // business logic
    auto design_parameters = file.create<Schema::IfcAlignmentHorizontalSegment>();
    design_parameters.setStartPoint(pc);
    design_parameters.setStartDirection(dir);
    design_parameters.setStartRadiusOfCurvature(radius);
    design_parameters.setEndRadiusOfCurvature(radius);
    design_parameters.setSegmentLength(lc);
    design_parameters.setPredefinedType(Schema::IfcAlignmentHorizontalSegmentTypeEnum::IfcAlignmentHorizontalSegmentType_CIRCULARARC);

    auto alignment_segment = file.create<Schema::IfcAlignmentSegment>();
    alignment_segment.setGlobalId(IfcParse::IfcGlobalId());
    alignment_segment.setDesignParameters(design_parameters);

    return {curve_segment, alignment_segment};
}

// creates geometry and business logic segments for vertical profile gradient runs
std::pair<typename Schema::IfcCurveSegment, typename Schema::IfcAlignmentSegment> create_gradient(IfcHierarchyHelper<Schema>& file, const typename Schema::IfcCartesianPoint& p, double slope, double length) {
    // geometry
    auto parent_curve = file.create<Schema::IfcLine>();
    parent_curve.setPnt(file.addDoublet<Schema::IfcCartesianPoint>(0.0, 0.0));
    auto vec = file.create<Schema::IfcVector>();
    vec.setOrientation(file.addDoublet<Schema::IfcDirection>(1.0, 0.0));
    vec.setMagnitude(1.0);
    parent_curve.setDir(vec);

    auto place2 = file.create<Schema::IfcAxis2Placement2D>();
    place2.setLocation(p);
    place2.setRefDirection(file.addDoublet<Schema::IfcDirection>(sqrt(1 - slope * slope), slope));

    auto curve_segment = file.create<Schema::IfcCurveSegment>();
    curve_segment.setTransition(Schema::IfcTransitionCode::IfcTransitionCode_CONTSAMEGRADIENT);
    curve_segment.setPlacement(place2);
    curve_segment.setSegmentStart(file.addValue<Schema::IfcLengthMeasure>(0.0));
    curve_segment.setSegmentLength(file.addValue<Schema::IfcLengthMeasure>(length));
    curve_segment.setParentCurve(parent_curve);

    // business logic
    auto design_parameters = file.create<Schema::IfcAlignmentVerticalSegment>();
    design_parameters.setStartDistAlong(p.Coordinates()[0]);
    design_parameters.setHorizontalLength(length);
    design_parameters.setStartHeight(p.Coordinates()[1]);
    design_parameters.setStartGradient(slope);
    design_parameters.setEndGradient(slope);
    design_parameters.setPredefinedType(Schema::IfcAlignmentVerticalSegmentTypeEnum::IfcAlignmentVerticalSegmentType_CONSTANTGRADIENT);

    auto alignment_segment = file.create<Schema::IfcAlignmentSegment>();
    alignment_segment.setGlobalId(IfcParse::IfcGlobalId());
    alignment_segment.setDesignParameters(design_parameters);

    return {curve_segment, alignment_segment};
}

// creates geometry and business logic segments for vertical profile parabolic vertical curves
std::pair<typename Schema::IfcCurveSegment, typename Schema::IfcAlignmentSegment> create_vcurve(IfcHierarchyHelper<Schema>& file, const typename Schema::IfcCartesianPoint& p, double start_slope, double end_slope, double length) {
    // geometry
    double A = p.Coordinates()[1];
    double B = start_slope;
    double C = (end_slope - start_slope) / (2 * length);

    auto place = file.create<Schema::IfcAxis2Placement2D>();
    place.setLocation(file.addDoublet<Schema::IfcCartesianPoint>(0.0, 0.0));
    place.setRefDirection(file.addDoublet<Schema::IfcDirection>(1.0, 0.0));

    auto parent_curve = file.create<Schema::IfcPolynomialCurve>();
    parent_curve.setPosition(place);
    parent_curve.setCoefficientsX(std::vector<double>{0.0, 1.0});
    parent_curve.setCoefficientsY(std::vector<double>{A, B, C});

    auto place2 = file.create<Schema::IfcAxis2Placement2D>();
    place2.setLocation(p);
    place2.setRefDirection(file.addDoublet<Schema::IfcDirection>(sqrt(1 - start_slope * start_slope), start_slope));

    auto curve_segment = file.create<Schema::IfcCurveSegment>();
    curve_segment.setTransition(Schema::IfcTransitionCode::IfcTransitionCode_CONTSAMEGRADIENT);
    curve_segment.setPlacement(place2);
    curve_segment.setSegmentStart(file.addValue<Schema::IfcLengthMeasure>(0.0));
    curve_segment.setSegmentLength(file.addValue<Schema::IfcLengthMeasure>(length));
    curve_segment.setParentCurve(parent_curve);

    // business logic
    double k = (end_slope - start_slope) / length;

    auto design_parameters = file.create<Schema::IfcAlignmentVerticalSegment>();
    design_parameters.setStartDistAlong(p.Coordinates()[0]);
    design_parameters.setHorizontalLength(length);
    design_parameters.setStartHeight(p.Coordinates()[1]);
    design_parameters.setStartGradient(start_slope);
    design_parameters.setEndGradient(end_slope);
    design_parameters.setRadiusOfCurvature(1 / k);
    design_parameters.setPredefinedType(Schema::IfcAlignmentVerticalSegmentTypeEnum::IfcAlignmentVerticalSegmentType_PARABOLICARC);

    auto alignment_segment = file.create<Schema::IfcAlignmentSegment>();
    alignment_segment.setGlobalId(IfcParse::IfcGlobalId());
    alignment_segment.setDesignParameters(design_parameters);

    return {curve_segment, alignment_segment};
}

// creates representations for each IfcAlignmentSegment per CT 4.1.7.1.1.4
// https://standards.buildingsmart.org/IFC/RELEASE/IFC4_3/HTML/concepts/Product_Shape/Product_Geometric_Representation/Alignment_Geometry/Alignment_Geometry_-_Segments/content.html
void create_segment_representations(IfcHierarchyHelper<Schema>& file, const Schema::IfcLocalPlacement& global_placement, const Schema::IfcGeometricRepresentationSubContext& segment_axis_subcontext, std::vector<Schema::IfcSegment>& curve_segments, std::vector<Schema::IfcObjectDefinition>& segments) {
    auto cs_iter = curve_segments.begin();
    auto s_iter = segments.begin();
    for (; cs_iter != curve_segments.end(); cs_iter++, s_iter++) {
        auto& curve_segment = *cs_iter;
        auto alignment_segment = (*s_iter).as<Schema::IfcAlignmentSegment>();

        auto axis_representation = file.create<Schema::IfcShapeRepresentation>();
        axis_representation.setContextOfItems(segment_axis_subcontext);
        axis_representation.setRepresentationIdentifier("Axis");
        axis_representation.setRepresentationType("Segment");
        axis_representation.setItems({curve_segment});

        auto product = file.create<Schema::IfcProductDefinitionShape>();
        product.setRepresentations({axis_representation});

        alignment_segment.setObjectPlacement(global_placement);
        alignment_segment.setRepresentation(product);
    }
}

int main() {
    IfcHierarchyHelper<Schema> file;

    auto project = setup_project(file);

    auto geometric_representation_context = file.getRepresentationContext(std::string("Model")); // creates the representation context if it doesn't already exist

    auto axis_model_representation_subcontext = file.create<Schema::IfcGeometricRepresentationSubContext>();
    axis_model_representation_subcontext.setContextIdentifier("Axis");
    axis_model_representation_subcontext.setContextType("Model");
    axis_model_representation_subcontext.setParentContext(geometric_representation_context);
    axis_model_representation_subcontext.setTargetView(Schema::IfcGeometricProjectionEnum::IfcGeometricProjection_MODEL_VIEW);

    auto global_placement = file.addLocalPlacement();

    //
    // Define horizontal alignment
    //

    // define key points
    // B.1.4 pg 212
    auto pob = file.addDoublet<Schema::IfcCartesianPoint>(500, 2500);                // beginning
    auto pc1 = file.addDoublet<Schema::IfcCartesianPoint>(2142.237995, 1436.014820); // Point of curve (PC),   Curve #1
    auto pt1 = file.addDoublet<Schema::IfcCartesianPoint>(3660.446123, 2050.736173); // Point of tangent (PT), Curve #1
    auto pc2 = file.addDoublet<Schema::IfcCartesianPoint>(4084.115884, 3889.462938); // Point of curve (PC),   Curve #2
    auto pt2 = file.addDoublet<Schema::IfcCartesianPoint>(5469.395067, 4847.566310); // Point of tangent (PT), Curve #2
    auto pc3 = file.addDoublet<Schema::IfcCartesianPoint>(7019.971367, 4638.286073); // Point of curve (PC),   Curve #3
    auto pt3 = file.addDoublet<Schema::IfcCartesianPoint>(7790.932128, 4006.730765); // Point of tangent (PT), Curve #3
    auto poe = file.addDoublet<Schema::IfcCartesianPoint>(8480, 2010);               // ending

    // define tangent runs and curve lengths
    double run_1 = 1956.785654;
    double lc_1 = 1919.222667;
    double run_2 = 1886.905454;
    double lc_2 = 1848.115835;
    double run_3 = 1564.635765;
    double lc_3 = 1049.119737;
    double run_4 = 2112.285084;

    // define curve radii
    double rc_1 = 1000;
    double rc_2 = -1250; // negative radius for curves to the right
    double rc_3 = -950;

    // bearing of tangents
    double angle_1 = to_radian(327.0613);
    double angle_2 = to_radian(77.0247);
    double angle_3 = to_radian(352.3133);
    double angle_4 = to_radian(289.0395);

    // create containers to store the curve segments
    std::vector<Schema::IfcSegment> horizontal_curve_segments;    // geometry
    std::vector<Schema::IfcObjectDefinition> horizontal_segments; // business logic

    //
    // Build the horizontal alignment segments
    //

    // POB to PC1
    auto curve_segment_1 = create_tangent(file, pob, angle_1, run_1);
    horizontal_curve_segments.push_back(curve_segment_1.first);
    horizontal_segments.push_back(curve_segment_1.second);

    // Curve 1
    auto curve_segment_2 = create_hcurve(file, pc1, angle_1, rc_1, lc_1);
    horizontal_curve_segments.push_back(curve_segment_2.first);
    horizontal_segments.push_back(curve_segment_2.second);

    // PT1 to PC2
    auto curve_segment_3 = create_tangent(file, pt1, angle_2, run_2);
    horizontal_curve_segments.push_back(curve_segment_3.first);
    horizontal_segments.push_back(curve_segment_3.second);

    // Curve 2
    auto curve_segment_4 = create_hcurve(file, pc2, angle_2, rc_2, lc_2);
    horizontal_curve_segments.push_back(curve_segment_4.first);
    horizontal_segments.push_back(curve_segment_4.second);

    // PT2 to PC3
    auto curve_segment_5 = create_tangent(file, pt2, angle_3, run_3);
    horizontal_curve_segments.push_back(curve_segment_5.first);
    horizontal_segments.push_back(curve_segment_5.second);

    // Curve 3
    auto curve_segment_6 = create_hcurve(file, pc3, angle_3, rc_3, lc_3);
    horizontal_curve_segments.push_back(curve_segment_6.first);
    horizontal_segments.push_back(curve_segment_6.second);

    // PT3 to POE
    auto curve_segment_7 = create_tangent(file, pt3, angle_4, run_4);
    horizontal_curve_segments.push_back(curve_segment_7.first);
    horizontal_segments.push_back(curve_segment_7.second);

    // Zero-length terminator segment
    auto terminator_segment = create_tangent(file, poe, angle_4, 0.0);
    terminator_segment.first.setTransition(Schema::IfcTransitionCode::IfcTransitionCode_DISCONTINUOUS);
    horizontal_curve_segments.push_back(terminator_segment.first);
    horizontal_segments.push_back(terminator_segment.second);

    //
    // Create the horizontal alignment (IfcAlignmentHorizontal) and nest alignment segments
    //
    auto horizontal_alignment = file.create<Schema::IfcAlignmentHorizontal>();
    horizontal_alignment.setGlobalId(IfcParse::IfcGlobalId());
    horizontal_alignment.setName("Example Alignment");

    auto nests_horizontal_segments = file.create<Schema::IfcRelNests>();
    nests_horizontal_segments.setGlobalId(IfcParse::IfcGlobalId());
    nests_horizontal_segments.setName("Nests horizontal alignment segments with horizontal alignment");
    nests_horizontal_segments.setRelatingObject(horizontal_alignment);
    nests_horizontal_segments.setRelatedObjects(horizontal_segments);
    
    //
    // Create plan view footprint model representation for the horizontal alignment
    //

    // start by defining a composite curve composed of the horizonal curve segments
    auto composite_curve = file.create<Schema::IfcCompositeCurve>();
    composite_curve.setSegments(horizontal_curve_segments);
    composite_curve.setSelfIntersect(false);

    // create the footprint representation
    auto footprint_shape_representation = file.create<Schema::IfcShapeRepresentation>();
    footprint_shape_representation.setContextOfItems(axis_model_representation_subcontext);
    footprint_shape_representation.setRepresentationIdentifier("Footprint");
    footprint_shape_representation.setRepresentationType("Curve2D");
    // the composite curve is a representation item
    footprint_shape_representation.setItems({composite_curve});
    
    //
    // Define vertical profile segments
    //

    // create containers to store the curve segments
    std::vector<Schema::IfcSegment> vertical_curve_segments;    // geometry
    std::vector<Schema::IfcObjectDefinition> vertical_segments; // business logic

    // define key profile points
    auto vpob = file.addDoublet<Schema::IfcCartesianPoint>(0.0, 100.0);     // beginning
    auto vpc1 = file.addDoublet<Schema::IfcCartesianPoint>(1200.0, 121.0);  // Vertical Curve Point (VPC),   Vertical Curve #1
    auto vpt1 = file.addDoublet<Schema::IfcCartesianPoint>(2800.0, 127.0);  // Vertical Curve Tangent (VPT), Vertical Curve #1
    auto vpc2 = file.addDoublet<Schema::IfcCartesianPoint>(4400.0, 111.0);  // Vertical Curve Point (VPC),   Vertical Curve #2
    auto vpt2 = file.addDoublet<Schema::IfcCartesianPoint>(5600.0, 117.0);  // Vertical Curve Tangent (VPT), Vertical Curve #2
    auto vpc3 = file.addDoublet<Schema::IfcCartesianPoint>(6400.0, 133.0);  // Vertical Curve Point (VPC),   Vertical Curve #3
    auto vpt3 = file.addDoublet<Schema::IfcCartesianPoint>(8400.0, 133.0);  // Vertical Curve Tangent (VPT), Vertical Curve #3
    auto vpc4 = file.addDoublet<Schema::IfcCartesianPoint>(9400.0, 113.0);  // Vertical Curve Point (VPC),   Vertical Curve #4
    auto vpt4 = file.addDoublet<Schema::IfcCartesianPoint>(10200.0, 103.0); // Vertical Curve Tangent (VPT), Vertical Curve #4
    auto vpoe = file.addDoublet<Schema::IfcCartesianPoint>(12800.0, 90.0);  // ending

    //
    // Build the vertical alignment segments
    //

    // Grade start to VPC1
    auto vertical_profile_segment_1 = create_gradient(file, vpob, 1.75 / 100, 1200);
    vertical_curve_segments.push_back(vertical_profile_segment_1.first);
    vertical_segments.push_back(vertical_profile_segment_1.second);

    // Vertical Curve 1
    auto vertical_profile_segment_2 = create_vcurve(file, vpc1, 1.75 / 100, -1.0 / 100, 1600);
    vertical_curve_segments.push_back(vertical_profile_segment_2.first);
    vertical_segments.push_back(vertical_profile_segment_2.second);

    // Grade VPT1 to VPC2
    auto vertical_profile_segment_3 = create_gradient(file, vpt1, -1.0 / 100, 1600);
    vertical_curve_segments.push_back(vertical_profile_segment_3.first);
    vertical_segments.push_back(vertical_profile_segment_3.second);

    // Vertical Curve 2
    auto vertical_profile_segment_4 = create_vcurve(file, vpc2, -1.0 / 100, 2.0 / 100, 1200);
    vertical_curve_segments.push_back(vertical_profile_segment_4.first);
    vertical_segments.push_back(vertical_profile_segment_4.second);

    // Grade PVT2 to VPC3
    auto vertical_profile_segment_5 = create_gradient(file, vpt2, 2.0 / 100, 800);
    vertical_curve_segments.push_back(vertical_profile_segment_5.first);
    vertical_segments.push_back(vertical_profile_segment_5.second);

    // Vertical Curve 3
    auto vertical_profile_segment_6 = create_vcurve(file, vpc3, 2.0 / 100, -2.0 / 100, 2000);
    vertical_curve_segments.push_back(vertical_profile_segment_6.first);
    vertical_segments.push_back(vertical_profile_segment_6.second);

    // Grade PVT3 to VPC4
    auto vertical_profile_segment_7 = create_gradient(file, vpt3, -2.0 / 100, 1000);
    vertical_curve_segments.push_back(vertical_profile_segment_7.first);
    vertical_segments.push_back(vertical_profile_segment_7.second);

    // Vertical Curve 4
    auto vertical_profile_segment_8 = create_vcurve(file, vpc4, -2.0 / 100, -0.5 / 100, 800);
    vertical_curve_segments.push_back(vertical_profile_segment_8.first);
    vertical_segments.push_back(vertical_profile_segment_8.second);

    // Grade VPT4 to End
    auto vertical_profile_segment_9 = create_gradient(file, vpt4, -0.5 / 100, 2600);
    vertical_curve_segments.push_back(vertical_profile_segment_9.first);
    vertical_segments.push_back(vertical_profile_segment_9.second);

    // Zero-length terminator
    auto vertical_terminator_segment = create_gradient(file, vpoe, -0.5 / 100, 0.0);
    vertical_terminator_segment.first.setTransition(Schema::IfcTransitionCode::IfcTransitionCode_DISCONTINUOUS);
    vertical_curve_segments.push_back(vertical_terminator_segment.first);
    vertical_segments.push_back(vertical_terminator_segment.second);

    //
    // Create the vertical alignment (IfcAlignmentVertical) and nest alignment segments
    //
    auto vertical_profile = file.create<Schema::IfcAlignmentVertical>();
    vertical_profile.setGlobalId(IfcParse::IfcGlobalId());
    vertical_profile.setName("Example Vertical Profile");

    auto nests_vertical_segments = file.create<Schema::IfcRelNests>();
    nests_vertical_segments.setGlobalId(IfcParse::IfcGlobalId());
    nests_vertical_segments.setName("Nests vertical alignment segments with vertical profile");
    nests_vertical_segments.setRelatingObject(vertical_profile);
    nests_vertical_segments.setRelatedObjects(vertical_segments);

    //
    // Create profile view axis model representation for the vertical profile
    //

    // start by defining a gradient curve composed of the vertical curve segments and associated with the horizontal composite curve
    auto gradient_curve = file.create<Schema::IfcGradientCurve>();
    gradient_curve.setSegments(vertical_curve_segments);
    gradient_curve.setSelfIntersect(false);
    gradient_curve.setBaseCurve(composite_curve);

    // create the axis representation
    auto axis3d_shape_representation = file.create<Schema::IfcShapeRepresentation>();
    axis3d_shape_representation.setContextOfItems(axis_model_representation_subcontext);
    axis3d_shape_representation.setRepresentationIdentifier("Axis");
    axis3d_shape_representation.setRepresentationType("Curve3D");
    // the gradient curve is a representation item
    axis3d_shape_representation.setItems({gradient_curve});

    // create axis representations for each segment
    create_segment_representations(file, global_placement, axis_model_representation_subcontext, horizontal_curve_segments, horizontal_segments);
    create_segment_representations(file, global_placement, axis_model_representation_subcontext, vertical_curve_segments, vertical_segments);

    //
    // Create the IfcAlignment
    //

    // create the alignment product definition
    auto alignment_product = file.create<Schema::IfcProductDefinitionShape>();
    alignment_product.setName("Alignment Product Definition Shape");
    // the alignment has two representations, a plan view footprint and a 3d curve
    alignment_product.setRepresentations({footprint_shape_representation, axis3d_shape_representation});

    // create the alignment
    auto alignment = file.create<Schema::IfcAlignment>();
    alignment.setGlobalId(IfcParse::IfcGlobalId());
    alignment.setName("Example Alignment");
    alignment.setObjectPlacement(global_placement);
    alignment.setRepresentation(alignment_product);

    // Nest the IfcAlignmentHorizontal and IfcAlignmentVertical with the IfcAlignment to complete the business logic
    // 4.1.4.4.1 Alignments nest horizontal and vertical layouts
    // https://standards.buildingsmart.org/IFC/RELEASE/IFC4_3/HTML/concepts/Object_Composition/Nesting/Alignment_Layouts/content.html
    auto nests_alignment_layouts = file.create<Schema::IfcRelNests>();
    nests_alignment_layouts.setGlobalId(IfcParse::IfcGlobalId());
    nests_alignment_layouts.setName("Nest horizontal and vertical alignment layouts with the alignment");
    nests_alignment_layouts.setRelatingObject(alignment);
    nests_alignment_layouts.setRelatedObjects({horizontal_alignment, vertical_profile});
    
    // Define the relationship with the project

    // IFC 4.1.4.1.1 "Every IfcAlignment must be related to IfcProject using the IfcRelAggregates relationship"
    // https://standards.buildingsmart.org/IFC/RELEASE/IFC4_3/HTML/concepts/Object_Composition/Aggregation/Alignment_Aggregation_To_Project/content.html
    // IfcProject <-> IfcRelAggregates <-> IfcAlignment
    auto aggregate_alignments_with_project = file.create<Schema::IfcRelAggregates>();
    aggregate_alignments_with_project.setGlobalId(IfcParse::IfcGlobalId());
    aggregate_alignments_with_project.setName("Alignments in project");
    aggregate_alignments_with_project.setRelatingObject(project);
    aggregate_alignments_with_project.setRelatedObjects({alignment});
    
    // Define the spatial structure of the alignment with respect to the site

    // IFC 4.1.5.1 alignment is referenced in spatial structure of an IfcSpatialElement. In this case IfcSite is the highest level IfcSpatialElement
    // https://standards.buildingsmart.org/IFC/RELEASE/IFC4_3/HTML/concepts/Object_Connectivity/Alignment_Spatial_Reference/content.html
    // IfcSite <-> IfcRelReferencedInSpatialStructure <-> IfcAlignment
    // This means IfcAlignment is not part of the IfcSite (it is not an aggregate component) but instead IfcAlignment is used within
    // the IfcSite by reference. This implies an IfcAlignment can traverse many IfcSite instances within an IfcProject
    std::vector<Schema::IfcSpatialReferenceSelect> list_alignments_referenced_in_site{alignment};

    // this alignment traverse 3 bridge sites.
    for (int i = 1; i <= 3; i++) {
        std::ostringstream os;
        os << "Site of Bridge " << i;
        auto site = file.addSite(project);
        site.setName(os.str());

        std::ostringstream description;
        description << "Alignments referenced into the spatial structure of Bridge Site " << i;

        auto rel_referenced_in_spatial_structure = file.create<Schema::IfcRelReferencedInSpatialStructure>();
        rel_referenced_in_spatial_structure.setGlobalId(IfcParse::IfcGlobalId());
        rel_referenced_in_spatial_structure.setDescription(description.str());
        rel_referenced_in_spatial_structure.setRelatedElements(list_alignments_referenced_in_site);
        rel_referenced_in_spatial_structure.setRelatingStructure(site);
    }

    // That's it - save the model to a file
    std::ofstream ofs("FHWA_Bridge_Geometry_Alignment_Example.ifc");
    ofs << file;
}
