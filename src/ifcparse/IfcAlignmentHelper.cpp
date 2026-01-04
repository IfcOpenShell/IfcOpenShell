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

/********************************************************************************
 *                                                                              *
 * Implements convenience functions for alignments                              *
 *                                                                              *
 ********************************************************************************/


#include "IfcAlignmentHelper.h"

#include <boost/math/constants/constants.hpp>
// @todo use std::numbers::pi when upgrading to C++ 20
static const double PI = boost::math::constants::pi<double>();

#include <boost/math/quadrature/trapezoidal.hpp>

#ifdef HAS_SCHEMA_4x3_add2

// sets the segment name like ("H1" for horizontal, "V1" for vertical, "C1" for cant)
void _name_segments(const char* prefix, std::vector<Ifc4x3_add2::IfcObjectDefinition>& segments) {
    unsigned idx = 1;
    for (auto& segment : segments) {
        std::ostringstream os;
        os << prefix << idx++;
        segment.setName(os.str());
    }
}

// creates representations for each IfcAlignmentSegment per CT 4.1.7.1.1.4
// https://standards.buildingsmart.org/IFC/RELEASE/IFC4_3/HTML/concepts/Product_Shape/Product_Geometric_Representation/Alignment_Geometry/Alignment_Geometry_-_Segments/content.html
void _createSegmentRepresentations(IfcHierarchyHelper<Ifc4x3_add2>& file, Ifc4x3_add2::IfcLocalPlacement global_placement, Ifc4x3_add2::IfcGeometricRepresentationSubContext segment_axis_subcontext, std::vector<Ifc4x3_add2::IfcSegment>& curve_segments, std::vector<Ifc4x3_add2::IfcObjectDefinition>& segments) {
    auto cs_iter = curve_segments.begin();
    auto s_iter = segments.begin();
    for (; cs_iter != curve_segments.end(); cs_iter++, s_iter++) {
        auto curve_segment = *cs_iter;
        auto alignment_segment = (s_iter)->as<Ifc4x3_add2::IfcAlignmentSegment>();

        auto axis_representation = file.create<Ifc4x3_add2::IfcShapeRepresentation>();
        axis_representation.setContextOfItems(segment_axis_subcontext);
        axis_representation.setRepresentationIdentifier("Axis");
        axis_representation.setRepresentationType("Segment");
        axis_representation.setItems(std::vector<Ifc4x3_add2::IfcRepresentationItem>{curve_segment});

        auto product = file.create<Ifc4x3_add2::IfcProductDefinitionShape>();
        product.setRepresentations(std::vector<Ifc4x3_add2::IfcRepresentation>{axis_representation});

        alignment_segment.setObjectPlacement(global_placement);
        alignment_segment.setRepresentation(product);
    }
}

// creates a horizontal alignment using a vector of PI points and curve radii
// returns a list of object definitions, curve segments, and a composite curve
std::tuple<std::vector<Ifc4x3_add2::IfcObjectDefinition>, std::vector<Ifc4x3_add2::IfcSegment>, Ifc4x3_add2::IfcCompositeCurve> _createHorizontalAlignment(IfcHierarchyHelper<Ifc4x3_add2>& file, const std::vector<std::pair<double, double>>& points, const std::vector<double>& radii,bool include_geometry) {
    std::vector<Ifc4x3_add2::IfcObjectDefinition> horizontal_segments; // business logic
    std::vector<Ifc4x3_add2::IfcSegment> horizontal_curve_segments;    // geometry

    auto point_iter = points.begin();
    double xBT, yBT, xPI, yPI;

    boost::tie(xBT, yBT) = *point_iter;

    point_iter++;
    boost::tie(xPI, yPI) = *point_iter;

    double xFT, yFT;
    for (auto radius : radii) {
        // back tangent
        auto dxBT = xPI - xBT;
        auto dyBT = yPI - yBT;
        auto angleBT = atan2(dyBT, dxBT);
        auto lengthBT = sqrt(dxBT * dxBT + dyBT * dyBT);

        // forward tangent
        point_iter++;
        std::tie(xFT, yFT) = *point_iter;
        auto dxFT = xFT - xPI;
        auto dyFT = yFT - yPI;
        auto angleFT = atan2(dyFT, dxFT);

        auto delta = angleFT - angleBT;

        auto tangent = fabs(radius * tan(delta / 2));

        auto lc = fabs(radius * delta);

        radius *= delta / fabs(delta);

        auto xPC = xPI - tangent * cos(angleBT);
        auto yPC = yPI - tangent * sin(angleBT);

        auto xPT = xPI + tangent * cos(angleFT);
        auto yPT = yPI + tangent * sin(angleFT);

        auto tangent_run = lengthBT - tangent;

        // create back tangent run
        {
            auto pt = file.addDoublet<Ifc4x3_add2::IfcCartesianPoint>(xBT, yBT);
            auto design_parameters = file.create<Ifc4x3_add2::IfcAlignmentHorizontalSegment>();
            design_parameters.setStartPoint(pt);
            design_parameters.setStartDirection(angleBT);
            design_parameters.setStartRadiusOfCurvature(0.0);
            design_parameters.setEndRadiusOfCurvature(0.0);
            design_parameters.setSegmentLength(tangent_run);
            design_parameters.setPredefinedType(Ifc4x3_add2::IfcAlignmentHorizontalSegmentTypeEnum::IfcAlignmentHorizontalSegmentType_LINE);

            auto alignment_segment = file.create<Ifc4x3_add2::IfcAlignmentSegment>();
            alignment_segment.setGlobalId(IfcParse::IfcGlobalId());
            alignment_segment.setDesignParameters(design_parameters);

            horizontal_segments.push_back(alignment_segment);

            if (include_geometry) {
                horizontal_curve_segments.push_back(mapAlignmentHorizontalSegment(file, design_parameters).first);
            }
        }

        // create circular curve
        {
            auto pc = file.addDoublet<Ifc4x3_add2::IfcCartesianPoint>(xPC, yPC);
            auto design_parameters = file.create<Ifc4x3_add2::IfcAlignmentHorizontalSegment>();
            design_parameters.setStartPoint(pc);
            design_parameters.setStartDirection(angleBT);
            design_parameters.setStartRadiusOfCurvature(radius);
            design_parameters.setEndRadiusOfCurvature(radius);
            design_parameters.setSegmentLength(lc);
            design_parameters.setPredefinedType(Ifc4x3_add2::IfcAlignmentHorizontalSegmentTypeEnum::IfcAlignmentHorizontalSegmentType_CIRCULARARC);

            auto alignment_segment = file.create<Ifc4x3_add2::IfcAlignmentSegment>();
            alignment_segment.setGlobalId(IfcParse::IfcGlobalId());
            alignment_segment.setDesignParameters(design_parameters);

            horizontal_segments.push_back(alignment_segment);

            if (include_geometry) {
                horizontal_curve_segments.push_back(mapAlignmentHorizontalSegment(file, design_parameters).first);
            }
        }

        xBT = xPT;
        yBT = yPT;
        xPI = xFT;
        yPI = yFT;
    }

    // create last tangent run
    auto dx = xPI - xBT;
    auto dy = yPI - yBT;
    auto angleBT = atan2(dy, dx);
    auto tangent_run = sqrt(dx * dx + dy * dy);
    auto pt = file.addDoublet<Ifc4x3_add2::IfcCartesianPoint>(xBT, yBT);
    auto design_parameters = file.create<Ifc4x3_add2::IfcAlignmentHorizontalSegment>();
    design_parameters.setStartPoint(pt);
    design_parameters.setStartDirection(angleBT);
    design_parameters.setStartRadiusOfCurvature(0);
    design_parameters.setEndRadiusOfCurvature(0);
    design_parameters.setSegmentLength(tangent_run);
    design_parameters.setPredefinedType(Ifc4x3_add2::IfcAlignmentHorizontalSegmentTypeEnum::IfcAlignmentHorizontalSegmentType_LINE);

    auto alignment_segment = file.create<Ifc4x3_add2::IfcAlignmentSegment>();
    alignment_segment.setGlobalId(IfcParse::IfcGlobalId());
    alignment_segment.setDesignParameters(design_parameters);

    horizontal_segments.push_back(alignment_segment);

    if (include_geometry) {
        horizontal_curve_segments.push_back(mapAlignmentHorizontalSegment(file, design_parameters).first);
    }

    // create zero length terminator segment
    auto poe = file.addDoublet<Ifc4x3_add2::IfcCartesianPoint>(xPI, yPI);
    design_parameters = file.create<Ifc4x3_add2::IfcAlignmentHorizontalSegment>();
    design_parameters.setStartPoint(poe);
    design_parameters.setStartDirection(angleBT);
    design_parameters.setStartRadiusOfCurvature(0);
    design_parameters.setEndRadiusOfCurvature(0);
    design_parameters.setSegmentLength(0.0);
    design_parameters.setPredefinedType(Ifc4x3_add2::IfcAlignmentHorizontalSegmentTypeEnum::IfcAlignmentHorizontalSegmentType_LINE);
    
    alignment_segment = file.create<Ifc4x3_add2::IfcAlignmentSegment>();
    alignment_segment.setGlobalId(IfcParse::IfcGlobalId());
    alignment_segment.setDesignParameters(design_parameters);
    
    horizontal_segments.push_back(alignment_segment);
    if (include_geometry) {
        auto segment = mapAlignmentHorizontalSegment(file, design_parameters).first;
        segment.setTransition(Ifc4x3_add2::IfcTransitionCode::IfcTransitionCode_DISCONTINUOUS);
        horizontal_curve_segments.push_back(segment);
    }

    Ifc4x3_add2::IfcCompositeCurve composite_curve;
    if (include_geometry) {
        composite_curve = file.create<Ifc4x3_add2::IfcCompositeCurve>();
        composite_curve.setSegments(horizontal_curve_segments);
        composite_curve.setSelfIntersect(false);
    }

    return {horizontal_segments, horizontal_curve_segments, composite_curve};
}

