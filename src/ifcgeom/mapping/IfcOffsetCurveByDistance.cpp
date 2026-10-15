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

#include "mapping.h"
#include "../profile_helper.h"
#include "../function_item_evaluator.h"
#define mapping POSTFIX_SCHEMA(mapping)
using namespace ifcopenshell::geom;

// ifc4x1
//#define SCHEMA_IfcOffsetCurveByDistances_HAS_OffsetValues
//#define SCHEMA_IfcOffsetCurveByDistances_HAS_Tag
//#define SCHEMA_IfcOffsetCurveByDistances_Tag_IS_OPTIONAL

#ifdef SCHEMA_HAS_IfcOffsetCurveByDistances

namespace {
// Lateral (y) and vertical (z) offset from the basis curve, the same over the whole span
struct constant_offset_function : public taxonomy::span_function {
    constant_offset_function(double y, double z) : y_(y), z_(z) {}

    Eigen::Matrix4d operator()(double /*u*/) const override {
        Eigen::Matrix4d m = Eigen::Matrix4d::Identity();
        m.col(3)(1) = y_;
        m.col(3)(2) = z_;
        return m;
    }

    double y_, z_;
};

// Lateral (y) and vertical (z) offset from the basis curve, varying linearly over a span of length l
struct linear_offset_function : public taxonomy::span_function {
    linear_offset_function(double y_start, double y_end, double z_start, double z_end, double l) : y_start_(y_start), y_end_(y_end), z_start_(z_start), z_end_(z_end), l_(l) {}

    Eigen::Matrix4d operator()(double u) const override {
        Eigen::Matrix4d m = Eigen::Matrix4d::Identity();
        m.col(3)(1) = (l_ == 0.0 ? y_start_ : (y_start_ + (y_end_ - y_start_) * u / l_));
        m.col(3)(2) = (l_ == 0.0 ? z_start_ : (z_start_ + (z_end_ - z_start_) * u / l_));
        return m;
    }

    double y_start_, y_end_, z_start_, z_end_, l_;
};

taxonomy::span_info offset_span_info(taxonomy::span_curve curve) {
    taxonomy::span_info info;
    info.layout = taxonomy::span_layout::OFFSET;
    info.curve = curve;
    return info;
}
} // namespace

