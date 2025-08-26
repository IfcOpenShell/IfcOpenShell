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
Schema::IfcProject* setup_project(IfcHierarchyHelper<Schema>& file) {
    std::vector<std::string> file_description;
    file_description.push_back("ViewDefinition[Alignment-basedReferenceView]");
    file.header().file_description()->setdescription(file_description);

    auto project = file.addProject();
    project->setName(std::string("FHWA Bridge Geometry Manual Example Alignment"));
    project->setDescription(std::string("C++ Example"));

    // set up project units for feet
    // the call to file.addProject() sets up length units as millimeter.
    auto units_in_context = project->UnitsInContext();
    auto units = units_in_context->Units();
    auto begin = units->begin();
    auto iter = begin;
    auto end = units->end();
    for (; iter != end; iter++) {
        auto unit = *iter;
        if (unit->as<Schema::IfcSIUnit>() && unit->as<Schema::IfcSIUnit>()->UnitType() == Schema::IfcUnitEnum::IfcUnit_LENGTHUNIT) {
            auto dimensions = new Schema::IfcDimensionalExponents(1, 0, 0, 0, 0, 0, 0);
            file.addEntity(dimensions);

            auto conversion_factor = new Schema::IfcMeasureWithUnit(new Schema::IfcLengthMeasure(304.80), unit->as<Schema::IfcSIUnit>());
            file.addEntity(conversion_factor);

            auto conversion_based_unit = new Schema::IfcConversionBasedUnit(dimensions, Schema::IfcUnitEnum::IfcUnit_LENGTHUNIT, "FEET", conversion_factor);
            file.addEntity(conversion_based_unit);

            units->remove(unit);                // remove the millimeter unit
            units->push(conversion_based_unit); // add the feet unit
            units_in_context->setUnits(units);  // update the UnitsInContext

            break; // Done!, the length unit was found, so break out of the loop
        }
    }

    return project;
}

// creates geometry and business logic segments for horizontal alignment tangent runs
std::pair<typename Schema::IfcCurveSegment*, typename Schema::IfcAlignmentSegment*> create_tangent(typename Schema::IfcCartesianPoint* p, double dir, double length) {
    // geometry
    auto parent_curve = new Schema::IfcLine(
        new Schema::IfcCartesianPoint(std::vector<double>({0, 0})),
        new Schema::IfcVector(new Schema::IfcDirection(std::vector<double>{1.0, 0.0}), 1.0));

    auto curve_segment = new Schema::IfcCurveSegment(
        Schema::IfcTransitionCode::IfcTransitionCode_CONTSAMEGRADIENT,
        new Schema::IfcAxis2Placement2D(p, new Schema::IfcDirection(std::vector<double>{cos(dir), sin(dir)})),
        new Schema::IfcLengthMeasure(0.0), // start
        new Schema::IfcLengthMeasure(length),
        parent_curve);

    // business logic
    auto design_parameters = new Schema::IfcAlignmentHorizontalSegment(
        boost::none, boost::none, p, dir, 0.0, 0.0, length, boost::none, Schema::IfcAlignmentHorizontalSegmentTypeEnum::IfcAlignmentHorizontalSegmentType_LINE);

    auto alignment_segment = new Schema::IfcAlignmentSegment(
        IfcParse::IfcGlobalId(), nullptr, boost::none, boost::none, boost::none, nullptr, nullptr, design_parameters);

    return {curve_segment, alignment_segment};
}