Ifc4x3_add2::IfcAlignment addHorizontalAlignment(IfcHierarchyHelper<Ifc4x3_add2>& file, const std::string& alignment_name, const std::vector<std::pair<double, double>>& points, const std::vector<double>& radii,bool include_geometry) {

    auto [horizontal_segments, horizontal_curve_segments, composite_curve] = _createHorizontalAlignment(file, points, radii, include_geometry);
    _name_segments("H", horizontal_segments);

    //
    // Create the horizontal alignment (IfcAlignmentHorizontal) and nest alignment segments
    //
    auto horizontal_alignment = file.create<Ifc4x3_add2::IfcAlignmentHorizontal>();
    horizontal_alignment.setGlobalId(IfcParse::IfcGlobalId());
    horizontal_alignment.setName(alignment_name + " - Horizontal");

    auto nests_horizontal_segments = file.create<Ifc4x3_add2::IfcRelNests>();
    nests_horizontal_segments.setGlobalId(IfcParse::IfcGlobalId());
    nests_horizontal_segments.setName("Nests horizontal alignment segments with horizontal alignment");
    nests_horizontal_segments.setRelatingObject(horizontal_alignment);
    nests_horizontal_segments.setRelatedObjects(horizontal_segments);

    //
    // Create geometric representation
    //
    Ifc4x3_add2::IfcLocalPlacement placement;
    Ifc4x3_add2::IfcProductDefinitionShape product_definition_shape;
    if (include_geometry) { 
       // create the footprint representation
       auto axis_model_representation_subcontext = file.getRepresentationSubContext("Axis", "Model");
       auto footprint_shape_representation = file.create<Ifc4x3_add2::IfcShapeRepresentation>();
       footprint_shape_representation.setContextOfItems(axis_model_representation_subcontext);
       footprint_shape_representation.setRepresentationIdentifier("FootPrint");
       footprint_shape_representation.setRepresentationType("Curve2D");
       footprint_shape_representation.setItems(std::vector<Ifc4x3_add2::IfcRepresentationItem>{composite_curve});
       
       placement = file.addLocalPlacement();
       // the alignment has a plan view footprint representation
       // create the alignment product definition
       product_definition_shape = file.create<Ifc4x3_add2::IfcProductDefinitionShape>();
       product_definition_shape.setName("Alignment Product Definition Shape");
       product_definition_shape.setRepresentations(std::vector<Ifc4x3_add2::IfcRepresentation>{footprint_shape_representation});

       // create representations for each segment
       _createSegmentRepresentations(file, placement, axis_model_representation_subcontext, horizontal_curve_segments, horizontal_segments);
    }

    // create the alignment
    auto alignment = file.create<Ifc4x3_add2::IfcAlignment>();
    alignment.setGlobalId(IfcParse::IfcGlobalId());
    alignment.setName(alignment_name);
    alignment.setObjectPlacement(placement);
    alignment.setRepresentation(product_definition_shape);    

    return alignment;
}