taxonomy::ptr mapping::map_impl(const IfcSchema::IfcOffsetCurveByDistances& inst) {
    auto offset_values = inst.OffsetValues();
    if (offset_values.empty()) {
        logger_.error("GEO", 270, "IfcOffsetCurveByDistances must have at least one offset value");
    }

    auto& first_offset_value = offset_values.front();

    auto basis_curve = inst.BasisCurve();

//    // IfcOffsetCurveByDistances can be based on another IfcOffsetCurveByDistances, an IfcGradientCurve, or an IfcCompositeCurve
//    // When based on IfcOffsetCurveByDistances, it creates a chain of curves that we must navigate down to the base curve.
//    // The source curve is IfcGradientCurve or IfcCompositeCurve. This loop drills down to the base curve.
//    while (auto offset_curve = basis_curve->as<IfcSchema::IfcOffsetCurveByDistances>()) {
//        basis_curve = offset_curve;
//    }
//
//#if defined SCHEMA_HAS_IfcGradientCurve
//    if (auto gc = basis_curve->as<IfcSchema::IfcGradientCurve>()) {
//        basis_curve = gc->BaseCurve();
//    }
//#endif

    auto basis_curve_fn = taxonomy::dcast<taxonomy::function_item>(map(basis_curve));
    if (!basis_curve_fn) {
        // Only implement on alignment curves
        logger_.warning("GEO", 271, "IfcOffsetCurveByDistances is only implemented for BasisCurves curves based on taxonomy::function_item", inst);
        return nullptr;
    }

    double start = basis_curve_fn->start();
    double basis_curve_length = basis_curve_fn->length();

    taxonomy::piecewise_function::span_list offset_spans;

#if defined SCHEMA_HAS_IfcDistanceExpression
   double first_distance = first_offset_value.DistanceAlong();
#else
   double first_distance = first_offset_value.DistanceAlong().as<IfcSchema::IfcLengthMeasure>();
#endif
   first_distance *= length_unit_;

   if (first_distance < 0.0) {
        logger_.warning("GEO", 272, "IfcOffsetCurveByDistance first offset value is before the start of the curve.");
   }

   if(0.0 < first_distance)
   {
      // First offset is defined after the start of the curve so the lateral and vertical offsets
		// implicitly continue with the same value towards the start of the basis curve
        double py = first_offset_value.OffsetLateral().value_or(0.0);
        double pz = first_offset_value.OffsetVertical().value_or(0.0);
        py *= length_unit_;
        pz *= length_unit_;

        auto fn = std::make_shared<constant_offset_function>(py, pz);
        offset_spans.emplace_back(taxonomy::make<taxonomy::functor_item>(first_distance, fn, offset_span_info(taxonomy::span_curve::CONSTANT), inst));
	}

    auto iter = offset_values.begin();
    auto next = std::next(iter);
    auto prev = std::prev(next);
    auto end = offset_values.end();
    for (; next != end; prev++, next++) {
#if defined SCHEMA_HAS_IfcDistanceExpression
        double dp = (*prev).DistanceAlong();
        double dn = (*next).DistanceAlong();
#else
        double dp = prev->DistanceAlong().as<IfcSchema::IfcLengthMeasure>();
        double dn = next->DistanceAlong().as<IfcSchema::IfcLengthMeasure>();
#endif
        dp *= length_unit_;
        dn *= length_unit_;

        if (dn < dp) // next is before previous
        {
            logger_.warning("GEO", 273, "IfcOffsetCurveByDistance offset value is out of bounds.");
            continue;
        }

        double l = (dn - dp);
        double yn = next->OffsetLateral().value_or(0.0) * length_unit_;
        double yp = prev->OffsetLateral().value_or(0.0) * length_unit_;
        double zn = next->OffsetVertical().value_or(0.0) * length_unit_;
        double zp = prev->OffsetVertical().value_or(0.0) * length_unit_;

        if ( (dp < 0.0 && dn < 0.0) || (basis_curve_length < dp && basis_curve_length < dn) ) {
            // both points are either before the start of the curve or after the end of the curve. ignore them.
            continue;
        }

        if (dp < 0.0) {
            // previous is before the start of the curve
            // compute y and z offsets at the start of the curve
            auto yp_at_start = yp - (yn - yp) * dp / l;
            auto zp_at_start = zp - (zn - zp) * dp / l;

            dp = 0.0;
            yp = yp_at_start;
            zp = zp_at_start;
        }

        if (basis_curve_length < dn) {
            // next is after the end of the curve
            // compute y and z offsets at the end of the curve
            auto yn_at_end = yn - (yn - yp) * (dn - basis_curve_length) / l;
            auto zn_at_end = zn - (zn - zp) * (dn - basis_curve_length) / l;
            dn = basis_curve_length;
            yn = yn_at_end;
            zn = zn_at_end;
        }


        auto fn = std::make_shared<linear_offset_function>(yp, yn, zp, zn, l);
        offset_spans.emplace_back(taxonomy::make<taxonomy::functor_item>(l, fn, offset_span_info(taxonomy::span_curve::LINEAR), inst));
    }

	 // at this point, next == end and prev == end-1
    #if defined SCHEMA_HAS_IfcDistanceExpression
    double last_distance = prev->DistanceAlong() * length_unit_;
    #else
    double last_distance = (double) prev->DistanceAlong().as<IfcSchema::IfcLengthMeasure>() * length_unit_;
    #endif

    if (last_distance < basis_curve_length) {
         // Last offset is defined before the end of the curve so the lateral and vertical offsets
         // implicitly continue with the same value towards the end of the basis curve
         double py = prev->OffsetLateral().value_or(0.0);
         double pz = prev->OffsetVertical().value_or(0.0);
         py *= length_unit_;
         pz *= length_unit_;
         double l = basis_curve_length - last_distance;
         auto fn = std::make_shared<constant_offset_function>(py, pz);
         offset_spans.emplace_back(taxonomy::make<taxonomy::functor_item>(l, fn, offset_span_info(taxonomy::span_curve::CONSTANT), inst));
    }

   auto offsets = taxonomy::make<taxonomy::piecewise_function>(start,offset_spans);

   auto fn = taxonomy::make<taxonomy::offset_function>(basis_curve_fn, offsets);
   return fn;
}

#endif