// creates geometry and business logic segments for horizontal alignment horizonal curves
std::pair<typename Schema::IfcCurveSegment*, typename Schema::IfcAlignmentSegment*> create_hcurve(typename Schema::IfcCartesianPoint* pc, double dir, double radius, double lc) {
    // geometry
    double sign = radius / fabs(radius);
    auto parent_curve = new Schema::IfcCircle(
        new Schema::IfcAxis2Placement2D(new Schema::IfcCartesianPoint(std::vector<double>({0, 0})), new Schema::IfcDirection(std::vector<double>{1, 0})),
        fabs(radius));

    auto curve_segment = new Schema::IfcCurveSegment(
        Schema::IfcTransitionCode::IfcTransitionCode_CONTSAMEGRADIENT,
        new Schema::IfcAxis2Placement2D(pc, new Schema::IfcDirection(std::vector<double>{cos(dir), sin(dir)})),
        new Schema::IfcLengthMeasure(0.0),
        new Schema::IfcLengthMeasure(sign * lc),
        parent_curve);

    // business logic
    auto design_parameters = new Schema::IfcAlignmentHorizontalSegment(boost::none, boost::none, pc, dir, radius, radius, lc, boost::none, Schema::IfcAlignmentHorizontalSegmentTypeEnum::IfcAlignmentHorizontalSegmentType_CIRCULARARC);
    auto alignment_segment = new Schema::IfcAlignmentSegment(IfcParse::IfcGlobalId(), nullptr, boost::none, boost::none, boost::none, nullptr, nullptr, design_parameters);

    return {curve_segment, alignment_segment};
}

// creates geometry and business logic segments for vertical profile gradient runs
std::pair<typename Schema::IfcCurveSegment*, typename Schema::IfcAlignmentSegment*> create_gradient(typename Schema::IfcCartesianPoint* p, double slope, double length) {
    // geometry
    auto parent_curve = new Schema::IfcLine(
        new Schema::IfcCartesianPoint(std::vector<double>({0, 0})),
        new Schema::IfcVector(new Schema::IfcDirection(std::vector<double>{1, 0}), 1.0));

    auto curve_segment = new Schema::IfcCurveSegment(
        Schema::IfcTransitionCode::IfcTransitionCode_CONTSAMEGRADIENT,
        new Schema::IfcAxis2Placement2D(p, new Schema::IfcDirection(std::vector<double>{sqrt(1 - slope * slope), slope})),
        new Schema::IfcLengthMeasure(0.0), // start
        new Schema::IfcLengthMeasure(length),
        parent_curve);

    // business logic
    auto design_parameters = new Schema::IfcAlignmentVerticalSegment(boost::none, boost::none, p->Coordinates()[0], length, p->Coordinates()[1], slope, slope, boost::none, Schema::IfcAlignmentVerticalSegmentTypeEnum::IfcAlignmentVerticalSegmentType_CONSTANTGRADIENT);
    auto alignment_segment = new Schema::IfcAlignmentSegment(IfcParse::IfcGlobalId(), nullptr, boost::none, boost::none, boost::none, nullptr, nullptr, design_parameters);

    return {curve_segment, alignment_segment};
}

// creates geometry and business logic segments for vertical profile parabolic vertical curves
std::pair<typename Schema::IfcCurveSegment*, typename Schema::IfcAlignmentSegment*> create_vcurve(typename Schema::IfcCartesianPoint* p, double start_slope, double end_slope, double length) {
    // geometry
    double A = p->Coordinates()[1];
    double B = start_slope;
    double C = (end_slope - start_slope) / (2 * length);

    auto parent_curve = new Schema::IfcPolynomialCurve(
        new Schema::IfcAxis2Placement2D(new Schema::IfcCartesianPoint(std::vector<double>{0.0, 0.0}), new Schema::IfcDirection(std::vector<double>{1.0, 0.0})),
        std::vector<double>{0.0, 1.0},
        std::vector<double>{A, B, C},
        boost::none);

    auto curve_segment = new Schema::IfcCurveSegment(
        Schema::IfcTransitionCode::IfcTransitionCode_CONTSAMEGRADIENT,
        new Schema::IfcAxis2Placement2D(p, new Schema::IfcDirection(std::vector<double>{sqrt(1 - start_slope * start_slope), start_slope})),
        new Schema::IfcLengthMeasure(0.0),
        new Schema::IfcLengthMeasure(length),
        parent_curve);

    // business logic
    double k = (end_slope - start_slope) / length;
    auto design_parameters = new Schema::IfcAlignmentVerticalSegment(boost::none, boost::none, p->Coordinates()[0], length, p->Coordinates()[1], start_slope, end_slope, 1 / k, Schema::IfcAlignmentVerticalSegmentTypeEnum::IfcAlignmentVerticalSegmentType_PARABOLICARC);
    auto alignment_segment = new Schema::IfcAlignmentSegment(IfcParse::IfcGlobalId(), nullptr, boost::none, boost::none, boost::none, nullptr, nullptr, design_parameters);

    return {curve_segment, alignment_segment};
}