std::tuple<typename std::vector<Ifc4x3_add2::IfcObjectDefinition>&, typename std::vector<Ifc4x3_add2::IfcSegment>&, Ifc4x3_add2::IfcGradientCurve> _createVerticalAlignment(IfcHierarchyHelper<Ifc4x3_add2>& file, Ifc4x3_add2::IfcCompositeCurve composite_curve,const std::vector<std::pair<double, double>>& vpoints, const std::vector<double>& vclengths, bool include_geometry) {
    std::vector<Ifc4x3_add2::IfcObjectDefinition> vertical_segments; // business logic
    std::vector<Ifc4x3_add2::IfcSegment> vertical_curve_segments;    // geometry

    auto point_iter = vpoints.begin();
    double xPBG, yPBG, xPVI, yPVI;

    boost::tie(xPBG, yPBG) = *point_iter;

    point_iter++;
    boost::tie(xPVI, yPVI) = *point_iter;

    double xPFG, yPFG;
    for (auto length : vclengths) {
        // back gradient
        auto dxBG = xPVI - xPBG;
        auto dyBG = yPVI - yPBG;
        auto start_slope = tan(atan2(dyBG,dxBG));

        // forward gradient
        point_iter++;
        std::tie(xPFG, yPFG) = *point_iter;
        auto dxFG = xPFG - xPVI;
        auto dyFG = yPFG - yPVI;
        auto end_slope = tan(atan2(dyFG,dxFG));

        double xEVC = xPVI + length / 2;
        double yEVC = yPVI + end_slope * length / 2;

        // create gradient
        {
            auto gradient_length = dxBG - length/2;
            auto design_parameters = file.create<Ifc4x3_add2::IfcAlignmentVerticalSegment>();
            design_parameters.setStartDistAlong(xPBG);
            design_parameters.setHorizontalLength(gradient_length);
            design_parameters.setStartHeight(yPBG);
            design_parameters.setStartGradient(start_slope);
            design_parameters.setEndGradient(start_slope);
            design_parameters.setPredefinedType(Ifc4x3_add2::IfcAlignmentVerticalSegmentTypeEnum::IfcAlignmentVerticalSegmentType_CONSTANTGRADIENT);

            auto alignment_segment = file.create<Ifc4x3_add2::IfcAlignmentSegment>();
            alignment_segment.setGlobalId(IfcParse::IfcGlobalId());
            alignment_segment.setDesignParameters(design_parameters);

            vertical_segments.push_back(alignment_segment);
            if (include_geometry) {
               vertical_curve_segments.push_back(mapAlignmentVerticalSegment(file, design_parameters).first);
            }
        }

        // create vertical curve
        {
            double k = (end_slope - start_slope) / length;
            double xBVC = xPVI - length / 2;
            double yBVC = yPVI - start_slope * length / 2;

            auto design_parameters = file.create<Ifc4x3_add2::IfcAlignmentVerticalSegment>();
            design_parameters.setStartDistAlong(xBVC);
            design_parameters.setHorizontalLength(length);
            design_parameters.setStartHeight(yBVC);
            design_parameters.setStartGradient(start_slope);
            design_parameters.setEndGradient(end_slope);
            design_parameters.setRadiusOfCurvature(1/k);
            design_parameters.setPredefinedType(Ifc4x3_add2::IfcAlignmentVerticalSegmentTypeEnum::IfcAlignmentVerticalSegmentType_PARABOLICARC);

            auto alignment_segment = file.create<Ifc4x3_add2::IfcAlignmentSegment>();
            alignment_segment.setGlobalId(IfcParse::IfcGlobalId());
            alignment_segment.setDesignParameters(design_parameters);

            vertical_segments.push_back(alignment_segment);
            if (include_geometry) {
                vertical_curve_segments.push_back(mapAlignmentVerticalSegment(file, design_parameters).first);
            }
        }

        xPBG = xEVC;
        yPBG = yEVC;
        xPVI = xPFG;
        yPVI = yPFG;
    }

    // create last tangent run
    auto dx = xPVI - xPBG;
    auto dy = yPVI - yPBG;
    auto slope = tan(atan2(dy,dx));
    auto gradient_length = dx;

    auto design_parameters = file.create<Ifc4x3_add2::IfcAlignmentVerticalSegment>();
    design_parameters.setStartDistAlong(xPBG);
    design_parameters.setHorizontalLength(gradient_length);
    design_parameters.setStartHeight(yPBG);
    design_parameters.setStartGradient(slope);
    design_parameters.setEndGradient(slope);
    design_parameters.setPredefinedType(Ifc4x3_add2::IfcAlignmentVerticalSegmentTypeEnum::IfcAlignmentVerticalSegmentType_CONSTANTGRADIENT);

    auto alignment_segment = file.create<Ifc4x3_add2::IfcAlignmentSegment>();
    alignment_segment.setGlobalId(IfcParse::IfcGlobalId());
    alignment_segment.setDesignParameters(design_parameters);

    vertical_segments.push_back(alignment_segment);
    if (include_geometry) {
        vertical_curve_segments.push_back(mapAlignmentVerticalSegment(file, design_parameters).first);
    }

    // create zero length terminator segment
    design_parameters = file.create<Ifc4x3_add2::IfcAlignmentVerticalSegment>();
    design_parameters.setStartDistAlong(xPVI);
    design_parameters.setHorizontalLength(0.);
    design_parameters.setStartHeight(yPVI);
    design_parameters.setStartGradient(slope);
    design_parameters.setEndGradient(slope);
    design_parameters.setPredefinedType(Ifc4x3_add2::IfcAlignmentVerticalSegmentTypeEnum::IfcAlignmentVerticalSegmentType_CONSTANTGRADIENT);

    alignment_segment = file.create<Ifc4x3_add2::IfcAlignmentSegment>();
    alignment_segment.setGlobalId(IfcParse::IfcGlobalId());
    alignment_segment.setDesignParameters(design_parameters);

    vertical_segments.push_back(alignment_segment);
    if (include_geometry) {
        auto segment = mapAlignmentVerticalSegment(file, design_parameters).first;
        segment.setTransition(Ifc4x3_add2::IfcTransitionCode::IfcTransitionCode_DISCONTINUOUS);
        vertical_curve_segments.push_back(segment);
    }

    Ifc4x3_add2::IfcGradientCurve gradient_curve;
    if (include_geometry) {
        gradient_curve = file.create<Ifc4x3_add2::IfcGradientCurve>();
        gradient_curve.setSegments(vertical_curve_segments);
        gradient_curve.setSelfIntersect(false);
        gradient_curve.setBaseCurve(composite_curve);
    }

    return {vertical_segments, vertical_curve_segments, gradient_curve};
}

