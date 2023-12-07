// This example illustrates the basic of building an alignment model.
// The alignment is based on "Bridge Geometry Manual", April 2022
// US Department of Transportation, Federal Highway Administration (FHWA)
// https://www.fhwa.dot.gov/bridge/pubs/hif22034.pdf
//
// Sections and page number for this document are cited in the code comments.

// Disable warnings coming from IfcOpenShell
#pragma warning(disable:4018 4267 4250 4984 4985)

#include "../ifcparse/IfcHierarchyHelper.h"
#include "../ifcparse/Ifc4x3_add2.h"

#include <boost/math/constants/constants.hpp>

const double PI = boost::math::constants::pi<double>();
double ToRadian(double deg) { return PI * deg / 180; }

#define Schema Ifc4x3_add2

// creates geometry and business logic segments for horizontal alignment tangent runs
std::pair<typename Schema::IfcCurveSegment*,typename Schema::IfcAlignmentSegment*> create_tangent(typename Schema::IfcCartesianPoint* p,double dir,double length)
{
   // geometry
   auto parent_curve = new Schema::IfcLine(
      new Schema::IfcCartesianPoint(std::vector<double>({0,0})), 
      new Schema::IfcVector(new Schema::IfcDirection(std::vector<double>{1.0, 0.0}), 1.0));

   auto curve_segment = new Schema::IfcCurveSegment(
      Schema::IfcTransitionCode::IfcTransitionCode_CONTSAMEGRADIENT, 
      new Schema::IfcAxis2Placement2D(p, new Schema::IfcDirection(std::vector<double>{cos(dir), sin(dir)})), 
      new Schema::IfcLengthMeasure(0.0), // start
      new Schema::IfcLengthMeasure(length), 
      parent_curve);

   // business logic
   auto design_parameters = new Schema::IfcAlignmentHorizontalSegment(
      boost::none, boost::none, p, dir, 0.0, 0.0, length, boost::none, 
      Schema::IfcAlignmentHorizontalSegmentTypeEnum::IfcAlignmentHorizontalSegmentType_LINE);
  
   auto alignment_segment = new Schema::IfcAlignmentSegment(
      IfcParse::IfcGlobalId(), nullptr, boost::none, boost::none, boost::none, nullptr, nullptr, design_parameters);

   return { curve_segment,alignment_segment };
}

// creates geometry and business logic segments for horizontal alignment horizonal curves
std::pair<typename Schema::IfcCurveSegment*, typename Schema::IfcAlignmentSegment*> create_hcurve(typename Schema::IfcCartesianPoint* pc, typename Schema::IfcCartesianPoint* cc, double dir, double radius,double lc)
{
   // geometry
   double sign = radius / fabs(radius);
   auto parent_curve = new Schema::IfcCircle(
      new Schema::IfcAxis2Placement2D(cc, new Schema::IfcDirection(std::vector<double>{cos(dir - sign*PI / 2), sin(dir - sign*PI / 2)})),
      fabs(radius));
   
   auto curve_segment = new Schema::IfcCurveSegment(
      Schema::IfcTransitionCode::IfcTransitionCode_CONTSAMEGRADIENT,
      new Schema::IfcAxis2Placement2D(new Schema::IfcCartesianPoint(std::vector<double>({ 0,0 })), new Schema::IfcDirection(std::vector<double>{1, 0})),
      new Schema::IfcLengthMeasure(0.0), 
      new Schema::IfcLengthMeasure(sign*lc), 
      parent_curve);

   // business logic
   auto design_parameters = new Schema::IfcAlignmentHorizontalSegment(boost::none, boost::none, pc, dir, radius, radius, lc, boost::none, Schema::IfcAlignmentHorizontalSegmentTypeEnum::IfcAlignmentHorizontalSegmentType_CIRCULARARC);
   auto alignment_segment = new Schema::IfcAlignmentSegment(IfcParse::IfcGlobalId(), nullptr,boost::none, boost::none, boost::none, nullptr, nullptr, design_parameters);

   return { curve_segment,alignment_segment };
}

