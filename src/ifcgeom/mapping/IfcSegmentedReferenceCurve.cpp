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
		  
	auto gradient = taxonomy::cast<taxonomy::piecewise_function>(map(inst->BaseCurve()));
	auto cant = taxonomy::make<taxonomy::piecewise_function>(&settings_);

	auto segments = inst->Segments();

	for (auto& segment : *segments) {
		if (segment->as<IfcSchema::IfcCurveSegment>()) {
			// @todo check that we don't get a mixture of implicit and explicit definitions
			auto crv = map(segment->as<IfcSchema::IfcCurveSegment>());
			if (crv->kind() == taxonomy::PIECEWISE_FUNCTION) {
				auto seg = taxonomy::cast<taxonomy::piecewise_function>(crv);
				cant->spans.insert(cant->spans.end(), seg->spans.begin(), seg->spans.end());
			} else {
				Logger::Error("Unsupported");
				return nullptr;
			}
		} else {
			Logger::Error("Unsupported");
			return nullptr;
		}
	}

	auto composition = [gradient, cant](double u)->Eigen::Matrix4d {
		auto g = gradient->evaluate(u);
		auto c = cant->evaluate(u);

      std::swap(c.col(3)(1), c.col(3)(2));

      Eigen::Matrix4d m;
      m = g * c;
      return m;
	};

	std::array<taxonomy::piecewise_function::ptr, 2> both = { gradient , cant };
	// @todo: rb - this constrains the range of u to the minimum of gradient and cant
	// we discussed using the maximum for the range of us and then using std::numeric_limits<double>::NAN
	// for values of u that gradient or cant cannot be computed.
	// Review and decide what to do.
	double min_length = std::numeric_limits<double>::infinity();
	for (auto i = 0; i < 2; ++i) {
		double l = 0;
		for (auto& s : both[i]->spans) {
			l += s.first;
		}
		if (l < min_length) {
			min_length = l;
		}
	}

	auto pwf = taxonomy::make<taxonomy::piecewise_function>(&settings_);
	pwf->spans.emplace_back( min_length, composition );
	pwf->instance = inst;
	return pwf;
}

#endif