Ifc4x3_add2::IfcAlignment addAlignment(IfcHierarchyHelper<Ifc4x3_add2>& file, const std::string& alignment_name, const std::vector<std::pair<double, double>>& points, const std::vector<double>& radii, const std::vector<std::pair<double, double>>& vpoints, const std::vector<double>& vclengths,bool include_geometry) {
    auto [horizontal_segments, horizontal_curve_segments, composite_curve] = _createHorizontalAlignment(file, points, radii, include_geometry);
    auto [vertical_segments, vertical_curve_segments, gradient_curve] = _createVerticalAlignment(file, composite_curve, vpoints, vclengths, include_geometry);

    _name_segments("H", horizontal_segments);
    _name_segments("V", vertical_segments);

    //
    // Create the horizontal alignment (IfcAlignmentHorizontal) and nest the segments
    //
    auto horizontal_alignment = file.create<Ifc4x3_add2::IfcAlignmentHorizontal>();
    horizontal_alignment.setGlobalId(IfcParse::IfcGlobalId());
    horizontal_alignment.setName(alignment_name + " - Horizontal");

    auto nests_horizontal_segments = file.create<Ifc4x3_add2::IfcRelNests>();
    nests_horizontal_segments.setGlobalId(IfcParse::IfcGlobalId());
    nests_horizontal_segments.setName("Nests horizontal alignment segments with horizontal alignment");
    nests_horizontal_segments.setRelatingObject(horizontal_alignment);
    nests_horizontal_segments.setRelatedObjects(horizontal_segments);

    //
    // Create the vertical alignment (IfcAlignmentVertical) and nest the segments
    //
    auto vertical_profile = file.create<Ifc4x3_add2::IfcAlignmentVertical>();
    vertical_profile.setGlobalId(IfcParse::IfcGlobalId());
    vertical_profile.setName(alignment_name + "- Vertical");
    
    auto nests_vertical_segments = file.create<Ifc4x3_add2::IfcRelNests>();
    nests_vertical_segments.setGlobalId(IfcParse::IfcGlobalId());
    nests_vertical_segments.setName("Nests vertical alignment segments with vertical alignment");
    nests_vertical_segments.setRelatingObject(vertical_profile);
    nests_vertical_segments.setRelatedObjects(vertical_segments);
    
    Ifc4x3_add2::IfcLocalPlacement placement;
    Ifc4x3_add2::IfcProductDefinitionShape product_definition_shape;
    if (include_geometry) {
        auto axis_model_representation_subcontext = file.getRepresentationSubContext("Axis", "Model");

        // create footprint representation
        auto footprint_shape_representation = file.create<Ifc4x3_add2::IfcShapeRepresentation>();
        footprint_shape_representation.setContextOfItems(axis_model_representation_subcontext);
        footprint_shape_representation.setRepresentationIdentifier("FootPrint");
        footprint_shape_representation.setRepresentationType("Curve2D");
        footprint_shape_representation.setItems(std::vector<Ifc4x3_add2::IfcRepresentationItem>{composite_curve});

        // create the axis representation
        auto axis3d_shape_representation = file.create<Ifc4x3_add2::IfcShapeRepresentation>();
        axis3d_shape_representation.setContextOfItems(axis_model_representation_subcontext);
        axis3d_shape_representation.setRepresentationIdentifier("Axis");
        axis3d_shape_representation.setRepresentationType("Curve3D");
        axis3d_shape_representation.setItems(std::vector<Ifc4x3_add2::IfcRepresentationItem>{gradient_curve});

        // create axis representations for each segment
        placement = file.addLocalPlacement();
        _createSegmentRepresentations(file, placement, axis_model_representation_subcontext, horizontal_curve_segments, horizontal_segments);
        _createSegmentRepresentations(file, placement, axis_model_representation_subcontext, vertical_curve_segments, vertical_segments);

        // the alignment has a 3d curve representation
        // create the alignment product definition
        product_definition_shape = file.create<Ifc4x3_add2::IfcProductDefinitionShape>();
        product_definition_shape.setName("Alignment Product Definition Shape");
        product_definition_shape.setRepresentations(std::vector<Ifc4x3_add2::IfcRepresentation>{footprint_shape_representation, axis3d_shape_representation});
    }

    //
    // Create the IfcAlignment
    //
    auto alignment = file.create<Ifc4x3_add2::IfcAlignment>();
    alignment.setGlobalId(IfcParse::IfcGlobalId());
    alignment.setName(alignment_name);
    alignment.setObjectPlacement(placement);
    alignment.setRepresentation(product_definition_shape);
    
    // Nest the IfcAlignmentHorizontal and IfcAlignmentVertical with the IfcAlignment to complete the business logic
    // 4.1.4.4.1 Alignments nest horizontal and vertical layouts
    // https://standards.buildingsmart.org/IFC/RELEASE/IFC4_3/HTML/concepts/Object_Composition/Nesting/Alignment_Layouts/content.html
    auto nests_alignment_layouts = file.create<Ifc4x3_add2::IfcRelNests>();
    nests_alignment_layouts.setGlobalId(IfcParse::IfcGlobalId());
    nests_alignment_layouts.setName("Nest horizontal and vertical alignment layouts with the alignment");
    nests_alignment_layouts.setRelatingObject(alignment);
    nests_alignment_layouts.setRelatedObjects(std::vector<Ifc4x3_add2::IfcObjectDefinition>{horizontal_alignment, vertical_profile});

    return alignment;
}

std::pair<Ifc4x3_add2::IfcCurveSegment, Ifc4x3_add2::IfcCurveSegment> mapAlignmentSegment(IfcHierarchyHelper<Ifc4x3_add2>& file, const Ifc4x3_add2::IfcAlignmentSegment& segment) {
    std::pair<Ifc4x3_add2::IfcCurveSegment, Ifc4x3_add2::IfcCurveSegment> result;
    auto design_parameters = segment.DesignParameters();
    auto horizontal = design_parameters.as<Ifc4x3_add2::IfcAlignmentHorizontalSegment>();
    auto vertical = design_parameters.as<Ifc4x3_add2::IfcAlignmentVerticalSegment>();
    auto cant = design_parameters.as<Ifc4x3_add2::IfcAlignmentCantSegment>();
    if (horizontal) {
        result = mapAlignmentHorizontalSegment(file, horizontal);
    } else if (vertical) {
        result = mapAlignmentVerticalSegment(file, vertical);
    } else if (cant) {
        result = mapAlignmentCantSegment(file, cant);
    } else {
        Logger::Error(std::string("Unexpected IfcAlignmentSegment subtype encountered"));
    }
    return result;
}

