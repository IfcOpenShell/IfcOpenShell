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
	auto horizontal = taxonomy::cast<taxonomy::piecewise_function>(map(inst->BaseCurve()));
	auto vertical = taxonomy::make<taxonomy::piecewise_function>();

	auto segments = inst->Segments();

	for (auto& segment : *segments) {
		if (segment->as<IfcSchema::IfcCurveSegment>()) {
			// @todo check that we don't get a mixture of implicit and explicit definitions
			auto crv = map(segment->as<IfcSchema::IfcCurveSegment>());
			if (crv->kind() == taxonomy::PIECEWISE_FUNCTION) {
				auto seg = taxonomy::cast<taxonomy::piecewise_function>(crv);
				vertical->spans.insert(vertical->spans.end(), seg->spans.begin(), seg->spans.end());
			} else {
				Logger::Error("Unsupported");
				return nullptr;
			}
		} else {
			Logger::Error("Unsupported");
			return nullptr;
		}
	}

	// @todo does this really make sense?
	auto composition = [horizontal, vertical](double u) {
		auto xy = horizontal->evaluate(u);
		auto z = vertical->evaluate(u);
		Eigen::VectorXd vec(3);
		vec << xy(0), xy(1), z(0);
		return vec;
	};

	// @todo where do we get the startdistalong from @civilx64's code?
	std::array<taxonomy::piecewise_function::ptr, 2> both = { horizontal , vertical };
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

	auto pwf = taxonomy::make<taxonomy::piecewise_function>();
	pwf->spans.push_back({ min_length, composition });
	return pwf;
}

#endif