// creates representations for each IfcAlignmentSegment per CT 4.1.7.1.1.4
// https://standards.buildingsmart.org/IFC/RELEASE/IFC4_3/HTML/concepts/Product_Shape/Product_Geometric_Representation/Alignment_Geometry/Alignment_Geometry_-_Segments/content.html
void create_segment_representations(IfcHierarchyHelper<Schema>& file, Schema::IfcLocalPlacement* global_placement, Schema::IfcGeometricRepresentationSubContext* segment_axis_subcontext, typename aggregate_of<typename Schema::IfcSegment>::ptr curve_segments, typename aggregate_of<typename Schema::IfcObjectDefinition>::ptr segments) {
    auto cs_iter = curve_segments->begin();
    auto s_iter = segments->begin();
    for (; cs_iter != curve_segments->end(); cs_iter++, s_iter++) {
        auto curve_segment = *cs_iter;
        auto alignment_segment = (*s_iter)->as<Schema::IfcAlignmentSegment>();

        typename aggregate_of<typename Schema::IfcRepresentationItem>::ptr representation_items(new aggregate_of<typename Schema::IfcRepresentationItem>());
        representation_items->push(curve_segment);

        auto axis_representation = new Schema::IfcShapeRepresentation(segment_axis_subcontext, std::string("Axis"), std::string("Segment"), representation_items);
        file.addEntity(axis_representation);

        typename aggregate_of<typename Schema::IfcRepresentation>::ptr representations(new aggregate_of<typename Schema::IfcRepresentation>());
        representations->push(axis_representation);

        auto product = new Schema::IfcProductDefinitionShape(boost::none, boost::none, representations);
        file.addEntity(product);

        alignment_segment->setObjectPlacement(global_placement);
        alignment_segment->setRepresentation(product);
    }
}