namespace {
Ifc4x3_add2::IfcLengthMeasure create_length(IfcHierarchyHelper<Ifc4x3_add2>& file, double d) {
    auto inst = file.create<Ifc4x3_add2::IfcLengthMeasure>();
    inst.set_attribute_value(0, d);
    return inst;
}
}

std::pair<Ifc4x3_add2::IfcCurveSegment, Ifc4x3_add2::IfcCurveSegment> mapAlignmentHorizontalSegment(IfcHierarchyHelper<Ifc4x3_add2>& file, const Ifc4x3_add2::IfcAlignmentHorizontalSegment& segment) {
    std::pair<Ifc4x3_add2::IfcCurveSegment, Ifc4x3_add2::IfcCurveSegment> result;
    auto start_point = segment.StartPoint();
    auto start_direction = segment.StartDirection();
    auto start_radius = segment.StartRadiusOfCurvature();
    auto end_radius = segment.EndRadiusOfCurvature();
    auto length = segment.SegmentLength();
    auto type = segment.PredefinedType();

    double f = (end_radius ? length / end_radius : 0.0) - (start_radius ? length / start_radius : 0.0);

    if (type == Ifc4x3_add2::IfcAlignmentHorizontalSegmentTypeEnum::IfcAlignmentHorizontalSegmentType_LINE) {
        auto parent_curve = file.create<Ifc4x3_add2::IfcLine>();
        parent_curve.setPnt(file.addDoublet<Ifc4x3_add2::IfcCartesianPoint>(0.0, 0.0));
        auto vec = file.create<Ifc4x3_add2::IfcVector>();
        vec.setOrientation(file.addDoublet<Ifc4x3_add2::IfcDirection>(1.0, 0.0));
        vec.setMagnitude(1.);
        parent_curve.setDir(vec);

        auto curve_segment = file.create<Ifc4x3_add2::IfcCurveSegment>();
        curve_segment.setTransition(Ifc4x3_add2::IfcTransitionCode::IfcTransitionCode_CONTSAMEGRADIENT);
        curve_segment.setPlacement(file.addPlacement2d(start_point.Coordinates()[0], start_point.Coordinates()[1], cos(start_direction), sin(start_direction)));
        curve_segment.setSegmentLength(create_length(file, 0.0));
        curve_segment.setSegmentLength(create_length(file, length));
        curve_segment.setParentCurve(parent_curve);

        result.first = curve_segment;
    } else if (type == Ifc4x3_add2::IfcAlignmentHorizontalSegmentTypeEnum::IfcAlignmentHorizontalSegmentType_CIRCULARARC) {
        auto parent_curve = file.create<Ifc4x3_add2::IfcCircle>();
        parent_curve.setPosition(file.addPlacement2d(0., 0., 1.0, 0.));
        parent_curve.setRadius(std::fabs(start_radius));

        auto curve_segment = file.create<Ifc4x3_add2::IfcCurveSegment>();
        curve_segment.setTransition(Ifc4x3_add2::IfcTransitionCode::IfcTransitionCode_CONTSAMEGRADIENT);
        curve_segment.setPlacement(file.addPlacement2d(start_point.Coordinates()[0], start_point.Coordinates()[1], cos(start_direction), sin(start_direction)));
        curve_segment.setSegmentLength(create_length(file, 0.0));
        curve_segment.setSegmentLength(create_length(file, length * start_radius / std::fabs(start_radius)));
        curve_segment.setParentCurve(parent_curve);

        result.first = curve_segment;
    } else if (type == Ifc4x3_add2::IfcAlignmentHorizontalSegmentTypeEnum::IfcAlignmentHorizontalSegmentType_CLOTHOID) {
        double A = length / sqrt(fabs(f)) * f / fabs(f);
        auto parent_curve = file.create<Ifc4x3_add2::IfcClothoid>();
        parent_curve.setPosition(file.addPlacement2d(0., 0., 1.0, 0.));
        parent_curve.setClothoidConstant(A);

        double offset;
        if ((fabs(start_radius) < fabs(end_radius) && start_radius) || end_radius == 0.) {
            offset = -length - (end_radius ? length * start_radius / (end_radius - start_radius) : 0);
        } else {
            offset = start_radius ? length * end_radius / (start_radius - end_radius) : 0;
        }

        auto curve_segment = file.create<Ifc4x3_add2::IfcCurveSegment>();
        curve_segment.setTransition(Ifc4x3_add2::IfcTransitionCode::IfcTransitionCode_CONTSAMEGRADIENT);
        curve_segment.setPlacement(file.addPlacement2d(start_point.Coordinates()[0], start_point.Coordinates()[1], cos(start_direction), sin(start_direction)));
        curve_segment.setSegmentLength(create_length(file, offset));
        curve_segment.setSegmentLength(create_length(file, length));
        curve_segment.setParentCurve(parent_curve);

        result.first = curve_segment;
    } else if (type == Ifc4x3_add2::IfcAlignmentHorizontalSegmentTypeEnum::IfcAlignmentHorizontalSegmentType_BLOSSCURVE) {
        auto a0 = start_radius ? length / start_radius : 0.0; // constant term
        auto a1 = 0.0;                                        // linear term
        auto a2 = 3 * f; // quadratic term
        auto a3 = -2 * f; // cubic term
        auto A0 = a0 ? length * pow(fabs(a0), -1. / 1.) * a0 / fabs(a0) : 0.0;
        auto A1 = a1 ? length * pow(fabs(a1), -1. / 2.) * a1 / fabs(a1) : 0.0;
        auto A2 = a2 ? length * pow(fabs(a2), -1. / 3.) * a2 / fabs(a2) : 0.0;
        auto A3 = a3 ? length * pow(fabs(a3), -1. / 4.) * a3 / fabs(a3) : 0.0;

        std::optional<double> A0_optional, A1_optional, A2_optional;
        if (A0) {
            A0_optional = A0;
        }
        if (A1) {
            A1_optional = A1;
        }
        if (A2) {
            A2_optional = A2;
        }

        auto parent_curve = file.create<Ifc4x3_add2::IfcThirdOrderPolynomialSpiral>();
        parent_curve.setPosition(file.addPlacement2d(0., 0., 1.0, 0.));
        parent_curve.setCubicTerm(A3);
        parent_curve.setQuadraticTerm(A2_optional);
        parent_curve.setLinearTerm(A1_optional);
        parent_curve.setConstantTerm(A0_optional);

        Ifc4x3_add2::IfcCurveSegment curve_segment = file.create<Ifc4x3_add2::IfcCurveSegment>();
        curve_segment.setTransition(Ifc4x3_add2::IfcTransitionCode::IfcTransitionCode_CONTSAMEGRADIENT);
        curve_segment.setPlacement(file.addPlacement2d(start_point.Coordinates()[0], start_point.Coordinates()[1], cos(start_direction), sin(start_direction)));
        curve_segment.setSegmentLength(create_length(file, 0.0));
        curve_segment.setSegmentLength(create_length(file, length));
        curve_segment.setParentCurve(parent_curve);

        result.first = curve_segment;
    } else if (type == Ifc4x3_add2::IfcAlignmentHorizontalSegmentTypeEnum::IfcAlignmentHorizontalSegmentType_COSINECURVE) {
        auto a0 = 0.5 * f + (start_radius ? length / start_radius : 0.0); // constant term
        auto a1 = -0.5 * f; // cosine term
        auto A0 = a0 ? length * pow(fabs(a0), -1. / 1.) * a0 / fabs(a0) : 0.0;
        auto A1 = a1 ? length * pow(fabs(a1), -1. / 1.) * a1 / fabs(a1) : 0.0;
        auto A0_optional = std::optional<double>();
        if (A0) {
            A0_optional = A0;
        }
        auto parent_curve = file.create<Ifc4x3_add2::IfcCosineSpiral>();
        parent_curve.setPosition(file.addPlacement2d(0., 0., 1.0, 0.));
        parent_curve.setCosineTerm(A1);
        parent_curve.setConstantTerm(A0_optional);

        Ifc4x3_add2::IfcCurveSegment curve_segment = file.create<Ifc4x3_add2::IfcCurveSegment>();
        curve_segment.setTransition(Ifc4x3_add2::IfcTransitionCode::IfcTransitionCode_CONTSAMEGRADIENT);
        curve_segment.setPlacement(file.addPlacement2d(start_point.Coordinates()[0], start_point.Coordinates()[1], cos(start_direction), sin(start_direction)));
        curve_segment.setSegmentLength(create_length(file, 0.0));
        curve_segment.setSegmentLength(create_length(file, length));
        curve_segment.setParentCurve(parent_curve);

        result.first = curve_segment;
    } else if (type == Ifc4x3_add2::IfcAlignmentHorizontalSegmentTypeEnum::IfcAlignmentHorizontalSegmentType_CUBIC) {
        double offset = 0;
        double A0 = 0; // constant term
        double A1 = 0; // linear term
        double A2 = 0; // quadratic term
        double A3 = 0; // cubic term
        if (end_radius && start_radius && end_radius != start_radius)
        {
            f = (start_radius - end_radius) / end_radius;
            A3 = f / (6. * start_radius * length);
            offset = length / f;
        } else if (end_radius) {
            A3 = 1. / (6. * end_radius * length);
            offset = 0.0;
        } else if (start_radius) {
            A3 = -1. / (6. * start_radius * length);
            offset = -length;
        }
        auto parent_curve = file.create<Ifc4x3_add2::IfcPolynomialCurve>();
        parent_curve.setPosition(file.addPlacement2d(0., 0., 1.0, 0.));
        parent_curve.setCoefficientsX(std::vector<double>{0.0, 1.0});
        parent_curve.setCoefficientsY(std::vector<double>{A0, A1, A2, A3});

        Ifc4x3_add2::IfcCurveSegment curve_segment = file.create<Ifc4x3_add2::IfcCurveSegment>();
        curve_segment.setTransition(Ifc4x3_add2::IfcTransitionCode::IfcTransitionCode_CONTSAMEGRADIENT);
        curve_segment.setPlacement(file.addPlacement2d(start_point.Coordinates()[0], start_point.Coordinates()[1], cos(start_direction), sin(start_direction)));
        curve_segment.setSegmentLength(create_length(file, offset));
        curve_segment.setSegmentLength(create_length(file, length));
        curve_segment.setParentCurve(parent_curve);

        result.first = curve_segment;
    } else if (type == Ifc4x3_add2::IfcAlignmentHorizontalSegmentTypeEnum::IfcAlignmentHorizontalSegmentType_HELMERTCURVE) {
        auto a0_1 = start_radius ? length / start_radius : 0.0; // constant term, first half
        auto a1_1 = 0.0;                                        // linear term, first half
        auto a2_1 = 2 * f; // quadratic term, first half

        auto A0_1 = a0_1 ? length * pow(fabs(a0_1), -1. / 1.) * a0_1 / fabs(a0_1) : 0.0;
        auto A1_1 = a1_1 ? length * pow(fabs(a1_1), -1. / 2.) * a1_1 / fabs(a1_1) : 0.0;
        auto A2_1 = a2_1 ? length * pow(fabs(a2_1), -1. / 3.) * a2_1 / fabs(a2_1) : 0.0;

        auto A0_1_optional = std::optional<double>();
        if (A0_1) {
            A0_1_optional = A0_1;
        }

        auto A1_1_optional = std::optional<double>();
        if (A1_1) {
            A1_1_optional = A1_1;
        }

        auto parent_curve1 = file.create<Ifc4x3_add2::IfcSecondOrderPolynomialSpiral>();
        parent_curve1.setPosition(file.addPlacement2d(0., 0., 1.0, 0.));
        parent_curve1.setQuadraticTerm(A2_1);
        parent_curve1.setLinearTerm(A1_1_optional);
        parent_curve1.setConstantTerm(A0_1_optional);

        Ifc4x3_add2::IfcCurveSegment curve_segment1 = file.create<Ifc4x3_add2::IfcCurveSegment>();
        curve_segment1.setTransition(Ifc4x3_add2::IfcTransitionCode::IfcTransitionCode_CONTSAMEGRADIENT);
        curve_segment1.setPlacement(file.addPlacement2d(start_point.Coordinates()[0], start_point.Coordinates()[1], cos(start_direction), sin(start_direction)));
        curve_segment1.setSegmentLength(create_length(file, 0.0));
        curve_segment1.setSegmentLength(create_length(file, length / 2));
        curve_segment1.setParentCurve(parent_curve1);

        result.first = curve_segment1;

        auto a0_2 = -f + (start_radius ? length / start_radius : 0.0); // constant term, second half
        auto a1_2 = 4 * f;                                             // linear term, second half
        auto a2_2 = -2 * f;                                            // quadratic term, second half

        auto A0_2 = a0_2 ? length * pow(fabs(a0_2), -1. / 1.) * a0_2 / fabs(a0_2) : 0.0;
        auto A1_2 = a1_2 ? length * pow(fabs(a1_2), -1. / 2.) * a1_2 / fabs(a1_2) : 0.0;
        auto A2_2 = a2_2 ? length * pow(fabs(a2_2), -1. / 3.) * a2_2 / fabs(a2_2) : 0.0;

        auto A0_2_optional = std::optional<double>();
        if (A0_2) {
            A0_2_optional = A0_2;
        }
        auto A1_2_optional = std::optional<double>();
        if (A1_2) {
            A1_2_optional = A1_2;
        }

        Ifc4x3_add2::IfcCurve parent_curve2 = file.create<Ifc4x3_add2::IfcSecondOrderPolynomialSpiral>();
        parent_curve1.setPosition(file.addPlacement2d(0., 0., 1.0, 0.));
        parent_curve1.setQuadraticTerm(A2_2);
        parent_curve1.setLinearTerm(A1_2_optional);
        parent_curve1.setConstantTerm(A0_2_optional);

        Ifc4x3_add2::IfcCurveSegment curve_segment2 = file.create<Ifc4x3_add2::IfcCurveSegment>();
        curve_segment2.setTransition(Ifc4x3_add2::IfcTransitionCode::IfcTransitionCode_CONTSAMEGRADIENT);
        curve_segment2.setPlacement(file.addPlacement2d(start_point.Coordinates()[0], start_point.Coordinates()[1], cos(start_direction), sin(start_direction)));
        curve_segment2.setSegmentLength(create_length(file, length / 2));
        curve_segment2.setSegmentLength(create_length(file, length / 2));
        curve_segment2.setParentCurve(parent_curve2);

        result.second = curve_segment2;
    } else if (type == Ifc4x3_add2::IfcAlignmentHorizontalSegmentTypeEnum::IfcAlignmentHorizontalSegmentType_SINECURVE) {
        auto a0 = start_radius ? length / start_radius : 0.0; // constant term
        auto a1 = f;                                          // linear term
        auto a2 = -f / (2 * PI); // sine term

        auto A0 = a0 ? length * pow(fabs(a0), -1. / 1.) * a0 / fabs(a0) : 0.0;
        auto A1 = a1 ? length * pow(fabs(a1), -1. / 2.) * a1 / fabs(a1) : 0.0;
        auto A2 = a2 ? length * pow(fabs(a2), -1. / 1.) * a2 / fabs(a2) : 0.0;

        auto A0_optional = std::optional<double>();
        if (A0) {
            A0_optional = A0;
        }
        auto A1_optional = std::optional<double>();
        if (A1) {
            A1_optional = A1;
        }

        auto parent_curve = file.create<Ifc4x3_add2::IfcSineSpiral>();
        parent_curve.setPosition(file.addPlacement2d(0., 0., 1.0, 0.));
        parent_curve.setSineTerm(A2);
        parent_curve.setLinearTerm(A1_optional);
        parent_curve.setConstantTerm(A0_optional);

        Ifc4x3_add2::IfcCurveSegment curve_segment = file.create<Ifc4x3_add2::IfcCurveSegment>();
        curve_segment.setTransition(Ifc4x3_add2::IfcTransitionCode::IfcTransitionCode_CONTSAMEGRADIENT);
        curve_segment.setPlacement(file.addPlacement2d(start_point.Coordinates()[0], start_point.Coordinates()[1], cos(start_direction), sin(start_direction)));
        curve_segment.setSegmentLength(create_length(file, 0.0));
        curve_segment.setSegmentLength(create_length(file, length));
        curve_segment.setParentCurve(parent_curve);

        result.first = curve_segment;
    } else if (type == Ifc4x3_add2::IfcAlignmentHorizontalSegmentTypeEnum::IfcAlignmentHorizontalSegmentType_VIENNESEBEND) {
        Logger::Warning(std::string("mapping of AlignmentHorizontalSegmentType VIENNESEBEND not supported"));
    } else {
        Logger::Error(std::string("unexpected AlignmentHorizontalSegmentType encountered"));
    }

    return result;
}

