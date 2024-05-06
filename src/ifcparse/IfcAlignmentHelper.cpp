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


#ifdef HAS_SCHEMA_4x3_add2

// sets the segment name like ("H1" for horizontal, "V1" for vertical, "C1" for cant)
void _name_segments(const char* prefix, typename aggregate_of<Ifc4x3_add2::IfcObjectDefinition>::ptr segments) {
    unsigned idx = 1;
    for (auto& segment : *segments) {
        std::ostringstream os;
        os << prefix << idx++;
        segment->setName(os.str());
    }
}

// creates representations for each IfcAlignmentSegment per CT 4.1.7.1.1.4
// https://standards.buildingsmart.org/IFC/RELEASE/IFC4_3/HTML/concepts/Product_Shape/Product_Geometric_Representation/Alignment_Geometry/Alignment_Geometry_-_Segments/content.html
void _createSegmentRepresentations(IfcHierarchyHelper<Ifc4x3_add2>& file, Ifc4x3_add2::IfcLocalPlacement* global_placement, Ifc4x3_add2::IfcGeometricRepresentationSubContext* segment_axis_subcontext, typename aggregate_of<Ifc4x3_add2::IfcSegment>::ptr curve_segments, typename aggregate_of<Ifc4x3_add2::IfcObjectDefinition>::ptr segments) {
    auto cs_iter = curve_segments->begin();
    auto s_iter = segments->begin();
    for (; cs_iter != curve_segments->end(); cs_iter++, s_iter++) {
        auto curve_segment = *cs_iter;
        auto alignment_segment = (*s_iter)->as<Ifc4x3_add2::IfcAlignmentSegment>();

        typename aggregate_of<Ifc4x3_add2::IfcRepresentationItem>::ptr representation_items(new aggregate_of<Ifc4x3_add2::IfcRepresentationItem>());
        representation_items->push(curve_segment);

        auto axis_representation = new Ifc4x3_add2::IfcShapeRepresentation(segment_axis_subcontext, std::string("Axis"), std::string("Segment"), representation_items);
        file.addEntity(axis_representation);

        typename aggregate_of<Ifc4x3_add2::IfcRepresentation>::ptr representations(new aggregate_of<Ifc4x3_add2::IfcRepresentation>());
        representations->push(axis_representation);

        auto product = new Ifc4x3_add2::IfcProductDefinitionShape(boost::none, boost::none, representations);
        file.addEntity(product);

        alignment_segment->setObjectPlacement(global_placement);
        alignment_segment->setRepresentation(product);
    }
}

