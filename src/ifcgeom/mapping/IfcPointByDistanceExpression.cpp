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

#if defined SCHEMA_HAS_IfcPointByDistanceExpression

taxonomy::ptr mapping::map_impl(const IfcSchema::IfcPointByDistanceExpression* inst) {
   auto u = (*inst->DistanceAlong()->as<IfcSchema::IfcLengthMeasure>()) * length_unit_;
   //auto basis_curve = inst->BasisCurve();
   //auto item = map(basis_curve);
   //auto pw_curve = ifcopenshell::geometry::piecewise_from_item(item);
   auto pw_curve = taxonomy::dcast<taxonomy::piecewise_function>(map(inst->BasisCurve()));
   auto m = pw_curve->evaluate(u);

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