std::pair<Ifc4x3_add2::IfcCurveSegment, Ifc4x3_add2::IfcCurveSegment> mapAlignmentVerticalSegment(IfcHierarchyHelper<Ifc4x3_add2>& file, const Ifc4x3_add2::IfcAlignmentVerticalSegment& segment) {
    std::pair<Ifc4x3_add2::IfcCurveSegment, Ifc4x3_add2::IfcCurveSegment> result;
    auto start_distance_along = segment.StartDistAlong();
    auto horizontal_length = segment.HorizontalLength();
    auto start_height = segment.StartHeight();
    auto start_gradient = segment.StartGradient();
    auto end_gradient = segment.EndGradient();
    auto radius_of_curvature = segment.RadiusOfCurvature();

    auto type = segment.PredefinedType();

    if (type == Ifc4x3_add2::IfcAlignmentVerticalSegmentTypeEnum::IfcAlignmentVerticalSegmentType_CONSTANTGRADIENT) {
        auto parent_curve = file.create<Ifc4x3_add2::IfcLine>();
        parent_curve.setPnt(file.addDoublet<Ifc4x3_add2::IfcCartesianPoint>(0, 0));
        auto vec = file.create<Ifc4x3_add2::IfcVector>();
        vec.setOrientation(file.addDoublet<Ifc4x3_add2::IfcDirection>(1, 0));
        vec.setMagnitude(1.0);
        parent_curve.setDir(vec);

        // IfcCurveSegment.SegmentLength is the length of the curve segment, not the horizontal length.
        auto dx = cos(atan(start_gradient));
        auto dy = sin(atan(start_gradient));
        auto segment_curve_length = horizontal_length / dx;

        auto curve_segment = file.create<Ifc4x3_add2::IfcCurveSegment>();
        curve_segment.setTransition(Ifc4x3_add2::IfcTransitionCode::IfcTransitionCode_CONTSAMEGRADIENT);
        curve_segment.setPlacement(file.addPlacement2d(start_distance_along, start_height, dx, dy));
        curve_segment.setSegmentLength(create_length(file, 0.0));
        curve_segment.setSegmentLength(create_length(file, segment_curve_length));
        curve_segment.setParentCurve(parent_curve);

        result.first = curve_segment;
    } else if (type == Ifc4x3_add2::IfcAlignmentVerticalSegmentTypeEnum::IfcAlignmentVerticalSegmentType_PARABOLICARC) {
        double A = start_height;
        double B = start_gradient;
        double C = (end_gradient - start_gradient) / (2 * horizontal_length);

        auto parent_curve = file.create<Ifc4x3_add2::IfcPolynomialCurve>();
        parent_curve.setPosition(file.addPlacement2d(0., 0., 1.0, 0.));
        parent_curve.setCoefficientsX(std::vector<double>{0.0, 1.0});
        parent_curve.setCoefficientsY(std::vector<double>{A, B, C});

        // IfcCurveSegment.SegmentLength is the length of the curve segment, not the horizontal length.
        // The curve length is calculated by integrating the differential curve length equation sqrt(1 + (dy/dx)^2) from 0 to horizontal_length.
        // y = A + Bx + Cx^2
        // dy/dx = B + 2Cx
        auto dx = cos(atan(start_gradient));
        auto dy = sin(atan(start_gradient));
        auto curve_length_fn = [B, C](double x) { return sqrt(1 + pow(B + 2*C * x, 2)); };
        auto segment_curve_length = boost::math::quadrature::trapezoidal(curve_length_fn, 0.0, horizontal_length);

        auto curve_segment = file.create<Ifc4x3_add2::IfcCurveSegment>();
        curve_segment.setTransition(Ifc4x3_add2::IfcTransitionCode::IfcTransitionCode_CONTSAMEGRADIENT);
        curve_segment.setPlacement(file.addPlacement2d(start_distance_along, start_height, dx, dy));
        curve_segment.setSegmentLength(create_length(file, 0.0));
        curve_segment.setSegmentLength(create_length(file, segment_curve_length));
        curve_segment.setParentCurve(parent_curve);

        result.first = curve_segment;
    } else if (type == Ifc4x3_add2::IfcAlignmentVerticalSegmentTypeEnum::IfcAlignmentVerticalSegmentType_CLOTHOID) {
        Logger::Warning(std::string("mapping of AlignmentVerticalSegmentType CLOTHOID not supported"));
    } else if (type == Ifc4x3_add2::IfcAlignmentVerticalSegmentTypeEnum::IfcAlignmentVerticalSegmentType_CIRCULARARC) {
        auto start_angle = atan(start_gradient);
        auto end_angle = atan(end_gradient);
        double radius;
        if (start_angle < end_angle) {
            radius = horizontal_length / (sin(end_angle) - sin(start_angle));
        } else {
            radius = horizontal_length / (sin(start_angle) - sin(end_angle));
        }

        auto parent_curve = file.create<Ifc4x3_add2::IfcCircle>();
        parent_curve.setPosition(file.addPlacement2d(0., 0., 1.0, 0.));
        parent_curve.setRadius(radius);

        auto segment_curve_length = radius * fabs(end_angle - start_angle);

        Ifc4x3_add2::IfcCurveSegment curve_segment = file.create<Ifc4x3_add2::IfcCurveSegment>();
        curve_segment.setTransition(Ifc4x3_add2::IfcTransitionCode::IfcTransitionCode_CONTSAMEGRADIENT);
        curve_segment.setPlacement(file.addPlacement2d(start_distance_along, start_height, 1.0, 0.));
        curve_segment.setSegmentLength(create_length(file, 0.0));
        curve_segment.setSegmentLength(create_length(file, segment_curve_length));
        curve_segment.setParentCurve(parent_curve);

        result.first = curve_segment;
    } else {
        Logger::Error(std::string("unexpected AlignmentVerticalSegmentType encountered"));
    }
    
    return result;
}

