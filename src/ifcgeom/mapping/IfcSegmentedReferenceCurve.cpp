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

#ifdef SCHEMA_HAS_IfcSegmentedReferenceCurve

taxonomy::ptr mapping::map_impl(const IfcSchema::IfcSegmentedReferenceCurve* inst) {
   if (!inst->BaseCurve()->as<IfcSchema::IfcGradientCurve>())
       Logger::Warning("Expected IfcSegmentedReferenceCurve.BaseCurve to be IfcGradient", inst); // CT 4.1.7.1.1.3
		  
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

	 // Get starting position of cant curve, relative to the gradient curve.
    // The cant curve can start before or after the start of the gradient curve
    auto first_segment = *(segments->begin());
    auto p = taxonomy::cast<taxonomy::matrix4>(map(first_segment->as<IfcSchema::IfcCurveSegment>()->Placement()));
    const Eigen::Matrix4d& m = p->ccomponents();
    double cant_start = m(0, 3); // start of cant curve

   auto cant = taxonomy::make<taxonomy::piecewise_function>(cant_start,pwfs,&settings_);

    // Determine the valid domain of the PWF... the valid domain is where 
    // horizontal, gradient and cant curves are defined
    auto gradient = taxonomy::cast<taxonomy::piecewise_function>(map(inst->BaseCurve()));
    auto horizontal = taxonomy::cast<taxonomy::piecewise_function>(map(inst->BaseCurve()->as<IfcSchema::IfcGradientCurve>()->BaseCurve()));
    double start = std::max(std::max(cant->start(), gradient->start()), horizontal->start());
    double end = std::min(std::min(cant->end(), gradient->end()), horizontal->end());
    double length = end - start;

    if (!(0 < length)) {
        Logger::Error("IfcSegmentedReferenceCurve does not have a common domain with BaseCurve");
    }

    // define the callback function for the segmented reference curve
	auto composition = [gradient, cant](double u)->Eigen::Matrix4d {
      // u is distance from start of cant curve
      // add cant->start() to u to get the distance from start of gradient curve
		auto g = gradient->evaluate(u+cant->start());
		auto c = cant->evaluate(u);

      c.col(3)(0) = 0.0;        // x is distance along. zero it out so it doesn't add to the x from gradient curve
      c.col(1).swap(c.col(2));  // c is 2D in distance along - y plane, swap y and z so elevations become z
      c.row(1).swap(c.row(2));

      Eigen::Matrix4d m;
      m = g * c;
      return m;
	};

	taxonomy::piecewise_function::spans_t spans;
   spans.emplace_back(length, composition);
   auto pwf = taxonomy::make<taxonomy::piecewise_function>(start, spans, &settings_, inst);
   return pwf;
}

#endif