// creates geometry and business logic segments for vertical profile gradient runs
std::pair<typename Schema::IfcCurveSegment*, typename Schema::IfcAlignmentSegment*> create_gradient(typename Schema::IfcCartesianPoint* p,double slope,double length)
{
   // geometry
   auto l = sqrt(1.0 + slope * slope);
   auto dx = 1.0 / l;
   auto dy = slope / l;   
   
   auto parent_curve = new Schema::IfcLine(
      new Schema::IfcCartesianPoint(std::vector<double>({ 0,p->Coordinates()[1]})),
      new Schema::IfcVector(new Schema::IfcDirection(std::vector<double>{dx,dy}), 1.0));

   auto curve_segment = new Schema::IfcCurveSegment(
      Schema::IfcTransitionCode::IfcTransitionCode_CONTSAMEGRADIENT,
      new Schema::IfcAxis2Placement2D(new Schema::IfcCartesianPoint(std::vector<double>({ 0, 0 })), new Schema::IfcDirection(std::vector<double>{1,0})),
      new Schema::IfcLengthMeasure(0.0), // start
      new Schema::IfcLengthMeasure(length),
      parent_curve);

   // business logic
   auto design_parameters = new Schema::IfcAlignmentVerticalSegment(boost::none, boost::none, p->Coordinates()[0], length, p->Coordinates()[1], slope, slope, boost::none, Schema::IfcAlignmentVerticalSegmentTypeEnum::IfcAlignmentVerticalSegmentType_CONSTANTGRADIENT);
   auto alignment_segment = new Schema::IfcAlignmentSegment(IfcParse::IfcGlobalId(), nullptr, boost::none, boost::none, boost::none, nullptr, nullptr, design_parameters);

   return { curve_segment,alignment_segment };
}

// creates geometry and business logic segments for vertical profile parabolic vertical curves
std::pair<typename Schema::IfcCurveSegment*, typename Schema::IfcAlignmentSegment*> create_vcurve(typename Schema::IfcCartesianPoint* p, double start_slope,double end_slope, double length)
{
   // geometry
   double A = p->Coordinates()[1];
   double B = start_slope;
   double C = (end_slope - start_slope) / (2 * length);
   auto parent_curve_placement = new Schema::IfcAxis2Placement2D(new Schema::IfcCartesianPoint(std::vector<double>{0.0, 0.0}), new Schema::IfcDirection(std::vector<double>{1.0, 0.0}));
   auto parent_curve = new Schema::IfcPolynomialCurve(parent_curve_placement, std::vector<double>{0.0, 1.0}, std::vector<double>{A,B,C}, boost::none);
   auto segment_curve_placement = new Schema::IfcAxis2Placement2D(new Schema::IfcCartesianPoint(std::vector<double>{0.0, 0.0}), new Schema::IfcDirection(std::vector<double>{1.0, 0.0}));
   auto curve_segment = new Schema::IfcCurveSegment(Schema::IfcTransitionCode::IfcTransitionCode_CONTSAMEGRADIENT, segment_curve_placement,
      new Schema::IfcLengthMeasure(p->Coordinates()[0]),
      new Schema::IfcLengthMeasure(length),
      parent_curve);

   // business logic
   double k = (end_slope - start_slope) / length;
   auto design_patameters = new Schema::IfcAlignmentVerticalSegment(boost::none, boost::none, p->Coordinates()[0], length, p->Coordinates()[1], start_slope, end_slope, 1 / k, Schema::IfcAlignmentVerticalSegmentTypeEnum::IfcAlignmentVerticalSegmentType_PARABOLICARC);
   auto alignment_segment = new Schema::IfcAlignmentSegment(IfcParse::IfcGlobalId(), nullptr, boost::none, boost::none, boost::none, nullptr, nullptr, design_patameters);

   return { curve_segment,alignment_segment };
}