std::pair<Ifc4x3_add2::IfcCurveSegment, Ifc4x3_add2::IfcCurveSegment> mapAlignmentCantSegment(IfcHierarchyHelper<Ifc4x3_add2>& file, const Ifc4x3_add2::IfcAlignmentCantSegment& segment) {
    std::pair<Ifc4x3_add2::IfcCurveSegment, Ifc4x3_add2::IfcCurveSegment> result;
    auto type = segment.PredefinedType();
    if (type == Ifc4x3_add2::IfcAlignmentCantSegmentTypeEnum::IfcAlignmentCantSegmentType_BLOSSCURVE) {
        Logger::Warning(std::string("mapping of AlignmentCantSegmentType BLOSSCURVE not supported"));
    } else if (type == Ifc4x3_add2::IfcAlignmentCantSegmentTypeEnum::IfcAlignmentCantSegmentType_CONSTANTCANT) {
        Logger::Warning(std::string("mapping of AlignmentCantSegmentType CONSTANTCANT not supported"));
    } else if (type == Ifc4x3_add2::IfcAlignmentCantSegmentTypeEnum::IfcAlignmentCantSegmentType_COSINECURVE) {
        Logger::Warning(std::string("mapping of AlignmentCantSegmentType COSINECURVE not supported"));
    } else if (type == Ifc4x3_add2::IfcAlignmentCantSegmentTypeEnum::IfcAlignmentCantSegmentType_HELMERTCURVE) {
        Logger::Warning(std::string("mapping of AlignmentCantSegmentType HELMERTCURVE not supported"));
    } else if (type == Ifc4x3_add2::IfcAlignmentCantSegmentTypeEnum::IfcAlignmentCantSegmentType_LINEARTRANSITION) {
        Logger::Warning(std::string("mapping of AlignmentCantSegmentType LINEARTRANSTION not supported"));
    } else if (type == Ifc4x3_add2::IfcAlignmentCantSegmentTypeEnum::IfcAlignmentCantSegmentType_SINECURVE) {
        Logger::Warning(std::string("mapping of AlignmentCantSegmentType SINECURVE not supported"));
    } else if (type == Ifc4x3_add2::IfcAlignmentCantSegmentTypeEnum::IfcAlignmentCantSegmentType_VIENNESEBEND) {
        Logger::Warning(std::string("mapping of AlignmentCantSegmentType VIENNESEBEND not supported"));
    } else {
        Logger::Error(std::string("unexpected AlignmentCantSegmentType encountered"));
    }
    return result;
}
#endif