// creates a horizontal alignment using a vector of PI points and curve radii
// returns a list of object definitions, curve segments, and a composite curve
std::tuple<typename aggregate_of<Ifc4x3_add2::IfcObjectDefinition>::ptr, typename aggregate_of<Ifc4x3_add2::IfcSegment>::ptr, Ifc4x3_add2::IfcCompositeCurve*> _createHorizontalAlignment(IfcHierarchyHelper<Ifc4x3_add2>& file, const std::vector<std::pair<double, double>>& points, const std::vector<double>& radii,bool include_geometry) {
    typename aggregate_of<Ifc4x3_add2::IfcObjectDefinition>::ptr horizontal_segments(new aggregate_of<Ifc4x3_add2::IfcObjectDefinition>()); // business logic
    typename aggregate_of<Ifc4x3_add2::IfcSegment>::ptr horizontal_curve_segments(include_geometry ? new aggregate_of<Ifc4x3_add2::IfcSegment>() : nullptr);             // geometry

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
            auto design_parameters = new Ifc4x3_add2::IfcAlignmentHorizontalSegment(boost::none, boost::none, pt, angleBT, 0.0, 0.0, tangent_run, boost::none, Ifc4x3_add2::IfcAlignmentHorizontalSegmentTypeEnum::IfcAlignmentHorizontalSegmentType_LINE);
            auto alignment_segment = new Ifc4x3_add2::IfcAlignmentSegment(IfcParse::IfcGlobalId(), nullptr, boost::none, boost::none, boost::none, nullptr, nullptr, design_parameters);
            horizontal_segments->push(alignment_segment);

            if (include_geometry) {
                horizontal_curve_segments->push(mapAlignmentHorizontalSegment(design_parameters).first);
            }
        }

        // create circular curve
        {
            auto pc = file.addDoublet<Ifc4x3_add2::IfcCartesianPoint>(xPC, yPC);
            auto design_parameters = new Ifc4x3_add2::IfcAlignmentHorizontalSegment(boost::none, boost::none, pc, angleBT, radius, radius, lc, boost::none, Ifc4x3_add2::IfcAlignmentHorizontalSegmentTypeEnum::IfcAlignmentHorizontalSegmentType_CIRCULARARC);
            auto alignment_segment = new Ifc4x3_add2::IfcAlignmentSegment(IfcParse::IfcGlobalId(), nullptr, boost::none, boost::none, boost::none, nullptr, nullptr, design_parameters);
            horizontal_segments->push(alignment_segment);

            if (include_geometry) {
                horizontal_curve_segments->push(mapAlignmentHorizontalSegment(design_parameters).first);
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
    auto design_parameters = new Ifc4x3_add2::IfcAlignmentHorizontalSegment(boost::none, boost::none, pt, angleBT, 0.0, 0.0, tangent_run, boost::none, Ifc4x3_add2::IfcAlignmentHorizontalSegmentTypeEnum::IfcAlignmentHorizontalSegmentType_LINE);
    auto alignment_segment = new Ifc4x3_add2::IfcAlignmentSegment(IfcParse::IfcGlobalId(), nullptr, boost::none, boost::none, boost::none, nullptr, nullptr, design_parameters);
    horizontal_segments->push(alignment_segment);
    if (include_geometry) {
        horizontal_curve_segments->push(mapAlignmentHorizontalSegment(design_parameters).first);
    }

    // create zero length terminator segment
    auto poe = file.addDoublet<Ifc4x3_add2::IfcCartesianPoint>(xPI, yPI);
    design_parameters = new Ifc4x3_add2::IfcAlignmentHorizontalSegment(boost::none, boost::none, poe, angleBT, 0.0, 0.0, 0.0, boost::none, Ifc4x3_add2::IfcAlignmentHorizontalSegmentTypeEnum::IfcAlignmentHorizontalSegmentType_LINE);
    alignment_segment = new Ifc4x3_add2::IfcAlignmentSegment(IfcParse::IfcGlobalId(), nullptr, boost::none, boost::none, boost::none, nullptr, nullptr, design_parameters);
    horizontal_segments->push(alignment_segment);
    if (include_geometry) {
        auto segment = mapAlignmentHorizontalSegment(design_parameters).first;
        segment->setTransition(Ifc4x3_add2::IfcTransitionCode::IfcTransitionCode_DISCONTINUOUS);
        horizontal_curve_segments->push(segment);
    }

    Ifc4x3_add2::IfcCompositeCurve* composite_curve = nullptr;
    if (include_geometry) {
        composite_curve = new Ifc4x3_add2::IfcCompositeCurve(horizontal_curve_segments, false /*not self-intersecting*/);
        file.addEntity(composite_curve);
    }

    return {horizontal_segments, horizontal_curve_segments, composite_curve};
}

Ifc4x3_add2::IfcAlignment* addHorizontalAlignment(IfcHierarchyHelper<Ifc4x3_add2>& file, const std::string& alignment_name, const std::vector<std::pair<double, double>>& points, const std::vector<double>& radii,bool include_geometry) {

    auto [horizontal_segments, horizontal_curve_segments, composite_curve] = _createHorizontalAlignment(file, points, radii, include_geometry);
    _name_segments("H", horizontal_segments);

    //
    // Create the horizontal alignment (IfcAlignmentHorizontal) and nest alignment segments
    //
    auto horizontal_alignment = new Ifc4x3_add2::IfcAlignmentHorizontal(IfcParse::IfcGlobalId(), nullptr, alignment_name + std::string(" - Horizontal"), boost::none, boost::none, nullptr, nullptr);
    file.addEntity(horizontal_alignment);

    auto nests_horizontal_segments = new Ifc4x3_add2::IfcRelNests(IfcParse::IfcGlobalId(), nullptr, boost::none, std::string("Nests horizontal alignment segments with horizontal alignment"), horizontal_alignment, horizontal_segments);
    file.addEntity(nests_horizontal_segments);

    //
    // Create geometric representation
    //
    Ifc4x3_add2::IfcLocalPlacement* placement = nullptr;
    Ifc4x3_add2::IfcProductDefinitionShape* product_definition_shape = nullptr;
    if (include_geometry) { 
       typename aggregate_of<Ifc4x3_add2::IfcRepresentationItem>::ptr alignment_representation_items(new aggregate_of<Ifc4x3_add2::IfcRepresentationItem>());
       alignment_representation_items->push(composite_curve);

       // create the footprint representation
       auto axis_model_representation_subcontext = file.getRepresentationSubContext("Axis", "Model");
       auto footprint_shape_representation = new Ifc4x3_add2::IfcShapeRepresentation(axis_model_representation_subcontext, std::string("FootPrint"), std::string("Curve2D"), alignment_representation_items);
       file.addEntity(footprint_shape_representation);

       placement = file.addLocalPlacement();

       // the alignment has two representations, a plan view footprint
       typename aggregate_of<Ifc4x3_add2::IfcRepresentation>::ptr alignment_representations(new aggregate_of<Ifc4x3_add2::IfcRepresentation>());
       alignment_representations->push(footprint_shape_representation); // 2D footprint

       // create the alignment product definition
       product_definition_shape = new Ifc4x3_add2::IfcProductDefinitionShape(std::string("Alignment Product Definition Shape"), boost::none, alignment_representations);

       // create representations for each segment
       _createSegmentRepresentations(file, placement, axis_model_representation_subcontext, horizontal_curve_segments, horizontal_segments);
    }

    // create the alignment
    auto alignment = new Ifc4x3_add2::IfcAlignment(IfcParse::IfcGlobalId(), nullptr, alignment_name, boost::none, boost::none, placement, product_definition_shape, boost::none);
    file.addEntity(alignment);
    

    return alignment;
}

std::tuple<typename aggregate_of<Ifc4x3_add2::IfcObjectDefinition>::ptr, typename aggregate_of<Ifc4x3_add2::IfcSegment>::ptr, Ifc4x3_add2::IfcGradientCurve*> _createVerticalAlignment(IfcHierarchyHelper<Ifc4x3_add2>& file, Ifc4x3_add2::IfcCompositeCurve* composite_curve,const std::vector<std::pair<double, double>>& vpoints, const std::vector<double>& vclengths, bool include_geometry) {
    typename aggregate_of<Ifc4x3_add2::IfcObjectDefinition>::ptr vertical_segments(new aggregate_of<Ifc4x3_add2::IfcObjectDefinition>()); // business logic
    typename aggregate_of<Ifc4x3_add2::IfcSegment>::ptr vertical_curve_segments(new aggregate_of<Ifc4x3_add2::IfcSegment>());             // geometry

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
        auto start_slope = atan2(dyBG, dxBG);

        // forward gradient
        point_iter++;
        std::tie(xPFG, yPFG) = *point_iter;
        auto dxFG = xPFG - xPVI;
        auto dyFG = yPFG - yPVI;
        auto end_slope = atan2(dyFG, dxFG);

        double xEVC = xPVI + length / 2;
        double yEVC = yPVI + end_slope * length / 2;

        // create gradient
        {
            file.addDoublet<Ifc4x3_add2::IfcCartesianPoint>(xPBG, yPBG);
            auto gradient_length = dxBG - length/2;
            auto design_parameters = new Ifc4x3_add2::IfcAlignmentVerticalSegment(boost::none, boost::none, xPBG, gradient_length, yPBG, start_slope, start_slope, boost::none, Ifc4x3_add2::IfcAlignmentVerticalSegmentTypeEnum::IfcAlignmentVerticalSegmentType_CONSTANTGRADIENT);
            auto alignment_segment = new Ifc4x3_add2::IfcAlignmentSegment(IfcParse::IfcGlobalId(), nullptr, boost::none, boost::none, boost::none, nullptr, nullptr, design_parameters);
            vertical_segments->push(alignment_segment);
            if (include_geometry) {
               vertical_curve_segments->push(mapAlignmentVerticalSegment(design_parameters).first);
            }
        }

        // create vertical curve
        {
            double k = (end_slope - start_slope) / length;
            double xBVC = xPVI - length / 2;
            double yBVC = yPVI - start_slope * length / 2;

            file.addDoublet<Ifc4x3_add2::IfcCartesianPoint>(xBVC, yBVC);

            auto design_parameters = new Ifc4x3_add2::IfcAlignmentVerticalSegment(boost::none, boost::none, xBVC, length, yBVC, start_slope, end_slope, 1 / k, Ifc4x3_add2::IfcAlignmentVerticalSegmentTypeEnum::IfcAlignmentVerticalSegmentType_PARABOLICARC);
            auto alignment_segment = new Ifc4x3_add2::IfcAlignmentSegment(IfcParse::IfcGlobalId(), nullptr, boost::none, boost::none, boost::none, nullptr, nullptr, design_parameters);
            vertical_segments->push(alignment_segment);
            if (include_geometry) {
                vertical_curve_segments->push(mapAlignmentVerticalSegment(design_parameters).first);
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
    auto slope = atan2(dy, dx);
    auto gradient_length = sqrt(dx * dx + dy * dy);
    file.addDoublet<Ifc4x3_add2::IfcCartesianPoint>(xPBG, yPBG);
    auto design_parameters = new Ifc4x3_add2::IfcAlignmentVerticalSegment(boost::none, boost::none, xPBG, gradient_length, yPBG, slope, slope, boost::none, Ifc4x3_add2::IfcAlignmentVerticalSegmentTypeEnum::IfcAlignmentVerticalSegmentType_CONSTANTGRADIENT);
    auto alignment_segment = new Ifc4x3_add2::IfcAlignmentSegment(IfcParse::IfcGlobalId(), nullptr, boost::none, boost::none, boost::none, nullptr, nullptr, design_parameters);
    vertical_segments->push(alignment_segment);
    if (include_geometry) {
        vertical_curve_segments->push(mapAlignmentVerticalSegment(design_parameters).first);
    }

    // create zero length terminator segment
    file.addDoublet<Ifc4x3_add2::IfcCartesianPoint>(xPVI, yPVI);
    design_parameters = new Ifc4x3_add2::IfcAlignmentVerticalSegment(boost::none, boost::none, xPVI, 0.0, yPVI, slope, slope, boost::none, Ifc4x3_add2::IfcAlignmentVerticalSegmentTypeEnum::IfcAlignmentVerticalSegmentType_CONSTANTGRADIENT);
    alignment_segment = new Ifc4x3_add2::IfcAlignmentSegment(IfcParse::IfcGlobalId(), nullptr, boost::none, boost::none, boost::none, nullptr, nullptr, design_parameters);
    vertical_segments->push(alignment_segment);
    if (include_geometry) {
        auto segment = mapAlignmentVerticalSegment(design_parameters).first;
        segment->setTransition(Ifc4x3_add2::IfcTransitionCode::IfcTransitionCode_DISCONTINUOUS);
        vertical_curve_segments->push(segment);
    }

    Ifc4x3_add2::IfcGradientCurve* gradient_curve = nullptr;
    if (include_geometry) {
        gradient_curve = new Ifc4x3_add2::IfcGradientCurve(vertical_curve_segments, false, composite_curve, nullptr);
        file.addEntity(gradient_curve);
    }

    return {vertical_segments, vertical_curve_segments, gradient_curve};
}

Ifc4x3_add2::IfcAlignment* addAlignment(IfcHierarchyHelper<Ifc4x3_add2>& file, const std::string& alignment_name, const std::vector<std::pair<double, double>>& points, const std::vector<double>& radii, const std::vector<std::pair<double, double>>& vpoints, const std::vector<double>& vclengths,bool include_geometry) {
    auto [horizontal_segments, horizontal_curve_segments, composite_curve] = _createHorizontalAlignment(file, points, radii, include_geometry);
    auto [vertical_segments, vertical_curve_segments, gradient_curve] = _createVerticalAlignment(file, composite_curve, vpoints, vclengths, include_geometry);

    _name_segments("H", horizontal_segments);
    _name_segments("V", vertical_segments);

    //
    // Create the horizontal alignment (IfcAlignmentHorizontal) and nest the segments
    //
    auto horizontal_alignment = new Ifc4x3_add2::IfcAlignmentHorizontal(IfcParse::IfcGlobalId(), nullptr, alignment_name + std::string(" - Horizontal"), boost::none, boost::none, nullptr, nullptr);
    file.addEntity(horizontal_alignment);

    auto nests_horizontal_segments = new Ifc4x3_add2::IfcRelNests(IfcParse::IfcGlobalId(), nullptr, boost::none, std::string("Nests horizontal alignment segments with horizontal alignment"), horizontal_alignment, horizontal_segments);
    file.addEntity(nests_horizontal_segments);

    //
    // Create the vertical alignment (IfcAlignmentVertical) and nest the segments
    //
    auto vertical_profile = new Ifc4x3_add2::IfcAlignmentVertical(IfcParse::IfcGlobalId(), nullptr, alignment_name + std::string("- Vertical"), boost::none, boost::none, nullptr, nullptr);
    file.addEntity(vertical_profile);

    auto nests_vertical_segments = new Ifc4x3_add2::IfcRelNests(IfcParse::IfcGlobalId(), nullptr, boost::none, std::string("Nests vertical alignment segments with vertical alignment"), vertical_profile, vertical_segments);
    file.addEntity(nests_vertical_segments);

    Ifc4x3_add2::IfcLocalPlacement* placement = nullptr;
    Ifc4x3_add2::IfcProductDefinitionShape* product_definition_shape = nullptr;
    if (include_geometry) {
        auto axis_model_representation_subcontext = file.getRepresentationSubContext("Axis", "Model");

        // the composite curve is a representation item
        typename aggregate_of<Ifc4x3_add2::IfcRepresentationItem>::ptr alignment_representation_items(new aggregate_of<Ifc4x3_add2::IfcRepresentationItem>());
        alignment_representation_items->push(composite_curve);

        // create the footprint representation
        auto footprint_shape_representation = new Ifc4x3_add2::IfcShapeRepresentation(axis_model_representation_subcontext, std::string("FootPrint"), std::string("Curve2D"), alignment_representation_items);
        file.addEntity(footprint_shape_representation);

        // the gradient curve is a representation item
        typename aggregate_of<typename Ifc4x3_add2::IfcRepresentationItem>::ptr profile_representation_items(new aggregate_of<Ifc4x3_add2::IfcRepresentationItem>());
        profile_representation_items->push(gradient_curve);

        // create the axis representation
        auto axis3d_shape_representation = new Ifc4x3_add2::IfcShapeRepresentation(axis_model_representation_subcontext, std::string("Axis"), std::string("Curve3D"), profile_representation_items);
        file.addEntity(axis3d_shape_representation);

        // create axis representations for each segment
        placement = file.addLocalPlacement();
        _createSegmentRepresentations(file, placement, axis_model_representation_subcontext, horizontal_curve_segments, horizontal_segments);
        _createSegmentRepresentations(file, placement, axis_model_representation_subcontext, vertical_curve_segments, vertical_segments);

       // the alignment has two representations, a plan view footprint and a 3d curve
        typename aggregate_of<typename Ifc4x3_add2::IfcRepresentation>::ptr alignment_representations(new aggregate_of<Ifc4x3_add2::IfcRepresentation>());
        alignment_representations->push(footprint_shape_representation); // 2D footprint
        alignment_representations->push(axis3d_shape_representation);    // 3D curve

        // create the alignment product definition
        product_definition_shape = new Ifc4x3_add2::IfcProductDefinitionShape(std::string("Alignment Product Definition Shape"), boost::none, alignment_representations);
    }

    //
    // Create the IfcAlignment
    //

    auto alignment = new Ifc4x3_add2::IfcAlignment(IfcParse::IfcGlobalId(), nullptr, alignment_name, boost::none, boost::none, placement, product_definition_shape, boost::none);
    file.addEntity(alignment);

    // Nest the IfcAlignmentHorizontal and IfcAlignmentVertical with the IfcAlignment to complete the business logic
    // 4.1.4.4.1 Alignments nest horizontal and vertical layouts
    // https://standards.buildingsmart.org/IFC/RELEASE/IFC4_3/HTML/concepts/Object_Composition/Nesting/Alignment_Layouts/content.html
    typename aggregate_of<Ifc4x3_add2::IfcObjectDefinition>::ptr alignment_layout_list(new aggregate_of<Ifc4x3_add2::IfcObjectDefinition>());
    alignment_layout_list->push(horizontal_alignment);
    alignment_layout_list->push(vertical_profile);

    auto nests_alignment_layouts = new Ifc4x3_add2::IfcRelNests(IfcParse::IfcGlobalId(), nullptr, std::string("Nest horizontal and vertical alignment layouts with the alignment"), boost::none, alignment, alignment_layout_list);
    file.addEntity(nests_alignment_layouts);

    return alignment;
}

std::pair<Ifc4x3_add2::IfcCurveSegment*, Ifc4x3_add2::IfcCurveSegment*> mapAlignmentSegment(const Ifc4x3_add2::IfcAlignmentSegment* segment) {
    std::pair<Ifc4x3_add2::IfcCurveSegment*, Ifc4x3_add2::IfcCurveSegment*> result(nullptr, nullptr);
    auto design_parameters = segment->DesignParameters();
    auto horizontal = design_parameters->as<Ifc4x3_add2::IfcAlignmentHorizontalSegment>();
    auto vertical = design_parameters->as<Ifc4x3_add2::IfcAlignmentVerticalSegment>();
    auto cant = design_parameters->as<Ifc4x3_add2::IfcAlignmentCantSegment>();
    if (horizontal) {
        result = mapAlignmentHorizontalSegment(horizontal);
    } else if (vertical) {
        result = mapAlignmentVerticalSegment(vertical);
    } else if (cant) {
        result = mapAlignmentCantSegment(cant);
    } else {
        Logger::Error(std::string("Unexpected IfcAlignmentSegment subtype encountered"));
    }
    return result;
}

std::pair<Ifc4x3_add2::IfcCurveSegment*, Ifc4x3_add2::IfcCurveSegment*> mapAlignmentHorizontalSegment(const Ifc4x3_add2::IfcAlignmentHorizontalSegment* segment) {
    std::pair<Ifc4x3_add2::IfcCurveSegment*, Ifc4x3_add2::IfcCurveSegment*> result(nullptr, nullptr);
    auto start_point = segment->StartPoint();
    auto start_direction = segment->StartDirection();
    auto start_radius = segment->StartRadiusOfCurvature();
    auto end_radius = segment->EndRadiusOfCurvature();
    auto length = segment->SegmentLength();
    auto type = segment->PredefinedType();

    double f = (end_radius ? length / end_radius : 0.0) - (start_radius ? length / start_radius : 0.0);

    if (type == Ifc4x3_add2::IfcAlignmentHorizontalSegmentTypeEnum::IfcAlignmentHorizontalSegmentType_LINE) {
        Ifc4x3_add2::IfcCurve* parent_curve = new Ifc4x3_add2::IfcLine(
            new Ifc4x3_add2::IfcCartesianPoint({0.0, 0.0}),
            new Ifc4x3_add2::IfcVector(new Ifc4x3_add2::IfcDirection({1.0, 0.0}), 1.0));

        Ifc4x3_add2::IfcCurveSegment* curve_segment = new Ifc4x3_add2::IfcCurveSegment(
            Ifc4x3_add2::IfcTransitionCode::IfcTransitionCode_CONTSAMEGRADIENT,
            new Ifc4x3_add2::IfcAxis2Placement2D(start_point, new Ifc4x3_add2::IfcDirection({cos(start_direction), sin(start_direction)})),
            new Ifc4x3_add2::IfcLengthMeasure(0.0),
            new Ifc4x3_add2::IfcLengthMeasure(length),
            parent_curve);

        result.first = curve_segment;
    } else if (type == Ifc4x3_add2::IfcAlignmentHorizontalSegmentTypeEnum::IfcAlignmentHorizontalSegmentType_CIRCULARARC) {
        Ifc4x3_add2::IfcCurve* parent_curve = new Ifc4x3_add2::IfcCircle(
            new Ifc4x3_add2::IfcAxis2Placement2D(new Ifc4x3_add2::IfcCartesianPoint(std::vector<double>({0, 0})),
                                                 new Ifc4x3_add2::IfcDirection(std::vector<double>{1, 0})),
            fabs(start_radius));

        Ifc4x3_add2::IfcCurveSegment* curve_segment = new Ifc4x3_add2::IfcCurveSegment(
            Ifc4x3_add2::IfcTransitionCode::IfcTransitionCode_CONTSAMEGRADIENT,
            new Ifc4x3_add2::IfcAxis2Placement2D(start_point, new Ifc4x3_add2::IfcDirection({cos(start_direction), sin(start_direction)})),
            new Ifc4x3_add2::IfcLengthMeasure(0.0),
            new Ifc4x3_add2::IfcLengthMeasure(length * start_radius / fabs(start_radius)),
            parent_curve);

        result.first = curve_segment;
    } else if (type == Ifc4x3_add2::IfcAlignmentHorizontalSegmentTypeEnum::IfcAlignmentHorizontalSegmentType_CLOTHOID) {
        double A = length / sqrt(fabs(f)) * f / fabs(f);
        Ifc4x3_add2::IfcCurve* parent_curve = new Ifc4x3_add2::IfcClothoid(
            new Ifc4x3_add2::IfcAxis2Placement2D(new Ifc4x3_add2::IfcCartesianPoint(std::vector<double>({0, 0})), new Ifc4x3_add2::IfcDirection(std::vector<double>{1, 0})),
            A);

        double offset;
        if ((fabs(start_radius) < fabs(end_radius) && start_radius) || end_radius == 0.) {
            offset = -length - (end_radius ? length * start_radius / (end_radius - start_radius) : 0);
        } else {
            offset = start_radius ? length * end_radius / (start_radius - end_radius) : 0;
        }

        Ifc4x3_add2::IfcCurveSegment* curve_segment = new Ifc4x3_add2::IfcCurveSegment(
            Ifc4x3_add2::IfcTransitionCode::IfcTransitionCode_CONTSAMEGRADIENT,
            new Ifc4x3_add2::IfcAxis2Placement2D(start_point, new Ifc4x3_add2::IfcDirection({cos(start_direction), sin(start_direction)})),
            new Ifc4x3_add2::IfcLengthMeasure(offset),
            new Ifc4x3_add2::IfcLengthMeasure(length),
            parent_curve);

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

        boost::optional<double> A0_optional, A1_optional, A2_optional;
        if (A0) {
            A0_optional = A0;
        }
        if (A1) {
            A1_optional = A1;
        }
        if (A2) {
            A2_optional = A2;
        }

        Ifc4x3_add2::IfcCurve* parent_curve = new Ifc4x3_add2::IfcThirdOrderPolynomialSpiral(
            new Ifc4x3_add2::IfcAxis2Placement2D(new Ifc4x3_add2::IfcCartesianPoint(std::vector<double>({0, 0})), new Ifc4x3_add2::IfcDirection(std::vector<double>{1, 0})),
            A3,
            A2_optional,
            A1_optional,
            A0_optional);

        Ifc4x3_add2::IfcCurveSegment* curve_segment = new Ifc4x3_add2::IfcCurveSegment(
            Ifc4x3_add2::IfcTransitionCode::IfcTransitionCode_CONTSAMEGRADIENT,
            new Ifc4x3_add2::IfcAxis2Placement2D(start_point, new Ifc4x3_add2::IfcDirection({cos(start_direction), sin(start_direction)})),
            new Ifc4x3_add2::IfcLengthMeasure(0.0),
            new Ifc4x3_add2::IfcLengthMeasure(length),
            parent_curve);

        result.first = curve_segment;
    } else if (type == Ifc4x3_add2::IfcAlignmentHorizontalSegmentTypeEnum::IfcAlignmentHorizontalSegmentType_COSINECURVE) {
        auto a0 = 0.5 * f + (start_radius ? length / start_radius : 0.0); // constant term
        auto a1 = -0.5 * f; // cosine term
        auto A0 = a0 ? length * pow(fabs(a0), -1. / 1.) * a0 / fabs(a0) : 0.0;
        auto A1 = a1 ? length * pow(fabs(a1), -1. / 1.) * a1 / fabs(a1) : 0.0;
        auto A0_optional = boost::optional<double>();
        if (A0) {
            A0_optional = A0;
        }
        Ifc4x3_add2::IfcCurve* parent_curve = new Ifc4x3_add2::IfcCosineSpiral(
            new Ifc4x3_add2::IfcAxis2Placement2D(new Ifc4x3_add2::IfcCartesianPoint(std::vector<double>({0, 0})), new Ifc4x3_add2::IfcDirection(std::vector<double>{1, 0})),
           A1, A0_optional);

        Ifc4x3_add2::IfcCurveSegment* curve_segment = new Ifc4x3_add2::IfcCurveSegment(
            Ifc4x3_add2::IfcTransitionCode::IfcTransitionCode_CONTSAMEGRADIENT,
            new Ifc4x3_add2::IfcAxis2Placement2D(start_point, new Ifc4x3_add2::IfcDirection({cos(start_direction), sin(start_direction)})),
            new Ifc4x3_add2::IfcLengthMeasure(0.0),
            new Ifc4x3_add2::IfcLengthMeasure(length),
            parent_curve);

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
        Ifc4x3_add2::IfcCurve* parent_curve = new Ifc4x3_add2::IfcPolynomialCurve(
            new Ifc4x3_add2::IfcAxis2Placement2D(new Ifc4x3_add2::IfcCartesianPoint(std::vector<double>({0, 0})), new Ifc4x3_add2::IfcDirection(std::vector<double>{1, 0})),
            std::vector<double>{0.0, 1.0},
            std::vector<double>{A0, A1, A2, A3},
           boost::none
        );

        Ifc4x3_add2::IfcCurveSegment* curve_segment = new Ifc4x3_add2::IfcCurveSegment(
            Ifc4x3_add2::IfcTransitionCode::IfcTransitionCode_CONTSAMEGRADIENT,
            new Ifc4x3_add2::IfcAxis2Placement2D(start_point, new Ifc4x3_add2::IfcDirection({cos(start_direction), sin(start_direction)})),
            new Ifc4x3_add2::IfcLengthMeasure(offset),
            new Ifc4x3_add2::IfcLengthMeasure(length),
            parent_curve);

        result.first = curve_segment;
    } else if (type == Ifc4x3_add2::IfcAlignmentHorizontalSegmentTypeEnum::IfcAlignmentHorizontalSegmentType_HELMERTCURVE) {
        auto a0_1 = start_radius ? length / start_radius : 0.0; // constant term, first half
        auto a1_1 = 0.0;                                        // linear term, first half
        auto a2_1 = 2 * f; // quadratic term, first half

        auto A0_1 = a0_1 ? length * pow(fabs(a0_1), -1. / 1.) * a0_1 / fabs(a0_1) : 0.0;
        auto A1_1 = a1_1 ? length * pow(fabs(a1_1), -1. / 2.) * a1_1 / fabs(a1_1) : 0.0;
        auto A2_1 = a2_1 ? length * pow(fabs(a2_1), -1. / 3.) * a2_1 / fabs(a2_1) : 0.0;

        auto A0_1_optional = boost::optional<double>();
        if (A0_1) {
            A0_1_optional = A0_1;
        }

        auto A1_1_optional = boost::optional<double>();
        if (A1_1) {
            A1_1_optional = A1_1;
        }

        Ifc4x3_add2::IfcCurve* parent_curve1 = new Ifc4x3_add2::IfcSecondOrderPolynomialSpiral(
            new Ifc4x3_add2::IfcAxis2Placement2D(new Ifc4x3_add2::IfcCartesianPoint(std::vector<double>({0, 0})), new Ifc4x3_add2::IfcDirection(std::vector<double>{1, 0})),
            A2_1,
            A1_1_optional,
            A0_1_optional);

        Ifc4x3_add2::IfcCurveSegment* curve_segment1 = new Ifc4x3_add2::IfcCurveSegment(
            Ifc4x3_add2::IfcTransitionCode::IfcTransitionCode_CONTSAMEGRADIENT,
            new Ifc4x3_add2::IfcAxis2Placement2D(start_point, new Ifc4x3_add2::IfcDirection({cos(start_direction), sin(start_direction)})),
            new Ifc4x3_add2::IfcLengthMeasure(0.0),
            new Ifc4x3_add2::IfcLengthMeasure(length/2),
            parent_curve1);

        result.first = curve_segment1;

        auto a0_2 = -f + (start_radius ? length / start_radius : 0.0); // constant term, second half
        auto a1_2 = 4 * f;                                             // linear term, second half
        auto a2_2 = -2 * f;                                            // quadratic term, second half

        auto A0_2 = a0_2 ? length * pow(fabs(a0_2), -1. / 1.) * a0_2 / fabs(a0_2) : 0.0;
        auto A1_2 = a1_2 ? length * pow(fabs(a1_2), -1. / 2.) * a1_2 / fabs(a1_2) : 0.0;
        auto A2_2 = a2_2 ? length * pow(fabs(a2_2), -1. / 3.) * a2_2 / fabs(a2_2) : 0.0;

        auto A0_2_optional = boost::optional<double>();
        if (A0_2) {
            A0_2_optional = A0_2;
        }
        auto A1_2_optional = boost::optional<double>();
        if (A1_2) {
            A1_2_optional = A1_2;
        }

        Ifc4x3_add2::IfcCurve* parent_curve2 = new Ifc4x3_add2::IfcSecondOrderPolynomialSpiral(
            new Ifc4x3_add2::IfcAxis2Placement2D(new Ifc4x3_add2::IfcCartesianPoint(std::vector<double>({0, 0})), new Ifc4x3_add2::IfcDirection(std::vector<double>{1, 0})),
            A2_2,
            A1_2_optional,
            A0_2_optional);

        Ifc4x3_add2::IfcCurveSegment* curve_segment2 = new Ifc4x3_add2::IfcCurveSegment(
            Ifc4x3_add2::IfcTransitionCode::IfcTransitionCode_CONTSAMEGRADIENT,
            new Ifc4x3_add2::IfcAxis2Placement2D(start_point, new Ifc4x3_add2::IfcDirection({cos(start_direction), sin(start_direction)})),
            new Ifc4x3_add2::IfcLengthMeasure(length/2),
            new Ifc4x3_add2::IfcLengthMeasure(length/2),
            parent_curve2);

        result.second = curve_segment2;
    } else if (type == Ifc4x3_add2::IfcAlignmentHorizontalSegmentTypeEnum::IfcAlignmentHorizontalSegmentType_SINECURVE) {
        auto a0 = start_radius ? length / start_radius : 0.0; // constant term
        auto a1 = f;                                          // linear term
        auto a2 = -f / (2 * PI); // sine term

        auto A0 = a0 ? length * pow(fabs(a0), -1. / 1.) * a0 / fabs(a0) : 0.0;
        auto A1 = a1 ? length * pow(fabs(a1), -1. / 2.) * a1 / fabs(a1) : 0.0;
        auto A2 = a2 ? length * pow(fabs(a2), -1. / 1.) * a2 / fabs(a2) : 0.0;

        auto A0_optional = boost::optional<double>();
        if (A0) {
            A0_optional = A0;
        }
        auto A1_optional = boost::optional<double>();
        if (A1) {
            A1_optional = A1;
        }

        Ifc4x3_add2::IfcCurve* parent_curve = new Ifc4x3_add2::IfcSineSpiral(new Ifc4x3_add2::IfcAxis2Placement2D(new Ifc4x3_add2::IfcCartesianPoint(std::vector<double>({0, 0})), new Ifc4x3_add2::IfcDirection(std::vector<double>{1, 0})), 
           A2, A1_optional, A0_optional);

        Ifc4x3_add2::IfcCurveSegment* curve_segment = new Ifc4x3_add2::IfcCurveSegment(
            Ifc4x3_add2::IfcTransitionCode::IfcTransitionCode_CONTSAMEGRADIENT,
            new Ifc4x3_add2::IfcAxis2Placement2D(start_point, new Ifc4x3_add2::IfcDirection({cos(start_direction), sin(start_direction)})),
            new Ifc4x3_add2::IfcLengthMeasure(0.0),
            new Ifc4x3_add2::IfcLengthMeasure(length),
            parent_curve);

        result.first = curve_segment;
    } else if (type == Ifc4x3_add2::IfcAlignmentHorizontalSegmentTypeEnum::IfcAlignmentHorizontalSegmentType_VIENNESEBEND) {
        Logger::Warning(std::string("mapping of AlignmentHorizontalSegmentType VIENNESEBEND not supported"));
    } else {
        Logger::Error(std::string("unexpected AlignmentHorizontalSegmentType encountered"));
    }

    return result;
}

std::pair<Ifc4x3_add2::IfcCurveSegment*, Ifc4x3_add2::IfcCurveSegment*> mapAlignmentVerticalSegment(const Ifc4x3_add2::IfcAlignmentVerticalSegment* segment) {
    std::pair<Ifc4x3_add2::IfcCurveSegment*, Ifc4x3_add2::IfcCurveSegment*> result(nullptr, nullptr);
    auto start_distance_along = segment->StartDistAlong();
    auto horizontal_length = segment->HorizontalLength();
    auto start_height = segment->StartHeight();
    auto start_gradient = segment->StartGradient();
    auto end_gradient = segment->EndGradient();
    auto radius_of_curvature = segment->RadiusOfCurvature();

    auto type = segment->PredefinedType();

    if (type == Ifc4x3_add2::IfcAlignmentVerticalSegmentTypeEnum::IfcAlignmentVerticalSegmentType_CONSTANTGRADIENT) {
        auto parent_curve = new Ifc4x3_add2::IfcLine(
            new Ifc4x3_add2::IfcCartesianPoint(std::vector<double>({0, 0})),
            new Ifc4x3_add2::IfcVector(new Ifc4x3_add2::IfcDirection(std::vector<double>{1, 0}), 1.0));

        auto curve_segment = new Ifc4x3_add2::IfcCurveSegment(
            Ifc4x3_add2::IfcTransitionCode::IfcTransitionCode_CONTSAMEGRADIENT,
            new Ifc4x3_add2::IfcAxis2Placement2D(
                new Ifc4x3_add2::IfcCartesianPoint({start_distance_along, start_height}),
                new Ifc4x3_add2::IfcDirection({sqrt(1.0 - start_gradient * start_gradient), start_gradient})),
            new Ifc4x3_add2::IfcLengthMeasure(0.0), // start
            new Ifc4x3_add2::IfcLengthMeasure(horizontal_length),
            parent_curve);

        result.first = curve_segment;

    } else if (type == Ifc4x3_add2::IfcAlignmentVerticalSegmentTypeEnum::IfcAlignmentVerticalSegmentType_PARABOLICARC) {
        double A = start_height;
        double B = start_gradient;
        double C = (end_gradient - start_gradient) / (2 * horizontal_length);

        auto parent_curve = new Ifc4x3_add2::IfcPolynomialCurve(
            new Ifc4x3_add2::IfcAxis2Placement2D(new Ifc4x3_add2::IfcCartesianPoint(std::vector<double>{0.0, 0.0}), new Ifc4x3_add2::IfcDirection(std::vector<double>{1.0, 0.0})),
            std::vector<double>{0.0, 1.0},
            std::vector<double>{A, B, C},
            boost::none);

        auto curve_segment = new Ifc4x3_add2::IfcCurveSegment(
            Ifc4x3_add2::IfcTransitionCode::IfcTransitionCode_CONTSAMEGRADIENT,
            new Ifc4x3_add2::IfcAxis2Placement2D(new Ifc4x3_add2::IfcCartesianPoint({start_distance_along, start_height}), new Ifc4x3_add2::IfcDirection({sqrt(1.0 - start_gradient * start_gradient), start_gradient})),
            new Ifc4x3_add2::IfcLengthMeasure(0.0),
            new Ifc4x3_add2::IfcLengthMeasure(horizontal_length),
            parent_curve);

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

        Ifc4x3_add2::IfcCurve* parent_curve = new Ifc4x3_add2::IfcCircle(
            new Ifc4x3_add2::IfcAxis2Placement2D(new Ifc4x3_add2::IfcCartesianPoint(std::vector<double>({0, 0})),
                                                 new Ifc4x3_add2::IfcDirection(std::vector<double>{1, 0})),
            radius);

        Ifc4x3_add2::IfcCurveSegment* curve_segment = new Ifc4x3_add2::IfcCurveSegment(
            Ifc4x3_add2::IfcTransitionCode::IfcTransitionCode_CONTSAMEGRADIENT,
            new Ifc4x3_add2::IfcAxis2Placement2D(new Ifc4x3_add2::IfcCartesianPoint({start_distance_along, start_height}), new Ifc4x3_add2::IfcDirection({1.0, 0.0})),
            new Ifc4x3_add2::IfcLengthMeasure(0.0),
            new Ifc4x3_add2::IfcLengthMeasure(horizontal_length),
            parent_curve);

        result.first = curve_segment;
    } else {
        Logger::Error(std::string("unexpected AlignmentVerticalSegmentType encountered"));
    }
    
    return result;
}

std::pair<Ifc4x3_add2::IfcCurveSegment*, Ifc4x3_add2::IfcCurveSegment*> mapAlignmentCantSegment(const Ifc4x3_add2::IfcAlignmentCantSegment* segment) {
    std::pair<Ifc4x3_add2::IfcCurveSegment*, Ifc4x3_add2::IfcCurveSegment*> result(nullptr, nullptr);
    auto type = segment->PredefinedType();
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