int main() {
    IfcHierarchyHelper<Schema> file;

    auto project = setup_project(file);

    auto geometric_representation_context = file.getRepresentationContext(std::string("Model")); // creates the representation context if it doesn't already exist

    auto axis_model_representation_subcontext = new Schema::IfcGeometricRepresentationSubContext(std::string("Axis"), std::string("Model"), geometric_representation_context, boost::none, Schema::IfcGeometricProjectionEnum::IfcGeometricProjection_MODEL_VIEW, boost::none);
    file.addEntity(axis_model_representation_subcontext);

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
    typename aggregate_of<typename Schema::IfcSegment>::ptr horizontal_curve_segments(new aggregate_of<typename Schema::IfcSegment>());             // geometry
    typename aggregate_of<typename Schema::IfcObjectDefinition>::ptr horizontal_segments(new aggregate_of<typename Schema::IfcObjectDefinition>()); // business logic

    //
    // Build the horizontal alignment segments
    //

    // POB to PC1
    auto curve_segment_1 = create_tangent(pob, angle_1, run_1);
    horizontal_curve_segments->push(curve_segment_1.first);
    horizontal_segments->push(curve_segment_1.second);

    // Curve 1
    auto curve_segment_2 = create_hcurve(pc1, angle_1, rc_1, lc_1);
    horizontal_curve_segments->push(curve_segment_2.first);
    horizontal_segments->push(curve_segment_2.second);

    // PT1 to PC2
    auto curve_segment_3 = create_tangent(pt1, angle_2, run_2);
    horizontal_curve_segments->push(curve_segment_3.first);
    horizontal_segments->push(curve_segment_3.second);

    // Curve 2
    auto curve_segment_4 = create_hcurve(pc2, angle_2, rc_2, lc_2);
    horizontal_curve_segments->push(curve_segment_4.first);
    horizontal_segments->push(curve_segment_4.second);

    // PT2 to PC3
    auto curve_segment_5 = create_tangent(pt2, angle_3, run_3);
    horizontal_curve_segments->push(curve_segment_5.first);
    horizontal_segments->push(curve_segment_5.second);

    // Curve 3
    auto curve_segment_6 = create_hcurve(pc3, angle_3, rc_3, lc_3);
    horizontal_curve_segments->push(curve_segment_6.first);
    horizontal_segments->push(curve_segment_6.second);

    // PT3 to POE
    auto curve_segment_7 = create_tangent(pt3, angle_4, run_4);
    horizontal_curve_segments->push(curve_segment_7.first);
    horizontal_segments->push(curve_segment_7.second);

    // Zero-length terminator segment
    auto terminator_segment = create_tangent(poe, angle_4, 0.0);
    terminator_segment.first->setTransition(Schema::IfcTransitionCode::IfcTransitionCode_DISCONTINUOUS);
    horizontal_curve_segments->push(terminator_segment.first);
    horizontal_segments->push(terminator_segment.second);

    //
    // Create the horizontal alignment (IfcAlignmentHorizontal) and nest alignment segments
    //
    auto horizontal_alignment = new Schema::IfcAlignmentHorizontal(IfcParse::IfcGlobalId(), nullptr, std::string("Horizontal Alignment"), boost::none, boost::none, nullptr, nullptr);
    file.addEntity(horizontal_alignment);

    auto nests_horizontal_segments = new Schema::IfcRelNests(IfcParse::IfcGlobalId(), nullptr, boost::none, std::string("Nests horizontal alignment segments with horizontal alignment"), horizontal_alignment, horizontal_segments);
    file.addEntity(nests_horizontal_segments);

    //
    // Create plan view footprint model representation for the horizontal alignment
    //

    // start by defining a composite curve composed of the horizonal curve segments
    auto composite_curve = new Schema::IfcCompositeCurve(horizontal_curve_segments, false /*not self-intersecting*/);
    file.addEntity(composite_curve);

    // the composite curve is a representation item
    typename aggregate_of<typename Schema::IfcRepresentationItem>::ptr alignment_representation_items(new aggregate_of<typename Schema::IfcRepresentationItem>());
    alignment_representation_items->push(composite_curve);

    // create the footprint representation
    auto footprint_shape_representation = new Schema::IfcShapeRepresentation(axis_model_representation_subcontext, std::string("FootPrint"), std::string("Curve2D"), alignment_representation_items);
    file.addEntity(footprint_shape_representation);

    //
    // Define vertical profile segments
    //

    // create containers to store the curve segments
    typename aggregate_of<typename Schema::IfcSegment>::ptr vertical_curve_segments(new aggregate_of<typename Schema::IfcSegment>());             // geometry
    typename aggregate_of<typename Schema::IfcObjectDefinition>::ptr vertical_segments(new aggregate_of<typename Schema::IfcObjectDefinition>()); // business logic

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
    auto vertical_profile_segment_1 = create_gradient(vpob, 1.75 / 100, 1200);
    vertical_curve_segments->push(vertical_profile_segment_1.first);
    vertical_segments->push(vertical_profile_segment_1.second);

    // Vertical Curve 1
    auto vertical_profile_segment_2 = create_vcurve(vpc1, 1.75 / 100, -1.0 / 100, 1600);
    vertical_curve_segments->push(vertical_profile_segment_2.first);
    vertical_segments->push(vertical_profile_segment_2.second);

    // Grade VPT1 to VPC2
    auto vertical_profile_segment_3 = create_gradient(vpt1, -1.0 / 100, 1600);
    vertical_curve_segments->push(vertical_profile_segment_3.first);
    vertical_segments->push(vertical_profile_segment_3.second);

    // Vertical Curve 2
    auto vertical_profile_segment_4 = create_vcurve(vpc2, -1.0 / 100, 2.0 / 100, 1200);
    vertical_curve_segments->push(vertical_profile_segment_4.first);
    vertical_segments->push(vertical_profile_segment_4.second);

    // Grade PVT2 to VPC3
    auto vertical_profile_segment_5 = create_gradient(vpt2, 2.0 / 100, 800);
    vertical_curve_segments->push(vertical_profile_segment_5.first);
    vertical_segments->push(vertical_profile_segment_5.second);

    // Vertical Curve 3
    auto vertical_profile_segment_6 = create_vcurve(vpc3, 2.0 / 100, -2.0 / 100, 2000);
    vertical_curve_segments->push(vertical_profile_segment_6.first);
    vertical_segments->push(vertical_profile_segment_6.second);

    // Grade PVT3 to VPC4
    auto vertical_profile_segment_7 = create_gradient(vpt3, -2.0 / 100, 1000);
    vertical_curve_segments->push(vertical_profile_segment_7.first);
    vertical_segments->push(vertical_profile_segment_7.second);

    // Vertical Curve 4
    auto vertical_profile_segment_8 = create_vcurve(vpc4, -2.0 / 100, -0.5 / 100, 800);
    vertical_curve_segments->push(vertical_profile_segment_8.first);
    vertical_segments->push(vertical_profile_segment_8.second);

    // Grade VPT4 to End
    auto vertical_profile_segment_9 = create_gradient(vpt4, -0.5 / 100, 2600);
    vertical_curve_segments->push(vertical_profile_segment_9.first);
    vertical_segments->push(vertical_profile_segment_9.second);

    // Zero-length terminator
    auto vertical_terminator_segment = create_gradient(vpoe, -0.5 / 100, 0.0);
    vertical_terminator_segment.first->setTransition(Schema::IfcTransitionCode::IfcTransitionCode_DISCONTINUOUS);
    vertical_curve_segments->push(vertical_terminator_segment.first);
    vertical_segments->push(vertical_terminator_segment.second);

    //
    // Create the vertical alignment (IfcAlignmentVertical) and nest alignment segments
    //
    auto vertical_profile = new Schema::IfcAlignmentVertical(IfcParse::IfcGlobalId(), nullptr, std::string("Vertical Alignment"), boost::none, boost::none, nullptr, nullptr);
    file.addEntity(vertical_profile);

    auto nests_vertical_segments = new Schema::IfcRelNests(IfcParse::IfcGlobalId(), nullptr, boost::none, std::string("Nests vertical alignment segments with vertical alignment"), vertical_profile, vertical_segments);
    file.addEntity(nests_vertical_segments);

    //
    // Create profile view axis model representation for the vertical profile
    //

    // start by defining a gradient curve composed of the vertical curve segments and associated with the horizontal composite curve
    auto gradient_curve = new Schema::IfcGradientCurve(vertical_curve_segments, false, composite_curve, nullptr);
    file.addEntity(gradient_curve);

    // the gradient curve is a representation item
    typename aggregate_of<typename Schema::IfcRepresentationItem>::ptr profile_representation_items(new aggregate_of<typename Schema::IfcRepresentationItem>());
    profile_representation_items->push(gradient_curve);

    // create the axis representation
    auto axis3d_shape_representation = new Schema::IfcShapeRepresentation(axis_model_representation_subcontext, std::string("Axis"), std::string("Curve3D"), profile_representation_items);
    file.addEntity(axis3d_shape_representation);

    // create axis representations for each segment
    create_segment_representations(file, global_placement, axis_model_representation_subcontext, horizontal_curve_segments, horizontal_segments);
    create_segment_representations(file, global_placement, axis_model_representation_subcontext, vertical_curve_segments, vertical_segments);

    //
    // Create the IfcAlignment
    //

    // the alignment has two representations, a plan view footprint and a 3d curve
    typename aggregate_of<typename Schema::IfcRepresentation>::ptr alignment_representations(new aggregate_of<typename Schema::IfcRepresentation>());
    alignment_representations->push(footprint_shape_representation); // 2D footprint
    alignment_representations->push(axis3d_shape_representation);    // 3D curve

    // create the alignment product definition
    auto alignment_product = new Schema::IfcProductDefinitionShape(std::string("Alignment Product Definition Shape"), boost::none, alignment_representations);

    // create the alignment
    auto alignment = new Schema::IfcAlignment(IfcParse::IfcGlobalId(), nullptr, std::string("Example Alignment"), boost::none, boost::none, global_placement, alignment_product, boost::none);
    file.addEntity(alignment);

    // Nest the IfcAlignmentHorizontal and IfcAlignmentVertical with the IfcAlignment to complete the business logic
    // 4.1.4.4.1 Alignments nest horizontal and vertical layouts
    // https://standards.buildingsmart.org/IFC/RELEASE/IFC4_3/HTML/concepts/Object_Composition/Nesting/Alignment_Layouts/content.html
    typename aggregate_of<typename Schema::IfcObjectDefinition>::ptr alignment_layout_list(new aggregate_of<typename Schema::IfcObjectDefinition>());
    alignment_layout_list->push(horizontal_alignment);
    alignment_layout_list->push(vertical_profile);

    auto nests_alignment_layouts = new Schema::IfcRelNests(IfcParse::IfcGlobalId(), nullptr, std::string("Nest horizontal and vertical alignment layouts with the alignment"), boost::none, alignment, alignment_layout_list);
    file.addEntity(nests_alignment_layouts);

    // Define the relationship with the project

    // IFC 4.1.4.1.1 "Every IfcAlignment must be related to IfcProject using the IfcRelAggregates relationship"
    // https://standards.buildingsmart.org/IFC/RELEASE/IFC4_3/HTML/concepts/Object_Composition/Aggregation/Alignment_Aggregation_To_Project/content.html
    // IfcProject <-> IfcRelAggregates <-> IfcAlignment
    typename aggregate_of<typename Schema::IfcObjectDefinition>::ptr list_of_alignments_in_project(new aggregate_of<typename Schema::IfcObjectDefinition>());
    list_of_alignments_in_project->push(alignment);
    auto aggregate_alignments_with_project = new Schema::IfcRelAggregates(IfcParse::IfcGlobalId(), nullptr, std::string("Alignments in project"), boost::none, project, list_of_alignments_in_project);
    file.addEntity(aggregate_alignments_with_project);

    // Define the spatial structure of the alignment with respect to the site

    // IFC 4.1.5.1 alignment is referenced in spatial structure of an IfcSpatialElement. In this case IfcSite is the highest level IfcSpatialElement
    // https://standards.buildingsmart.org/IFC/RELEASE/IFC4_3/HTML/concepts/Object_Connectivity/Alignment_Spatial_Reference/content.html
    // IfcSite <-> IfcRelReferencedInSpatialStructure <-> IfcAlignment
    // This means IfcAlignment is not part of the IfcSite (it is not an aggregate component) but instead IfcAlignment is used within
    // the IfcSite by reference. This implies an IfcAlignment can traverse many IfcSite instances within an IfcProject
    typename Schema::IfcSpatialReferenceSelect::list::ptr list_alignments_referenced_in_site(new Schema::IfcSpatialReferenceSelect::list);
    list_alignments_referenced_in_site->push(alignment);

    // this alignment traverse 3 bridge sites.
    for (int i = 1; i <= 3; i++) {
        std::ostringstream os;
        os << "Site of Bridge " << i;
        auto site = file.addSite(project, nullptr);
        site->setName(os.str());

        std::ostringstream description;
        description << "Alignments referenced into the spatial structure of Bridge Site " << i;

        auto rel_referenced_in_spatial_structure = new Schema::IfcRelReferencedInSpatialStructure(IfcParse::IfcGlobalId(), nullptr, boost::none, description.str(), list_alignments_referenced_in_site, site);
        file.addEntity(rel_referenced_in_spatial_structure);
    }

    // That's it - save the model to a file
    std::ofstream ofs("FHWA_Bridge_Geometry_Alignment_Example.ifc");
    ofs << file;
}
