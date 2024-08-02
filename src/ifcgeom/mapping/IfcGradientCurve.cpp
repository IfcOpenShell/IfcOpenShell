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

#ifdef SCHEMA_HAS_IfcGradientCurve

taxonomy::ptr mapping::map_impl(const IfcSchema::IfcGradientCurve* inst) {
   if (!inst->BaseCurve()->as<IfcSchema::IfcCompositeCurve>())
       Logger::Warning("Expected IfcGradientCurve.BaseCurve to be IfcCompositeCurve", inst); // CT 4.1.7.1.1.2

	auto segments = inst->Segments();

   std::vector<taxonomy::piecewise_function::ptr> pwfs;

	for (auto& segment : *segments) {
		if (segment->as<IfcSchema::IfcCurveSegment>()) {
			// @todo check that we don't get a mixture of implicit and explicit definitions
			auto crv = map(segment->as<IfcSchema::IfcCurveSegment>());
			if (crv && crv->kind() == taxonomy::PIECEWISE_FUNCTION) {
				pwfs.push_back(taxonomy::cast<taxonomy::piecewise_function>(crv));
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
	auto vertical = taxonomy::make<taxonomy::piecewise_function>(gradient_start, pwfs, &settings_);

	// Determine the valid domain of the PWF... the valid domain is where both
	// the base curve and gradient curves are defined
   auto horizontal = taxonomy::cast<taxonomy::piecewise_function>(map(inst->BaseCurve()));
	double start = std::max(horizontal->start(),vertical->start());
   double end = std::min(horizontal->end(), vertical->end());
   double length = end - start;

	if (!(0 < length)) {
       Logger::Error("IfcGradientCurve does not have a common domain with BaseCurve");
   }

	// define the callback function for the gradient curve
	auto composition = [horizontal, vertical](double u)->Eigen::Matrix4d {
		// u is distance from start of gradient curve (vertical)
		// add vertical->start() to u to get distance from start of horizontal
      auto xy = horizontal->evaluate(u + vertical->start());
		auto uz = vertical->evaluate(u);

      uz.col(3)(0) = 0.0; // x is distance along. zero it out so it doesn't add to the x from horizontal
      uz.col(1).swap(uz.col(2)); // uz is 2D in distance along - y plane, swap y and z so elevations become z
      uz.row(1).swap(uz.row(2));

		Eigen::Matrix4d m;
      m = xy * uz; // combine horizontal and vertical
      return m;
	};

	taxonomy::piecewise_function::spans_t spans;
   spans.emplace_back(length, composition);
   auto pwf = taxonomy::make<taxonomy::piecewise_function>(start, spans, &settings_, inst);
   return pwf;
}

#endif