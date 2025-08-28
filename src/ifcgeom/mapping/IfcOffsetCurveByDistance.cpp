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
using namespace ifcopenshell::geometry;

// ifc4x1
//#define SCHEMA_IfcOffsetCurveByDistances_HAS_OffsetValues
//#define SCHEMA_IfcOffsetCurveByDistances_HAS_Tag
//#define SCHEMA_IfcOffsetCurveByDistances_Tag_IS_OPTIONAL

#ifdef SCHEMA_HAS_IfcOffsetCurveByDistances

taxonomy::ptr mapping::map_impl(const IfcSchema::IfcOffsetCurveByDistances* inst) {
    auto offset_values = inst->OffsetValues();
    if (offset_values->size() == 0) {
        Logger::Error("IfcOffsetCurveByDistances must have at least one offset value");
    }

    auto first_offset_value = *(offset_values->begin());

    auto basis_curve = inst->BasisCurve();

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
        Logger::Warning("IfcOffsetCurveByDistances is only implemented for BasisCurves curves based on taxonomy::function_item", inst);
        return nullptr;
    }

    double start = basis_curve_fn->start();
    double basis_curve_length = basis_curve_fn->length();

    taxonomy::piecewise_function::spans_t offset_spans;

#if defined SCHEMA_HAS_IfcDistanceExpression
   double first_distance = first_offset_value->DistanceAlong();
#else
   double first_distance = *first_offset_value->DistanceAlong()->as<IfcSchema::IfcLengthMeasure>();
#endif
   first_distance *= length_unit_;

   if (first_distance < 0.0) {
        Logger::Warning("IfcOffsetCurveByDistance first offset value is before the start of the curve.");
   }

   if(0.0 < first_distance)
   {
      // First offset is defined after the start of the curve so the lateral and vertical offsets
		// implicitly continue with the same value towards the start of the basis curve
        double py = first_offset_value->OffsetLateral().get_value_or(0.0);
        double pz = first_offset_value->OffsetVertical().get_value_or(0.0);
        py *= length_unit_;
        pz *= length_unit_;
        
        auto fn = [py, pz](double /*u*/) -> Eigen::Matrix4d { 
           Eigen::Matrix4d m = Eigen::Matrix4d::Identity(); 
           m.col(3)(1) = py; 
           m.col(3)(2) = pz; 
           return m; };
        offset_spans.emplace_back(taxonomy::make<taxonomy::functor_item>(first_distance, fn));
	}

    auto iter = offset_values->begin();
    auto next = std::next(iter);
    auto prev = std::prev(next);
    auto end = offset_values->end();
    for (; next != end; prev++, next++) {
#if defined SCHEMA_HAS_IfcDistanceExpression
        double dp = (*prev)->DistanceAlong();
        double dn = (*next)->DistanceAlong();
#else
        double dp = *(*prev)->DistanceAlong()->as<IfcSchema::IfcLengthMeasure>();
        double dn = *(*next)->DistanceAlong()->as<IfcSchema::IfcLengthMeasure>();
#endif
        dp *= length_unit_;
        dn *= length_unit_;

        if (dn < dp) // next is before previous
        {
            Logger::Warning("IfcOffsetCurveByDistance offset value is out of bounds.");
            continue;
        }

        double l = (dn - dp);
        double yn = (*next)->OffsetLateral().get_value_or(0.0) * length_unit_;
        double yp = (*prev)->OffsetLateral().get_value_or(0.0) * length_unit_;
        double zn = (*next)->OffsetVertical().get_value_or(0.0) * length_unit_;
        double zp = (*prev)->OffsetVertical().get_value_or(0.0) * length_unit_;

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

       
        auto fn = [yp, yn, zp, zn, l](double u) -> Eigen::Matrix4d {
            Eigen::Matrix4d m = Eigen::Matrix4d::Identity();
            m.col(3)(1) = (l == 0.0 ? yp : (yp + (yn - yp) * u / l));
            m.col(3)(2) = (l == 0.0 ? zp : (zp + (zn - zp) * u / l));
            return m;
        };
        offset_spans.emplace_back(taxonomy::make<taxonomy::functor_item>(l, fn));
    }

	 // at this point, next == end and prev == end-1
    #if defined SCHEMA_HAS_IfcDistanceExpression
    double last_distance = (*prev)->DistanceAlong() * length_unit_;
    #else
    double last_distance = *(*prev)->DistanceAlong()->as<IfcSchema::IfcLengthMeasure>() * length_unit_;
    #endif

    if (last_distance < basis_curve_length) {
         // Last offset is defined before the end of the curve so the lateral and vertical offsets
         // implicitly continue with the same value towards the end of the basis curve
         double py = (*prev)->OffsetLateral().get_value_or(0.0);
         double pz = (*prev)->OffsetVertical().get_value_or(0.0);
         py *= length_unit_;
         pz *= length_unit_;
         double l = basis_curve_length - last_distance;
         auto fn = [py, pz](double /*u*/) -> Eigen::Matrix4d { 
            Eigen::Matrix4d m = Eigen::Matrix4d::Identity(); 
            m.col(3)(1) = py; 
            m.col(3)(2) = pz; 
            return m; };

         offset_spans.emplace_back(taxonomy::make<taxonomy::functor_item>(l, fn));
    }

   auto offsets = taxonomy::make<taxonomy::piecewise_function>(start,offset_spans);

   auto fn = taxonomy::make<taxonomy::offset_function>(basis_curve_fn, offsets);
   return fn;
}

#endif