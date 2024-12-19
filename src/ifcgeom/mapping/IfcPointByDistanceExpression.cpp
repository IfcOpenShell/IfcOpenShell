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

#if defined SCHEMA_HAS_IfcPointByDistanceExpression

taxonomy::ptr mapping::map_impl(const IfcSchema::IfcPointByDistanceExpression* inst) {
   auto u = (*inst->DistanceAlong()->as<IfcSchema::IfcLengthMeasure>()) * length_unit_;
   auto basis_curve = map(inst->BasisCurve());
   taxonomy::function_item::ptr curve = taxonomy::dcast<taxonomy::function_item>(basis_curve);
   if (!curve) {
      // if the basis curve is not a function_item, the cast it to piecewise_function. the casting operator
      // calls loop_to_piecewise_function_upgrade and will convert loops to a piecewise function
       curve = taxonomy::dcast<taxonomy::piecewise_function>(basis_curve);
   }

   function_item_evaluator evaluator(curve,settings_);
   auto m = evaluator.evaluate(u);

   auto o = m.col(3).head<3>();
   auto z = m.col(2).head<3>();
   auto x = m.col(0).head<3>();

   if (inst->OffsetLateral().has_value()) {
       auto offset_lateral = inst->OffsetLateral().get() * length_unit_;
       auto y = Eigen::Vector3d(m.col(1)(0), m.col(1)(1), m.col(1)(2)); 
       o += offset_lateral * y;
   }

   if (inst->OffsetVertical().has_value()) {
       auto offset_vertical = inst->OffsetVertical().get() * length_unit_;
       o += offset_vertical * z;
   }

   if (inst->OffsetLongitudinal().has_value()) {
       auto offset_longitudinal = inst->OffsetLongitudinal().get() * length_unit_;
       o += offset_longitudinal* x;
   }

   return taxonomy::make<taxonomy::matrix4>(o,z,x);
}

#endif
