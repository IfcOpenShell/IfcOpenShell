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
#include "../function_item_evaluator.h"
#define mapping POSTFIX_SCHEMA(mapping)
using namespace ifcopenshell::geometry;

#ifdef SCHEMA_HAS_IfcGradientCurve

taxonomy::ptr mapping::map_impl(const IfcSchema::IfcGradientCurve* inst) {
   if (!inst->BaseCurve()->as<IfcSchema::IfcCompositeCurve>())
       Logger::Warning("Expected IfcGradientCurve.BaseCurve to be IfcCompositeCurve", inst); // CT 4.1.7.1.1.2

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

	// Get starting position of gradient curve, which is relative to the base curve
	// The gradient curve can start before or after the start of the base curve
	auto first_segment = *(segments->begin());
   auto p = taxonomy::cast<taxonomy::matrix4>(map(first_segment->as<IfcSchema::IfcCurveSegment>()->Placement()));
   const Eigen::Matrix4d& m = p->ccomponents();
   double gradient_start = m(0, 3); // start of vertical (row 0, col 3) - "Distance Along" horizontal curve

	// create the vertical pwf
	auto vertical = taxonomy::make<taxonomy::piecewise_function>(gradient_start, spans);

	// create the horizontal pwf
   auto horizontal = taxonomy::cast<taxonomy::piecewise_function>(map(inst->BaseCurve()));

	// create the composite gradient curve function
   auto gradient_function = taxonomy::make<taxonomy::gradient_function>(horizontal, vertical, inst);

	// check to see if there is valid overlap of the horizontal and vertical domains
   if (!(0 < gradient_function->length())) {
       Logger::Error("IfcGradientCurve does not have a common domain with BaseCurve");
       gradient_function = nullptr; // not valid
   }

   return gradient_function;
}

#endif