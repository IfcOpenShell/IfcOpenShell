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
    auto pw_curve = taxonomy::dcast<taxonomy::piecewise_function>(map(basis_curve));

    double start = pw_curve->start();
    double basis_curve_length = pw_curve->length();

    taxonomy::piecewise_function::spans_t offset_spans;

#if defined SCHEMA_HAS_IfcDistanceExpression
   double first_distance = first_offset_value->DistanceAlong();
#else
   double first_distance = *first_offset_value->DistanceAlong()->as<IfcSchema::IfcLengthMeasure>();
#endif

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
        offset_spans.emplace_back(first_distance, fn);
	}

    auto iter = offset_values->begin();
    auto next = std::next(iter);
    auto prev = std::prev(next);
    auto end = offset_values->end();
    for (; next != end; prev++, next++) {
#if defined SCHEMA_HAS_IfcPointByDistanceExpression
        if ((*prev)->BasisCurve() != basis_curve || (*next)->BasisCurve() != basis_curve) {
            Logger::Error("All offsets from a IfcOffsetCurveByDistances must refer to the same BasisCurve");
        }
#endif

#if defined SCHEMA_HAS_IfcDistanceExpression
        double dn = (*next)->DistanceAlong();
        double dp = (*prev)->DistanceAlong();
#else
        double dn = *(*next)->DistanceAlong()->as<IfcSchema::IfcLengthMeasure>();
        double dp = *(*prev)->DistanceAlong()->as<IfcSchema::IfcLengthMeasure>();
#endif
        if ((dp < 0.0 || basis_curve_length < dp) 
             or 
            (dn < 0.0 || basis_curve_length < dn)
           or
            (dn < dp)
           )
        {
            Logger::Warning("IfcOffsetCurveByDistance offset value is out of bounds.");
            continue;
        }

        double l = (dn - dp)*length_unit_;
        double yn = (*next)->OffsetLateral().get_value_or(0.0) * length_unit_;
        double yp = (*prev)->OffsetLateral().get_value_or(0.0) * length_unit_;
        double zn = (*next)->OffsetVertical().get_value_or(0.0) * length_unit_;
        double zp = (*prev)->OffsetVertical().get_value_or(0.0) * length_unit_;
       
        auto fn = [yp, yn, zp, zn, l](double u) -> Eigen::Matrix4d {
            Eigen::Matrix4d m = Eigen::Matrix4d::Identity();
            m.col(3)(1) = (l == 0.0 ? yp : (yp + (yn - yp) * u / l));
            m.col(3)(2) = (l == 0.0 ? zp : (zp + (zn - zp) * u / l));
            return m;
        };
        offset_spans.emplace_back(l, fn);
    }

	 // at this point, next == end and prev == end-1
    #if defined SCHEMA_HAS_IfcDistanceExpression
    double last_distance = (*prev)->DistanceAlong() * length_unit_;
    #else
    double last_distance = *(*prev)->DistanceAlong()->as<IfcSchema::IfcLengthMeasure>() * length_unit_;
    #endif
    
    if (basis_curve_length < last_distance) {
          Logger::Warning("IfcOffsetCurveByDistance last offset value is after the end of the curve.");
    }

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

         offset_spans.emplace_back(l, fn);
    }

   auto offsets = taxonomy::make<taxonomy::piecewise_function>(start,offset_spans,&settings_);

	auto composition = [pw_curve, offsets](double u) -> Eigen::Matrix4d {
      auto p = pw_curve->evaluate(u);
		auto offset = offsets->evaluate(u);
      Eigen::Matrix4d m = p * offset;
      return m;
	};

   // current implementation assumes that composition is equal to the full length of basis curve
   // this may change depending on decisions in the bSI-IF
   taxonomy::piecewise_function::spans_t spans;
   spans.emplace_back(basis_curve_length, composition);
	auto pwf = taxonomy::make<taxonomy::piecewise_function>(start,spans,&settings_,inst);
	return pwf;
}

#endif