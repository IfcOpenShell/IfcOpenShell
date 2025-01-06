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
#define mapping POSTFIX_SCHEMA(mapping)
using namespace ifcopenshell::geometry;

#include "../function_item_evaluator.h"

#ifdef SCHEMA_HAS_IfcSegmentedReferenceCurve

taxonomy::ptr mapping::map_impl(const IfcSchema::IfcSegmentedReferenceCurve* inst) {
   if (!inst->BaseCurve()->as<IfcSchema::IfcGradientCurve>())
       Logger::Warning("Expected IfcSegmentedReferenceCurve.BaseCurve to be IfcGradient", inst); // CT 4.1.7.1.1.3
		  
	auto segments = inst->Segments();

	taxonomy::piecewise_function::spans_t spans;
    for (auto& segment : *segments) {
		if (segment->as<IfcSchema::IfcCurveSegment>()) {
			// @todo check that we don't get a mixture of implicit and explicit definitions
			auto crv = map(segment->as<IfcSchema::IfcCurveSegment>());
        if (auto fi = taxonomy::dcast<taxonomy::function_item>(crv); crv && fi /*crv->kind() == taxonomy::FUNCTION_ITEM*/) {
            // crv->kind() is polymorphic and the kind of the actual function_item is returned. PWF can have spans of any FUNCTION_ITEM
            // for this reason, a dynamic cast is used and if crv is a function_item it is added to the span
            spans.push_back(fi);
        } else {
				Logger::Error("Unsupported");
				return nullptr;
			}
		} else {
			Logger::Error("Unsupported");
			return nullptr;
		}
	 }

	 // Get starting position of cant curve, relative to the gradient curve.
    // The cant curve can start before or after the start of the gradient curve
    auto first_segment = *(segments->begin());
    auto p = taxonomy::cast<taxonomy::matrix4>(map(first_segment->as<IfcSchema::IfcCurveSegment>()->Placement()));
    const Eigen::Matrix4d& m = p->ccomponents();
    double cant_start = m(0, 3); // start of cant curve

   auto cant = taxonomy::make<taxonomy::piecewise_function>(cant_start,spans);
   auto gradient = taxonomy::cast<taxonomy::gradient_function>(map(inst->BaseCurve()));

   auto cant_function = taxonomy::make<taxonomy::cant_function>(gradient, cant, inst);
   if (!(0 < cant_function->length())) {
       Logger::Error("IfcSegmentedReferenceCurve does not have a common domain with BaseCurve");
       cant_function = nullptr;
   }
   return cant_function;
}

#endif