int main()
{
   IfcHierarchyHelper<Schema> file;

   std::vector<std::string> file_description;
   std::ostringstream os;
   os << "ViewDefinition[Alignment-basedReferenceView]" << std::ends;
   file_description.push_back(os.str().c_str());
   file.header().file_description().description(file_description);

   auto project = file.addProject();
   project->setName(std::string("FHWA Bridge Geometry Manual Example Alignment"));

   // set up project units for feet
   // the call to file.addProject() sets up length units as millimeter.
   auto units_in_context = project->UnitsInContext();
   auto units = units_in_context->Units();
   auto begin = units->begin();
   auto iter = begin;
   auto end = units->end();
   for (; iter != end; iter++)
   {
      auto unit = *iter;
      if (unit->as<Schema::IfcSIUnit>() && unit->as<Schema::IfcSIUnit>()->UnitType() == Schema::IfcUnitEnum::IfcUnit_LENGTHUNIT)
      {
         auto dimensions = new Schema::IfcDimensionalExponents(1, 0, 0, 0, 0, 0, 0);
         file.addEntity(dimensions);
         
         auto conversion_factor = new Schema::IfcMeasureWithUnit(new Schema::IfcLengthMeasure(304.80), unit->as<Schema::IfcSIUnit>());
         file.addEntity(conversion_factor);

         auto conversion_based_unit = new Schema::IfcConversionBasedUnit(dimensions, Schema::IfcUnitEnum::IfcUnit_LENGTHUNIT, "FEET", conversion_factor);
         file.addEntity(conversion_based_unit);

         units->remove(unit); // remove the millimeter unit
         units->push(conversion_based_unit); // add the feet unit
         units_in_context->setUnits(units); // update the UnitsInContext

         break; // Done!, the length unit was found, so break out of the loop
      }
   }

   auto site = file.addSite(project, nullptr);
   auto local_placement = site->ObjectPlacement();
   if (!local_placement) {
      local_placement = file.addLocalPlacement();
   }

   auto geometric_representation_context = file.getRepresentationContext(std::string("Model")); // creates the representation context if it doesn't already exist
   
   //
   // Define horizontal alignment
   //

   // define key points
   // B.1.4 pg 212
   auto pob = file.addDoublet<Schema::IfcCartesianPoint>(500, 2500); // beginning
   auto pc1 = file.addDoublet<Schema::IfcCartesianPoint>(2142.237995, 1436.014820); // Point of curve (PC), Curve #1
   auto cc1 = file.addDoublet<Schema::IfcCartesianPoint>(2685.979298, 2275.267700); // Center of circle (CC), Curve #1
   auto pt1 = file.addDoublet<Schema::IfcCartesianPoint>(3660.446123, 2050.736173); // Point of tangent (PT), Curve #1
   auto pc2 = file.addDoublet<Schema::IfcCartesianPoint>(4084.115884, 3889.462938);
   auto cc2 = file.addDoublet<Schema::IfcCartesianPoint>(5302.199416, 3608.798529);
   auto pt2 = file.addDoublet<Schema::IfcCartesianPoint>(5469.395067, 4847.566310);
   auto pc3 = file.addDoublet<Schema::IfcCartesianPoint>(7019.971367, 4638.286073);
   auto cc3 = file.addDoublet<Schema::IfcCartesianPoint>(6892.902672, 3696.822560);
   auto pt3 = file.addDoublet<Schema::IfcCartesianPoint>(7790.932128, 4006.730765);
   auto poe = file.addDoublet<Schema::IfcCartesianPoint>(8480, 2010); // ending

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

   // curve delta angles
   // pg 17, Eq 2.16 - 2.19
   double angle_1 = ToRadian(327.0613);
   double angle_2 = ToRadian(77.0247);
   double angle_3 = ToRadian(352.3133);
   double angle_4 = ToRadian(289.0395);

   // geometric representations
   typename aggregate_of<typename Schema::IfcSegment>::ptr horizontal_curve_segments(new aggregate_of<typename Schema::IfcSegment>());
   typename aggregate_of<typename Schema::IfcObjectDefinition>::ptr horizontal_segments(new aggregate_of<typename Schema::IfcObjectDefinition>());

   // POB to PC1
   auto curve_segment_1 = create_tangent(pob, angle_1, run_1);
   horizontal_curve_segments->push(curve_segment_1.first);
   horizontal_segments->push(curve_segment_1.second);

   // Curve 1
   auto curve_segment_2 = create_hcurve(pc1, cc1,angle_1,rc_1,lc_1);
   horizontal_curve_segments->push(curve_segment_2.first);
   horizontal_segments->push(curve_segment_2.second);

   // PT1 to PC2
   auto curve_segment_3 = create_tangent(pt1, angle_2, run_2);
   horizontal_curve_segments->push(curve_segment_3.first);
   horizontal_segments->push(curve_segment_3.second);

   // Curve 2
   auto curve_segment_4 = create_hcurve(pc2, cc2, angle_2, rc_2, lc_2);
   horizontal_curve_segments->push(curve_segment_4.first);
   horizontal_segments->push(curve_segment_4.second);

   // PT2 to PC3
   auto curve_segment_5 = create_tangent(pt2, angle_3, run_3);
   horizontal_curve_segments->push(curve_segment_5.first);
   horizontal_segments->push(curve_segment_5.second);

   // Curve 3
   auto curve_segment_6 = create_hcurve(pc3, cc3, angle_3, rc_3, lc_3);
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

   // create plan view footprint model representation for the horizontal alignment
   
   // start by defining a composite curve composed of the horizonal curve segments
   auto composite_curve = new Schema::IfcCompositeCurve(horizontal_curve_segments, false /*not self-intersecting*/);
   file.addEntity(composite_curve);

   // the composite curve is a representation item
   typename aggregate_of<typename Schema::IfcRepresentationItem>::ptr alignment_representation_items(new aggregate_of<typename Schema::IfcRepresentationItem>());
   alignment_representation_items->push(composite_curve);

   // create the footprint representation subcontext for CT 4.1.7.1.1.2 Alignment Geometry - Horizontal and Vertical
   auto footprint_representation_subcontext = new Schema::IfcGeometricRepresentationSubContext(std::string("FootPrint"), std::string("Model"), geometric_representation_context, boost::none, Schema::IfcGeometricProjectionEnum::IfcGeometricProjection_MODEL_VIEW, boost::none);
   file.addEntity(footprint_representation_subcontext);

   // create the footprint representation
   auto footprint_shape_representation = new Schema::IfcShapeRepresentation(footprint_representation_subcontext, std::string("FootPrint"), std::string("Curve2D"), alignment_representation_items);
   file.addEntity(footprint_shape_representation);

   auto horizontal_alignment = new Schema::IfcAlignmentHorizontal(IfcParse::IfcGlobalId(), nullptr, std::string("Horizontal Alignment"), boost::none, boost::none, nullptr, nullptr);
   file.addEntity(horizontal_alignment);

   // for the business logic, nest the individual horizontal alignment segment with the alignment
   auto nests_horizontal_segments = new Schema::IfcRelNests(IfcParse::IfcGlobalId(), nullptr, boost::none, std::string("Nests horizontal alignment segments with horizontal alignment"), horizontal_alignment, horizontal_segments);
   file.addEntity(nests_horizontal_segments);
   
   //
   // Define vertical profile segments
   //

   typename aggregate_of<typename Schema::IfcSegment>::ptr vertical_curve_segments(new aggregate_of<typename Schema::IfcSegment>());
   typename aggregate_of<typename Schema::IfcObjectDefinition>::ptr vertical_segments(new aggregate_of<typename Schema::IfcObjectDefinition>());

   // define key profile points
   auto vpob = file.addDoublet<Schema::IfcCartesianPoint>(0.0, 100.0); // beginning
   auto vpc1 = file.addDoublet<Schema::IfcCartesianPoint>(1200.0, 121.0); // Vertical Curve Point (VPC), Vertical Curve #1
   auto vpt1 = file.addDoublet<Schema::IfcCartesianPoint>(2800.0, 127.0); // Vertical Curve Tangent (VPT), Vertical Curve #1
   auto vpc2 = file.addDoublet<Schema::IfcCartesianPoint>(4400.0, 111.0);
   auto vpt2 = file.addDoublet<Schema::IfcCartesianPoint>(5600.0, 117.0);
   auto vpc3 = file.addDoublet<Schema::IfcCartesianPoint>(6400.0, 133.0);
   auto vpt3 = file.addDoublet<Schema::IfcCartesianPoint>(8400.0, 133.0);
   auto vpc4 = file.addDoublet<Schema::IfcCartesianPoint>(9400.0, 113.0);
   auto vpt4 = file.addDoublet<Schema::IfcCartesianPoint>(10200.0, 103.0);
   auto vpoe = file.addDoublet<Schema::IfcCartesianPoint>(12800.0, 90.0); // ending

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
   vertical_curve_segments->push(vertical_terminator_segment.first);
   vertical_segments->push(vertical_terminator_segment.second);

   // create profile view axis model representation for the vertical profile

   // start by defining a gradient curve composed of the vertical curve segments and associated with the horizontal composite curve
   auto gradient_curve = new Schema::IfcGradientCurve(vertical_curve_segments, false, composite_curve, nullptr);

   // the gradient curve is a representation item
   typename aggregate_of<typename Schema::IfcRepresentationItem>::ptr profile_representation_items(new aggregate_of<typename Schema::IfcRepresentationItem>());
   profile_representation_items->push(gradient_curve);

   // create the axis representation subcontext
   auto axis_representation_subcontext = new Schema::IfcGeometricRepresentationSubContext(std::string("Axis"), std::string("Model"), geometric_representation_context, boost::none, Schema::IfcGeometricProjectionEnum::IfcGeometricProjection_MODEL_VIEW, boost::none);
   file.addEntity(axis_representation_subcontext);

   // create the axis representation
   auto axis3d_shape_representation = new Schema::IfcShapeRepresentation(axis_representation_subcontext, std::string("Axis"), std::string("Curve3D"), profile_representation_items);
   file.addEntity(axis3d_shape_representation);

   auto vertical_profile = new Schema::IfcAlignmentVertical(IfcParse::IfcGlobalId(), nullptr, std::string("Vertical Alignment"), boost::none, boost::none, nullptr, nullptr);
   file.addEntity(vertical_profile);

   // for the business logic, nest the individual vertical curve segments with the vertical alignment
   auto nests_vertical_segments = new Schema::IfcRelNests(IfcParse::IfcGlobalId(), nullptr, boost::none, std::string("Nests vertical alignment segments with vertical alignment"), vertical_profile, vertical_segments);
   file.addEntity(nests_vertical_segments);

   // the alignment has two representations, a plan view footprint and a 3d curve
   typename aggregate_of<typename Schema::IfcRepresentation>::ptr alignment_representations(new aggregate_of<typename Schema::IfcRepresentation>());
   alignment_representations->push(footprint_shape_representation); // 2D footprint
   alignment_representations->push(axis3d_shape_representation);    // 3D curve

   // create the alignment
   auto alignment_product = new Schema::IfcProductDefinitionShape(std::string("Alignment Product Definition Shape"), boost::none, alignment_representations);
   
   auto alignment = new Schema::IfcAlignment(IfcParse::IfcGlobalId(), nullptr, std::string("Example Alignment"), boost::none, boost::none, local_placement, alignment_product, boost::none);
   file.addEntity(alignment);

   file.relatePlacements(site, horizontal_alignment);
   file.relatePlacements(site, vertical_profile);
   file.relatePlacements(site, alignment);

   // 4.1.4.4.1 Alignments nest horizontal and vertical layouts
   // https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/concepts/Object_Composition/Nesting/Alignment_Layouts/content.html
   typename aggregate_of<typename Schema::IfcObjectDefinition>::ptr alignment_layout_list(new aggregate_of<typename Schema::IfcObjectDefinition>());
   alignment_layout_list->push(horizontal_alignment);
   alignment_layout_list->push(vertical_profile);

   auto nests_alignment_layouts = new Schema::IfcRelNests(IfcParse::IfcGlobalId(), nullptr, std::string("Nest horizontal and vertical alignment layouts with the alignment"), boost::none, alignment, alignment_layout_list);
   file.addEntity(nests_alignment_layouts);

   // IFC 4.1.4.1.1 "Every IfcAlignment must be related to IfcProject using the IfcRelAggregates relationship"
   // https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/concepts/Object_Composition/Aggregation/Alignment_Aggregation_To_Project/content.html
   // IfcProject <-> IfcRelAggregates <-> IfcAlignment
   typename aggregate_of<typename Schema::IfcObjectDefinition>::ptr list_of_alignments_in_project(new aggregate_of<typename Schema::IfcObjectDefinition>());
   list_of_alignments_in_project->push(alignment);
   auto aggregate_alignments_with_project = new Schema::IfcRelAggregates(IfcParse::IfcGlobalId(), nullptr, std::string("Alignments in project"), boost::none, project, list_of_alignments_in_project);
   file.addEntity(aggregate_alignments_with_project);

   // IFC 4.1.5.1 alignment is referenced in spatial structure of an IfcSpatialElement. In this case IfcSite is the highest level IfcSpatialElement
   // https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/concepts/Object_Connectivity/Alignment_Spatial_Reference/content.html
   // IfcSite <-> IfcRelReferencedInSpatialStructure <-> IfcAlignment
   // This means IfcAlignment is not part of the IfcSite (it is not an aggregate component) but instead IfcAlignment is used within
   // the IfcSite by reference. This implies an IfcAlignment can traverse many IfcSite instances within an IfcProject
   typename Schema::IfcSpatialReferenceSelect::list::ptr list_alignments_referenced_in_site(new Schema::IfcSpatialReferenceSelect::list);
   list_alignments_referenced_in_site->push(alignment);
   auto rel_referenced_in_spatial_structure = new Schema::IfcRelReferencedInSpatialStructure(IfcParse::IfcGlobalId(), nullptr, boost::none, boost::none, list_alignments_referenced_in_site, site);
   file.addEntity(rel_referenced_in_spatial_structure);

   std::ofstream ofs("FHWA_Bridge_Geometry_Alignment_Example.ifc");
   ofs << file;
}
